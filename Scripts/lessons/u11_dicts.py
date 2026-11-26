from .dsl import ask, checkpoint, code, fix, has, lesson, oops, out, predict, term, unit, vals, walk


def units():
    return [
        unit(
            "dictionaries",
            "Dictionaries",
            "Look things up by name.",
            "book.closed.fill",
            [
                lesson(
                    "dict-make",
                    "Keys and values",
                    """
A dictionary stores pairs: a key and its value. You look up the value using the key, like looking up a word to find its meaning.

pet = {"name": "Luna", "age": 3}

Curly brackets { }, a colon between each key and value, and commas between pairs. Look up with square brackets: pet["name"].
""",
                    """
A list finds things by position number. A dictionary finds things by key, which is often a word. That's handy when position doesn't mean anything, like a player's name, score, and level.
""",
                    'pet = {"name": "Luna", "age": 3}\nprint(pet["name"])\nprint(pet["age"] + 1)',
                    "One dictionary with two pairs.",
                    [
                        walk('pet = {"name": "Luna", "age": 3}', 'Two pairs: "name" goes with "Luna", "age" goes with 3.'),
                        walk('print(pet["name"])', 'Looks up the key "name": Luna'),
                        walk('print(pet["age"] + 1)', "Looks up age (3), then adds 1: 4"),
                    ],
                    [
                        oops('pet = {"name": "Luna"}\nprint(pet["Name"])', 'Keys must match exactly. "Name" isn\'t the same as "name", so you get a KeyError.', 'pet = {"name": "Luna"}\nprint(pet["name"])'),
                        oops('pet = {"name": "Luna"}\nprint(pet[0])', "Dictionaries don't use position numbers. Use the key.", 'pet = {"name": "Luna"}\nprint(pet["name"])'),
                    ],
                    [
                        code(
                            'Fill in the blank with the key that looks up the color.',
                            'car = {"color": "red", "wheels": 4}\nprint(car[___])',
                            'car = {"color": "red", "wheels": 4}\nprint(car["color"])',
                            [out("red")],
                            [
                                "Keys are written in quotes.",
                                'Replace ___ with "color".',
                                'The answer is: print(car["color"])',
                            ],
                        ),
                        code(
                            'Make a dictionary called player with "name" set to "Kai" and "level" set to 5. Print the level.',
                            "# Make player, then print its level\n",
                            'player = {"name": "Kai", "level": 5}\nprint(player["level"])',
                            [out("5"), out("5\nKai", append='print(player["name"])')],
                            [
                                'Use { } with "name": "Kai" and "level": 5, separated by a comma.',
                                'Look up with player["level"].',
                                'The answer is:\nplayer = {"name": "Kai", "level": 5}\nprint(player["level"])',
                            ],
                        ),
                        predict(
                            'd = {"a": 1, "b": 2}\nprint(d["b"] * 10)',
                            ["10", "b10", "2"],
                            'd["b"] is 2, times 10 is 20.',
                            ['What value goes with "b"?', "Then multiply."],
                        ),
                    ],
                    terms=[
                        term("dictionary", "A collection of key and value pairs, inside { }.", "a real dictionary: look up a word (the key) to find its meaning (the value)."),
                        term("key", 'The name you look up, like "age".', "the label on a locker."),
                    ],
                ),
                lesson(
                    "dict-update",
                    "Adding and changing",
                    """
To add a new pair or change an existing one, assign to a key:

scores["Ana"] = 10

If "Ana" is already a key, her value is replaced. If not, a new pair is added.
""",
                    """
A dictionary can only have each key once. So setting a key that exists overwrites it, and setting a new key creates it. It's like writing on a labeled locker: the same label always points to the same locker.
""",
                    'scores = {"Ana": 5}\nscores["Ana"] = 8\nscores["Ben"] = 3\nprint(scores)',
                    "Change one value, add another pair.",
                    [
                        walk('scores = {"Ana": 5}', "Starts with one pair."),
                        walk('scores["Ana"] = 8', "Ana is already there, so 5 becomes 8."),
                        walk('scores["Ben"] = 3', "Ben is new, so a new pair is added."),
                        walk("print(scores)", "{'Ana': 8, 'Ben': 3}"),
                    ],
                    [
                        oops('stock = {"apples": 3}\nstock["apples"] + 2\nprint(stock)', 'This works out 5 but doesn\'t save it. Use stock["apples"] += 2.', 'stock = {"apples": 3}\nstock["apples"] += 2\nprint(stock)'),
                    ],
                    [
                        code(
                            'Fill in the blank to add the key "c" with the value 3.',
                            'd = {"a": 1, "b": 2}\nd[___] = 3\nprint(d)',
                            'd = {"a": 1, "b": 2}\nd["c"] = 3\nprint(d)',
                            [vals("d")],
                            [
                                "The new key goes in the square brackets.",
                                'Replace ___ with "c".',
                                'The line is: d["c"] = 3',
                            ],
                        ),
                        code(
                            'The shop sold 2 apples. Use -= to take 2 away from stock["apples"]. Then print stock.',
                            'stock = {"apples": 10, "pears": 4}\n# Sell 2 apples\n\nprint(stock)',
                            'stock = {"apples": 10, "pears": 4}\nstock["apples"] -= 2\nprint(stock)',
                            [vals("stock")],
                            [
                                'The thing to change is stock["apples"].',
                                "Use -= 2 on it.",
                                'The line is: stock["apples"] -= 2',
                            ],
                            must=["-="],
                            wrong=['stock = {"apples": 8, "pears": 4}\nprint(stock)'],
                        ),
                        predict(
                            'd = {"x": 1}\nd["x"] = 5\nd["y"] = 5\nprint(len(d))',
                            ["3", "1", "5"],
                            'Setting "x" again replaces it. "y" is new. That makes 2 keys.',
                            ["Does setting an existing key add a new pair?", "Count the keys at the end."],
                        ),
                    ],
                ),
                lesson(
                    "dict-loop",
                    "Looping over a dictionary",
                    """
A for loop over a dictionary gives you each key. Use the key to get its value:

for name in ages:
    print(name, ages[name])

.items() gives you the key and value together: for name, age in ages.items():
""",
                    """
Each lap, the loop variable holds one key. Looking up dict[key] inside the loop gets that key's value. items() hands you both at once, which saves a lookup.
""",
                    'ages = {"Ana": 12, "Ben": 14}\nfor name in ages:\n    print(name, ages[name])\nfor name, age in ages.items():\n    print(f"{name} is {age}")',
                    "Two ways to loop through the same dictionary.",
                    [
                        walk("for name in ages:", "name holds each key: Ana, then Ben."),
                        walk("print(name, ages[name])", "Looks up each one's age."),
                        walk("for name, age in ages.items():", "items() gives both key and value each lap."),
                        walk('print(f"{name} is {age}")', "Ana is 12, Ben is 14."),
                    ],
                    [],
                    [
                        code(
                            "Fill in the blank to print each fruit's price.",
                            'prices = {"apple": 2, "melon": 5}\nfor fruit in prices:\n    print(fruit, prices[___])',
                            'prices = {"apple": 2, "melon": 5}\nfor fruit in prices:\n    print(fruit, prices[fruit])',
                            [out("apple 2\nmelon 5")],
                            [
                                "Look up the value using the loop variable.",
                                "Replace ___ with fruit.",
                                "The line is: print(fruit, prices[fruit])",
                            ],
                            must=["for"],
                        ),
                        code(
                            "Add up all the values in points with a loop. Print the total. It should print 60.",
                            'points = {"Ana": 10, "Ben": 20, "Cy": 30}\ntotal = 0\n# Loop here\n\nprint(total)',
                            'points = {"Ana": 10, "Ben": 20, "Cy": 30}\ntotal = 0\nfor name in points:\n    total += points[name]\nprint(total)',
                            [vals("total", out="60")],
                            [
                                "for name in points:",
                                "Inside: total += points[name]",
                                "The loop is:\nfor name in points:\n    total += points[name]",
                            ],
                            must=["for"],
                            wrong=['points = {"Ana": 10, "Ben": 20, "Cy": 30}\ntotal = 60\nprint(total)'],
                        ),
                        predict(
                            'd = {"a": 1, "b": 2}\nfor k in d:\n    print(k)',
                            ["1\n2", "a 1\nb 2", "{'a': 1, 'b': 2}"],
                            "Looping over a dictionary gives the keys.",
                            ["What does the loop variable hold for a dictionary?", "Keys or values?"],
                        ),
                    ],
                ),
                lesson(
                    "dict-in",
                    "Check before you look",
                    """
Looking up a key that isn't there causes a KeyError. Check first with in:

if "Ana" in scores:

Or use .get(key, default), which gives back the default instead of an error.
""",
                    """
in on a dictionary checks its keys. .get is a safe lookup: it tries the key, and if it's missing, hands you the backup value you chose. Counting things is a classic use: counts[word] = counts.get(word, 0) + 1.
""",
                    'counts = {}\nfor animal in ["cat", "dog", "cat"]:\n    counts[animal] = counts.get(animal, 0) + 1\nprint(counts)\nprint("cow" in counts)',
                    "Counting with .get, then checking with in.",
                    [
                        walk("counts = {}", "An empty dictionary."),
                        walk("counts[animal] = counts.get(animal, 0) + 1", "Get the count so far (0 if new), add 1, save it."),
                        walk("print(counts)", "{'cat': 2, 'dog': 1}"),
                        walk('print("cow" in counts)', "cow was never added: False."),
                    ],
                    [
                        oops('counts = {}\ncounts["cat"] += 1', '"cat" isn\'t a key yet, so there\'s nothing to add to. Use counts.get("cat", 0) + 1.', 'counts = {}\ncounts["cat"] = counts.get("cat", 0) + 1'),
                    ],
                    [
                        code(
                            "Fill in the blank so it checks for the key before looking it up.",
                            'ages = {"Ana": 12}\nif "Ana" ___ ages:\n    print(ages["Ana"])',
                            'ages = {"Ana": 12}\nif "Ana" in ages:\n    print(ages["Ana"])',
                            [out("12")],
                            [
                                "The word that checks is very short.",
                                "Replace ___ with in.",
                                'The line is: if "Ana" in ages:',
                            ],
                            must=["in"],
                        ),
                        code(
                            'The checker types a fruit. Print its price from prices. If it isn\'t there, print Not sold here.',
                            'prices = {"apple": 2, "kiwi": 1}\nfruit = input("Fruit? ")\n# Check, then print\n',
                            'prices = {"apple": 2, "kiwi": 1}\nfruit = input("Fruit? ")\nif fruit in prices:\n    print(prices[fruit])\nelse:\n    print("Not sold here")',
                            [has("2", stdin=["apple"]), has("Not sold here", stdin=["mango"])],
                            [
                                "if fruit in prices:",
                                "Inside, print(prices[fruit]). Then else: for Not sold here.",
                                'The answer is:\nif fruit in prices:\n    print(prices[fruit])\nelse:\n    print("Not sold here")',
                            ],
                            one_of=["in", "get"],
                            wrong=['prices = {"apple": 2, "kiwi": 1}\nfruit = input("Fruit? ")\nprint(prices[fruit])'],
                        ),
                        code(
                            "Count each letter in word using .get. Print counts. The checker looks at counts.",
                            'word = "hello"\ncounts = {}\n# Loop over word and count\n\nprint(counts)',
                            'word = "hello"\ncounts = {}\nfor ch in word:\n    counts[ch] = counts.get(ch, 0) + 1\nprint(counts)',
                            [vals("counts")],
                            [
                                "Loop with for ch in word:",
                                "Inside: counts[ch] = counts.get(ch, 0) + 1",
                                "The loop is:\nfor ch in word:\n    counts[ch] = counts.get(ch, 0) + 1",
                            ],
                            must=["for"],
                        ),
                    ],
                ),
            ],
        )
    ]
