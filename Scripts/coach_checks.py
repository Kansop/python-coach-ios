"""Shared checking tools for Python Coach lessons.

The same Python harness runs here and inside the app (in Pyodide). `CPythonRunner` runs it in this
process. `PyodideRunner` runs it in the real Pyodide 0.26.4 through Node, which is the Python 3.12
build the iPhone downloads.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLANK = "___"

HARNESS = r"""
import sys, io, json, traceback, time, builtins

try:
    _limit = float(_time_limit)
except NameError:
    _limit = 3.0

class _NeedInput(BaseException):
    def __init__(self, prompt):
        super().__init__("need-input")
        self.prompt = prompt

_namespace = {"__name__": "__main__"}
_out = io.StringIO()
_err = io.StringIO()
_old_out, _old_err = sys.stdout, sys.stderr
_old_input = builtins.input
_old_trace = sys.gettrace()
sys.stdout = _out
sys.stderr = _err
_stdin_lines = json.loads(_stdin_json)
_names = json.loads(_names_json)
_interactive_flag = bool(_interactive)
_it = iter(_stdin_lines)

def _input(prompt=""):
    if prompt is None:
        prompt = ""
    else:
        prompt = str(prompt)
    try:
        value = next(_it)
    except StopIteration:
        if _interactive_flag:
            raise _NeedInput(prompt)
        raise EOFError("This program asked for more input than this exercise provides.")
    sys.stdout.write(prompt)
    sys.stdout.write(str(value))
    sys.stdout.write("\n")
    return str(value)

builtins.input = _input
_namespace["input"] = _input
_start = time.time()

def _trace(frame, event, arg):
    if frame.f_code.co_name == "_trace":
        return None
    filename = frame.f_code.co_filename
    if filename not in ("<your code>", "<check>"):
        return None
    if time.time() - _start > _limit:
        raise TimeoutError("timeout")
    return _trace

sys.settrace(_trace)
_needs_input = False
_input_prompt = ""
_error_type = None
_error_message = None
_tb = None
_timed_out = False
try:
    _compiled = compile(_student_code, "<your code>", "exec")
    exec(_compiled, _namespace)
    if str(_append_code).strip():
        exec(compile(_append_code, "<check>", "exec"), _namespace)
except _NeedInput as exc:
    _needs_input = True
    _input_prompt = exc.prompt
except TimeoutError:
    _timed_out = True
    _error_type = "TimeoutError"
    _error_message = "timeout"
    _tb = traceback.format_exc()
except BaseException as exc:
    _error_type = type(exc).__name__
    _error_message = str(exc)
    _tb = traceback.format_exc()
finally:
    sys.settrace(_old_trace)
    sys.stdout = _old_out
    sys.stderr = _old_err
    builtins.input = _old_input

_values = {}
if (not _needs_input) and (_error_type is None):
    for _name in _names:
        if _name in _namespace:
            try:
                _values[_name] = repr(_namespace[_name])
            except Exception:
                _values[_name] = "<unreadable>"

_pycoach_result = json.dumps({
    "ok": _error_type is None and not _needs_input and not _timed_out,
    "stdout": _out.getvalue(),
    "stderr": _err.getvalue(),
    "errorType": _error_type,
    "errorMessage": _error_message,
    "traceback": _tb,
    "values": _values,
    "needsInput": _needs_input,
    "inputPrompt": _input_prompt,
    "timedOut": _timed_out,
})
"""


def run_code(code, stdin=None, append="", names=None, interactive=False, limit=1.0):
    globals_dict = {
        "_student_code": code,
        "_append_code": append or "",
        "_stdin_json": json.dumps(list(stdin or [])),
        "_names_json": json.dumps(list(names or [])),
        "_interactive": interactive,
        "_time_limit": limit,
        "__name__": "__main__",
    }
    exec(HARNESS, globals_dict)
    return json.loads(globals_dict["_pycoach_result"])



class CPythonRunner:
    name = "CPython " + sys.version.split()[0]

    def run(self, code, stdin=None, append="", names=None, limit=1.0):
        return run_code(code, stdin=stdin, append=append, names=names, interactive=False, limit=limit)

    def close(self):
        pass


NODE_SERVER = r"""
const readline = require("readline");
const { loadPyodide } = require("pyodide");
(async () => {
  const py = await loadPyodide();
  py.runPython("import sys, io, json, traceback, time, builtins");
  const harness = require("fs").readFileSync(process.argv[2], "utf8");
  process.stdout.write(JSON.stringify({ ready: py.runPython("import sys; sys.version") }) + "\n");
  const rl = readline.createInterface({ input: process.stdin });
  for await (const line of rl) {
    const req = JSON.parse(line);
    let result;
    try {
      py.globals.set("_student_code", req.code || "");
      py.globals.set("_append_code", req.append || "");
      py.globals.set("_stdin_json", JSON.stringify(req.stdin || []));
      py.globals.set("_names_json", JSON.stringify(req.names || []));
      py.globals.set("_interactive", false);
      py.globals.set("_time_limit", req.limit || 3);
      py.runPython(harness);
      const raw = py.globals.get("_pycoach_result");
      result = JSON.parse(typeof raw === "string" ? raw : String(raw));
    } catch (error) {
      result = { ok: false, stdout: "", stderr: "", errorType: "BridgeError", errorMessage: String(error), traceback: "", values: {}, needsInput: false, inputPrompt: "", timedOut: false };
    }
    process.stdout.write(JSON.stringify(result) + "\n");
  }
})();
"""


class PyodideRunner:
    """Runs the harness in Pyodide under Node. Needs `npm install pyodide@0.26.4` in PYODIDE_NODE_DIR."""

    def __init__(self, node_dir: str):
        node_dir = os.path.abspath(node_dir)
        server = Path(node_dir) / "pycoach_server.cjs"
        server.write_text(NODE_SERVER, encoding="utf-8")
        harness = Path(node_dir) / "pycoach_harness.py"
        harness.write_text(HARNESS.strip() + "\n", encoding="utf-8")
        self.proc = subprocess.Popen(
            ["node", str(server), str(harness)],
            cwd=node_dir,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
        )
        ready = json.loads(self.proc.stdout.readline())
        self.name = "Pyodide (Python " + ready["ready"].split()[0] + ")"

    def run(self, code, stdin=None, append="", names=None, limit=1.0):
        req = {"code": code, "stdin": list(stdin or []), "append": append or "", "names": list(names or []), "limit": max(limit, 2.0)}
        self.proc.stdin.write(json.dumps(req) + "\n")
        self.proc.stdin.flush()
        return json.loads(self.proc.stdout.readline())

    def close(self):
        if self.proc.stdin:
            self.proc.stdin.close()
        self.proc.wait(timeout=30)


def normalize(raw: str) -> str:
    text = raw.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip(" \t") for line in text.split("\n")]
    while lines and lines[-1] == "":
        lines.pop()
    while lines and lines[0] == "":
        lines.pop()
    return "\n".join(lines)


_PREFIXES = {"r", "u", "b", "f", "fr", "rf", "br", "rb", "ur", "ru", "fb", "bf"}


def _is_prefix(word: str) -> bool:
    lowered = word.lower()
    return lowered in _PREFIXES


def scan_source(source: str) -> dict:
    chars = list(source)
    n = len(chars)
    i = 0
    stripped = []
    has_comment = False
    has_fstring = False

    def starts_triple(quote: str, index: int) -> bool:
        return index + 2 < n and chars[index] == quote and chars[index + 1] == quote and chars[index + 2] == quote

    while i < n:
        ch = chars[i]
        if ch == "#":
            has_comment = True
            while i < n and chars[i] != "\n":
                stripped.append(" ")
                i += 1
            continue
        if ch.isalpha() or ch == "_":
            start = i
            i += 1
            while i < n and (chars[i].isalnum() or chars[i] == "_"):
                i += 1
            word = "".join(chars[start:i])
            if i < n and chars[i] in ("'", '"') and _is_prefix(word):
                if "f" in word.lower():
                    has_fstring = True
                quote = chars[i]
                triple = starts_triple(quote, i)
                end = _consume_string(chars, i, quote, triple)
                stripped.extend(" " * (end - start))
                i = end
                continue
            stripped.extend(word)
            continue
        if ch in ("'", '"'):
            quote = ch
            triple = starts_triple(quote, i)
            end = _consume_string(chars, i, quote, triple)
            stripped.extend(" " * (end - i))
            i = end
            continue
        stripped.append(ch)
        i += 1
    return {
        "stripped": "".join(stripped),
        "has_comment": has_comment,
        "has_fstring": has_fstring,
    }


def _consume_string(chars, i, quote, triple) -> int:
    n = len(chars)
    if triple:
        i += 3
        while i < n:
            if i + 2 < n and chars[i] == quote and chars[i + 1] == quote and chars[i + 2] == quote:
                return i + 3
            i += 1
        return i
    i += 1
    while i < n:
        if chars[i] == "\\":
            i += 2
            continue
        if chars[i] == "\n":
            return i
        if chars[i] == quote:
            return i + 1
        i += 1
    return i


def _is_ident_char(ch: str) -> bool:
    return ch.isalnum() or ch == "_"


def contains_word(haystack: str, word: str) -> bool:
    start = 0
    while True:
        index = haystack.find(word, start)
        if index < 0:
            return False
        before_ok = index == 0 or not _is_ident_char(haystack[index - 1])
        after_index = index + len(word)
        after_ok = after_index == len(haystack) or not _is_ident_char(haystack[after_index])
        if before_ok and after_ok:
            return True
        start = index + 1


def snippet_present(source: str, snippet: str) -> bool:
    facts = scan_source(source)
    if snippet in ('f"', "f'"):
        return facts["has_fstring"]
    if snippet == "#":
        return facts["has_comment"]
    if snippet.isidentifier():
        return contains_word(facts["stripped"], snippet)
    return snippet in facts["stripped"]


def source_passes(source: str, lesson: dict) -> bool:
    if not all(snippet_present(source, snippet) for snippet in lesson["sourceMustContain"]):
        return False
    one_of = lesson["sourceMustContainOneOf"]
    if one_of and not any(snippet_present(source, snippet) for snippet in one_of):
        return False
    return True


def compact(text: str) -> str:
    return "".join(text.split())


def failed(result: dict) -> bool:
    return bool(result.get("needsInput") or result.get("timedOut") or result.get("errorType"))


def passes_all(runner, code: str, practice: dict, finalized_tests: list, limit=1.0) -> tuple[bool, str]:
    """The same decision LessonChecker.swift makes, in the same order."""
    if BLANK in code:
        return False, "blank"
    for test in finalized_tests:
        names = list(test["values"].keys())
        result = runner.run(code, stdin=test["stdin"], append=test["appendCode"] or "", names=names, limit=limit)
        if failed(result):
            return False, "run:" + str(result.get("errorType"))
        if test["stdoutEquals"] is not None:
            if normalize(result["stdout"]) != normalize(test["stdoutEquals"]):
                return False, "stdout:" + normalize(result["stdout"])
        for needle in test["stdoutContains"]:
            if normalize(needle) not in normalize(result["stdout"]):
                return False, "contains:" + needle
        for name, expected in test["values"].items():
            if result["values"].get(name) != expected:
                return False, f"value:{name}={result['values'].get(name)!r}"
    if not source_passes(code, practice):
        return False, "source"
    return True, "ok"


def self_test() -> None:
    hello = run_code('print("Hello")', limit=1)
    if normalize(hello["stdout"]) != "Hello":
        raise SystemExit("harness self-test failed for print")
    needed = run_code('input("Age: ")', interactive=True, limit=1)
    if not needed["needsInput"] or needed["inputPrompt"] != "Age: ":
        raise SystemExit("harness self-test failed for input")
    timed = run_code("while True:\n    x = 1", limit=0.2)
    if not timed["timedOut"]:
        raise SystemExit("harness self-test failed for timeout")
    if normalize("Hello \n\n") != "Hello":
        raise SystemExit("normalize failed")
    sample = 'message = "while"  # note\nif ready:\n    print(f"hi {message}")\n'
    if snippet_present(sample, "while"):
        raise SystemExit("while inside a string should not count")
    if not snippet_present(sample, "#"):
        raise SystemExit("comment should count")
    if not snippet_present(sample, 'f"'):
        raise SystemExit("f-string should count")
    if snippet_present("elif hour < 18:\n    pass", "if"):
        raise SystemExit("elif must not count as the word if")
    if not snippet_present("elif hour < 18:\n    pass", "elif"):
        raise SystemExit("elif should count")

