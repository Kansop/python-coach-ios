import Foundation

struct DailyPick: Equatable, Identifiable {
    var id: String
    var title: String
    var prompt: String
    var starter: String
    var tests: [LessonTest]
    var xp: Int

    func asPractice() -> Practice {
        Practice(
            id: id,
            kind: "code",
            prompt: prompt,
            starterCode: starter,
            showCode: "",
            hints: [
                "Read the prompt again and match the output exactly.",
                "Run it, then change the part that does not match."
            ],
            sourceMustContain: [],
            sourceMustContainOneOf: [],
            tests: tests,
            choices: [],
            answer: -1,
            explain: "",
            carryCode: false
        )
    }
}

enum DailyChallengeBank {
    static let all: [DailyPick] = [
        DailyPick(
            id: "daily-hello",
            title: "Say it twice",
            prompt: "Print Hi on two lines.",
            starter: "print(\"Hi\")",
            tests: [LessonTest(stdin: [], appendCode: nil, stdoutEquals: "Hi\nHi", stdoutContains: [], values: [:])],
            xp: 15
        ),
        DailyPick(
            id: "daily-sum",
            title: "Add them",
            prompt: "Print the sum of 20 and 22.",
            starter: "print(0)",
            tests: [LessonTest(stdin: [], appendCode: nil, stdoutEquals: "42", stdoutContains: [], values: [:])],
            xp: 15
        ),
        DailyPick(
            id: "daily-shout",
            title: "Shout",
            prompt: "Set word to code and print it in uppercase.",
            starter: "word = \"code\"\nprint(word)",
            tests: [LessonTest(stdin: [], appendCode: nil, stdoutEquals: "CODE", stdoutContains: [], values: ["word": "'code'"])],
            xp: 15
        ),
        DailyPick(
            id: "daily-list",
            title: "First and last",
            prompt: "nums is [4, 8, 15]. Print the first and the last number on two lines.",
            starter: "nums = [4, 8, 15]\nprint(nums)",
            tests: [LessonTest(stdin: [], appendCode: nil, stdoutEquals: "4\n15", stdoutContains: [], values: [:])],
            xp: 15
        ),
        DailyPick(
            id: "daily-loop",
            title: "Three cheers",
            prompt: "Print Go three times, each on its own line.",
            starter: "print(\"Go\")",
            tests: [LessonTest(stdin: [], appendCode: nil, stdoutEquals: "Go\nGo\nGo", stdoutContains: [], values: [:])],
            xp: 15
        ),
        DailyPick(
            id: "daily-choice",
            title: "Warm or cold",
            prompt: "temp is 5. If temp is under 10, print Cold. Otherwise print Warm.",
            starter: "temp = 5",
            tests: [LessonTest(stdin: [], appendCode: nil, stdoutEquals: "Cold", stdoutContains: [], values: ["temp": "5"])],
            xp: 15
        ),
        DailyPick(
            id: "daily-dict",
            title: "Look it up",
            prompt: "pet is {\"name\": \"Luna\"}. Print pet[\"name\"].",
            starter: "pet = {\"name\": \"Luna\"}\nprint(pet)",
            tests: [LessonTest(stdin: [], appendCode: nil, stdoutEquals: "Luna", stdoutContains: [], values: [:])],
            xp: 15
        )
    ]

    static func pick(on date: Date, calendar: Calendar) -> DailyPick {
        let day = calendar.ordinality(of: .day, in: .era, for: date) ?? 0
        let index = ((day % all.count) + all.count) % all.count
        return all[index]
    }
}

struct DailyRecord: Equatable {
    var stamp: String

    static func stamp(for date: Date, calendar: Calendar) -> String {
        let day = calendar.startOfDay(for: date)
        let parts = calendar.dateComponents([.year, .month, .day], from: day)
        let year = parts.year ?? 0
        let month = parts.month ?? 0
        let dayNumber = parts.day ?? 0
        return String(format: "%04d-%02d-%02d", year, month, dayNumber)
    }

    func isDone(on date: Date, calendar: Calendar) -> Bool {
        stamp == Self.stamp(for: date, calendar: calendar)
    }

    func completed(on date: Date, calendar: Calendar) -> DailyRecord {
        DailyRecord(stamp: Self.stamp(for: date, calendar: calendar))
    }
}
