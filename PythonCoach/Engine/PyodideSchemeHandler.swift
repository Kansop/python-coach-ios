import Foundation
import WebKit

final class PyodideSchemeHandler: NSObject, WKURLSchemeHandler {
    let cacheDirectory: URL
    private let lock = NSLock()
    private var stopped = Set<ObjectIdentifier>()
    private lazy var runnerHTML = BridgeScripts.runnerHTML
    private lazy var workerScript = BridgeScripts.workerJavaScript()
    private lazy var harness = PythonHarness.source

    init(cacheDirectory: URL) {
        self.cacheDirectory = cacheDirectory
    }

    func webView(_ webView: WKWebView, start urlSchemeTask: WKURLSchemeTask) {
        let id = ObjectIdentifier(urlSchemeTask)
        guard let url = urlSchemeTask.request.url, let resolved = PyodidePaths.resolve(url) else {
            respond(urlSchemeTask, url: urlSchemeTask.request.url, status: 404, mime: "text/plain", body: Data("Not found".utf8), id: id, contentRange: nil)
            return
        }
        let body: Data
        switch resolved.kind {
        case .runner:
            body = Data(runnerHTML.utf8)
        case .worker:
            body = Data(workerScript.utf8)
        case .harness:
            body = Data(harness.utf8)
        case .runtime(let name):
            let file = PyodideCache.fileURL(in: cacheDirectory, name: name)
            guard let data = try? Data(contentsOf: file) else {
                respond(urlSchemeTask, url: url, status: 404, mime: resolved.mime, body: Data(), id: id, contentRange: nil)
                return
            }
            body = data
        }
        if let header = urlSchemeTask.request.value(forHTTPHeaderField: "Range"),
           let range = ByteRanges.parse(header, length: body.count),
           range.lowerBound >= 0, range.upperBound <= body.count {
            let slice = body.subdata(in: range)
            let contentRange = "bytes \(range.lowerBound)-\(range.upperBound - 1)/\(body.count)"
            respond(urlSchemeTask, url: url, status: 206, mime: resolved.mime, body: slice, id: id, contentRange: contentRange)
        } else {
            respond(urlSchemeTask, url: url, status: 200, mime: resolved.mime, body: body, id: id, contentRange: nil)
        }
    }

    func webView(_ webView: WKWebView, stop urlSchemeTask: WKURLSchemeTask) {
        lock.lock()
        stopped.insert(ObjectIdentifier(urlSchemeTask))
        lock.unlock()
    }

    private func respond(
        _ task: WKURLSchemeTask,
        url: URL?,
        status: Int,
        mime: String,
        body: Data,
        id: ObjectIdentifier,
        contentRange: String?
    ) {
        if isStopped(id) { return }
        guard let url else { return }
        var headers = [
            "Content-Type": mime,
            "Content-Length": String(body.count),
            "Accept-Ranges": "bytes",
            "Cache-Control": "no-store",
            "Access-Control-Allow-Origin": "*",
            "Cross-Origin-Resource-Policy": "cross-origin"
        ]
        if let contentRange {
            headers["Content-Range"] = contentRange
        }
        guard let response = HTTPURLResponse(url: url, statusCode: status, httpVersion: "HTTP/1.1", headerFields: headers) else {
            return
        }
        if isStopped(id) { return }
        task.didReceive(response)
        if isStopped(id) { return }
        task.didReceive(body)
        if isStopped(id) { return }
        task.didFinish()
        lock.lock()
        stopped.remove(id)
        lock.unlock()
    }

    private func isStopped(_ id: ObjectIdentifier) -> Bool {
        lock.lock()
        defer { lock.unlock() }
        return stopped.contains(id)
    }
}
