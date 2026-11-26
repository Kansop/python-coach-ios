import Foundation

struct ReviewItem: Equatable, Identifiable, Hashable {
    var lessonID: String
    var practiceID: String
    var misses: Int
    var lastPracticed: Date?

    var id: String { PracticeKey.make(lessonID: lessonID, practiceID: practiceID) }
}

/// Picks practices from finished lessons to bring back, weighted toward ones that were missed.
enum ReviewPlanner {
    static let sessionSize = 5
    static let xpPerItem = 3

    /// Every practice from a finished lesson. Project steps are left out because they build on each other.
    static func candidates(snapshot: ProgressSnapshot, units: [Unit]) -> [ReviewItem] {
        var items: [ReviewItem] = []
        for unit in units {
            for lesson in unit.lessons where !lesson.isProject {
                guard snapshot.lessons[lesson.id]?.completed == true else { continue }
                for practice in lesson.practices {
                    let saved = snapshot.practices[lesson.practiceKey(practice)]
                    items.append(
                        ReviewItem(
                            lessonID: lesson.id,
                            practiceID: practice.id,
                            misses: saved?.misses ?? 0,
                            lastPracticed: saved?.lastPracticed
                        )
                    )
                }
            }
        }
        return items
    }

    /// Missed practices count a lot. Practices not seen for a while count a little more.
    static func weight(_ item: ReviewItem, now: Date) -> Double {
        let missWeight = 4.0 * Double(min(item.misses, 5))
        var ageWeight = 2.0
        if let last = item.lastPracticed {
            let days = max(0, now.timeIntervalSince(last) / 86_400)
            ageWeight = min(days, 14) / 7
        }
        return 1.0 + missWeight + ageWeight
    }

    /// A weighted pick without repeats. The same seed gives the same session.
    static func pick(_ items: [ReviewItem], count: Int = sessionSize, now: Date, seed: UInt64) -> [ReviewItem] {
        var pool = items
        var picked: [ReviewItem] = []
        var generator = SplitMix64(seed: seed)
        while picked.count < count && !pool.isEmpty {
            let weights = pool.map { weight($0, now: now) }
            let total = weights.reduce(0, +)
            var target = generator.nextUnit() * total
            var chosen = pool.count - 1
            for (index, value) in weights.enumerated() {
                if target < value {
                    chosen = index
                    break
                }
                target -= value
            }
            picked.append(pool.remove(at: chosen))
        }
        return picked
    }

    static func daySeed(_ date: Date, calendar: Calendar) -> UInt64 {
        let parts = calendar.dateComponents([.year, .month, .day, .hour], from: date)
        let year = UInt64(max(parts.year ?? 0, 0))
        let month = UInt64(max(parts.month ?? 0, 0))
        let day = UInt64(max(parts.day ?? 0, 0))
        let hour = UInt64(max(parts.hour ?? 0, 0))
        return year &* 1_000_000 &+ month &* 10_000 &+ day &* 100 &+ hour
    }
}

/// Small deterministic random numbers, so review sessions are testable.
struct SplitMix64 {
    private var state: UInt64

    init(seed: UInt64) {
        state = seed
    }

    mutating func next() -> UInt64 {
        state &+= 0x9E37_79B9_7F4A_7C15
        var z = state
        z = (z ^ (z >> 30)) &* 0xBF58_476D_1CE4_E5B9
        z = (z ^ (z >> 27)) &* 0x94D0_49BB_1331_11EB
        return z ^ (z >> 31)
    }

    /// A number from 0 up to, but not including, 1.
    mutating func nextUnit() -> Double {
        Double(next() >> 11) / Double(UInt64(1) << 53)
    }
}
