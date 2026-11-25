import Foundation

struct LessonSnapshot: Equatable {
    var completed: Bool
    var hintsUnlocked: Int
    var code: String
}

struct ProgressSnapshot: Equatable {
    var xp: Int
    var streak: Int
    var longestStreak: Int
    var lastActiveDay: Date?
    var hintsUsed: Int
    var lessons: [String: LessonSnapshot]

    static let empty = ProgressSnapshot(
        xp: 0,
        streak: 0,
        longestStreak: 0,
        lastActiveDay: nil,
        hintsUsed: 0,
        lessons: [:]
    )

    var completedIDs: Set<String> {
        Set(lessons.compactMap { $0.value.completed ? $0.key : nil })
    }

    var completedCount: Int {
        completedIDs.count
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
