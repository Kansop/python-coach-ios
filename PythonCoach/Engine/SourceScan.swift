import Foundation

/// Finds real Python syntax, skipping text hidden inside strings and comments.
enum SourceScan {
    static func containsSnippet(_ source: String, _ snippet: String) -> Bool {
        let facts = scan(source)
        if snippet == "f\"" || snippet == "f'" {
            return facts.hasFString
        }
        if snippet == "#" {
            return facts.hasComment
        }
        if isIdentifier(snippet) {
            return containsWord(facts.stripped, snippet)
        }
        return facts.stripped.contains(snippet)
    }

    static func sentence(for snippet: String) -> String {
        switch snippet {
        case "#":
            return "Add a comment that starts with #."
        case "while":
            return "Use a while loop."
        case "for":
            return "Use a for loop."
        case "range":
            return "Use range to count."
        case "def":
            return "Define a function with def."
        case "return":
            return "Use return to hand a value back."
        case "and":
            return "Use and to check both things."
        case "if":
            return "Use an if statement."
        case "else":
            return "Add an else branch."
        case "elif":
            return "Use elif for the middle choice."
        case "input":
            return "Use input to ask a question."
        case "int":
            return "Use int to turn text into a number."
        case "len":
            return "Use len to count the characters."
        case "upper":
            return "Use .upper() to make capital letters."
        case "append":
            return "Use .append to add to the list."
        case "==":
            return "Use == to compare two values."
        case "(":
            return "Use parentheses so the addition happens first."
        case ")":
            return "Close the parentheses you opened."
        case "[":
            return "Use square brackets."
        case "+":
            return "Use + to join the pieces or do the math."
        case "*":
            return "Use * to multiply."
        case "/":
            return "Use / to divide."
        case "%":
            return "Use % to get the remainder."
        case "f\"", "f'":
            return "Use an f-string, with an f right before the quotes."
        default:
            return "Your code still needs \(snippet)."
        }
    }

    private struct Facts {
        var stripped: String
        var hasComment: Bool
        var hasFString: Bool
    }

    private static let prefixes: Set<String> = ["r", "u", "b", "f", "fr", "rf", "br", "rb", "ur", "ru", "fb", "bf"]

    private static func scan(_ source: String) -> Facts {
        let chars = Array(source)
        let count = chars.count
        var index = 0
        var stripped = ""
        var hasComment = false
        var hasFString = false

        func startsTriple(_ quote: Character, _ position: Int) -> Bool {
            position + 2 < count && chars[position] == quote && chars[position + 1] == quote && chars[position + 2] == quote
        }

        while index < count {
            let character = chars[index]
            if character == "#" {
                hasComment = true
                while index < count, chars[index] != "\n" {
                    stripped.append(" ")
                    index += 1
                }
                continue
            }
            if character.isLetter || character == "_" {
                let start = index
                index += 1
                while index < count, chars[index].isLetter || chars[index].isNumber || chars[index] == "_" {
                    index += 1
                }
                let word = String(chars[start..<index])
                if index < count, chars[index] == "'" || chars[index] == "\"", prefixes.contains(word.lowercased()) {
                    if word.lowercased().contains("f") {
                        hasFString = true
                    }
                    let quote = chars[index]
                    let end = consumeString(chars, index, quote, startsTriple(quote, index))
                    stripped.append(String(repeating: " ", count: end - start))
                    index = end
                    continue
                }
                stripped.append(word)
                continue
            }
            if character == "'" || character == "\"" {
                let end = consumeString(chars, index, character, startsTriple(character, index))
                stripped.append(String(repeating: " ", count: end - index))
                index = end
                continue
            }
            stripped.append(character)
            index += 1
        }
        return Facts(stripped: stripped, hasComment: hasComment, hasFString: hasFString)
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

    private static func isIdentifier(_ snippet: String) -> Bool {
        guard let first = snippet.first, first.isLetter || first == "_" else { return false }
        return snippet.allSatisfy { $0.isLetter || $0.isNumber || $0 == "_" }
    }

    private static func containsWord(_ haystack: String, _ word: String) -> Bool {
        var search = haystack.startIndex
        while let range = haystack.range(of: word, range: search..<haystack.endIndex) {
            let beforeOK = range.lowerBound == haystack.startIndex || !isWordCharacter(haystack[haystack.index(before: range.lowerBound)])
            let afterOK = range.upperBound == haystack.endIndex || !isWordCharacter(haystack[range.upperBound])
            if beforeOK && afterOK {
                return true
            }
            search = range.upperBound
        }
        return false
    }

    private static func isWordCharacter(_ character: Character) -> Bool {
        character.isLetter || character.isNumber || character == "_"
    }
}
