from .dsl import ask, checkpoint, code, fix, has, lesson, oops, out, predict, term, unit, vals, walk


def units():
    return [
        unit(
            "bonus-collections",
            "Bonus: tuples, sets, and one-line lists",
            "Extra tools for when you feel ready. Not needed for the main path.",
            "square.stack.3d.up.fill",
            [
                lesson(
                    "tuple-make",
                    "Tuples: fixed groups",
                    """
A tuple is like a list that can't be changed. It uses round brackets: point = (3, 5).

You read items the same way, point[0], but you can't replace them. Tuples are good for things that belong together and shouldn't change, like a map position.
""",
                    """
Because a tuple can't change, Python can trust it to stay the same. That makes it safe to pass around. If you need to add or change items, use a list instead.
""",
                    "point = (3, 5)\nprint(point[0])\nprint(len(point))\nx, y = point\nprint(x + y)",
                    "A pair of numbers, read by position, then unpacked into two names.",
                    [
                        walk("point = (3, 5)", "A tuple with two items."),
                        walk("print(point[0])", "First item: 3"),
                        walk("x, y = point", "Unpacking: x gets 3 and y gets 5, in one line."),
                        walk("print(x + y)", "8"),
                    ],
                    [
                        oops("point = (3, 5)\npoint[0] = 9", "Tuples can't be changed, so this is a TypeError. Use a list if you need changes.", "point = [3, 5]\npoint[0] = 9"),
                    ],
                    [
                        code(
                            "Fill in the blank to unpack the tuple into name and age.",
                            'person = ("Mo", 12)\n___ = person\nprint(name, age)',
                            'person = ("Mo", 12)\nname, age = person\nprint(name, age)',
                            [out("Mo 12")],
                            ["Two names on the left, separated by a comma.", "Replace ___ with name, age", "The line is: name, age = person"],
                        ),
                        code(
                            "Write a function min_max(nums) that returns a tuple (smallest, biggest). Use min() and max().",
                            "def min_max(nums):\n    # return a tuple\n    pass",
                            "def min_max(nums):\n    return (min(nums), max(nums))",
                            [out("(1, 9)", append="print(min_max([4, 1, 9]))"), out("(5, 5)", append="print(min_max([5]))")],
                            ["min(nums) is the smallest, max(nums) the biggest.", "Return them inside round brackets.", "The answer is:\ndef min_max(nums):\n    return (min(nums), max(nums))"],
                            must=["return"],
                        ),
                        predict("a, b = (1, 2)\na, b = b, a\nprint(a, b)", ["1 2", "2 2", "(2, 1)"], "a, b = b, a swaps the two values.", ["The right side is worked out first: (2, 1).", "Then it's unpacked into a and b."]),
                    ],
                    terms=[term("tuple", "A fixed group of values in round brackets. It can't be changed.", "a date written in pen: day, month, year.")],
                ),
                lesson(
                    "set-unique",
                    "Sets: no repeats",
                    """
A set holds values with no repeats and no fixed order. Make one with set(some_list) or with curly brackets {1, 2, 3}.

It's the quickest way to remove duplicates or to check whether something has been seen.
""",
                    """
A set only keeps one copy of each value. Adding something that's already there does nothing. That's why set(["a", "a", "b"]) has just 2 items.
""",
                    'votes = ["cat", "dog", "cat", "cat"]\nunique = set(votes)\nprint(len(unique))\nseen = set()\nseen.add("x")\nseen.add("x")\nprint(len(seen))',
                    "Repeats disappear in a set.",
                    [
                        walk("unique = set(votes)", "Only cat and dog remain."),
                        walk("print(len(unique))", "2"),
                        walk('seen.add("x")', "Add to a set with .add(). Adding x twice keeps one x."),
                        walk("print(len(seen))", "1"),
                    ],
                    [
                        oops("empty = {}\nempty.add(1)", "{} makes an empty dictionary, not a set. Use set() for an empty set.", "empty = set()\nempty.add(1)"),
                    ],
                    [
                        code(
                            "Fill in the blank to make a set from the list, then print how many different colors there are.",
                            'colors = ["red", "blue", "red"]\nprint(len(___(colors)))',
                            'colors = ["red", "blue", "red"]\nprint(len(set(colors)))',
                            [out("2")],
                            ["Which tool turns a list into a set?", "Replace ___ with set.", "The answer is: print(len(set(colors)))"],
                            must=["set"],
                        ),
                        code(
                            "Write has_repeat(items) that returns True if any value appears more than once. Tip: compare len(items) with len(set(items)).",
                            "def has_repeat(items):\n    # compare the lengths\n    pass",
                            "def has_repeat(items):\n    return len(set(items)) < len(items)",
                            [out("True", append="print(has_repeat([1, 2, 1]))"), out("False", append="print(has_repeat([1, 2, 3]))"), out("False", append="print(has_repeat([]))")],
                            ["If there's a repeat, the set is shorter than the list.", "return len(set(items)) < len(items)", "The answer is:\ndef has_repeat(items):\n    return len(set(items)) < len(items)"],
                            must=["set", "return"],
                        ),
                        predict('s = {1, 2}\ns.add(2)\ns.add(3)\nprint(len(s))', ["4", "2", "5"], "2 was already there, so only 3 is new: {1, 2, 3}.", ["Does adding 2 again change anything?", "Count the different values."]),
                    ],
                    terms=[term("set", "A group of values with no repeats.", "a sticker album: you only stick in one of each.")],
                ),
                lesson(
                    "comp-squares",
                    "One-line lists",
                    """
A list comprehension builds a list in one line. Instead of making an empty list and appending in a loop, you write:

squares = [n * n for n in range(5)]

Read it as: "n * n, for each n in range(5)."
""",
                    """
It does exactly what the loop-and-append pattern does, in a shorter form. The part before for is what goes in the list. The for part says where the values come from.
""",
                    "squares = []\nfor n in range(4):\n    squares.append(n * n)\nprint(squares)\nquick = [n * n for n in range(4)]\nprint(quick)",
                    "The long way and the one-line way make the same list.",
                    [
                        walk("squares.append(n * n)", "The long way: a loop that appends."),
                        walk("quick = [n * n for n in range(4)]", "The one-line way. Same result."),
                        walk("print(quick)", "[0, 1, 4, 9]"),
                    ],
                    [],
                    [
                        code(
                            "Fill in the blank so the list holds each n times 10.",
                            "tens = [___ for n in range(1, 4)]\nprint(tens)",
                            "tens = [n * 10 for n in range(1, 4)]\nprint(tens)",
                            [vals("tens", out="[10, 20, 30]")],
                            ["What should each item be?", "Replace ___ with n * 10.", "The line is: tens = [n * 10 for n in range(1, 4)]"],
                            must=["for"],
                        ),
                        code(
                            "Use a comprehension to make shout: every word in words in capitals.",
                            'words = ["hi", "yo"]\n# shout = [...]\n',
                            'words = ["hi", "yo"]\nshout = [w.upper() for w in words]',
                            [vals("shout")],
                            ["Each item is w.upper().", "for w in words", "The line is: shout = [w.upper() for w in words]"],
                            must=["for", "upper"],
                            wrong=['shout = ["HI", "YO"]'],
                        ),
                        predict("print([c * 2 for c in \"ab\"])", ["['a', 'b']", "abab", "['ab', 'ab']"], "Each letter doubled: ['aa', 'bb'].", ["The loop goes through a and b.", "Each one becomes c * 2."]),
                    ],
                    terms=[term("list comprehension", "A one-line way to build a list from a loop.", "a cookie cutter stamping out one cookie per piece of dough.")],
                ),
                lesson(
                    "comp-filter",
                    "One-line lists with if",
                    """
Add an if at the end of a comprehension to keep only some items:

evens = [n for n in range(10) if n % 2 == 0]
""",
                    """
The if acts like a filter. Each n is checked, and only the ones where the condition is True make it into the new list.
""",
                    "nums = [3, 8, 1, 12]\nbig = [n for n in nums if n > 5]\nprint(big)",
                    "Keeping only the big numbers.",
                    [
                        walk("big = [n for n in nums if n > 5]", "Keep n only if n > 5."),
                        walk("print(big)", "[8, 12]"),
                    ],
                    [],
                    [
                        code(
                            "Fill in the blank so only odd numbers are kept.",
                            "odds = [n for n in range(8) if ___]\nprint(odds)",
                            "odds = [n for n in range(8) if n % 2 == 1]\nprint(odds)",
                            [vals("odds", out="[1, 3, 5, 7]")],
                            ["Odd numbers have a remainder of 1 when divided by 2.", "Replace ___ with n % 2 == 1.", "The line is: odds = [n for n in range(8) if n % 2 == 1]"],
                            must=["for", "if"],
                        ),
                        code(
                            "Make short: the words in words with 3 letters or fewer.",
                            'words = ["cat", "zebra", "ox", "lion"]\n# short = [...]\n',
                            'words = ["cat", "zebra", "ox", "lion"]\nshort = [w for w in words if len(w) <= 3]',
                            [vals("short")],
                            ["Keep w if len(w) <= 3.", "[w for w in words if ...]", "The line is: short = [w for w in words if len(w) <= 3]"],
                            must=["for", "if"],
                            wrong=['short = ["cat", "ox"]'],
                        ),
                        predict("print([n for n in [1, 2, 3, 4] if n != 2])", ["[2]", "[1, 2, 3, 4]", "[False, True, False, False]"], "Everything except 2: [1, 3, 4].", ["Which numbers pass the check?", "!= means not equal."]),
                    ],
                ),
            ],
            optional=True,
        )
    ]
