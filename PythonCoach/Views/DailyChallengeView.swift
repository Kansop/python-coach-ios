import SwiftUI

struct DailyRoute: Hashable {
    var id = "today"
}

struct DailyChallengeView: View {
    @EnvironmentObject private var store: ProgressStore
    @EnvironmentObject private var engine: PythonEngine
    @Environment(\.colorScheme) private var scheme
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    @State private var code = ""
    @State private var loaded = false
    @State private var check: LessonCheck?
    @State private var isRunning = false
    @State private var celebrated = false
    @State private var awarded = false

    private var pick: DailyPick {
        DailyChallengeBank.pick(on: Date(), calendar: .current)
    }

    private var alreadyDone: Bool {
        store.dailyRecord().isDone(on: Date(), calendar: .current)
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 14) {
                Text(pick.prompt)
                    .font(AppTheme.rounded(.title3))
                    .foregroundStyle(AppTheme.ink)
                    .fixedSize(horizontal: false, vertical: true)
                Text(alreadyDone ? "You already finished today's challenge. You can still practice." : "Finish this once today for \(pick.xp) bonus XP.")
                    .font(AppTheme.rounded(.subheadline))
                    .foregroundStyle(AppTheme.muted)
                CodeEditor(text: $code, palette: EditorPalette.forScheme(scheme))
                    .frame(height: 220)
                    .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
                if let check {
                    FeedbackCard(check: check)
                    ConsoleBlock(sections: check.sections, emptyText: "Run the challenge to see the output.")
                }
                PrimaryButton(
                    title: isRunning ? "Running" : "Run challenge",
                    systemImage: isRunning ? nil : "play.fill",
                    enabled: (engine.phase == .ready || engine.phase == .running) && !isRunning
                ) {
                    run()
                }
                .accessibilityHint("Runs today's Python challenge")
            }
            .padding(20)
            .frame(maxWidth: 760)
            .frame(maxWidth: .infinity)
        }
        .background(AppTheme.paper)
        .navigationTitle("Daily challenge")
        .navigationBarTitleDisplayMode(.inline)
        .onAppear {
            guard !loaded else { return }
            loaded = true
            code = pick.starter
        }
        .overlay {
            if celebrated {
                CelebrationView(
                    result: CompletionResult(
                        xpGained: awarded ? pick.xp : 0,
                        totalXP: store.snapshot.xp,
                        leveledUp: false,
                        level: LevelLogic.level(for: store.snapshot.xp),
                        levelTitle: LevelLogic.title(for: store.snapshot.xp),
                        streak: store.snapshot.streak,
                        streakIncreased: awarded,
                        streakReset: false,
                        newBadges: [],
                        finishedUnitTitle: nil,
                        alreadyCompleted: !awarded
                    ),
                    nextTitle: nil,
                    onNext: { celebrated = false },
                    onStay: { celebrated = false }
                )
            }
        }
    }

    private func run() {
        guard !isRunning else { return }
        isRunning = true
        let lesson = pick.asLesson()
        let source = code
        Task {
            var runs: [CapturedRun] = []
            for test in lesson.tests {
                let result = await engine.run(
                    code: source,
                    stdin: test.stdin,
                    append: test.appendCode ?? "",
                    names: Array(test.values.keys),
                    interactive: false
                )
                runs.append(result)
                if result.failed { break }
            }
            let result = LessonChecker.evaluate(source: source, lesson: lesson, runs: runs)
            check = result
            isRunning = false
            if result.passed {
                awarded = store.markDailyDone(xp: pick.xp)
                withAnimation(AppMotion.spring(reduceMotion)) {
                    celebrated = true
                }
            }
        }
    }
}
