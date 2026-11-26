#!/usr/bin/env python3
"""Bundle Python Trail into a single offline HTML file.

Important: never pass the inlined JavaScript through re.sub as a replacement
string. re.sub interprets backslash escapes, so JS literals like '\\n' would
become real newlines and Safari would fail with "SyntaxError: Unexpected EOF".
"""
from __future__ import annotations

import base64
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def minify_css(css: str) -> str:
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    return re.sub(r"\s+", " ", css).strip()


def replace_once(haystack: str, pattern: str, replacement: str) -> str:
    updated, count = re.subn(pattern, lambda _m: replacement, haystack, count=1)
    if count != 1:
        raise SystemExit(f"expected to replace pattern once: {pattern}")
    return updated


def check_scripts(html: str) -> None:
    scripts = re.findall(r"<script[^>]*>(.*?)</script>", html, flags=re.I | re.S)
    if len(scripts) < 2:
        raise SystemExit("standalone build is missing inlined scripts")
    # The lesson source uses escaped newlines inside quoted strings. Those
    # two-character sequences must still be present after bundling.
    if r'name = "River"\nprint(name)' not in html:
        raise SystemExit("standalone build corrupted JS '\\n' escapes")
    for i, source in enumerate(scripts):
        if "trailWorkerURL" in source or "const paths" in source or "TrailOnline" in source:
            with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as tmp:
                tmp.write(source)
                name = tmp.name
            try:
                result = subprocess.run(["node", "--check", name], capture_output=True, text=True)
            finally:
                Path(name).unlink(missing_ok=True)
            if result.returncode != 0:
                raise SystemExit(f"standalone script {i} failed syntax check:\n{result.stderr}")


def main() -> None:
    png = base64.b64encode((ROOT / "trail.png").read_bytes()).decode()
    css = (ROOT / "style.css").read_text()
    css = css.replace("url(trail.png)", f"url(data:image/png;base64,{png})")
    worker = (
        (ROOT / "skulpt.js").read_bytes()
        + b"\n"
        + (ROOT / "stdlib.js").read_bytes()
        + b"\n"
        + (ROOT / "runner.js").read_bytes()
    )
    worker_b64 = base64.b64encode(worker).decode()
    html = (ROOT / "index.html").read_text()
    html = replace_once(
        html,
        r'<link rel="stylesheet" href="style\.css(?:\?v=[^"]*)?"\s*/?>',
        f"<style>{minify_css(css)}</style>",
    )
    scripts = (
        "<script>window.trailWorkerURL=URL.createObjectURL(new Blob("
        f"[Uint8Array.from(atob('{worker_b64}'))],{{type:'text/javascript'}}));"
        + (ROOT / "course.js").read_text()
        + "\n"
        + (ROOT / "online.js").read_text()
        + "</script>\n<script>"
        + (ROOT / "app.js").read_text()
        + "</script>"
    )
    html = replace_once(
        html,
        r'<script src="course\.js(?:\?v=[^"]*)?"></script>\s*'
        r'<script src="online\.js(?:\?v=[^"]*)?"></script>\s*'
        r'<script src="app\.js(?:\?v=[^"]*)?"></script>',
        scripts,
    )
    if "trailWorkerURL" not in html or "TrailOnline" not in html:
        raise SystemExit("standalone build is missing inlined scripts")
    check_scripts(html)
    out = ROOT / "Python-Trail.html"
    out.write_text(html)
    print(f"Wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
