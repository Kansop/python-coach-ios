import SwiftData
import SwiftUI

@main
struct PythonCoachApp: App {
    @StateObject private var runtime: RuntimeManager
    @StateObject private var progress: ProgressStore
    private let container: ModelContainer

    init() {
        UserSettings.registerDefaults()
        let container = AppModelContainer.make()
        self.container = container
        _runtime = StateObject(wrappedValue: RuntimeManager())
        _progress = StateObject(wrappedValue: ProgressStore(context: container.mainContext))
    }

    var body: some Scene {
        WindowGroup {
            RootView()
                .environmentObject(runtime)
                .environmentObject(progress)
                .modelContainer(container)
                .tint(AppTheme.accent)
        }
    }
}
