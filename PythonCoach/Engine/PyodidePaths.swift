import Foundation

enum ByteRanges {
    static func parse(_ header: String, length: Int) -> Range<Int>? {
        guard length > 0 else { return nil }
        let trimmed = header.trimmingCharacters(in: .whitespaces)
        guard trimmed.lowercased().hasPrefix("bytes=") else { return nil }
        let spec = trimmed.dropFirst(6)
        if spec.contains(",") { return nil }
        let parts = spec.split(separator: "-", maxSplits: 1, omittingEmptySubsequences: false)
        guard parts.count == 2 else { return nil }
        if parts[0].isEmpty {
            guard let suffix = Int(parts[1]), suffix > 0 else { return nil }
            let start = max(0, length - suffix)
            return start..<length
        }
        guard let start = Int(parts[0]), start >= 0, start < length else { return nil }
        if parts[1].isEmpty {
            return start..<length
        }
        guard let endInclusive = Int(parts[1]), endInclusive >= start else { return nil }
        let end = min(length - 1, endInclusive)
        return start..<(end + 1)
    }
}

enum PyodidePaths {
    enum Kind: Equatable {
        case runner
        case worker
        case harness
        case runtime(String)
    }

    struct Resolved: Equatable {
        var kind: Kind
        var mime: String
    }

    static func resolve(_ url: URL) -> Resolved? {
        guard url.scheme?.lowercased() == "pycoach" else { return nil }
        let rawPath = url.path
        if rawPath.contains("..") { return nil }
        var path = rawPath
        if path.hasPrefix("/") { path.removeFirst() }
        switch path {
        case "runner.html":
            return Resolved(kind: .runner, mime: "text/html; charset=utf-8")
        case "worker.js":
            return Resolved(kind: .worker, mime: "text/javascript; charset=utf-8")
        case "harness.py":
            return Resolved(kind: .harness, mime: "text/plain; charset=utf-8")
        default:
            break
        }
        let prefix = "pyodide/"
        guard path.hasPrefix(prefix) else { return nil }
        let name = String(path.dropFirst(prefix.count))
        guard isSafeFileName(name), PyodideCache.fileNames.contains(name) else { return nil }
        return Resolved(kind: .runtime(name), mime: mime(for: name))
    }

    static func isSafeFileName(_ name: String) -> Bool {
        guard !name.isEmpty, !name.contains("/"), !name.contains("\\") else { return false }
        return name.range(of: #"^[A-Za-z0-9._-]+$"#, options: .regularExpression) != nil
    }

    static func mime(for name: String) -> String {
        switch (name as NSString).pathExtension.lowercased() {
        case "js", "mjs":
            return "text/javascript; charset=utf-8"
        case "wasm":
            return "application/wasm"
        case "json":
            return "application/json"
        case "zip":
            return "application/zip"
        default:
            return "application/octet-stream"
        }
    }
}
