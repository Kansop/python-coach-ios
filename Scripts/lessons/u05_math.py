from .dsl import ask, checkpoint, code, fix, lesson, oops, out, predict, term, unit, vals, walk


def units():
    return [
        unit(
            "math",
            "Math",
            "Add, multiply, divide, and more.",
            "plus.forwardslash.minus",
            [
                lesson(
                    "math-ops",
                    "The four operations",
                    """
Python is a great calculator. The symbols are:

+ add, - subtract, * multiply, / divide.

Multiply uses * (a star), not x. Divide uses / (a slash).
""",
                    """
Keyboards don't have a × or ÷ key, so coding languages use * and / instead. Python works out the math first, then print shows the answer.
""",
                    "print(7 + 3)\nprint(7 - 3)\nprint(7 * 3)\nprint(8 / 2)",
                    "Each line does one kind of math.",
                    [
                        walk("print(7 + 3)", "Adds: 10"),
                        walk("print(7 - 3)", "Subtracts: 4"),
                        walk("print(7 * 3)", "Multiplies: 21"),
                        walk("print(8 / 2)", "Divides: 4.0. Dividing with / always gives a decimal number."),
                    ],
                    [
                        oops("print(4 x 2)", "x isn't the times symbol in Python. Use *.", "print(4 * 2)"),
                        oops('print("4" + "2")', 'In quotes, these are text, so + joins them into 42 instead of adding.', "print(4 + 2)"),
                    ],
                    [
                        code(
                            "Fill in the blank with the multiply symbol so it prints 12.",
                            "print(3 ___ 4)",
                            "print(3 * 4)",
                            [out("12")],
                            [
                                "Multiply is a star symbol.",
                                "Replace ___ with *.",
                                "The answer is: print(3 * 4)",
                            ],
                            must=["*"],
                        ),
                        code(
                            "A pizza has 8 slices and 4 friends share it. Make slices = 8 and friends = 4, then print slices divided by friends.",
                            "slices = 8\nfriends = 4\n# Print slices divided by friends\n",
                            "slices = 8\nfriends = 4\nprint(slices / friends)",
                            [out("2.0")],
                            [
                                "Divide uses /.",
                                "Put slices / friends inside print.",
                                "The answer is: print(slices / friends)",
                            ],
                            must=["/", "slices", "friends"],
                            wrong=["print(2.0)"],
                        ),
                        predict(
                            "print(10 - 4 + 1)",
                            ["5", "10 - 4 + 1", "-4"],
                            "Python goes left to right here: 10 - 4 is 6, then 6 + 1 is 7.",
                            ["Do the first part first: 10 - 4.", "Then add 1."],
                        ),
                    ],
                    terms=[
                        term("operator", "A symbol that does math, like + or *.", "the buttons on a calculator."),
                    ],
                ),
                lesson(
                    "math-types",
                    "Whole numbers and decimals",
                    """
Python has two main kinds of numbers:

- int: a whole number, like 5 or -2.
- float: a number with a decimal point, like 2.5.

Dividing with / always gives a float, even 6 / 2, which is 3.0. If you want a whole number back, int() chops off the decimal part.
""",
                    """
Python keeps track of what type each value is. Whole numbers and decimals are stored differently. int(3.9) doesn't round, it just cuts off everything after the decimal point, so you get 3.
""",
                    "print(6 / 2)\nprint(int(6 / 2))\nprint(int(3.9))",
                    "Division gives a float. int() turns it into a whole number.",
                    [
                        walk("print(6 / 2)", "/ always gives a float: 3.0"),
                        walk("print(int(6 / 2))", "int() turns 3.0 into 3."),
                        walk("print(int(3.9))", "int() cuts off the .9, it doesn't round. You get 3."),
                    ],
                    [
                        oops("print(int(2.7))\nprint(\"that rounds\")", "int() doesn't round up. int(2.7) is 2. Use round(2.7) to round.", "print(round(2.7))\nprint(\"that rounds\")"),
                    ],
                    [
                        code(
                            "Fill in the blank so it prints the whole number 4, not 4.0.",
                            "print(___(8 / 2))",
                            "print(int(8 / 2))",
                            [out("4")],
                            [
                                "Which tool turns a float into a whole number?",
                                "Replace ___ with int.",
                                "The answer is: print(int(8 / 2))",
                            ],
                            must=["int"],
                            wrong=["print(8 / 2)"],
                        ),
                        code(
                            "price is 9.75. Make dollars hold the whole-number part of price, then print dollars.",
                            "price = 9.75\n# Make dollars here\n",
                            "price = 9.75\ndollars = int(price)\nprint(dollars)",
                            [vals("dollars", out="9")],
                            [
                                "int() keeps only the whole part.",
                                "dollars = int(price)",
                                "The answer is:\ndollars = int(price)\nprint(dollars)",
                            ],
                            must=["int"],
                            wrong=["dollars = 9\nprint(dollars)"],
                        ),
                        ask(
                            "Which of these is a float?",
                            "2.5",
                            ["2", "-7", "100"],
                            "A float has a decimal point. 2.5 does.",
                            ["Look for a decimal point.", "An int is a whole number."],
                        ),
                    ],
                    terms=[
                        term("int", "A whole number, like 4 or -10.", "counting people. You can't have half a person in line."),
                        term("float", "A number with a decimal point, like 1.5.", "measuring water. You can have 1.5 cups."),
                    ],
                ),
                lesson(
                    "math-parens",
                    "Which math goes first",
                    """
Python follows the same order as math class: * and / happen before + and -.

So 2 + 3 * 4 is 14, not 20. If you want the adding to happen first, use brackets: (2 + 3) * 4 is 20.
""",
                    """
Brackets say "do this part first." Python works out the inside of the brackets, then uses that answer in the rest of the math. When in doubt, add brackets. They make your meaning clear.
""",
                    "print(2 + 3 * 4)\nprint((2 + 3) * 4)",
                    "Same numbers, different order, different answers.",
                    [
                        walk("print(2 + 3 * 4)", "Multiply first: 3 * 4 is 12. Then 2 + 12 is 14."),
                        walk("print((2 + 3) * 4)", "Brackets first: 2 + 3 is 5. Then 5 * 4 is 20."),
                    ],
                    [
                        oops("a = 80\nb = 90\nprint(a + b / 2)", "To average, the adding must happen first. Without brackets, only b is divided.", "a = 80\nb = 90\nprint((a + b) / 2)"),
                    ],
                    [
                        code(
                            "Add brackets in the blank spots so the adding happens first. It should print 20.",
                            "print(___2 + 8___ * 2)",
                            "print((2 + 8) * 2)",
                            [out("20")],
                            [
                                "The first ___ needs an opening bracket (.",
                                "The second ___ needs a closing bracket ).",
                                "The answer is: print((2 + 8) * 2)",
                            ],
                            must=["("],
                        ),
                        code(
                            "Two test scores are 70 and 90. Print their average: add them, then divide by 2. It should print 80.0.",
                            "a = 70\nb = 90\n# Print the average\n",
                            "a = 70\nb = 90\nprint((a + b) / 2)",
                            [out("80.0")],
                            [
                                "Add a and b first, inside brackets.",
                                "Then divide that by 2.",
                                "The answer is: print((a + b) / 2)",
                            ],
                            must=["/"],
                            wrong=["a = 70\nb = 90\nprint(a + b / 2)", "print(80.0)"],
                        ),
                        predict(
                            "print(10 - 2 * 3)",
                            ["24", "10 - 6", "8"],
                            "Multiply first: 2 * 3 is 6. Then 10 - 6 is 4.",
                            ["Which happens first, * or -?", "Work out 2 * 3 before subtracting."],
                        ),
                    ],
                ),
                lesson(
                    "math-mod",
                    "Remainders",
                    """
Two more operators:

- // divides and keeps only the whole number. 7 // 2 is 3.
- % gives the remainder, what's left over. 7 % 2 is 1.

A neat trick: a number is even when number % 2 is 0.
""",
                    """
Think of sharing 7 sweets between 2 friends. Each friend gets 3 (that's 7 // 2), and 1 sweet is left over (that's 7 % 2). If nothing is left over, the number divides evenly.
""",
                    "sweets = 7\nprint(sweets // 2)\nprint(sweets % 2)\nprint(10 % 2)",
                    "Sharing sweets: how many each, and how many left over.",
                    [
                        walk("sweets = 7", "7 sweets to share between 2 friends."),
                        walk("print(sweets // 2)", "Each friend gets 3 whole sweets."),
                        walk("print(sweets % 2)", "1 sweet is left over."),
                        walk("print(10 % 2)", "10 shares evenly, so the remainder is 0. 10 is even."),
                    ],
                    [
                        oops("print(7 / 2)\nprint(\"each\")", "/ gives 3.5. To get whole sweets each, use //.", "print(7 // 2)\nprint(\"each\")"),
                    ],
                    [
                        code(
                            "Fill in the blank with the remainder symbol, so it prints what's left when 10 is shared by 3.",
                            "print(10 ___ 3)",
                            "print(10 % 3)",
                            [out("1")],
                            [
                                "The remainder symbol looks like a percent sign.",
                                "Replace ___ with %.",
                                "The answer is: print(10 % 3)",
                            ],
                            must=["%"],
                        ),
                        code(
                            "There are 23 players and teams of 5. Print how many full teams you can make (use //), then on the next line how many players are left over (use %).",
                            "players = 23\n# Two print lines\n",
                            "players = 23\nprint(players // 5)\nprint(players % 5)",
                            [out("4\n3")],
                            [
                                "Full teams: players // 5",
                                "Left over: players % 5",
                                "The answer is:\nprint(players // 5)\nprint(players % 5)",
                            ],
                            must=["//", "%"],
                            wrong=["print(4)\nprint(3)"],
                        ),
                        predict(
                            "print(9 % 2, 8 % 2)",
                            ["0 1", "4 4", "4.5 4.0"],
                            "9 is odd, so it has 1 left over. 8 is even, so 0 is left over.",
                            ["% gives the remainder.", "Is 9 even or odd? What about 8?"],
                        ),
                    ],
                    terms=[
                        term("remainder", "What's left over after sharing evenly.", "the last slice of pizza nobody gets."),
                    ],
                ),
                lesson(
                    "math-update",
                    "Shortcuts: += and -=",
                    """
Changing a variable by a little is so common that Python has shortcuts:

- score += 5 means score = score + 5
- lives -= 1 means lives = lives - 1

They do the same thing. The shortcut is just shorter to type.
""",
                    """
+= reads the current value, adds to it, and saves the result back in the same variable, in one step. Games use it all the time: adding points, losing lives, counting moves.
""",
                    "lives = 3\nlives -= 1\nprint(lives)\nscore = 0\nscore += 10\nscore += 10\nprint(score)",
                    "Losing a life, then scoring twice.",
                    [
                        walk("lives = 3", "Start with 3 lives."),
                        walk("lives -= 1", "Same as lives = lives - 1. Now 2."),
                        walk("print(lives)", "Shows 2."),
                        walk("score += 10", "score goes from 0 to 10, then the next line takes it to 20."),
                        walk("print(score)", "Shows 20."),
                    ],
                    [
                        oops("score = 5\nscore =+ 2\nprint(score)", "=+ is backwards. It sets score to +2. The shortcut is +=.", "score = 5\nscore += 2\nprint(score)"),
                    ],
                    [
                        code(
                            "Fill in the blank with the shortcut that adds 1 to steps.",
                            "steps = 9\nsteps ___ 1\nprint(steps)",
                            "steps = 9\nsteps += 1\nprint(steps)",
                            [vals("steps", out="10")],
                            [
                                "The add shortcut is a plus sign and an equals sign.",
                                "Replace ___ with +=.",
                                "The answer is: steps += 1",
                            ],
                            must=["+="],
                        ),
                        code(
                            "health starts at 100. Use -= to take away 30, then print health.",
                            "health = 100\n# Take away 30 with -=\n\nprint(health)",
                            "health = 100\nhealth -= 30\nprint(health)",
                            [vals("health", out="70")],
                            [
                                "Use the -= shortcut.",
                                "health -= 30",
                                "The answer is:\nhealth = 100\nhealth -= 30\nprint(health)",
                            ],
                            must=["-="],
                            wrong=["health = 70\nprint(health)"],
                        ),
                        predict(
                            "x = 10\nx += 5\nx -= 3\nprint(x)",
                            ["10", "15", "18"],
                            "10, then 15, then 12.",
                            ["Do each line in order.", "Add 5, then take away 3."],
                        ),
                    ],
                ),
                checkpoint(
                    "math-check",
                    "Checkpoint: math",
                    "Work out each one in your head. Remember which operations go first.",
                    [
                        predict("print(3 + 2 * 2)", ["10", "3 + 4", "12"], "2 * 2 is 4 first, then 3 + 4 is 7.", ["* goes before +.", "Work out 2 * 2 first."]),
                        predict("print(9 / 3)", ["3", "3.3", "0"], "/ always gives a float: 3.0", ["Does / give a whole number or a decimal?", "Think about what kind of number / gives."]),
                        predict("n = 4\nn += n\nprint(n % 3)", ["1", "0", "8"], "n becomes 8. 8 shared by 3 leaves 2.", ["n += n doubles n.", "What's left over when 8 is shared by 3?"]),
                    ],
                ),
            ],
        )
    ]
