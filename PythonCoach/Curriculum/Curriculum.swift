import Foundation

struct Unit: Codable, Hashable, Identifiable {
    var id: String
    var title: String
    var summary: String
    var symbol: String
    /// Bonus units sit at the end of the path. They are for later, not required.
    var optional: Bool
    var lessons: [Lesson]
}

/// A new word the lesson introduces, with an everyday comparison.
struct Term: Codable, Hashable {
    var word: String
    var meaning: String
    var like: String
}

/// One line of the worked example and what it does.
struct WalkStep: Codable, Hashable {
    var code: String
    var note: String
}

/// A mistake beginners often make, why it goes wrong, and the fix.
struct Mistake: Codable, Hashable {
    var wrong: String
    var why: String
    var fix: String
}

struct Lesson: Codable, Hashable, Identifiable {
    var id: String
    var title: String
    /// "lesson", "project", or "checkpoint".
    var kind: String
    var xp: Int
    var terms: [Term]
    var explanation: String
    var why: String
    var exampleCode: String
    var exampleNote: String
    var walkthrough: [WalkStep]
    var mistakes: [Mistake]
    var practices: [Practice]

    var isProject: Bool { kind == "project" }
    var isCheckpoint: Bool { kind == "checkpoint" }
    var hasExample: Bool { !exampleCode.isEmpty }

    func practiceKey(_ practice: Practice) -> String {
        PracticeKey.make(lessonID: id, practiceID: practice.id)
    }

    func practice(id practiceID: String) -> Practice? {
        practices.first { $0.id == practiceID }
    }

    func practice(before practice: Practice) -> Practice? {
        guard let index = practices.firstIndex(where: { $0.id == practice.id }), index > 0 else { return nil }
        return practices[index - 1]
    }
}

/// One thing the learner does: write code, fix a bug, predict output, or answer a quick question.
struct Practice: Codable, Hashable, Identifiable {
    var id: String
    /// "code", "fix", "predict", or "choice".
    var kind: String
    var prompt: String
    var starterCode: String
    /// Code shown for a prediction question.
    var showCode: String
    var hints: [String]
    var sourceMustContain: [String]
    var sourceMustContainOneOf: [String]
    var tests: [LessonTest]
    var choices: [String]
    var answer: Int
    var explain: String
    /// Project steps start from the learner's own code from the step before.
    var carryCode: Bool

    var isChoice: Bool { kind == "predict" || kind == "choice" }
    var isPredict: Bool { kind == "predict" }
    var isFix: Bool { kind == "fix" }
}

struct LessonTest: Codable, Hashable {
    var stdin: [String]
    var appendCode: String?
    var stdoutEquals: String?
    var stdoutContains: [String]
    var values: [String: String]
}

enum PracticeKey {
    static let separator: Character = "/"

    static func make(lessonID: String, practiceID: String) -> String {
        "\(lessonID)\(separator)\(practiceID)"
    }

    static func isPracticeKey(_ key: String) -> Bool {
        key.contains(separator)
    }

    static func split(_ key: String) -> (lessonID: String, practiceID: String)? {
        guard let index = key.firstIndex(of: separator) else { return nil }
        let lessonID = String(key[key.startIndex..<index])
        let practiceID = String(key[key.index(after: index)...])
        guard !lessonID.isEmpty, !practiceID.isEmpty else { return nil }
        return (lessonID, practiceID)
    }
}

struct UnitOutline: Equatable {
    var id: String
    var title: String
    var lessonIDs: [String]
}

enum Curriculum {
    static let units: [Unit] = loadUnits()

    static let lessonsByID: [String: Lesson] = {
        var map: [String: Lesson] = [:]
        for unit in units {
            for lesson in unit.lessons {
                map[lesson.id] = lesson
            }
        }
        return map
    }()

    static let orderedIDs: [String] = units.flatMap { $0.lessons.map(\.id) }

    static var outlines: [UnitOutline] {
        units.map { UnitOutline(id: $0.id, title: $0.title, lessonIDs: $0.lessons.map(\.id)) }
    }

    /// Lessons in units that are not bonus units.
    static var coreIDs: [String] {
        units.filter { !$0.optional }.flatMap { $0.lessons.map(\.id) }
    }

    static var totalXP: Int {
        units.flatMap(\.lessons).reduce(0) { $0 + $1.xp }
    }

    static func lesson(id: String) -> Lesson? {
        lessonsByID[id]
    }

    static func unit(containing lessonID: String) -> Unit? {
        units.first { unit in unit.lessons.contains { $0.id == lessonID } }
    }

    static func nextLesson(after lessonID: String) -> Lesson? {
        let ids = orderedIDs
        guard let index = ids.firstIndex(of: lessonID), index + 1 < ids.count else { return nil }
        return lesson(id: ids[index + 1])
    }

    static func decode(_ text: String) throws -> [Unit] {
        try JSONDecoder().decode([Unit].self, from: Data(text.utf8))
    }

    private static func loadUnits() -> [Unit] {
        do {
            return try decode(CurriculumJSON.text)
        } catch {
            fatalError("Curriculum failed to decode: \(error)")
        }
    }
}

enum LessonLock {
    static func isUnlocked(lessonID: String, completed: Set<String>, orderedIDs: [String]) -> Bool {
        if completed.contains(lessonID) { return true }
        guard let index = orderedIDs.firstIndex(of: lessonID) else { return false }
        if index == 0 { return true }
        return completed.contains(orderedIDs[index - 1])
    }
}
