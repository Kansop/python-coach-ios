import Foundation

enum LessonChecker {
    static func gradeQuiz(lesson: Lesson, choice: Int) -> LessonCheck {
        let correct = choice == lesson.quizAnswer && lesson.quizChoices.indices.contains(choice)
        if correct {
            return LessonCheck(
                passed: true,
                headline: "Nice work",
                message: lesson.quizExplain.isEmpty ? "That is the right answer." : lesson.quizExplain,
                expected: nil,
                actual: nil,
                error: nil,
                sections: []
            )
        }
        let picked = lesson.quizChoices.indices.contains(choice) ? lesson.quizChoices[choice] : "that"
        return LessonCheck(
            passed: false,
            headline: "Not yet",
            message: "\(picked) is not the one. \(lesson.quizExplain)",
            expected: lesson.quizChoices.indices.contains(lesson.quizAnswer) ? lesson.quizChoices[lesson.quizAnswer] : nil,
            actual: lesson.quizChoices.indices.contains(choice) ? lesson.quizChoices[choice] : nil,
            error: nil,
            sections: []
        )
    }

    static func evaluate(source: String, lesson: Lesson, runs: [CapturedRun]) -> LessonCheck {
        let multiple = lesson.tests.count > 1
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
            let error = FriendlyErrors.explain(type: "TimeoutError", message: "timeout", traceback: nil, timedOut: true)
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
                timedOut: false
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

        if runs.count != lesson.tests.count {
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

        for (test, run) in zip(lesson.tests, runs) {
            if let expected = test.stdoutEquals {
                let actual = OutputNormalizer.normalize(run.stdout)
                let wanted = OutputNormalizer.normalize(expected)
                if actual != wanted {
                    return mismatch(
                        message: "The output doesn't match yet.",
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
                        message: "The output is missing something it needs.",
                        expected: wanted,
                        actual: actual,
                        sections: sections
                    )
                }
            }
            for (name, expected) in test.values {
                if let actual = run.values[name] {
                    if actual != expected {
                        return LessonCheck(
                            passed: false,
                            headline: "Not yet",
                            message: "The variable \(name) should be \(expected), but it was \(actual).",
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
                        message: "Create a variable named \(name).",
                        expected: expected,
                        actual: nil,
                        error: nil,
                        sections: sections
                    )
                }
            }
        }

        var missing: [String] = []
        for snippet in lesson.sourceMustContain where !SourceScan.containsSnippet(source, snippet) {
            missing.append(snippet)
        }
        let choice = lesson.sourceMustContainOneOf
        let choiceOK = choice.isEmpty || choice.contains { SourceScan.containsSnippet(source, $0) }
        if !missing.isEmpty || !choiceOK {
            var sentences = missing.map { SourceScan.sentence(for: $0) }
            if !choiceOK, let first = choice.first {
                sentences.append(SourceScan.sentence(for: first))
            }
            return LessonCheck(
                passed: false,
                headline: "Almost",
                message: sentences.joined(separator: " "),
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
