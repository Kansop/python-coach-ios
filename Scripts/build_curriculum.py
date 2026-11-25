#!/usr/bin/env python3
"""Check every Python Coach lesson, then write the lesson catalog and the harness for the app.

For each lesson this script:
  - runs the example (it must run without an error),
  - checks every walkthrough line is really in the example,
  - runs each "watch out" mistake and its fix (the fix must run; the mistake must crash or print something else),
  - runs each practice's reference solution through the same checks the app uses (it must pass),
  - runs the starter, an empty program, and every listed wrong answer (each one must fail),
  - runs each "What will this print?" snippet and uses its real output as the right answer.

It writes:
  PythonCoach/Engine/PythonHarness.swift
  PythonCoach/Curriculum/CurriculumJSON.swift

Reference solutions stay in Scripts/lessons. They are not copied into the app.
Use Scripts/check_lessons.py for a report, or to run the same checks in real Pyodide.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from coach_checks import (
    BLANK,
    HARNESS,
    ROOT,
    CPythonRunner,
    compact,
    failed,
    normalize,
    passes_all,
    self_test,
)
from lessons.catalog import all_units

HARNESS_SWIFT = ROOT / "PythonCoach" / "Engine" / "PythonHarness.swift"
CURRICULUM_SWIFT = ROOT / "PythonCoach" / "Curriculum" / "CurriculumJSON.swift"

XP = {"code": 5, "fix": 5, "predict": 3, "choice": 3}
BANNED = ["simply", "obviously", "trivial", "easy peasy", "it's easy", "this is easy", "just do"]
EMOJI = re.compile("[\U0001F000-\U0001FFFF\u2600-\u27BF\uFE0F]")


class Report:
    def __init__(self, runner_name: str):
        self.runner = runner_name
        self.counts = {
            "units": 0,
            "lessons": 0,
            "practices": 0,
            "code practices": 0,
            "fix practices": 0,
            "project steps": 0,
            "predictions": 0,
            "quick questions": 0,
            "examples run": 0,
            "walkthrough lines matched": 0,
            "mistakes checked": 0,
            "solutions passed": 0,
            "starters rejected": 0,
            "empty programs rejected": 0,
            "wrong answers rejected": 0,
            "wrong answers listed": 0,
            "predictions verified": 0,
        }
        self.failures: list[str] = []

    def add(self, key: str, amount: int = 1) -> None:
        self.counts[key] += amount

    def fail(self, where: str, why: str) -> None:
        self.failures.append(f"{where}: {why}")


def choice_order(key: str, right: str, others: list[str]) -> tuple[list[str], int]:
    slot = sum(ord(ch) for ch in key) % (len(others) + 1)
    choices = list(others)
    choices.insert(slot, right)
    return choices, slot


def text_fields(lesson: dict) -> list[str]:
    texts = [lesson["title"], lesson["explanation"], lesson["why"], lesson["exampleNote"]]
    for t in lesson["terms"]:
        texts += [t["word"], t["meaning"], t["like"]]
    for w in lesson["walkthrough"]:
        texts.append(w["note"])
    for m in lesson["mistakes"]:
        texts.append(m["why"])
    for p in lesson["practices"]:
        texts += [p["prompt"], p["explain"]] + p["hints"]
        texts += p.get("others", [])
    return texts


def walk_matches(example: str, steps: list[dict]) -> list[str]:
    flat = "\n".join(line.strip() for line in example.split("\n"))
    position = 0
    problems = []
    for step in steps:
        piece = "\n".join(line.strip() for line in step["code"].split("\n"))
        found = flat.find(piece, position)
        if found < 0:
            found = flat.find(piece)
            if found < 0:
                problems.append(f"walkthrough line not in example: {step['code']!r}")
                continue
        position = found
    return problems


def finalize_tests(runner, where, practice, report) -> list[dict] | None:
    finalized = []
    for test in practice["tests"]:
        if test["stdoutEquals"] is None and not test["stdoutContains"] and not test["valueNames"]:
            report.fail(where, "a test has nothing to check")
            return None
        result = runner.run(practice["solution"], stdin=test["stdin"], append=test["appendCode"] or "", names=test["valueNames"])
        if failed(result):
            report.fail(where, f"solution crashed: {result.get('errorType')}: {result.get('errorMessage')}\n{practice['solution']}")
            return None
        if test["stdoutEquals"] is not None and normalize(result["stdout"]) != normalize(test["stdoutEquals"]):
            report.fail(where, f"solution output {normalize(result['stdout'])!r} != expected {test['stdoutEquals']!r}")
            return None
        values = {}
        for name in test["valueNames"]:
            if name not in result["values"]:
                report.fail(where, f"solution did not set {name}")
                return None
            values[name] = result["values"][name]
        finalized.append(
            {
                "stdin": test["stdin"],
                "appendCode": test["appendCode"],
                "stdoutEquals": test["stdoutEquals"],
                "stdoutContains": test["stdoutContains"],
                "values": values,
            }
        )
    return finalized


def check_code_practice(runner, where, practice, report) -> list[dict] | None:
    kind = practice["kind"]
    report.add("project steps" if practice["carryCode"] else ("fix practices" if kind == "fix" else "code practices"))
    if len(practice["hints"]) < 3:
        report.fail(where, "code practices need at least 3 hints")
    solution_compact = compact(practice["solution"])
    for hint in practice["hints"][:-1]:
        if solution_compact and solution_compact in compact(hint):
            report.fail(where, f"only the last hint may show the whole answer: {hint}")
    if not practice["tests"]:
        report.fail(where, "no tests")
        return None
    if BLANK in practice["solution"]:
        report.fail(where, "solution still has a blank")
    finalized = finalize_tests(runner, where, practice, report)
    if finalized is None:
        return None
    ok, why = passes_all(runner, practice["solution"], practice, finalized)
    if ok:
        report.add("solutions passed")
    else:
        report.fail(where, f"solution did not pass the app's checks ({why})")
    ok, why = passes_all(runner, practice["starterCode"], practice, finalized)
    if ok:
        report.fail(where, "the starter already passes")
    else:
        report.add("starters rejected")
    if kind == "fix" and BLANK in practice["starterCode"]:
        report.fail(where, "fix practices should start with real buggy code, not a blank")
    ok, _ = passes_all(runner, "", practice, finalized)
    if ok:
        report.fail(where, "an empty program passes")
    else:
        report.add("empty programs rejected")
    for wrong in practice["wrong"]:
        report.add("wrong answers listed")
        ok, _ = passes_all(runner, wrong, practice, finalized)
        if ok:
            report.fail(where, f"a wrong answer passes:\n{wrong}")
        else:
            report.add("wrong answers rejected")
    return finalized


def build_lesson(runner, unit, item, report) -> dict | None:
    lid = item["id"]
    report.add("lessons")
    for text in text_fields(item):
        lowered = text.lower()
        for word in BANNED:
            if word in lowered:
                report.fail(lid, f"avoid the phrase {word!r}: {text}")
        if EMOJI.search(text):
            report.fail(lid, f"no emoji in lesson text: {text}")
    if item["kind"] == "checkpoint":
        if len(item["practices"]) < 3:
            report.fail(lid, "checkpoints need at least 3 questions")
    elif len(item["practices"]) < 2:
        report.fail(lid, "lessons need at least 2 practices")
    if item["kind"] == "lesson":
        if not item["why"]:
            report.fail(lid, "missing why-it-works")
        if not item["exampleCode"]:
            report.fail(lid, "missing example")
        if not item["walkthrough"]:
            report.fail(lid, "missing walkthrough")
    if item["exampleCode"]:
        result = runner.run(item["exampleCode"], stdin=item["exampleStdin"])
        if failed(result):
            report.fail(lid, f"example failed: {result.get('errorType')}: {result.get('errorMessage')}")
        else:
            report.add("examples run")
        for problem in walk_matches(item["exampleCode"], item["walkthrough"]):
            report.fail(lid, problem)
        report.add("walkthrough lines matched", len(item["walkthrough"]))
    for mistake in item["mistakes"]:
        fixed = runner.run(mistake["fix"], stdin=mistake["stdin"])
        if failed(fixed):
            report.fail(lid, f"mistake fix does not run: {mistake['fix']!r} ({fixed.get('errorType')})")
            continue
        wrong = runner.run(mistake["wrong"], stdin=mistake["stdin"])
        if not failed(wrong) and normalize(wrong["stdout"]) == normalize(fixed["stdout"]):
            report.fail(lid, f"mistake behaves the same as the fix: {mistake['wrong']!r}")
            continue
        report.add("mistakes checked")

    public_practices = []
    xp = 10 if item["kind"] == "project" else 0
    for index, practice in enumerate(item["practices"]):
        pid = f"p{index + 1}"
        where = f"{lid}/{pid}"
        report.add("practices")
        kind = practice["kind"]
        xp += XP[kind]
        if kind in ("predict", "choice") and len(practice["hints"]) < 2:
            report.fail(where, "needs at least 2 hints")
        tests: list[dict] = []
        choices: list[str] = []
        answer = -1
        if kind == "predict":
            report.add("predictions")
            if "input(" in practice["showCode"]:
                report.fail(where, "prediction code should not ask for input")
            result = runner.run(practice["showCode"])
            if failed(result):
                report.fail(where, f"prediction code failed: {result.get('errorType')}")
                continue
            actual = normalize(result["stdout"])
            others = [normalize(o) for o in practice["others"]]
            if len(others) < 2:
                report.fail(where, "predictions need at least 2 wrong choices")
            if actual in others:
                report.fail(where, f"a wrong choice equals the real output {actual!r}")
            if len(set(others)) != len(others):
                report.fail(where, "duplicate choices")
            choices, answer = choice_order(where, actual, others)
            report.add("predictions verified")
        elif kind == "choice":
            report.add("quick questions")
            if practice["right"] in practice["others"] or len(practice["others"]) < 2:
                report.fail(where, "bad choices")
            choices, answer = choice_order(where, practice["right"], practice["others"])
        else:
            finalized = check_code_practice(runner, where, practice, report)
            if finalized is None:
                continue
            tests = finalized
        public_practices.append(
            {
                "id": pid,
                "kind": kind,
                "prompt": practice["prompt"],
                "starterCode": practice["starterCode"],
                "showCode": practice["showCode"],
                "hints": practice["hints"],
                "sourceMustContain": practice["sourceMustContain"],
                "sourceMustContainOneOf": practice["sourceMustContainOneOf"],
                "tests": tests,
                "choices": choices,
                "answer": answer,
                "explain": practice["explain"],
                "carryCode": practice["carryCode"],
            }
        )
    return {
        "id": lid,
        "title": item["title"],
        "kind": item["kind"],
        "xp": xp,
        "terms": item["terms"],
        "explanation": item["explanation"],
        "why": item["why"],
        "exampleCode": item["exampleCode"],
        "exampleNote": item["exampleNote"],
        "walkthrough": [{"code": w["code"], "note": w["note"]} for w in item["walkthrough"]],
        "mistakes": [{"wrong": m["wrong"], "why": m["why"], "fix": m["fix"]} for m in item["mistakes"]],
        "practices": public_practices,
    }


def audit(runner) -> tuple[list[dict], Report]:
    report = Report(runner.name)
    built = []
    seen = set()
    for unit in all_units():
        report.add("units")
        lessons = []
        for item in unit["lessons"]:
            if item["id"] in seen:
                report.fail(item["id"], "duplicate lesson id")
            seen.add(item["id"])
            public = build_lesson(runner, unit, item, report)
            if public is not None:
                lessons.append(public)
        built.append(
            {
                "id": unit["id"],
                "title": unit["title"],
                "summary": unit["summary"],
                "symbol": unit["symbol"],
                "optional": unit["optional"],
                "lessons": lessons,
            }
        )
    if report.counts["lessons"] < 80:
        report.fail("catalog", f"expected at least 80 lessons, found {report.counts['lessons']}")
    return built, report


def swift_raw_string(text: str) -> str:
    hashes = 1
    while True:
        opener = "#" * hashes + '"""'
        closer = '"""' + "#" * hashes
        if opener not in text and closer not in text:
            return opener + "\n" + text + "\n" + closer
        hashes += 1


def emit_swift(path: Path, type_name: str, body: str, note: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    prop = "source" if type_name == "PythonHarness" else "text"
    contents = (
        "import Foundation\n\n"
        f"/// {note}\n"
        "/// Generated by Scripts/build_curriculum.py. Do not edit by hand.\n"
        f"enum {type_name} {{\n"
        f"    static let {prop}: String = {swift_raw_string(body)}\n"
        "}\n"
    )
    path.write_text(contents, encoding="utf-8")


def print_report(report: Report) -> None:
    print(f"Checked with {report.runner}")
    for key, value in report.counts.items():
        print(f"  {key}: {value}")
    if report.failures:
        print(f"FAILURES ({len(report.failures)}):")
        for line in report.failures:
            print("  - " + line.replace("\n", "\n    "))
    else:
        print("  failures: 0")


def main() -> None:
    self_test()
    built, report = audit(CPythonRunner())
    print_report(report)
    if report.failures:
        raise SystemExit(1)
    payload = json.dumps(built, indent=1, ensure_ascii=False)
    json.loads(payload)
    emit_swift(HARNESS_SWIFT, "PythonHarness", HARNESS.strip() + "\n", "Python wrapper that runs learner code with input, a time limit, and captured values.")
    emit_swift(CURRICULUM_SWIFT, "CurriculumJSON", payload + "\n", "Lesson catalog for Python Coach.")
    xp = sum(lesson["xp"] for unit in built for lesson in unit["lessons"])
    print(f"wrote lessons={report.counts['lessons']} practices={report.counts['practices']} xp={xp} units={len(built)}")


if __name__ == "__main__":
    sys.exit(main())
