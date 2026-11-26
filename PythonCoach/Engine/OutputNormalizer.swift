import Foundation

enum OutputNormalizer {
    /// Ignores trailing spaces and extra blank lines so a correct program still passes.
    static func normalize(_ raw: String) -> String {
        let unified = raw.replacingOccurrences(of: "\r\n", with: "\n").replacingOccurrences(of: "\r", with: "\n")
        var lines = unified.split(separator: "\n", omittingEmptySubsequences: false).map { trimTrailingWhitespace(String($0)) }
        while lines.last == "" {
            lines.removeLast()
        }
        while lines.first == "" {
            lines.removeFirst()
        }
        return lines.joined(separator: "\n")
    }

    private static func trimTrailingWhitespace(_ line: String) -> String {
        var text = line
        while let last = text.last, last.isWhitespace, last != "\n" {
            text.removeLast()
        }
        return text
    }
}
