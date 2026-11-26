"""Writes real CPython runs for the Swift parity check (see swift_parity.sh).

For every code, fix, and project-step practice it runs the reference solution,
the starter, an empty program, and each listed wrong answer through the same
harness the app uses, and records the Python checker's verdict. The Swift side
feeds the same runs to LessonChecker and must reach the same verdict.

It also runs every "Watch out for" mistake and records the crash, so the Swift
side can check FriendlyErrors points at a real line of the learner's code.
"""

import json
import sys
from pathlib import Path

from build_curriculum import audit
from coach_checks import CPythonRunner, passes_all
from lessons.catalog import all_units


def main() -> None:
    target = Path(sys.argv[1])
    runner = CPythonRunner()
    built, report = audit(runner)
    if report.failures:
        raise SystemExit("lesson check failed; run check_lessons.py first")
    raw_units = all_units()
    cases = []
    crashes = []
    for unit, raw_unit in zip(built, raw_units):
        for lesson, raw_lesson in zip(unit["lessons"], raw_unit["lessons"]):
            for practice, raw in zip(lesson["practices"], raw_lesson["practices"]):
                if practice["kind"] not in ("code", "fix"):
                    continue
                candidates = [("solution", raw["solution"]), ("starter", raw["starterCode"]), ("empty", "")]
                candidates += [(f"wrong{i + 1}", w) for i, w in enumerate(raw["wrong"])]
                for label, source in candidates:
                    verdict, why = passes_all(runner, source, practice, practice["tests"], limit=2.0)
                    runs = []
                    for test in practice["tests"]:
                        runs.append(runner.run(source, stdin=test["stdin"], append=test["appendCode"] or "", names=list(test["values"].keys()), limit=2.0))
                    cases.append({
                        "lesson": lesson["id"],
                        "practice": practice["id"],
                        "label": label,
                        "source": source,
                        "expected": verdict,
                        "why": why,
                        "runs": runs,
                    })
            for mistake in raw_lesson.get("mistakes", []):
                result = runner.run(mistake["wrong"], stdin=mistake.get("stdin") or [], limit=2.0)
                if result.get("errorType"):
                    crashes.append({"lesson": lesson["id"], "source": mistake["wrong"], "run": result})
    target.write_text(json.dumps({"cases": cases, "crashes": crashes}))
    print(f"wrote {len(cases)} graded cases and {len(crashes)} crashes to {target}")


if __name__ == "__main__":
    main()
