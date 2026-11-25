import SwiftUI

struct LessonMapView: View {
    @EnvironmentObject private var store: ProgressStore
    @Environment(\.horizontalSizeClass) private var sizeClass

    var body: some View {
        VStack(alignment: .leading, spacing: 18) {
            ForEach(Curriculum.units) { unit in
                VStack(alignment: .leading, spacing: 8) {
                    HStack {
                        Image(systemName: unit.symbol)
                            .foregroundStyle(AppTheme.accent)
                            .accessibilityHidden(true)
                        Text(unit.title)
                            .font(AppTheme.rounded(.headline, weight: .bold))
                            .foregroundStyle(AppTheme.ink)
                        Spacer()
                        Text("\(store.completedCount(in: unit))/\(unit.lessons.count)")
                            .font(AppTheme.rounded(.caption, weight: .semibold))
                            .foregroundStyle(AppTheme.muted)
                            .monospacedDigit()
                    }
                    LazyVGrid(columns: columns, spacing: 10) {
                        ForEach(unit.lessons) { lesson in
                            node(lesson)
                        }
                    }
                }
            }
        }
    }

    private var columns: [GridItem] {
        if sizeClass == .regular {
            return Array(repeating: GridItem(.flexible(), spacing: 10), count: 8)
        }
        return Array(repeating: GridItem(.flexible(), spacing: 10), count: 4)
    }

    @ViewBuilder
    private func node(_ lesson: Lesson) -> some View {
        let done = store.snapshot.lessons[lesson.id]?.completed == true
        let unlocked = store.isUnlocked(lesson.id)
        let symbol = done ? "checkmark" : (lesson.isQuiz ? "questionmark" : (lesson.isFix ? "ladybug" : "circle.fill"))
        let label = "\(lesson.title), \(done ? "complete" : (unlocked ? "ready" : "locked"))"
        if unlocked {
            NavigationLink(value: lesson.id) {
                nodeFace(symbol: symbol, done: done, locked: false)
            }
            .buttonStyle(PressScaleButtonStyle())
            .accessibilityLabel(label)
        } else {
            nodeFace(symbol: "lock.fill", done: false, locked: true)
                .accessibilityLabel(label)
        }
    }

    private func nodeFace(symbol: String, done: Bool, locked: Bool) -> some View {
        Image(systemName: symbol)
            .font(.footnote.weight(.bold))
            .foregroundStyle(done ? AppTheme.onAccent : (locked ? AppTheme.muted : AppTheme.accent))
            .frame(maxWidth: .infinity)
            .frame(height: 44)
            .background(done ? AppTheme.success : AppTheme.card)
            .clipShape(RoundedRectangle(cornerRadius: 12, style: .continuous))
            .overlay(
                RoundedRectangle(cornerRadius: 12, style: .continuous)
                    .stroke(AppTheme.line, lineWidth: 1)
            )
    }
}
