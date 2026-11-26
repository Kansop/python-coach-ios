import SwiftUI

struct MainShell: View {
    let cacheDirectory: URL
    @StateObject private var engine = PythonEngine()
    @AppStorage(UserSettings.welcome) private var hasSeenWelcome = false
    @State private var showWelcome = false

    var body: some View {
        ZStack(alignment: .topLeading) {
            TabView {
                HomeView()
                    .tabItem { Label("Learn", systemImage: "book.fill") }
                PlaygroundView()
                    .tabItem { Label("Play", systemImage: "terminal.fill") }
                ProgressScreen()
                    .tabItem { Label("Progress", systemImage: "chart.bar.fill") }
                SettingsView()
                    .tabItem { Label("Settings", systemImage: "gearshape.fill") }
            }
            HiddenPythonView(webView: engine.webView, generation: engine.webViewGeneration)
                .frame(width: 8, height: 8)
                .opacity(0.01)
                .accessibilityHidden(true)
                .allowsHitTesting(false)
        }
        .environmentObject(engine)
        .sheet(isPresented: inputPresented) {
            InputPromptSheet(prompt: engine.inputRequest?.prompt ?? "Type an answer") { answer in
                engine.finishInput(answer)
            }
        }
        .sheet(isPresented: $showWelcome, onDismiss: { hasSeenWelcome = true }) {
            WelcomeSheet {
                hasSeenWelcome = true
            }
        }
        .onAppear {
            engine.start(cacheDirectory: cacheDirectory)
            SoundPlayer.shared.prepare()
            if !hasSeenWelcome {
                showWelcome = true
            }
        }
    }

    private var inputPresented: Binding<Bool> {
        Binding(
            get: { engine.inputRequest != nil },
            set: { presented in
                if !presented {
                    engine.finishInput(nil)
                }
            }
        )
    }
}

struct RootView: View {
    @EnvironmentObject private var runtime: RuntimeManager
    @AppStorage(UserSettings.appearance) private var appearance = "system"
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    var body: some View {
        Group {
            switch runtime.phase {
            case .checking:
                CheckingView()
            case .downloading:
                DownloadView()
            case .failed:
                DownloadFailedView()
            case .ready:
                if let cache = runtime.cacheDirectory {
                    MainShell(cacheDirectory: cache)
                } else {
                    DownloadFailedView()
                }
            }
        }
        .preferredColorScheme(preferredScheme)
        .animation(AppMotion.spring(reduceMotion), value: runtime.phase)
        .task {
            runtime.prepare()
        }
    }

    private var preferredScheme: ColorScheme? {
        switch appearance {
        case "light": return .light
        case "dark": return .dark
        default: return nil
        }
    }
}
