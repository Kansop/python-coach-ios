import SwiftUI

struct LessonFlowView: View {
    let lessonID: String
    @EnvironmentObject private var store: ProgressStore
    @EnvironmentObject private var engine: PythonEngine
    @Environment(\.dismiss) private var dismiss
    @Environment(\.colorScheme) private var scheme
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    @State private var currentID: String
    @State private var step = 0
    @State private var stepForward = true
    @State private var code = ""
    @State private var hintsUnlocked = 0
    @State private var didLoad = false
    @State private var exampleRun: CapturedRun?
    @State private var exerciseCheck: LessonCheck?
    @State private var isRunning = false
    @State private var showReset = false
    @State private var celebration: CompletionResult?

    init(lessonID: String) {
        self.lessonID = lessonID
        _currentID = State(initialValue: lessonID)
    }

    private var lesson: Lesson {
        Curriculum.lesson(id: currentID) ?? Curriculum.units[0].lessons[0]
    }

    private var pythonReady: Bool {
        engine.phase == .ready || engine.phase == .running
    }

    var body: some View {
        Group {
            if lesson.isQuiz {
                quizBody
            } else {
                codeBody
            }
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
        .onAppear(perform: loadIfNeeded)
        .onChange(of: currentID) { _, _ in
            step = 0
            loadLessonState()
        }
        .task(id: code) {
            guard didLoad, !lesson.isQuiz else { return }
            let id = lesson.id
            let starter = lesson.starterCode
            let current = code
            try? await Task.sleep(nanoseconds: 400_000_000)
            store.saveCode(lessonID: id, code: current, starter: starter)
        }
        .onDisappear {
            if didLoad, !lesson.isQuiz {
                store.saveCode(lessonID: lesson.id, code: code, starter: lesson.starterCode)
            }
            if engine.inputRequest != nil {
                engine.finishInput(nil)
            }
        }
    }

    private var quizBody: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text(lesson.explanation)
                    .font(AppTheme.rounded(.title3))
                    .foregroundStyle(AppTheme.ink)
                    .fixedSize(horizontal: false, vertical: true)
                Text(lesson.exercise)
                    .font(AppTheme.rounded(.headline, weight: .semibold))
                    .foregroundStyle(AppTheme.ink)
                    .fixedSize(horizontal: false, vertical: true)
                    .accessibilityAddTraits(.isHeader)
                ForEach(Array(lesson.quizChoices.enumerated()), id: \.offset) { index, choice in
                    Button {
                        answerQuiz(index)
                    } label: {
                        HStack {
                            Text(choice)
                                .font(AppTheme.rounded(.body, weight: .semibold))
                                .foregroundStyle(AppTheme.ink)
                                .multilineTextAlignment(.leading)
                            Spacer()
                            Image(systemName: "circle")
                                .foregroundStyle(AppTheme.muted)
                        }
                        .padding(14)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .coachCard()
                    }
                    .buttonStyle(PressScaleButtonStyle())
                    .accessibilityLabel("Choice \(index + 1): \(choice)")
                }
                if let exerciseCheck, !exerciseCheck.passed {
                    FeedbackCard(check: exerciseCheck)
                    hintSection
                }
            }
            .padding(20)
            .frame(maxWidth: 760)
            .frame(maxWidth: .infinity)
        }
    }

    private var codeBody: some View {
        VStack(spacing: 0) {
            stepHeader
            ZStack {
                if step == 0 {
                    learnStep.transition(stepTransition)
                } else if step == 1 {
                    exampleStep.transition(stepTransition)
                } else {
                    exerciseStep.transition(stepTransition)
                }
            }
            .animation(AppMotion.spring(reduceMotion), value: step)
            bottomBar
        }
        .toolbar {
            if step == 2 {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button {
                        showReset = true
                    } label: {
                        Image(systemName: "arrow.counterclockwise")
                    }
                    .accessibilityLabel("Reset code")
                }
            }
        }
        .confirmationDialog("Reset this code to the starter?", isPresented: $showReset, titleVisibility: .visible) {
            Button("Reset code", role: .destructive) {
                code = lesson.starterCode
                exerciseCheck = nil
                store.saveCode(lessonID: lesson.id, code: lesson.starterCode, starter: lesson.starterCode)
            }
            Button("Cancel", role: .cancel) {}
        }
    }

    private var stepTransition: AnyTransition {
        .asymmetric(
            insertion: .move(edge: stepForward ? .trailing : .leading).combined(with: .opacity),
            removal: .move(edge: stepForward ? .leading : .trailing).combined(with: .opacity)
        )
    }

    private var stepHeader: some View {
        HStack(spacing: 8) {
            ForEach(0..<3, id: \.self) { index in
                Capsule()
                    .fill(index <= step ? AppTheme.accent : AppTheme.line)
                    .frame(height: 6)
                    .animation(AppMotion.spring(reduceMotion), value: step)
            }
        }
        .padding(.horizontal, 20)
        .padding(.top, 8)
        .accessibilityElement(children: .ignore)
        .accessibilityLabel("Step \(step + 1) of 3")
    }

    private var learnStep: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text(lesson.explanation)
                    .font(AppTheme.rounded(.title3))
                    .foregroundStyle(AppTheme.ink)
                    .fixedSize(horizontal: false, vertical: true)
                Label("Next you'll run an example, then type your own.", systemImage: "book.fill")
                    .font(AppTheme.rounded(.subheadline))
                    .foregroundStyle(AppTheme.muted)
            }
            .padding(20)
            .frame(maxWidth: .infinity, alignment: .leading)
        }
    }

    private var exampleStep: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 14) {
                Text(lesson.exampleNote)
                    .font(AppTheme.rounded(.body))
                    .foregroundStyle(AppTheme.ink)
                    .fixedSize(horizontal: false, vertical: true)
                HighlightedCode(code: lesson.exampleCode)
                if let exampleRun {
                    ConsoleBlock(
                        sections: [OutputSection(index: 0, title: "Output", stdout: exampleRun.stdout, stderr: exampleRun.stderr)],
                        emptyText: exampleRun.cancelled ? "You closed the question." : "Run the example to see the output."
                    )
                    if exampleRun.timedOut || exampleRun.errorType != nil {
                        let error = FriendlyErrors.explain(
                            type: exampleRun.errorType,
                            message: exampleRun.errorMessage,
                            traceback: exampleRun.traceback,
                            timedOut: exampleRun.timedOut
                        )
                        Text(error.message)
                            .font(AppTheme.rounded(.subheadline))
                            .foregroundStyle(AppTheme.danger)
                    }
                } else {
                    ConsoleBlock(sections: [], emptyText: "Run the example to see the output.")
                }
            }
            .padding(20)
        }
        .scrollDismissesKeyboard(.interactively)
    }

    private var exerciseStep: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 14) {
                Text(lesson.isFix ? "Fix the bug" : "Your turn")
                    .font(AppTheme.rounded(.caption, weight: .bold))
                    .foregroundStyle(lesson.isFix ? AppTheme.danger : AppTheme.accent)
                if lesson.isFix {
                    Label("The starter has a bug. Change it until the checks pass.", systemImage: "ladybug")
                        .font(AppTheme.rounded(.subheadline))
                        .foregroundStyle(AppTheme.ink)
                }
                Text(lesson.exercise)
                    .font(AppTheme.rounded(.body))
                    .foregroundStyle(AppTheme.ink)
                    .fixedSize(horizontal: false, vertical: true)
                hintSection
                CodeEditor(text: $code, palette: EditorPalette.forScheme(scheme))
                    .frame(height: 240)
                    .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
                    .overlay(
                        RoundedRectangle(cornerRadius: 16, style: .continuous)
                            .stroke(AppTheme.line, lineWidth: 1)
                    )
                if let exerciseCheck {
                    FeedbackCard(check: exerciseCheck)
                    ConsoleBlock(
                        sections: exerciseCheck.sections,
                        emptyText: "Run your code to see what Python says."
                    )
                } else {
                    ConsoleBlock(sections: [], emptyText: "Run your code to see what Python says.")
                }
            }
            .padding(20)
        }
        .scrollDismissesKeyboard(.interactively)
    }

    private var hintSection: some View {
        VStack(alignment: .leading, spacing: 8) {
            ForEach(Array(lesson.hints.prefix(hintsUnlocked).enumerated()), id: \.offset) { index, hint in
                HStack(alignment: .top, spacing: 8) {
                    Image(systemName: "lightbulb.fill")
                        .foregroundStyle(AppTheme.flameStart)
                    Text("Hint \(index + 1): \(hint)")
                        .font(AppTheme.rounded(.subheadline))
                        .foregroundStyle(AppTheme.ink)
                        .fixedSize(horizontal: false, vertical: true)
                }
            }
            if hintsUnlocked < lesson.hints.count {
                Button {
                    withAnimation(AppMotion.spring(reduceMotion)) {
                        hintsUnlocked = store.revealNextHint(for: lesson)
                    }
                } label: {
                    Label(hintsUnlocked == 0 ? "Need a hint?" : "Another hint", systemImage: "lightbulb")
                        .font(AppTheme.rounded(.subheadline, weight: .semibold))
                }
                .buttonStyle(PressScaleButtonStyle())
                Text("\(lesson.hints.count - hintsUnlocked) left. Hints never show the full answer.")
                    .font(AppTheme.rounded(.caption))
                    .foregroundStyle(AppTheme.muted)
            }
        }
        .padding(14)
        .frame(maxWidth: .infinity, alignment: .leading)
        .coachCard()
    }

    private var bottomBar: some View {
        VStack(spacing: 8) {
            if !pythonReady {
                Text(engine.phase == .failed ? engine.failureMessage : "Getting Python ready…")
                    .font(AppTheme.rounded(.caption, weight: .semibold))
                    .foregroundStyle(AppTheme.muted)
            }
            if step == 0 {
                PrimaryButton(title: "Try the example", systemImage: "arrow.right") {
                    changeStep(1)
                }
            } else if step == 1 {
                PrimaryButton(
                    title: isRunning ? "Running" : "Run example",
                    systemImage: isRunning ? nil : "play.fill",
                    enabled: pythonReady && !isRunning
                ) {
                    runExample()
                }
                Button("I'm ready to try") { changeStep(2) }
                    .font(AppTheme.rounded(.subheadline, weight: .semibold))
                    .foregroundStyle(AppTheme.accent)
                    .buttonStyle(PressScaleButtonStyle())
            } else {
                PrimaryButton(
                    title: isRunning ? "Running" : "Run my code",
                    systemImage: isRunning ? nil : "play.fill",
                    enabled: pythonReady && !isRunning
                ) {
                    runExercise()
                }
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
        stepForward = newStep > step
        withAnimation(AppMotion.spring(reduceMotion)) {
            step = newStep
        }
    }

    private func loadIfNeeded() {
        guard !didLoad else { return }
        didLoad = true
        loadLessonState()
    }

    private func loadLessonState() {
        code = store.code(for: lesson)
        hintsUnlocked = store.hintsUnlocked(for: lesson.id)
        exampleRun = nil
        exerciseCheck = nil
        celebration = nil
    }

    private func answerQuiz(_ choice: Int) {
        let check = LessonChecker.gradeQuiz(lesson: lesson, choice: choice)
        exerciseCheck = check
        if check.passed {
            let reward = store.recordPass(lesson: lesson)
            withAnimation(AppMotion.spring(reduceMotion)) {
                celebration = reward
            }
        }
    }

    private func runExample() {
        guard !isRunning else { return }
        isRunning = true
        Task {
            let result = await engine.run(
                code: lesson.exampleCode,
                stdin: [],
                append: "",
                names: [],
                interactive: true
            )
            exampleRun = result
            isRunning = false
        }
    }

    private func runExercise() {
        guard !isRunning else { return }
        isRunning = true
        let lesson = lesson
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
            let check = LessonChecker.evaluate(source: source, lesson: lesson, runs: runs)
            exerciseCheck = check
            isRunning = false
            if check.passed {
                let reward = store.recordPass(lesson: lesson)
                withAnimation(AppMotion.spring(reduceMotion)) {
                    celebration = reward
                }
            }
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
