import SwiftUI

struct DownloadView: View {
    @EnvironmentObject private var runtime: RuntimeManager
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    var body: some View {
        VStack(spacing: 28) {
            Spacer()
            ZStack {
                Circle()
                    .fill(AppTheme.accent.opacity(0.14))
                    .frame(width: 148, height: 148)
                Image(systemName: "arrow.down.circle.fill")
                    .font(.system(size: 64))
                    .foregroundStyle(AppTheme.accent)
                    .symbolEffect(.pulse, options: .repeating, isActive: !reduceMotion)
            }
            VStack(spacing: 8) {
                Text("Putting Python on this iPhone")
                    .font(AppTheme.rounded(.title2, weight: .bold))
                    .foregroundStyle(AppTheme.ink)
                    .multilineTextAlignment(.center)
                Text("This happens once, about 14 MB. After that, lessons work offline, even in airplane mode.")
                    .font(AppTheme.rounded(.body))
                    .foregroundStyle(AppTheme.muted)
                    .multilineTextAlignment(.center)
            }
            VStack(alignment: .leading, spacing: 10) {
                XPBar(fraction: runtime.progress.fraction)
                HStack {
                    Text(runtime.progress.fileLabel.isEmpty ? "Starting download" : runtime.progress.fileLabel)
                        .font(AppTheme.rounded(.subheadline, weight: .semibold))
                        .foregroundStyle(AppTheme.ink)
                    Spacer()
                    Text(runtime.progress.percentText)
                        .font(AppTheme.rounded(.subheadline, weight: .bold))
                        .foregroundStyle(AppTheme.accent)
                        .monospacedDigit()
                }
                Text("File \(min(runtime.progress.fileIndex + 1, runtime.progress.fileCount)) of \(runtime.progress.fileCount)")
                    .font(AppTheme.rounded(.caption))
                    .foregroundStyle(AppTheme.muted)
            }
            .padding(18)
            .coachCard()
            Spacer()
        }
        .padding(24)
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(AppTheme.paper.ignoresSafeArea())
    }
}

struct CheckingView: View {
    var body: some View {
        VStack(spacing: 16) {
            ProgressView()
                .controlSize(.large)
            Text("Checking saved Python")
                .font(AppTheme.rounded(.headline, weight: .semibold))
                .foregroundStyle(AppTheme.ink)
            Text("If it's already on this iPhone, you can start right away.")
                .font(AppTheme.rounded(.body))
                .foregroundStyle(AppTheme.muted)
                .multilineTextAlignment(.center)
        }
        .padding(32)
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(AppTheme.paper.ignoresSafeArea())
    }
}

struct DownloadFailedView: View {
    @EnvironmentObject private var runtime: RuntimeManager

    var body: some View {
        VStack(spacing: 20) {
            Spacer()
            Image(systemName: "wifi.slash")
                .font(.system(size: 56))
                .foregroundStyle(AppTheme.danger)
            Text("Python isn't on this iPhone yet")
                .font(AppTheme.rounded(.title2, weight: .bold))
                .foregroundStyle(AppTheme.ink)
                .multilineTextAlignment(.center)
            Text(runtime.errorMessage)
                .font(AppTheme.rounded(.body))
                .foregroundStyle(AppTheme.muted)
                .multilineTextAlignment(.center)
            PrimaryButton(title: "Try again", systemImage: "arrow.clockwise") {
                runtime.retry()
            }
            Spacer()
        }
        .padding(24)
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(AppTheme.paper.ignoresSafeArea())
    }
}
