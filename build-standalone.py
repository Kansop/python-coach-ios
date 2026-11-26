#!/usr/bin/env python3
"""Bundle Python Trail into a single offline HTML file."""
from __future__ import annotations

import base64
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def minify_css(css: str) -> str:
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    return re.sub(r"\s+", " ", css).strip()


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
    html = re.sub(
        r'<link rel="stylesheet" href="style.css"\s*/?>',
        f"<style>{minify_css(css)}</style>",
        html,
        count=1,
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
    html = re.sub(
        r'<script src="course.js"></script>\s*'
        r'<script src="online.js"></script>\s*'
        r'<script src="app.js"></script>',
        scripts,
        html,
        count=1,
    )
    if "trailWorkerURL" not in html or "TrailOnline" not in html:
        raise SystemExit("standalone build is missing inlined scripts")
    out = ROOT / "Python-Trail.html"
    out.write_text(html)
    print(f"Wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
