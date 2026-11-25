import Foundation

struct LessonSnapshot: Equatable {
    var completed: Bool
    var hintsUnlocked: Int
    var code: String
}

struct PracticeSnapshot: Equatable {
    var passed: Bool
    var hintsUnlocked: Int
    var code: String
    var misses: Int
    var lastPracticed: Date?
}

struct ProgressSnapshot: Equatable {
    var xp: Int
    var streak: Int
    var longestStreak: Int
    var lastActiveDay: Date?
    var hintsUsed: Int
    var lessons: [String: LessonSnapshot]
    /// Keyed by practice key, for example "print-hello/p1".
    var practices: [String: PracticeSnapshot] = [:]

    static let empty = ProgressSnapshot(
        xp: 0,
        streak: 0,
        longestStreak: 0,
        lastActiveDay: nil,
        hintsUsed: 0,
        lessons: [:],
        practices: [:]
    )

    var completedIDs: Set<String> {
        Set(lessons.compactMap { $0.value.completed ? $0.key : nil })
    }

    var completedCount: Int {
        completedIDs.count
    }

    func passedPractices(in lesson: Lesson) -> Int {
        lesson.practices.filter { practices[lesson.practiceKey($0)]?.passed == true }.count
    }
}

struct CompletionResult: Equatable {
    var xpGained: Int
    var totalXP: Int
    var leveledUp: Bool
    var level: Int
    var levelTitle: String
    var streak: Int
    var streakIncreased: Bool
    var streakReset: Bool
    var newBadges: [Badge]
    var finishedUnitTitle: String?
    var alreadyCompleted: Bool
}
