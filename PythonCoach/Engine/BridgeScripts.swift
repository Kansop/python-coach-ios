import Foundation

enum BridgeScripts {
    static let runnerHTML: String = """
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body>
    <script>
    \(pageScript)
    </script>
    </body>
    </html>
    """

    static func workerJavaScript() -> String {
        // JSONSerialization only accepts arrays and dictionaries at the top level.
        // Wrap the harness, then peel off the surrounding brackets to leave a JS string literal.
        let literal: String
        if let data = try? JSONSerialization.data(withJSONObject: [PythonHarness.source]),
           var text = String(data: data, encoding: .utf8),
           text.first == "[", text.last == "]" {
            text.removeFirst()
            text.removeLast()
            literal = text
        } else {
            literal = "\"\""
        }
        return workerTemplate.replacingOccurrences(of: "__HARNESS_JSON__", with: literal)
    }

    private static let workerTemplate = #"""
    "use strict";
    var pyodide = null;
    var harnessSource = __HARNESS_JSON__;

    function post(obj) {
      self.postMessage(obj);
    }

    function boot() {
      try {
        importScripts("pycoach://local/pyodide/pyodide.js");
      } catch (error) {
        post({ type: "boot-error", message: String(error && (error.stack || error.message) || error) });
        return;
      }
      loadPyodide({
        indexURL: "pycoach://local/pyodide/",
        stdout: function () {},
        stderr: function () {}
      }).then(function (py) {
        pyodide = py;
        py.runPython("import sys, io, json, traceback, time, builtins");
        post({ type: "ready" });
      }).catch(function (error) {
        post({ type: "boot-error", message: String(error && (error.stack || error.message) || error) });
      });
    }

    self.onmessage = function (event) {
      var msg = event.data;
      if (!msg || msg.type !== "run") return;
      if (!pyodide) {
        post({
          type: "result",
          id: msg.id,
          ok: false,
          stdout: "",
          stderr: "",
          errorType: "RuntimeError",
          errorMessage: "Python is not ready yet.",
          traceback: "",
          values: {},
          needsInput: false,
          inputPrompt: "",
          timedOut: false,
          hardReset: false
        });
        return;
      }
      try {
        pyodide.globals.set("_student_code", msg.code || "");
        pyodide.globals.set("_append_code", msg.append || "");
        pyodide.globals.set("_stdin_json", JSON.stringify(msg.stdin || []));
        pyodide.globals.set("_names_json", JSON.stringify(msg.names || []));
        pyodide.globals.set("_interactive", !!msg.interactive);
        pyodide.globals.set("_time_limit", 3);
        pyodide.runPython(harnessSource);
        var raw = pyodide.globals.get("_pycoach_result");
        var text = typeof raw === "string" ? raw : String(raw);
        if (raw && typeof raw.destroy === "function") raw.destroy();
        var result = JSON.parse(text);
        result.type = "result";
        result.id = msg.id;
        result.hardReset = false;
        post(result);
      } catch (error) {
        post({
          type: "result",
          id: msg.id,
          ok: false,
          stdout: "",
          stderr: "",
          errorType: "RuntimeError",
          errorMessage: String(error && (error.message || error)),
          traceback: String(error && (error.stack || error)),
          values: {},
          needsInput: false,
          inputPrompt: "",
          timedOut: false,
          hardReset: false
        });
      }
    };

    boot();
    """#

    private static let pageScript = #"""
    (function () {
      "use strict";
      var worker = null;
      var mode = "starting";
      var booted = false;
      var triedMain = false;
      var pyodide = null;
      var harnessSource = null;
      var activeRun = 0;
      var runTimer = null;
      var bootTimer = null;

      function send(obj) {
        try {
          window.webkit.messageHandlers.pycoach.postMessage(JSON.stringify(obj));
        } catch (error) {}
      }

      function blank(id, extra) {
        var base = {
          type: "result",
          id: id,
          ok: false,
          stdout: "",
          stderr: "",
          errorType: "RuntimeError",
          errorMessage: "Python hit a problem.",
          traceback: "",
          values: {},
          needsInput: false,
          inputPrompt: "",
          timedOut: false,
          hardReset: false
        };
        if (!extra) return base;
        var key;
        for (key in extra) {
          if (Object.prototype.hasOwnProperty.call(extra, key)) base[key] = extra[key];
        }
        return base;
      }

      function clearRunTimer() {
        if (runTimer) {
          clearTimeout(runTimer);
          runTimer = null;
        }
      }

      function clearBootTimer() {
        if (bootTimer) {
          clearTimeout(bootTimer);
          bootTimer = null;
        }
      }

      function armBootTimer() {
        clearBootTimer();
        bootTimer = setTimeout(function () {
          if (!booted) fallbackOrFail("Python took too long to start.");
        }, 35000);
      }

      function onWorkerMessage(event) {
        var msg = event.data || {};
        if (msg.type === "ready") {
          booted = true;
          mode = "worker";
          clearBootTimer();
          send({ type: "ready", mode: "worker" });
          return;
        }
        if (msg.type === "boot-error") {
          clearBootTimer();
          if (!booted) fallbackOrFail(msg.message || "Python failed to start.");
          else send({ type: "boot-error", message: msg.message || "Python failed." });
          return;
        }
        if (msg.type === "result") {
          if (msg.id !== activeRun) return;
          clearRunTimer();
          send(msg);
        }
      }

      function onWorkerError(event) {
        var message = (event && event.message) || "The Python worker could not start.";
        if (!booted) {
          fallbackOrFail(message);
          return;
        }
        if (activeRun) {
          clearRunTimer();
          send(blank(activeRun, { errorMessage: message, hardReset: true }));
        }
        booted = false;
        spawnWorker();
      }

      function spawnWorker() {
        if (worker) {
          worker.onmessage = null;
          worker.onerror = null;
          worker.terminate();
        }
        try {
          worker = new Worker("pycoach://local/worker.js");
        } catch (error) {
          fallbackOrFail(String(error && (error.message || error)));
          return;
        }
        worker.onmessage = onWorkerMessage;
        worker.onerror = onWorkerError;
      }

      function fallbackOrFail(message) {
        if (!triedMain) {
          triedMain = true;
          if (worker) {
            worker.onmessage = null;
            worker.onerror = null;
            worker.terminate();
            worker = null;
          }
          startMain();
          return;
        }
        send({ type: "boot-error", message: message });
      }

      function loadClassic(src) {
        return new Promise(function (resolve, reject) {
          var script = document.createElement("script");
          script.src = src;
          script.onload = function () { resolve(); };
          script.onerror = function () { reject(new Error("Could not load " + src)); };
          document.head.appendChild(script);
        });
      }

      function loadHarness() {
        if (harnessSource) return Promise.resolve(harnessSource);
        return fetch("pycoach://local/harness.py").then(function (response) {
          if (!response.ok) throw new Error("Missing Python harness");
          return response.text();
        }).then(function (text) {
          harnessSource = text;
          return text;
        });
      }

      function execute(py, req) {
        return loadHarness().then(function () {
          py.globals.set("_student_code", req.code || "");
          py.globals.set("_append_code", req.append || "");
          py.globals.set("_stdin_json", JSON.stringify(req.stdin || []));
          py.globals.set("_names_json", JSON.stringify(req.names || []));
          py.globals.set("_interactive", !!req.interactive);
          py.globals.set("_time_limit", 3);
          py.runPython(harnessSource);
          var raw = py.globals.get("_pycoach_result");
          var text = typeof raw === "string" ? raw : String(raw);
          if (raw && typeof raw.destroy === "function") raw.destroy();
          return JSON.parse(text);
        });
      }

      function startMain() {
        mode = "main";
        armBootTimer();
        loadClassic("pycoach://local/pyodide/pyodide.js").then(function () {
          return loadPyodide({ indexURL: "pycoach://local/pyodide/" });
        }).then(function (py) {
          pyodide = py;
          py.runPython("import sys, io, json, traceback, time, builtins");
          return loadHarness();
        }).then(function () {
          booted = true;
          clearBootTimer();
          send({ type: "ready", mode: "main" });
        }).catch(function (error) {
          clearBootTimer();
          send({ type: "boot-error", message: String(error && (error.message || error)) });
        });
      }

      function armHardTimeout(id) {
        clearRunTimer();
        runTimer = setTimeout(function () {
          if (id !== activeRun) return;
          if (worker) worker.terminate();
          send(blank(id, {
            errorType: "TimeoutError",
            errorMessage: "timeout",
            timedOut: true,
            hardReset: true
          }));
          booted = false;
          spawnWorker();
        }, 6000);
      }

      window.pycoachRun = function (req) {
        activeRun += 1;
        var id = activeRun;
        var payload = {
          type: "run",
          id: id,
          code: req.code || "",
          stdin: req.stdin || [],
          append: req.append || "",
          names: req.names || [],
          interactive: !!req.interactive
        };
        if (mode === "worker" && worker && booted) {
          armHardTimeout(id);
          worker.postMessage(payload);
          return;
        }
        if (mode === "main" && pyodide && booted) {
          execute(pyodide, payload).then(function (result) {
            if (id !== activeRun) return;
            result.type = "result";
            result.id = id;
            result.hardReset = false;
            send(result);
          }).catch(function (error) {
            if (id !== activeRun) return;
            send(blank(id, {
              errorMessage: String(error && (error.message || error)),
              traceback: String(error && (error.stack || error))
            }));
          });
          return;
        }
        send(blank(id, { errorMessage: "Python is not ready yet." }));
      };

      window.pycoachKill = function () {
        clearRunTimer();
        activeRun += 1;
        if (worker) worker.terminate();
        if (mode === "worker") {
          booted = false;
          spawnWorker();
        }
      };

      armBootTimer();
      spawnWorker();
    })();
    """#
}
