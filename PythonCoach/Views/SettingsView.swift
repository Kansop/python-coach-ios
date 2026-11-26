import SwiftUI

struct SettingsView: View {
    @EnvironmentObject private var runtime: RuntimeManager
    @EnvironmentObject private var store: ProgressStore
    @AppStorage(UserSettings.sound) private var soundEnabled = false
    @AppStorage(UserSettings.haptics) private var hapticsEnabled = true
    @AppStorage(UserSettings.appearance) private var appearance = "system"
    @State private var confirmReset = false
    @State private var confirmRepair = false

    var body: some View {
        NavigationStack {
            Form {
                Section {
                    Toggle(isOn: $soundEnabled) {
                        Label("Success sound", systemImage: soundEnabled ? "speaker.wave.2.fill" : "speaker.slash.fill")
                    }
                    Text("Off unless you turn it on. A short chime when a lesson is finished. It follows the iPhone silent switch.")
                        .font(AppTheme.rounded(.footnote))
                        .foregroundStyle(AppTheme.muted)
                    Button {
                        SoundPlayer.shared.playSuccess()
                    } label: {
                        Label("Play the chime", systemImage: "play.fill")
                    }
                    .disabled(!soundEnabled)
                    Toggle(isOn: $hapticsEnabled) {
                        Label("Light haptic", systemImage: "iphone")
                    }
                } header: {
                    Text("Feedback")
                }

                Section {
                    Picker("Appearance", selection: $appearance) {
                        Label("System", systemImage: "circle.lefthalf.filled").tag("system")
                        Label("Light", systemImage: "sun.max.fill").tag("light")
                        Label("Dark", systemImage: "moon.fill").tag("dark")
                    }
                } header: {
                    Text("Look")
                }

                Section {
                    Button {
                        confirmRepair = true
                    } label: {
                        Label("Redownload Python", systemImage: "arrow.clockwise")
                    }
                    Button(role: .destructive) {
                        confirmReset = true
                    } label: {
                        Label("Reset progress", systemImage: "trash")
                    }
                } header: {
                    Text("On this iPhone")
                } footer: {
                    Text("Progress, streaks, and saved code stay on this iPhone. There is no account and nothing is tracked.")
                }

                Section {
                    LabeledContent("Version", value: "1.0")
                    Text("Python runs on this iPhone with Pyodide \(PyodideCache.version). The runtime is downloaded once from the official Pyodide CDN and cached here. Pyodide is licensed under the Mozilla Public License 2.0.")
                        .font(AppTheme.rounded(.footnote))
                        .foregroundStyle(AppTheme.muted)
                } header: {
                    Text("About")
                }
            }
            .scrollContentBackground(.hidden)
            .background(AppTheme.paper)
            .navigationTitle("Settings")
            .confirmationDialog("Download Python again? You'll need the internet.", isPresented: $confirmRepair, titleVisibility: .visible) {
                Button("Redownload", role: .destructive) { runtime.repair() }
                Button("Cancel", role: .cancel) {}
            }
            .confirmationDialog("Erase lessons, XP, and the streak?", isPresented: $confirmReset, titleVisibility: .visible) {
                Button("Erase progress", role: .destructive) { store.reset() }
                Button("Cancel", role: .cancel) {}
            }
        }
    }
}

struct WelcomeSheet: View {
    var onStart: () -> Void
    @Environment(\.dismiss) private var dismiss
    @State private var page = 0

    private let pages: [(String, String, String)] = [
        ("graduationcap.fill", "Python runs on this iPhone", "Nothing is sent to a server. There is no account, no ads, and no tracking. After one download, lessons work offline."),
        ("book.fill", "Learn, see, then try", "Each lesson teaches one idea. You read it, walk through an example line by line, then practice in small steps that start easy."),
        ("lightbulb.fill", "Hints and help with errors", "Hints open one at a time. The last one shows the answer if you're stuck. When Python shows an error, the app explains it in plain words and points at the line."),
        ("arrow.triangle.2.circlepath", "Review makes it stick", "Review brings back practice from lessons you finished, especially the ones you found tricky.")
    ]

    var body: some View {
        VStack(alignment: .leading, spacing: 18) {
            TabView(selection: $page) {
                ForEach(pages.indices, id: \.self) { index in
                    VStack(alignment: .leading, spacing: 14) {
                        Image(systemName: pages[index].0)
                            .font(.system(size: 44))
                            .foregroundStyle(AppTheme.accent)
                            .accessibilityHidden(true)
                        Text(pages[index].1)
                            .font(AppTheme.rounded(.largeTitle, weight: .bold))
                            .foregroundStyle(AppTheme.ink)
                            .accessibilityAddTraits(.isHeader)
                        Text(pages[index].2)
                            .font(AppTheme.rounded(.body))
                            .foregroundStyle(AppTheme.muted)
                        Spacer()
                    }
                    .padding(.top, 12)
                    .tag(index)
                    .accessibilityElement(children: .combine)
                }
            }
            .tabViewStyle(.page(indexDisplayMode: .always))
            .frame(maxHeight: .infinity)
            PrimaryButton(title: page == pages.count - 1 ? "Start learning" : "Next", systemImage: "arrow.right") {
                if page < pages.count - 1 {
                    withAnimation { page += 1 }
                } else {
                    onStart()
                    dismiss()
                }
            }
            .accessibilityHint(page == pages.count - 1 ? "Closes the introduction" : "Shows the next introduction page")
        }
        .padding(24)
        .frame(maxWidth: 640)
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .leading)
        .background(AppTheme.paper)
        .presentationDetents([.medium, .large])
    }
}
