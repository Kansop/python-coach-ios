import SwiftUI
import UIKit

struct EditorPalette: Equatable {
    var background: UIColor
    var plain: UIColor
    var keyword: UIColor
    var builtin: UIColor
    var string: UIColor
    var comment: UIColor
    var number: UIColor
    var cursor: UIColor
    var isDark: Bool

    static func forScheme(_ scheme: ColorScheme) -> EditorPalette {
        if scheme == .dark {
            return EditorPalette(
                background: UIColor(red: 0.07, green: 0.10, blue: 0.15, alpha: 1),
                plain: UIColor(red: 0.90, green: 0.93, blue: 0.97, alpha: 1),
                keyword: UIColor(red: 0.77, green: 0.71, blue: 0.99, alpha: 1),
                builtin: UIColor(red: 0.49, green: 0.83, blue: 0.99, alpha: 1),
                string: UIColor(red: 0.53, green: 0.94, blue: 0.67, alpha: 1),
                comment: UIColor(red: 0.55, green: 0.62, blue: 0.70, alpha: 1),
                number: UIColor(red: 0.99, green: 0.73, blue: 0.45, alpha: 1),
                cursor: UIColor(red: 0.55, green: 0.70, blue: 1, alpha: 1),
                isDark: true
            )
        }
        return EditorPalette(
            background: UIColor(red: 0.97, green: 0.98, blue: 0.99, alpha: 1),
            plain: UIColor(red: 0.11, green: 0.14, blue: 0.19, alpha: 1),
            keyword: UIColor(red: 0.36, green: 0.29, blue: 0.86, alpha: 1),
            builtin: UIColor(red: 0.02, green: 0.41, blue: 0.63, alpha: 1),
            string: UIColor(red: 0.02, green: 0.47, blue: 0.34, alpha: 1),
            comment: UIColor(red: 0.42, green: 0.45, blue: 0.50, alpha: 1),
            number: UIColor(red: 0.76, green: 0.25, blue: 0.05, alpha: 1),
            cursor: UIColor(red: 0.23, green: 0.38, blue: 0.93, alpha: 1),
            isDark: false
        )
    }

    func color(for kind: TokenKind?) -> UIColor {
        switch kind {
        case .keyword: return keyword
        case .builtin: return builtin
        case .string: return string
        case .comment: return comment
        case .number: return number
        case nil: return plain
        }
    }
}

struct HighlightedCode: View {
    var code: String
    @Environment(\.colorScheme) private var scheme

    var body: some View {
        Text(attributed)
            .frame(maxWidth: .infinity, alignment: .leading)
            .padding(14)
            .background(AppTheme.editorBackground)
            .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
            .overlay(
                RoundedRectangle(cornerRadius: 16, style: .continuous)
                    .stroke(AppTheme.line, lineWidth: 1)
            )
            .textSelection(.enabled)
    }

    private var attributed: AttributedString {
        let palette = EditorPalette.forScheme(scheme)
        let tokens = SyntaxHighlighter.tokens(in: code)
        var result = AttributedString()
        var cursor = code.startIndex

        func append(_ text: String, kind: TokenKind?) {
            guard !text.isEmpty else { return }
            var part = AttributedString(text)
            part.font = .system(size: 16, weight: kind == .keyword ? .semibold : .regular, design: .monospaced)
            part.foregroundColor = Color(uiColor: palette.color(for: kind))
            result += part
        }

        for token in tokens {
            if cursor < token.range.lowerBound {
                append(String(code[cursor..<token.range.lowerBound]), kind: nil)
            }
            append(String(code[token.range]), kind: token.kind)
            cursor = token.range.upperBound
        }
        if cursor < code.endIndex {
            append(String(code[cursor..<code.endIndex]), kind: nil)
        }
        if result.characters.isEmpty {
            append(" ", kind: nil)
        }
        return result
    }
}

struct CodeEditor: UIViewRepresentable {
    @Binding var text: String
    var palette: EditorPalette

    func makeCoordinator() -> Coordinator {
        Coordinator(text: $text, palette: palette)
    }

    func makeUIView(context: Context) -> UITextView {
        let textView = UITextView()
        textView.delegate = context.coordinator
        textView.backgroundColor = palette.background
        textView.tintColor = palette.cursor
        textView.font = UIFont.monospacedSystemFont(ofSize: 16, weight: .regular)
        textView.textColor = palette.plain
        textView.autocorrectionType = .no
        textView.autocapitalizationType = .none
        textView.smartDashesType = .no
        textView.smartQuotesType = .no
        textView.smartInsertDeleteType = .no
        textView.spellCheckingType = .no
        textView.keyboardType = .asciiCapable
        textView.keyboardAppearance = palette.isDark ? .dark : .light
        textView.alwaysBounceVertical = true
        textView.textContainerInset = UIEdgeInsets(top: 12, left: 10, bottom: 12, right: 10)
        textView.textContainer.lineBreakMode = .byCharWrapping
        textView.textContainer.widthTracksTextView = true
        textView.accessibilityLabel = "Python code editor"
        textView.inputAccessoryView = context.coordinator.makeAccessory(isDark: palette.isDark)
        context.coordinator.textView = textView
        context.coordinator.apply(text, to: textView, restore: nil)
        return textView
    }

    func updateUIView(_ textView: UITextView, context: Context) {
        context.coordinator.parentText = $text
        let paletteChanged = context.coordinator.palette != palette
        context.coordinator.palette = palette
        textView.backgroundColor = palette.background
        textView.tintColor = palette.cursor
        textView.keyboardAppearance = palette.isDark ? .dark : .light
        textView.overrideUserInterfaceStyle = palette.isDark ? .dark : .light
        textView.inputAccessoryView?.overrideUserInterfaceStyle = palette.isDark ? .dark : .light
        if textView.text != text || paletteChanged {
            let selection = textView.selectedRange
            context.coordinator.apply(text, to: textView, restore: selection)
        }
    }

    final class Coordinator: NSObject, UITextViewDelegate {
        var parentText: Binding<String>
        var palette: EditorPalette
        weak var textView: UITextView?

        init(text: Binding<String>, palette: EditorPalette) {
            self.parentText = text
            self.palette = palette
        }

        func textViewDidChange(_ textView: UITextView) {
            let selection = textView.selectedRange
            let updated = textView.text ?? ""
            parentText.wrappedValue = updated
            apply(updated, to: textView, restore: selection)
        }

        func apply(_ text: String, to textView: UITextView, restore: NSRange?) {
            let attributed = NSMutableAttributedString(string: text)
            let full = NSRange(location: 0, length: (text as NSString).length)
            let font = UIFont.monospacedSystemFont(ofSize: 16, weight: .regular)
            let keywordFont = UIFont.monospacedSystemFont(ofSize: 16, weight: .semibold)
            attributed.addAttribute(.font, value: font, range: full)
            attributed.addAttribute(.foregroundColor, value: palette.plain, range: full)
            for token in SyntaxHighlighter.tokens(in: text) {
                let range = NSRange(token.range, in: text)
                guard range.location != NSNotFound, range.location + range.length <= full.length else { continue }
                attributed.addAttribute(.foregroundColor, value: palette.color(for: token.kind), range: range)
                if token.kind == .keyword {
                    attributed.addAttribute(.font, value: keywordFont, range: range)
                }
            }
            textView.attributedText = attributed
            if let restore, restore.location <= (text as NSString).length {
                let maxLocation = (text as NSString).length
                let location = min(restore.location, maxLocation)
                let length = min(restore.length, maxLocation - location)
                textView.selectedRange = NSRange(location: location, length: length)
            }
        }

        func makeAccessory(isDark: Bool) -> UIView {
            let bar = UIView(frame: CGRect(x: 0, y: 0, width: 0, height: 52))
            bar.autoresizingMask = [.flexibleWidth]
            bar.backgroundColor = UIColor.secondarySystemBackground
            bar.overrideUserInterfaceStyle = isDark ? .dark : .light

            let scroll = UIScrollView()
            scroll.translatesAutoresizingMaskIntoConstraints = false
            scroll.showsHorizontalScrollIndicator = false
            scroll.alwaysBounceHorizontal = true
            bar.addSubview(scroll)

            let stack = UIStackView()
            stack.translatesAutoresizingMaskIntoConstraints = false
            stack.axis = .horizontal
            stack.spacing = 8
            stack.alignment = .center
            scroll.addSubview(stack)

            let keys: [(String, String, String)] = [
                (":", ":", "Colon"),
                ("(", "(", "Open parenthesis"),
                (")", ")", "Close parenthesis"),
                ("[", "[", "Open bracket"),
                ("]", "]", "Close bracket"),
                ("\"", "\"", "Double quote"),
                ("'", "'", "Single quote"),
                ("=", "=", "Equals"),
                ("Tab", "    ", "Insert tab")
            ]
            for key in keys {
                var config = UIButton.Configuration.filled()
                config.title = key.0
                config.baseBackgroundColor = UIColor.tertiarySystemFill
                config.baseForegroundColor = UIColor.label
                config.cornerStyle = .medium
                config.contentInsets = NSDirectionalEdgeInsets(top: 8, leading: 12, bottom: 8, trailing: 12)
                config.titleTextAttributesTransformer = UIConfigurationTextAttributesTransformer { incoming in
                    var outgoing = incoming
                    outgoing.font = UIFont.monospacedSystemFont(ofSize: key.0 == "Tab" ? 15 : 18, weight: .semibold)
                    return outgoing
                }
                let button = UIButton(configuration: config)
                button.accessibilityLabel = key.2
                button.addAction(UIAction { [weak self] _ in
                    self?.insert(key.1)
                }, for: .touchUpInside)
                stack.addArrangedSubview(button)
            }

            NSLayoutConstraint.activate([
                scroll.leadingAnchor.constraint(equalTo: bar.leadingAnchor),
                scroll.trailingAnchor.constraint(equalTo: bar.trailingAnchor),
                scroll.topAnchor.constraint(equalTo: bar.topAnchor),
                scroll.bottomAnchor.constraint(equalTo: bar.bottomAnchor),
                stack.leadingAnchor.constraint(equalTo: scroll.contentLayoutGuide.leadingAnchor, constant: 10),
                stack.trailingAnchor.constraint(equalTo: scroll.contentLayoutGuide.trailingAnchor, constant: -10),
                stack.topAnchor.constraint(equalTo: scroll.contentLayoutGuide.topAnchor, constant: 8),
                stack.bottomAnchor.constraint(equalTo: scroll.contentLayoutGuide.bottomAnchor, constant: -8),
                stack.heightAnchor.constraint(equalTo: scroll.frameLayoutGuide.heightAnchor, constant: -16)
            ])
            return bar
        }

        private func insert(_ snippet: String) {
            guard let textView else { return }
            let selection = textView.selectedRange
            let current = textView.text ?? ""
            let ns = current as NSString
            guard selection.location <= ns.length else { return }
            let updated = ns.replacingCharacters(in: selection, with: snippet)
            parentText.wrappedValue = updated
            let caret = selection.location + (snippet as NSString).length
            apply(updated, to: textView, restore: NSRange(location: caret, length: 0))
        }
    }
}
