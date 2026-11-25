import Combine
import Foundation
@preconcurrency import WebKit

enum EnginePhase: Equatable {
    case idle
    case booting
    case ready
    case running
    case restarting
    case failed
}

struct InputRequest: Identifiable, Equatable {
    let id = UUID()
    var prompt: String
}

private struct RunPayload: Encodable {
    var code: String
    var stdin: [String]
    var append: String
    var names: [String]
    var interactive: Bool
}

private struct BridgeEnvelope: Decodable {
    var type: String
    var id: Int?
    var message: String?
    var ok: Bool?
    var stdout: String?
    var stderr: String?
    var errorType: String?
    var errorMessage: String?
    var traceback: String?
    var values: [String: String]?
    var needsInput: Bool?
    var inputPrompt: String?
    var timedOut: Bool?
    var hardReset: Bool?

    func asRun() -> CapturedRun {
        CapturedRun(
            stdout: stdout ?? "",
            stderr: stderr ?? "",
            values: values ?? [:],
            errorType: errorType,
            errorMessage: errorMessage,
            traceback: traceback,
            needsInput: needsInput ?? false,
            inputPrompt: inputPrompt ?? "",
            timedOut: timedOut ?? false,
            cancelled: false
        )
    }
}

@MainActor
final class PythonEngine: NSObject, ObservableObject {
    @Published private(set) var phase: EnginePhase = .idle
    @Published private(set) var inputRequest: InputRequest?
    @Published private(set) var failureMessage = ""
    @Published private(set) var failureDetail = ""
    @Published private(set) var webViewGeneration = 0

    private(set) var webView: WKWebView?
    private var cacheDirectory: URL?
    private var bootToken = 0
    private var waiterToken = 0
    private var waiter: CheckedContinuation<CapturedRun, Never>?
    private var inputContinuation: CheckedContinuation<String?, Never>?
    private var runInFlight = false
    private var bootTimer: DispatchWorkItem?
    private var runTimer: DispatchWorkItem?

    func start(cacheDirectory: URL) {
        self.cacheDirectory = cacheDirectory
        guard phase == .idle || phase == .failed else { return }
        boot()
    }

    func restart() {
        boot()
    }

    func run(code: String, stdin: [String], append: String, names: [String], interactive: Bool) async -> CapturedRun {
        guard phase == .ready || phase == .running else {
            return .failure(type: "RuntimeError", message: "Python is still starting. Try again in a moment.")
        }
        if runInFlight {
            return .failure(type: "RuntimeError", message: "Python is already running.")
        }
        runInFlight = true
        phase = .running
        var answers = stdin
        var result = CapturedRun.failure(type: "RuntimeError", message: "Python did not answer.")
        while true {
            result = await executeSlice(code: code, stdin: answers, append: append, names: names, interactive: interactive)
            if result.cancelled { break }
            if result.needsInput && interactive {
                let answer = await waitForInput(prompt: result.inputPrompt)
                guard let answer else {
                    result = .cancelledRun(stdout: result.stdout, prompt: result.inputPrompt)
                    break
                }
                answers.append(answer)
                continue
            }
            break
        }
        runInFlight = false
        if phase == .running {
            phase = .ready
        }
        return result
    }

    func finishInput(_ value: String?) {
        inputRequest = nil
        guard let continuation = inputContinuation else { return }
        inputContinuation = nil
        continuation.resume(returning: value)
    }

    func receive(_ body: String, token: Int) {
        guard token == bootToken else { return }
        guard let data = body.data(using: .utf8),
              let envelope = try? JSONDecoder().decode(BridgeEnvelope.self, from: data) else {
            return
        }
        switch envelope.type {
        case "ready":
            bootTimer?.cancel()
            failureMessage = ""
            failureDetail = ""
            if waiter == nil {
                phase = .ready
            }
        case "boot-error":
            bootTimer?.cancel()
            phase = .failed
            failureMessage = "Python didn't start."
            failureDetail = envelope.message ?? ""
            finishWaiting(with: .failure(type: "RuntimeError", message: "Python didn't start."))
        case "result":
            if envelope.hardReset == true {
                phase = .restarting
            }
            finishWaiting(with: envelope.asRun())
        default:
            break
        }
    }

    func failBoot(_ message: String) {
        guard phase == .booting || phase == .restarting else { return }
        phase = .failed
        failureMessage = "Python didn't start."
        failureDetail = message
    }

    private func boot() {
        guard let cacheDirectory else { return }
        bootTimer?.cancel()
        bootToken += 1
        let token = bootToken
        phase = .booting
        failureMessage = ""
        failureDetail = ""

        let handler = PyodideSchemeHandler(cacheDirectory: cacheDirectory)
        let configuration = WKWebViewConfiguration()
        configuration.setURLSchemeHandler(handler, forURLScheme: "pycoach")
        let proxy = ScriptProxy(token: token)
        proxy.engine = self
        configuration.userContentController.add(proxy, name: "pycoach")

        let view = WKWebView(frame: CGRect(x: 0, y: 0, width: 8, height: 8), configuration: configuration)
        view.navigationDelegate = self
        view.uiDelegate = self
        view.isOpaque = false
        view.backgroundColor = .clear
        view.scrollView.isScrollEnabled = false
        #if DEBUG
        view.isInspectable = true
        #endif
        webView = view
        webViewGeneration += 1
        // Load on the next turn so SwiftUI can put the web view in the window first.
        // A zero-size or not-yet-attached WKWebView can stall JavaScript.
        if let url = URL(string: "pycoach://local/runner.html") {
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.2) { [weak self, weak view] in
                Task { @MainActor in
                    guard let self, self.bootToken == token else { return }
                    view?.load(URLRequest(url: url))
                }
            }
        }
        armBootTimer(token: token)
    }

    private func executeSlice(
        code: String,
        stdin: [String],
        append: String,
        names: [String],
        interactive: Bool
    ) async -> CapturedRun {
        guard let webView else {
            return .failure(type: "RuntimeError", message: "Python is not ready yet.")
        }
        waiterToken += 1
        let token = waiterToken
        let payload = RunPayload(code: code, stdin: stdin, append: append, names: names, interactive: interactive)
        guard let data = try? JSONEncoder().encode(payload) else {
            return .failure(type: "RuntimeError", message: "Could not prepare this program.")
        }
        let script = "window.pycoachRun && window.pycoachRun(JSON.parse(atob('\(data.base64EncodedString())')))"
        return await withCheckedContinuation { continuation in
            self.waiter = continuation
            self.armRunTimer(token: token)
            webView.evaluateJavaScript(script) { _, error in
                guard let error else { return }
                Task { @MainActor in
                    self.finishWaiting(
                        token: token,
                        run: .failure(type: "RuntimeError", message: "Could not talk to Python. \(error.localizedDescription)")
                    )
                }
            }
        }
    }

    private func waitForInput(prompt: String) async -> String? {
        inputRequest = InputRequest(prompt: prompt.isEmpty ? "Type an answer" : prompt)
        return await withCheckedContinuation { continuation in
            self.inputContinuation = continuation
        }
    }

    private func finishWaiting(with run: CapturedRun) {
        finishWaiting(token: waiterToken, run: run)
    }

    private func finishWaiting(token: Int, run: CapturedRun) {
        guard token == waiterToken, let continuation = waiter else { return }
        runTimer?.cancel()
        waiter = nil
        continuation.resume(returning: run)
    }

    private func armBootTimer(token: Int) {
        bootTimer?.cancel()
        let item = DispatchWorkItem { [weak self] in
            Task { @MainActor in
                guard let self, self.bootToken == token else { return }
                guard self.phase == .booting || self.phase == .restarting else { return }
                self.phase = .failed
                self.failureMessage = "Python took too long to start."
                self.failureDetail = "Try again. If it keeps happening, redownload Python in Settings."
            }
        }
        bootTimer = item
        DispatchQueue.main.asyncAfter(deadline: .now() + 40, execute: item)
    }

    private func armRunTimer(token: Int) {
        runTimer?.cancel()
        let item = DispatchWorkItem { [weak self] in
            Task { @MainActor in
                guard let self, self.waiterToken == token, self.waiter != nil else { return }
                self.forceRestart()
            }
        }
        runTimer = item
        DispatchQueue.main.asyncAfter(deadline: .now() + 8, execute: item)
    }

    private func forceRestart() {
        runTimer?.cancel()
        let continuation = waiter
        waiter = nil
        phase = .booting
        continuation?.resume(returning: .failure(type: "TimeoutError", message: "timeout", timedOut: true))
        boot()
    }
}

extension PythonEngine: WKNavigationDelegate, WKUIDelegate {
    nonisolated func webView(_ webView: WKWebView, didFail navigation: WKNavigation!, withError error: Error) {
        reportNavigationFailure(error)
    }

    nonisolated func webView(_ webView: WKWebView, didFailProvisionalNavigation navigation: WKNavigation!, withError error: Error) {
        reportNavigationFailure(error)
    }

    nonisolated func webView(
        _ webView: WKWebView,
        runJavaScriptAlertPanelWithMessage message: String,
        initiatedByFrame frame: WKFrameInfo,
        completionHandler: @escaping () -> Void
    ) {
        completionHandler()
    }

    nonisolated func webView(
        _ webView: WKWebView,
        runJavaScriptConfirmPanelWithMessage message: String,
        initiatedByFrame frame: WKFrameInfo,
        completionHandler: @escaping (Bool) -> Void
    ) {
        completionHandler(true)
    }

    nonisolated func webView(
        _ webView: WKWebView,
        runJavaScriptTextInputPanelWithPrompt prompt: String,
        defaultText: String?,
        initiatedByFrame frame: WKFrameInfo,
        completionHandler: @escaping (String?) -> Void
    ) {
        completionHandler(defaultText)
    }

    private nonisolated func reportNavigationFailure(_ error: Error) {
        let nsError = error as NSError
        if nsError.domain == NSURLErrorDomain && nsError.code == NSURLErrorCancelled { return }
        let text = error.localizedDescription
        Task { @MainActor in
            self.failBoot(text)
        }
    }
}

private final class ScriptProxy: NSObject, WKScriptMessageHandler {
    nonisolated(unsafe) weak var engine: PythonEngine?
    let token: Int

    init(token: Int) {
        self.token = token
    }

    func userContentController(_ userContentController: WKUserContentController, didReceive message: WKScriptMessage) {
        let body = message.body as? String ?? ""
        let token = self.token
        Task { @MainActor [weak self] in
            self?.engine?.receive(body, token: token)
        }
    }
}
