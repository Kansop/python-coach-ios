import Combine
import Foundation
import SwiftData

final class ProgressStore: ObservableObject {
    @Published private(set) var snapshot: ProgressSnapshot
    private let context: ModelContext
    private var profile: LearnerProfile

    init(context: ModelContext) {
        self.context = context
        let profile = Self.loadOrCreate(context: context)
        self.profile = profile
        self.snapshot = Self.makeSnapshot(from: profile)
    }

    /// The code to show for a practice: what the learner last typed, or the starter.
    /// Project steps that carry code start from the learner's passing code of the step before.
    func code(for practice: Practice, in lesson: Lesson) -> String {
        let key = lesson.practiceKey(practice)
        if let saved = snapshot.practices[key] {
            return saved.code
        }
        if practice.carryCode, let previous = lesson.practice(before: practice) {
            let previousKey = lesson.practiceKey(previous)
            if let earlier = snapshot.practices[previousKey], earlier.passed,
               !earlier.code.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
                return earlier.code
            }
        }
        return practice.starterCode
    }

    func hintsUnlocked(forKey key: String) -> Int {
        snapshot.practices[key]?.hintsUnlocked ?? 0
    }

    func isPracticePassed(_ key: String) -> Bool {
        snapshot.practices[key]?.passed == true
    }

    func isLessonCompleted(_ lessonID: String) -> Bool {
        snapshot.lessons[lessonID]?.completed == true
    }

    func isUnlocked(_ lessonID: String) -> Bool {
        LessonLock.isUnlocked(
            lessonID: lessonID,
            completed: snapshot.completedIDs,
            orderedIDs: Curriculum.orderedIDs
        )
    }

    func nextLessonID() -> String? {
        for id in Curriculum.orderedIDs {
            let done = snapshot.lessons[id]?.completed == true
            if !done && isUnlocked(id) {
                return id
            }
        }
        return nil
    }

    func completedCount(in unit: Unit) -> Int {
        unit.lessons.filter { snapshot.lessons[$0.id]?.completed == true }.count
    }

    func saveCode(key: String, code: String, starter: String) {
        let record = record(id: key, starter: starter)
        guard record.code != code else { return }
        record.code = code
        publish()
    }

    @discardableResult
    func revealNextHint(key: String, total: Int, starter: String) -> Int {
        let record = record(id: key, starter: starter)
        guard record.hintsUnlocked < total else { return record.hintsUnlocked }
        record.hintsUnlocked += 1
        profile.hintsUsed += 1
        publish()
        return record.hintsUnlocked
    }

    /// A failed check. Review mode brings practices with misses back more often.
    func recordMiss(key: String, starter: String) {
        let record = record(id: key, starter: starter)
        record.misses += 1
        publish()
    }

    /// Marks one practice as passed. Returns true the first time.
    @discardableResult
    func recordPracticePass(key: String, code: String, starter: String, now: Date = Date()) -> Bool {
        let record = record(id: key, starter: starter)
        let first = !record.completed
        record.completed = true
        record.code = code
        record.lastPracticed = now
        publish()
        return first
    }

    /// A review item passed. Getting it right on the first try lowers its weight.
    func recordReviewPass(key: String, firstTry: Bool, now: Date = Date(), calendar: Calendar = .current) -> Int {
        let record = record(id: key, starter: "")
        if firstTry {
            record.misses = max(0, record.misses - 1)
        }
        record.lastPracticed = now
        registerStreak(now: now, calendar: calendar)
        let gained = firstTry ? ReviewPlanner.xpPerItem : 1
        profile.xp += gained
        publish()
        return gained
    }

    func recordPass(lesson: Lesson, now: Date = Date(), calendar: Calendar = .current) -> CompletionResult {
        let beforeLevel = LevelLogic.level(for: snapshot.xp)
        let beforeBadges = BadgeLogic.earned(snapshot: snapshot, units: Curriculum.outlines)
        let record = record(id: lesson.id, starter: "")
        let already = record.completed
        var gained = 0
        if !already {
            record.completed = true
            profile.xp += lesson.xp
            gained = lesson.xp
        }
        let update = StreakLogic.registerActivity(
            state: StreakState(
                current: profile.currentStreak,
                longest: profile.longestStreak,
                lastActiveDay: profile.lastActiveDay
            ),
            now: now,
            calendar: calendar
        )
        profile.currentStreak = update.state.current
        profile.longestStreak = update.state.longest
        profile.lastActiveDay = update.state.lastActiveDay
        publish()

        let afterBadges = BadgeLogic.earned(snapshot: snapshot, units: Curriculum.outlines)
        let newBadges = Badge.allCases.filter { afterBadges.contains($0) && !beforeBadges.contains($0) }
        let level = LevelLogic.level(for: snapshot.xp)
        var finishedUnit: String?
        if !already, let unit = Curriculum.unit(containing: lesson.id) {
            let done = unit.lessons.allSatisfy { snapshot.lessons[$0.id]?.completed == true }
            if done {
                finishedUnit = unit.title
            }
        }
        return CompletionResult(
            xpGained: gained,
            totalXP: snapshot.xp,
            leveledUp: level > beforeLevel,
            level: level,
            levelTitle: LevelLogic.title(for: snapshot.xp),
            streak: update.state.current,
            streakIncreased: update.increased,
            streakReset: update.reset,
            newBadges: newBadges,
            finishedUnitTitle: finishedUnit,
            alreadyCompleted: already
        )
    }

    func dailyRecord() -> DailyRecord {
        DailyRecord(stamp: UserDefaults.standard.string(forKey: Self.dailyKey) ?? "")
    }

    func markDailyDone(xp: Int, now: Date = Date(), calendar: Calendar = .current) -> Bool {
        let record = dailyRecord()
        if record.isDone(on: now, calendar: calendar) {
            return false
        }
        let update = StreakLogic.registerActivity(
            state: StreakState(
                current: profile.currentStreak,
                longest: profile.longestStreak,
                lastActiveDay: profile.lastActiveDay
            ),
            now: now,
            calendar: calendar
        )
        profile.currentStreak = update.state.current
        profile.longestStreak = update.state.longest
        profile.lastActiveDay = update.state.lastActiveDay
        profile.xp += xp
        UserDefaults.standard.set(record.completed(on: now, calendar: calendar).stamp, forKey: Self.dailyKey)
        publish()
        return true
    }

    func reset() {
        let profiles = (try? context.fetch(FetchDescriptor<LearnerProfile>())) ?? []
        profiles.forEach { context.delete($0) }
        let lessons = (try? context.fetch(FetchDescriptor<LessonProgress>())) ?? []
        lessons.forEach { context.delete($0) }
        let fresh = LearnerProfile()
        context.insert(fresh)
        profile = fresh
        publish()
    }

    private static let dailyKey = "dailyCompletedStamp"

    private func registerStreak(now: Date, calendar: Calendar) {
        let update = StreakLogic.registerActivity(
            state: StreakState(
                current: profile.currentStreak,
                longest: profile.longestStreak,
                lastActiveDay: profile.lastActiveDay
            ),
            now: now,
            calendar: calendar
        )
        profile.currentStreak = update.state.current
        profile.longestStreak = update.state.longest
        profile.lastActiveDay = update.state.lastActiveDay
    }

    private func record(id: String, starter: String) -> LessonProgress {
        if let existing = profile.lessons.first(where: { $0.lessonID == id }) {
            return existing
        }
        let created = LessonProgress(lessonID: id, code: starter)
        context.insert(created)
        profile.lessons.append(created)
        return created
    }

    private func publish() {
        try? context.save()
        snapshot = Self.makeSnapshot(from: profile)
    }

    private static func loadOrCreate(context: ModelContext) -> LearnerProfile {
        if let existing = try? context.fetch(FetchDescriptor<LearnerProfile>()), let first = existing.first {
            return first
        }
        let profile = LearnerProfile()
        context.insert(profile)
        try? context.save()
        return profile
    }

    private static func makeSnapshot(from profile: LearnerProfile) -> ProgressSnapshot {
        var lessons: [String: LessonSnapshot] = [:]
        var practices: [String: PracticeSnapshot] = [:]
        for record in profile.lessons {
            if PracticeKey.isPracticeKey(record.lessonID) {
                practices[record.lessonID] = PracticeSnapshot(
                    passed: record.completed,
                    hintsUnlocked: record.hintsUnlocked,
                    code: record.code,
                    misses: record.misses,
                    lastPracticed: record.lastPracticed
                )
            } else {
                lessons[record.lessonID] = LessonSnapshot(
                    completed: record.completed,
                    hintsUnlocked: record.hintsUnlocked,
                    code: record.code
                )
            }
        }
        return ProgressSnapshot(
            xp: profile.xp,
            streak: profile.currentStreak,
            longestStreak: profile.longestStreak,
            lastActiveDay: profile.lastActiveDay,
            hintsUsed: profile.hintsUsed,
            lessons: lessons,
            practices: practices
        )
    }
}
