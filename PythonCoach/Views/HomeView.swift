import SwiftUI

struct HomeView: View {
    @EnvironmentObject private var store: ProgressStore
    @EnvironmentObject private var engine: PythonEngine
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @State private var appeared = false

    private var calendar: Calendar { .current }
    private var streakState: StreakState {
        StreakState(current: store.snapshot.streak, longest: store.snapshot.longestStreak, lastActiveDay: store.snapshot.lastActiveDay)
    }
    private var shownStreak: Int {
        StreakLogic.displayStreak(state: streakState, now: Date(), calendar: calendar)
    }

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    dailyCard
                    header
                    if engine.phase == .failed {
                        engineBanner
                    }
                    HStack(spacing: 12) {
                        streakCard
                        xpCard
                    }
                    if let nextID = store.nextLessonID(), let lesson = Curriculum.lesson(id: nextID) {
                        continueCard(lesson)
                    } else if store.snapshot.completedCount >= Curriculum.orderedIDs.count {
                        finishedCard
                    }
                    reviewCard
                    Text("Lesson map")
                        .font(AppTheme.rounded(.title3, weight: .bold))
                        .foregroundStyle(AppTheme.ink)
                        .accessibilityAddTraits(.isHeader)
                    LessonMapView()
                    Text("Units")
                        .font(AppTheme.rounded(.title3, weight: .bold))
                        .foregroundStyle(AppTheme.ink)
                        .accessibilityAddTraits(.isHeader)
                    ForEach(Array(Curriculum.units.enumerated()), id: \.element.id) { index, unit in
                        NavigationLink(value: unit) {
                            unitRow(unit)
                        }
                        .buttonStyle(PressScaleButtonStyle())
                        .opacity(appeared ? 1 : 0)
                        .offset(y: appeared || reduceMotion ? 0 : 14)
                        .animation(AppMotion.spring(reduceMotion).delay(Double(index) * 0.04), value: appeared)
                    }
                }
                .padding(20)
                .frame(maxWidth: 980)
                .frame(maxWidth: .infinity)
            }
            .background(AppTheme.paper)
            .navigationTitle("Python Coach")
            .navigationDestination(for: Unit.self) { unit in
                UnitDetailView(unit: unit)
            }
            .navigationDestination(for: String.self) { id in
                LessonFlowView(lessonID: id)
            }
            .navigationDestination(for: DailyRoute.self) { _ in
                DailyChallengeView()
            }
            .navigationDestination(for: ReviewRoute.self) { _ in
                ReviewView()
            }
            .onAppear { appeared = true }
        }
    }

    private var dailyCard: some View {
        let done = store.dailyRecord().isDone(on: Date(), calendar: calendar)
        let pick = DailyChallengeBank.pick(on: Date(), calendar: calendar)
        return NavigationLink(value: DailyRoute()) {
            HStack(spacing: 12) {
                Image(systemName: done ? "checkmark.circle.fill" : "sun.max.fill")
                    .font(.title2)
                    .foregroundStyle(done ? AppTheme.success : AppTheme.flameStart)
                    .accessibilityHidden(true)
                VStack(alignment: .leading, spacing: 2) {
                    Text(done ? "Daily challenge done" : "Daily challenge")
                        .font(AppTheme.rounded(.caption, weight: .semibold))
                        .foregroundStyle(AppTheme.muted)
                    Text(pick.title)
                        .font(AppTheme.rounded(.headline, weight: .bold))
                        .foregroundStyle(AppTheme.ink)
                }
                Spacer()
                Image(systemName: "chevron.right")
                    .foregroundStyle(AppTheme.muted)
            }
            .padding(16)
            .coachCard()
        }
        .buttonStyle(PressScaleButtonStyle())
        .accessibilityLabel(done ? "Daily challenge done, \(pick.title)" : "Daily challenge, \(pick.title)")
    }

    private var header: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text("Learn by typing real code")
                .font(AppTheme.rounded(.subheadline, weight: .semibold))
                .foregroundStyle(AppTheme.accent)
            Text(StreakLogic.message(state: streakState, now: Date(), calendar: calendar))
                .font(AppTheme.rounded(.body))
                .foregroundStyle(AppTheme.muted)
        }
    }

    private var engineBanner: some View {
        VStack(alignment: .leading, spacing: 10) {
            Label(engine.failureMessage, systemImage: "exclamationmark.triangle.fill")
                .font(AppTheme.rounded(.headline, weight: .semibold))
                .foregroundStyle(AppTheme.danger)
            if !engine.failureDetail.isEmpty {
                Text(engine.failureDetail)
                    .font(AppTheme.rounded(.footnote))
                    .foregroundStyle(AppTheme.muted)
                    .lineLimit(4)
            }
            Button("Start Python again") { engine.restart() }
                .font(AppTheme.rounded(.subheadline, weight: .semibold))
        }
        .padding(16)
        .frame(maxWidth: .infinity, alignment: .leading)
        .coachCard()
    }

    private var streakCard: some View {
        VStack(alignment: .leading, spacing: 8) {
            streakIcon
                .accessibilityLabel(shownStreak == 1 ? "1 day streak" : "\(shownStreak) day streak")
            Text("\(shownStreak)")
                .font(AppTheme.rounded(.largeTitle, weight: .bold))
                .foregroundStyle(AppTheme.ink)
                .contentTransition(.numericText())
                .animation(AppMotion.spring(reduceMotion), value: shownStreak)
            Text(shownStreak == 1 ? "day" : "days")
                .font(AppTheme.rounded(.caption, weight: .semibold))
                .foregroundStyle(AppTheme.muted)
        }
        .padding(16)
        .frame(maxWidth: .infinity, alignment: .leading)
        .coachCard()
    }

    @ViewBuilder
    private var streakIcon: some View {
        if shownStreak > 0 {
            Image(systemName: "flame.fill")
                .font(.system(size: 28))
                .foregroundStyle(AppTheme.flameGradient)
                .symbolEffect(.pulse, options: .repeating, isActive: !reduceMotion)
                .symbolEffect(.bounce, value: shownStreak)
        } else {
            Image(systemName: "flame")
                .font(.system(size: 28))
                .foregroundStyle(AppTheme.muted)
        }
    }

    private var xpCard: some View {
        VStack(alignment: .leading, spacing: 8) {
            Image(systemName: "star.fill")
                .font(.system(size: 24))
                .foregroundStyle(AppTheme.accent)
            Text("Level \(LevelLogic.level(for: store.snapshot.xp))")
                .font(AppTheme.rounded(.headline, weight: .bold))
                .foregroundStyle(AppTheme.ink)
            Text(LevelLogic.title(for: store.snapshot.xp))
                .font(AppTheme.rounded(.caption, weight: .semibold))
                .foregroundStyle(AppTheme.muted)
                .lineLimit(1)
            XPBar(fraction: LevelLogic.fraction(for: store.snapshot.xp))
            Text("\(store.snapshot.xp) XP")
                .font(AppTheme.rounded(.caption, weight: .semibold))
                .foregroundStyle(AppTheme.muted)
                .contentTransition(.numericText())
        }
        .padding(16)
        .frame(maxWidth: .infinity, alignment: .leading)
        .coachCard()
    }

    private func continueCard(_ lesson: Lesson) -> some View {
        NavigationLink(value: lesson.id) {
            HStack(spacing: 12) {
                Image(systemName: "play.fill")
                    .font(.headline)
                    .foregroundStyle(AppTheme.onAccent)
                    .frame(width: 44, height: 44)
                    .background(AppTheme.accent)
                    .clipShape(RoundedRectangle(cornerRadius: 12, style: .continuous))
                VStack(alignment: .leading, spacing: 2) {
                    Text("Continue")
                        .font(AppTheme.rounded(.caption, weight: .semibold))
                        .foregroundStyle(AppTheme.muted)
                    Text(lesson.title)
                        .font(AppTheme.rounded(.headline, weight: .bold))
                        .foregroundStyle(AppTheme.ink)
                }
                Spacer()
                Image(systemName: "chevron.right")
                    .foregroundStyle(AppTheme.muted)
            }
            .padding(16)
            .coachCard()
        }
        .buttonStyle(PressScaleButtonStyle())
    }

    private var reviewCard: some View {
        let candidates = ReviewPlanner.candidates(snapshot: store.snapshot, units: Curriculum.units)
        let tricky = candidates.filter { $0.misses > 0 }.count
        let detail: String
        if candidates.isEmpty {
            detail = "Finish a lesson to unlock review."
        } else if tricky > 0 {
            detail = tricky == 1 ? "1 tricky one to practice again" : "\(tricky) tricky ones to practice again"
        } else {
            detail = "Practice what you've learned so it sticks"
        }
        return NavigationLink(value: ReviewRoute()) {
            HStack(spacing: 12) {
                Image(systemName: "arrow.triangle.2.circlepath")
                    .font(.title2)
                    .foregroundStyle(AppTheme.accent)
                    .accessibilityHidden(true)
                VStack(alignment: .leading, spacing: 2) {
                    Text("Review")
                        .font(AppTheme.rounded(.headline, weight: .bold))
                        .foregroundStyle(AppTheme.ink)
                    Text(detail)
                        .font(AppTheme.rounded(.caption, weight: .semibold))
                        .foregroundStyle(AppTheme.muted)
                }
                Spacer()
                Image(systemName: "chevron.right")
                    .foregroundStyle(AppTheme.muted)
            }
            .padding(16)
            .coachCard()
        }
        .buttonStyle(PressScaleButtonStyle())
        .accessibilityLabel("Review. \(detail)")
    }

    private var finishedCard: some View {
        HStack(spacing: 12) {
            Image(systemName: "trophy.fill")
                .font(.title2)
                .foregroundStyle(AppTheme.flameStart)
            Text("You finished the path. Replay any lesson to keep the streak going.")
                .font(AppTheme.rounded(.subheadline))
                .foregroundStyle(AppTheme.ink)
        }
        .padding(16)
        .coachCard()
    }

    private func unitRow(_ unit: Unit) -> some View {
        let done = store.completedCount(in: unit)
        let total = unit.lessons.count
        let fraction = total == 0 ? 0 : Double(done) / Double(total)
        return HStack(spacing: 14) {
            Image(systemName: unit.symbol)
                .font(.title3)
                .foregroundStyle(AppTheme.accent)
                .frame(width: 44, height: 44)
                .background(AppTheme.accent.opacity(0.12))
                .clipShape(RoundedRectangle(cornerRadius: 12, style: .continuous))
            VStack(alignment: .leading, spacing: 6) {
                HStack(spacing: 6) {
                    Text(unit.title)
                        .font(AppTheme.rounded(.headline, weight: .bold))
                        .foregroundStyle(AppTheme.ink)
                    if unit.optional {
                        Text("Bonus")
                            .font(AppTheme.rounded(.caption2, weight: .bold))
                            .foregroundStyle(AppTheme.accent)
                            .padding(.horizontal, 6)
                            .padding(.vertical, 2)
                            .background(AppTheme.accent.opacity(0.12))
                            .clipShape(Capsule())
                    }
                }
                Text(unit.summary)
                    .font(AppTheme.rounded(.caption))
                    .foregroundStyle(AppTheme.muted)
                XPBar(fraction: fraction)
            }
            Text("\(done)/\(total)")
                .font(AppTheme.rounded(.subheadline, weight: .bold))
                .foregroundStyle(AppTheme.muted)
                .monospacedDigit()
            Image(systemName: "chevron.right")
                .font(.footnote.weight(.semibold))
                .foregroundStyle(AppTheme.muted)
        }
        .padding(14)
        .coachCard()
    }
}
