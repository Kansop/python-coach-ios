import Foundation

struct CapturedRun: Equatable {
    var stdout: String
    var stderr: String
    var values: [String: String]
    var errorType: String?
    var errorMessage: String?
    var traceback: String?
    var needsInput: Bool
    var inputPrompt: String
    var timedOut: Bool
    var cancelled: Bool

    var failed: Bool {
        cancelled || timedOut || errorType != nil
    }

    static func failure(type: String, message: String, timedOut: Bool = false) -> CapturedRun {
        CapturedRun(
            stdout: "",
            stderr: "",
            values: [:],
            errorType: type,
            errorMessage: message,
            traceback: nil,
            needsInput: false,
            inputPrompt: "",
            timedOut: timedOut,
            cancelled: false
        )
    }

    static func cancelledRun(stdout: String = "", prompt: String = "") -> CapturedRun {
        CapturedRun(
            stdout: stdout,
            stderr: "",
            values: [:],
            errorType: nil,
            errorMessage: nil,
            traceback: nil,
            needsInput: false,
            inputPrompt: prompt,
            timedOut: false,
            cancelled: true
        )
    }
}

struct ErrorExplanation: Equatable {
    var title: String
    var message: String
    var line: Int?
    /// The learner's code on that line, when it is known.
    var lineText: String?
    /// One concrete thing to try next.
    var tip: String
    var detail: String
}

struct OutputSection: Equatable, Identifiable {
    var index: Int
    var title: String
    var stdout: String
    var stderr: String
    var id: Int { index }
}

struct LessonCheck: Equatable {
    var passed: Bool
    var headline: String
    var message: String
    var expected: String?
    var actual: String?
    var error: ErrorExplanation?
    var sections: [OutputSection]
}
