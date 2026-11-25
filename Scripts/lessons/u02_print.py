from .dsl import ask, checkpoint, code, fix, has, lesson, oops, out, predict, term, unit, walk


def units():
    return [
        unit(
            "print",
            "Printing",
            "Make Python show words and numbers.",
            "text.bubble.fill",
            [
                lesson(
                    "print-hello",
                    "Say hello",
                    """
print() is how Python shows something on the screen.

You write the word print, then round brackets ( ), and inside the brackets you put what to show. Words go inside quote marks, like "Hello".
""",
                    """
The quote marks tell Python "this part is text, not an instruction." Without them, Python would try to understand the words as code. With them, it shows the words exactly as you typed them.
""",
                    'print("Hello, world!")',
                    "This is the most famous first program in the world. Run it, then read what each part does.",
                    [
                        walk('print("Hello, world!")', 'print is the instruction. The brackets hold what to show. The quotes mark "Hello, world!" as text.'),
                    ],
                    [
                        oops("print(Hello)", "Without quotes, Python thinks Hello is a name it should know, and it doesn't. You get a NameError.", 'print("Hello")'),
                        oops('Print("Hello")', "Capital P. Python cares about capital letters, and the instruction is print, all lowercase.", 'print("Hello")'),
                    ],
                    [
                        code(
                            "Fill in the blank so the program prints: I am learning Python",
                            'print("___")',
                            'print("I am learning Python")',
                            [out("I am learning Python")],
                            [
                                "Replace the ___ with the sentence. Keep the quotes around it.",
                                "Match the capital I and the capital P, and put one space between words.",
                                'The answer is: print("I am learning Python")',
                            ],
                            wrong=['print("i am learning python")', 'print("I am learning")'],
                        ),
                        code(
                            "Now write the whole line yourself. Print: Python is fun",
                            "# Type your print line below this note\n",
                            'print("Python is fun")',
                            [out("Python is fun")],
                            [
                                "Start with print, then an opening bracket (.",
                                "Inside the brackets, put the words between quote marks.",
                                'The answer is: print("Python is fun")',
                            ],
                            must=["print"],
                        ),
                        fix(
                            "This line has a bug. Fix it so it prints: Ready to code",
                            "print(Ready to code)",
                            'print("Ready to code")',
                            [out("Ready to code")],
                            [
                                "Words you want to show need something around them.",
                                "Put a quote mark right after ( and another right before ).",
                                'The fixed line is: print("Ready to code")',
                            ],
                        ),
                    ],
                    terms=[
                        term("print()", "An instruction that shows something on the screen.", "a loudspeaker. Whatever you put inside, it says out loud."),
                        term("string", 'Text inside quote marks, like "Hello". Coders call text a string.', "beads on a string: letters lined up one after another."),
                    ],
                ),
                lesson(
                    "print-two-lines",
                    "One line at a time",
                    """
A program can have many lines. Python runs them in order, from the top to the bottom.

Each print() shows its text on a new line. So three print lines make three lines of output.
""",
                    """
After print shows its text, it moves to the next line, like pressing Enter when you type. That's why the next print starts on a fresh line.
""",
                    'print("Line one")\nprint("Line two")\nprint("Line three")',
                    "Three print lines in a row. Run it and watch them come out in order.",
                    [
                        walk('print("Line one")', "Runs first, because it's at the top."),
                        walk('print("Line two")', "Runs second, on a new line."),
                        walk('print("Line three")', "Runs last. Then the program is done."),
                    ],
                    [
                        oops('print("Line one") print("Line two")', "Two instructions squeezed onto one line confuse Python. Give each print its own line.", 'print("Line one")\nprint("Line two")'),
                    ],
                    [
                        code(
                            "Fill in both blanks so it prints Python on the first line and Coach on the second.",
                            'print("___")\nprint("___")',
                            'print("Python")\nprint("Coach")',
                            [out("Python\nCoach")],
                            [
                                "The first line should show Python.",
                                "The second line should show Coach.",
                                'The answer is:\nprint("Python")\nprint("Coach")',
                            ],
                            wrong=['print("Coach")\nprint("Python")', 'print("Python Coach")'],
                        ),
                        code(
                            "Write a 3-line countdown. Print 3, then 2, then 1, each on its own line. Use text in quotes for now.",
                            "# Three print lines, one under the other\n",
                            'print("3")\nprint("2")\nprint("1")',
                            [out("3\n2\n1")],
                            [
                                "You need three print lines.",
                                'Start with print("3") on the first line.',
                                'The answer is:\nprint("3")\nprint("2")\nprint("1")',
                            ],
                            wrong=['print("1")\nprint("2")\nprint("3")', 'print("3 2 1")'],
                        ),
                        predict(
                            'print("Top")\nprint("Middle")\nprint("Bottom")',
                            ["Bottom\nMiddle\nTop", "Top Middle Bottom", "Top\nBottom"],
                            "Python runs the lines from the top down, and each print starts a new line.",
                            ["Which line does Python run first?", "Each print shows its text on its own line."],
                        ),
                    ],
                    terms=[
                        term("line of code", "One instruction, on its own line.", "one step in a recipe."),
                    ],
                ),
                lesson(
                    "print-mix",
                    "Words and numbers",
                    """
Numbers don't need quotes. print(7) shows 7.

You can show several things with one print by putting commas between them. Python puts a space between each part for you.
""",
                    """
Quotes are only for text. A number on its own is already something Python understands, so it doesn't need them. The comma means "and then this too," and print joins all the parts on one line with spaces.
""",
                    'print("Score:", 12)\nprint("Lives:", 3)',
                    "Each print mixes some text and a number, joined by a comma.",
                    [
                        walk('print("Score:", 12)', 'The text "Score:" comes first. The comma adds 12 after it, with a space. Output: Score: 12'),
                        walk('print("Lives:", 3)', "Same idea on the next line. Output: Lives: 3"),
                    ],
                    [
                        oops('print("Score:" 12)', "The comma is missing between the parts. Python needs it to know where one part ends.", 'print("Score:", 12)'),
                    ],
                    [
                        code(
                            "Fill in the blank with the number 3, so it prints: Level 3",
                            'print("Level", ___)',
                            'print("Level", 3)',
                            [out("Level 3")],
                            [
                                "Replace ___ with the number 3.",
                                "Numbers don't need quotes.",
                                'The answer is: print("Level", 3)',
                            ],
                            wrong=['print("Level", 4)'],
                        ),
                        code(
                            "Write one print that shows: Age: 13. Use text, a comma, then the number.",
                            "# One print line with a comma\n",
                            'print("Age:", 13)',
                            [out("Age: 13")],
                            [
                                'The text part is "Age:" in quotes.',
                                "After the text, type a comma, then 13.",
                                'The answer is: print("Age:", 13)',
                            ],
                            must=[","],
                            wrong=['print("Age: 13")'],
                        ),
                        predict(
                            'print("I have", 2, "cats")',
                            ["I have2cats", "I have, 2, cats", '"I have", 2, "cats"'],
                            "print puts one space between each part, and the commas themselves are not shown.",
                            ["Commas separate the parts. They don't get printed.", "print adds a space between parts."],
                        ),
                    ],
                    terms=[
                        term("number", "A value like 7 or 3.5. Python can do math with numbers.", "the numbers on a calculator."),
                    ],
                ),
                lesson(
                    "print-comments",
                    "Notes for humans",
                    """
A comment is a note in your code for people, not for Python. It starts with a # sign.

Python skips everything from the # to the end of that line. Coders use comments to explain what the code does.
""",
                    """
When Python reads a line and sees #, it stops reading that line and moves on. That makes comments safe: you can write anything after a # and it never changes what the program does.
""",
                    '# This program greets the player\nprint("Welcome!")  # shows a welcome',
                    "One comment on its own line, and one after some code.",
                    [
                        walk("# This program greets the player", "A comment line. Python skips it completely."),
                        walk('print("Welcome!")  # shows a welcome', "The print runs. The part from # onward is skipped."),
                    ],
                    [
                        oops("This prints a greeting\nprint(\"Hi\")", "Without the #, Python tries to run your note as code and gets confused.", "# This prints a greeting\nprint(\"Hi\")"),
                    ],
                    [
                        code(
                            "Add a comment on the first line (start it with #). Keep the print so it still shows: Hi",
                            '___\nprint("Hi")',
                            '# Say hi\nprint("Hi")',
                            [out("Hi")],
                            [
                                "Replace the ___ with a note that starts with #.",
                                "Any words can go after the #, like: # Say hi",
                                'The answer is:\n# Say hi\nprint("Hi")',
                            ],
                            must=["#"],
                            wrong=['print("Hi")'],
                        ),
                        predict(
                            '# print("A")\nprint("B")\n# print("C")',
                            ["A\nB\nC", "A\nC", "B\nC"],
                            "Lines that start with # are skipped, so only the middle line runs.",
                            ["Which lines start with #?", "Python skips any line that starts with #."],
                        ),
                        fix(
                            "Someone wrote a note without a #. Fix it so the program runs and prints: Done",
                            'Print the word Done\nprint("Done")',
                            '# Print the word Done\nprint("Done")',
                            [out("Done")],
                            [
                                "The first line is meant to be a note, not code.",
                                "Put a # at the start of the first line.",
                                'The fixed code is:\n# Print the word Done\nprint("Done")',
                            ],
                            must=["#"],
                        ),
                    ],
                    terms=[
                        term("comment", "A note in code that starts with #. Python ignores it.", "a sticky note on your homework. It's for you, not the teacher."),
                    ],
                ),
                checkpoint(
                    "print-check",
                    "Checkpoint: printing",
                    "Time to check what you know. Read each program like Python does, one line at a time, and pick what it prints.",
                    [
                        predict(
                            'print("Hi")\nprint("there")',
                            ["Hi there", "there\nHi", "Hithere"],
                            "Two print lines make two lines of output.",
                            ["How many print lines are there?", "Each print starts a new line."],
                        ),
                        predict(
                            'print("Total:", 5)',
                            ["Total:5", "Total: , 5", "Total"],
                            "The comma joins the parts with one space.",
                            ["What does a comma do inside print?", "print adds a space between parts."],
                        ),
                        predict(
                            'print("one")  # print("two")',
                            ["one\ntwo", "two", "one two"],
                            "Everything after # is a comment, so only one is shown.",
                            ["Where does the comment start?", "Python skips the rest of the line after #."],
                        ),
                    ],
                ),
            ],
        )
    ]
