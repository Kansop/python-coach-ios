import SwiftData
import XCTest
@testable import PythonCoach

/// Tests that need SwiftData, Combine, or the app's file storage. These run in Xcode on iOS.
final class ProgressStoreTests: XCTestCase {
    private var calendar: Calendar {
        var calendar = Calendar(identifier: .gregorian)
        calendar.timeZone = TimeZone(secondsFromGMT: 0)!
        return calendar
    }

    private func day(_ offset: Int) -> Date {
        Date(timeIntervalSince1970: TimeInterval(offset) * 86_400 + 3_600)
    }

    @MainActor
    private func makeContainer() throws -> ModelContainer {
        let configuration = ModelConfiguration(isStoredInMemoryOnly: true)
        return try ModelContainer(for: LearnerProfile.self, LessonProgress.self, configurations: configuration)
    }

    @MainActor
    func testLessonPassAwardsOnceAndKeepsStreak() throws {
        let container = try makeContainer()
        let store = ProgressStore(context: container.mainContext)
        let lesson = try XCTUnwrap(Curriculum.lesson(id: "print-hello"))
        let first = store.recordPass(lesson: lesson, now: day(10), calendar: calendar)
        XCTAssertEqual(first.xpGained, lesson.xp)
        XCTAssertEqual(store.snapshot.xp, lesson.xp)
        XCTAssertEqual(store.snapshot.streak, 1)
        XCTAssertTrue(first.newBadges.contains(.firstWord))

        let again = store.recordPass(lesson: lesson, now: day(10), calendar: calendar)
        XCTAssertEqual(again.xpGained, 0)
        XCTAssertTrue(again.alreadyCompleted)

        let next = try XCTUnwrap(Curriculum.lesson(id: "print-two-lines"))
        let second = store.recordPass(lesson: next, now: day(11), calendar: calendar)
        XCTAssertEqual(second.streak, 2)
        XCTAssertTrue(second.streakIncreased)
        XCTAssertTrue(store.isLessonCompleted(next.id))
    }

    @MainActor
    func testPracticeCodeHintsAndMisses() throws {
        let container = try makeContainer()
        let store = ProgressStore(context: container.mainContext)
        let lesson = try XCTUnwrap(Curriculum.lesson(id: "print-hello"))
        let practice = lesson.practices[1]
        let key = lesson.practiceKey(practice)

        XCTAssertEqual(store.code(for: practice, in: lesson), practice.starterCode)
        store.saveCode(key: key, code: "print('saved')", starter: practice.starterCode)
        XCTAssertEqual(store.code(for: practice, in: lesson), "print('saved')")

        XCTAssertEqual(store.revealNextHint(key: key, total: practice.hints.count, starter: practice.starterCode), 1)
        XCTAssertEqual(store.hintsUnlocked(forKey: key), 1)
        for _ in 0..<10 {
            store.revealNextHint(key: key, total: practice.hints.count, starter: practice.starterCode)
        }
        XCTAssertEqual(store.hintsUnlocked(forKey: key), practice.hints.count)
        XCTAssertEqual(store.snapshot.hintsUsed, practice.hints.count)

        store.recordMiss(key: key, starter: practice.starterCode)
        store.recordMiss(key: key, starter: practice.starterCode)
        XCTAssertEqual(store.snapshot.practices[key]?.misses, 2)
        XCTAssertFalse(store.isPracticePassed(key))

        XCTAssertTrue(store.recordPracticePass(key: key, code: "print(\"Python is fun\")", starter: practice.starterCode, now: day(3)))
        XCTAssertFalse(store.recordPracticePass(key: key, code: "print(\"Python is fun\")", starter: practice.starterCode, now: day(3)))
        XCTAssertTrue(store.isPracticePassed(key))
        XCTAssertEqual(store.snapshot.practices[key]?.lastPracticed, day(3))

        // Practice records never count as finished lessons.
        XCTAssertEqual(store.snapshot.completedCount, 0)
        XCTAssertNil(store.snapshot.lessons[key])
        XCTAssertEqual(store.snapshot.passedPractices(in: lesson), 1)

        let reloaded = ProgressStore(context: container.mainContext)
        XCTAssertEqual(reloaded.snapshot.practices[key]?.misses, 2)
        XCTAssertEqual(reloaded.code(for: practice, in: lesson), "print(\"Python is fun\")")
    }

    @MainActor
    func testProjectStepsCarryCodeForward() throws {
        let container = try makeContainer()
        let store = ProgressStore(context: container.mainContext)
        let project = try XCTUnwrap(Curriculum.lesson(id: "proj-todo"))
        let step1 = project.practices[0]
        let step2 = project.practices[1]
        XCTAssertTrue(step2.carryCode)

        XCTAssertEqual(store.code(for: step2, in: project), step2.starterCode)
        let mine = "todos = [\"a\"]\nfor task in todos:\n    print(\"-\", task)"
        store.saveCode(key: project.practiceKey(step1), code: mine, starter: step1.starterCode)
        // Not passed yet, so nothing carries.
        XCTAssertEqual(store.code(for: step2, in: project), step2.starterCode)
        store.recordPracticePass(key: project.practiceKey(step1), code: mine, starter: step1.starterCode)
        XCTAssertEqual(store.code(for: step2, in: project), mine)

        // Once step 2 has its own saved code, that wins.
        store.saveCode(key: project.practiceKey(step2), code: mine + "\n# more", starter: mine)
        XCTAssertEqual(store.code(for: step2, in: project), mine + "\n# more")
    }

    @MainActor
    func testReviewPassLowersMissesAndAwardsXP() throws {
        let container = try makeContainer()
        let store = ProgressStore(context: container.mainContext)
        let key = "print-hello/p1"
        store.recordMiss(key: key, starter: "")
        store.recordMiss(key: key, starter: "")
        let gained = store.recordReviewPass(key: key, firstTry: true, now: day(20), calendar: calendar)
        XCTAssertEqual(gained, ReviewPlanner.xpPerItem)
        XCTAssertEqual(store.snapshot.practices[key]?.misses, 1)
        XCTAssertEqual(store.snapshot.practices[key]?.lastPracticed, day(20))
        XCTAssertEqual(store.snapshot.streak, 1)
        XCTAssertEqual(store.recordReviewPass(key: key, firstTry: false, now: day(20), calendar: calendar), 1)
        XCTAssertEqual(store.snapshot.practices[key]?.misses, 1)
        XCTAssertEqual(store.snapshot.xp, ReviewPlanner.xpPerItem + 1)
    }

    @MainActor
    func testResetClearsEverything() throws {
        let container = try makeContainer()
        let store = ProgressStore(context: container.mainContext)
        let lesson = try XCTUnwrap(Curriculum.lesson(id: "print-hello"))
        _ = store.recordPass(lesson: lesson, now: day(1), calendar: calendar)
        store.recordMiss(key: lesson.practiceKey(lesson.practices[0]), starter: "")
        store.reset()
        XCTAssertEqual(store.snapshot.xp, 0)
        XCTAssertEqual(store.snapshot.completedCount, 0)
        XCTAssertTrue(store.snapshot.practices.isEmpty)
        XCTAssertTrue(store.isUnlocked(Curriculum.orderedIDs[0]))
        XCTAssertFalse(store.isUnlocked(Curriculum.orderedIDs[1]))
    }

    @MainActor
    func testSoundIsOffByDefault() {
        // The test host has no saved choice, so the registered defaults apply.
        UserDefaults.standard.removeObject(forKey: UserSettings.sound)
        UserDefaults.standard.removeObject(forKey: UserSettings.haptics)
        UserSettings.registerDefaults()
        XCTAssertFalse(UserSettings.soundEnabled)
        XCTAssertTrue(UserSettings.hapticsEnabled)
    }

    @MainActor
    func testPlaygroundLibrary() throws {
        let folder = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString, isDirectory: true)
        try FileManager.default.createDirectory(at: folder, withIntermediateDirectories: true)
        defer { try? FileManager.default.removeItem(at: folder) }
        let library = PlaygroundLibrary(directory: folder)
        library.save(title: "Demo", code: "print(1)")
        let again = PlaygroundLibrary(directory: folder)
        XCTAssertEqual(again.snippets.count, 1)
        XCTAssertEqual(again.snippets.first?.code, "print(1)")
        if let id = again.snippets.first?.id {
            again.delete(id)
        }
        XCTAssertTrue(PlaygroundLibrary(directory: folder).snippets.isEmpty)
    }

    @MainActor
    func testCacheValidation() throws {
        let folder = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString, isDirectory: true)
        try FileManager.default.createDirectory(at: folder, withIntermediateDirectories: true)
        defer { try? FileManager.default.removeItem(at: folder) }
        let wasm = folder.appendingPathComponent("pyodide.asm.wasm")
        try Data([0x00, 0x61, 0x73, 0x6d, 0x01, 0x02]).write(to: wasm)
        XCTAssertTrue(PyodideCache.validate(url: wasm, name: "pyodide.asm.wasm", minBytes: 4))
        XCTAssertFalse(PyodideCache.validate(url: wasm, name: "pyodide.asm.wasm", minBytes: 100))
        let bad = folder.appendingPathComponent("nope.wasm")
        try Data([0x01, 0x02, 0x03, 0x04]).write(to: bad)
        XCTAssertFalse(PyodideCache.validate(url: bad, name: "nope.wasm", minBytes: 4))
    }
}
