import Foundation

struct Unit: Codable, Hashable, Identifiable {
    var id: String
    var title: String
    var summary: String
    var symbol: String
    var lessons: [Lesson]
}

struct Lesson: Codable, Hashable, Identifiable {
    var id: String
    var title: String
    var explanation: String
    var exampleCode: String
    var exampleNote: String
    var exercise: String
    var starterCode: String
    var hints: [String]
    var sourceMustContain: [String]
    var sourceMustContainOneOf: [String]
    var xp: Int
    var tests: [LessonTest]
}

struct LessonTest: Codable, Hashable {
    var stdin: [String]
    var appendCode: String?
    var stdoutEquals: String?
    var stdoutContains: [String]
    var values: [String: String]
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

    static var orderedIDs: [String] {
        units.flatMap { $0.lessons.map(\.id) }
    }

    static var outlines: [UnitOutline] {
        units.map { UnitOutline(id: $0.id, title: $0.title, lessonIDs: $0.lessons.map(\.id)) }
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

    private static func loadUnits() -> [Unit] {
        do {
            return try JSONDecoder().decode([Unit].self, from: Data(CurriculumJSON.text.utf8))
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
