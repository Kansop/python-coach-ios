import Foundation

enum Badge: String, CaseIterable, Identifiable, Equatable {
    case firstWord
    case printingUnit
    case choicesUnit
    case loopsUnit
    case functionsUnit
    case projectsUnit
    case streak3
    case streak7
    case xp100
    case xp300
    case askedForHelp
    case allLessons

    var id: String { rawValue }

    var title: String {
        switch self {
        case .firstWord: return "First word"
        case .printingUnit: return "Printing complete"
        case .choicesUnit: return "Decision maker"
        case .loopsUnit: return "Looper"
        case .functionsUnit: return "Function maker"
        case .projectsUnit: return "Project builder"
        case .streak3: return "Three-day streak"
        case .streak7: return "Seven-day streak"
        case .xp100: return "100 XP"
        case .xp300: return "300 XP"
        case .askedForHelp: return "Asked for help"
        case .allLessons: return "Python Coach"
        }
    }

    var detail: String {
        switch self {
        case .firstWord: return "Finish the first lesson."
        case .printingUnit: return "Finish the Printing unit."
        case .choicesUnit: return "Finish the Choices unit."
        case .loopsUnit: return "Finish the Loops unit."
        case .functionsUnit: return "Finish the Functions unit."
        case .projectsUnit: return "Finish the Projects unit."
        case .streak3: return "Practice three days in a row."
        case .streak7: return "Practice seven days in a row."
        case .xp100: return "Earn 100 XP."
        case .xp300: return "Earn 300 XP."
        case .askedForHelp: return "Open a hint when you need one."
        case .allLessons: return "Finish every lesson."
        }
    }

    var symbol: String {
        switch self {
        case .firstWord: return "text.bubble.fill"
        case .printingUnit: return "flag.fill"
        case .choicesUnit: return "arrow.triangle.branch"
        case .loopsUnit: return "repeat"
        case .functionsUnit: return "function"
        case .projectsUnit: return "hammer.fill"
        case .streak3, .streak7: return "flame.fill"
        case .xp100, .xp300: return "star.fill"
        case .askedForHelp: return "lightbulb.fill"
        case .allLessons: return "trophy.fill"
        }
    }
}

enum BadgeLogic {
    static func earned(snapshot: ProgressSnapshot, units: [UnitOutline]) -> [Badge] {
        let completed = snapshot.completedIDs
        var badges: [Badge] = []
        if completed.contains("print-hello") {
            badges.append(.firstWord)
        }
        if unitComplete("print", units: units, completed: completed) { badges.append(.printingUnit) }
        if unitComplete("choices", units: units, completed: completed) { badges.append(.choicesUnit) }
        if unitComplete("loops", units: units, completed: completed) { badges.append(.loopsUnit) }
        if unitComplete("functions", units: units, completed: completed) { badges.append(.functionsUnit) }
        if unitComplete("projects", units: units, completed: completed) { badges.append(.projectsUnit) }
        if snapshot.longestStreak >= 3 { badges.append(.streak3) }
        if snapshot.longestStreak >= 7 { badges.append(.streak7) }
        if snapshot.xp >= 100 { badges.append(.xp100) }
        if snapshot.xp >= 300 { badges.append(.xp300) }
        if snapshot.hintsUsed >= 1 { badges.append(.askedForHelp) }
        let allIDs = units.flatMap(\.lessonIDs)
        if !allIDs.isEmpty && allIDs.allSatisfy({ completed.contains($0) }) {
            badges.append(.allLessons)
        }
        return badges
    }

    private static func unitComplete(_ id: String, units: [UnitOutline], completed: Set<String>) -> Bool {
        guard let unit = units.first(where: { $0.id == id }), !unit.lessonIDs.isEmpty else { return false }
        return unit.lessonIDs.allSatisfy { completed.contains($0) }
    }
}
