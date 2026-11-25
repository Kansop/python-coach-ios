import SwiftUI

struct UnitDetailView: View {
    let unit: Unit
    @EnvironmentObject private var store: ProgressStore

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 12) {
                Text(unit.summary)
                    .font(AppTheme.rounded(.body))
                    .foregroundStyle(AppTheme.muted)
                ForEach(unit.lessons) { lesson in
                    if store.isUnlocked(lesson.id) {
                        NavigationLink(value: lesson.id) {
                            lessonRow(lesson)
                        }
                        .buttonStyle(PressScaleButtonStyle())
                    } else {
                        lessonRow(lesson)
                            .opacity(0.55)
                    }
                }
            }
            .padding(20)
            .frame(maxWidth: 860)
            .frame(maxWidth: .infinity)
        }
        .background(AppTheme.paper)
        .navigationTitle(unit.title)
        .navigationBarTitleDisplayMode(.large)
    }

    private func lessonRow(_ lesson: Lesson) -> some View {
        let done = store.snapshot.lessons[lesson.id]?.completed == true
        let unlocked = store.isUnlocked(lesson.id)
        return HStack(spacing: 12) {
            Image(systemName: done ? "checkmark.circle.fill" : (unlocked ? "circle" : "lock.fill"))
                .font(.title3)
                .foregroundStyle(done ? AppTheme.success : AppTheme.muted)
                .symbolEffect(.bounce, value: done)
            VStack(alignment: .leading, spacing: 2) {
                Text(lesson.title)
                    .font(AppTheme.rounded(.body, weight: .semibold))
                    .foregroundStyle(AppTheme.ink)
                Text("\(lesson.xp) XP")
                    .font(AppTheme.rounded(.caption))
                    .foregroundStyle(AppTheme.muted)
            }
            Spacer()
            if unlocked {
                Image(systemName: "chevron.right")
                    .font(.footnote.weight(.semibold))
                    .foregroundStyle(AppTheme.muted)
            }
        }
        .padding(14)
        .coachCard()
        .accessibilityElement(children: .combine)
        .accessibilityLabel(unlocked ? lesson.title : "\(lesson.title), locked")
    }
}
