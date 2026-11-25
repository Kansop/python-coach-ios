import Foundation

enum TokenKind: Equatable {
    case keyword
    case builtin
    case string
    case comment
    case number
}

struct SyntaxToken: Equatable {
    var range: Range<String.Index>
    var kind: TokenKind
}

enum SyntaxHighlighter {
    static let keywords: Set<String> = [
        "False", "None", "True", "and", "as", "assert", "async", "await", "break", "class",
        "continue", "def", "del", "elif", "else", "except", "finally", "for", "from", "global",
        "if", "import", "in", "is", "lambda", "nonlocal", "not", "or", "pass", "raise", "return",
        "try", "while", "with", "yield"
    ]

    static let builtins: Set<String> = [
        "print", "input", "len", "range", "int", "str", "float", "list", "dict", "bool", "type",
        "round", "sum", "min", "max", "abs", "sorted", "enumerate", "zip", "map", "filter",
        "isinstance", "repr", "super"
    ]

    static func tokens(in source: String) -> [SyntaxToken] {
        let chars = Array(source)
        let count = chars.count
        var index = 0
        var tokens: [SyntaxToken] = []

        func emit(_ start: Int, _ end: Int, _ kind: TokenKind) {
            guard end > start, end <= count else { return }
            let lower = source.index(source.startIndex, offsetBy: start)
            let upper = source.index(source.startIndex, offsetBy: end)
            tokens.append(SyntaxToken(range: lower..<upper, kind: kind))
        }

        func startsTriple(_ quote: Character, _ position: Int) -> Bool {
            position + 2 < count && chars[position] == quote && chars[position + 1] == quote && chars[position + 2] == quote
        }

        while index < count {
            let character = chars[index]
            if character == "#" {
                let start = index
                while index < count, chars[index] != "\n" { index += 1 }
                emit(start, index, .comment)
                continue
            }
            if character.isNumber || (character == "." && index + 1 < count && chars[index + 1].isNumber) {
                let start = index
                index += 1
                while index < count {
                    let next = chars[index]
                    if next.isNumber || next == "." {
                        index += 1
                        continue
                    }
                    break
                }
                emit(start, index, .number)
                continue
            }
            if character.isLetter || character == "_" {
                let start = index
                index += 1
                while index < count, chars[index].isLetter || chars[index].isNumber || chars[index] == "_" {
                    index += 1
                }
                let word = String(chars[start..<index])
                if index < count, chars[index] == "'" || chars[index] == "\"", isStringPrefix(word) {
                    let quote = chars[index]
                    let end = consumeString(chars, index, quote, startsTriple(quote, index))
                    emit(start, end, .string)
                    index = end
                    continue
                }
                if keywords.contains(word) {
                    emit(start, index, .keyword)
                } else if builtins.contains(word) {
                    emit(start, index, .builtin)
                }
                continue
            }
            if character == "'" || character == "\"" {
                let end = consumeString(chars, index, character, startsTriple(character, index))
                emit(index, end, .string)
                index = end
                continue
            }
            index += 1
        }
        return tokens
    }

    private static func isStringPrefix(_ word: String) -> Bool {
        let lowered = word.lowercased()
        return ["r", "u", "b", "f", "fr", "rf", "br", "rb", "ur", "ru", "fb", "bf"].contains(lowered)
    }

    private static func consumeString(_ chars: [Character], _ start: Int, _ quote: Character, _ triple: Bool) -> Int {
        let count = chars.count
        var index = start
        if triple {
            index += 3
            while index < count {
                if index + 2 < count, chars[index] == quote, chars[index + 1] == quote, chars[index + 2] == quote {
                    return index + 3
                }
                index += 1
            }
            return index
        }
        index += 1
        while index < count {
            if chars[index] == "\\" {
                index += 2
                continue
            }
            if chars[index] == "\n" {
                return index
            }
            if chars[index] == quote {
                return index + 1
            }
            index += 1
        }
        return index
    }
}
