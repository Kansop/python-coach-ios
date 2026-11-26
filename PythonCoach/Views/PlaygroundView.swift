import SwiftUI

struct PlaygroundView: View {
    @EnvironmentObject private var engine: PythonEngine
    @Environment(\.colorScheme) private var scheme
    @StateObject private var library = PlaygroundLibrary.live()
    @State private var code = "# Free play. Nothing here is graded.\nprint(\"Hello from the playground\")\n"
    @State private var title = ""
    @State private var output = ""
    @State private var errorText = ""
    @State private var lastError: ErrorExplanation?
    @State private var isRunning = false

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 14) {
                    Text("Write anything. It stays on this iPhone.")
                        .font(AppTheme.rounded(.subheadline))
                        .foregroundStyle(AppTheme.muted)
                    TextField("Snippet name", text: $title)
                        .textFieldStyle(.roundedBorder)
                        .font(AppTheme.rounded(.body))
                        .accessibilityLabel("Snippet name")
                    CodeEditor(text: $code, palette: EditorPalette.forScheme(scheme))
                        .frame(minHeight: 240, maxHeight: 420)
                        .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
                    HStack {
                        PrimaryButton(
                            title: isRunning ? "Running" : "Run",
                            systemImage: isRunning ? nil : "play.fill",
                            enabled: (engine.phase == .ready || engine.phase == .running) && !isRunning
                        ) {
                            run()
                        }
                        Button {
                            library.save(title: title, code: code)
                            title = ""
                        } label: {
                            Image(systemName: "square.and.arrow.down")
                                .font(.title3)
                                .frame(width: 52, height: 52)
                                .background(AppTheme.card)
                                .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
                        }
                        .buttonStyle(PressScaleButtonStyle())
                        .accessibilityLabel("Save snippet")
                    }
                    ConsoleBlock(
                        sections: [OutputSection(index: 0, title: "Output", stdout: output, stderr: "")],
                        emptyText: errorText.isEmpty ? "Run your snippet to see the output." : errorText
                    )
                    if let lastError {
                        ErrorHelpView(error: lastError, showTitle: true)
                            .padding(14)
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .background(AppTheme.flameStart.opacity(0.12))
                            .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
                    }
                    if !library.snippets.isEmpty {
                        Text("Saved snippets")
                            .font(AppTheme.rounded(.headline, weight: .bold))
                            .foregroundStyle(AppTheme.ink)
                        ForEach(library.snippets) { snippet in
                            HStack {
                                Button {
                                    code = snippet.code
                                    title = snippet.title
                                } label: {
                                    VStack(alignment: .leading, spacing: 2) {
                                        Text(snippet.title)
                                            .font(AppTheme.rounded(.body, weight: .semibold))
                                            .foregroundStyle(AppTheme.ink)
                                        Text(snippet.code)
                                            .font(.system(size: 13, design: .monospaced))
                                            .foregroundStyle(AppTheme.muted)
                                            .lineLimit(2)
                                    }
                                    .frame(maxWidth: .infinity, alignment: .leading)
                                }
                                .accessibilityLabel("Open \(snippet.title)")
                                Button {
                                    library.delete(snippet.id)
                                } label: {
                                    Image(systemName: "trash")
                                        .foregroundStyle(AppTheme.danger)
                                }
                                .accessibilityLabel("Delete \(snippet.title)")
                            }
                            .padding(12)
                            .coachCard()
                        }
                    }
                }
                .padding(20)
                .frame(maxWidth: 860)
                .frame(maxWidth: .infinity)
            }
            .background(AppTheme.paper)
            .navigationTitle("Playground")
        }
    }

    private func run() {
        guard !isRunning else { return }
        isRunning = true
        errorText = ""
        lastError = nil
        let source = code
        Task {
            let result = await engine.run(code: source, stdin: [], append: "", names: [], interactive: true)
            output = result.stdout
            if result.timedOut || result.errorType != nil {
                let explanation = FriendlyErrors.explain(
                    type: result.errorType,
                    message: result.errorMessage,
                    traceback: result.traceback,
                    timedOut: result.timedOut,
                    source: source
                )
                errorText = "Python stopped early. Read the note below."
                lastError = explanation
            } else if result.cancelled {
                errorText = "You closed the question."
            }
            isRunning = false
        }
    }
}
