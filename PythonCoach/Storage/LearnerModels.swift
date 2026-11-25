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
    var profile: LearnerProfile?

    init(lessonID: String, code: String, completed: Bool = false, hintsUnlocked: Int = 0) {
        self.lessonID = lessonID
        self.code = code
        self.completed = completed
        self.hintsUnlocked = hintsUnlocked
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
