import Foundation
import SwiftData

@Model
final class LearnerProfile {
    var xp: Int
    var currentStreak: Int
    var longestStreak: Int
    var lastActiveDay: Date?
    var hintsUsed: Int
    @Relationship(deleteRule: .cascade, inverse: \LessonProgress.profile)
    var lessons: [LessonProgress]

    init(
        xp: Int = 0,
        currentStreak: Int = 0,
        longestStreak: Int = 0,
        lastActiveDay: Date? = nil,
        hintsUsed: Int = 0
    ) {
        self.xp = xp
        self.currentStreak = currentStreak
        self.longestStreak = longestStreak
        self.lastActiveDay = lastActiveDay
        self.hintsUsed = hintsUsed
        self.lessons = []
    }
}

@Model
final class LessonProgress {
    var lessonID: String
    var completed: Bool
    var hintsUnlocked: Int
    var code: String
    /// How many times a practice check failed. Review mode brings these back more often.
    var misses: Int = 0
    /// Last time this practice was passed, in a lesson or in review.
    var lastPracticed: Date? = nil
    var profile: LearnerProfile?

    /// `lessonID` is a lesson id, or a practice key such as "print-hello/p1".
    init(lessonID: String, code: String, completed: Bool = false, hintsUnlocked: Int = 0) {
        self.lessonID = lessonID
        self.code = code
        self.completed = completed
        self.hintsUnlocked = hintsUnlocked
        self.misses = 0
        self.lastPracticed = nil
    }
}

enum AppModelContainer {
    static func make() -> ModelContainer {
        do {
            return try ModelContainer(for: LearnerProfile.self, LessonProgress.self)
        } catch {
            let memory = ModelConfiguration(isStoredInMemoryOnly: true)
            do {
                return try ModelContainer(for: LearnerProfile.self, LessonProgress.self, configurations: memory)
            } catch {
                fatalError("Could not open local progress storage: \(error)")
            }
        }
    }
}
