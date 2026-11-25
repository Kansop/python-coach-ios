import Combine
import Foundation

struct Snippet: Codable, Identifiable, Equatable {
    var id: UUID
    var title: String
    var code: String
    var updated: Date
}

final class PlaygroundLibrary: ObservableObject {
    @Published private(set) var snippets: [Snippet] = []
    private let fileURL: URL

    init(directory: URL) {
        fileURL = directory.appendingPathComponent("snippets.json")
        reload()
    }

    static func live() -> PlaygroundLibrary {
        let base = (try? FileManager.default.url(for: .applicationSupportDirectory, in: .userDomainMask, appropriateFor: nil, create: true))
            ?? FileManager.default.temporaryDirectory
        let folder = base.appendingPathComponent("PythonCoachPlayground", isDirectory: true)
        try? FileManager.default.createDirectory(at: folder, withIntermediateDirectories: true)
        return PlaygroundLibrary(directory: folder)
    }

    func reload() {
        guard let data = try? Data(contentsOf: fileURL),
              let decoded = try? JSONDecoder().decode([Snippet].self, from: data) else {
            snippets = []
            return
        }
        snippets = decoded.sorted { $0.updated > $1.updated }
    }

    func save(title: String, code: String) {
        let trimmed = title.trimmingCharacters(in: .whitespacesAndNewlines)
        let name = trimmed.isEmpty ? "Snippet \(snippets.count + 1)" : trimmed
        let snippet = Snippet(id: UUID(), title: name, code: code, updated: Date())
        snippets.insert(snippet, at: 0)
        persist()
    }

    func delete(_ id: UUID) {
        snippets.removeAll { $0.id == id }
        persist()
    }

    private func persist() {
        let folder = fileURL.deletingLastPathComponent()
        try? FileManager.default.createDirectory(at: folder, withIntermediateDirectories: true)
        if let data = try? JSONEncoder().encode(snippets) {
            try? data.write(to: fileURL, options: .atomic)
        }
    }
}
