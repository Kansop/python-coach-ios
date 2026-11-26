import SwiftUI

struct CelebrationView: View {
    var result: CompletionResult
    var nextTitle: String?
    var onNext: () -> Void
    var onStay: () -> Void
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @State private var showMark = false
    @State private var burst = false

    var body: some View {
        ZStack {
            AppTheme.paper.opacity(0.94).ignoresSafeArea()
            VStack(spacing: 18) {
                ZStack {
                    if !reduceMotion {
                        confetti
                    }
                    Image(systemName: "checkmark.circle.fill")
                        .font(.system(size: 88))
                        .foregroundStyle(AppTheme.success)
                        .scaleEffect(showMark ? 1 : 0.4)
                        .symbolEffect(.bounce, value: showMark)
                }
                .frame(height: 160)
                Text(result.leveledUp ? "Level up" : "Nice work")
                    .font(AppTheme.rounded(.largeTitle, weight: .bold))
                    .foregroundStyle(AppTheme.ink)
                    .accessibilityAddTraits(.isHeader)
                if result.leveledUp {
                    Text("You reached level \(result.level)")
                        .font(AppTheme.rounded(.title3, weight: .semibold))
                        .foregroundStyle(AppTheme.accent)
                }
                VStack(spacing: 6) {
                    if result.xpGained > 0 {
                        Text("+\(result.xpGained) XP")
                            .font(AppTheme.rounded(.title3, weight: .bold))
                            .foregroundStyle(AppTheme.accent)
                            .contentTransition(.numericText())
                    } else {
                        Text("Practice counts. You already earned this XP.")
                            .font(AppTheme.rounded(.body))
                            .foregroundStyle(AppTheme.muted)
                            .multilineTextAlignment(.center)
                    }
                    if result.leveledUp {
                        Text("Level \(result.level): \(result.levelTitle)")
                            .font(AppTheme.rounded(.headline, weight: .semibold))
                            .foregroundStyle(AppTheme.ink)
                    }
                    if result.streakIncreased {
                        Label("Streak is \(result.streak) \(result.streak == 1 ? "day" : "days")", systemImage: "flame.fill")
                            .font(AppTheme.rounded(.subheadline, weight: .semibold))
                            .foregroundStyle(AppTheme.flameEnd)
                    } else if result.streakReset {
                        Text("New streak started.")
                            .font(AppTheme.rounded(.subheadline))
                            .foregroundStyle(AppTheme.muted)
                    }
                    if let unit = result.finishedUnitTitle {
                        Text("You finished \(unit).")
                            .font(AppTheme.rounded(.subheadline, weight: .semibold))
                            .foregroundStyle(AppTheme.ink)
                    }
                    ForEach(result.newBadges) { badge in
                        Label(badge.title, systemImage: badge.symbol)
                            .font(AppTheme.rounded(.subheadline, weight: .semibold))
                            .foregroundStyle(AppTheme.accent)
                    }
                }
                .padding(.horizontal, 12)
                VStack(spacing: 10) {
                    PrimaryButton(title: nextTitle ?? "Back to the path", systemImage: "arrow.right", action: onNext)
                    Button("Stay here", action: onStay)
                        .font(AppTheme.rounded(.body, weight: .semibold))
                        .foregroundStyle(AppTheme.muted)
                        .buttonStyle(PressScaleButtonStyle())
                }
                .padding(.top, 8)
            }
            .padding(24)
        }
        .accessibilityAddTraits(.isModal)
        .onAppear {
            SoundPlayer.shared.playSuccess()
            Haptics.success()
            if reduceMotion {
                showMark = true
                burst = true
            } else {
                withAnimation(.spring(response: 0.5, dampingFraction: 0.68)) {
                    showMark = true
                }
                withAnimation(.easeOut(duration: 0.9)) {
                    burst = true
                }
            }
        }
    }

    private var confetti: some View {
        ZStack {
            ForEach(ConfettiPiece.burst) { piece in
                Circle()
                    .fill(piece.color)
                    .frame(width: piece.size, height: piece.size)
                    .offset(
                        x: burst ? CGFloat(cos(piece.angle)) * piece.distance : 0,
                        y: burst ? CGFloat(sin(piece.angle)) * piece.distance : 0
                    )
                    .opacity(burst ? 0 : 1)
            }
        }
    }
}

private struct ConfettiPiece: Identifiable {
    var id: Int
    var angle: Double
    var distance: CGFloat
    var size: CGFloat
    var color: Color

    static let burst: [ConfettiPiece] = [
        ConfettiPiece(id: 0, angle: 0.2, distance: 110, size: 9, color: AppTheme.accent),
        ConfettiPiece(id: 1, angle: 0.7, distance: 130, size: 7, color: AppTheme.flameStart),
        ConfettiPiece(id: 2, angle: 1.2, distance: 100, size: 8, color: AppTheme.success),
        ConfettiPiece(id: 3, angle: 1.8, distance: 120, size: 6, color: AppTheme.accent),
        ConfettiPiece(id: 4, angle: 2.3, distance: 140, size: 9, color: AppTheme.flameEnd),
        ConfettiPiece(id: 5, angle: 2.8, distance: 105, size: 7, color: AppTheme.success),
        ConfettiPiece(id: 6, angle: 3.4, distance: 125, size: 8, color: AppTheme.accent),
        ConfettiPiece(id: 7, angle: 4.0, distance: 115, size: 6, color: AppTheme.flameStart),
        ConfettiPiece(id: 8, angle: 4.6, distance: 135, size: 9, color: AppTheme.success),
        ConfettiPiece(id: 9, angle: 5.2, distance: 100, size: 7, color: AppTheme.flameEnd),
        ConfettiPiece(id: 10, angle: 5.7, distance: 120, size: 8, color: AppTheme.accent),
        ConfettiPiece(id: 11, angle: 6.1, distance: 110, size: 6, color: AppTheme.success)
    ]
}
