import Foundation

enum LevelLogic {
    static let step = 40
    static let titles = [
        "Explorer",
        "Scripter",
        "Collector",
        "Calculator",
        "Question Asker",
        "Decider",
        "Looper",
        "List Builder",
        "Function Maker",
        "Lookup Pro",
        "Builder",
        "Python Coach"
    ]

    static func level(for xp: Int) -> Int {
        max(0, xp) / step + 1
    }

    static func title(for xp: Int) -> String {
        let index = min(level(for: xp) - 1, titles.count - 1)
        return titles[max(0, index)]
    }

    /// Progress inside the current level, from 0 to 1.
    static func fraction(for xp: Int) -> Double {
        let safe = max(0, xp)
        return Double(safe % step) / Double(step)
    }
}
