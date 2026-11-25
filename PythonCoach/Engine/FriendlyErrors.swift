import Foundation

enum FriendlyErrors {
    static func explain(type: String?, message: String?, traceback: String?, timedOut: Bool) -> ErrorExplanation {
        if timedOut || type == "TimeoutError" {
            return ErrorExplanation(
                title: "That ran too long",
                message: "I stopped the program. Look for a loop that never ends, like while True without changing something.",
                line: nil,
                detail: "TimeoutError: The run was stopped after a few seconds."
            )
        }

        let errorType = type ?? "Error"
        let raw = message ?? ""
        let line = lineNumber(in: traceback) ?? lineNumber(in: raw)
        var title = "Python found a problem"
        var body = "Something went wrong. \(raw)"

        switch errorType {
        case "SyntaxError":
            title = "Python couldn't read that"
            body = "A symbol is missing or extra. Check quotes, parentheses, and colons. \(raw)"
        case "IndentationError", "TabError":
            title = "The spacing is off"
            body = "Lines inside if, for, while, and def need to be indented, usually by 4 spaces. Mix spaces and tabs and Python gets confused."
        case "NameError":
            title = "Unknown name"
            body = nameMessage(raw)
        case "TypeError":
            title = "Those types don't mix"
            body = typeMessage(raw)
        case "ZeroDivisionError":
            title = "Can't divide by zero"
            body = "Dividing by zero isn't allowed in math or in Python."
        case "IndexError":
            title = "That spot isn't in the list"
            body = "You asked for an item that isn't there. The first item is index 0."
        case "KeyError":
            title = "That key isn't in the dictionary"
            body = "Check the spelling of the key. Keys are case-sensitive. \(raw)"
        case "ValueError":
            title = "That value doesn't fit"
            if raw.contains("invalid literal for int") {
                body = "int() needs text made of digits, like 12. Words and empty answers won't work."
            } else {
                body = raw.isEmpty ? "Python didn't know how to use that value." : raw
            }
        case "EOFError":
            title = "Python wanted an answer"
            body = raw.isEmpty ? "This program asked for more input than the exercise provides." : raw
        case "RecursionError":
            title = "The function called itself too much"
            body = "It kept calling itself and never stopped. Check the base case."
        case "ModuleNotFoundError", "ImportError":
            title = "That module isn't on this iPhone"
            body = "The lessons use normal Python. You don't need to import anything extra for them."
        case "AttributeError":
            title = "That thing doesn't have that tool"
            body = "Check the spelling after the dot. \(raw)"
        default:
            title = "Python found a problem"
            body = raw.isEmpty ? errorType : "\(errorType): \(raw)"
        }

        if let line {
            body += " Look at line \(line)."
        }

        let detailSource = (traceback?.isEmpty == false ? traceback! : "\(errorType): \(raw)")
        return ErrorExplanation(title: title, message: body, line: line, detail: detailSource)
    }

    private static func nameMessage(_ raw: String) -> String {
        let name = firstMatch(#"name '([^']+)' is not defined"#, in: raw)
        if let name {
            if name != "print" && name.lowercased() == "print" {
                return "Python doesn't know '\(name)'. Python is case-sensitive. The command is print, all lowercase."
            }
            if ["prnt", "prin", "pint", "pirnt"].contains(name) {
                return "Python doesn't know '\(name)'. Did you mean print?"
            }
            if raw.contains("Did you mean") {
                return "Python doesn't know '\(name)'. \(raw)"
            }
            return "Python doesn't know '\(name)'. Check the spelling and the capital letters."
        }
        return raw.isEmpty ? "Python ran into a name it doesn't know." : raw
    }

    private static func typeMessage(_ raw: String) -> String {
        let lowered = raw.lowercased()
        if lowered.contains("concatenate") || lowered.contains("can only concatenate") {
            return "You're mixing text and a number. Wrap the number in str(), or use an f-string."
        }
        if lowered.contains("unsupported operand") {
            return "Those values can't use that math symbol together. \(raw)"
        }
        if lowered.contains("not callable") {
            return "Python tried to call something that isn't a function. Check the parentheses."
        }
        return raw.isEmpty ? "A value had a type Python didn't expect." : raw
    }

    private static func lineNumber(in text: String?) -> Int? {
        guard let text else { return nil }
        if let value = firstMatch(#"File "<your code>", line (\d+)"#, in: text), let line = Int(value) {
            return line
        }
        if let value = firstMatch(#"\(<your code>, line (\d+)\)"#, in: text), let line = Int(value) {
            return line
        }
        return nil
    }

    private static func firstMatch(_ pattern: String, in text: String) -> String? {
        guard let regex = try? NSRegularExpression(pattern: pattern) else { return nil }
        let range = NSRange(text.startIndex..<text.endIndex, in: text)
        guard let match = regex.firstMatch(in: text, range: range), match.numberOfRanges > 1,
              let capture = Range(match.range(at: 1), in: text) else {
            return nil
        }
        return String(text[capture])
    }
}
