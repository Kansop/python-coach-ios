"""Small helpers for writing lessons.

Everything written here is checked by Scripts/build_curriculum.py before it reaches the app:
reference solutions must pass, starters and listed wrong answers must fail, examples must run,
walkthrough lines must come from the example, and prediction answers come from really running the code.
"""

from __future__ import annotations


def term(word, meaning, like=""):
    return {"word": word, "meaning": meaning.strip(), "like": like.strip()}


def walk(code, note):
    return {"code": code, "note": note.strip()}


def oops(wrong, why, fix, stdin=None):
    """A common mistake. `wrong` must crash or print something different from `fix`."""
    return {"wrong": wrong.strip("\n"), "why": why.strip(), "fix": fix.strip("\n"), "stdin": list(stdin or [])}


def _test(stdin=None, append=None, out=None, contains=None, names=None):
    return {
        "stdin": [str(x) for x in (stdin or [])],
        "appendCode": append,
        "stdoutEquals": out,
        "stdoutContains": list(contains or []),
        "valueNames": list(names or []),
    }


def out(text, stdin=None, append=None):
    """The program must print exactly this."""
    return _test(stdin=stdin, append=append, out=text)


def has(*needles, stdin=None, append=None):
    """The output must contain each of these."""
    return _test(stdin=stdin, append=append, contains=needles)


def vals(*names, stdin=None, append=None, out=None):
    """These variables must end with the same values the reference solution gives them."""
    return _test(stdin=stdin, append=append, out=out, names=names)


def code(prompt, starter, solution, tests, hints, wrong=(), must=(), one_of=(), kind="code", carry=False):
    return {
        "kind": kind,
        "prompt": prompt.strip(),
        "starterCode": starter.strip("\n"),
        "solution": solution.strip("\n"),
        "tests": tests,
        "hints": list(hints),
        "wrong": [w.strip("\n") for w in wrong],
        "sourceMustContain": list(must),
        "sourceMustContainOneOf": list(one_of),
        "carryCode": carry,
        "showCode": "",
        "others": [],
        "choices": [],
        "answer": -1,
        "explain": "",
    }


def fix(prompt, starter, solution, tests, hints, wrong=(), must=(), one_of=()):
    return code(prompt, starter, solution, tests, hints, wrong=wrong, must=must, one_of=one_of, kind="fix")


def step(prompt, starter, solution, tests, hints, wrong=(), must=(), one_of=()):
    """A project step. It starts from the learner's code from the step before."""
    return code(prompt, starter, solution, tests, hints, wrong=wrong, must=must, one_of=one_of, carry=True)


def predict(show, others, explain, hints, prompt="What will this print?", stdin=None):
    """A prediction question. The right answer is whatever the code really prints."""
    return {
        "kind": "predict",
        "prompt": prompt.strip(),
        "showCode": show.strip("\n"),
        "others": list(others),
        "explain": explain.strip(),
        "hints": list(hints),
        "stdin": list(stdin or []),
        "starterCode": "",
        "solution": "",
        "tests": [],
        "wrong": [],
        "sourceMustContain": [],
        "sourceMustContainOneOf": [],
        "carryCode": False,
        "choices": [],
        "answer": -1,
    }


def ask(prompt, right, others, explain, hints):
    """A quick multiple-choice question. `right` is the correct choice."""
    return {
        "kind": "choice",
        "prompt": prompt.strip(),
        "right": right,
        "others": list(others),
        "explain": explain.strip(),
        "hints": list(hints),
        "showCode": "",
        "starterCode": "",
        "solution": "",
        "tests": [],
        "wrong": [],
        "sourceMustContain": [],
        "sourceMustContainOneOf": [],
        "carryCode": False,
        "choices": [],
        "answer": -1,
    }


def lesson(id, title, idea, why, example, note, walkthrough, mistakes, practice, terms=(), kind="lesson", example_stdin=None):
    return {
        "id": id,
        "title": title,
        "kind": kind,
        "terms": list(terms),
        "explanation": idea.strip(),
        "why": why.strip(),
        "exampleCode": example.strip("\n"),
        "exampleNote": note.strip(),
        "exampleStdin": list(example_stdin or []),
        "walkthrough": list(walkthrough),
        "mistakes": list(mistakes),
        "practices": list(practice),
    }


def project(id, title, idea, why, steps, example="", note="", walkthrough=(), mistakes=(), terms=(), example_stdin=None):
    return lesson(id, title, idea, why, example, note, walkthrough, mistakes, steps, terms=terms, kind="project", example_stdin=example_stdin)


def checkpoint(id, title, idea, practice):
    return lesson(id, title, idea, "", "", "", [], [], practice, kind="checkpoint")


def unit(id, title, summary, symbol, lessons, optional=False):
    return {"id": id, "title": title, "summary": summary, "symbol": symbol, "optional": optional, "lessons": lessons}
