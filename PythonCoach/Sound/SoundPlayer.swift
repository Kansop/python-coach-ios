import AVFoundation
import UIKit

enum UserSettings {
    static let sound = "soundEnabled"
    static let haptics = "hapticsEnabled"
    static let appearance = "appearance"
    static let welcome = "hasSeenWelcome"

    static func registerDefaults() {
        UserDefaults.standard.register(defaults: [
            sound: false,
            haptics: true,
            appearance: "system",
            welcome: false
        ])
    }

    static var soundEnabled: Bool {
        UserDefaults.standard.bool(forKey: sound)
    }

    static var hapticsEnabled: Bool {
        UserDefaults.standard.bool(forKey: haptics)
    }
}

/// Plays a short original chime. Ambient playback follows the silent switch.
final class SoundPlayer {
    static let shared = SoundPlayer()
    private var player: AVAudioPlayer?

    func prepare() {
        guard player == nil, let url = Bundle.main.url(forResource: "SuccessChime", withExtension: "wav") else { return }
        player = try? AVAudioPlayer(contentsOf: url)
        player?.prepareToPlay()
        player?.volume = 0.55
    }

    func playSuccess() {
        guard UserSettings.soundEnabled else { return }
        let session = AVAudioSession.sharedInstance()
        try? session.setCategory(.ambient, options: [.mixWithOthers])
        try? session.setActive(true)
        if player == nil { prepare() }
        player?.currentTime = 0
        player?.play()
    }
}

enum Haptics {
    static func success() {
        guard UserSettings.hapticsEnabled else { return }
        let generator = UINotificationFeedbackGenerator()
        generator.prepare()
        generator.notificationOccurred(.success)
    }
}
