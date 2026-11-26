from .dsl import ask, checkpoint, code, fix, lesson, oops, out, predict, term, unit, vals, walk


def units():
    return [
        unit(
            "variables",
            "Variables",
            "Store things in named boxes.",
            "archivebox.fill",
            [
                lesson(
                    "var-name",
                    "A named box",
                    """
A variable is a name that holds a value, so you can use it later.

You make one with an equals sign: name = "Sam". The name goes on the left. The value goes on the right.

After that, whenever you write name, Python uses "Sam".
""",
                    """
The = sign in Python doesn't mean "is equal to" like in math. It means "put the value on the right into the box on the left." Python remembers what's in the box until you change it.
""",
                    'name = "Sam"\nprint(name)\nprint("Hi", name)',
                    "Make a variable, then use it twice.",
                    [
                        walk('name = "Sam"', 'Makes a box called name and puts the text "Sam" in it. Nothing is shown yet.'),
                        walk("print(name)", "No quotes around name, so Python looks inside the box. It shows Sam."),
                        walk('print("Hi", name)', "Shows the text Hi, a space, then what's in the box: Hi Sam"),
                    ],
                    [
                        oops('name = "Sam"\nprint("name")', 'With quotes, "name" is just the word name, not the box. Leave the quotes off to use the variable.', 'name = "Sam"\nprint(name)'),
                        oops('name = "Sam"\nprint(Name)', "Name with a capital N is a different name. Python is picky about capitals.", 'name = "Sam"\nprint(name)'),
                    ],
                    [
                        code(
                            'Fill in the blank to put the text Ada in the variable name. The print line shows it.',
                            'name = "___"\nprint(name)',
                            'name = "Ada"\nprint(name)',
                            [vals("name", out="Ada")],
                            [
                                "Replace ___ with Ada.",
                                "Keep the quotes, because Ada is text.",
                                'The answer is:\nname = "Ada"\nprint(name)',
                            ],
                            wrong=['name = "ada"\nprint(name)', 'name = "Ada"\nprint("name")'],
                        ),
                        code(
                            "Make a variable called pet that holds the text Rex. Then print pet.",
                            "# Make the variable, then print it\n",
                            'pet = "Rex"\nprint(pet)',
                            [vals("pet", out="Rex")],
                            [
                                "First line: the name pet, then =, then the value.",
                                'The value is text, so it needs quotes: "Rex"',
                                'The answer is:\npet = "Rex"\nprint(pet)',
                            ],
                            wrong=['print("Rex")'],
                        ),
                        predict(
                            'animal = "cat"\nprint("animal")\nprint(animal)',
                            ["cat\ncat", "animal\nanimal", "cat\nanimal"],
                            'With quotes, print shows the word itself. Without quotes, it shows what\'s inside the variable.',
                            ['Look closely: one print has quotes and one does not.', '"animal" in quotes is just text.'],
                        ),
                    ],
                    terms=[
                        term("variable", "A name that holds a value so you can use it later.", "a labeled box. The label is the name, and the thing inside is the value."),
                        term("value", "The thing stored, like the text \"Sam\" or the number 13.", "what's inside the box."),
                    ],
                ),
                lesson(
                    "var-number",
                    "Numbers in boxes",
                    """
Variables can hold numbers too. Numbers don't need quotes: age = 13.

Then you can do math with the variable, like age + 1.
""",
                    """
When Python sees age + 1, it first looks inside the box called age, finds 13, and then works out 13 + 1. The box itself doesn't change unless you use = again.
""",
                    "age = 13\nprint(age)\nprint(age + 1)",
                    "A number in a variable, then a little math with it.",
                    [
                        walk("age = 13", "Puts the number 13 in a box called age. No quotes, because it's a number."),
                        walk("print(age)", "Shows 13."),
                        walk("print(age + 1)", "Python works out 13 + 1 and shows 14. age itself is still 13."),
                    ],
                    [
                        oops('age = "13"\nprint(age + 1)', 'In quotes, "13" is text, not a number, so Python can\'t add 1 to it.', "age = 13\nprint(age + 1)"),
                    ],
                    [
                        code(
                            "Fill in the blank so the variable score holds the number 10.",
                            "score = ___\nprint(score)",
                            "score = 10\nprint(score)",
                            [vals("score", out="10")],
                            [
                                "Replace ___ with 10.",
                                "Numbers don't need quotes.",
                                "The answer is:\nscore = 10\nprint(score)",
                            ],
                            wrong=['score = "10"\nprint(score)'],
                        ),
                        code(
                            "Make a variable lives that holds 3. Then print lives + 2.",
                            "# Make lives, then print lives + 2\n",
                            "lives = 3\nprint(lives + 2)",
                            [vals("lives", out="5")],
                            [
                                "First line: lives = 3",
                                "Second line: print, with lives + 2 inside the brackets.",
                                "The answer is:\nlives = 3\nprint(lives + 2)",
                            ],
                            must=["lives +"],
                            wrong=["lives = 3\nprint(5)", "lives = 5\nprint(lives)"],
                        ),
                        predict(
                            "coins = 4\nprint(coins + coins)",
                            ["coins + coins", "4", "44"],
                            "coins holds 4, so coins + coins is 4 + 4, which is 8.",
                            ["What number is inside coins?", "Add that number to itself."],
                        ),
                    ],
                ),
                lesson(
                    "var-change",
                    "Changing the box",
                    """
You can put a new value in a variable at any time. The old value is replaced.

A very common move is to change a variable using its own value: score = score + 1. That means "take what's in score, add 1, and put the result back in score."
""",
                    """
Python always works out the right side of = first, using what's in the boxes right now. Then it stores the answer in the box on the left. So score = score + 1 reads the old score, adds 1, and saves the new number.
""",
                    "score = 0\nprint(score)\nscore = score + 5\nprint(score)",
                    "Watch score change as the program runs.",
                    [
                        walk("score = 0", "score starts at 0."),
                        walk("print(score)", "Shows 0."),
                        walk("score = score + 5", "Right side first: 0 + 5 is 5. Then 5 goes into score."),
                        walk("print(score)", "Shows 5, the new value."),
                    ],
                    [
                        oops("score = 0\nscore + 5\nprint(score)", "score + 5 works out 5 but doesn't save it anywhere. You need score = in front to change the box.", "score = 0\nscore = score + 5\nprint(score)"),
                    ],
                    [
                        code(
                            "coins starts at 2. Fill in the blank so the second line adds 1 to coins.",
                            "coins = 2\ncoins = coins + ___\nprint(coins)",
                            "coins = 2\ncoins = coins + 1\nprint(coins)",
                            [vals("coins", out="3")],
                            [
                                "Replace ___ with the amount to add.",
                                "You're adding 1.",
                                "The answer is:\ncoins = 2\ncoins = coins + 1\nprint(coins)",
                            ],
                            wrong=["coins = 2\ncoins = coins + 2\nprint(coins)"],
                        ),
                        code(
                            "points starts at 10. Add 5 to points, then print points. It should print 15.",
                            "points = 10\n# Add 5 to points on the next line\n\nprint(points)",
                            "points = 10\npoints = points + 5\nprint(points)",
                            [vals("points", out="15")],
                            [
                                "Use the pattern points = points + something.",
                                "The something is 5.",
                                "The middle line is: points = points + 5",
                            ],
                            must=["points +"],
                            wrong=["points = 15\nprint(points)", "points = 10\nprint(points + 5)"],
                        ),
                        predict(
                            "x = 1\nx = 7\nprint(x)",
                            ["1", "1\n7", "8"],
                            "The second line replaces the 1 with 7. A variable only holds its newest value.",
                            ["What happens to the old value when you use = again?", "The box can only hold one thing at a time."],
                        ),
                    ],
                ),
                lesson(
                    "var-together",
                    "Boxes working together",
                    """
You can use several variables at once. Their values can be combined to make a new variable.

total = apples + pears adds what's in apples and what's in pears, and puts the answer in total.
""",
                    """
Each name on the right side is swapped for its value before the math happens. So if apples is 3 and pears is 4, Python sees 3 + 4, works out 7, and stores 7 in total.
""",
                    "apples = 3\npears = 4\ntotal = apples + pears\nprint(total)",
                    "Two boxes are added together into a third box.",
                    [
                        walk("apples = 3", "apples holds 3."),
                        walk("pears = 4", "pears holds 4."),
                        walk("total = apples + pears", "Python sees 3 + 4, works out 7, and puts 7 in total."),
                        walk("print(total)", "Shows 7."),
                    ],
                    [
                        oops("total = apples + pears\napples = 3\npears = 4\nprint(total)", "Order matters. You can't use apples before you make it. Python reads from the top down.", "apples = 3\npears = 4\ntotal = apples + pears\nprint(total)"),
                    ],
                    [
                        code(
                            "Fill in the blank so total holds a + b.",
                            "a = 6\nb = 4\ntotal = ___\nprint(total)",
                            "a = 6\nb = 4\ntotal = a + b\nprint(total)",
                            [vals("total", out="10")],
                            [
                                "Use the two variable names with a + between them.",
                                "Replace ___ with a + b.",
                                "The answer is: total = a + b",
                            ],
                            must=["a + b"],
                            wrong=["a = 6\nb = 4\ntotal = 10\nprint(total)"],
                        ),
                        code(
                            "Make width = 5 and height = 3. Make area = width times height (use *). Print area.",
                            "width = 5\nheight = 3\n# Make area here, then print it\n",
                            "width = 5\nheight = 3\narea = width * height\nprint(area)",
                            [vals("area", out="15")],
                            [
                                "In Python, * means times.",
                                "area = width * height",
                                "The answer is:\nwidth = 5\nheight = 3\narea = width * height\nprint(area)",
                            ],
                            must=["width", "height", "*"],
                            wrong=["area = 15\nprint(area)"],
                        ),
                        predict(
                            'first = "Ice"\nsecond = "cream"\nprint(first, second)',
                            ["Icecream", "first second", "Ice, cream"],
                            "print shows what's in each variable, with a space between them.",
                            ["What's inside first and second?", "A comma in print adds a space."],
                        ),
                    ],
                ),
                lesson(
                    "var-names",
                    "Good names",
                    """
Variable names have a few rules:

- Use letters, numbers, and underscores _.
- No spaces. Use an underscore instead: high_score.
- Don't start with a number. score2 is fine, 2score is not.
- Capitals matter. Score and score are two different names.

Pick names that say what's inside, like lives or player_name.
""",
                    """
Python reads a space as the end of a name, so my score looks like two separate names to it. The underscore glues words together into one name. Good names make your code easier to read, for you and for anyone else.
""",
                    'player_name = "Kai"\nhigh_score = 120\nprint(player_name, high_score)',
                    "Two clear names, using underscores instead of spaces.",
                    [
                        walk('player_name = "Kai"', "The underscore joins player and name into one variable name."),
                        walk("high_score = 120", "Another two-word name joined with _."),
                        walk("print(player_name, high_score)", "Shows Kai 120."),
                    ],
                    [
                        oops("high score = 120\nprint(high score)", "A space in a name confuses Python. Use high_score.", "high_score = 120\nprint(high_score)"),
                        oops("2nd_place = \"Mo\"\nprint(2nd_place)", "Names can't start with a number.", "second_place = \"Mo\"\nprint(second_place)"),
                    ],
                    [
                        ask(
                            "Which one is an allowed variable name?",
                            "best_time",
                            ["best time", "1st_time", "best-time"],
                            "best_time uses only letters and an underscore, and starts with a letter.",
                            ["Spaces and dashes are not allowed in names.", "A name can't start with a number."],
                        ),
                        fix(
                            "This name has a space in it. Fix the name on both lines by using an underscore, so it prints 3.",
                            "my lives = 3\nprint(my lives)",
                            "my_lives = 3\nprint(my_lives)",
                            [vals("my_lives", out="3")],
                            [
                                "Python can't have a space inside a name.",
                                "Change my lives to my_lives on both lines.",
                                "The fixed code is:\nmy_lives = 3\nprint(my_lives)",
                            ],
                        ),
                        fix(
                            "The name changes between lines. Make both lines use score, all lowercase, so it prints 9.",
                            "score = 9\nprint(Score)",
                            "score = 9\nprint(score)",
                            [out("9")],
                            [
                                "Look at the capital letters on each line.",
                                "Score and score are different names to Python.",
                                "The fixed second line is: print(score)",
                            ],
                        ),
                    ],
                ),
                checkpoint(
                    "var-check",
                    "Checkpoint: variables",
                    "Follow each variable from the top down. Keep track of what's in each box as you go.",
                    [
                        predict(
                            "a = 2\nb = a + 3\nprint(b)",
                            ["a + 3", "2", "23"],
                            "a is 2, so b is 2 + 3, which is 5.",
                            ["What is in a?", "Work out the right side of b = first."],
                        ),
                        predict(
                            "n = 5\nn = n + 1\nn = n + 1\nprint(n)",
                            ["5", "6", "n"],
                            "n goes 5, then 6, then 7.",
                            ["Each n = n + 1 adds one.", "There are two of those lines."],
                        ),
                        predict(
                            'word = "hi"\nprint("word", word)',
                            ["hi hi", "word word", '"word" hi'],
                            'The first part is the text "word". The second is the variable, which holds hi.',
                            ["One has quotes and one does not.", "Quotes mean show this text exactly."],
                        ),
                    ],
                ),
            ],
        )
    ]
