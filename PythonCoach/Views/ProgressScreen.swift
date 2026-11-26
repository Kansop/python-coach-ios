import SwiftUI

struct ProgressScreen: View {
    @EnvironmentObject private var store: ProgressStore

    private var earned: [Badge] {
        BadgeLogic.earned(snapshot: store.snapshot, units: Curriculum.outlines)
    }

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    levelCard
                    stats
                    Text("Badges")
                        .font(AppTheme.rounded(.title3, weight: .bold))
                        .foregroundStyle(AppTheme.ink)
                    LazyVGrid(columns: [GridItem(.flexible(), spacing: 12), GridItem(.flexible(), spacing: 12)], spacing: 12) {
                        ForEach(Badge.allCases) { badge in
                            badgeCard(badge, unlocked: earned.contains(badge))
                        }
                    }
                }
                .padding(20)
            }
            .background(AppTheme.paper)
            .navigationTitle("Progress")
        }
    }

    private var levelCard: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Level \(LevelLogic.level(for: store.snapshot.xp))")
                .font(AppTheme.rounded(.title, weight: .bold))
                .foregroundStyle(AppTheme.ink)
            Text(LevelLogic.title(for: store.snapshot.xp))
                .font(AppTheme.rounded(.headline))
                .foregroundStyle(AppTheme.accent)
            XPBar(fraction: LevelLogic.fraction(for: store.snapshot.xp))
            Text("\(store.snapshot.xp) / \(Curriculum.totalXP) XP along the path")
                .font(AppTheme.rounded(.caption, weight: .semibold))
                .foregroundStyle(AppTheme.muted)
        }
        .padding(16)
        .coachCard()
    }

    private var stats: some View {
        HStack(spacing: 12) {
            stat("Lessons", value: "\(store.snapshot.completedCount)/\(Curriculum.orderedIDs.count)", symbol: "book.fill")
            stat("Longest", value: "\(store.snapshot.longestStreak)", symbol: "flame.fill")
            stat("Hints", value: "\(store.snapshot.hintsUsed)", symbol: "lightbulb.fill")
        }
    }

    private func stat(_ title: String, value: String, symbol: String) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            Image(systemName: symbol)
                .foregroundStyle(AppTheme.accent)
            Text(value)
                .font(AppTheme.rounded(.headline, weight: .bold))
                .foregroundStyle(AppTheme.ink)
                .monospacedDigit()
            Text(title)
                .font(AppTheme.rounded(.caption))
                .foregroundStyle(AppTheme.muted)
        }
        .padding(12)
        .frame(maxWidth: .infinity, alignment: .leading)
        .coachCard()
    }

    private func badgeCard(_ badge: Badge, unlocked: Bool) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Image(systemName: unlocked ? badge.symbol : "lock.fill")
                .font(.title2)
                .foregroundStyle(unlocked ? AppTheme.accent : AppTheme.muted)
            Text(badge.title)
                .font(AppTheme.rounded(.subheadline, weight: .bold))
                .foregroundStyle(AppTheme.ink)
                .fixedSize(horizontal: false, vertical: true)
            Text(badge.detail)
                .font(AppTheme.rounded(.caption))
                .foregroundStyle(AppTheme.muted)
                .fixedSize(horizontal: false, vertical: true)
        }
        .padding(14)
        .frame(maxWidth: .infinity, minHeight: 140, alignment: .topLeading)
        .coachCard()
        .opacity(unlocked ? 1 : 0.55)
        .accessibilityElement(children: .combine)
        .accessibilityLabel(unlocked ? "\(badge.title), earned" : "\(badge.title), locked")
    }
}
