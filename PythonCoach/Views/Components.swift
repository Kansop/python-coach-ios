import SwiftUI
import WebKit

struct PrimaryButton: View {
    var title: String
    var systemImage: String?
    var enabled: Bool = true
    var action: () -> Void

    var body: some View {
        Button(action: action) {
            HStack(spacing: 8) {
                if let systemImage {
                    Image(systemName: systemImage)
                        .font(.headline)
                }
                Text(title)
            }
            .font(AppTheme.rounded(.headline, weight: .semibold))
            .foregroundStyle(AppTheme.onAccent)
            .frame(maxWidth: .infinity)
            .padding(.vertical, 14)
            .background(enabled ? AppTheme.accent : AppTheme.muted.opacity(0.35))
            .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
        }
        .buttonStyle(PressScaleButtonStyle())
        .disabled(!enabled)
    }
}

struct XPBar: View {
    var fraction: Double
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @State private var shown = 0.0

    var body: some View {
        GeometryReader { geo in
            ZStack(alignment: .leading) {
                Capsule().fill(AppTheme.line)
                Capsule()
                    .fill(AppTheme.accent)
                    .frame(width: max(0, geo.size.width * shown))
            }
        }
        .frame(height: 10)
        .accessibilityElement(children: .ignore)
        .accessibilityLabel("Level progress")
        .accessibilityValue("\(Int((fraction * 100).rounded())) percent")
        .onAppear { animate(to: fraction) }
        .onChange(of: fraction) { _, newValue in animate(to: newValue) }
    }

    private func animate(to value: Double) {
        if reduceMotion {
            shown = value
        } else {
            withAnimation(.spring(response: 0.75, dampingFraction: 0.86)) {
                shown = value
            }
        }
    }
}

struct HiddenPythonView: UIViewRepresentable {
    let webView: WKWebView?
    let generation: Int

    func makeUIView(context: Context) -> UIView {
        let view = UIView(frame: CGRect(x: 0, y: 0, width: 8, height: 8))
        view.backgroundColor = .clear
        view.isUserInteractionEnabled = false
        attach(to: view)
        return view
    }

    func updateUIView(_ view: UIView, context: Context) {
        _ = generation
        if view.subviews.first !== webView {
            view.subviews.forEach { $0.removeFromSuperview() }
            attach(to: view)
        }
    }

    private func attach(to view: UIView) {
        guard let webView else { return }
        webView.frame = view.bounds
        webView.autoresizingMask = [.flexibleWidth, .flexibleHeight]
        webView.isUserInteractionEnabled = false
        view.addSubview(webView)
    }
}

struct ConsoleBlock: View {
    var sections: [OutputSection]
    var emptyText: String

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Label("Output", systemImage: "terminal.fill")
                .font(AppTheme.rounded(.subheadline, weight: .semibold))
                .foregroundStyle(AppTheme.consoleMuted)
            if sections.isEmpty || sections.allSatisfy({ $0.stdout.isEmpty && $0.stderr.isEmpty }) {
                Text(emptyText)
                    .font(.system(size: 15, design: .monospaced))
                    .foregroundStyle(AppTheme.consoleMuted)
            } else {
                ForEach(sections) { section in
                    if sections.count > 1 {
                        Text(section.title)
                            .font(AppTheme.rounded(.caption, weight: .semibold))
                            .foregroundStyle(AppTheme.consoleMuted)
                    }
                    if !section.stdout.isEmpty {
                        Text(section.stdout)
                            .font(.system(size: 15, design: .monospaced))
                            .foregroundStyle(AppTheme.consoleText)
                            .textSelection(.enabled)
                            .frame(maxWidth: .infinity, alignment: .leading)
                    }
                    if !section.stderr.isEmpty {
                        Text(section.stderr)
                            .font(.system(size: 15, design: .monospaced))
                            .foregroundStyle(Color(red: 1, green: 0.72, blue: 0.72))
                            .frame(maxWidth: .infinity, alignment: .leading)
                    }
                }
            }
        }
        .padding(14)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(AppTheme.console)
        .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
    }
}

struct FeedbackCard: View {
    var check: LessonCheck

    private var tone: Color {
        check.passed ? AppTheme.success : AppTheme.flameStart
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Label(check.headline, systemImage: check.passed ? "checkmark.circle.fill" : (check.error == nil ? "arrow.triangle.2.circlepath" : "lightbulb.fill"))
                .font(AppTheme.rounded(.headline, weight: .semibold))
                .foregroundStyle(tone)
            if let error = check.error {
                ErrorHelpView(error: error)
            } else {
                Text(check.message)
                    .font(AppTheme.rounded(.body))
                    .foregroundStyle(AppTheme.ink)
                    .fixedSize(horizontal: false, vertical: true)
            }
            if let expected = check.expected {
                compareBlock(title: "Expected", text: expected.isEmpty ? "(nothing)" : expected)
            }
            if let actual = check.actual {
                compareBlock(title: "Your program", text: actual.isEmpty ? "(nothing)" : actual)
            }
        }
        .padding(14)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(tone.opacity(0.12))
        .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
        .accessibilityElement(children: .contain)
    }

    private func compareBlock(title: String, text: String) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(title)
                .font(AppTheme.rounded(.caption, weight: .semibold))
                .foregroundStyle(AppTheme.muted)
            Text(text)
                .font(.system(size: 14, design: .monospaced))
                .foregroundStyle(AppTheme.ink)
                .textSelection(.enabled)
                .frame(maxWidth: .infinity, alignment: .leading)
        }
    }
}

struct InputPromptSheet: View {
    var prompt: String
    var onSubmit: (String) -> Void
    @State private var answer = ""
    @FocusState private var focused: Bool

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Label("Python is asking", systemImage: "keyboard")
                .font(AppTheme.rounded(.headline, weight: .semibold))
                .foregroundStyle(AppTheme.ink)
            Text(prompt.isEmpty ? "This program is waiting for an answer." : prompt)
                .font(AppTheme.rounded(.title3, weight: .semibold))
                .foregroundStyle(AppTheme.ink)
            TextField("Your answer", text: $answer)
                .textFieldStyle(.roundedBorder)
                .font(.system(size: 18, design: .monospaced))
                .focused($focused)
                .submitLabel(.done)
                .onSubmit { onSubmit(answer) }
            PrimaryButton(title: "Give this to Python", systemImage: "arrow.right") {
                onSubmit(answer)
            }
        }
        .padding(24)
        .presentationDetents([.height(280)])
        .presentationDragIndicator(.visible)
        .onAppear { focused = true }
    }
}

/// The kid-friendly error explainer: what happened, where, and one thing to try.
struct ErrorHelpView: View {
    var error: ErrorExplanation
    var showTitle = false

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            if showTitle {
                Label(error.title, systemImage: "lightbulb.fill")
                    .font(AppTheme.rounded(.headline, weight: .semibold))
                    .foregroundStyle(AppTheme.flameStart)
            }
            Text(FriendlyErrors.encouragement)
                .font(AppTheme.rounded(.caption, weight: .semibold))
                .foregroundStyle(AppTheme.muted)
            if let line = error.line {
                VStack(alignment: .leading, spacing: 4) {
                    Text("Line \(line)")
                        .font(AppTheme.rounded(.caption, weight: .bold))
                        .foregroundStyle(AppTheme.flameStart)
                    if let text = error.lineText {
                        Text(text)
                            .font(.system(size: 15, design: .monospaced))
                            .foregroundStyle(AppTheme.ink)
                            .textSelection(.enabled)
                            .frame(maxWidth: .infinity, alignment: .leading)
                    }
                }
                .padding(10)
                .background(AppTheme.card)
                .clipShape(RoundedRectangle(cornerRadius: 10, style: .continuous))
                .accessibilityElement(children: .combine)
                .accessibilityLabel(error.lineText.map { "Line \(line): \($0)" } ?? "Line \(line)")
            }
            Text(error.message)
                .font(AppTheme.rounded(.body))
                .foregroundStyle(AppTheme.ink)
                .fixedSize(horizontal: false, vertical: true)
            if !error.tip.isEmpty {
                Label {
                    Text("Try this: \(error.tip)")
                        .font(AppTheme.rounded(.subheadline, weight: .semibold))
                        .foregroundStyle(AppTheme.ink)
                        .fixedSize(horizontal: false, vertical: true)
                } icon: {
                    Image(systemName: "wrench.and.screwdriver.fill")
                        .foregroundStyle(AppTheme.accent)
                }
            }
            if !error.detail.isEmpty {
                DisclosureGroup("What Python said") {
                    Text(error.detail)
                        .font(.system(size: 13, design: .monospaced))
                        .foregroundStyle(AppTheme.muted)
                        .textSelection(.enabled)
                        .frame(maxWidth: .infinity, alignment: .leading)
                }
                .font(AppTheme.rounded(.subheadline, weight: .semibold))
                .foregroundStyle(AppTheme.muted)
            }
        }
    }
}
