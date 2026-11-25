import SwiftUI

struct ReviewRoute: Hashable {
    var id = "review"
}

/// Brings back practices from finished lessons. Ones you missed come back more often.
struct ReviewView: View {
    @EnvironmentObject private var store: ProgressStore
    @Environment(\.dismiss) private var dismiss

    @State private var items: [ReviewItem] = []
    @State private var index = 0
    @State private var firstTry = 0
    @State private var xpGained = 0
    @State private var finished = false
    @State private var round: UInt64 = 0
    @State private var loaded = false

    var body: some View {
        Group {
            if !loaded {
                Color.clear
            } else if items.isEmpty {
                emptyState
            } else if finished {
                summary
            } else if let pair = current {
                PracticePanel(
                    lesson: pair.0,
                    practice: pair.1,
                    number: index + 1,
                    total: items.count,
                    mode: .review,
                    continueTitle: index + 1 < items.count ? "Next (\(index + 2) of \(items.count))" : "See how you did",
                    onSolved: { first in
                        let item = items[index]
                        xpGained += store.recordReviewPass(key: item.id, firstTry: first)
                        if first { firstTry += 1 }
                    },
                    onContinue: advance,
                    onBack: nil
                )
                .id("\(round)-\(index)-\(items[index].id)")
            } else {
                emptyState
            }
        }
        .background(AppTheme.paper)
        .navigationTitle("Review")
        .navigationBarTitleDisplayMode(.inline)
        .toolbar(.hidden, for: .tabBar)
        .onAppear {
            guard !loaded else { return }
            loaded = true
            plan()
        }
    }

    private var current: (Lesson, Practice)? {
        guard items.indices.contains(index) else { return nil }
        let item = items[index]
        guard let lesson = Curriculum.lesson(id: item.lessonID), let practice = lesson.practice(id: item.practiceID) else { return nil }
        return (lesson, practice)
    }

    private var emptyState: some View {
        VStack(alignment: .leading, spacing: 14) {
            Image(systemName: "arrow.triangle.2.circlepath")
                .font(.system(size: 40))
                .foregroundStyle(AppTheme.accent)
                .accessibilityHidden(true)
            Text("Nothing to review yet")
                .font(AppTheme.rounded(.title2, weight: .bold))
                .foregroundStyle(AppTheme.ink)
            Text("Finish a lesson first. Review brings back practice from lessons you've finished, so the ideas stick. The ones you found tricky come back more often.")
                .font(AppTheme.rounded(.body))
                .foregroundStyle(AppTheme.muted)
                .fixedSize(horizontal: false, vertical: true)
            Spacer()
        }
        .padding(24)
        .frame(maxWidth: 640)
        .frame(maxWidth: .infinity, alignment: .leading)
    }

    private var summary: some View {
        VStack(alignment: .leading, spacing: 16) {
            Image(systemName: "checkmark.seal.fill")
                .font(.system(size: 44))
                .foregroundStyle(AppTheme.success)
                .accessibilityHidden(true)
            Text("Review done")
                .font(AppTheme.rounded(.largeTitle, weight: .bold))
                .foregroundStyle(AppTheme.ink)
            Text("You got \(firstTry) of \(items.count) right on the first try and earned \(xpGained) XP.")
                .font(AppTheme.rounded(.title3))
                .foregroundStyle(AppTheme.ink)
                .fixedSize(horizontal: false, vertical: true)
            Text(firstTry == items.count
                 ? "Those ideas are sticking. Nice."
                 : "The ones you missed will come back in a later review. Practicing them again is how they stick.")
                .font(AppTheme.rounded(.body))
                .foregroundStyle(AppTheme.muted)
                .fixedSize(horizontal: false, vertical: true)
            Spacer()
            PrimaryButton(title: "Review more", systemImage: "arrow.triangle.2.circlepath") {
                round += 1
                plan()
            }
            Button("Done") { dismiss() }
                .font(AppTheme.rounded(.body, weight: .semibold))
                .foregroundStyle(AppTheme.muted)
                .frame(maxWidth: .infinity)
        }
        .padding(24)
        .frame(maxWidth: 640)
        .frame(maxWidth: .infinity, alignment: .leading)
    }

    private func plan() {
        let now = Date()
        let candidates = ReviewPlanner.candidates(snapshot: store.snapshot, units: Curriculum.units)
        let seed = ReviewPlanner.daySeed(now, calendar: .current) &+ round &* 7919
        items = ReviewPlanner.pick(candidates, now: now, seed: seed)
        index = 0
        firstTry = 0
        xpGained = 0
        finished = false
    }

    private func advance() {
        if index + 1 < items.count {
            index += 1
        } else {
            finished = true
        }
    }
}
