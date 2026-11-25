import Foundation

struct StreakState: Equatable {
    var current: Int
    var longest: Int
    var lastActiveDay: Date?

    static let empty = StreakState(current: 0, longest: 0, lastActiveDay: nil)
}

struct StreakUpdate: Equatable {
    var state: StreakState
    var increased: Bool
    var reset: Bool
}

enum StreakLogic {
    /// Completing a lesson counts for today. Same-day repeats do not grow the streak.
    static func registerActivity(state: StreakState, now: Date, calendar: Calendar) -> StreakUpdate {
        let today = calendar.startOfDay(for: now)
        guard let last = state.lastActiveDay else {
            let next = StreakState(current: 1, longest: max(state.longest, 1), lastActiveDay: today)
            return StreakUpdate(state: next, increased: true, reset: false)
        }
        let lastDay = calendar.startOfDay(for: last)
        if lastDay > today {
            var copy = state
            copy.lastActiveDay = today
            return StreakUpdate(state: copy, increased: false, reset: false)
        }
        if calendar.isDate(lastDay, inSameDayAs: today) {
            return StreakUpdate(state: state, increased: false, reset: false)
        }
        if let yesterday = calendar.date(byAdding: .day, value: -1, to: today),
           calendar.isDate(lastDay, inSameDayAs: yesterday) {
            let current = state.current + 1
            let next = StreakState(current: current, longest: max(state.longest, current), lastActiveDay: today)
            return StreakUpdate(state: next, increased: true, reset: false)
        }
        let next = StreakState(current: 1, longest: state.longest, lastActiveDay: today)
        return StreakUpdate(state: next, increased: false, reset: state.current > 0)
    }

    /// The number to show. A gap of more than one day pauses the streak until the next lesson.
    static func displayStreak(state: StreakState, now: Date, calendar: Calendar) -> Int {
        guard state.current > 0, let last = state.lastActiveDay else { return 0 }
        let today = calendar.startOfDay(for: now)
        let lastDay = calendar.startOfDay(for: last)
        if calendar.isDate(lastDay, inSameDayAs: today) {
            return state.current
        }
        if let yesterday = calendar.date(byAdding: .day, value: -1, to: today),
           calendar.isDate(lastDay, inSameDayAs: yesterday) {
            return state.current
        }
        return 0
    }

    static func message(state: StreakState, now: Date, calendar: Calendar) -> String {
        let shown = displayStreak(state: state, now: now, calendar: calendar)
        guard let last = state.lastActiveDay else {
            return "Finish a lesson to start your streak."
        }
        let today = calendar.startOfDay(for: now)
        let lastDay = calendar.startOfDay(for: last)
        if calendar.isDate(lastDay, inSameDayAs: today) {
            return shown == 1 ? "You started a streak today." : "You practiced today."
        }
        if shown > 0 {
            return "Practice today to keep the streak."
        }
        return "Your streak paused. Finish a lesson to start a new one."
    }
}
