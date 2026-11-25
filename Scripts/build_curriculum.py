#!/usr/bin/env python3
"""Build the Python Coach curriculum and the on-device harness.

The script runs every reference solution and starter through the same Python
harness the iPhone app uses, then writes:
  PythonCoach/Engine/PythonHarness.swift
  PythonCoach/Curriculum/CurriculumJSON.swift

Reference solutions stay in this file. They are not copied into the app.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from more_lessons import extra_units

ROOT = Path(__file__).resolve().parents[1]
HARNESS_SWIFT = ROOT / "PythonCoach" / "Engine" / "PythonHarness.swift"
CURRICULUM_SWIFT = ROOT / "PythonCoach" / "Curriculum" / "CurriculumJSON.swift"

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


def runtime_passes(result: dict, tests: list, expected_by_test: list) -> bool:
    if result.get("needsInput") or result.get("timedOut") or result.get("errorType"):
        return False
    # Single-run helper is not used for multi-test. See passes_all.
    return True


def passes_all(code: str, lesson: dict, finalized_tests: list, limit=1.0) -> tuple[bool, str]:
    if not source_passes(code, lesson):
        return False, "source"
    for test in finalized_tests:
        names = list(test["values"].keys())
        result = run_code(
            code,
            stdin=test["stdin"],
            append=test["appendCode"] or "",
            names=names,
            interactive=False,
            limit=limit,
        )
        if result.get("needsInput") or result.get("timedOut") or result.get("errorType"):
            return False, "run:" + str(result.get("errorType") or result.get("inputPrompt"))
        if test["stdoutEquals"] is not None:
            if normalize(result["stdout"]) != normalize(test["stdoutEquals"]):
                return False, "stdout:" + normalize(result["stdout"])
        for needle in test["stdoutContains"]:
            if normalize(needle) not in normalize(result["stdout"]):
                return False, "contains"
        for name, expected in test["values"].items():
            if result["values"].get(name) != expected:
                return False, f"value:{name}={result['values'].get(name)!r}"
    return True, "ok"


def compact(text: str) -> str:
    return "".join(text.split())


def check(stdout=None, contains=None, names=None, stdin=None, append=None):
    return {
        "stdin": list(stdin or []),
        "appendCode": append,
        "stdoutEquals": stdout,
        "stdoutContains": list(contains or []),
        "valueNames": list(names or []),
    }


def lesson(
    id,
    title,
    explanation,
    example_code,
    example_note,
    exercise,
    starter,
    hints,
    solution,
    tests,
    source=None,
    one_of=None,
    xp=10,
    example_stdin=None,
):
    if len(hints) < 2:
        raise SystemExit(f"{id} needs at least 2 hints")
    return {
        "id": id,
        "title": title,
        "explanation": explanation.strip(),
        "exampleCode": example_code.strip("\n"),
        "exampleNote": example_note.strip(),
        "exercise": exercise.strip(),
        "starterCode": starter.strip("\n"),
        "hints": hints,
        "sourceMustContain": list(source or []),
        "sourceMustContainOneOf": list(one_of or []),
        "xp": xp,
        "kind": "code",
        "quizChoices": [],
        "quizAnswer": -1,
        "quizExplain": "",
        "solution": solution.strip("\n"),
        "exampleStdin": list(example_stdin or []),
        "tests": tests,
    }


def units():
    return [
        {
            "id": "print",
            "title": "Printing",
            "summary": "Make Python talk.",
            "symbol": "text.bubble.fill",
            "lessons": [
                lesson(
                    "print-hello",
                    "Say hello",
                    """
print() tells Python to show something.
The words go inside quotes. When you run the program, those words appear in the output.
""",
                    'print("Hello, world!")',
                    "The quotes hold the text. print sends it to the output.",
                    'Print exactly this sentence: I am learning Python',
                    'print("")',
                    [
                        "You already have print and a pair of quotes. Put the sentence between the quotes.",
                        "The sentence is I am learning Python. Match the capitals and the spaces.",
                    ],
                    'print("I am learning Python")',
                    [check(stdout="I am learning Python")],
                ),
                lesson(
                    "print-two-lines",
                    "Two lines",
                    """
Each print() starts a new line.
Call it twice and you get two lines of output, one after the other.
""",
                    'print("First")\nprint("Second")',
                    "Two print calls. Two lines.",
                    "Print Python on the first line and Coach on the second line.",
                    'print("")\nprint("")',
                    [
                        "Use two print calls, one under the other.",
                        "The first line should be Python and the second should be Coach.",
                    ],
                    'print("Python")\nprint("Coach")',
                    [check(stdout="Python\nCoach")],
                ),
                lesson(
                    "print-mix",
                    "Words and numbers",
                    """
print can show more than one thing. Separate the parts with commas.
Python puts a space between them for you.
""",
                    'print("Score:", 12)',
                    "The comma mixes text and a number. A space is added for you.",
                    "Using one print and a comma, show Level and the number 3 on the same line.",
                    'print("Level")',
                    [
                        "Put a comma inside the parentheses, after the word.",
                        "The number 3 does not need quotes. Text does.",
                    ],
                    'print("Level", 3)',
                    [check(stdout="Level 3")],
                    source=["print"],
                ),
                lesson(
                    "print-comments",
                    "Notes to yourself",
                    """
A comment is a note for humans. Python skips it.
Start a comment with #. Everything after # on that line is ignored.
""",
                    '# This line is only a note\nprint("Hi")',
                    "The # line does not show up in the output. The print line does.",
                    "Print Ready, and add a real comment somewhere in your code. The comment should start with #.",
                    'print("Change me")',
                    [
                        "Change the text so the output is Ready.",
                        "Add a new line that starts with #. Python will not print that line.",
                    ],
                    '# A note for me\nprint("Ready")',
                    [check(stdout="Ready")],
                    source=["#"],
                ),
            ],
        },
        {
            "id": "variables",
            "title": "Variables",
            "summary": "Store things in named boxes.",
            "symbol": "shippingbox.fill",
            "lessons": [
                lesson(
                    "var-name",
                    "A named box",
                    """
A variable is a name that holds a value.
Use one equals sign to put a value in. Later, use the name and Python remembers the value.
""",
                    'favorite = "pizza"\nprint(favorite)',
                    "favorite holds the word pizza. print uses whatever is inside.",
                    'Create a variable named snack that holds tacos, then print it.',
                    'snack = ""\nprint(snack)',
                    [
                        "The name is snack. Put the value on the right side of =.",
                        "tacos needs quotes because it is text. Then print snack, not a new sentence.",
                    ],
                    'snack = "tacos"\nprint(snack)',
                    [check(stdout="tacos", names=["snack"])],
                ),
                lesson(
                    "var-number",
                    "A number box",
                    """
Variables can hold numbers too.
Numbers do not get quotes. Quotes are only for text.
""",
                    "score = 7\nprint(score)",
                    "score holds the number 7.",
                    "Create a variable named lives set to 3, then print it.",
                    "lives = 0\nprint(lives)",
                    [
                        "Change the 0. lives should hold 3.",
                        "Do not put quotes around 3. It is a number, not text.",
                    ],
                    "lives = 3\nprint(lives)",
                    [check(stdout="3", names=["lives"])],
                ),
                lesson(
                    "var-change",
                    "Changing the box",
                    """
You can update a variable by assigning it again.
Read the old value, change it, and store it back with =.
""",
                    "points = 0\npoints = points + 5\nprint(points)",
                    "points starts at 0, then becomes 5.",
                    "Start coins at 10. Then add 4 to coins and print the new amount.",
                    "coins = 10\nprint(coins)",
                    [
                        "After the first line, write another line that changes coins.",
                        "coins = coins + 4 uses the old value and adds 4.",
                    ],
                    "coins = 10\ncoins = coins + 4\nprint(coins)",
                    [check(stdout="14", names=["coins"])],
                ),
                lesson(
                    "var-together",
                    "Using two boxes",
                    """
A program can have lots of variables.
Print them together with a comma and Python separates them with a space.
""",
                    'city = "Paris"\nyear = 2024\nprint(city, year)',
                    "Two variables, one print, one line of output.",
                    'Set team to Comets and wins to 2. Print them on one line so the output is Comets 2.',
                    'team = ""\nwins = 0\nprint(team)',
                    [
                        "Fill in both variables first.",
                        "print(team, wins) shows both with a space between them.",
                    ],
                    'team = "Comets"\nwins = 2\nprint(team, wins)',
                    [check(stdout="Comets 2", names=["team", "wins"])],
                ),
            ],
        },
        {
            "id": "strings",
            "title": "Strings",
            "summary": "Work with text.",
            "symbol": "textformat",
            "lessons": [
                lesson(
                    "str-quotes",
                    "Text in quotes",
                    """
Text in Python is called a string. A string starts and ends with quotes.
If the text itself has an apostrophe, wrap it in double quotes so Python does not stop early.
""",
                    'message = "It\'s fine"\nprint(message)',
                    "Double quotes wrap the whole string. The apostrophe is just another character.",
                    "Set cheer to Let's go and print it. The apostrophe in Let's should stay.",
                    'cheer = ""\nprint(cheer)',
                    [
                        "The sentence contains an apostrophe, so start and end the string with double quotes.",
                        "The value should be Let's go, including the space.",
                    ],
                    'cheer = "Let\'s go"\nprint(cheer)',
                    [check(stdout="Let's go", names=["cheer"])],
                ),
                lesson(
                    "str-concat",
                    "Sticking text together",
                    """
The + sign joins strings. This is called concatenation.
It does not add a space unless you put a space in one of the strings.
""",
                    'greeting = "Hello" + " " + "Ada"\nprint(greeting)',
                    "Three pieces join into one string, with a space in the middle piece.",
                    'word1 is sun and word2 is flower. Print them joined into one word: sunflower.',
                    'word1 = "sun"\nword2 = "flower"\nprint(word1)',
                    [
                        "You need both variables in the print.",
                        "Use + between word1 and word2. Do not add a space this time.",
                    ],
                    'word1 = "sun"\nword2 = "flower"\nprint(word1 + word2)',
                    [check(stdout="sunflower", names=["word1", "word2"])],
                    source=["+"],
                ),
                lesson(
                    "str-upper",
                    "Upper and lower",
                    """
Strings have tools called methods. .upper() makes a new uppercase string.
The original variable does not change unless you save the result.
""",
                    'shout = "hey".upper()\nprint(shout)',
                    ".upper() returns a new string. print shows HEY.",
                    'Set message to python and print the uppercase version using .upper().',
                    'message = "python"\nprint(message)',
                    [
                        "Call the method on message with a dot: message.upper().",
                        "Print the result of message.upper(), not the original message.",
                    ],
                    'message = "python"\nprint(message.upper())',
                    [check(stdout="PYTHON", names=["message"])],
                    source=["upper"],
                ),
                lesson(
                    "str-fstring",
                    "F-strings",
                    """
An f-string is a string with an f before the quotes.
Inside it, put a variable in curly braces and Python drops the value in.
""",
                    'name = "Noa"\nprint(f"Hi {name}")',
                    "The f before the quote turns {name} into Noa.",
                    'item is gems and count is 2. Print You have 2 gems using an f-string.',
                    'item = "gems"\ncount = 2\nprint("You have")',
                    [
                        "Put an f right before the opening quote.",
                        "Inside the string, use {count} and {item} where the values should appear.",
                    ],
                    'item = "gems"\ncount = 2\nprint(f"You have {count} {item}")',
                    [check(stdout="You have 2 gems", names=["item", "count"])],
                    one_of=['f"', "f'"],
                ),
                lesson(
                    "str-len",
                    "How long is it?",
                    """
len() tells you how many characters are in a string.
Spaces count. The quotes around the string do not.
""",
                    'print(len("cat"))',
                    "c, a, and t are three characters, so len returns 3.",
                    'Set word to robot and print how many characters it has.',
                    'word = "robot"\nprint(word)',
                    [
                        "len(word) gives you the number of characters.",
                        "Print len(word), not the word itself. robot has 5 letters.",
                    ],
                    'word = "robot"\nprint(len(word))',
                    [check(stdout="5", names=["word"])],
                    source=["len"],
                ),
            ],
        },
        {
            "id": "math",
            "title": "Math",
            "summary": "Add, multiply, and more.",
            "symbol": "number",
            "lessons": [
                lesson(
                    "math-ops",
                    "The four operations",
                    """
Python does math with + - * and /.
* means multiply. You can print a calculation directly.
""",
                    "print(2 + 3)\nprint(10 - 4)\nprint(6 * 5)",
                    "Each line prints one answer: 5, 6, and 30.",
                    "Print the result of 8 times 7.",
                    "print(0)",
                    [
                        "The sign for multiply is *.",
                        "The whole calculation goes inside print.",
                    ],
                    "print(8 * 7)",
                    [check(stdout="56")],
                    source=["*"],
                ),
                lesson(
                    "math-types",
                    "Whole numbers and decimals",
                    """
Dividing with / always gives a decimal, even when the answer is a whole number.
5 / 2 is 2.5. Two integers can still produce a float, which is Python's decimal type.
""",
                    "print(5 / 2)\nprint(4 / 2)",
                    "Both answers have a decimal point: 2.5 and 2.0.",
                    "Print 7 divided by 2.",
                    "print(7)",
                    [
                        "Use the / operator.",
                        "Print the division itself, not a number you typed in.",
                    ],
                    "print(7 / 2)",
                    [check(stdout="3.5")],
                    source=["/"],
                ),
                lesson(
                    "math-parens",
                    "Parentheses first",
                    """
Python multiplies before it adds. Parentheses change the order.
(2 + 3) * 4 is 20, but 2 + 3 * 4 is 14 because the multiply happens first.
""",
                    "print(2 + 3 * 4)\nprint((2 + 3) * 4)",
                    "Same numbers, different answers, because of the parentheses.",
                    "Print the result of adding 5 and 5 first, then multiplying by 3. The answer should be 30.",
                    "print(5 + 5 * 3)",
                    [
                        "Without parentheses this prints 20, because multiply happens first.",
                        "Wrap the addition in parentheses so it happens before the multiply.",
                    ],
                    "print((5 + 5) * 3)",
                    [check(stdout="30")],
                    source=["(", ")", "*", "+"],
                ),
                lesson(
                    "math-mod",
                    "Remainders",
                    """
% is the remainder operator. 10 % 3 is 1, because 3 goes into 10 three times with 1 left over.
It is useful for even and odd numbers: a number is even when number % 2 is 0.
""",
                    "print(10 % 3)\nprint(8 % 2)",
                    "10 % 3 is 1. 8 % 2 is 0, so 8 is even.",
                    "Print the remainder when 17 is divided by 5.",
                    "print(0)",
                    [
                        "The remainder operator is %.",
                        "17 % 5 leaves a remainder of 2.",
                    ],
                    "print(17 % 5)",
                    [check(stdout="2")],
                    source=["%"],
                ),
            ],
        },
        {
            "id": "input",
            "title": "Input",
            "summary": "Ask the person using your program.",
            "symbol": "keyboard",
            "lessons": [
                lesson(
                    "input-ask",
                    "Asking a question",
                    """
input() pauses and waits for an answer. The text you pass in is the prompt.
The answer comes back as a string, so you can store it in a variable and print it.
""",
                    'name = input("Name: ")\nprint("Hi", name)',
                    "Run it and type a name. Python waits, then continues.",
                    """
Ask for a name with the prompt Name: and then print Hi plus the answer.
We will test it by typing Sam. The output should look like this:
Name: Sam
Hi Sam
""",
                    'name = input("Name: ")\nprint(name)',
                    [
                        "You already ask the question. Change the print line.",
                        "print(\"Hi\", name) adds a space between Hi and the name.",
                    ],
                    'name = input("Name: ")\nprint("Hi", name)',
                    [check(stdout="Name: Sam\nHi Sam", stdin=["Sam"], names=["name"])],
                    source=["input"],
                    example_stdin=["Ada"],
                ),
                lesson(
                    "input-int",
                    "Numbers from text",
                    """
input() always gives you text, even when someone types digits.
int() turns that text into a number so you can do math with it.
""",
                    'years = int(input("Years: "))\nprint(years + 1)',
                    "The answer is text first. int() makes it a number before the addition.",
                    """
Ask Age: and turn the answer into a number.
Add 1 and print Next year you will be plus that new age.
We will try two answers: 8 and then 2.
""",
                    'age = input("Age: ")\nprint(age)',
                    [
                        "Wrap the input call in int() so age is a number.",
                        "Print the words and age + 1. A comma in print adds the space.",
                    ],
                    'age = int(input("Age: "))\nprint("Next year you will be", age + 1)',
                    [
                        check(stdout="Age: 8\nNext year you will be 9", stdin=["8"], names=["age"]),
                        check(stdout="Age: 2\nNext year you will be 3", stdin=["2"], names=["age"]),
                    ],
                    source=["input", "int"],
                    example_stdin=["4"],
                ),
                lesson(
                    "input-chat",
                    "A tiny conversation",
                    """
You can ask more than once. Each input() waits for the next answer.
Use both answers later in one sentence.
""",
                    'color = input("Color: ")\nanimal = input("Animal: ")\nprint("A", color, animal)',
                    "Two questions, then one line that uses both answers.",
                    """
Ask City: and then Food: .
Print a line like In Rio I want tacos.
We will answer Rio and then tacos.
""",
                    'city = input("City: ")\nfood = input("Food: ")\nprint(city)',
                    [
                        "Keep both answers in variables.",
                        "The final line should read In Rio I want tacos. Build it from the words and the two variables.",
                    ],
                    'city = input("City: ")\nfood = input("Food: ")\nprint("In", city, "I want", food)',
                    [check(stdout="City: Rio\nFood: tacos\nIn Rio I want tacos", stdin=["Rio", "tacos"], names=["city", "food"])],
                    source=["input"],
                    example_stdin=["blue", "fox"],
                ),
            ],
        },
        {
            "id": "choices",
            "title": "Choices",
            "summary": "Let the code decide.",
            "symbol": "arrow.triangle.branch",
            "lessons": [
                lesson(
                    "if-compare",
                    "True or false",
                    """
Comparisons ask a yes-or-no question. == checks whether two values are equal.
The answer is a Boolean: True or False. Capital letters matter.
""",
                    "print(5 > 3)\nprint(5 == 4)",
                    "5 > 3 is True. 5 == 4 is False.",
                    "Print whether 10 == 10. The output should be True.",
                    "print(10 == 9)",
                    [
                        "== checks equality. A single = would assign instead.",
                        "Compare 10 with 10, then print the result.",
                    ],
                    "print(10 == 10)",
                    [check(stdout="True")],
                    source=["=="],
                ),
                lesson(
                    "if-basic",
                    "The if statement",
                    """
if runs a block of code only when a condition is True.
The line ends with a colon. The next line is indented four spaces.
""",
                    'score = 12\nif score >= 10:\n    print("You win")',
                    "score is at least 10, so the indented print runs.",
                    "Set temp to 35. If temp is greater than 30, print Hot.",
                    "temp = 35",
                    [
                        "Start the decision line with if and end it with a colon.",
                        "Indent the print line. The condition can be temp > 30.",
                    ],
                    'temp = 35\nif temp > 30:\n    print("Hot")',
                    [check(stdout="Hot", names=["temp"])],
                    source=["if"],
                ),
                lesson(
                    "if-else",
                    "A backup plan",
                    """
else runs when the if condition is False.
It also ends with a colon, and its body is indented.
""",
                    'weather = "rain"\nif weather == "sun":\n    print("Hat")\nelse:\n    print("Coat")',
                    "The condition is false, so the else branch prints Coat.",
                    "Set coins to 2. If coins is at least 5, print Buy. Otherwise print Save.",
                    "coins = 2\nprint(coins)",
                    [
                        "You need both if and else. else is the path for when there are not enough coins.",
                        "2 is less than 5, so the else line should print Save.",
                    ],
                    'coins = 2\nif coins >= 5:\n    print("Buy")\nelse:\n    print("Save")',
                    [check(stdout="Save", names=["coins"])],
                    source=["if", "else"],
                ),
                lesson(
                    "if-elif",
                    "More than two paths",
                    """
elif means else if. Use it to check another condition after the first if fails.
Python picks the first branch that is True and skips the rest.
""",
                    'temp = 10\nif temp > 25:\n    print("Hot")\nelif temp > 15:\n    print("Warm")\nelse:\n    print("Cool")',
                    "10 fails both comparisons, so the else branch runs.",
                    "Set hour to 20. If hour is under 12 print Morning, else if it is under 18 print Afternoon, otherwise print Evening.",
                    "hour = 20",
                    [
                        "Use if, then elif, then else. Each header ends with a colon.",
                        "20 is not under 12 or under 18, so the else branch should print Evening.",
                    ],
                    'hour = 20\nif hour < 12:\n    print("Morning")\nelif hour < 18:\n    print("Afternoon")\nelse:\n    print("Evening")',
                    [check(stdout="Evening", names=["hour"])],
                    source=["elif"],
                ),
                lesson(
                    "if-and",
                    "And and or",
                    """
and is True only when both sides are True.
or is True when at least one side is True. You can use them inside an if.
""",
                    "has_ticket = True\nage = 15\nif has_ticket and age >= 13:\n    print(\"Enter\")\nelse:\n    print(\"Wait\")",
                    "Both parts are true, so the if branch runs.",
                    "has_key is True and has_map is False. If both are True print Go, otherwise print Wait.",
                    "has_key = True\nhas_map = False",
                    [
                        "Join the two checks with and.",
                        "One of them is False, so and fails and you should print Wait.",
                    ],
                    'has_key = True\nhas_map = False\nif has_key and has_map:\n    print("Go")\nelse:\n    print("Wait")',
                    [check(stdout="Wait", names=["has_key", "has_map"])],
                    source=["and", "if"],
                ),
            ],
        },
        {
            "id": "loops",
            "title": "Loops",
            "summary": "Repeat without copy-paste.",
            "symbol": "repeat",
            "lessons": [
                lesson(
                    "loop-while",
                    "While loops",
                    """
while repeats a block as long as its condition stays True.
Change something inside the loop, or it will never end. We stop runaway loops.
""",
                    "count = 1\nwhile count <= 3:\n    print(count)\n    count = count + 1",
                    "count grows by 1 each time. When it passes 3, the loop stops.",
                    "Use a while loop to print 1, then 2, then 3, each on its own line.",
                    "count = 1",
                    [
                        "The condition can be count <= 3. Don't forget the colon.",
                        "Inside the loop, print count and then add 1 to it.",
                    ],
                    "count = 1\nwhile count <= 3:\n    print(count)\n    count = count + 1",
                    [check(stdout="1\n2\n3")],
                    source=["while"],
                ),
                lesson(
                    "loop-for",
                    "For and range",
                    """
for walks through a sequence. range(n) gives the numbers 0, 1, 2, up to but not including n.
The loop variable takes each number, one pass at a time.
""",
                    'for number in range(3):\n    print(number)',
                    "range(3) is 0, 1, and 2. It stops before 3.",
                    "Print Go! four times, each on its own line, using for and range.",
                    "print(\"Go!\")",
                    [
                        "range(4) repeats four times. The numbers will be 0, 1, 2, and 3.",
                        "You can ignore the number and print Go! in the indented body.",
                    ],
                    'for number in range(4):\n    print("Go!")',
                    [check(stdout="Go!\nGo!\nGo!\nGo!")],
                    source=["for", "range"],
                ),
                lesson(
                    "loop-range",
                    "Start, stop, step",
                    """
range can take more than one number. range(start, stop) begins at start and stops before stop.
range(start, stop, step) jumps by step. range(2, 8, 2) is 2, 4, 6.
""",
                    "for n in range(1, 5):\n    print(n)",
                    "This prints 1 through 4. 5 is the stop, so it is not included.",
                    "Print the even numbers 2, 4, 6, and 8. Use range with a step.",
                    "print(2)",
                    [
                        "A step of 2 counts by twos.",
                        "range(2, 10, 2) starts at 2 and stops before 10.",
                    ],
                    "for n in range(2, 10, 2):\n    print(n)",
                    [check(stdout="2\n4\n6\n8")],
                    source=["range"],
                ),
                lesson(
                    "loop-letters",
                    "Loop over text",
                    """
A string is a sequence of characters. for can walk through it one character at a time.
You do not need range for this. The loop variable becomes each letter.
""",
                    'for letter in "cat":\n    print(letter)',
                    "Three passes: c, then a, then t.",
                    'Set word to hi and print each letter on its own line with a for loop.',
                    'word = "hi"\nprint(word)',
                    [
                        "for letter in word: visits h, then i.",
                        "Indent print(letter) so it runs once per letter.",
                    ],
                    'word = "hi"\nfor letter in word:\n    print(letter)',
                    [check(stdout="h\ni", names=["word"])],
                    source=["for"],
                ),
            ],
        },
        {
            "id": "lists",
            "title": "Lists",
            "summary": "Keep items in order.",
            "symbol": "list.bullet",
            "lessons": [
                lesson(
                    "list-make",
                    "Making a list",
                    """
A list keeps values in order. Write them inside square brackets, separated by commas.
The whole list is one value, so you can store it in a variable and print it.
""",
                    'pets = ["cat", "dog"]\nprint(pets)',
                    "Square brackets build the list. print shows it with the brackets still visible.",
                    "Create a list named colors with red, blue, and green in that order. Print the list.",
                    "colors = []\nprint(colors)",
                    [
                        "Put three strings inside the brackets, separated by commas.",
                        "The order matters: red, then blue, then green.",
                    ],
                    'colors = ["red", "blue", "green"]\nprint(colors)',
                    [check(stdout="['red', 'blue', 'green']", names=["colors"])],
                ),
                lesson(
                    "list-index",
                    "Picking an item",
                    """
Indexes start at 0, not 1. The first item is list[0].
The last item is list[-1]. You can also count forward to the last position.
""",
                    'foods = ["soup", "bread", "apple"]\nprint(foods[0])\nprint(foods[-1])',
                    "Index 0 is soup. Index -1 means the last item, apple.",
                    'foods is ["soup", "bread", "apple"]. Print the first item and the last item on two lines.',
                    'foods = ["soup", "bread", "apple"]\nprint(foods)',
                    [
                        "The first item is foods[0], not foods[1].",
                        "The last item is foods[2] or foods[-1]. Print them on separate lines.",
                    ],
                    'foods = ["soup", "bread", "apple"]\nprint(foods[0])\nprint(foods[-1])',
                    [check(stdout="soup\napple", names=["foods"])],
                    source=["["],
                ),
                lesson(
                    "list-append",
                    "Growing a list",
                    """
.append() adds one item at the end of a list.
It changes the list you already have. It does not return a new one.
""",
                    'bag = ["pen"]\nbag.append("pencil")\nprint(bag)',
                    "append sticks pencil onto the end of bag.",
                    'Start bag as ["pen"]. Append pencil, then print the list.',
                    'bag = ["pen"]\nprint(bag)',
                    [
                        "Call bag.append(...) with the new item inside the parentheses.",
                        "pencil is text, so it needs quotes. Print bag after you append.",
                    ],
                    'bag = ["pen"]\nbag.append("pencil")\nprint(bag)',
                    [check(stdout="['pen', 'pencil']", names=["bag"])],
                    source=["append"],
                ),
                lesson(
                    "list-loop",
                    "Visiting every item",
                    """
for can walk through a list the same way it walks through a string.
Each pass, the loop variable is the next item.
""",
                    'colors = ["red", "blue"]\nfor color in colors:\n    print(color)',
                    "The body runs once for red and once for blue.",
                    "scores is [3, 5, 2]. Print each score on its own line using a for loop.",
                    "scores = [3, 5, 2]\nprint(scores)",
                    [
                        "for score in scores: visits 3, then 5, then 2.",
                        "Print the loop variable, not the whole list.",
                    ],
                    "scores = [3, 5, 2]\nfor score in scores:\n    print(score)",
                    [check(stdout="3\n5\n2", names=["scores"])],
                    source=["for"],
                ),
            ],
        },
        {
            "id": "functions",
            "title": "Functions",
            "summary": "Package code you can reuse.",
            "symbol": "function",
            "lessons": [
                lesson(
                    "fn-define",
                    "Defining a function",
                    """
def creates a function. The name ends with parentheses and a colon.
Nothing inside runs until you call the function by writing its name with parentheses.
""",
                    'def cheer():\n    print("Go team")\n\ncheer()',
                    "def saves the steps. cheer() actually runs them.",
                    'Define greet so it prints Hello friend, then call greet.',
                    'def greet():\n    print("")\n\ngreet()',
                    [
                        "Change the text inside the function. Indent that line so it belongs to greet.",
                        "The call greet() under the function is what makes it run.",
                    ],
                    'def greet():\n    print("Hello friend")\n\ngreet()',
                    [check(stdout="Hello friend")],
                    source=["def"],
                ),
                lesson(
                    "fn-params",
                    "Parameters",
                    """
A parameter is a name for a value the caller passes in.
When you call shout("wow"), the word parameter becomes wow inside the function.
""",
                    'def hello(name):\n    print("Hi", name)\n\nhello("Sam")',
                    "name holds Sam only during that call.",
                    """
Define shout(word) so it prints the uppercase word.
Do not call it yourself. We will try shout("wow"), shout("python"), and shout("hi").
""",
                    "def shout(word):\n    pass",
                    [
                        "Use word.upper() to get the uppercase letters.",
                        "print that uppercase string. Leave the testing to us, so don't add your own calls.",
                    ],
                    "def shout(word):\n    print(word.upper())",
                    [check(stdout="WOW\nPYTHON\nHI", append='shout("wow")\nshout("python")\nshout("hi")')],
                    source=["def"],
                ),
                lesson(
                    "fn-return",
                    "Giving a value back",
                    """
return sends a value back to the caller and ends the function.
Without return, the caller gets None. print shows a value, but it does not give it back.
""",
                    "def double(n):\n    return n * 2\n\nprint(double(4))",
                    "double(4) returns 8, and print shows that returned number.",
                    """
Define add_ten(n) so it returns n + 10.
Do not print inside the function. We will print add_ten(4) and add_ten(0).
""",
                    "def add_ten(n):\n    return n",
                    [
                        "return hands the answer back. The answer is the parameter plus 10.",
                        "Don't print inside add_ten. We print the values that come back.",
                    ],
                    "def add_ten(n):\n    return n + 10",
                    [check(stdout="14\n10", append="print(add_ten(4))\nprint(add_ten(0))")],
                    source=["def", "return"],
                ),
                lesson(
                    "fn-reuse",
                    "Using a function twice",
                    """
Once a function returns a value, you can use it as many times as you want.
The function stays the same. The arguments can change.
""",
                    'def stars(count):\n    return "*" * count\n\nprint(stars(2))\nprint(stars(4))',
                    "* on a string repeats it. Two calls make two different strings.",
                    """
Define badge(name) so it returns the name plus the text " the Coder".
Do not print inside the function. We will print badge("Ari") and badge("Noa").
""",
                    "def badge(name):\n    return name",
                    [
                        "Join the name and the extra words with +.",
                        "The extra text starts with a space: space, then the Coder.",
                    ],
                    'def badge(name):\n    return name + " the Coder"',
                    [check(stdout="Ari the Coder\nNoa the Coder", append='print(badge("Ari"))\nprint(badge("Noa"))')],
                    source=["def", "return"],
                ),
            ],
        },
        {
            "id": "dictionaries",
            "title": "Dictionaries",
            "summary": "Look things up by name.",
            "symbol": "curlybraces",
            "lessons": [
                lesson(
                    "dict-make",
                    "Keys and values",
                    """
A dictionary pairs keys with values. Look a key up with square brackets.
Keys are usually strings. The values can be text, numbers, or other things.
""",
                    'pet = {"name": "Luna", "age": 3}\nprint(pet["name"])',
                    'pet["name"] finds the value stored under that key.',
                    'Make player with name set to Kai and lives set to 3. Print player["name"].',
                    "player = {}\nprint(player)",
                    [
                        "Inside the braces, write the key, a colon, then the value. Separate pairs with a comma.",
                        'Print player["name"], with quotes around the key name.',
                    ],
                    'player = {"name": "Kai", "lives": 3}\nprint(player["name"])',
                    [check(stdout="Kai", names=["player"])],
                ),
                lesson(
                    "dict-update",
                    "Adding and changing",
                    """
Assigning to a key updates the dictionary.
If the key is new, Python adds it. If it already exists, Python replaces the value.
""",
                    'player = {"name": "Kai"}\nplayer["score"] = 10\nprint(player["score"])',
                    "score was not there before. The assignment creates it.",
                    'Start inventory as {"potion": 1}. Add the key "key" with the value 2, then print that value.',
                    'inventory = {"potion": 1}\nprint(inventory)',
                    [
                        'inventory["key"] = 2 adds a new pair.',
                        'After that, print inventory["key"].',
                    ],
                    'inventory = {"potion": 1}\ninventory["key"] = 2\nprint(inventory["key"])',
                    [check(stdout="2", names=["inventory"])],
                ),
                lesson(
                    "dict-loop",
                    "Looping over a dictionary",
                    """
for walks through a dictionary's keys. The values are not the loop variable.
Use the key to look the value back up: scores[name].
""",
                    'pet = {"name": "Luna", "age": 3}\nfor key in pet:\n    print(key, pet[key])',
                    "Each pass prints one key and the value stored with it.",
                    'scores is {"Ana": 5, "Bo": 7}. Use a loop to print each name and score, like Ana 5.',
                    'scores = {"Ana": 5, "Bo": 7}\nprint(scores)',
                    [
                        "for name in scores: gives you Ana, then Bo.",
                        "print(name, scores[name]) shows the name and the number on one line.",
                    ],
                    'scores = {"Ana": 5, "Bo": 7}\nfor name in scores:\n    print(name, scores[name])',
                    [check(stdout="Ana 5\nBo 7", names=["scores"])],
                    source=["for"],
                ),
            ],
        },
        {
            "id": "projects",
            "title": "Projects",
            "summary": "Mix the ideas into small programs.",
            "symbol": "hammer.fill",
            "lessons": [
                lesson(
                    "proj-greeter",
                    "Greeter bot",
                    """
This project mixes input, strings, and if.
.lower() makes a copy of the text in lowercase, which is handy when you do not care about capitals.
""",
                    'name = input("Name: ")\nif name.lower() == "sam":\n    print("Welcome back, coach")\nelse:\n    print("Hello there")',
                    "Sam, SAM, and sam all take the special path because of .lower().",
                    """
Ask Name: .
If the lowercase name is sam, print Welcome back, coach.
Otherwise print Hello, plus the name exactly as it was typed.
We will try Sam, then SAM, then Riley.
""",
                    'name = input("Name: ")',
                    [
                        "Compare name.lower() with sam so capitals do not matter.",
                        "The else branch should print Hello, and then the original name. Keep their capitals.",
                    ],
                    'name = input("Name: ")\nif name.lower() == "sam":\n    print("Welcome back, coach")\nelse:\n    print("Hello,", name)',
                    [
                        check(stdout="Name: Sam\nWelcome back, coach", stdin=["Sam"]),
                        check(stdout="Name: SAM\nWelcome back, coach", stdin=["SAM"]),
                        check(stdout="Name: Riley\nHello, Riley", stdin=["Riley"]),
                    ],
                    source=["input", "if", "else"],
                    xp=20,
                    example_stdin=["Sam"],
                ),
                lesson(
                    "proj-adder",
                    "Adding machine",
                    """
input() returns text, so convert both answers with int() before you add them.
Then build a clear sentence around the result.
""",
                    'first = int(input("A: "))\nsecond = int(input("B: "))\nprint(first + second)',
                    "Two numbers come in as text, become integers, and get added.",
                    """
Ask First: and Second: .
Convert both answers to integers, add them, and print The sum is plus the result.
We will try 12 and 30, then 0 and 5.
""",
                    'first = input("First: ")\nsecond = input("Second: ")\nprint(first)',
                    [
                        "Wrap each input() in int() before you add.",
                        "print(\"The sum is\", total) puts one space before the number.",
                    ],
                    'first = int(input("First: "))\nsecond = int(input("Second: "))\nprint("The sum is", first + second)',
                    [
                        check(stdout="First: 12\nSecond: 30\nThe sum is 42", stdin=["12", "30"]),
                        check(stdout="First: 0\nSecond: 5\nThe sum is 5", stdin=["0", "5"]),
                    ],
                    source=["input", "int"],
                    xp=20,
                    example_stdin=["2", "3"],
                ),
                lesson(
                    "proj-inventory",
                    "Inventory",
                    """
Functions and dictionaries work well together.
The function knows how to describe one item. The dictionary knows how many you have.
""",
                    'def describe(item, count):\n    return f"{count} x {item}"\n\nprint(describe("map", 1))',
                    "describe returns text. It does not print by itself.",
                    """
Define describe(item, count) so it returns text like 3 x apples.
Create inventory as {"apples": 3, "bread": 1}.
Do not print yourself. We will describe every inventory item, then describe("gem", 4).
""",
                    'def describe(item, count):\n    return ""\n\ninventory = {}',
                    [
                        "An f-string can build count, a space, x, a space, and the item.",
                        "inventory needs both keys: apples with 3, and bread with 1.",
                    ],
                    'def describe(item, count):\n    return f"{count} x {item}"\n\ninventory = {"apples": 3, "bread": 1}',
                    [
                        check(
                            stdout="3 x apples\n1 x bread\n4 x gem",
                            names=["inventory"],
                            append='for item in inventory:\n    print(describe(item, inventory[item]))\nprint(describe("gem", 4))',
                        )
                    ],
                    source=["def", "return"],
                    one_of=['f"', "f'"],
                    xp=20,
                ),
                lesson(
                    "proj-quiz",
                    "Mini quiz",
                    """
You now have the pieces for a tiny quiz: ask, convert, decide, and answer.
int() lets you compare the answer to a real number instead of text.
""",
                    'answer = int(input("2 + 2 = "))\nif answer == 4:\n    print("Correct")\nelse:\n    print("Not quite")',
                    "The number 4 takes the Correct branch. Anything else does not.",
                    """
Ask the question 7 + 5 = with a space after the equals sign.
Turn the answer into an integer. If it is 12, print Correct. Otherwise print Not quite.
We will answer 12 and then 3.
""",
                    'answer = input("7 + 5 = ")',
                    [
                        "int(input(...)) gives you a number you can compare with ==.",
                        "if / else chooses Correct or Not quite. 12 is the only correct answer.",
                    ],
                    'answer = int(input("7 + 5 = "))\nif answer == 12:\n    print("Correct")\nelse:\n    print("Not quite")',
                    [
                        check(stdout="7 + 5 = 12\nCorrect", stdin=["12"]),
                        check(stdout="7 + 5 = 3\nNot quite", stdin=["3"]),
                    ],
                    source=["input", "int", "if", "else"],
                    xp=20,
                    example_stdin=["4"],
                ),
            ],
        },
    ]


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
    contents = (
        "import Foundation\n\n"
        f"/// {note}\n"
        "/// Generated by Scripts/build_curriculum.py. Do not edit by hand.\n"
        f"enum {type_name} {{\n"
        f"    static let text: String = {swift_raw_string(body)}\n"
        "}\n"
    )
    # PythonHarness uses `source` as the property name.
    if type_name == "PythonHarness":
        contents = contents.replace("static let text:", "static let source:", 1)
    path.write_text(contents, encoding="utf-8")


def public_lesson(item: dict, tests: list) -> dict:
    return {
        "id": item["id"],
        "title": item["title"],
        "explanation": item["explanation"],
        "exampleCode": item["exampleCode"],
        "exampleNote": item["exampleNote"],
        "exercise": item["exercise"],
        "starterCode": item["starterCode"],
        "hints": item["hints"],
        "sourceMustContain": item["sourceMustContain"],
        "sourceMustContainOneOf": item["sourceMustContainOneOf"],
        "xp": item["xp"],
        "kind": item.get("kind", "code"),
        "quizChoices": item.get("quizChoices", []),
        "quizAnswer": item.get("quizAnswer", -1),
        "quizExplain": item.get("quizExplain", ""),
        "tests": tests,
    }


def main() -> None:
    self_test()
    built_units = []
    lesson_count = 0
    xp_total = 0
    for unit in units() + extra_units():
        public_lessons = []
        for item in unit["lessons"]:
            lesson_count += 1
            xp_total += item["xp"]
            item.setdefault("kind", "code")
            item.setdefault("quizChoices", [])
            item.setdefault("quizAnswer", -1)
            item.setdefault("quizExplain", "")
            if item["kind"] == "quiz":
                choices = item["quizChoices"]
                if len(choices) < 2 or not (0 <= item["quizAnswer"] < len(choices)):
                    raise SystemExit(f"bad quiz {item['id']}")
                if len(item["hints"]) < 2:
                    raise SystemExit(f"{item['id']} needs at least 2 hints")
                public_lessons.append(public_lesson(item, []))
                continue
            names = []
            for test in item["tests"]:
                names.extend(test["valueNames"])
                if test["stdoutEquals"] is None and not test["stdoutContains"] and not test["valueNames"]:
                    raise SystemExit(f"{item['id']} has a test with no expectation")
            solution = run_code(
                item["solution"],
                stdin=item["tests"][0]["stdin"],
                append=item["tests"][0]["appendCode"] or "",
                names=item["tests"][0]["valueNames"],
                limit=1,
            )
            if solution.get("errorType") or solution.get("timedOut") or solution.get("needsInput"):
                raise SystemExit(f"solution failed for {item['id']}: {solution}")
            finalized = []
            for test in item["tests"]:
                result = run_code(
                    item["solution"],
                    stdin=test["stdin"],
                    append=test["appendCode"] or "",
                    names=test["valueNames"],
                    limit=1,
                )
                if result.get("errorType") or result.get("timedOut") or result.get("needsInput"):
                    raise SystemExit(f"solution test failed for {item['id']}: {result}")
                if test["stdoutEquals"] is not None and normalize(result["stdout"]) != normalize(test["stdoutEquals"]):
                    raise SystemExit(
                        f"{item['id']} stdout mismatch\nexpected {test['stdoutEquals']!r}\nactual {result['stdout']!r}"
                    )
                for needle in test["stdoutContains"]:
                    if normalize(needle) not in normalize(result["stdout"]):
                        raise SystemExit(f"{item['id']} missing needle {needle!r}")
                values = {}
                for name in test["valueNames"]:
                    if name not in result["values"]:
                        raise SystemExit(f"{item['id']} solution did not set {name}")
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
            ok, reason = passes_all(item["solution"], item, finalized)
            if not ok:
                raise SystemExit(f"solution did not pass checks for {item['id']}: {reason}")
            starter_ok, starter_reason = passes_all(item["starterCode"], item, finalized)
            if starter_ok:
                raise SystemExit(f"starter already passes {item['id']}")
            solution_compact = compact(item["solution"])
            for hint in item["hints"]:
                if solution_compact and solution_compact in compact(hint):
                    raise SystemExit(f"hint contains the full solution for {item['id']}: {hint}")
            example = run_code(
                item["exampleCode"],
                stdin=item["exampleStdin"],
                limit=1,
            )
            if example.get("errorType") or example.get("timedOut") or example.get("needsInput"):
                raise SystemExit(f"example failed for {item['id']}: {example}")
            public_lessons.append(public_lesson(item, finalized))
        built_units.append(
            {
                "id": unit["id"],
                "title": unit["title"],
                "summary": unit["summary"],
                "symbol": unit["symbol"],
                "lessons": public_lessons,
            }
        )
    if lesson_count < 80:
        raise SystemExit(f"expected at least 80 lessons, found {lesson_count}")
    payload = json.dumps(built_units, indent=2, ensure_ascii=False)
    json.loads(payload)
    emit_swift(
        HARNESS_SWIFT,
        "PythonHarness",
        HARNESS.strip() + "\n",
        "Python wrapper that runs learner code with input, a time limit, and captured values.",
    )
    emit_swift(
        CURRICULUM_SWIFT,
        "CurriculumJSON",
        payload + "\n",
        "Lesson catalog for Python Coach.",
    )
    print(f"lessons={lesson_count} xp={xp_total} units={len(built_units)}")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as exc:
        print(f"build_curriculum failed: {exc}", file=sys.stderr)
        raise
