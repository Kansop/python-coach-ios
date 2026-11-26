from .dsl import ask, checkpoint, code, fix, has, lesson, oops, out, predict, term, unit, vals, walk


def units():
    built = _units()
    stdin = {"input-ask": ["Sam"], "input-int": ["12"], "input-chat": ["Sam", "pizza"]}
    for item in built[0]["lessons"]:
        item["exampleStdin"] = stdin.get(item["id"], [])
    return built


def _units():
    return [
        unit(
            "input",
            "Input",
            "Ask the person using your program a question.",
            "keyboard",
            [
                lesson(
                    "input-ask",
                    "Asking a question",
                    """
input() lets your program ask a question and wait for an answer. Whatever the person types comes back as a string, and you can save it in a variable:

name = input("What's your name? ")

When you press Run here, a box pops up so you can type your answer. When the app checks your practice, it types the answers for you.
""",
                    """
input() pauses the program. It shows the question, waits for typing, and when the person presses enter, gives back what they typed. Saving it with = means you can use the answer later in your program.
""",
                    'name = input("What is your name? ")\nprint("Nice to meet you,", name)',
                    "Run it and type your name when the box pops up.",
                    [
                        walk('name = input("What is your name? ")', "Shows the question, waits, then saves what was typed in name."),
                        walk('print("Nice to meet you,", name)', "Uses the answer: Nice to meet you, plus the name."),
                    ],
                    [
                        oops('input("Name? ")\nprint("Hi", name)', "The answer wasn't saved, so name doesn't exist. Put name = in front of input.", 'name = input("Name? ")\nprint("Hi", name)', stdin=["Kim"]),
                    ],
                    [
                        code(
                            'Fill in the blank so the answer is saved in color. The checker will type blue.',
                            'color = ___("Favorite color? ")\nprint("You like", color)',
                            'color = input("Favorite color? ")\nprint("You like", color)',
                            [has("You like blue", stdin=["blue"]), has("You like green", stdin=["green"])],
                            [
                                "Which tool asks a question and waits for an answer?",
                                "Replace ___ with input.",
                                'The answer is: color = input("Favorite color? ")',
                            ],
                            must=["input"],
                            wrong=['color = "blue"\nprint("You like", color)'],
                        ),
                        code(
                            'Ask "What is your pet called? " and save the answer in pet. Then print: Hello, followed by the pet\'s name, with a comma in print.',
                            "# Ask, then print\n",
                            'pet = input("What is your pet called? ")\nprint("Hello,", pet)',
                            [has("Hello, Rex", stdin=["Rex"]), has("Hello, Mittens", stdin=["Mittens"])],
                            [
                                "First line: pet = input(...) with the question inside.",
                                'Second line: print("Hello,", pet)',
                                'The answer is:\npet = input("What is your pet called? ")\nprint("Hello,", pet)',
                            ],
                            must=["input"],
                            wrong=['print("Hello, Rex")'],
                        ),
                        ask(
                            "What does input() give back?",
                            "The text the person typed",
                            ["Always a number", "Nothing", "The question itself"],
                            "input() gives back what was typed, as a string.",
                            ["Think about where the answer goes.", "Even if someone types 5, it comes back as text."],
                        ),
                    ],
                    terms=[
                        term("input()", "Asks a question, waits for typing, and gives back the answer as a string.", "a waiter asking for your order and writing it down."),
                    ],
                ),
                lesson(
                    "input-int",
                    "Numbers from answers",
                    """
input() always gives back a string, even if someone types 12. "12" in quotes is text, so you can't do math with it yet.

int() turns text digits into a real number: age = int(input("Age? ")).
""",
                    """
To Python, "12" and 12 are different things: one is text, one is a number. "12" + 1 is an error, because you can't add a number to text. int() reads the digits in the text and makes a number you can do math with.
""",
                    'age = int(input("How old are you? "))\nprint("Next year you will be", age + 1)',
                    "Run it and type a number.",
                    [
                        walk('age = int(input("How old are you? "))', "input gets text like \"12\". int turns it into the number 12."),
                        walk('print("Next year you will be", age + 1)', "Now the math works: 12 + 1 is 13."),
                    ],
                    [
                        oops('age = input("Age? ")\nprint(age + 1)', "age is text, so + 1 fails with a TypeError. Wrap input with int().", 'age = int(input("Age? "))\nprint(age + 1)', stdin=["12"]),
                    ],
                    [
                        code(
                            "Fill in the blank so n becomes a number. The checker types 4.",
                            'n = ___(input("Pick a number: "))\nprint(n * 2)',
                            'n = int(input("Pick a number: "))\nprint(n * 2)',
                            [has("8", stdin=["4"]), has("20", stdin=["10"])],
                            [
                                "Which tool turns text into a whole number?",
                                "Replace ___ with int.",
                                'The answer is: n = int(input("Pick a number: "))',
                            ],
                            must=["int"],
                        ),
                        code(
                            'Ask "How many cookies? " and turn the answer into a number called cookies. Print cookies times 2.',
                            "# Ask for a number, then print double\n",
                            'cookies = int(input("How many cookies? "))\nprint(cookies * 2)',
                            [out("How many cookies? 3\n6", stdin=["3"]), out("How many cookies? 5\n10", stdin=["5"])],
                            [
                                "Wrap input(...) inside int(...).",
                                "Then print cookies * 2.",
                                'The answer is:\ncookies = int(input("How many cookies? "))\nprint(cookies * 2)',
                            ],
                            must=["int", "input"],
                            wrong=['cookies = input("How many cookies? ")\nprint(cookies * 2)'],
                        ),
                        predict(
                            'a = "5"\nb = "5"\nprint(a + b)',
                            ["10", "5 5", "a + b"],
                            "a and b are strings, so + joins them: 55.",
                            ["Are a and b text or numbers?", "+ joins text end to end."],
                        ),
                    ],
                ),
                lesson(
                    "input-chat",
                    "A tiny conversation",
                    """
A program can ask several questions in a row and use all the answers. Each input() waits for its own answer.

This is how chat bots, quizzes, and sign-up forms work.
""",
                    """
Each input() line pauses until it gets an answer, then the program moves to the next line. So the questions come one at a time, in order, and each answer is saved in its own variable.
""",
                    'name = input("Name? ")\nfood = input("Favorite food? ")\nprint(f"{name} loves {food}!")',
                    "Two questions, one answer that uses both.",
                    [
                        walk('name = input("Name? ")', "Asks the first question and saves the answer."),
                        walk('food = input("Favorite food? ")', "Then asks the second question."),
                        walk('print(f"{name} loves {food}!")', "Uses both answers in one f-string."),
                    ],
                    [],
                    [
                        code(
                            "Fill in the blanks: save the first answer in name and the second in town.",
                            'name = ___("Name? ")\ntown = ___("Town? ")\nprint(name, "lives in", town)',
                            'name = input("Name? ")\ntown = input("Town? ")\nprint(name, "lives in", town)',
                            [has("Ana lives in Lima", stdin=["Ana", "Lima"])],
                            [
                                "Both blanks need the same tool.",
                                "Replace each ___ with input.",
                                'The first line is: name = input("Name? ")',
                            ],
                            must=["input"],
                        ),
                        code(
                            'Ask "First number? " and "Second number? ". Turn both into numbers. Print their sum.',
                            "# Two questions, then print the sum\n",
                            'a = int(input("First number? "))\nb = int(input("Second number? "))\nprint(a + b)',
                            [has("7", stdin=["3", "4"]), has("30", stdin=["10", "20"])],
                            [
                                "Use int(input(...)) twice, once for each number.",
                                "Save them as a and b, then print(a + b).",
                                'The answer is:\na = int(input("First number? "))\nb = int(input("Second number? "))\nprint(a + b)',
                            ],
                            must=["int", "input"],
                            wrong=['a = input("First number? ")\nb = input("Second number? ")\nprint(a + b)'],
                        ),
                        ask(
                            "A program has two input() lines. How many answers does it wait for?",
                            "Two, one at a time",
                            ["One", "None", "As many as you like at once"],
                            "Each input() waits for its own answer, in order.",
                            ["Count the input() calls.", "Each one pauses the program."],
                        ),
                    ],
                ),
            ],
        )
    ]
