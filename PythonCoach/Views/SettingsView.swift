import SwiftUI

struct SettingsView: View {
    @EnvironmentObject private var runtime: RuntimeManager
    @EnvironmentObject private var store: ProgressStore
    @AppStorage(UserSettings.sound) private var soundEnabled = true
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
                    Text("A short chime when an exercise passes. It follows the iPhone silent switch.")
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

    var body: some View {
        VStack(alignment: .leading, spacing: 18) {
            Image(systemName: "graduationcap.fill")
                .font(.system(size: 44))
                .foregroundStyle(AppTheme.accent)
            Text("Python runs on this iPhone")
                .font(AppTheme.rounded(.largeTitle, weight: .bold))
                .foregroundStyle(AppTheme.ink)
            Text("You'll read a short idea, run an example, then type the code yourself. Nothing is sent to a server. There are no ads and no account.")
                .font(AppTheme.rounded(.body))
                .foregroundStyle(AppTheme.muted)
            Spacer()
            PrimaryButton(title: "Start learning", systemImage: "arrow.right") {
                onStart()
                dismiss()
            }
        }
        .padding(24)
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .leading)
        .background(AppTheme.paper)
        .presentationDetents([.medium, .large])
    }
}
