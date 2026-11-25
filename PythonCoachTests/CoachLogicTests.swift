import XCTest
@testable import PythonCoach

final class CoachLogicTests: XCTestCase {
    private var calendar: Calendar {
        var calendar = Calendar(identifier: .gregorian)
        calendar.timeZone = TimeZone(secondsFromGMT: 0)!
        return calendar
    }

    private func day(_ offset: Int) -> Date {
        Date(timeIntervalSince1970: TimeInterval(offset) * 86_400 + 3_600)
    }

    func testCurriculumShape() {
        XCTAssertGreaterThanOrEqual(Curriculum.orderedIDs.count, 30)
        XCTAssertEqual(Curriculum.orderedIDs.count, Set(Curriculum.orderedIDs).count)
        XCTAssertEqual(Curriculum.units.count, 11)
        let requiredUnits = ["print", "variables", "strings", "math", "input", "choices", "loops", "lists", "functions", "dictionaries", "projects"]
        XCTAssertEqual(Curriculum.units.map(\.id), requiredUnits)
        XCTAssertNotNil(Curriculum.lesson(id: "print-hello"))
        XCTAssertNotNil(Curriculum.lesson(id: "proj-quiz"))
        var text = ""
        for unit in Curriculum.units {
            XCTAssertFalse(unit.lessons.isEmpty)
            XCTAssertFalse(unit.symbol.isEmpty)
            text += unit.title + unit.summary
            for lesson in unit.lessons {
                XCTAssertGreaterThanOrEqual(lesson.hints.count, 2)
                XCTAssertFalse(lesson.tests.isEmpty)
                XCTAssertFalse(lesson.explanation.isEmpty)
                XCTAssertFalse(lesson.exampleCode.isEmpty)
                XCTAssertFalse(lesson.exercise.isEmpty)
                XCTAssertFalse(lesson.starterCode.isEmpty)
                XCTAssertGreaterThan(lesson.xp, 0)
                text += lesson.explanation + lesson.exercise + lesson.hints.joined() + lesson.title
                for test in lesson.tests {
                    let hasExpect = test.stdoutEquals != nil || !test.stdoutContains.isEmpty || !test.values.isEmpty
                    XCTAssertTrue(hasExpect, lesson.id)
                }
            }
        }
        XCTAssertFalse(containsEmoji(text))
        XCTAssertEqual(Curriculum.totalXP, 480)
    }

    func testUnlockOrder() {
        let ids = Curriculum.orderedIDs
        XCTAssertTrue(LessonLock.isUnlocked(lessonID: ids[0], completed: [], orderedIDs: ids))
        XCTAssertFalse(LessonLock.isUnlocked(lessonID: ids[1], completed: [], orderedIDs: ids))
        XCTAssertTrue(LessonLock.isUnlocked(lessonID: ids[1], completed: [ids[0]], orderedIDs: ids))
        XCTAssertTrue(LessonLock.isUnlocked(lessonID: ids[2], completed: [ids[2]], orderedIDs: ids))
        XCTAssertFalse(LessonLock.isUnlocked(lessonID: "missing", completed: [], orderedIDs: ids))
    }

    func testOutputNormalizer() {
        XCTAssertEqual(OutputNormalizer.normalize("Hello \n"), "Hello")
        XCTAssertEqual(OutputNormalizer.normalize("\n\nHello\n\n"), "Hello")
        XCTAssertEqual(OutputNormalizer.normalize("A  \r\nB\r"), "A\nB")
        XCTAssertEqual(OutputNormalizer.normalize("  keep\n"), "keep")
        XCTAssertNotEqual(OutputNormalizer.normalize("Hello"), "hello")
    }

    func testHelloLessonCheck() throws {
        let lesson = try XCTUnwrap(Curriculum.lesson(id: "print-hello"))
        let pass = LessonChecker.evaluate(
            source: "print(\"I am learning Python\")",
            lesson: lesson,
            runs: [run(stdout: "I am learning Python\n")]
        )
        XCTAssertTrue(pass.passed)
        let extraSpace = LessonChecker.evaluate(
            source: "print(\"I am learning Python\")",
            lesson: lesson,
            runs: [run(stdout: "I am learning Python  \n")]
        )
        XCTAssertTrue(extraSpace.passed)
        let fail = LessonChecker.evaluate(
            source: lesson.starterCode,
            lesson: lesson,
            runs: [run(stdout: "\n")]
        )
        XCTAssertFalse(fail.passed)
        XCTAssertEqual(fail.expected, "I am learning Python")
    }

    func testCommentRequiresRealComment() throws {
        let lesson = try XCTUnwrap(Curriculum.lesson(id: "print-comments"))
        let onlyPrint = LessonChecker.evaluate(
            source: "print(\"Ready\")",
            lesson: lesson,
            runs: [run(stdout: "Ready\n")]
        )
        XCTAssertFalse(onlyPrint.passed)
        XCTAssertTrue(onlyPrint.message.contains("#"))
        let withComment = LessonChecker.evaluate(
            source: "# note\nprint(\"Ready\")",
            lesson: lesson,
            runs: [run(stdout: "Ready")]
        )
        XCTAssertTrue(withComment.passed)
        let hashInString = LessonChecker.evaluate(
            source: "print(\"# Ready\")",
            lesson: lesson,
            runs: [run(stdout: "Ready")]
        )
        XCTAssertFalse(hashInString.passed)
    }

    func testValueAndTimeoutAndNameError() throws {
        let lesson = try XCTUnwrap(Curriculum.lesson(id: "var-name"))
        let wrong = LessonChecker.evaluate(
            source: "snack = \"soup\"\nprint(snack)",
            lesson: lesson,
            runs: [run(stdout: "soup\n", values: ["snack": "'soup'"])]
        )
        XCTAssertFalse(wrong.passed)
        XCTAssertTrue(wrong.message.contains("snack"))
        let missing = LessonChecker.evaluate(
            source: "print(\"tacos\")",
            lesson: lesson,
            runs: [run(stdout: "tacos\n")]
        )
        XCTAssertFalse(missing.passed)
        XCTAssertTrue(missing.message.contains("snack"))

        let timed = LessonChecker.evaluate(
            source: "while True:\n    pass",
            lesson: lesson,
            runs: [run(timedOut: true)]
        )
        XCTAssertFalse(timed.passed)
        XCTAssertEqual(timed.error?.title, "That ran too long")

        let named = LessonChecker.evaluate(
            source: "print(prnt)",
            lesson: lesson,
            runs: [run(errorType: "NameError", errorMessage: "name 'prnt' is not defined", traceback: "File \"<your code>\", line 1\nNameError: name 'prnt' is not defined")]
        )
        XCTAssertFalse(named.passed)
        XCTAssertTrue(named.message.contains("print"))
        XCTAssertEqual(named.error?.line, 1)
    }

    func testMultipleChecksStopOnFirstMismatchMessage() throws {
        let lesson = try XCTUnwrap(Curriculum.lesson(id: "proj-quiz"))
        XCTAssertEqual(lesson.tests.count, 2)
        let check = LessonChecker.evaluate(
            source: "print('nope')",
            lesson: lesson,
            runs: [
                run(stdout: "wrong"),
                run(stdout: "also wrong")
            ]
        )
        XCTAssertFalse(check.passed)
        XCTAssertEqual(check.sections.count, 2)
    }

    func testSourceScanSkipsStringsAndComments() {
        let sample = "message = \"while\"  # note\nif ready:\n    print(f\"hi {message}\")\n"
        XCTAssertFalse(SourceScan.containsSnippet(sample, "while"))
        XCTAssertTrue(SourceScan.containsSnippet(sample, "#"))
        XCTAssertTrue(SourceScan.containsSnippet(sample, "f\""))
        XCTAssertTrue(SourceScan.containsSnippet(sample, "if"))
        XCTAssertFalse(SourceScan.containsSnippet("elif hour < 18:\n    pass", "if"))
        XCTAssertTrue(SourceScan.containsSnippet("elif hour < 18:\n    pass", "elif"))
        XCTAssertFalse(SourceScan.containsSnippet("print(\"#\")", "#"))
    }

    func testSyntaxHighlighter() {
        let code = "print(\"hi\") # note\nif True:\n    x = 3"
        let tokens = SyntaxHighlighter.tokens(in: code)
        func kind(_ word: String) -> TokenKind? {
            tokens.first { String(code[$0.range]) == word }?.kind
        }
        XCTAssertEqual(kind("print"), .builtin)
        XCTAssertEqual(kind("\"hi\""), .string)
        XCTAssertEqual(kind("# note"), .comment)
        XCTAssertEqual(kind("if"), .keyword)
        XCTAssertEqual(kind("True"), .keyword)
        XCTAssertEqual(kind("3"), .number)
        let inside = "name = \"if\""
        let insideTokens = SyntaxHighlighter.tokens(in: inside)
        XCTAssertFalse(insideTokens.contains { String(inside[$0.range]) == "if" && $0.kind == .keyword })
    }

    func testFriendlyErrors() {
        let syntax = FriendlyErrors.explain(
            type: "SyntaxError",
            message: "'(' was never closed (<your code>, line 2)",
            traceback: "SyntaxError: '(' was never closed",
            timedOut: false
        )
        XCTAssertEqual(syntax.line, 2)
        XCTAssertTrue(syntax.message.contains("quotes") || syntax.message.contains("parentheses"))

        let divide = FriendlyErrors.explain(type: "ZeroDivisionError", message: "division by zero", traceback: nil, timedOut: false)
        XCTAssertTrue(divide.message.lowercased().contains("zero"))

        let indent = FriendlyErrors.explain(type: "IndentationError", message: "expected an indented block", traceback: nil, timedOut: false)
        XCTAssertTrue(indent.message.contains("4 spaces"))

        let mixed = FriendlyErrors.explain(
            type: "TypeError",
            message: "can only concatenate str (not \"int\") to str",
            traceback: nil,
            timedOut: false
        )
        XCTAssertTrue(mixed.message.contains("f-string") || mixed.message.contains("str"))
    }

    func testStreakLogic() {
        let calendar = calendar
        let first = StreakLogic.registerActivity(state: .empty, now: day(0), calendar: calendar)
        XCTAssertEqual(first.state.current, 1)
        XCTAssertTrue(first.increased)

        let sameDay = StreakLogic.registerActivity(state: first.state, now: day(0), calendar: calendar)
        XCTAssertEqual(sameDay.state.current, 1)
        XCTAssertFalse(sameDay.increased)

        let next = StreakLogic.registerActivity(state: first.state, now: day(1), calendar: calendar)
        XCTAssertEqual(next.state.current, 2)
        XCTAssertEqual(next.state.longest, 2)
        XCTAssertTrue(next.increased)

        let gap = StreakLogic.registerActivity(state: next.state, now: day(4), calendar: calendar)
        XCTAssertEqual(gap.state.current, 1)
        XCTAssertEqual(gap.state.longest, 2)
        XCTAssertTrue(gap.reset)
        XCTAssertEqual(StreakLogic.displayStreak(state: next.state, now: day(1), calendar: calendar), 2)
        XCTAssertEqual(StreakLogic.displayStreak(state: next.state, now: day(2), calendar: calendar), 2)
        XCTAssertEqual(StreakLogic.displayStreak(state: next.state, now: day(4), calendar: calendar), 0)
        XCTAssertTrue(StreakLogic.message(state: .empty, now: day(0), calendar: calendar).contains("streak"))
    }

    func testLevelAndBadges() {
        XCTAssertEqual(LevelLogic.level(for: 0), 1)
        XCTAssertEqual(LevelLogic.title(for: 0), "Explorer")
        XCTAssertEqual(LevelLogic.fraction(for: 0), 0)
        XCTAssertEqual(LevelLogic.level(for: 40), 2)
        XCTAssertEqual(LevelLogic.fraction(for: 20), 0.5)
        XCTAssertEqual(LevelLogic.title(for: 440), "Python Coach")

        let units = [
            UnitOutline(id: "print", title: "Printing", lessonIDs: ["print-hello", "print-two-lines"]),
            UnitOutline(id: "choices", title: "Choices", lessonIDs: ["if-basic"])
        ]
        var snapshot = ProgressSnapshot.empty
        XCTAssertTrue(BadgeLogic.earned(snapshot: snapshot, units: units).isEmpty)
        snapshot.lessons["print-hello"] = LessonSnapshot(completed: true, hintsUnlocked: 0, code: "")
        snapshot.xp = 10
        snapshot.longestStreak = 1
        var badges = BadgeLogic.earned(snapshot: snapshot, units: units)
        XCTAssertTrue(badges.contains(.firstWord))
        XCTAssertFalse(badges.contains(.printingUnit))
        snapshot.lessons["print-two-lines"] = LessonSnapshot(completed: true, hintsUnlocked: 0, code: "")
        snapshot.lessons["if-basic"] = LessonSnapshot(completed: true, hintsUnlocked: 1, code: "")
        snapshot.xp = 120
        snapshot.longestStreak = 7
        snapshot.hintsUsed = 1
        badges = BadgeLogic.earned(snapshot: snapshot, units: units)
        XCTAssertTrue(badges.contains(.printingUnit))
        XCTAssertTrue(badges.contains(.choicesUnit))
        XCTAssertTrue(badges.contains(.streak7))
        XCTAssertTrue(badges.contains(.xp100))
        XCTAssertTrue(badges.contains(.askedForHelp))
        XCTAssertTrue(badges.contains(.allLessons))
        snapshot.longestStreak = 7
        snapshot.streak = 0
        XCTAssertTrue(BadgeLogic.earned(snapshot: snapshot, units: units).contains(.streak7))
    }

    func testPyodidePathsAndRanges() {
        let wasm = URL(string: "pycoach://local/pyodide/pyodide.asm.wasm")!
        let resolved = PyodidePaths.resolve(wasm)
        XCTAssertEqual(resolved?.mime, "application/wasm")
        if case .runtime(let name) = resolved?.kind {
            XCTAssertEqual(name, "pyodide.asm.wasm")
        } else {
            XCTFail("expected a runtime file")
        }
        XCTAssertEqual(kind("pycoach://local/runner.html"), .runner)
        XCTAssertEqual(kind("pycoach://local/worker.js"), .worker)
        XCTAssertEqual(kind("pycoach://local/harness.py"), .harness)
        XCTAssertNil(PyodidePaths.resolve(URL(string: "pycoach://local/pyodide/../runner.html")!))
        XCTAssertNil(PyodidePaths.resolve(URL(string: "https://example.com/pyodide.js")!))
        XCTAssertNil(PyodidePaths.resolve(URL(string: "pycoach://local/pyodide/evil.sh")!))
        XCTAssertEqual(kind("pycoach://local/pyodide/pyodide.js?cache=1"), .runtime("pyodide.js"))

        XCTAssertEqual(ByteRanges.parse("bytes=0-3", length: 10), 0..<4)
        XCTAssertEqual(ByteRanges.parse("bytes=2-", length: 10), 2..<10)
        XCTAssertEqual(ByteRanges.parse("bytes=-4", length: 10), 6..<10)
        XCTAssertNil(ByteRanges.parse("bytes=0-1,2-3", length: 10))
        XCTAssertNil(ByteRanges.parse("items=0-1", length: 10))
    }

    func testCacheValidation() throws {
        let folder = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString, isDirectory: true)
        try FileManager.default.createDirectory(at: folder, withIntermediateDirectories: true)
        defer { try? FileManager.default.removeItem(at: folder) }
        let wasm = folder.appendingPathComponent("pyodide.asm.wasm")
        var bytes = Data([0x00, 0x61, 0x73, 0x6d, 0x01, 0x02])
        try bytes.write(to: wasm)
        XCTAssertTrue(PyodideCache.validate(url: wasm, name: "pyodide.asm.wasm", minBytes: 4))
        XCTAssertFalse(PyodideCache.validate(url: wasm, name: "pyodide.asm.wasm", minBytes: 100))
        let bad = folder.appendingPathComponent("nope.wasm")
        try Data([0x01, 0x02, 0x03, 0x04]).write(to: bad)
        XCTAssertFalse(PyodideCache.validate(url: bad, name: "nope.wasm", minBytes: 4))
        let zip = folder.appendingPathComponent("python_stdlib.zip")
        try Data([0x50, 0x4b, 0x03, 0x04]).write(to: zip)
        XCTAssertTrue(PyodideCache.validate(url: zip, name: "python_stdlib.zip", minBytes: 4))
    }

    func testWorkerEmbedsHarness() {
        let script = BridgeScripts.workerJavaScript()
        XCTAssertTrue(script.contains("loadPyodide"))
        XCTAssertTrue(script.contains("import sys"))
        XCTAssertTrue(script.contains("_pycoach_result"))
        XCTAssertFalse(script.contains("__HARNESS_JSON__"))
        XCTAssertTrue(BridgeScripts.runnerHTML.contains("pycoachRun"))
        XCTAssertTrue(BridgeScripts.runnerHTML.contains("new Worker"))
    }

    func testProgressStoreAwardsOnceAndKeepsStreak() throws {
        let configuration = ModelConfiguration(isStoredInMemoryOnly: true)
        let container = try ModelContainer(for: LearnerProfile.self, LessonProgress.self, configurations: configuration)
        let store = ProgressStore(context: container.mainContext)
        let lesson = try XCTUnwrap(Curriculum.lesson(id: "print-hello"))
        let calendar = calendar
        let first = store.recordPass(lesson: lesson, now: day(10), calendar: calendar)
        XCTAssertEqual(first.xpGained, 10)
        XCTAssertEqual(store.snapshot.xp, 10)
        XCTAssertEqual(store.snapshot.streak, 1)
        XCTAssertTrue(first.newBadges.contains(.firstWord))
        XCTAssertEqual(first.finishedUnitTitle, nil)

        let again = store.recordPass(lesson: lesson, now: day(10), calendar: calendar)
        XCTAssertEqual(again.xpGained, 0)
        XCTAssertEqual(store.snapshot.xp, 10)
        XCTAssertTrue(again.alreadyCompleted)
        XCTAssertEqual(store.snapshot.streak, 1)

        let nextLesson = try XCTUnwrap(Curriculum.lesson(id: "print-two-lines"))
        let second = store.recordPass(lesson: nextLesson, now: day(11), calendar: calendar)
        XCTAssertEqual(second.streak, 2)
        XCTAssertTrue(second.streakIncreased)
        XCTAssertEqual(store.snapshot.xp, 20)

        store.saveCode(lessonID: lesson.id, code: "print('saved')", starter: lesson.starterCode)
        XCTAssertEqual(store.code(for: lesson), "print('saved')")
        let reloaded = ProgressStore(context: container.mainContext)
        XCTAssertEqual(reloaded.snapshot.xp, 20)
        XCTAssertEqual(reloaded.code(for: lesson), "print('saved')")
        XCTAssertEqual(reloaded.revealNextHint(for: lesson), 1)
        XCTAssertEqual(reloaded.snapshot.hintsUsed, 1)
        XCTAssertEqual(reloaded.revealNextHint(for: lesson), 2)
        let maxHints = lesson.hints.count
        var count = 2
        while count < maxHints {
            count = reloaded.revealNextHint(for: lesson)
        }
        XCTAssertEqual(reloaded.revealNextHint(for: lesson), maxHints)
        XCTAssertEqual(reloaded.snapshot.hintsUsed, maxHints)

        reloaded.reset()
        XCTAssertEqual(reloaded.snapshot.xp, 0)
        XCTAssertEqual(reloaded.snapshot.completedCount, 0)
        XCTAssertFalse(reloaded.isUnlocked(nextLesson.id))
        XCTAssertTrue(reloaded.isUnlocked(lesson.id))
    }

    private func kind(_ url: String) -> PyodidePaths.Kind {
        guard let kind = PyodidePaths.resolve(URL(string: url)!)?.kind else {
            XCTFail("missing kind for \(url)")
            return .runner
        }
        return kind
    }

    private func run(
        stdout: String = "",
        values: [String: String] = [:],
        errorType: String? = nil,
        errorMessage: String? = nil,
        traceback: String? = nil,
        timedOut: Bool = false
    ) -> CapturedRun {
        CapturedRun(
            stdout: stdout,
            stderr: "",
            values: values,
            errorType: errorType,
            errorMessage: errorMessage,
            traceback: traceback,
            needsInput: false,
            inputPrompt: "",
            timedOut: timedOut,
            cancelled: false
        )
    }

    private func containsEmoji(_ text: String) -> Bool {
        text.unicodeScalars.contains { $0.properties.isEmojiPresentation }
    }
}
