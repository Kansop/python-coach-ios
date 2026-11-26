import SwiftUI
import UIKit

enum AppTheme {
    static let accent = Color(red: 0.23, green: 0.38, blue: 0.93)
    static let onAccent = Color.white
    static let success = Color(red: 0.09, green: 0.62, blue: 0.42)
    static let danger = Color(red: 0.82, green: 0.27, blue: 0.30)

    static let paper = Color(uiColor: UIColor { traits in
        traits.userInterfaceStyle == .dark
            ? UIColor(red: 0.06, green: 0.08, blue: 0.12, alpha: 1)
            : UIColor(red: 0.95, green: 0.96, blue: 0.98, alpha: 1)
    })

    static let card = Color(uiColor: UIColor { traits in
        traits.userInterfaceStyle == .dark
            ? UIColor(red: 0.11, green: 0.14, blue: 0.20, alpha: 1)
            : UIColor(red: 1, green: 1, blue: 1, alpha: 1)
    })

    static let ink = Color(uiColor: UIColor { traits in
        traits.userInterfaceStyle == .dark
            ? UIColor(red: 0.92, green: 0.94, blue: 0.97, alpha: 1)
            : UIColor(red: 0.11, green: 0.14, blue: 0.19, alpha: 1)
    })

    static let muted = Color(uiColor: UIColor { traits in
        traits.userInterfaceStyle == .dark
            ? UIColor(red: 0.62, green: 0.68, blue: 0.76, alpha: 1)
            : UIColor(red: 0.36, green: 0.42, blue: 0.50, alpha: 1)
    })

    static let line = Color(uiColor: UIColor { traits in
        traits.userInterfaceStyle == .dark
            ? UIColor(white: 1, alpha: 0.08)
            : UIColor(red: 0.11, green: 0.14, blue: 0.19, alpha: 0.08)
    })

    static let editorBackground = Color(uiColor: UIColor { traits in
        traits.userInterfaceStyle == .dark
            ? UIColor(red: 0.07, green: 0.10, blue: 0.15, alpha: 1)
            : UIColor(red: 0.97, green: 0.98, blue: 0.99, alpha: 1)
    })

    static let console = Color(red: 0.07, green: 0.09, blue: 0.13)
    static let consoleText = Color(red: 0.83, green: 0.96, blue: 0.89)
    static let consoleMuted = Color(red: 0.62, green: 0.70, blue: 0.78)

    static let flameStart = Color(red: 1.0, green: 0.58, blue: 0.18)
    static let flameEnd = Color(red: 0.95, green: 0.32, blue: 0.22)

    static var flameGradient: LinearGradient {
        LinearGradient(colors: [flameStart, flameEnd], startPoint: .top, endPoint: .bottom)
    }

    static func rounded(_ style: Font.TextStyle, weight: Font.Weight = .regular) -> Font {
        .system(style, design: .rounded).weight(weight)
    }
}

enum AppMotion {
    static func spring(_ reduceMotion: Bool) -> Animation {
        if reduceMotion {
            return .easeOut(duration: 0.16)
        }
        return .spring(response: 0.48, dampingFraction: 0.84)
    }

    static func quick(_ reduceMotion: Bool) -> Animation {
        if reduceMotion {
            return .easeOut(duration: 0.12)
        }
        return .spring(response: 0.28, dampingFraction: 0.72)
    }
}

struct CardModifier: ViewModifier {
    @Environment(\.colorScheme) private var scheme

    func body(content: Content) -> some View {
        content
            .background(AppTheme.card)
            .clipShape(RoundedRectangle(cornerRadius: 22, style: .continuous))
            .overlay(
                RoundedRectangle(cornerRadius: 22, style: .continuous)
                    .stroke(AppTheme.line, lineWidth: 1)
            )
            .shadow(color: scheme == .dark ? .clear : Color.black.opacity(0.05), radius: 16, y: 8)
    }
}

extension View {
    func coachCard() -> some View {
        modifier(CardModifier())
    }
}

struct PressScaleButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        PressScaleBody(configuration: configuration)
    }

    private struct PressScaleBody: View {
        let configuration: ButtonStyleConfiguration
        @Environment(\.accessibilityReduceMotion) private var reduceMotion

        var body: some View {
            configuration.label
                .scaleEffect(!reduceMotion && configuration.isPressed ? 0.96 : 1)
                .opacity(configuration.isPressed ? 0.9 : 1)
                .animation(AppMotion.quick(reduceMotion), value: configuration.isPressed)
        }
    }
}
