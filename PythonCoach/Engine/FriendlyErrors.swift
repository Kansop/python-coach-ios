import Foundation

/// Turns Python errors into short, kind explanations that point at the learner's line.
enum FriendlyErrors {
    static let encouragement = "Every coder sees errors. They are clues, not failures."

    static func explain(
        type: String?,
        message: String?,
        traceback: String?,
        timedOut: Bool,
        source: String? = nil
    ) -> ErrorExplanation {
        let errorType = (timedOut ? "TimeoutError" : type) ?? "Error"
        let raw = message ?? ""
        let line = lineNumber(in: traceback) ?? lineNumber(in: raw)
        let lineText = line.flatMap { codeLine($0, in: source) }
        let parts = describe(type: errorType, raw: raw, lineText: lineText)

        var body = parts.what
        if let line {
            body += " Look at line \(line)."
        }
        let detail: String
        if let traceback, !traceback.isEmpty {
            detail = traceback
        } else if errorType == "TimeoutError" {
            detail = "TimeoutError: the run was stopped after a few seconds."
        } else {
            detail = raw.isEmpty ? errorType : "\(errorType): \(raw)"
        }
        return ErrorExplanation(
            title: parts.title,
            message: body,
            line: line,
            lineText: lineText,
            tip: parts.tip,
            detail: detail
        )
    }

    struct Parts {
        var title: String
        var what: String
        var tip: String
    }

    // MARK: - Error kinds

    static func describe(type: String, raw: String, lineText: String?) -> Parts {
        switch type {
        case "TimeoutError":
            return Parts(
                title: "That loop kept going",
                what: "Your program ran for too long, so I stopped it. Usually a loop never reaches its end.",
                tip: "In a while loop, make sure something changes each time around, like count = count + 1, so the condition can become False."
            )
        case "SyntaxError":
            return syntax(raw, lineText: lineText)
        case "IndentationError", "TabError":
            return indentation(raw)
        case "NameError", "UnboundLocalError":
            return name(raw, type: type)
        case "TypeError":
            return typeError(raw)
        case "ZeroDivisionError":
            return Parts(
                title: "Dividing by zero",
                what: "Your code tried to divide by 0. That has no answer, in math or in Python.",
                tip: "Check the number after / or %. If it might be 0, use an if to skip the division."
            )
        case "IndexError":
            return index(raw)
        case "KeyError":
            let key = raw.isEmpty ? "that key" : raw
            return Parts(
                title: "That key isn't in the dictionary",
                what: "You asked the dictionary for \(key), but it doesn't have that key.",
                tip: "Keys must match exactly, including capital letters. You can check first with: if key in my_dict:"
            )
        case "ValueError":
            return value(raw)
        case "AttributeError":
            return attribute(raw)
        case "EOFError":
            return Parts(
                title: "Python wanted another answer",
                what: "Your program called input() more times than this exercise gives answers for.",
                tip: "Count your input() calls. The exercise says how many questions to ask."
            )
        case "RecursionError":
            return Parts(
                title: "The function kept calling itself",
                what: "A function called itself over and over and never stopped.",
                tip: "Give it a stopping case: an if that returns without calling the function again."
            )
        case "ModuleNotFoundError", "ImportError":
            return Parts(
                title: "That module isn't here",
                what: "Python couldn't find the module you imported.",
                tip: "The lessons only need plain Python. Check the spelling, or remove the import."
            )
        default:
            let shown = raw.isEmpty ? type : "\(type): \(raw)"
            return Parts(
                title: "Python hit a problem",
                what: "Python stopped with this message: \(shown).",
                tip: "Read the line it points to, and compare it with the example."
            )
        }
    }

    private static func syntax(_ raw: String, lineText: String?) -> Parts {
        let lowered = raw.lowercased()
        let title = "Python couldn't read that line"
        if lowered.contains("invalid character") && (raw.contains("U+201C") || raw.contains("U+201D") || raw.contains("U+2018") || raw.contains("U+2019")) {
            return Parts(title: "Curly quotes sneaked in", what: "That line has curly quotes like \u{201C} or \u{2019}. Python only understands straight quotes.", tip: "Delete the quote marks and type them again with the \" or ' key above the keyboard.")
        }
        if lowered.contains("invalid character") {
            return Parts(title: title, what: "That line has a symbol Python doesn't know.", tip: "Look for an odd character, like a fancy dash or an emoji, and retype it.")
        }
        if lowered.contains("unterminated string") || lowered.contains("eol while scanning") || lowered.contains("unterminated triple-quoted") {
            return Parts(title: "A quote is missing", what: "Some text starts with a quote mark but never ends with one.", tip: "Text needs a quote at the start and the same kind of quote at the end, like \"hello\".")
        }
        if lowered.contains("was never closed") {
            let symbol = firstMatch(#"'(.)' was never closed"#, in: raw) ?? "("
            return Parts(title: "A bracket is still open", what: "You opened a \(symbol) but never closed it.", tip: "Every \(symbol) needs a partner \(closing(symbol)). Add it at the end of the line.")
        }
        if lowered.contains("unmatched") {
            let symbol = firstMatch(#"unmatched '(.)'"#, in: raw) ?? ")"
            return Parts(title: "An extra bracket", what: "There's a \(symbol) without a matching opening bracket.", tip: "Count your brackets. Each opening one needs exactly one closing one.")
        }
        if lowered.contains("does not match opening parenthesis") {
            return Parts(title: "Brackets don't match", what: "A closing bracket doesn't match the one that opened.", tip: "( goes with ), [ goes with ], and { goes with }.")
        }
        if lowered.contains("expected ':'") {
            return Parts(title: "A colon is missing", what: "Lines that start with if, elif, else, for, while, def, or class must end with a colon.", tip: "Add : at the end of that line.")
        }
        if lowered.contains("missing parentheses in call to 'print'") {
            return Parts(title: "print needs parentheses", what: "In Python 3, print is a function, so it needs ( ).", tip: "Write print(\"hello\"), not print \"hello\".")
        }
        if lowered.contains("maybe you meant '=='") || lowered.contains("cannot assign to") {
            return Parts(title: "= or ==?", what: "One = puts a value into a variable. Two == asks whether two things are equal.", tip: "Inside an if or while, compare with ==, like if age == 13:")
        }
        if lowered.contains("perhaps you forgot a comma") {
            return Parts(title: "A comma might be missing", what: "Python found two things side by side with nothing between them.", tip: "Put a comma between items, like print(\"Score:\", 5) or [1, 2, 3].")
        }
        if lowered.contains("invalid decimal literal") {
            return Parts(title: "Names can't start with a number", what: "A number is stuck to letters, like 2cats.", tip: "Variable names must start with a letter or _. Try cats2 instead.")
        }
        if lowered.contains("expected 'except' or 'finally'") {
            return Parts(title: "try needs an except", what: "A try: block must be followed by an except: block.", tip: "Add except ValueError: (or another error name) under the try block.")
        }
        if lowered.contains("incomplete input") || lowered.contains("unexpected eof") {
            return Parts(title: "The code stops too early", what: "Python reached the end before something was finished.", tip: "Check for a missing ), ], }, or a quote at the end.")
        }
        if let lineText, lineText.trimmingCharacters(in: .whitespaces).hasPrefix("else if") {
            return Parts(title: title, what: "Python spells it elif, not else if.", tip: "Write elif score > 5: instead of else if score > 5:")
        }
        return Parts(title: title, what: "Something on that line doesn't follow Python's spelling rules.", tip: "Check quotes, brackets, colons, and commas. Compare it with the example.")
    }

    private static func indentation(_ raw: String) -> Parts {
        let lowered = raw.lowercased()
        if lowered.contains("expected an indented block") {
            let after = firstMatch(#"after '([a-z]+)' statement"#, in: raw)
            let what = after.map { "The lines under your \($0) need to be pushed in." } ?? "The lines under a line ending in a colon need to be pushed in."
            return Parts(title: "Push this line in", what: what, tip: "Add 4 spaces (or press Tab) at the start of each line that belongs inside it.")
        }
        if lowered.contains("unexpected indent") {
            return Parts(title: "This line is pushed in too far", what: "This line starts with spaces, but nothing above it ends with a colon.", tip: "Delete the spaces at the start of the line so it lines up with the line above.")
        }
        if lowered.contains("unindent does not match") {
            return Parts(title: "The spacing doesn't line up", what: "This line's spaces don't match any line above it.", tip: "Lines in the same block need exactly the same number of spaces. Use 4 spaces each level.")
        }
        return Parts(title: "The spacing is off", what: "Python uses spaces at the start of a line to know what belongs inside if, for, while, and def.", tip: "Use 4 spaces for each level, and don't mix tabs and spaces.")
    }

    private static func name(_ raw: String, type: String) -> Parts {
        if type == "UnboundLocalError" || raw.contains("cannot access local variable") {
            let variable = firstMatch(#"local variable '([^']+)'"#, in: raw) ?? "a variable"
            return Parts(title: "Used before it was set", what: "Inside a function, \(variable) was used before it got a value.", tip: "Give it a value first inside the function, or pass it in as a parameter.")
        }
        let title = "Python doesn't know that name"
        guard let found = firstMatch(#"name '([^']+)' is not defined"#, in: raw) else {
            return Parts(title: title, what: "Python found a word it doesn't know.", tip: "Check the spelling, and make the variable before you use it.")
        }
        if let suggestion = firstMatch(#"Did you mean: '([^']+)'"#, in: raw) {
            return Parts(title: title, what: "Python doesn't know \(found). Did you mean \(suggestion)?", tip: "Names must be spelled the same way every time, including capitals.")
        }
        if found.lowercased() == "print" || ["prnt", "prin", "pint", "pirnt", "prit", "printt"].contains(found.lowercased()) {
            return Parts(title: title, what: "Python doesn't know \(found). The command is print, all lowercase.", tip: "Python is picky about spelling and capital letters.")
        }
        if ["true", "false", "none"].contains(found.lowercased()) {
            let proper = found.prefix(1).uppercased() + found.dropFirst().lowercased()
            return Parts(title: title, what: "Python doesn't know \(found). It's spelled \(proper), with a capital letter.", tip: "True, False, and None always start with a capital.")
        }
        return Parts(
            title: title,
            what: "Python doesn't know \(found). Either it's spelled differently somewhere, it's used before it's made, or it's text that needs quotes.",
            tip: "If \(found) is a variable, make it first, like \(found) = 5. If it's words, put quotes around it, like \"\(found)\"."
        )
    }

    private static func typeError(_ raw: String) -> Parts {
        let lowered = raw.lowercased()
        let title = "Those don't mix"
        if lowered.contains("can only concatenate str") || (lowered.contains("unsupported operand") && lowered.contains("'str'") && lowered.contains("'int'")) {
            return Parts(title: "Text and a number don't add", what: "You tried to join text and a number with +.", tip: "Turn the number into text with str(), like \"Age: \" + str(age), or use an f-string. If the text came from input(), turn it into a number with int().")
        }
        if lowered.contains("can only concatenate list") {
            return Parts(title: title, what: "You can only add a list to another list.", tip: "To put one item in a list, use .append(item).")
        }
        if lowered.contains("not supported between instances") {
            return Parts(title: "Can't compare those", what: "You compared text with a number, like \"5\" < 3.", tip: "input() always gives text. Wrap it with int() before comparing, like int(input()).")
        }
        if lowered.contains("can't multiply sequence by non-int") {
            return Parts(title: title, what: "You multiplied text by something that isn't a whole number.", tip: "If the number came from input(), wrap it with int() first.")
        }
        if lowered.contains("unsupported operand") {
            return Parts(title: title, what: "Those two values can't use that math symbol together.", tip: "Check that both sides are numbers. Text from input() needs int() first.")
        }
        if lowered.contains("not subscriptable") {
            let kind = firstMatch(#"'([A-Za-z]+)' object is not subscriptable"#, in: raw) ?? "value"
            return Parts(title: "Square brackets don't work here", what: "You used [ ] on \(article(kind)) \(friendlyType(kind)), but only lists, text, and dictionaries can be indexed.", tip: "Check which variable is in front of the [ ].")
        }
        if lowered.contains("does not support item assignment") {
            return Parts(title: "That can't be changed in place", what: "Text and tuples can't be changed one item at a time.", tip: "Make a new string instead, for example with .replace().")
        }
        if lowered.contains("missing") && lowered.contains("required positional argument") {
            let fn = firstMatch(#"^([A-Za-z_][A-Za-z_0-9.]*)\(\)"#, in: raw) ?? "the function"
            return Parts(title: "The function needs more values", what: "\(fn) needs more values inside its ( ) than you gave it.", tip: "Look at the def line. Give one value for each name in its parentheses.")
        }
        if lowered.contains("positional argument") && lowered.contains("were given") {
            let fn = firstMatch(#"^([A-Za-z_][A-Za-z_0-9.]*)\(\)"#, in: raw) ?? "the function"
            return Parts(title: "Too many values", what: "You gave \(fn) more values than it takes.", tip: "Look at the def line and match the number of values. In a class, remember self as the first parameter.")
        }
        if lowered.contains("not callable") {
            return Parts(title: "That isn't a function", what: "Python tried to call something with ( ) that isn't a function.", tip: "Did you name a variable the same as a function, like print = 5 or len = 3? Pick a different name.")
        }
        if lowered.contains("has no len()") {
            return Parts(title: "That has no length", what: "len() works on text, lists, and dictionaries, not on numbers.", tip: "To count digits, turn the number into text first: len(str(number)).")
        }
        if lowered.contains("is not iterable") {
            return Parts(title: "Can't loop over that", what: "A for loop needs a list, text, or range() to walk through.", tip: "To repeat a number of times, use for i in range(count):")
        }
        if lowered.contains("indices must be integers") {
            return Parts(title: "List positions are numbers", what: "A list position must be a whole number, like items[0].", tip: "If it came from input(), wrap it with int().")
        }
        if lowered.contains("nonetype") {
            return Parts(title: "Something was None", what: "A value was None, which means \"nothing\". Often a function printed instead of returning.", tip: "Make sure the function has a return line.")
        }
        return Parts(title: title, what: "A value was a different type than Python expected.", tip: "Check whether each value is text, a whole number, or a list.")
    }

    private static func index(_ raw: String) -> Parts {
        let lowered = raw.lowercased()
        if lowered.contains("pop from empty") {
            return Parts(title: "The list is empty", what: "You tried to take an item out of a list with nothing in it.", tip: "Check the list has items first, like: if items:")
        }
        let thing = lowered.contains("string") ? "text" : "list"
        return Parts(
            title: "That spot doesn't exist",
            what: "You asked for a position past the end of the \(thing).",
            tip: "Positions start at 0, so a \(thing) with 3 items has positions 0, 1, and 2. The last one is [-1]."
        )
    }

    private static func value(_ raw: String) -> Parts {
        let lowered = raw.lowercased()
        if lowered.contains("invalid literal for int()") {
            let bad = firstMatch(#"base 10: (.*)$"#, in: raw) ?? "that"
            return Parts(title: "That isn't a whole number", what: "int() can only turn digits into a number, but it got \(bad).", tip: "Type digits only, like 12. To accept bad answers safely, use try and except ValueError.")
        }
        if lowered.contains("could not convert string to float") {
            return Parts(title: "That isn't a number", what: "float() needs text that looks like a number, like 2.5.", tip: "Check what was typed. Words and empty answers can't become numbers.")
        }
        if lowered.contains("too many values to unpack") || lowered.contains("not enough values to unpack") {
            return Parts(title: "The counts don't match", what: "The number of names on the left doesn't match the number of values on the right.", tip: "a, b = (1, 2) works because there are two names and two values.")
        }
        if lowered.contains("not in list") {
            return Parts(title: "Not in the list", what: "You looked for or removed an item the list doesn't have.", tip: "Check first with: if item in my_list:")
        }
        if lowered.contains("substring not found") {
            return Parts(title: "Text not found", what: "The text you searched for isn't there.", tip: "Use .find(), which gives -1 instead of an error, or check with in first.")
        }
        return Parts(title: "That value doesn't fit", what: "The value was the right type, but not a value Python could use there.", tip: "Read the line and check what the value really is. print() it to see.")
    }

    private static func attribute(_ raw: String) -> Parts {
        let kind = firstMatch(#"'([A-Za-z_]+)' object has no attribute"#, in: raw)
        let attr = firstMatch(#"has no attribute '([^']+)'"#, in: raw)
        let suggestion = firstMatch(#"Did you mean: '([^']+)'"#, in: raw)
        if kind == "NoneType" {
            return Parts(title: "Something was None", what: "You used a dot on None, which means \"nothing\".", tip: "A function without return gives None. Add a return line.")
        }
        if let kind, let attr {
            var what = "\(article(kind).capitalized) \(friendlyType(kind)) doesn't have a tool called .\(attr)."
            if let suggestion {
                what += " Did you mean .\(suggestion)?"
            }
            var tip = "Check the spelling after the dot."
            if kind == "list" && (attr == "push" || attr == "add") { tip = "Lists use .append(item) to add to the end." }
            if kind == "str" && attr == "append" { tip = "Text can't append. Join text with + instead." }
            if kind == "dict" && attr == "append" { tip = "Dictionaries add with my_dict[key] = value." }
            if kind == "int" { tip = "That variable holds a number. Check that it's the variable you meant." }
            return Parts(title: "No tool with that name", what: what, tip: tip)
        }
        return Parts(title: "No tool with that name", what: "That value doesn't have what comes after the dot.", tip: "Check the spelling after the dot.")
    }

    // MARK: - Helpers

    private static func friendlyType(_ kind: String) -> String {
        switch kind {
        case "str": return "text (str)"
        case "int": return "whole number (int)"
        case "float": return "decimal number (float)"
        case "list": return "list"
        case "dict": return "dictionary"
        case "tuple": return "tuple"
        case "set": return "set"
        case "bool": return "True or False value"
        case "NoneType": return "None"
        default: return kind
        }
    }

    private static func article(_ kind: String) -> String {
        switch kind {
        case "int", "str", "float", "list", "dict", "tuple", "set", "bool": return "a"
        default: return "a"
        }
    }

    private static func closing(_ symbol: String) -> String {
        switch symbol {
        case "[": return "]"
        case "{": return "}"
        default: return ")"
        }
    }

    /// The learner's line number: the last place in the traceback that is their code.
    static func lineNumber(in text: String?) -> Int? {
        guard let text else { return nil }
        if let value = lastMatch(#"File "<your code>", line (\d+)"#, in: text), let line = Int(value) {
            return line
        }
        if let value = lastMatch(#"\(<your code>, line (\d+)\)"#, in: text), let line = Int(value) {
            return line
        }
        return nil
    }

    static func codeLine(_ number: Int, in source: String?) -> String? {
        guard let source, number >= 1 else { return nil }
        let lines = source.components(separatedBy: "\n")
        guard number <= lines.count else { return nil }
        let text = lines[number - 1].trimmingCharacters(in: .whitespaces)
        return text.isEmpty ? nil : text
    }

    private static func firstMatch(_ pattern: String, in text: String) -> String? {
        matches(pattern, in: text).first
    }

    private static func lastMatch(_ pattern: String, in text: String) -> String? {
        matches(pattern, in: text).last
    }

    private static func matches(_ pattern: String, in text: String) -> [String] {
        guard let regex = try? NSRegularExpression(pattern: pattern, options: [.anchorsMatchLines]) else { return [] }
        let range = NSRange(text.startIndex..<text.endIndex, in: text)
        return regex.matches(in: text, range: range).compactMap { match in
            guard match.numberOfRanges > 1, let capture = Range(match.range(at: 1), in: text) else { return nil }
            return String(text[capture])
        }
    }
}
