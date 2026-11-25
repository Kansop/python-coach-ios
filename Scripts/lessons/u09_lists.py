from .dsl import ask, checkpoint, code, fix, has, lesson, oops, out, predict, term, unit, vals, walk


def units():
    return [
        unit(
            "lists",
            "Lists",
            "Keep many things in order.",
            "list.bullet",
            [
                lesson(
                    "list-make",
                    "Making a list",
                    """
A list holds many values in one variable, in order. Use square brackets [ ] with commas between the items:

snacks = ["chips", "apple", "nuts"]

A list can hold strings, numbers, or a mix.
""",
                    """
Without lists, you'd need snack1, snack2, snack3 and so on. A list keeps them together under one name, in the order you wrote them, so you can work with all of them at once.
""",
                    'snacks = ["chips", "apple", "nuts"]\nprint(snacks)\nprint(len(snacks))',
                    "One list, printed whole, then counted.",
                    [
                        walk('snacks = ["chips", "apple", "nuts"]', "Three strings in one list."),
                        walk("print(snacks)", "Shows the whole list with its brackets."),
                        walk("print(len(snacks))", "len counts the items: 3."),
                    ],
                    [
                        oops('colors = ["red" "blue"]\nprint(len(colors))', "Without a comma, Python glues the two strings into one item. Put commas between items.", 'colors = ["red", "blue"]\nprint(len(colors))'),
                    ],
                    [
                        code(
                            'Fill in the blank: add "pear" as the third item, with a comma before it.',
                            'fruits = ["apple", "kiwi", ___]\nprint(fruits)',
                            'fruits = ["apple", "kiwi", "pear"]\nprint(fruits)',
                            [vals("fruits")],
                            [
                                "The item is text, so it needs quotes.",
                                'Replace ___ with "pear".',
                                'The answer is: fruits = ["apple", "kiwi", "pear"]',
                            ],
                            wrong=['fruits = ["apple", "kiwi", "Pear"]\nprint(fruits)'],
                        ),
                        code(
                            "Make a list called scores with the numbers 10, 20, and 30. Print how many items it has.",
                            "# Make scores, then print its length\n",
                            "scores = [10, 20, 30]\nprint(len(scores))",
                            [vals("scores", out="3")],
                            [
                                "Square brackets, numbers, commas between them.",
                                "Then print(len(scores)).",
                                "The answer is:\nscores = [10, 20, 30]\nprint(len(scores))",
                            ],
                            must=["len"],
                        ),
                        predict(
                            "nums = [4, 8, 15, 16]\nprint(len(nums))",
                            ["16", "43", "3"],
                            "len counts the items, not the numbers inside them. There are 4.",
                            ["Count the items between the commas.", "len doesn't add them up."],
                        ),
                    ],
                    terms=[
                        term("list", "Many values in one variable, in order, inside [ ].", "a shopping list. One piece of paper, many items, in order."),
                        term("item", "One value inside a list.", "one thing on the shopping list."),
                    ],
                ),
                lesson(
                    "list-index",
                    "Picking an item",
                    """
Each item in a list has a position number, called an index. Like with strings, counting starts at 0.

players[0] is the first item. players[1] is the second. players[-1] is the last.

You can also replace an item: players[0] = "Max".
""",
                    """
The index says how many steps from the start. The first item is right at the start, 0 steps away. Using an index that's too big gives an IndexError, because that spot doesn't exist.
""",
                    'players = ["Ana", "Ben", "Cy"]\nprint(players[0])\nprint(players[-1])\nplayers[1] = "Bo"\nprint(players)',
                    "Read the first and last items, then replace one.",
                    [
                        walk("print(players[0])", "Position 0 is the first item: Ana"),
                        walk("print(players[-1])", "-1 is the last item: Cy"),
                        walk('players[1] = "Bo"', 'Replaces the item at position 1 ("Ben") with "Bo".'),
                        walk("print(players)", "Shows the changed list."),
                    ],
                    [
                        oops('pets = ["cat", "dog"]\nprint(pets[2])', "There are 2 items, at positions 0 and 1. [2] is past the end.", 'pets = ["cat", "dog"]\nprint(pets[1])'),
                    ],
                    [
                        code(
                            "Fill in the blank to print the first color.",
                            'colors = ["red", "green", "blue"]\nprint(colors[___])',
                            'colors = ["red", "green", "blue"]\nprint(colors[0])',
                            [out("red")],
                            [
                                "The first position isn't 1.",
                                "Replace ___ with 0.",
                                "The answer is: print(colors[0])",
                            ],
                            wrong=['colors = ["red", "green", "blue"]\nprint(colors[1])'],
                        ),
                        code(
                            'Change the second item of days to "Wed", then print days.',
                            'days = ["Mon", "Tue", "Fri"]\n# Change the second item\n\nprint(days)',
                            'days = ["Mon", "Tue", "Fri"]\ndays[1] = "Wed"\nprint(days)',
                            [vals("days")],
                            [
                                "The second item is at position 1.",
                                'Use days[1] = "Wed"',
                                'The middle line is: days[1] = "Wed"',
                            ],
                            must=["days[1]"],
                            wrong=['days = ["Mon", "Wed", "Fri"]\nprint(days)'],
                        ),
                        predict(
                            'letters = ["a", "b", "c", "d"]\nprint(letters[2], letters[-1])',
                            ["b d", "c c", "b a"],
                            "Position 2 is c (a is 0, b is 1). -1 is the last one, d.",
                            ["Start counting at 0.", "-1 means the last item."],
                        ),
                    ],
                ),
                lesson(
                    "list-append",
                    "Growing a list",
                    """
.append() adds an item to the end of a list:

bag.append("key")

You can start with an empty list, [ ], and add to it as your program runs.
""",
                    """
append is a method, a tool that belongs to the list. It changes the list itself, so you don't need = to save anything. The new item always goes at the end.
""",
                    'bag = []\nbag.append("map")\nbag.append("torch")\nprint(bag)\nprint(len(bag))',
                    "Start empty, add two items.",
                    [
                        walk("bag = []", "An empty list."),
                        walk('bag.append("map")', 'Adds "map" to the end. bag is ["map"].'),
                        walk('bag.append("torch")', 'Adds "torch" after it.'),
                        walk("print(bag)", "Shows ['map', 'torch']."),
                        walk("print(len(bag))", "2 items."),
                    ],
                    [
                        oops('bag = []\nbag = bag.append("map")\nprint(bag)', "append changes the list and gives back None. Saving that with = wipes out your list. Write bag.append(...) on its own.", 'bag = []\nbag.append("map")\nprint(bag)'),
                    ],
                    [
                        code(
                            'Fill in the blank with the method that adds to the end.',
                            'team = ["Ana"]\nteam.___("Ben")\nprint(team)',
                            'team = ["Ana"]\nteam.append("Ben")\nprint(team)',
                            [vals("team")],
                            [
                                "The method's name means add to the end.",
                                "Replace ___ with append.",
                                'The line is: team.append("Ben")',
                            ],
                            must=["append"],
                        ),
                        code(
                            "Start with an empty list called squares. Use a loop over range(1, 5) to append n * n each lap. Print squares.",
                            "squares = []\n# Loop and append\n\nprint(squares)",
                            "squares = []\nfor n in range(1, 5):\n    squares.append(n * n)\nprint(squares)",
                            [vals("squares", out="[1, 4, 9, 16]")],
                            [
                                "for n in range(1, 5):",
                                "Inside the loop: squares.append(n * n)",
                                "The answer is:\nfor n in range(1, 5):\n    squares.append(n * n)",
                            ],
                            must=["append", "for"],
                            wrong=["squares = [1, 4, 9, 16]\nprint(squares)"],
                        ),
                        predict(
                            "a = [1]\na.append(2)\na.append(1)\nprint(a)",
                            ["[1, 2]", "[2, 1, 1]", "[1, 1, 2]"],
                            "Each append adds to the end, in order.",
                            ["Where does append put the new item?", "Go line by line."],
                        ),
                    ],
                ),
                lesson(
                    "list-loop",
                    "Visiting every item",
                    """
A for loop can walk through a list, one item at a time:

for name in friends:
    print("Hi", name)

Each lap, the loop variable holds the next item.
""",
                    """
It's the same as looping over a string. The list hands its items to the loop in order. You pick the loop variable's name, so choose one that says what each item is, like name for a list of names.
""",
                    'prices = [3, 5, 2]\ntotal = 0\nfor p in prices:\n    total += p\nprint("Total:", total)',
                    "Adding up a list with a loop.",
                    [
                        walk("prices = [3, 5, 2]", "Three prices."),
                        walk("total = 0", "The running total starts at 0."),
                        walk("for p in prices:", "p will be 3, then 5, then 2."),
                        walk("total += p", "Adds each price: 3, 8, 10."),
                        walk('print("Total:", total)', "Total: 10"),
                    ],
                    [
                        oops('pets = ["cat", "dog"]\nfor p in pets:\n    print(pets)', "Printing pets shows the whole list every lap. Print the loop variable p instead.", 'pets = ["cat", "dog"]\nfor p in pets:\n    print(p)'),
                    ],
                    [
                        code(
                            "Fill in the blank so the loop goes through the list.",
                            'friends = ["Ana", "Ben"]\nfor f in ___:\n    print("Hi", f)',
                            'friends = ["Ana", "Ben"]\nfor f in friends:\n    print("Hi", f)',
                            [out("Hi Ana\nHi Ben")],
                            [
                                "The loop walks through the list.",
                                "Replace ___ with friends.",
                                "The line is: for f in friends:",
                            ],
                            must=["for"],
                        ),
                        code(
                            "Print each word in words in capitals, one per line, using a loop.",
                            'words = ["sun", "sea", "sky"]\n# Loop and print\n',
                            'words = ["sun", "sea", "sky"]\nfor w in words:\n    print(w.upper())',
                            [out("SUN\nSEA\nSKY")],
                            [
                                "for w in words:",
                                "Inside the loop: print(w.upper())",
                                "The answer is:\nfor w in words:\n    print(w.upper())",
                            ],
                            must=["for", "upper"],
                            wrong=['print("SUN")\nprint("SEA")\nprint("SKY")'],
                        ),
                        code(
                            "Find the biggest number in nums with a loop. Start biggest at nums[0], and replace it whenever you find a bigger n. Print biggest.",
                            "nums = [4, 9, 2, 7]\nbiggest = nums[0]\n# Loop here\n\nprint(biggest)",
                            "nums = [4, 9, 2, 7]\nbiggest = nums[0]\nfor n in nums:\n    if n > biggest:\n        biggest = n\nprint(biggest)",
                            [vals("biggest", out="9")],
                            [
                                "Loop: for n in nums:",
                                "Inside: if n > biggest: then biggest = n.",
                                "The loop is:\nfor n in nums:\n    if n > biggest:\n        biggest = n",
                            ],
                            must=["for", "if"],
                            wrong=["nums = [4, 9, 2, 7]\nbiggest = 9\nprint(biggest)"],
                        ),
                    ],
                ),
                lesson(
                    "list-in",
                    "Is it in the list?",
                    """
in checks whether something is in a list. It gives True or False:

"milk" in groceries

It works great with if. not in checks the opposite.
""",
                    """
in looks at each item until it finds a match. If it finds one, the answer is True. If it reaches the end without a match, the answer is False. The match must be exact, including capitals.
""",
                    'guests = ["Ana", "Ben"]\nprint("Ana" in guests)\nif "Zed" not in guests:\n    print("Zed is not invited")',
                    "Checking who's on the guest list.",
                    [
                        walk('print("Ana" in guests)', "Ana is in the list: True."),
                        walk('if "Zed" not in guests:', "Zed isn't there, so not in is True."),
                        walk('print("Zed is not invited")', "This runs."),
                    ],
                    [
                        oops('guests = ["Ana"]\nprint("ana" in guests)', '"ana" with a lowercase a doesn\'t match "Ana".', 'guests = ["Ana"]\nprint("Ana" in guests)'),
                    ],
                    [
                        code(
                            "Fill in the blank so it checks whether pizza is on the menu.",
                            'menu = ["pizza", "soup"]\nif "pizza" ___ menu:\n    print("Yum")',
                            'menu = ["pizza", "soup"]\nif "pizza" in menu:\n    print("Yum")',
                            [out("Yum")],
                            [
                                "The word that checks for an item is very short.",
                                "Replace ___ with in.",
                                'The line is: if "pizza" in menu:',
                            ],
                            must=["in"],
                        ),
                        code(
                            'The checker types a name. If it is in allowed, print Welcome. Otherwise print Sorry.',
                            'allowed = ["Ana", "Ben", "Cy"]\nname = input("Name? ")\n# Check here\n',
                            'allowed = ["Ana", "Ben", "Cy"]\nname = input("Name? ")\nif name in allowed:\n    print("Welcome")\nelse:\n    print("Sorry")',
                            [has("Welcome", stdin=["Ben"]), has("Sorry", stdin=["Dee"])],
                            [
                                "if name in allowed:",
                                "Add an else for Sorry.",
                                'The answer is:\nif name in allowed:\n    print("Welcome")\nelse:\n    print("Sorry")',
                            ],
                            must=["in", "else"],
                            wrong=['allowed = ["Ana", "Ben", "Cy"]\nname = input("Name? ")\nprint("Welcome")'],
                        ),
                        predict(
                            "nums = [1, 2, 3]\nprint(4 in nums, 2 in nums)",
                            ["True True", "False False", "4 2"],
                            "4 isn't in the list, 2 is.",
                            ["Is 4 in the list?", "Is 2 in the list?"],
                        ),
                    ],
                ),
                checkpoint(
                    "list-check",
                    "Checkpoint: lists",
                    "Remember: positions start at 0, append adds to the end, and len counts items.",
                    [
                        predict('x = ["a", "b", "c"]\nprint(x[1])', ["a", "c", "1"], "Position 1 is the second item, b.", ["Start counting at 0.", "a is at 0."]),
                        predict("x = [5]\nx.append(6)\nprint(len(x))", ["1", "11", "6"], "Now the list has 2 items.", ["What does append do?", "Count the items."]),
                        predict("t = 0\nfor n in [2, 4, 6]:\n    t += n\nprint(t)", ["6", "246", "3"], "2 + 4 + 6 = 12.", ["Add each item to t.", "The loop runs 3 times."]),
                    ],
                ),
            ],
        )
    ]
