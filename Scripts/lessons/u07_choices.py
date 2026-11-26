from .dsl import ask, checkpoint, code, fix, has, lesson, oops, out, predict, term, unit, vals, walk


def units():
    return [
        unit(
            "choices",
            "Choices",
            "Let your code decide what to do.",
            "arrow.triangle.branch",
            [
                lesson(
                    "if-compare",
                    "True or False",
                    """
Python can compare two values. The answer is always True or False.

- == equal to (two equals signs)
- != not equal to
- < less than, > greater than
- <= less than or equal, >= greater than or equal

True and False are called booleans. They always start with a capital letter.
""",
                    """
One = puts a value in a variable. Two == asks a question: are these the same? Python answers the question with True or False. Those answers are what let programs make decisions.
""",
                    "age = 13\nprint(age == 13)\nprint(age > 18)\nprint(age != 10)",
                    "Three questions about age, each answered with True or False.",
                    [
                        walk("age = 13", "One = puts 13 in age."),
                        walk("print(age == 13)", "Two == asks: is age equal to 13? True."),
                        walk("print(age > 18)", "Is 13 greater than 18? False."),
                        walk("print(age != 10)", "Is age not equal to 10? True."),
                    ],
                    [
                        oops('print("a" == "A")\nprint("same?")', "Capitals matter when comparing text. \"a\" and \"A\" are different, so this is False.", 'print("a" == "a")\nprint("same?")'),
                    ],
                    [
                        code(
                            "Fill in the blank with the symbol that asks is equal to, so it prints True.",
                            "score = 10\nprint(score ___ 10)",
                            "score = 10\nprint(score == 10)",
                            [out("True")],
                            [
                                "Asking is equal to uses two equals signs.",
                                "Replace ___ with ==.",
                                "The answer is: print(score == 10)",
                            ],
                            must=["=="],
                        ),
                        code(
                            "Print whether 7 is greater than 3. It should print True.",
                            "# Print the comparison\n",
                            "print(7 > 3)",
                            [out("True")],
                            [
                                "Greater than is >.",
                                "Put 7 > 3 inside print.",
                                "The answer is: print(7 > 3)",
                            ],
                            must=[">"],
                            wrong=["print(True)"],
                        ),
                        predict(
                            "x = 5\nprint(x < 5)\nprint(x <= 5)",
                            ["True\nTrue", "False\nFalse", "True\nFalse"],
                            "5 is not less than 5, but it is less than or equal to 5.",
                            ["Is 5 less than 5?", "<= also counts equal."],
                        ),
                    ],
                    terms=[
                        term("boolean", "A value that is either True or False.", "a light switch: it's either on or off."),
                        term("==", "Asks whether two things are equal. Different from =, which stores a value.", "asking 'are these twins?' instead of naming a baby."),
                    ],
                ),
                lesson(
                    "if-basic",
                    "The if statement",
                    """
if runs some code only when a condition is True.

if score > 10:
    print("Great!")

Two things matter: the colon : at the end of the if line, and the 4 spaces at the start of the line inside. Those spaces are called indentation. They show which lines belong to the if.
""",
                    """
Python checks the condition. If it's True, it runs the indented lines underneath. If it's False, it skips them and carries on after. The spaces at the start of a line are how Python knows what's inside the if and what isn't.
""",
                    'temp = 30\nif temp > 25:\n    print("It is hot")\n    print("Drink water")\nprint("Have a nice day")',
                    "Two lines are inside the if. The last line is outside, so it always runs.",
                    [
                        walk("temp = 30", "temp holds 30."),
                        walk("if temp > 25:", "Is 30 greater than 25? True, so the indented lines run. Note the colon."),
                        walk('print("It is hot")', "Indented by 4 spaces, so it's inside the if."),
                        walk('print("Drink water")', "Also inside the if."),
                        walk('print("Have a nice day")', "Not indented, so it runs no matter what."),
                    ],
                    [
                        oops('x = 5\nif x > 3\n    print("big")', "The colon at the end of the if line is missing.", 'x = 5\nif x > 3:\n    print("big")'),
                        oops('x = 5\nif x > 3:\nprint("big")', "The line inside the if needs 4 spaces in front.", 'x = 5\nif x > 3:\n    print("big")'),
                    ],
                    [
                        code(
                            "Fill in the blank with the symbol that ends an if line.",
                            'coins = 50\nif coins > 20___\n    print("You are rich")',
                            'coins = 50\nif coins > 20:\n    print("You are rich")',
                            [out("You are rich")],
                            [
                                "Every if line ends with the same punctuation mark.",
                                "Replace ___ with a colon :",
                                "The if line is: if coins > 20:",
                            ],
                            must=["if"],
                        ),
                        code(
                            "The checker types a number of points. Write an if that prints Winner when points is greater than 100. Remember the colon and the 4 spaces.",
                            'points = int(input("Points? "))\n# Write the if here\n',
                            'points = int(input("Points? "))\nif points > 100:\n    print("Winner")',
                            [out("Points? 150\nWinner", stdin=["150"]), out("Points? 50", stdin=["50"]), out("Points? 100", stdin=["100"])],
                            [
                                "Start with: if points > 100:",
                                "On the next line, put 4 spaces, then the print.",
                                'The answer is:\nif points > 100:\n    print("Winner")',
                            ],
                            must=["if"],
                            wrong=['points = int(input("Points? "))\nprint("Winner")', 'points = int(input("Points? "))\nif points >= 100:\n    print("Winner")'],
                        ),
                        predict(
                            'n = 3\nif n > 5:\n    print("big")\nprint("done")',
                            ["big\ndone", "big", "done\nbig"],
                            "3 is not greater than 5, so the indented line is skipped. done always runs.",
                            ["Is 3 > 5 True or False?", "Which line is not indented?"],
                        ),
                    ],
                    terms=[
                        term("condition", "A question that is True or False, like score > 10.", "a bouncer checking: are you on the list?"),
                        term("indentation", "Spaces at the start of a line. In Python, they show which lines belong inside something.", "items in a list on paper that are pushed in, to show they belong to the line above."),
                    ],
                ),
                lesson(
                    "if-else",
                    "A backup plan with else",
                    """
else gives the if a backup plan. If the condition is True, the if part runs. Otherwise, the else part runs. Exactly one of them runs, never both.

else also ends with a colon, and its lines are indented too.
""",
                    """
Python checks the condition once. True sends it into the if block. False sends it into the else block. After either one, the program carries on below.
""",
                    'age = 10\nif age >= 13:\n    print("You can join")\nelse:\n    print("Ask a parent")',
                    "One of the two prints runs, depending on age.",
                    [
                        walk("age = 10", "age is 10."),
                        walk("if age >= 13:", "Is 10 at least 13? False."),
                        walk('print("You can join")', "Skipped, because the condition was False."),
                        walk("else:", "The backup plan. Note the colon."),
                        walk('print("Ask a parent")', "This one runs."),
                    ],
                    [
                        oops('x = 1\nif x > 5:\n    print("big")\nelse\n    print("small")', "else needs a colon too.", 'x = 1\nif x > 5:\n    print("big")\nelse:\n    print("small")'),
                    ],
                    [
                        code(
                            "Fill in the blank so the program has a backup plan.",
                            'raining = False\nif raining:\n    print("Take an umbrella")\n___:\n    print("Wear sunglasses")',
                            'raining = False\nif raining:\n    print("Take an umbrella")\nelse:\n    print("Wear sunglasses")',
                            [out("Wear sunglasses")],
                            [
                                "The backup plan word is else.",
                                "Replace ___ with else.",
                                "The line is: else:",
                            ],
                            must=["else"],
                        ),
                        code(
                            'The checker types a number. If it is greater than 0, print Positive. Otherwise print Not positive.',
                            'n = int(input("Number? "))\n# if / else here\n',
                            'n = int(input("Number? "))\nif n > 0:\n    print("Positive")\nelse:\n    print("Not positive")',
                            [has("Positive", stdin=["5"]), has("Not positive", stdin=["-2"]), has("Not positive", stdin=["0"])],
                            [
                                "Start with: if n > 0:",
                                "Then else: with its own indented print.",
                                'The answer is:\nif n > 0:\n    print("Positive")\nelse:\n    print("Not positive")',
                            ],
                            must=["if", "else"],
                            wrong=['n = int(input("Number? "))\nprint("Positive")', 'n = int(input("Number? "))\nif n >= 0:\n    print("Positive")\nelse:\n    print("Not positive")'],
                        ),
                        predict(
                            'x = 7\nif x % 2 == 0:\n    print("even")\nelse:\n    print("odd")',
                            ["even", "even\nodd", "7"],
                            "7 % 2 is 1, not 0, so the else part runs.",
                            ["What is 7 % 2?", "Is that equal to 0?"],
                        ),
                    ],
                ),
                lesson(
                    "if-elif",
                    "More than two paths",
                    """
elif means "else, if." It adds more choices between the if and the else.

Python checks each condition from the top down and runs the first one that's True. Then it skips the rest.
""",
                    """
Think of a line of doors. Python tries the first door. If it's locked (False), it tries the next. As soon as one opens (True), it goes through and ignores all the doors after it. The else is the last door, which is always open.
""",
                    'score = 75\nif score >= 90:\n    print("A")\nelif score >= 70:\n    print("B")\nelse:\n    print("Keep practicing")',
                    "Three paths. Only one runs.",
                    [
                        walk("score = 75", "score is 75."),
                        walk("if score >= 90:", "75 >= 90? False. Skip."),
                        walk("elif score >= 70:", "75 >= 70? True. Run this part."),
                        walk('print("B")', "Shows B. The else is skipped."),
                    ],
                    [
                        oops('n = 95\nif n >= 50:\n    print("pass")\nelif n >= 90:\n    print("top")', "Order matters. 95 matches the first check, so top is never reached. Put the biggest check first.", 'n = 95\nif n >= 90:\n    print("top")\nelif n >= 50:\n    print("pass")'),
                        oops('n = 5\nif n > 9:\n    print("big")\nelse if n > 3:\n    print("medium")', "Python spells it elif, not else if.", 'n = 5\nif n > 9:\n    print("big")\nelif n > 3:\n    print("medium")'),
                    ],
                    [
                        code(
                            "Fill in the blank with the word for else-if.",
                            'light = "yellow"\nif light == "green":\n    print("Go")\n___ light == "yellow":\n    print("Slow down")\nelse:\n    print("Stop")',
                            'light = "yellow"\nif light == "green":\n    print("Go")\nelif light == "yellow":\n    print("Slow down")\nelse:\n    print("Stop")',
                            [out("Slow down")],
                            [
                                "It's a short word made from else and if.",
                                "Replace ___ with elif.",
                                'The line is: elif light == "yellow":',
                            ],
                            must=["elif"],
                        ),
                        code(
                            "The checker types a temperature. Print Hot if it's over 25, Nice if it's over 15, and Cold otherwise.",
                            'temp = int(input("Temperature? "))\n# if / elif / else here\n',
                            'temp = int(input("Temperature? "))\nif temp > 25:\n    print("Hot")\nelif temp > 15:\n    print("Nice")\nelse:\n    print("Cold")',
                            [has("Hot", stdin=["30"]), has("Nice", stdin=["20"]), has("Cold", stdin=["5"]), has("Nice", stdin=["25"])],
                            [
                                "Check the biggest number first: if temp > 25:",
                                "Then elif temp > 15:, then else:.",
                                'The answer is:\nif temp > 25:\n    print("Hot")\nelif temp > 15:\n    print("Nice")\nelse:\n    print("Cold")',
                            ],
                            must=["elif", "else"],
                            wrong=['temp = int(input("Temperature? "))\nif temp > 15:\n    print("Nice")\nelif temp > 25:\n    print("Hot")\nelse:\n    print("Cold")'],
                        ),
                        predict(
                            'n = 50\nif n > 10:\n    print("A")\nelif n > 40:\n    print("B")\nelse:\n    print("C")',
                            ["B", "A\nB", "C"],
                            "50 > 10 is True, so A runs and the rest are skipped, even though 50 > 40 is also True.",
                            ["Which check comes first?", "Only the first True one runs."],
                        ),
                    ],
                ),
                lesson(
                    "if-and",
                    "and, or, not",
                    """
You can join conditions:

- and: True only if both sides are True.
- or: True if at least one side is True.
- not: flips True to False and False to True.
""",
                    """
and is strict: both checks must pass, like needing a ticket and a wristband to get in. or is relaxed: either one is enough, like paying with cash or card.
""",
                    'age = 14\nhas_ticket = True\nif age >= 12 and has_ticket:\n    print("Enjoy the movie")\nif age < 5 or age > 65:\n    print("Discount")',
                    "One and, one or.",
                    [
                        walk("if age >= 12 and has_ticket:", "Both are True, so the print runs."),
                        walk('print("Enjoy the movie")', "Runs."),
                        walk("if age < 5 or age > 65:", "Both sides are False for 14, so the discount line is skipped."),
                    ],
                    [
                        oops('x = 5\nif x > 1 and < 10:\n    print("ok")', "Each side of and needs its own full comparison: x > 1 and x < 10.", 'x = 5\nif x > 1 and x < 10:\n    print("ok")'),
                    ],
                    [
                        code(
                            "Fill in the blank so it prints Go only when both are True.",
                            'sunny = True\nwarm = True\nif sunny ___ warm:\n    print("Go to the beach")',
                            'sunny = True\nwarm = True\nif sunny and warm:\n    print("Go to the beach")',
                            [out("Go to the beach")],
                            [
                                "You need a word that means both.",
                                "Replace ___ with and.",
                                "The line is: if sunny and warm:",
                            ],
                            must=["and"],
                        ),
                        code(
                            "The checker types a day. Print Weekend if it is Saturday or Sunday, otherwise print School day.",
                            'day = input("Day? ")\n# Use or\n',
                            'day = input("Day? ")\nif day == "Saturday" or day == "Sunday":\n    print("Weekend")\nelse:\n    print("School day")',
                            [has("Weekend", stdin=["Saturday"]), has("Weekend", stdin=["Sunday"]), has("School day", stdin=["Monday"])],
                            [
                                'Compare day to "Saturday", and separately to "Sunday".',
                                'Join the two comparisons with or: day == "Saturday" or day == "Sunday"',
                                'The answer is:\nif day == "Saturday" or day == "Sunday":\n    print("Weekend")\nelse:\n    print("School day")',
                            ],
                            must=["or"],
                        ),
                        predict(
                            "a = True\nb = False\nprint(a and b)\nprint(a or b)\nprint(not b)",
                            ["True\nTrue\nFalse", "False\nFalse\nTrue", "True\nFalse\nTrue"],
                            "and needs both (False), or needs one (True), not flips False to True.",
                            ["and is True only if both are True.", "not b flips b."],
                        ),
                    ],
                ),
                checkpoint(
                    "if-check",
                    "Checkpoint: choices",
                    "Follow the conditions from the top. Only one path in an if/elif/else runs.",
                    [
                        predict('x = 4\nif x == 4:\n    print("yes")\nelse:\n    print("no")', ["no", "yes\nno", "4"], "x == 4 is True.", ["Is x equal to 4?", "Only one branch runs."]),
                        predict('t = 15\nif t > 20:\n    print("hot")\nelif t > 10:\n    print("warm")\nprint("end")', ["hot\nend", "end", "warm"], "15 isn't over 20, but it's over 10. Then end always prints.", ["Check each condition in order.", "The last line is not indented."]),
                        predict("print(3 > 1 and 2 > 5)", ["True", "3 > 1", "None"], "2 > 5 is False, so the whole and is False.", ["Is each side True?", "and needs both."]),
                    ],
                ),
            ],
        )
    ]
