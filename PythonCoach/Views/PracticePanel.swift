import SwiftUI

/// One practice: write code, fix a bug, predict the output, or answer a quick question.
/// Used inside a lesson and in review mode.
struct PracticePanel: View {
    enum Mode {
        case lesson
        case review
    }

    let lesson: Lesson
    let practice: Practice
    let number: Int
    let total: Int
    var mode: Mode = .lesson
    var continueTitle: String?
    var onSolved: (Bool) -> Void
    var onContinue: (() -> Void)?
    var onBack: (() -> Void)?

    @EnvironmentObject private var store: ProgressStore
    @EnvironmentObject private var engine: PythonEngine
    @Environment(\.colorScheme) private var scheme
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    @State private var code = ""
    @State private var loaded = false
    @State private var hintsUnlocked = 0
    @State private var check: LessonCheck?
    @State private var isRunning = false
    @State private var solvedNow = false
    @State private var missedOnce = false
    @State private var pickedChoice: Int?
    @State private var showReset = false

    private var key: String { lesson.practiceKey(practice) }

    private var solved: Bool {
        solvedNow || (mode == .lesson && store.isPracticePassed(key))
    }

    private var pythonReady: Bool {
        engine.phase == .ready || engine.phase == .running
    }

    private var hasBlank: Bool {
        practice.starterCode.contains(LessonChecker.blank)
    }

    var body: some View {
        VStack(spacing: 0) {
            ScrollView {
                VStack(alignment: .leading, spacing: 14) {
                    header
                    Text(practice.prompt)
                        .font(AppTheme.rounded(.body))
                        .foregroundStyle(AppTheme.ink)
                        .fixedSize(horizontal: false, vertical: true)
                    if practice.isPredict {
                        HighlightedCode(code: practice.showCode)
                            .accessibilityLabel("Code: \(practice.showCode)")
                    }
                    if practice.isChoice {
                        choiceList
                        if let check {
                            FeedbackCard(check: check)
                        }
                        hintSection
                    } else {
                        if hasBlank && !solved {
                            Label("Replace each \(LessonChecker.blank) with your answer.", systemImage: "square.and.pencil")
                                .font(AppTheme.rounded(.subheadline, weight: .semibold))
                                .foregroundStyle(AppTheme.accent)
                        }
                        hintSection
                        CodeEditor(text: $code, palette: EditorPalette.forScheme(scheme))
                            .frame(height: 220)
                            .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
                            .overlay(
                                RoundedRectangle(cornerRadius: 16, style: .continuous)
                                    .stroke(AppTheme.line, lineWidth: 1)
                            )
                            .accessibilityLabel("Code editor")
                        HStack {
                            Spacer()
                            Button {
                                showReset = true
                            } label: {
                                Label("Start this one over", systemImage: "arrow.counterclockwise")
                                    .font(AppTheme.rounded(.footnote, weight: .semibold))
                            }
                            .foregroundStyle(AppTheme.muted)
                        }
                        if let check {
                            FeedbackCard(check: check)
                            ConsoleBlock(sections: check.sections, emptyText: "Your program didn't print anything.")
                        } else {
                            ConsoleBlock(sections: [], emptyText: "Press Run my code to see what Python prints.")
                        }
                    }
                }
                .padding(20)
                .frame(maxWidth: 760)
                .frame(maxWidth: .infinity)
            }
            .scrollDismissesKeyboard(.interactively)
            bottomBar
        }
        .onAppear(perform: load)
        .task(id: code) {
            guard loaded, mode == .lesson, !practice.isChoice else { return }
            let current = code
            let saveKey = key
            let starter = practice.starterCode
            try? await Task.sleep(nanoseconds: 400_000_000)
            store.saveCode(key: saveKey, code: current, starter: starter)
        }
        .onDisappear {
            if loaded, mode == .lesson, !practice.isChoice {
                store.saveCode(key: key, code: code, starter: practice.starterCode)
            }
        }
        .confirmationDialog("Go back to the starter code?", isPresented: $showReset, titleVisibility: .visible) {
            Button("Start over", role: .destructive) {
                code = practice.starterCode
                check = nil
                if mode == .lesson {
                    store.saveCode(key: key, code: practice.starterCode, starter: practice.starterCode)
                }
            }
            Button("Cancel", role: .cancel) {}
        }
    }

    // MARK: - Pieces

    private var kindLabel: String {
        if mode == .review { return "Review" }
        if lesson.isProject { return "Project step \(number) of \(total)" }
        switch practice.kind {
        case "predict": return "What will this print?"
        case "choice": return "Quick check"
        case "fix": return "Fix the bug"
        default: return hasBlank ? "Fill in the blank" : "Your turn"
        }
    }

    private var kindSymbol: String {
        switch practice.kind {
        case "predict": return "eye"
        case "choice": return "questionmark.circle"
        case "fix": return "ladybug"
        default: return lesson.isProject ? "hammer" : "keyboard"
        }
    }

    private var header: some View {
        HStack(spacing: 8) {
            Label(kindLabel, systemImage: kindSymbol)
                .font(AppTheme.rounded(.caption, weight: .bold))
                .foregroundStyle(practice.isFix ? AppTheme.danger : AppTheme.accent)
            Spacer()
            if mode == .review {
                Text(lesson.title)
                    .font(AppTheme.rounded(.caption))
                    .foregroundStyle(AppTheme.muted)
                    .lineLimit(1)
            } else if !lesson.isProject {
                Text("\(number) of \(total)")
                    .font(AppTheme.rounded(.caption, weight: .semibold))
                    .foregroundStyle(AppTheme.muted)
            }
            if solved {
                Image(systemName: "checkmark.circle.fill")
                    .foregroundStyle(AppTheme.success)
                    .accessibilityLabel("Solved")
            }
        }
    }

    private var choiceList: some View {
        VStack(alignment: .leading, spacing: 10) {
            ForEach(Array(practice.choices.enumerated()), id: \.offset) { index, choice in
                Button {
                    answer(index)
                } label: {
                    HStack(alignment: .top) {
                        Text(choice.isEmpty ? "(nothing)" : choice)
                            .font(practice.isPredict ? Font.system(size: 16, design: .monospaced) : AppTheme.rounded(.body, weight: .semibold))
                            .foregroundStyle(AppTheme.ink)
                            .multilineTextAlignment(.leading)
                            .fixedSize(horizontal: false, vertical: true)
                        Spacer()
                        Image(systemName: symbol(for: index))
                            .foregroundStyle(color(for: index))
                    }
                    .padding(14)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .coachCard()
                }
                .buttonStyle(PressScaleButtonStyle())
                .accessibilityLabel("Choice \(index + 1): \(choice.isEmpty ? "nothing" : choice.replacingOccurrences(of: "\n", with: ", then "))")
            }
        }
    }

    private func symbol(for index: Int) -> String {
        guard let pickedChoice, pickedChoice == index else { return "circle" }
        return index == practice.answer ? "checkmark.circle.fill" : "xmark.circle"
    }

    private func color(for index: Int) -> Color {
        guard let pickedChoice, pickedChoice == index else { return AppTheme.muted }
        return index == practice.answer ? AppTheme.success : AppTheme.flameStart
    }

    private var hintSection: some View {
        VStack(alignment: .leading, spacing: 8) {
            ForEach(Array(practice.hints.prefix(hintsUnlocked).enumerated()), id: \.offset) { index, hint in
                HStack(alignment: .top, spacing: 8) {
                    Image(systemName: "lightbulb.fill")
                        .foregroundStyle(AppTheme.flameStart)
                        .accessibilityHidden(true)
                    Text("Hint \(index + 1): \(hint)")
                        .font(AppTheme.rounded(.subheadline))
                        .foregroundStyle(AppTheme.ink)
                        .fixedSize(horizontal: false, vertical: true)
                        .textSelection(.enabled)
                }
            }
            if hintsUnlocked < practice.hints.count {
                Button {
                    revealHint()
                } label: {
                    Label(hintsUnlocked == 0 ? "Need a hint?" : "Another hint", systemImage: "lightbulb")
                        .font(AppTheme.rounded(.subheadline, weight: .semibold))
                }
                .buttonStyle(PressScaleButtonStyle())
                Text(hintFooter)
                    .font(AppTheme.rounded(.caption))
                    .foregroundStyle(AppTheme.muted)
            }
        }
        .padding(14)
        .frame(maxWidth: .infinity, alignment: .leading)
        .coachCard()
    }

    private var hintFooter: String {
        let left = practice.hints.count - hintsUnlocked
        let noun = left == 1 ? "hint" : "hints"
        if practice.isChoice {
            return "\(left) \(noun) left."
        }
        return "\(left) \(noun) left. If you're stuck, the last hint shows the answer."
    }

    private var bottomBar: some View {
        VStack(spacing: 8) {
            if !pythonReady && !practice.isChoice {
                Text(engine.phase == .failed ? engine.failureMessage : "Getting Python ready…")
                    .font(AppTheme.rounded(.caption, weight: .semibold))
                    .foregroundStyle(AppTheme.muted)
            }
            if solved, let onContinue {
                PrimaryButton(title: continueTitle ?? "Continue", systemImage: "arrow.right") {
                    onContinue()
                }
                if !practice.isChoice {
                    Button(isRunning ? "Running" : "Run my code again") { runCode() }
                        .font(AppTheme.rounded(.subheadline, weight: .semibold))
                        .foregroundStyle(AppTheme.accent)
                        .disabled(!pythonReady || isRunning)
                }
            } else if !practice.isChoice {
                PrimaryButton(
                    title: isRunning ? "Running" : "Run my code",
                    systemImage: isRunning ? nil : "play.fill",
                    enabled: pythonReady && !isRunning
                ) {
                    runCode()
                }
            }
            if let onBack {
                Button("Back") { onBack() }
                    .font(AppTheme.rounded(.footnote, weight: .semibold))
                    .foregroundStyle(AppTheme.muted)
            }
        }
        .padding(.horizontal, 20)
        .padding(.top, 8)
        .padding(.bottom, 12)
        .background(AppTheme.paper)
    }

    // MARK: - Actions

    private func load() {
        guard !loaded else { return }
        loaded = true
        if mode == .lesson {
            code = store.code(for: practice, in: lesson)
            hintsUnlocked = store.hintsUnlocked(forKey: key)
        } else {
            code = practice.starterCode
            hintsUnlocked = 0
        }
    }

    private func revealHint() {
        withAnimation(AppMotion.spring(reduceMotion)) {
            if mode == .lesson {
                hintsUnlocked = store.revealNextHint(key: key, total: practice.hints.count, starter: code)
            } else {
                hintsUnlocked = min(hintsUnlocked + 1, practice.hints.count)
            }
        }
    }

    private func answer(_ index: Int) {
        pickedChoice = index
        let result = LessonChecker.gradeChoice(practice: practice, choice: index)
        withAnimation(AppMotion.quick(reduceMotion)) {
            check = result
        }
        handle(result)
    }

    private func runCode() {
        guard !isRunning else { return }
        if let blank = LessonChecker.blankCheck(source: code) {
            withAnimation(AppMotion.quick(reduceMotion)) {
                check = blank
            }
            return
        }
        isRunning = true
        let source = code
        let tests = practice.tests
        let current = practice
        Task {
            var runs: [CapturedRun] = []
            for test in tests {
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
            let result = LessonChecker.evaluate(source: source, practice: current, runs: runs)
            withAnimation(AppMotion.quick(reduceMotion)) {
                check = result
            }
            isRunning = false
            handle(result)
        }
    }

    private func handle(_ result: LessonCheck) {
        if result.passed {
            guard !solvedNow else { return }
            solvedNow = true
            if mode == .lesson {
                store.recordPracticePass(key: key, code: code, starter: practice.starterCode)
            }
            onSolved(!missedOnce)
        } else if !missedOnce && !solvedNow {
            missedOnce = true
            store.recordMiss(key: key, starter: mode == .lesson ? code : practice.starterCode)
        }
    }
}
