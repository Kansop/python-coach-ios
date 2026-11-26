from .dsl import ask, checkpoint, code, fix, has, lesson, oops, out, predict, term, unit, vals, walk


def units():
    built = _units()
    stdin = {"loop-break": ["hi", "quit"], "loop-ask-again": ["abc", "open sesame"]}
    for item in built[0]["lessons"]:
        item["exampleStdin"] = stdin.get(item["id"], [])
    return built


def _units():
    return [
        unit(
            "more-loops",
            "More loops",
            "Stop early, skip ahead, and put loops inside loops.",
            "arrow.2.squarepath",
            [
                lesson(
                    "loop-break",
                    "Stop early with break",
                    """
break stops a loop right away, even if it had more laps to go. The program carries on after the loop.

It's often used with while True:, a loop that would run forever, plus an if that breaks out when it's time to stop.
""",
                    """
while True means "keep going," so the only way out is break. That's handy when you don't know ahead of time how many laps you need, like asking questions until someone types quit.
""",
                    'while True:\n    word = input("Say something (or quit): ")\n    if word == "quit":\n        break\n    print("You said", word)\nprint("Bye!")',
                    "Run it. Type a few words, then type quit.",
                    [
                        walk("while True:", "Keeps looping until something breaks out."),
                        walk('word = input("Say something (or quit): ")', "Asks each lap."),
                        walk('if word == "quit":', "Checks whether it's time to stop."),
                        walk("break", "Leaves the loop right away."),
                        walk('print("Bye!")', "Runs after the loop."),
                    ],
                    [
                        oops('for n in range(5):\n    print(n)\nbreak', "break only works inside a loop. Indent it under an if inside the loop.", 'for n in range(5):\n    print(n)\n    if n == 2:\n        break'),
                    ],
                    [
                        code(
                            "Fill in the blank so the loop stops when n reaches 3.",
                            "for n in range(10):\n    if n == 3:\n        ___\n    print(n)",
                            "for n in range(10):\n    if n == 3:\n        break\n    print(n)",
                            [out("0\n1\n2")],
                            [
                                "The word that stops a loop right away.",
                                "Replace ___ with break.",
                                "The line is: break",
                            ],
                            must=["break"],
                        ),
                        code(
                            "Ask for numbers and add them to total until the person types 0. Then print total. The checker types 5, 10, then 0.",
                            'total = 0\nwhile True:\n    n = int(input("Number (0 to stop): "))\n    # stop on 0, otherwise add to total\n\nprint(total)',
                            'total = 0\nwhile True:\n    n = int(input("Number (0 to stop): "))\n    if n == 0:\n        break\n    total += n\nprint(total)',
                            [vals("total", stdin=["5", "10", "0"]), vals("total", stdin=["0"]), vals("total", stdin=["1", "2", "3", "0"])],
                            [
                                "Inside the loop: if n == 0: break",
                                "After the if, still inside the loop: total += n",
                                "The loop body is:\n    n = int(input(\"Number (0 to stop): \"))\n    if n == 0:\n        break\n    total += n",
                            ],
                            must=["break", "while"],
                        ),
                        predict(
                            'for c in "hello":\n    if c == "l":\n        break\n    print(c)',
                            ["h\ne\nl", "hello", "h\ne\nl\nl\no"],
                            "The loop stops at the first l, before printing it.",
                            ["Which letter triggers the break?", "Is the l printed before the break?"],
                        ),
                    ],
                    terms=[
                        term("break", "Stops a loop right away.", "the emergency stop button on a treadmill."),
                    ],
                ),
                lesson(
                    "loop-continue",
                    "Skip a lap with continue",
                    """
continue skips the rest of the current lap and jumps to the next one. Unlike break, the loop keeps going.
""",
                    """
When Python hits continue, it ignores the lines below it in the loop for this lap only, then starts the next lap as usual. It's useful for skipping things you don't care about.
""",
                    "for n in range(1, 6):\n    if n == 3:\n        continue\n    print(n)",
                    "Every number except 3.",
                    [
                        walk("for n in range(1, 6):", "1 to 5."),
                        walk("if n == 3:", "On the lap where n is 3..."),
                        walk("continue", "...skip the print and go to the next lap."),
                        walk("print(n)", "Prints 1, 2, 4, 5."),
                    ],
                    [],
                    [
                        code(
                            "Fill in the blank so odd numbers are skipped.",
                            "for n in range(1, 7):\n    if n % 2 == 1:\n        ___\n    print(n)",
                            "for n in range(1, 7):\n    if n % 2 == 1:\n        continue\n    print(n)",
                            [out("2\n4\n6")],
                            [
                                "You want to skip this lap, not stop the loop.",
                                "Replace ___ with continue.",
                                "The line is: continue",
                            ],
                            must=["continue"],
                            wrong=["for n in range(1, 7):\n    if n % 2 == 1:\n        break\n    print(n)"],
                        ),
                        code(
                            'Print every word in words except the empty ones (""). Use continue.',
                            'words = ["hi", "", "there", ""]\nfor w in words:\n    # skip empty words\n    print(w)',
                            'words = ["hi", "", "there", ""]\nfor w in words:\n    if w == "":\n        continue\n    print(w)',
                            [out("hi\nthere")],
                            [
                                'Check: if w == "":',
                                "Inside that if: continue",
                                'The loop body is:\n    if w == "":\n        continue\n    print(w)',
                            ],
                            must=["continue"],
                        ),
                        predict(
                            'for c in "a1b2":\n    if c in "12":\n        continue\n    print(c)',
                            ["a\n1\nb\n2", "1\n2", "a"],
                            "The digits are skipped, so a and b print.",
                            ["Which characters are skipped?", "continue goes on to the next character."],
                        ),
                    ],
                ),
                lesson(
                    "loop-nested",
                    "Loops inside loops",
                    """
You can put a loop inside another loop. For each lap of the outer loop, the inner loop runs all the way through.

This is how you make grids, tables, and patterns.
""",
                    """
Think of a clock: the minute hand goes all the way around for each single step of the hour hand. The inner loop is the minute hand. Each level of loop gets 4 more spaces of indentation.
""",
                    'for row in range(1, 3):\n    for col in range(1, 4):\n        print(row, col)',
                    "2 rows times 3 columns makes 6 lines.",
                    [
                        walk("for row in range(1, 3):", "Outer loop: row is 1, then 2."),
                        walk("for col in range(1, 4):", "Inner loop: col goes 1, 2, 3 for every row."),
                        walk("print(row, col)", "1 1, 1 2, 1 3, then 2 1, 2 2, 2 3."),
                    ],
                    [
                        oops('for i in range(2):\n    for j in range(2):\n    print(i, j)', "The print needs 8 spaces to be inside the inner loop.", 'for i in range(2):\n    for j in range(2):\n        print(i, j)'),
                    ],
                    [
                        code(
                            'Fill in the blank so each row prints 3 stars. The end="" keeps the stars on one line, and print() starts the next row.',
                            'for row in range(2):\n    for star in range(___):\n        print("*", end="")\n    print()',
                            'for row in range(2):\n    for star in range(3):\n        print("*", end="")\n    print()',
                            [out("***\n***")],
                            [
                                "The inner range decides how many stars per row.",
                                "Replace ___ with 3.",
                                "The inner loop line is: for star in range(3):",
                            ],
                            must=["for"],
                        ),
                        code(
                            "Print a staircase of #: row 1 has 1 #, row 2 has 2, row 3 has 3. Tip: \"#\" * n makes n of them.",
                            "for n in range(1, 4):\n    # print n hashes\n    pass",
                            'for n in range(1, 4):\n    print("#" * n)',
                            [out("#\n##\n###")],
                            [
                                '"#" * n repeats # n times.',
                                'Replace pass with print("#" * n).',
                                'The answer is:\nfor n in range(1, 4):\n    print("#" * n)',
                            ],
                            must=["for"],
                            wrong=['print("#")\nprint("##")\nprint("###")'],
                        ),
                        code(
                            "Print a times table from 1 to 3: each line shows a, b, and a * b, like 1 2 2. Use two loops over range(1, 4).",
                            "# Two loops, one inside the other\n",
                            "for a in range(1, 4):\n    for b in range(1, 4):\n        print(a, b, a * b)",
                            [out("1 1 1\n1 2 2\n1 3 3\n2 1 2\n2 2 4\n2 3 6\n3 1 3\n3 2 6\n3 3 9")],
                            [
                                "Outer: for a in range(1, 4):",
                                "Inner (indented): for b in range(1, 4): then print(a, b, a * b) with 8 spaces.",
                                "The answer is:\nfor a in range(1, 4):\n    for b in range(1, 4):\n        print(a, b, a * b)",
                            ],
                            must=["for"],
                        ),
                    ],
                    terms=[
                        term("nested loop", "A loop inside another loop.", "a clock: the minute hand laps once for every hour step."),
                    ],
                ),
                lesson(
                    "loop-ask-again",
                    "Ask until it's right",
                    """
A while loop can keep asking a question until the answer is good. This is how programs check what people type.

Start with a loop that checks whether the answer is still wrong, and ask again inside it.
""",
                    """
The condition is checked before every lap. As long as the answer is not acceptable, the loop asks again. The moment a good answer arrives, the condition is False and the program moves on with an answer it can trust.
""",
                    'password = input("Password: ")\nwhile password != "open sesame":\n    print("Try again")\n    password = input("Password: ")\nprint("Welcome in")',
                    "Run it. Try a wrong password first.",
                    [
                        walk('password = input("Password: ")', "Ask once before the loop."),
                        walk('while password != "open sesame":', "While it's wrong..."),
                        walk('password = input("Password: ")', "...ask again inside the loop."),
                        walk('print("Welcome in")', "Only reached with the right answer."),
                    ],
                    [
                        oops('answer = input("Yes? ")\nwhile answer != "yes":\n    print("Try again")\nprint("ok")', "The loop never asks again, so answer never changes. Ask inside the loop.", 'answer = input("Yes? ")\nwhile answer != "yes":\n    print("Try again")\n    answer = input("Yes? ")\nprint("ok")', stdin=["no", "yes"]),
                    ],
                    [
                        code(
                            'Fill in the blank so the loop asks again. The checker types no, no, then yes.',
                            'answer = input("Ready? ")\nwhile answer != "yes":\n    answer = ___("Ready? ")\nprint("Let\'s go")',
                            'answer = input("Ready? ")\nwhile answer != "yes":\n    answer = input("Ready? ")\nprint("Let\'s go")',
                            [has("Let's go", stdin=["no", "no", "yes"]), has("Let's go", stdin=["yes"])],
                            [
                                "Which tool asks a question?",
                                "Replace ___ with input.",
                                'The line is: answer = input("Ready? ")',
                            ],
                            must=["while"],
                        ),
                        code(
                            'Keep asking "Pick 1 to 3: " until the number is between 1 and 3. Then print You picked, and the number.',
                            'n = int(input("Pick 1 to 3: "))\n# loop while n is too small or too big\n\nprint("You picked", n)',
                            'n = int(input("Pick 1 to 3: "))\nwhile n < 1 or n > 3:\n    n = int(input("Pick 1 to 3: "))\nprint("You picked", n)',
                            [has("You picked 2", stdin=["7", "0", "2"]), has("You picked 3", stdin=["3"])],
                            [
                                "The loop condition: while n < 1 or n > 3:",
                                'Inside: n = int(input("Pick 1 to 3: "))',
                                'The loop is:\nwhile n < 1 or n > 3:\n    n = int(input("Pick 1 to 3: "))',
                            ],
                            must=["while"],
                            wrong=['n = int(input("Pick 1 to 3: "))\nprint("You picked", n)'],
                        ),
                        ask(
                            "Why do you ask again inside the loop?",
                            "So the answer can change and the loop can end",
                            ["To make the loop faster", "Python requires two input lines", "To print the question twice"],
                            "If the answer never changes, the condition never changes, and the loop never ends.",
                            ["What would happen if the answer stayed the same?", "Think about infinite loops."],
                        ),
                    ],
                ),
            ],
        )
    ]
