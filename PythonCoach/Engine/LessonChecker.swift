import Foundation

enum LessonChecker {
    /// The placeholder beginners replace in fill-in-the-blank starters.
    static let blank = "___"

    static func gradeChoice(practice: Practice, choice: Int) -> LessonCheck {
        let valid = practice.choices.indices.contains(choice)
        let correct = valid && choice == practice.answer
        if correct {
            return LessonCheck(
                passed: true,
                headline: practice.isPredict ? "You called it" : "Nice work",
                message: practice.explain.isEmpty ? "That is the right answer." : practice.explain,
                expected: nil,
                actual: nil,
                error: nil,
                sections: []
            )
        }
        let opener = practice.isPredict
            ? "Good guess, but Python prints something else. Read the code one line at a time, like Python does, and try again."
            : "Not that one, but you're close. Read the question again and try another answer."
        return LessonCheck(
            passed: false,
            headline: "Not yet",
            message: opener,
            expected: nil,
            actual: valid ? practice.choices[choice] : nil,
            error: nil,
            sections: []
        )
    }

    /// Checked before running. A starter that still has ___ in it is not finished yet.
    static func blankCheck(source: String) -> LessonCheck? {
        let lines = source.components(separatedBy: "\n")
        guard let index = lines.firstIndex(where: { $0.contains(blank) }) else { return nil }
        let count = lines.reduce(0) { $0 + $1.components(separatedBy: blank).count - 1 }
        let which = count == 1 ? "the blank" : "each blank"
        return LessonCheck(
            passed: false,
            headline: "Fill in the blank",
            message: "Replace \(which) (\(blank)) with your answer, then run it again. The first one is on line \(index + 1).",
            expected: nil,
            actual: nil,
            error: nil,
            sections: []
        )
    }

    static func evaluate(source: String, practice: Practice, runs: [CapturedRun]) -> LessonCheck {
        let multiple = practice.tests.count > 1
        let sections = runs.enumerated().map { index, run in
            OutputSection(
                index: index,
                title: multiple ? "Check \(index + 1)" : "Output",
                stdout: run.stdout,
                stderr: run.stderr
            )
        }

        if runs.contains(where: \.cancelled) {
            return LessonCheck(
                passed: false,
                headline: "Stopped",
                message: "You closed the question Python asked. Run the code again when you want to answer.",
                expected: nil,
                actual: nil,
                error: nil,
                sections: sections
            )
        }

        if runs.contains(where: \.timedOut) || runs.contains(where: { $0.errorType == "TimeoutError" }) {
            let failed = runs.first(where: { $0.timedOut || $0.errorType == "TimeoutError" })
            let error = FriendlyErrors.explain(
                type: "TimeoutError",
                message: "timeout",
                traceback: failed?.traceback,
                timedOut: true,
                source: source
            )
            return LessonCheck(
                passed: false,
                headline: error.title,
                message: error.message,
                expected: nil,
                actual: nil,
                error: error,
                sections: sections
            )
        }

        if let failed = runs.first(where: { $0.errorType != nil }) {
            let error = FriendlyErrors.explain(
                type: failed.errorType,
                message: failed.errorMessage,
                traceback: failed.traceback,
                timedOut: false,
                source: source
            )
            return LessonCheck(
                passed: false,
                headline: error.title,
                message: error.message,
                expected: nil,
                actual: nil,
                error: error,
                sections: sections
            )
        }

        if runs.count != practice.tests.count {
            return LessonCheck(
                passed: false,
                headline: "Not finished",
                message: "I couldn't finish every check. Run the code again.",
                expected: nil,
                actual: nil,
                error: nil,
                sections: sections
            )
        }

        for (index, pair) in zip(practice.tests, runs).enumerated() {
            let (test, run) = pair
            let label = multiple ? " (check \(index + 1)\(inputNote(test)))" : ""
            if let expected = test.stdoutEquals {
                let actual = OutputNormalizer.normalize(run.stdout)
                let wanted = OutputNormalizer.normalize(expected)
                if actual != wanted {
                    return mismatch(
                        message: OutputDiff.describe(expected: wanted, actual: actual) + label,
                        expected: wanted,
                        actual: actual,
                        sections: sections
                    )
                }
            }
            for needle in test.stdoutContains {
                let actual = OutputNormalizer.normalize(run.stdout)
                let wanted = OutputNormalizer.normalize(needle)
                if !actual.contains(wanted) {
                    return mismatch(
                        message: "So close. The output is missing \"\(wanted)\"\(label).",
                        expected: wanted,
                        actual: actual,
                        sections: sections
                    )
                }
            }
            for (name, expected) in test.values.sorted(by: { $0.key < $1.key }) {
                if let actual = run.values[name] {
                    if actual != expected {
                        return LessonCheck(
                            passed: false,
                            headline: "Not yet",
                            message: "The variable \(name) should be \(expected), but it was \(actual)\(label).",
                            expected: expected,
                            actual: actual,
                            error: nil,
                            sections: sections
                        )
                    }
                } else {
                    return LessonCheck(
                        passed: false,
                        headline: "Not yet",
                        message: "Make a variable named \(name). Spell it exactly like that, all lowercase.",
                        expected: expected,
                        actual: nil,
                        error: nil,
                        sections: sections
                    )
                }
            }
        }

        var missing: [String] = []
        for snippet in practice.sourceMustContain where !SourceScan.containsSnippet(source, snippet) {
            missing.append(snippet)
        }
        let choice = practice.sourceMustContainOneOf
        let choiceOK = choice.isEmpty || choice.contains { SourceScan.containsSnippet(source, $0) }
        if !missing.isEmpty || !choiceOK {
            var sentences = missing.map { SourceScan.sentence(for: $0) }
            if !choiceOK, let first = choice.first {
                sentences.append(SourceScan.sentence(for: first))
            }
            return LessonCheck(
                passed: false,
                headline: "Almost",
                message: "The output is right. One more thing: " + sentences.joined(separator: " "),
                expected: nil,
                actual: nil,
                error: nil,
                sections: sections
            )
        }

        return LessonCheck(
            passed: true,
            headline: "Nice work",
            message: "That does what the exercise asked.",
            expected: nil,
            actual: nil,
            error: nil,
            sections: sections
        )
    }

    private static func inputNote(_ test: LessonTest) -> String {
        guard !test.stdin.isEmpty else { return "" }
        let typed = test.stdin.map { "\"\($0)\"" }.joined(separator: ", ")
        return ", when the answer typed is \(typed)"
    }

    private static func mismatch(message: String, expected: String, actual: String, sections: [OutputSection]) -> LessonCheck {
        LessonCheck(
            passed: false,
            headline: "Not yet",
            message: message,
            expected: expected,
            actual: actual,
            error: nil,
            sections: sections
        )
    }
}

/// Points at the first line where the output is different, in plain words.
enum OutputDiff {
    static func describe(expected: String, actual: String) -> String {
        if actual.isEmpty {
            return "Your program didn't print anything yet. Use print() to show the answer."
        }
        let want = expected.components(separatedBy: "\n")
        let got = actual.components(separatedBy: "\n")
        for index in 0..<max(want.count, got.count) {
            let line = index + 1
            guard index < got.count else {
                return "Your output stops too early. Line \(line) should be \(shown(want[index]))"
            }
            guard index < want.count else {
                return "Your output has an extra line \(line): \(shown(got[index]))"
            }
            if want[index] != got[index] {
                let a = want[index]
                let b = got[index]
                if a.lowercased() == b.lowercased() {
                    return "Line \(line) of the output is close. Check the capital letters: it should be \(a)"
                }
                if a.replacingOccurrences(of: " ", with: "") == b.replacingOccurrences(of: " ", with: "") {
                    return "Line \(line) of the output is close. Check the spaces: it should be \(a)"
                }
                return "Line \(line) of the output is different. It should be \(shown(a)), but yours is \(shown(b))"
            }
        }
        return "The output doesn't match yet."
    }

    /// Shows a line in quotes, and names an empty line in plain words.
    static func shown(_ text: String) -> String {
        text.isEmpty ? "an empty line" : "\"\(text)\""
    }
}
