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
    var kind: String
    var quizChoices: [String]
    var quizAnswer: Int
    var quizExplain: String
    var tests: [LessonTest]

    var isQuiz: Bool { kind == "quiz" }
    var isFix: Bool { kind == "fix" }

    private enum CodingKeys: String, CodingKey {
        case id, title, explanation, exampleCode, exampleNote, exercise, starterCode, hints
        case sourceMustContain, sourceMustContainOneOf, xp, kind, quizChoices, quizAnswer, quizExplain, tests
    }

    init(
        id: String,
        title: String,
        explanation: String,
        exampleCode: String,
        exampleNote: String,
        exercise: String,
        starterCode: String,
        hints: [String],
        sourceMustContain: [String],
        sourceMustContainOneOf: [String],
        xp: Int,
        kind: String,
        quizChoices: [String],
        quizAnswer: Int,
        quizExplain: String,
        tests: [LessonTest]
    ) {
        self.id = id
        self.title = title
        self.explanation = explanation
        self.exampleCode = exampleCode
        self.exampleNote = exampleNote
        self.exercise = exercise
        self.starterCode = starterCode
        self.hints = hints
        self.sourceMustContain = sourceMustContain
        self.sourceMustContainOneOf = sourceMustContainOneOf
        self.xp = xp
        self.kind = kind
        self.quizChoices = quizChoices
        self.quizAnswer = quizAnswer
        self.quizExplain = quizExplain
        self.tests = tests
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        id = try container.decode(String.self, forKey: .id)
        title = try container.decode(String.self, forKey: .title)
        explanation = try container.decode(String.self, forKey: .explanation)
        exampleCode = try container.decode(String.self, forKey: .exampleCode)
        exampleNote = try container.decode(String.self, forKey: .exampleNote)
        exercise = try container.decode(String.self, forKey: .exercise)
        starterCode = try container.decode(String.self, forKey: .starterCode)
        hints = try container.decode([String].self, forKey: .hints)
        sourceMustContain = try container.decode([String].self, forKey: .sourceMustContain)
        sourceMustContainOneOf = try container.decode([String].self, forKey: .sourceMustContainOneOf)
        xp = try container.decode(Int.self, forKey: .xp)
        kind = try container.decodeIfPresent(String.self, forKey: .kind) ?? "code"
        quizChoices = try container.decodeIfPresent([String].self, forKey: .quizChoices) ?? []
        quizAnswer = try container.decodeIfPresent(Int.self, forKey: .quizAnswer) ?? -1
        quizExplain = try container.decodeIfPresent(String.self, forKey: .quizExplain) ?? ""
        tests = try container.decodeIfPresent([LessonTest].self, forKey: .tests) ?? []
    }

    func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encode(id, forKey: .id)
        try container.encode(title, forKey: .title)
        try container.encode(explanation, forKey: .explanation)
        try container.encode(exampleCode, forKey: .exampleCode)
        try container.encode(exampleNote, forKey: .exampleNote)
        try container.encode(exercise, forKey: .exercise)
        try container.encode(starterCode, forKey: .starterCode)
        try container.encode(hints, forKey: .hints)
        try container.encode(sourceMustContain, forKey: .sourceMustContain)
        try container.encode(sourceMustContainOneOf, forKey: .sourceMustContainOneOf)
        try container.encode(xp, forKey: .xp)
        try container.encode(kind, forKey: .kind)
        try container.encode(quizChoices, forKey: .quizChoices)
        try container.encode(quizAnswer, forKey: .quizAnswer)
        try container.encode(quizExplain, forKey: .quizExplain)
        try container.encode(tests, forKey: .tests)
    }
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
