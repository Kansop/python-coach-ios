import XCTest
@testable import PythonCoach

/// Logic tests that need only Foundation. They also build and run on Linux (see README).
final class CoachLogicTests: XCTestCase {
    private var calendar: Calendar {
        var calendar = Calendar(identifier: .gregorian)
        calendar.timeZone = TimeZone(secondsFromGMT: 0)!
        return calendar
    }

    private func day(_ offset: Int) -> Date {
        Date(timeIntervalSince1970: TimeInterval(offset) * 86_400 + 3_600)
    }

    // MARK: Curriculum

    func testCurriculumShape() {
        XCTAssertGreaterThanOrEqual(Curriculum.orderedIDs.count, 80)
        XCTAssertEqual(Curriculum.orderedIDs.count, Set(Curriculum.orderedIDs).count)
        let path = ["start", "print", "variables", "strings", "math", "input", "choices", "loops", "lists", "functions", "dictionaries"]
        XCTAssertEqual(Array(Curriculum.units.map(\.id).prefix(path.count)), path)
        XCTAssertNotNil(Curriculum.lesson(id: "print-hello"))
        for id in ["proj-todo", "proj-grades", "proj-words", "proj-adventure", "proj-bank"] {
            XCTAssertEqual(Curriculum.lesson(id: id)?.isProject, true, id)
        }

        // Bonus units come last, after every core unit.
        let flags = Curriculum.units.map(\.optional)
        XCTAssertTrue(flags.contains(true))
        let firstBonus = flags.firstIndex(of: true)!
        XCTAssertFalse(flags[firstBonus...].contains(false))
        XCTAssertTrue(Curriculum.units.filter(\.optional).flatMap(\.lessons).contains { $0.id == "class-init" })
        XCTAssertTrue(Curriculum.units.filter(\.optional).flatMap(\.lessons).contains { $0.id == "comp-squares" })
        XCTAssertLessThan(Curriculum.coreIDs.count, Curriculum.orderedIDs.count)

        var text = ""
        var predictions = 0
        var keys = Set<String>()
        for unit in Curriculum.units {
            XCTAssertFalse(unit.lessons.isEmpty)
            XCTAssertFalse(unit.symbol.isEmpty)
            text += unit.title + unit.summary
            for lesson in unit.lessons {
                XCTAssertGreaterThan(lesson.xp, 0)
                XCTAssertFalse(lesson.explanation.isEmpty, lesson.id)
                XCTAssertGreaterThanOrEqual(lesson.practices.count, 2, lesson.id)
                if lesson.kind == "lesson" {
                    XCTAssertFalse(lesson.why.isEmpty, lesson.id)
                    XCTAssertTrue(lesson.hasExample, lesson.id)
                    XCTAssertFalse(lesson.walkthrough.isEmpty, lesson.id)
                }
                for step in lesson.walkthrough {
                    XCTAssertTrue(lesson.exampleCode.contains(step.code), "\(lesson.id): \(step.code)")
                }
                text += lesson.title + lesson.explanation + lesson.why
                for practice in lesson.practices {
                    XCTAssertTrue(keys.insert(lesson.practiceKey(practice)).inserted)
                    text += practice.prompt + practice.hints.joined()
                    if practice.isChoice || practice.isPredict {
                        XCTAssertGreaterThanOrEqual(practice.choices.count, 3, lesson.id)
                        XCTAssertTrue(practice.choices.indices.contains(practice.answer), lesson.id)
                        XCTAssertEqual(practice.choices.count, Set(practice.choices).count, lesson.id)
                        if practice.isPredict {
                            predictions += 1
                            XCTAssertFalse(practice.showCode.isEmpty, lesson.id)
                        }
                    } else {
                        XCTAssertFalse(practice.tests.isEmpty, lesson.id)
                        XCTAssertGreaterThanOrEqual(practice.hints.count, 3, lesson.id)
                        for test in practice.tests {
                            let expects = test.stdoutEquals != nil || !test.stdoutContains.isEmpty || !test.values.isEmpty
                            XCTAssertTrue(expects, lesson.id)
                        }
                    }
                }
                if lesson.isProject {
                    XCTAssertTrue(lesson.practices.dropFirst().allSatisfy(\.carryCode), lesson.id)
                }
            }
        }
        XCTAssertGreaterThanOrEqual(predictions, 30)
        XCTAssertFalse(containsEmoji(text))
        XCTAssertGreaterThanOrEqual(Curriculum.totalXP, 800)
    }

    func testFirstPracticeOfEachLessonStartsGently() {
        // Regular lessons open with a fill-in-the-blank, a prediction, a quick question, or a one-spot bug fix.
        for lesson in Curriculum.units.flatMap(\.lessons) where lesson.kind == "lesson" {
            guard let first = lesson.practices.first else { continue }
            let gentle = first.starterCode.contains(LessonChecker.blank) || first.isPredict || first.isChoice || first.isFix
            XCTAssertTrue(gentle, lesson.id)
        }
    }

    func testDecodeRejectsBrokenJSON() {
        XCTAssertThrowsError(try Curriculum.decode("[{\"id\": 1}]"))
        XCTAssertEqual(try Curriculum.decode("[]").count, 0)
    }

    func testPracticeKeys() {
        let key = PracticeKey.make(lessonID: "print-hello", practiceID: "p2")
        XCTAssertEqual(key, "print-hello/p2")
        XCTAssertTrue(PracticeKey.isPracticeKey(key))
        XCTAssertFalse(PracticeKey.isPracticeKey("print-hello"))
        XCTAssertEqual(PracticeKey.split(key)?.lessonID, "print-hello")
        XCTAssertEqual(PracticeKey.split(key)?.practiceID, "p2")
        XCTAssertNil(PracticeKey.split("print-hello"))

        let project = try! XCTUnwrap(Curriculum.lesson(id: "proj-todo"))
        XCTAssertNil(project.practice(before: project.practices[0]))
        XCTAssertEqual(project.practice(before: project.practices[1])?.id, project.practices[0].id)
    }

    func testUnlockOrder() {
        let ids = Curriculum.orderedIDs
        XCTAssertTrue(LessonLock.isUnlocked(lessonID: ids[0], completed: [], orderedIDs: ids))
        XCTAssertFalse(LessonLock.isUnlocked(lessonID: ids[1], completed: [], orderedIDs: ids))
        XCTAssertTrue(LessonLock.isUnlocked(lessonID: ids[1], completed: [ids[0]], orderedIDs: ids))
        XCTAssertTrue(LessonLock.isUnlocked(lessonID: ids[2], completed: [ids[2]], orderedIDs: ids))
        XCTAssertFalse(LessonLock.isUnlocked(lessonID: "missing", completed: [], orderedIDs: ids))
    }

    // MARK: Checking answers

    func testOutputNormalizer() {
        XCTAssertEqual(OutputNormalizer.normalize("Hello \n"), "Hello")
        XCTAssertEqual(OutputNormalizer.normalize("\n\nHello\n\n"), "Hello")
        XCTAssertEqual(OutputNormalizer.normalize("A  \r\nB\r"), "A\nB")
        XCTAssertNotEqual(OutputNormalizer.normalize("Hello"), "hello")
    }

    func testBlankCheck() {
        XCTAssertNil(LessonChecker.blankCheck(source: "print(\"hi\")"))
        let one = LessonChecker.blankCheck(source: "x = 1\nprint(___)")
        XCTAssertEqual(one?.passed, false)
        XCTAssertEqual(one?.headline, "Fill in the blank")
        XCTAssertTrue(one?.message.contains("line 2") == true)
        XCTAssertTrue(one?.message.contains("the blank") == true)
        let two = LessonChecker.blankCheck(source: "___ = ___")
        XCTAssertTrue(two?.message.contains("each blank") == true)
    }

    func testHelloPractice() throws {
        let lesson = try XCTUnwrap(Curriculum.lesson(id: "print-hello"))
        let practice = lesson.practices[0]
        XCTAssertNotNil(LessonChecker.blankCheck(source: practice.starterCode))
        let pass = LessonChecker.evaluate(source: "print(\"I am learning Python\")", practice: practice, runs: [run(stdout: "I am learning Python\n")])
        XCTAssertTrue(pass.passed)
        let spaces = LessonChecker.evaluate(source: "print(\"I am learning Python\")", practice: practice, runs: [run(stdout: "I am learning Python  \n")])
        XCTAssertTrue(spaces.passed)
        let caps = LessonChecker.evaluate(source: "print(\"i am learning python\")", practice: practice, runs: [run(stdout: "i am learning python\n")])
        XCTAssertFalse(caps.passed)
        XCTAssertTrue(caps.message.contains("capital"))
        XCTAssertEqual(caps.expected, "I am learning Python")
        let nothing = LessonChecker.evaluate(source: "", practice: practice, runs: [run(stdout: "")])
        XCTAssertFalse(nothing.passed)
        XCTAssertTrue(nothing.message.contains("print"))
    }

    func testCommentRequiresRealComment() throws {
        let practice = try XCTUnwrap(Curriculum.lesson(id: "print-comments")?.practices[0])
        let onlyPrint = LessonChecker.evaluate(source: "print(\"Hi\")", practice: practice, runs: [run(stdout: "Hi\n")])
        XCTAssertFalse(onlyPrint.passed)
        XCTAssertTrue(onlyPrint.message.contains("#"))
        XCTAssertTrue(LessonChecker.evaluate(source: "# note\nprint(\"Hi\")", practice: practice, runs: [run(stdout: "Hi")]).passed)
        XCTAssertFalse(LessonChecker.evaluate(source: "print(\"#\" and \"Hi\")", practice: practice, runs: [run(stdout: "Hi")]).passed)
    }

    func testValuesTimeoutAndErrors() throws {
        let practice = try XCTUnwrap(Curriculum.lesson(id: "var-name")?.practices[0])
        let wrong = LessonChecker.evaluate(source: "name = \"Bo\"\nprint(\"Ada\")", practice: practice, runs: [run(stdout: "Ada\n", values: ["name": "'Bo'"])])
        XCTAssertFalse(wrong.passed)
        XCTAssertTrue(wrong.message.contains("name"))
        let missing = LessonChecker.evaluate(source: "print(\"Ada\")", practice: practice, runs: [run(stdout: "Ada\n")])
        XCTAssertFalse(missing.passed)
        XCTAssertTrue(missing.message.contains("Make a variable named name"))

        let timed = LessonChecker.evaluate(source: "while True:\n    pass", practice: practice, runs: [run(timedOut: true)])
        XCTAssertFalse(timed.passed)
        XCTAssertEqual(timed.error?.title, "That loop kept going")

        let source = "name = \"Ada\"\nprnt(name)"
        let named = LessonChecker.evaluate(
            source: source,
            practice: practice,
            runs: [run(errorType: "NameError", errorMessage: "name 'prnt' is not defined. Did you mean: 'print'?", traceback: trace(2, "NameError: name 'prnt' is not defined. Did you mean: 'print'?"))]
        )
        XCTAssertFalse(named.passed)
        XCTAssertEqual(named.error?.line, 2)
        XCTAssertEqual(named.error?.lineText, "prnt(name)")
        XCTAssertTrue(named.message.contains("print"))
    }

    func testMultipleChecksNameTheTypedInput() throws {
        let practice = try XCTUnwrap(Curriculum.lesson(id: "input-int")?.practices[1])
        XCTAssertEqual(practice.tests.count, 2)
        let check = LessonChecker.evaluate(
            source: "n = int(input(\"How many cookies? \"))\nprint(n * 3)",
            practice: practice,
            runs: [run(stdout: "How many cookies? 3\n9"), run(stdout: "How many cookies? 5\n15")]
        )
        XCTAssertFalse(check.passed)
        XCTAssertEqual(check.sections.count, 2)
        XCTAssertEqual(check.sections.first?.title, "Check 1")
        XCTAssertTrue(check.message.contains("\"3\""))
        let good = LessonChecker.evaluate(
            source: "n = int(input(\"How many cookies? \"))\nprint(n * 2)",
            practice: practice,
            runs: [run(stdout: "How many cookies? 3\n6\n"), run(stdout: "How many cookies? 5\n10")]
        )
        XCTAssertTrue(good.passed)
        let short = LessonChecker.evaluate(source: "x", practice: practice, runs: [run(stdout: "How many cookies? 3\n6")])
        XCTAssertFalse(short.passed)
    }

    func testChoiceAndPredictionGrading() throws {
        let lessons = Curriculum.units.flatMap(\.lessons)
        let predict = try XCTUnwrap(lessons.flatMap(\.practices).first(where: \.isPredict))
        XCTAssertTrue(LessonChecker.gradeChoice(practice: predict, choice: predict.answer).passed)
        let wrong = predict.answer == 0 ? 1 : 0
        let missed = LessonChecker.gradeChoice(practice: predict, choice: wrong)
        XCTAssertFalse(missed.passed)
        XCTAssertTrue(missed.message.contains("one line at a time"))
        XCTAssertFalse(LessonChecker.gradeChoice(practice: predict, choice: 99).passed)

        let quick = try XCTUnwrap(lessons.flatMap(\.practices).first(where: \.isChoice))
        XCTAssertTrue(LessonChecker.gradeChoice(practice: quick, choice: quick.answer).passed)
        XCTAssertFalse(LessonChecker.gradeChoice(practice: quick, choice: quick.answer == 0 ? 1 : 0).passed)
    }

    func testOutputDiffWording() {
        XCTAssertTrue(OutputDiff.describe(expected: "Hi", actual: "").contains("didn't print anything"))
        XCTAssertTrue(OutputDiff.describe(expected: "Hi\nBye", actual: "Hi").contains("stops too early"))
        XCTAssertTrue(OutputDiff.describe(expected: "Hi", actual: "Hi\nBye").contains("extra line 2"))
        XCTAssertTrue(OutputDiff.describe(expected: "Score: 5", actual: "score: 5").contains("capital"))
        XCTAssertTrue(OutputDiff.describe(expected: "Score: 5", actual: "Score:5").contains("spaces"))
        let different = OutputDiff.describe(expected: "A\nB", actual: "A\nC")
        XCTAssertTrue(different.contains("Line 2"))
        XCTAssertTrue(different.contains("\"B\""))
        XCTAssertTrue(OutputDiff.describe(expected: "A\n\nB", actual: "A\nx\nB").contains("an empty line"))
    }

    func testSourceScanSkipsStringsAndComments() {
        let sample = "message = \"while\"  # note\nif ready:\n    print(f\"hi {message}\")\n"
        XCTAssertFalse(SourceScan.containsSnippet(sample, "while"))
        XCTAssertTrue(SourceScan.containsSnippet(sample, "#"))
        XCTAssertTrue(SourceScan.containsSnippet(sample, "if"))
        XCTAssertFalse(SourceScan.containsSnippet("elif hour < 18:\n    pass", "if"))
        XCTAssertFalse(SourceScan.containsSnippet("print(\"#\")", "#"))
    }

    // MARK: Friendly errors

    func testFriendlyErrorsPointAtTheLine() {
        let source = "name = \"Ada\"\nif name == \"Ada\"\n    print(\"hi\")"
        let colon = FriendlyErrors.explain(type: "SyntaxError", message: "expected ':'", traceback: "  File \"<your code>\", line 2\n    if name == \"Ada\"\n                     ^\nSyntaxError: expected ':'", timedOut: false, source: source)
        XCTAssertEqual(colon.title, "A colon is missing")
        XCTAssertEqual(colon.line, 2)
        XCTAssertEqual(colon.lineText, "if name == \"Ada\"")
        XCTAssertTrue(colon.message.contains("line 2"))
        XCTAssertFalse(colon.tip.isEmpty)

        // The last "<your code>" line wins, so an error inside a function points at the real line.
        let nested = "def half(n):\n    return n / 0\n\nprint(half(4))"
        let divide = FriendlyErrors.explain(type: "ZeroDivisionError", message: "division by zero", traceback: trace(4, "") + "  File \"<your code>\", line 2, in half\nZeroDivisionError: division by zero", timedOut: false, source: nested)
        XCTAssertEqual(divide.line, 2)
        XCTAssertEqual(divide.lineText, "return n / 0")
        XCTAssertEqual(divide.title, "Dividing by zero")
        XCTAssertTrue(divide.message.contains("line 2"))
    }

    func testFriendlyErrorsCoverBeginnerMistakes() {
        func explain(_ type: String, _ message: String, line: Int = 1) -> ErrorExplanation {
            FriendlyErrors.explain(type: type, message: message, traceback: trace(line, "\(type): \(message)"), timedOut: false, source: "x = 1")
        }
        XCTAssertEqual(explain("SyntaxError", "unterminated string literal (detected at line 1)").title, "A quote is missing")
        XCTAssertEqual(explain("SyntaxError", "'(' was never closed").title, "A bracket is still open")
        XCTAssertEqual(explain("SyntaxError", "Missing parentheses in call to 'print'. Did you mean print(...)?").title, "print needs parentheses")
        XCTAssertEqual(explain("SyntaxError", "invalid character '\u{201C}' (U+201C)").title, "Curly quotes sneaked in")
        XCTAssertEqual(explain("IndentationError", "expected an indented block after 'if' statement on line 1").title, "Push this line in")
        XCTAssertEqual(explain("IndentationError", "unexpected indent").title, "This line is pushed in too far")
        XCTAssertTrue(explain("NameError", "name 'scor' is not defined. Did you mean: 'score'?").message.contains("score"))
        XCTAssertTrue(explain("NameError", "name 'true' is not defined").message.contains("True"))
        XCTAssertEqual(explain("TypeError", "can only concatenate str (not \"int\") to str").title, "Text and a number don't add")
        XCTAssertEqual(explain("TypeError", "'<' not supported between instances of 'str' and 'int'").title, "Can't compare those")
        XCTAssertEqual(explain("TypeError", "greet() missing 1 required positional argument: 'name'").title, "The function needs more values")
        XCTAssertEqual(explain("IndexError", "list index out of range").title, "That spot doesn't exist")
        XCTAssertEqual(explain("KeyError", "'age'").title, "That key isn't in the dictionary")
        XCTAssertEqual(explain("ZeroDivisionError", "division by zero").title, "Dividing by zero")
        XCTAssertEqual(explain("ValueError", "invalid literal for int() with base 10: 'abc'").title, "That isn't a whole number")
        XCTAssertEqual(explain("AttributeError", "'list' object has no attribute 'add'").title, "No tool with that name")
        XCTAssertEqual(FriendlyErrors.explain(type: nil, message: nil, traceback: nil, timedOut: true).title, "That loop kept going")
        let unknown = explain("OverflowError", "math range error")
        XCTAssertFalse(unknown.title.isEmpty)
        XCTAssertFalse(unknown.tip.isEmpty)
        XCTAssertTrue(unknown.detail.contains("OverflowError"))
        XCTAssertFalse(FriendlyErrors.encouragement.isEmpty)
    }

    // MARK: Review

    func testReviewCandidatesComeFromFinishedLessons() {
        let units = Curriculum.units
        var snapshot = ProgressSnapshot.empty
        XCTAssertTrue(ReviewPlanner.candidates(snapshot: snapshot, units: units).isEmpty)
        snapshot.lessons["print-hello"] = LessonSnapshot(completed: true, hintsUnlocked: 0, code: "")
        snapshot.lessons["proj-todo"] = LessonSnapshot(completed: true, hintsUnlocked: 0, code: "")
        snapshot.practices["print-hello/p2"] = PracticeSnapshot(passed: true, hintsUnlocked: 0, code: "", misses: 3, lastPracticed: day(1))
        let items = ReviewPlanner.candidates(snapshot: snapshot, units: units)
        XCTAssertEqual(items.count, Curriculum.lesson(id: "print-hello")?.practices.count)
        XCTAssertTrue(items.allSatisfy { $0.lessonID == "print-hello" })
        XCTAssertEqual(items.first { $0.practiceID == "p2" }?.misses, 3)
    }

    func testReviewWeightsFavorMisses() {
        let now = day(30)
        let fresh = ReviewItem(lessonID: "a", practiceID: "p1", misses: 0, lastPracticed: now)
        let missed = ReviewItem(lessonID: "a", practiceID: "p2", misses: 2, lastPracticed: now)
        let old = ReviewItem(lessonID: "a", practiceID: "p3", misses: 0, lastPracticed: day(2))
        let never = ReviewItem(lessonID: "a", practiceID: "p4", misses: 0, lastPracticed: nil)
        let capped = ReviewItem(lessonID: "a", practiceID: "p5", misses: 50, lastPracticed: now)
        XCTAssertEqual(ReviewPlanner.weight(fresh, now: now), 1, accuracy: 0.0001)
        XCTAssertEqual(ReviewPlanner.weight(missed, now: now), 9, accuracy: 0.0001)
        XCTAssertEqual(ReviewPlanner.weight(old, now: now), 3, accuracy: 0.0001)
        XCTAssertEqual(ReviewPlanner.weight(never, now: now), 3, accuracy: 0.0001)
        XCTAssertEqual(ReviewPlanner.weight(capped, now: now), 21, accuracy: 0.0001)

        // Over many sessions, the missed item shows up far more often than the fresh one.
        var counts: [String: Int] = [:]
        for seed in 0..<400 {
            for item in ReviewPlanner.pick([fresh, missed, old], count: 1, now: now, seed: UInt64(seed)) {
                counts[item.practiceID, default: 0] += 1
            }
        }
        XCTAssertGreaterThan(counts["p2", default: 0], counts["p1", default: 0] * 3)
    }

    func testReviewPickIsDeterministicWithoutRepeats() {
        let items = (1...12).map { ReviewItem(lessonID: "l", practiceID: "p\($0)", misses: $0 % 3, lastPracticed: nil) }
        let now = day(5)
        let first = ReviewPlanner.pick(items, now: now, seed: 42)
        XCTAssertEqual(first.count, ReviewPlanner.sessionSize)
        XCTAssertEqual(Set(first.map(\.id)).count, first.count)
        XCTAssertEqual(first, ReviewPlanner.pick(items, now: now, seed: 42))
        XCTAssertEqual(ReviewPlanner.pick(Array(items.prefix(2)), now: now, seed: 1).count, 2)
        XCTAssertTrue(ReviewPlanner.pick([], now: now, seed: 1).isEmpty)
        XCTAssertEqual(ReviewPlanner.daySeed(day(3), calendar: calendar), ReviewPlanner.daySeed(day(3), calendar: calendar))
        XCTAssertNotEqual(ReviewPlanner.daySeed(day(3), calendar: calendar), ReviewPlanner.daySeed(day(4), calendar: calendar))
        var generator = SplitMix64(seed: 7)
        for _ in 0..<100 {
            let value = generator.nextUnit()
            XCTAssertGreaterThanOrEqual(value, 0)
            XCTAssertLessThan(value, 1)
        }
    }

    // MARK: Daily, streaks, levels, badges

    func testDailyChallenge() {
        let calendar = calendar
        let first = DailyChallengeBank.pick(on: day(3), calendar: calendar)
        XCTAssertEqual(first.id, DailyChallengeBank.pick(on: day(3), calendar: calendar).id)
        let practice = first.asPractice()
        XCTAssertEqual(practice.tests, first.tests)
        XCTAssertFalse(practice.isChoice)
        var record = DailyRecord(stamp: "")
        XCTAssertFalse(record.isDone(on: day(3), calendar: calendar))
        record = record.completed(on: day(3), calendar: calendar)
        XCTAssertTrue(record.isDone(on: day(3), calendar: calendar))
        XCTAssertFalse(record.isDone(on: day(4), calendar: calendar))
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
        let gap = StreakLogic.registerActivity(state: next.state, now: day(4), calendar: calendar)
        XCTAssertEqual(gap.state.current, 1)
        XCTAssertEqual(gap.state.longest, 2)
        XCTAssertTrue(gap.reset)
        XCTAssertEqual(StreakLogic.displayStreak(state: next.state, now: day(2), calendar: calendar), 2)
        XCTAssertEqual(StreakLogic.displayStreak(state: next.state, now: day(4), calendar: calendar), 0)
    }

    func testLevelAndBadges() {
        XCTAssertEqual(LevelLogic.level(for: 0), 1)
        XCTAssertEqual(LevelLogic.title(for: 0), "Explorer")
        XCTAssertEqual(LevelLogic.level(for: 40), 2)
        XCTAssertEqual(LevelLogic.fraction(for: 20), 0.5)

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
        // Practice records never count as finished lessons.
        snapshot.practices["print-two-lines/p1"] = PracticeSnapshot(passed: true, hintsUnlocked: 0, code: "", misses: 0, lastPracticed: nil)
        XCTAssertFalse(BadgeLogic.earned(snapshot: snapshot, units: units).contains(.printingUnit))
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
    }

    func testPassedPracticeCount() throws {
        let lesson = try XCTUnwrap(Curriculum.lesson(id: "print-hello"))
        var snapshot = ProgressSnapshot.empty
        XCTAssertEqual(snapshot.passedPractices(in: lesson), 0)
        snapshot.practices[lesson.practiceKey(lesson.practices[0])] = PracticeSnapshot(passed: true, hintsUnlocked: 0, code: "", misses: 0, lastPracticed: nil)
        snapshot.practices[lesson.practiceKey(lesson.practices[1])] = PracticeSnapshot(passed: false, hintsUnlocked: 2, code: "", misses: 1, lastPracticed: nil)
        XCTAssertEqual(snapshot.passedPractices(in: lesson), 1)
    }

    // MARK: Editor and engine plumbing

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
        XCTAssertEqual(kind("3"), .number)
    }

    func testPyodidePathsAndRanges() {
        let resolved = PyodidePaths.resolve(URL(string: "pycoach://local/pyodide/pyodide.asm.wasm")!)
        XCTAssertEqual(resolved?.mime, "application/wasm")
        XCTAssertEqual(kind("pycoach://local/runner.html"), .runner)
        XCTAssertEqual(kind("pycoach://local/worker.js"), .worker)
        XCTAssertEqual(kind("pycoach://local/harness.py"), .harness)
        XCTAssertNil(PyodidePaths.resolve(URL(string: "pycoach://local/pyodide/../runner.html")!))
        XCTAssertNil(PyodidePaths.resolve(URL(string: "https://example.com/pyodide.js")!))
        XCTAssertEqual(ByteRanges.parse("bytes=0-3", length: 10), 0..<4)
        XCTAssertEqual(ByteRanges.parse("bytes=-4", length: 10), 6..<10)
        XCTAssertNil(ByteRanges.parse("bytes=0-1,2-3", length: 10))
    }

    func testWorkerEmbedsHarness() {
        let script = BridgeScripts.workerJavaScript()
        XCTAssertTrue(script.contains("loadPyodide"))
        XCTAssertTrue(script.contains("import sys"))
        XCTAssertTrue(script.contains("_pycoach_result"))
        XCTAssertTrue(PythonHarness.source.contains("<your code>"))
    }

    // MARK: Helpers

    private func kind(_ url: String) -> PyodidePaths.Kind {
        guard let kind = PyodidePaths.resolve(URL(string: url)!)?.kind else {
            XCTFail("missing kind for \(url)")
            return .runner
        }
        return kind
    }

    private func trace(_ line: Int, _ last: String) -> String {
        "Traceback (most recent call last):\n  File \"<string>\", line 66, in <module>\n  File \"<your code>\", line \(line), in <module>\n" + (last.isEmpty ? "" : last + "\n")
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
            stdout: stdout, stderr: "", values: values,
            errorType: errorType, errorMessage: errorMessage, traceback: traceback,
            needsInput: false, inputPrompt: "", timedOut: timedOut, cancelled: false
        )
    }

    private func containsEmoji(_ text: String) -> Bool {
        text.unicodeScalars.contains { $0.properties.isEmojiPresentation }
    }
}
