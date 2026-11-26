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
                if unit.optional {
                    Label("Bonus unit. These are extra ideas for when you feel ready. You don't need them for the main path.", systemImage: "sparkles")
                        .font(AppTheme.rounded(.subheadline))
                        .foregroundStyle(AppTheme.accent)
                }
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

    private func rowDetail(_ lesson: Lesson) -> String {
        let count = lesson.practices.count
        let what: String
        if lesson.isProject {
            what = "Project, \(count) steps"
        } else if lesson.isCheckpoint {
            what = "Checkpoint, \(count) questions"
        } else {
            what = count == 1 ? "1 practice" : "\(count) practices"
        }
        return "\(what) · \(lesson.xp) XP"
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
                Text(rowDetail(lesson))
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
