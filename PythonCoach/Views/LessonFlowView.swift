import SwiftUI

/// A lesson: learn the idea, walk through an example, then practice in small steps.
struct LessonFlowView: View {
    let lessonID: String
    @EnvironmentObject private var store: ProgressStore
    @EnvironmentObject private var engine: PythonEngine
    @Environment(\.dismiss) private var dismiss
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    @State private var currentID: String
    @State private var step = 0
    @State private var stepForward = true
    @State private var exampleRun: CapturedRun?
    @State private var isRunning = false
    @State private var celebration: CompletionResult?

    init(lessonID: String) {
        self.lessonID = lessonID
        _currentID = State(initialValue: lessonID)
    }

    private var lesson: Lesson {
        Curriculum.lesson(id: currentID) ?? Curriculum.units[0].lessons[0]
    }

    private var introSteps: Int {
        lesson.hasExample ? 2 : 1
    }

    private var stepCount: Int {
        introSteps + lesson.practices.count
    }

    private var pythonReady: Bool {
        engine.phase == .ready || engine.phase == .running
    }

    var body: some View {
        VStack(spacing: 0) {
            stepHeader
            ZStack {
                currentStep
                    .id("\(lesson.id)-\(step)")
                    .transition(stepTransition)
            }
            .animation(AppMotion.spring(reduceMotion), value: step)
        }
        .background(AppTheme.paper)
        .navigationTitle(lesson.title)
        .navigationBarTitleDisplayMode(.inline)
        .toolbar(.hidden, for: .tabBar)
        .overlay {
            if let celebration {
                CelebrationView(
                    result: celebration,
                    nextTitle: nextTitle,
                    onNext: goNext,
                    onStay: { withAnimation(AppMotion.spring(reduceMotion)) { self.celebration = nil } }
                )
                .transition(.opacity.combined(with: .scale(scale: 0.96)))
            }
        }
        .animation(AppMotion.spring(reduceMotion), value: celebration != nil)
        .onChange(of: currentID) { _, _ in
            step = 0
            exampleRun = nil
            celebration = nil
        }
        .onDisappear {
            if engine.inputRequest != nil {
                engine.finishInput(nil)
            }
        }
    }

    @ViewBuilder
    private var currentStep: some View {
        if step == 0 {
            learnStep
        } else if step == 1 && lesson.hasExample {
            exampleStep
        } else {
            let index = min(max(step - introSteps, 0), max(lesson.practices.count - 1, 0))
            if lesson.practices.indices.contains(index) {
                practiceStep(index)
            } else {
                learnStep
            }
        }
    }

    private var stepTransition: AnyTransition {
        .asymmetric(
            insertion: .move(edge: stepForward ? .trailing : .leading).combined(with: .opacity),
            removal: .move(edge: stepForward ? .leading : .trailing).combined(with: .opacity)
        )
    }

    private var stepHeader: some View {
        HStack(spacing: 6) {
            ForEach(0..<stepCount, id: \.self) { index in
                Capsule()
                    .fill(index <= step ? AppTheme.accent : AppTheme.line)
                    .frame(height: 6)
            }
        }
        .padding(.horizontal, 20)
        .padding(.top, 8)
        .padding(.bottom, 4)
        .accessibilityElement(children: .ignore)
        .accessibilityLabel("Step \(step + 1) of \(stepCount)")
    }

    // MARK: - Learn

    private var learnStep: some View {
        VStack(spacing: 0) {
            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    if lesson.isProject {
                        Label("Project: \(lesson.practices.count) small steps", systemImage: "hammer.fill")
                            .font(AppTheme.rounded(.subheadline, weight: .bold))
                            .foregroundStyle(AppTheme.accent)
                    } else if lesson.isCheckpoint {
                        Label("Checkpoint: predict what Python prints", systemImage: "eye.fill")
                            .font(AppTheme.rounded(.subheadline, weight: .bold))
                            .foregroundStyle(AppTheme.accent)
                    }
                    if !lesson.terms.isEmpty {
                        Text("New words")
                            .font(AppTheme.rounded(.headline, weight: .bold))
                            .foregroundStyle(AppTheme.ink)
                            .accessibilityAddTraits(.isHeader)
                        ForEach(lesson.terms, id: \.word) { term in
                            termCard(term)
                        }
                    }
                    Text(lesson.explanation)
                        .font(AppTheme.rounded(.title3))
                        .foregroundStyle(AppTheme.ink)
                        .fixedSize(horizontal: false, vertical: true)
                    if !lesson.why.isEmpty {
                        VStack(alignment: .leading, spacing: 6) {
                            Label("Why it works", systemImage: "gearshape.2.fill")
                                .font(AppTheme.rounded(.subheadline, weight: .bold))
                                .foregroundStyle(AppTheme.accent)
                            Text(lesson.why)
                                .font(AppTheme.rounded(.body))
                                .foregroundStyle(AppTheme.ink)
                                .fixedSize(horizontal: false, vertical: true)
                        }
                        .padding(14)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .coachCard()
                    }
                }
                .padding(20)
                .frame(maxWidth: 760)
                .frame(maxWidth: .infinity)
            }
            bar {
                PrimaryButton(title: lesson.hasExample ? "See an example" : "Start step 1", systemImage: "arrow.right") {
                    changeStep(1)
                }
            }
        }
    }

    private func termCard(_ term: Term) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(term.word)
                .font(AppTheme.rounded(.headline, weight: .bold))
                .foregroundStyle(AppTheme.accent)
            Text(term.meaning)
                .font(AppTheme.rounded(.body))
                .foregroundStyle(AppTheme.ink)
                .fixedSize(horizontal: false, vertical: true)
            if !term.like.isEmpty {
                Text("Think of it like this: \(term.like)")
                    .font(AppTheme.rounded(.subheadline))
                    .foregroundStyle(AppTheme.muted)
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
        .padding(14)
        .frame(maxWidth: .infinity, alignment: .leading)
        .coachCard()
        .accessibilityElement(children: .combine)
    }

    // MARK: - Example

    private var exampleStep: some View {
        VStack(spacing: 0) {
            ScrollView {
                VStack(alignment: .leading, spacing: 14) {
                    if !lesson.exampleNote.isEmpty {
                        Text(lesson.exampleNote)
                            .font(AppTheme.rounded(.body))
                            .foregroundStyle(AppTheme.ink)
                            .fixedSize(horizontal: false, vertical: true)
                    }
                    HighlightedCode(code: lesson.exampleCode)
                    exampleOutput
                    if !lesson.walkthrough.isEmpty {
                        Text("Line by line")
                            .font(AppTheme.rounded(.headline, weight: .bold))
                            .foregroundStyle(AppTheme.ink)
                            .accessibilityAddTraits(.isHeader)
                        ForEach(Array(lesson.walkthrough.enumerated()), id: \.offset) { index, walk in
                            walkRow(index: index, walk: walk)
                        }
                    }
                    if !lesson.mistakes.isEmpty {
                        Text("Watch out for")
                            .font(AppTheme.rounded(.headline, weight: .bold))
                            .foregroundStyle(AppTheme.ink)
                            .accessibilityAddTraits(.isHeader)
                        ForEach(Array(lesson.mistakes.enumerated()), id: \.offset) { _, mistake in
                            mistakeCard(mistake)
                        }
                    }
                }
                .padding(20)
                .frame(maxWidth: 760)
                .frame(maxWidth: .infinity)
            }
            bar {
                PrimaryButton(
                    title: isRunning ? "Running" : "Run the example",
                    systemImage: isRunning ? nil : "play.fill",
                    enabled: pythonReady && !isRunning
                ) {
                    runExample()
                }
                Button("I'm ready to practice") { changeStep(2) }
                    .font(AppTheme.rounded(.subheadline, weight: .semibold))
                    .foregroundStyle(AppTheme.accent)
                    .buttonStyle(PressScaleButtonStyle())
            }
        }
    }

    @ViewBuilder
    private var exampleOutput: some View {
        if let exampleRun {
            ConsoleBlock(
                sections: [OutputSection(index: 0, title: "Output", stdout: exampleRun.stdout, stderr: exampleRun.stderr)],
                emptyText: exampleRun.cancelled ? "You closed the question." : "This example doesn't print anything."
            )
            if exampleRun.timedOut || exampleRun.errorType != nil {
                ErrorHelpView(
                    error: FriendlyErrors.explain(
                        type: exampleRun.errorType,
                        message: exampleRun.errorMessage,
                        traceback: exampleRun.traceback,
                        timedOut: exampleRun.timedOut,
                        source: lesson.exampleCode
                    ),
                    showTitle: true
                )
            }
        } else {
            ConsoleBlock(sections: [], emptyText: "Press Run the example to see what it prints.")
        }
    }

    private func walkRow(index: Int, walk: WalkStep) -> some View {
        HStack(alignment: .top, spacing: 10) {
            Text("\(index + 1)")
                .font(AppTheme.rounded(.caption, weight: .bold))
                .foregroundStyle(AppTheme.onAccent)
                .frame(width: 24, height: 24)
                .background(AppTheme.accent)
                .clipShape(Circle())
                .accessibilityHidden(true)
            VStack(alignment: .leading, spacing: 4) {
                Text(walk.code)
                    .font(.system(size: 15, design: .monospaced))
                    .foregroundStyle(AppTheme.ink)
                    .fixedSize(horizontal: false, vertical: true)
                Text(walk.note)
                    .font(AppTheme.rounded(.subheadline))
                    .foregroundStyle(AppTheme.muted)
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
        .padding(12)
        .frame(maxWidth: .infinity, alignment: .leading)
        .coachCard()
        .accessibilityElement(children: .combine)
    }

    private func mistakeCard(_ mistake: Mistake) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            Label("Oops", systemImage: "xmark.circle")
                .font(AppTheme.rounded(.caption, weight: .bold))
                .foregroundStyle(AppTheme.flameStart)
            Text(mistake.wrong)
                .font(.system(size: 15, design: .monospaced))
                .foregroundStyle(AppTheme.ink)
                .fixedSize(horizontal: false, vertical: true)
            Text(mistake.why)
                .font(AppTheme.rounded(.subheadline))
                .foregroundStyle(AppTheme.ink)
                .fixedSize(horizontal: false, vertical: true)
            Label("Better", systemImage: "checkmark.circle")
                .font(AppTheme.rounded(.caption, weight: .bold))
                .foregroundStyle(AppTheme.success)
            Text(mistake.fix)
                .font(.system(size: 15, design: .monospaced))
                .foregroundStyle(AppTheme.ink)
                .fixedSize(horizontal: false, vertical: true)
        }
        .padding(14)
        .frame(maxWidth: .infinity, alignment: .leading)
        .coachCard()
        .accessibilityElement(children: .combine)
    }

    // MARK: - Practice

    private func practiceStep(_ index: Int) -> some View {
        let practice = lesson.practices[index]
        let isLast = index == lesson.practices.count - 1
        return PracticePanel(
            lesson: lesson,
            practice: practice,
            number: index + 1,
            total: lesson.practices.count,
            mode: .lesson,
            continueTitle: isLast ? (nextTitle ?? "Finish") : (lesson.isProject ? "Next step" : "Next practice"),
            onSolved: { _ in practiceSolved() },
            onContinue: {
                if isLast {
                    finishOrNext()
                } else {
                    changeStep(step + 1)
                }
            },
            onBack: { changeStep(step - 1) }
        )
        .id(lesson.practiceKey(practice))
    }

    private func bar<Content: View>(@ViewBuilder _ content: () -> Content) -> some View {
        VStack(spacing: 8) {
            if !pythonReady {
                Text(engine.phase == .failed ? engine.failureMessage : "Getting Python ready…")
                    .font(AppTheme.rounded(.caption, weight: .semibold))
                    .foregroundStyle(AppTheme.muted)
            }
            content()
            if step > 0 {
                Button("Back") { changeStep(step - 1) }
                    .font(AppTheme.rounded(.footnote, weight: .semibold))
                    .foregroundStyle(AppTheme.muted)
            }
        }
        .padding(.horizontal, 20)
        .padding(.top, 8)
        .padding(.bottom, 12)
        .background(AppTheme.paper)
    }

    private var nextTitle: String? {
        if let next = Curriculum.nextLesson(after: lesson.id), store.isUnlocked(next.id) {
            return "Next: \(next.title)"
        }
        return nil
    }

    private func changeStep(_ newStep: Int) {
        let clamped = min(max(newStep, 0), stepCount - 1)
        stepForward = clamped > step
        withAnimation(AppMotion.spring(reduceMotion)) {
            step = clamped
        }
    }

    private func practiceSolved() {
        let passed = store.snapshot.passedPractices(in: lesson)
        guard passed >= lesson.practices.count else { return }
        let reward = store.recordPass(lesson: lesson)
        withAnimation(AppMotion.spring(reduceMotion)) {
            celebration = reward
        }
    }

    private func finishOrNext() {
        if store.isLessonCompleted(lesson.id) {
            goNext()
        } else {
            practiceSolved()
            if !store.isLessonCompleted(lesson.id) {
                dismiss()
            }
        }
    }

    private func runExample() {
        guard !isRunning else { return }
        isRunning = true
        let source = lesson.exampleCode
        Task {
            let result = await engine.run(code: source, stdin: [], append: "", names: [], interactive: true)
            exampleRun = result
            isRunning = false
        }
    }

    private func goNext() {
        if let next = Curriculum.nextLesson(after: lesson.id), store.isUnlocked(next.id) {
            stepForward = true
            withAnimation(AppMotion.spring(reduceMotion)) {
                celebration = nil
                currentID = next.id
            }
        } else {
            dismiss()
        }
    }
}
