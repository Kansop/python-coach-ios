import Combine
import Foundation

enum PyodideDownloadError: LocalizedError {
    case badResponse(Int)
    case damagedFile(String)

    var errorDescription: String? {
        switch self {
        case .badResponse(let code):
            return "The server replied with status \(code)."
        case .damagedFile(let name):
            return "\(name) did not download correctly."
        }
    }
}

enum PyodideCache {
    static let version = "0.26.4"
    static let cdn = URL(string: "https://cdn.jsdelivr.net/pyodide/v0.26.4/full/")!

    struct File: Equatable {
        var name: String
        var minBytes: Int
        var expectedBytes: Int64
        var label: String
    }

    /// Pinned files for Pyodide 0.26.4. This release still runs on the Safari in iOS 17.
    static let files: [File] = [
        File(name: "pyodide.js", minBytes: 5_000, expectedBytes: 14_761, label: "Coach loader"),
        File(name: "pyodide.asm.js", minBytes: 200_000, expectedBytes: 1_229_099, label: "Python starter"),
        File(name: "python_stdlib.zip", minBytes: 500_000, expectedBytes: 2_341_872, label: "Python library"),
        File(name: "pyodide-lock.json", minBytes: 10_000, expectedBytes: 106_335, label: "Package list"),
        File(name: "pyodide.asm.wasm", minBytes: 1_000_000, expectedBytes: 10_088_051, label: "Python engine")
    ]

    static var fileNames: Set<String> { Set(files.map(\.name)) }
    static var totalExpectedBytes: Int64 { files.reduce(0) { $0 + $1.expectedBytes } }

    static func directory() throws -> URL {
        let base = try FileManager.default.url(
            for: .applicationSupportDirectory,
            in: .userDomainMask,
            appropriateFor: nil,
            create: true
        )
        let folder = base.appendingPathComponent("Pyodide/\(version)", isDirectory: true)
        try FileManager.default.createDirectory(at: folder, withIntermediateDirectories: true)
        return folder
    }

    static func fileURL(in directory: URL, name: String) -> URL {
        directory.appendingPathComponent(name)
    }

    static func isReady(_ directory: URL) -> Bool {
        let marker = directory.appendingPathComponent("complete.marker")
        guard let text = try? String(contentsOf: marker, encoding: .utf8),
              text.trimmingCharacters(in: .whitespacesAndNewlines) == version else {
            return false
        }
        return files.allSatisfy { file in
            validate(url: fileURL(in: directory, name: file.name), name: file.name, minBytes: file.minBytes)
        }
    }

    static func markReady(_ directory: URL) throws {
        let marker = directory.appendingPathComponent("complete.marker")
        try Data(version.utf8).write(to: marker, options: .atomic)
    }

    static func remove(_ directory: URL) {
        try? FileManager.default.removeItem(at: directory)
    }

    static func validate(url: URL, name: String, minBytes: Int) -> Bool {
        guard FileManager.default.fileExists(atPath: url.path),
              let attrs = try? FileManager.default.attributesOfItem(atPath: url.path),
              let size = attrs[.size] as? NSNumber,
              size.intValue >= minBytes else {
            return false
        }
        if name.hasSuffix(".wasm") {
            return hasPrefix(url, Data([0x00, 0x61, 0x73, 0x6d]))
        }
        if name.hasSuffix(".zip") {
            return hasPrefix(url, Data([0x50, 0x4b]))
        }
        if name.hasSuffix(".js") {
            guard let data = try? Data(contentsOf: url), let text = String(data: data, encoding: .utf8) else { return false }
            if name == "pyodide.js" {
                return text.contains("loadPyodide")
            }
            return text.contains("WebAssembly") || text.contains("wasm")
        }
        if name.hasSuffix(".json") {
            guard let data = try? Data(contentsOf: url), let text = String(data: data, encoding: .utf8) else { return false }
            return text.trimmingCharacters(in: .whitespacesAndNewlines).hasPrefix("{")
        }
        return true
    }

    private static func hasPrefix(_ url: URL, _ magic: Data) -> Bool {
        guard let handle = try? FileHandle(forReadingFrom: url) else { return false }
        defer { try? handle.close() }
        guard let data = try? handle.read(upToCount: magic.count) else { return false }
        return data.starts(with: magic)
    }
}

struct DownloadProgress: Equatable {
    var completedBytes: Int64 = 0
    var currentBytes: Int64 = 0
    var totalBytes: Int64 = PyodideCache.totalExpectedBytes
    var fileIndex: Int = 0
    var fileCount: Int = PyodideCache.files.count
    var fileLabel: String = ""

    var fraction: Double {
        guard totalBytes > 0 else { return 0 }
        let value = Double(completedBytes + currentBytes) / Double(totalBytes)
        return min(1, max(0, value))
    }

    var percentText: String {
        "\(Int((fraction * 100).rounded()))%"
    }
}

enum RuntimePhase: Equatable {
    case checking
    case downloading
    case ready
    case failed
}

@MainActor
final class RuntimeManager: ObservableObject {
    @Published private(set) var phase: RuntimePhase = .checking
    @Published private(set) var progress = DownloadProgress()
    @Published private(set) var errorMessage = ""
    @Published private(set) var cacheDirectory: URL?

    private var loadTask: Task<Void, Never>?

    func prepare() {
        guard loadTask == nil else { return }
        loadTask = Task { await self.run(repair: false) }
    }

    func retry() {
        loadTask?.cancel()
        loadTask = Task { await self.run(repair: false) }
    }

    func repair() {
        loadTask?.cancel()
        loadTask = Task { await self.run(repair: true) }
    }

    private func run(repair: Bool) async {
        phase = .checking
        errorMessage = ""
        do {
            var directory = try PyodideCache.directory()
            if repair {
                PyodideCache.remove(directory)
                directory = try PyodideCache.directory()
            }
            if PyodideCache.isReady(directory) {
                cacheDirectory = directory
                phase = .ready
                return
            }
            phase = .downloading
            progress = DownloadProgress()
            try await download(into: directory)
            guard PyodideCache.isReady(directory) else {
                throw PyodideDownloadError.damagedFile("Python")
            }
            cacheDirectory = directory
            phase = .ready
        } catch is CancellationError {
            return
        } catch {
            phase = .failed
            errorMessage = Self.friendly(error)
        }
    }

    private func download(into directory: URL) async throws {
        var completed: Int64 = 0
        for (index, file) in PyodideCache.files.enumerated() {
            try Task.checkCancellation()
            let destination = PyodideCache.fileURL(in: directory, name: file.name)
            if PyodideCache.validate(url: destination, name: file.name, minBytes: file.minBytes) {
                completed += file.expectedBytes
                progress = DownloadProgress(
                    completedBytes: completed,
                    currentBytes: 0,
                    totalBytes: PyodideCache.totalExpectedBytes,
                    fileIndex: index,
                    fileCount: PyodideCache.files.count,
                    fileLabel: file.label
                )
                continue
            }
            progress = DownloadProgress(
                completedBytes: completed,
                currentBytes: 0,
                totalBytes: PyodideCache.totalExpectedBytes,
                fileIndex: index,
                fileCount: PyodideCache.files.count,
                fileLabel: file.label
            )
            let remote = PyodideCache.cdn.appendingPathComponent(file.name)
            try await downloadFile(from: remote, to: destination, label: file.label)
            guard PyodideCache.validate(url: destination, name: file.name, minBytes: file.minBytes) else {
                try? FileManager.default.removeItem(at: destination)
                throw PyodideDownloadError.damagedFile(file.label)
            }
            completed += file.expectedBytes
            progress = DownloadProgress(
                completedBytes: completed,
                currentBytes: 0,
                totalBytes: PyodideCache.totalExpectedBytes,
                fileIndex: index,
                fileCount: PyodideCache.files.count,
                fileLabel: file.label
            )
        }
        try PyodideCache.markReady(directory)
    }

    private func downloadFile(from remote: URL, to destination: URL, label: String) async throws {
        let relay = DownloadRelay(destination: destination)
        let configuration = URLSessionConfiguration.ephemeral
        configuration.timeoutIntervalForRequest = 60
        configuration.timeoutIntervalForResource = 300
        configuration.waitsForConnectivity = false
        let session = URLSession(configuration: configuration, delegate: relay, delegateQueue: nil)
        defer { session.finishTasksAndInvalidate() }

        relay.onProgress = { [weak self] written, _ in
            Task { @MainActor in
                guard let self else { return }
                var copy = self.progress
                copy.currentBytes = written
                copy.fileLabel = label
                self.progress = copy
            }
        }

        try await withCheckedThrowingContinuation { (continuation: CheckedContinuation<Void, Error>) in
            relay.onComplete = { result in
                Task { @MainActor in
                    continuation.resume(with: result)
                }
            }
            session.downloadTask(with: remote).resume()
        }
    }

    private static func friendly(_ error: Error) -> String {
        if let urlError = error as? URLError {
            switch urlError.code {
            case .notConnectedToInternet, .networkConnectionLost, .dataNotAllowed, .cannotConnectToHost, .timedOut, .cannotFindHost:
                return "Connect to the internet once so Python Coach can download Python. After that, lessons work offline, even in airplane mode."
            default:
                break
            }
        }
        if let download = error as? PyodideDownloadError, let description = download.errorDescription {
            return description + " Try again."
        }
        return "The download didn't finish. Check your connection and try again."
    }
}

final class DownloadRelay: NSObject, URLSessionDownloadDelegate {
    var onProgress: ((Int64, Int64) -> Void)?
    var onComplete: ((Result<Void, Error>) -> Void)?
    let destination: URL
    private let lock = NSLock()
    private var finished = false

    init(destination: URL) {
        self.destination = destination
    }

    func urlSession(
        _ session: URLSession,
        downloadTask: URLSessionDownloadTask,
        didWriteData bytesWritten: Int64,
        totalBytesWritten: Int64,
        totalBytesExpectedToWrite: Int64
    ) {
        onProgress?(totalBytesWritten, totalBytesExpectedToWrite)
    }

    func urlSession(_ session: URLSession, downloadTask: URLSessionDownloadTask, didFinishDownloadingTo location: URL) {
        let status = (downloadTask.response as? HTTPURLResponse)?.statusCode ?? 0
        do {
            guard (200..<300).contains(status) else {
                throw PyodideDownloadError.badResponse(status)
            }
            let folder = destination.deletingLastPathComponent()
            try FileManager.default.createDirectory(at: folder, withIntermediateDirectories: true)
            if FileManager.default.fileExists(atPath: destination.path) {
                try FileManager.default.removeItem(at: destination)
            }
            try FileManager.default.moveItem(at: location, to: destination)
            complete(.success(()))
        } catch {
            complete(.failure(error))
        }
    }

    func urlSession(_ session: URLSession, task: URLSessionTask, didCompleteWithError error: Error?) {
        if let error {
            complete(.failure(error))
        }
    }

    private func complete(_ result: Result<Void, Error>) {
        lock.lock()
        let callback = onComplete
        let shouldCall = !finished
        finished = true
        lock.unlock()
        guard shouldCall else { return }
        callback?(result)
    }
}
