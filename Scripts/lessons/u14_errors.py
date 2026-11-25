from .dsl import ask, checkpoint, code, fix, has, lesson, oops, out, predict, term, unit, vals, walk


def units():
    return [
        unit(
            "errors",
            "Errors",
            "Read error messages and catch problems.",
            "exclamationmark.shield.fill",
            [
                lesson(
                    "err-detective",
                    "Error detective",
                    """
Every Python error has a name that tells you what kind of problem it is. Here are the ones you'll see most:

- SyntaxError: Python can't read the line. Something's missing, like a bracket or quote.
- NameError: a name isn't known. Often a typo, or a variable used before it's made.
- TypeError: two kinds of values don't mix, like text + a number.
- IndexError: a position past the end of a list or string.
- KeyError: a key that isn't in a dictionary.

The app tells you the line number. Start there.
""",
                    """
The error name is your first clue, and the line number is your second. Fix the first error you see, then run again. Often one small fix makes several problems disappear.
""",
                    'items = ["pen", "ink"]\nprint(items[1])\nprint("Count: " + str(len(items)))',
                    "This code avoids two classic errors. The mistakes below show them.",
                    [
                        walk("print(items[1])", "Position 1 exists, so no IndexError."),
                        walk('print("Count: " + str(len(items)))', "str() turns the number into text, so no TypeError."),
                    ],
                    [
                        oops('items = ["pen", "ink"]\nprint(items[2])', "IndexError: positions are 0 and 1 only.", 'items = ["pen", "ink"]\nprint(items[1])'),
                        oops('n = 2\nprint("Count: " + n)', "TypeError: text + number. Wrap the number with str().", 'n = 2\nprint("Count: " + str(n))'),
                    ],
                    [
                        fix(
                            "NameError hunt. Fix the spelling so it prints 10.",
                            "score = 10\nprint(scroe)",
                            "score = 10\nprint(score)",
                            [out("10")],
                            [
                                "Read the variable name on each line carefully.",
                                "scroe is a typo.",
                                "The fixed line is: print(score)",
                            ],
                        ),
                        fix(
                            "TypeError hunt. Fix it so it prints: Level 5",
                            'level = 5\nprint("Level " + level)',
                            'level = 5\nprint("Level " + str(level))',
                            [out("Level 5")],
                            [
                                "level is a number and \"Level \" is text.",
                                "Wrap level with str().",
                                'The fixed line is: print("Level " + str(level))',
                            ],
                            one_of=["str(", ",", 'f"'],
                        ),
                        fix(
                            "IndexError hunt. Fix it so it prints the last item, c.",
                            'letters = ["a", "b", "c"]\nprint(letters[3])',
                            'letters = ["a", "b", "c"]\nprint(letters[2])',
                            [out("c")],
                            [
                                "Three items have positions 0, 1, and 2.",
                                "Use 2, or -1 for the last item.",
                                "The fixed line is: print(letters[2])",
                            ],
                        ),
                    ],
                    terms=[
                        term("traceback", "The full error message Python prints. Its last line names the error.", "a trail of footprints leading to the problem."),
                    ],
                ),
                lesson(
                    "try-int",
                    "try and except",
                    """
Some errors you can see coming. If someone types "abc" when you asked for a number, int() raises a ValueError.

try and except let you catch that error and do something friendly instead of crashing:

try:
    n = int(text)
except ValueError:
    print("That's not a number")
""",
                    """
Python runs the try block. If an error happens inside it, Python jumps straight to the matching except block instead of stopping the program. If no error happens, the except block is skipped.
""",
                    'text = "abc"\ntry:\n    n = int(text)\n    print("Double is", n * 2)\nexcept ValueError:\n    print("That is not a number")',
                    "int(\"abc\") fails, so the except part runs.",
                    [
                        walk("try:", "Try the indented lines."),
                        walk("n = int(text)", "This fails: abc isn't a number."),
                        walk('print("Double is", n * 2)', "Skipped, because the line above failed."),
                        walk("except ValueError:", "Catches that exact kind of error."),
                        walk('print("That is not a number")', "Runs instead of crashing."),
                    ],
                    [
                        oops('try:\n    n = int("x")\nprint("after")', "A try needs an except after it.", 'try:\n    n = int("x")\nexcept ValueError:\n    n = 0\nprint("after")'),
                    ],
                    [
                        code(
                            "Fill in the blank with the error name that int() raises for bad text.",
                            'try:\n    n = int("seven")\nexcept ___:\n    print("Oops, not a number")',
                            'try:\n    n = int("seven")\nexcept ValueError:\n    print("Oops, not a number")',
                            [out("Oops, not a number")],
                            [
                                "It's the error for a value that doesn't fit.",
                                "Replace ___ with ValueError.",
                                "The line is: except ValueError:",
                            ],
                            must=["try", "except"],
                        ),
                        code(
                            'The checker types an age. Print Next year: and the age + 1. If it isn\'t a number, print Please type digits.',
                            'text = input("Age? ")\n# try / except here\n',
                            'text = input("Age? ")\ntry:\n    age = int(text)\n    print("Next year:", age + 1)\nexcept ValueError:\n    print("Please type digits")',
                            [has("Next year: 13", stdin=["12"]), has("Please type digits", stdin=["twelve"])],
                            [
                                "Put the int() and the print inside try:.",
                                "Then except ValueError: with the friendly message.",
                                'The answer is:\ntry:\n    age = int(text)\n    print("Next year:", age + 1)\nexcept ValueError:\n    print("Please type digits")',
                            ],
                            must=["try", "except"],
                            wrong=['text = input("Age? ")\nage = int(text)\nprint("Next year:", age + 1)'],
                        ),
                        predict(
                            'try:\n    print("A")\n    x = 1 / 0\n    print("B")\nexcept ZeroDivisionError:\n    print("C")',
                            ["A\nB", "A\nB\nC", "C"],
                            "A prints, then the division fails, so B is skipped and C runs.",
                            ["Which line causes the error?", "Lines after the error in try are skipped."],
                        ),
                    ],
                    terms=[
                        term("exception", "An error that happens while the program runs.", "a fire alarm going off in the middle of class."),
                        term("try / except", "Try some code, and if a certain error happens, run a backup plan.", "a safety net under a trapeze."),
                    ],
                ),
                lesson(
                    "try-safe",
                    "A safe number function",
                    """
You can put try and except inside a function, so the rest of your program never has to worry about bad input.

A function like safe_int(text) gives back a number if it can, and a backup value if it can't.
""",
                    """
The return inside try only happens if int() worked. If it failed, Python jumps to except, which returns the backup. Either way the caller always gets a number back.
""",
                    'def safe_int(text):\n    try:\n        return int(text)\n    except ValueError:\n        return 0\n\nprint(safe_int("42"))\nprint(safe_int("oops"))',
                    "Good text gives its number. Bad text gives 0.",
                    [
                        walk("return int(text)", "If this works, the function returns the number."),
                        walk("except ValueError:", "If it fails..."),
                        walk("return 0", "...return 0 instead."),
                        walk('print(safe_int("oops"))', "Prints 0, no crash."),
                    ],
                    [],
                    [
                        code(
                            "Fill in the blank so bad text returns -1.",
                            'def to_number(text):\n    try:\n        return int(text)\n    except ValueError:\n        return ___\n\nprint(to_number("x"))',
                            'def to_number(text):\n    try:\n        return int(text)\n    except ValueError:\n        return -1\n\nprint(to_number("x"))',
                            [out("-1"), out("-1\n8", append='print(to_number("8"))')],
                            [
                                "The backup value goes after return in the except part.",
                                "Replace ___ with -1.",
                                "The line is: return -1",
                            ],
                            must=["try", "except"],
                        ),
                        code(
                            "Write safe_divide(a, b) that returns a / b, or None when b is 0. Catch ZeroDivisionError.",
                            "def safe_divide(a, b):\n    # try / except here\n    pass",
                            "def safe_divide(a, b):\n    try:\n        return a / b\n    except ZeroDivisionError:\n        return None",
                            [out("5.0", append="print(safe_divide(10, 2))"), out("None", append="print(safe_divide(1, 0))")],
                            [
                                "Inside try: return a / b",
                                "except ZeroDivisionError: return None",
                                "The answer is:\ndef safe_divide(a, b):\n    try:\n        return a / b\n    except ZeroDivisionError:\n        return None",
                            ],
                            must=["try", "except"],
                            wrong=["def safe_divide(a, b):\n    return a / b"],
                        ),
                        ask(
                            "When does the except block run?",
                            "Only when that error happens in the try block",
                            ["Always, after the try block", "Never", "Before the try block"],
                            "except is the backup plan. It only runs if the error it names happens.",
                            ["Think of it as a safety net.", "Does a safety net do anything if nobody falls?"],
                        ),
                    ],
                ),
            ],
        )
    ]
