import Foundation

// Linux-friendly check that LessonChecker and FriendlyErrors (the Swift code the app ships)
// agree with the Python lesson checker on real CPython runs. Built by swift_parity.sh.

struct Fixture: Decodable {
    struct Run: Decodable {
        var stdout: String
        var stderr: String
        var values: [String: String]
        var errorType: String?
        var errorMessage: String?
        var traceback: String?
        var timedOut: Bool

        var captured: CapturedRun {
            CapturedRun(
                stdout: stdout, stderr: stderr, values: values,
                errorType: errorType, errorMessage: errorMessage, traceback: traceback,
                needsInput: false, inputPrompt: "", timedOut: timedOut, cancelled: false
            )
        }
    }
    struct Case: Decodable {
        var lesson: String
        var practice: String
        var label: String
        var source: String
        var expected: Bool
        var why: String
        var runs: [Run]
    }
    struct Crash: Decodable {
        var lesson: String
        var source: String
        var run: Run
    }
    var cases: [Case]
    var crashes: [Crash]
}

let path = CommandLine.arguments[1]
let fixture = try JSONDecoder().decode(Fixture.self, from: Data(contentsOf: URL(fileURLWithPath: path)))
var failures: [String] = []
var agreed = 0
var passedCount = 0

for item in fixture.cases {
    guard let lesson = Curriculum.lesson(id: item.lesson), let practice = lesson.practice(id: item.practice) else {
        failures.append("\(item.lesson)/\(item.practice): missing from CurriculumJSON")
        continue
    }
    let check = LessonChecker.blankCheck(source: item.source)
        ?? LessonChecker.evaluate(source: item.source, practice: practice, runs: item.runs.map(\.captured))
    if check.passed == item.expected {
        agreed += 1
        if check.passed { passedCount += 1 }
    } else {
        failures.append("\(item.lesson)/\(item.practice) \(item.label): Swift says \(check.passed), Python says \(item.expected) (\(item.why)); message: \(check.message)")
    }
    if !check.passed && check.message.isEmpty {
        failures.append("\(item.lesson)/\(item.practice) \(item.label): empty feedback")
    }
}

var pointed = 0
var generic: [String] = []
for crash in fixture.crashes {
    let run = crash.run
    let error = FriendlyErrors.explain(type: run.errorType, message: run.errorMessage, traceback: run.traceback, timedOut: run.timedOut, source: crash.source)
    let lines = crash.source.components(separatedBy: "\n")
    if let line = error.line, line >= 1, line <= lines.count, error.lineText != nil {
        pointed += 1
    } else {
        failures.append("\(crash.lesson): \(run.errorType ?? "?") did not point at a line of the learner's code")
    }
    if error.title == "Python hit a problem" || error.tip.isEmpty {
        generic.append("\(crash.lesson): \(run.errorType ?? "?") \(run.errorMessage ?? "")")
    }
}

print("checker cases: \(fixture.cases.count), agreed with Python: \(agreed), passing solutions: \(passedCount)")
print("mistake crashes: \(fixture.crashes.count), pointed at the learner's line: \(pointed), generic explanations: \(generic.count)")
for item in generic { print("  generic: \(item)") }
for failure in failures { print("FAIL: \(failure)") }
exit(failures.isEmpty ? 0 : 1)
