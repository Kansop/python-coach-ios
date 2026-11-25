from .dsl import ask, code, fix, lesson, oops, out, predict, term, unit, walk


def units():
    return [
        unit(
            "start",
            "Start here",
            "What coding is and how this app works.",
            "flag.fill",
            [
                lesson(
                    "start-what",
                    "What is coding?",
                    """
Coding means writing instructions for a computer.

A computer can't guess what you want. It only does exactly what the instructions say, one at a time, from the top down. Your job as a coder is to write those instructions clearly.

In this app you'll write instructions in a language called Python. You type them, press Run, and the computer follows them right away.
""",
                    """
A computer is very fast but very literal. It doesn't understand "you know what I mean." That's why code has exact spelling and punctuation rules. Once you learn the rules, the computer does exactly what you tell it, every single time.
""",
                    'print("Hello!")\nprint("I am a program.")',
                    "Here's a tiny program. It has two instructions. Press Run the example to watch the computer follow them in order.",
                    [
                        walk('print("Hello!")', "The first instruction. print means show this on the screen. The computer shows Hello!"),
                        walk('print("I am a program.")', "The second instruction runs next. The computer shows I am a program. on a new line."),
                    ],
                    [],
                    [
                        ask(
                            "In what order does the computer follow a program's instructions?",
                            "From the top line down, one at a time",
                            ["In any order it likes", "From the bottom line up", "Only the last line"],
                            "Right. Python starts at the top and works its way down, one line at a time.",
                            ["Think about how you read a recipe card.", "The example printed Hello! first, then the second line."],
                        ),
                        predict(
                            'print("Ready")\nprint("Set")\nprint("Go")',
                            ["Go\nSet\nReady", "Ready Set Go", "Ready"],
                            "Each line runs in order from the top, and each print shows its text on a new line.",
                            ["Start at the top line. What does it show?", "Every print makes its own line of output."],
                        ),
                        code(
                            "Your first code. The starter has a blank: ___. Replace the three underscores with the word Hi, then press Run my code.",
                            'print("___")',
                            'print("Hi")',
                            [out("Hi")],
                            [
                                "Tap the editor and delete the three underscores ___.",
                                "Type Hi where the underscores were. Keep the quote marks on both sides.",
                                'The finished line is: print("Hi")',
                            ],
                            wrong=['print("hi")', 'print("Hi!")'],
                        ),
                    ],
                    terms=[
                        term("code", "Instructions written for a computer.", "a recipe. Each line tells the cook one thing to do."),
                        term("program", "A set of instructions that does a job, like a game, a calculator, or a chat bot.", "a whole recipe card, from the first step to the last."),
                        term("Python", "One of the most popular coding languages. Its instructions read a lot like English.", "a language, like Spanish or French, but for talking to computers."),
                    ],
                ),
                lesson(
                    "start-app",
                    "How this app works",
                    """
Every lesson has the same three parts:

1. Learn. You read about one new idea. New words are explained first.
2. Example. You see real code, press Run, and read what each line does.
3. Practice. You try it yourself in two or three small steps. The first one is the easiest.

Some practice starts with a blank like ___. Replace it with your answer. Stuck? Tap Need a hint. Hints open one at a time, and the last one shows the answer, so you're never stuck for long.
""",
                    """
You learn coding by typing it, not only by reading it. Typing the code yourself, and fixing it when it's wrong, is what makes it stick. That's why every lesson ends with practice.
""",
                    'print("The output box shows what your program prints.")',
                    "When you press Run, anything your program prints shows up in the dark Output box. Try it.",
                    [
                        walk('print("The output box shows what your program prints.")', "print sends this sentence to the Output box."),
                    ],
                    [],
                    [
                        ask(
                            "A starter says print(\"___\"). What should you do with the ___?",
                            "Replace it with your answer",
                            ["Leave it there", "Delete the whole line", "Add more underscores"],
                            "Yes. The ___ is a blank to fill in, like a blank on a worksheet.",
                            ["The underscores mark a spot that's missing something.", "Think of a fill-in-the-blank question on a worksheet."],
                        ),
                        code(
                            "Fill in the blank so the program prints: I can write code",
                            'print("I can ___ code")',
                            'print("I can write code")',
                            [out("I can write code")],
                            [
                                "Only the ___ needs to change. The rest is already right.",
                                "Replace ___ with the word write.",
                                'The finished line is: print("I can write code")',
                            ],
                            wrong=['print("I can code")', 'print("I can Write code")'],
                        ),
                        ask(
                            "You're stuck on a practice. What can you do?",
                            "Open the hints one at a time",
                            ["Give up on the lesson", "Close the app", "Type random letters"],
                            "Hints are there to help. The first ones give a nudge, and the last one shows the answer.",
                            ["Look for the lightbulb button.", "It says Need a hint?"],
                        ),
                    ],
                    terms=[
                        term("run", "Telling the computer to follow your code now.", "pressing play on a song."),
                        term("output", "What your program shows when it runs.", "the words that come out of a speaker when you press play."),
                    ],
                ),
                lesson(
                    "start-errors",
                    "Errors are clues",
                    """
Sometimes Python can't follow your code, so it stops and shows an error. That's normal. Every coder sees errors every day, even experts.

An error is a clue. It tells you what confused Python and which line it was on. This app explains each error in plain words and points at the line.

A mistake in code is called a bug. Finding and fixing it is called debugging.
""",
                    """
Python reads your code very carefully. If something is missing, like a closing quote or bracket, it would rather stop and tell you than guess wrong. A clear error now saves you from a confusing problem later.
""",
                    'print("No errors here")',
                    "This code works. Below it you'll see a common mistake and how to fix it.",
                    [
                        walk('print("No errors here")', "The quote marks and the brackets each come in pairs, so Python can read it."),
                    ],
                    [
                        oops('print("Oops"', "The closing bracket ) is missing. Brackets come in pairs, like shoes.", 'print("Oops")'),
                        oops('print("Hi)', "The closing quote is missing, so Python can't tell where the text ends.", 'print("Hi")'),
                    ],
                    [
                        fix(
                            "This code has a bug. Press Run my code to see the error explained. Then fix it so it prints: Fixed it",
                            'print("Fixed it"',
                            'print("Fixed it")',
                            [out("Fixed it")],
                            [
                                "Count the brackets. There's an opening ( but is there a closing one?",
                                "Add a ) at the very end of the line.",
                                'The fixed line is: print("Fixed it")',
                            ],
                        ),
                        fix(
                            "Another bug. Fix it so it prints: Debugging is fun",
                            'print("Debugging is fun)',
                            'print("Debugging is fun")',
                            [out("Debugging is fun")],
                            [
                                "The text starts with a quote mark. Does it end with one?",
                                "Put a \" right after the word fun, before the ).",
                                'The fixed line is: print("Debugging is fun")',
                            ],
                        ),
                        ask(
                            "What is a bug?",
                            "A mistake in code",
                            ["A broken phone", "A kind of output", "A Python command"],
                            "Right. A bug is a mistake in code. Fixing it is called debugging.",
                            ["It's a word coders use for something that went wrong.", "Debugging means removing these."],
                        ),
                    ],
                    terms=[
                        term("error", "Python's message when it can't follow your code. It says what went wrong and where.", "a teacher circling the exact spot on your homework that needs fixing."),
                        term("bug", "A mistake in code.", "a typo in a text message."),
                    ],
                ),
            ],
        )
    ]
