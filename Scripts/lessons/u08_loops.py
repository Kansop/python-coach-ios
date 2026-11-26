from .dsl import ask, checkpoint, code, fix, has, lesson, oops, out, predict, term, unit, vals, walk


def units():
    return [
        unit(
            "loops",
            "Loops",
            "Repeat code without copying it.",
            "repeat",
            [
                lesson(
                    "loop-for",
                    "Repeat with for",
                    """
A loop repeats code. A for loop with range() repeats a set number of times:

for i in range(3):
    print("Hi")

prints Hi three times. Like if, the for line ends with a colon, and the lines to repeat are indented.
""",
                    """
range(3) makes the numbers 0, 1, 2. The for loop takes them one at a time and puts each in the variable i, then runs the indented lines. Three numbers means three times around. One trip around a loop is called a lap, or an iteration.
""",
                    'for i in range(3):\n    print("Lap", i)\nprint("Finished")',
                    "The indented line runs three times. The last line runs once, after the loop.",
                    [
                        walk("for i in range(3):", "range(3) gives 0, 1, 2. Each lap, i holds the next one."),
                        walk('print("Lap", i)', "Runs once per lap: Lap 0, Lap 1, Lap 2."),
                        walk('print("Finished")', "Not indented, so it runs once, after the loop ends."),
                    ],
                    [
                        oops('for i in range(3):\nprint("Hi")', "The line to repeat needs 4 spaces in front.", 'for i in range(3):\n    print("Hi")'),
                        oops('for i in range(3)\n    print("Hi")', "The for line needs a colon at the end.", 'for i in range(3):\n    print("Hi")'),
                    ],
                    [
                        code(
                            "Fill in the blank so the loop prints Go 4 times.",
                            'for i in range(___):\n    print("Go")',
                            'for i in range(4):\n    print("Go")',
                            [out("Go\nGo\nGo\nGo")],
                            [
                                "The number in range() is how many laps.",
                                "Replace ___ with 4.",
                                "The first line is: for i in range(4):",
                            ],
                            must=["for", "range"],
                            wrong=['for i in range(3):\n    print("Go")'],
                        ),
                        code(
                            "Use a for loop to print Python 5 times. Don't write 5 print lines.",
                            "# Write a for loop\n",
                            'for i in range(5):\n    print("Python")',
                            [out("Python\nPython\nPython\nPython\nPython")],
                            [
                                "Start with: for i in range(5):",
                                "Indent the print by 4 spaces.",
                                'The answer is:\nfor i in range(5):\n    print("Python")',
                            ],
                            must=["for", "range"],
                            wrong=['print("Python")\nprint("Python")\nprint("Python")\nprint("Python")\nprint("Python")'],
                        ),
                        predict(
                            "for n in range(3):\n    print(n)",
                            ["1\n2\n3", "0\n1\n2\n3", "3"],
                            "range(3) starts at 0 and stops before 3: 0, 1, 2.",
                            ["What number does range start at?", "range stops before the number you give it."],
                        ),
                    ],
                    terms=[
                        term("loop", "Code that repeats.", "running laps around a track."),
                        term("range()", "Makes a row of numbers, starting at 0. range(3) is 0, 1, 2.", "the numbers on a ruler, starting at 0."),
                    ],
                ),
                lesson(
                    "loop-range",
                    "Start, stop, and step",
                    """
range() can take up to three numbers: range(start, stop, step).

- range(1, 6) is 1, 2, 3, 4, 5. It stops before 6.
- range(0, 10, 2) counts by twos: 0, 2, 4, 6, 8.
- range(5, 0, -1) counts down: 5, 4, 3, 2, 1.
""",
                    """
The stop number is never included. That feels odd at first, but it means range(1, 6) gives exactly 6 - 1 = 5 numbers. The step is how big each jump is, and a negative step counts backward.
""",
                    "for n in range(1, 4):\n    print(n)\nfor n in range(10, 0, -5):\n    print(n)",
                    "Counting up from 1, then counting down by fives.",
                    [
                        walk("for n in range(1, 4):", "Starts at 1, stops before 4: 1, 2, 3."),
                        walk("for n in range(10, 0, -5):", "Starts at 10, jumps by -5, stops before 0: 10, 5."),
                    ],
                    [
                        oops("for n in range(1, 5):\n    print(n)\nprint(\"that's 1 to 5?\")", "range(1, 5) stops before 5, so it's 1 to 4. Use range(1, 6) to include 5.", "for n in range(1, 6):\n    print(n)\nprint(\"that's 1 to 5?\")"),
                    ],
                    [
                        code(
                            "Fill in the blank so it prints 1 to 5.",
                            "for n in range(1, ___):\n    print(n)",
                            "for n in range(1, 6):\n    print(n)",
                            [out("1\n2\n3\n4\n5")],
                            [
                                "The stop number is not included.",
                                "To include 5, stop at 6.",
                                "The first line is: for n in range(1, 6):",
                            ],
                            must=["range"],
                            wrong=["for n in range(1, 5):\n    print(n)"],
                        ),
                        code(
                            "Count down for a rocket: print 3, 2, 1 with a loop, then print Liftoff! after the loop.",
                            "# Countdown loop, then Liftoff!\n",
                            'for n in range(3, 0, -1):\n    print(n)\nprint("Liftoff!")',
                            [out("3\n2\n1\nLiftoff!")],
                            [
                                "Use range(3, 0, -1). The -1 counts down.",
                                "Put the Liftoff! print after the loop, with no spaces in front.",
                                'The answer is:\nfor n in range(3, 0, -1):\n    print(n)\nprint("Liftoff!")',
                            ],
                            must=["for", "range"],
                            wrong=['for n in range(3, 0, -1):\n    print(n)\n    print("Liftoff!")'],
                        ),
                        predict(
                            "for n in range(2, 9, 3):\n    print(n)",
                            ["2\n3\n4\n5\n6\n7\n8", "3\n6\n9", "2\n5\n8\n9"],
                            "Start at 2, add 3 each time: 2, 5, 8. 11 would be past 9, so it stops.",
                            ["What's the first number?", "Add the step each time, and stop before 9."],
                        ),
                    ],
                ),
                lesson(
                    "loop-total",
                    "Adding up in a loop",
                    """
A loop can build up a total. Make a variable before the loop that starts at 0. Each lap, add to it. After the loop, it holds the total.

This pattern is used everywhere: scores, money, counting things.
""",
                    """
The total lives outside the loop, so it remembers its value from lap to lap. If you set total = 0 inside the loop, it would be reset every lap and you'd lose the count.
""",
                    "total = 0\nfor n in range(1, 4):\n    total += n\nprint(total)",
                    "Adding 1 + 2 + 3 with a loop.",
                    [
                        walk("total = 0", "Start the total at 0, before the loop."),
                        walk("for n in range(1, 4):", "n will be 1, then 2, then 3."),
                        walk("total += n", "Each lap adds n: 0 + 1 = 1, then 1 + 2 = 3, then 3 + 3 = 6."),
                        walk("print(total)", "After the loop, shows 6."),
                    ],
                    [
                        oops("for n in range(1, 4):\n    total = 0\n    total += n\nprint(total)", "total = 0 is inside the loop, so it resets every lap. You end up with only the last number. Move it above the loop.", "total = 0\nfor n in range(1, 4):\n    total += n\nprint(total)"),
                        oops("total = 0\nfor n in range(1, 4):\n    total += n\n    print(total)", "The print is inside the loop, so it shows the total every lap. Unindent it to print once at the end.", "total = 0\nfor n in range(1, 4):\n    total += n\nprint(total)"),
                    ],
                    [
                        code(
                            "Fill in the blank so the loop adds each n to total. It should print 10.",
                            "total = 0\nfor n in range(1, 5):\n    total ___ n\nprint(total)",
                            "total = 0\nfor n in range(1, 5):\n    total += n\nprint(total)",
                            [vals("total", out="10")],
                            [
                                "Use the add shortcut.",
                                "Replace ___ with +=.",
                                "The line is: total += n",
                            ],
                            must=["for"],
                        ),
                        code(
                            "Add up all the numbers from 1 to 10 with a loop and print the total. It should print 55.",
                            "total = 0\n# Loop from 1 to 10, then print\n",
                            "total = 0\nfor n in range(1, 11):\n    total += n\nprint(total)",
                            [vals("total", out="55")],
                            [
                                "range(1, 11) gives 1 to 10.",
                                "Inside the loop: total += n. After the loop: print(total).",
                                "The answer is:\ntotal = 0\nfor n in range(1, 11):\n    total += n\nprint(total)",
                            ],
                            must=["for"],
                            wrong=["total = 55\nprint(total)", "total = 0\nfor n in range(1, 10):\n    total += n\nprint(total)"],
                        ),
                        code(
                            "Count how many numbers from 1 to 20 are even. Add 1 to count whenever n % 2 == 0. Replace the word pass with your if. (pass means do nothing. It keeps the loop from being empty.)",
                            "count = 0\nfor n in range(1, 21):\n    # add 1 to count when n is even\n    pass\nprint(count)",
                            "count = 0\nfor n in range(1, 21):\n    if n % 2 == 0:\n        count += 1\nprint(count)",
                            [vals("count", out="10")],
                            [
                                "Inside the loop, use an if to check n % 2 == 0.",
                                "Inside that if, add 1: count += 1. That line needs 8 spaces.",
                                "The loop body is:\n    if n % 2 == 0:\n        count += 1",
                            ],
                            must=["if", "%"],
                            wrong=["count = 10\nprint(count)"],
                        ),
                    ],
                    terms=[
                        term("total (accumulator)", "A variable that collects a running total as a loop goes.", "a piggy bank. Each lap drops a coin in."),
                    ],
                ),
                lesson(
                    "loop-letters",
                    "Looping over text",
                    """
A for loop can walk through a string one character at a time:

for letter in "cat":
    print(letter)

prints c, a, t on separate lines.
""",
                    """
A string is a row of characters, so for can hand them out one by one. Each lap, the loop variable holds the next character. You don't need range() or positions for this.
""",
                    'word = "hey"\nfor letter in word:\n    print(letter.upper())',
                    "Each letter, one at a time, in capitals.",
                    [
                        walk('word = "hey"', "Three letters: h, e, y."),
                        walk("for letter in word:", "Each lap, letter holds the next character."),
                        walk("print(letter.upper())", "Shows H, then E, then Y."),
                    ],
                    [
                        oops('for letter in "hi":\n    print("letter")', 'Quotes around letter print the word letter every lap. Leave the quotes off.', 'for letter in "hi":\n    print(letter)'),
                    ],
                    [
                        code(
                            "Fill in the blank so the loop goes through the word.",
                            'word = "dog"\nfor ch in ___:\n    print(ch)',
                            'word = "dog"\nfor ch in word:\n    print(ch)',
                            [out("d\no\ng")],
                            [
                                "The loop needs something to walk through.",
                                "Replace ___ with word.",
                                "The line is: for ch in word:",
                            ],
                            must=["for"],
                        ),
                        code(
                            'Count the letter a in "banana" with a loop. Print the count. It should print 3.',
                            'word = "banana"\ncount = 0\n# Loop over word\n\nprint(count)',
                            'word = "banana"\ncount = 0\nfor ch in word:\n    if ch == "a":\n        count += 1\nprint(count)',
                            [vals("count", out="3")],
                            [
                                "Loop with: for ch in word:",
                                'Inside the loop, if ch == "a": then count += 1.',
                                'The loop is:\nfor ch in word:\n    if ch == "a":\n        count += 1',
                            ],
                            must=["for", "if"],
                            wrong=['word = "banana"\ncount = 3\nprint(count)'],
                        ),
                        predict(
                            'for c in "abc":\n    print(c * 2)',
                            ["abcabc", "a\nb\nc", "2\n2\n2"],
                            "Each letter is repeated twice: aa, bb, cc.",
                            ["What does * 2 do to a string?", "The loop runs once per letter."],
                        ),
                    ],
                ),
                lesson(
                    "loop-while",
                    "While loops",
                    """
A while loop repeats as long as its condition is True:

while count < 3:
    ...

Something inside the loop must change, so the condition eventually becomes False. Otherwise the loop never ends. That's called an infinite loop. If it happens here, the app stops it and tells you.
""",
                    """
Before each lap, Python checks the condition. True means do another lap. False means stop and move on. It's like a game that keeps going while you still have lives.
""",
                    "count = 1\nwhile count <= 3:\n    print(count)\n    count += 1\nprint(\"Done\")",
                    "Counting to 3 with while.",
                    [
                        walk("count = 1", "Start at 1."),
                        walk("while count <= 3:", "Check: is count at most 3? If yes, do a lap."),
                        walk("print(count)", "Show the current count."),
                        walk("count += 1", "Change count, so the loop can end."),
                        walk('print("Done")', "When count reaches 4, the check is False and the loop ends."),
                    ],
                    [
                        oops("n = 1\nwhile n < 3:\n    print(n)\nprint(\"end\")", "Nothing changes n, so n < 3 is True forever. Add n += 1 inside the loop.", "n = 1\nwhile n < 3:\n    print(n)\n    n += 1\nprint(\"end\")"),
                    ],
                    [
                        code(
                            "Fill in the blank so the loop counts up and ends.",
                            "n = 0\nwhile n < 3:\n    print(n)\n    n ___ 1",
                            "n = 0\nwhile n < 3:\n    print(n)\n    n += 1",
                            [out("0\n1\n2")],
                            [
                                "n needs to grow each lap.",
                                "Replace ___ with +=.",
                                "The last line is: n += 1",
                            ],
                            must=["while"],
                        ),
                        fix(
                            "This loop never ends. Press Run to see the explainer, then fix it so it prints 5, 4, 3, 2, 1.",
                            "n = 5\nwhile n > 0:\n    print(n)",
                            "n = 5\nwhile n > 0:\n    print(n)\n    n -= 1",
                            [out("5\n4\n3\n2\n1")],
                            [
                                "Something inside the loop has to change n.",
                                "n should get smaller each lap.",
                                "Add this line inside the loop: n -= 1",
                            ],
                            must=["while"],
                        ),
                        code(
                            "Double money until it is at least 100. Start money at 1. Each lap, double it with money *= 2. Print money after the loop. It should print 128.",
                            "money = 1\n# while money is less than 100, double it\n\nprint(money)",
                            "money = 1\nwhile money < 100:\n    money *= 2\nprint(money)",
                            [vals("money", out="128")],
                            [
                                "The condition is money < 100.",
                                "Inside the loop: money *= 2.",
                                "The answer is:\nmoney = 1\nwhile money < 100:\n    money *= 2\nprint(money)",
                            ],
                            must=["while"],
                            wrong=["money = 128\nprint(money)"],
                        ),
                    ],
                    terms=[
                        term("while loop", "Repeats as long as a condition is True.", "eating chips while there are still chips in the bag."),
                        term("infinite loop", "A loop that never stops because its condition never becomes False.", "a song stuck on repeat forever."),
                    ],
                ),
                checkpoint(
                    "loop-check",
                    "Checkpoint: loops",
                    "Trace each loop lap by lap. Keep track of the variable each time around.",
                    [
                        predict('for i in range(2):\n    print("hi")', ["hi", "hi\nhi\nhi", "0\n1"], "range(2) means 2 laps.", ["How many laps does range(2) make?", "The print doesn't use i."]),
                        predict("t = 0\nfor n in range(3):\n    t += n\nprint(t)", ["6", "0\n1\n3", "2"], "0 + 0 + 1 + 2 = 3.", ["range(3) is 0, 1, 2.", "Add them up."]),
                        predict("n = 10\nwhile n > 6:\n    n -= 2\nprint(n)", ["8", "10", "4"], "10, 8, 6. When n is 6 the check fails, so it prints 6.", ["Check before each lap.", "Is 6 > 6?"]),
                    ],
                ),
            ],
        )
    ]
