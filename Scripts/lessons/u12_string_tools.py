from .dsl import ask, checkpoint, code, fix, has, lesson, oops, out, predict, term, unit, vals, walk


def units():
    return [
        unit(
            "string-tools",
            "Text tools",
            "Clean, search, split, and change text.",
            "wand.and.stars",
            [
                lesson(
                    "str-strip",
                    "Trim the edges",
                    """
.strip() removes spaces from the start and end of a string. Spaces in the middle stay.

People often type extra spaces by accident, so cleaning input with .strip() is a good habit.
""",
                    """
strip looks at each end of the string and removes blank characters until it reaches a real one. Like all string methods, it makes a new string and leaves the original alone, so save the result.
""",
                    'raw = "   hi there   "\nclean = raw.strip()\nprint("[" + clean + "]")',
                    "The brackets show exactly where the text starts and ends.",
                    [
                        walk('raw = "   hi there   "', "Extra spaces at both ends."),
                        walk("clean = raw.strip()", "A trimmed copy: \"hi there\". The middle space stays."),
                        walk('print("[" + clean + "]")', "[hi there]"),
                    ],
                    [
                        oops('name = "  Ana  "\nname.strip()\nprint("[" + name + "]")', "strip made a clean copy but it wasn't saved. Use name = name.strip().", 'name = "  Ana  "\nname = name.strip()\nprint("[" + name + "]")'),
                    ],
                    [
                        code(
                            "Fill in the blank to trim the spaces.",
                            'word = "  cat  "\nprint(word.___())',
                            'word = "  cat  "\nprint(word.strip())',
                            [out("cat")],
                            [
                                "The method that trims the edges.",
                                "Replace ___ with strip.",
                                "The answer is: print(word.strip())",
                            ],
                            must=["strip"],
                        ),
                        code(
                            'The checker types an answer with extra spaces. Strip it, then print Correct if it equals yes, otherwise print Wrong.',
                            'answer = input("Ready? ")\n# Clean the answer, then check it\n',
                            'answer = input("Ready? ")\nanswer = answer.strip()\nif answer == "yes":\n    print("Correct")\nelse:\n    print("Wrong")',
                            [has("Correct", stdin=["  yes "]), has("Wrong", stdin=["no"]), has("Correct", stdin=["yes"])],
                            [
                                "First: answer = answer.strip()",
                                'Then: if answer == "yes":',
                                'The answer is:\nanswer = answer.strip()\nif answer == "yes":\n    print("Correct")\nelse:\n    print("Wrong")',
                            ],
                            must=["strip", "if"],
                            wrong=['answer = input("Ready? ")\nif answer == "yes":\n    print("Correct")\nelse:\n    print("Wrong")'],
                        ),
                        predict(
                            'print(len("  ab  ".strip()))',
                            ["6", "4", "0"],
                            "After stripping, only ab is left: 2 characters.",
                            ["What's left after removing the outside spaces?", "Then count."],
                        ),
                    ],
                ),
                lesson(
                    "str-replace",
                    "Swap some text",
                    """
.replace(old, new) gives a copy of the string with every old part swapped for new:

"I like cats".replace("cats", "dogs") gives "I like dogs".
""",
                    """
replace searches the whole string for the old text and swaps each match. If it finds nothing, you get back the same text. Matching is exact, so capitals matter.
""",
                    'msg = "Hello, World"\nprint(msg.replace("World", "Sam"))\nprint("banana".replace("a", "o"))',
                    "Swapping one word, then every a.",
                    [
                        walk('print(msg.replace("World", "Sam"))', "Hello, Sam"),
                        walk('print("banana".replace("a", "o"))', "Every a becomes o: bonono"),
                    ],
                    [
                        oops('text = "I like Cats"\nprint(text.replace("cats", "dogs"))', '"cats" doesn\'t match "Cats", so nothing changes.', 'text = "I like Cats"\nprint(text.replace("Cats", "dogs"))'),
                    ],
                    [
                        code(
                            "Fill in the blank so cold becomes hot.",
                            'weather = "It is cold"\nprint(weather.replace("cold", ___))',
                            'weather = "It is cold"\nprint(weather.replace("cold", "hot"))',
                            [out("It is hot")],
                            [
                                "The second thing in the brackets is the new text.",
                                'Replace ___ with "hot".',
                                'The answer is: print(weather.replace("cold", "hot"))',
                            ],
                            must=["replace"],
                        ),
                        code(
                            "Replace every space in phrase with an underscore _ and print it.",
                            'phrase = "my cool game"\n# Use replace\n',
                            'phrase = "my cool game"\nprint(phrase.replace(" ", "_"))',
                            [out("my_cool_game")],
                            [
                                'The old part is a space: " "',
                                'The new part is "_".',
                                'The answer is: print(phrase.replace(" ", "_"))',
                            ],
                            must=["replace"],
                            wrong=['print("my_cool_game")'],
                        ),
                        predict(
                            'print("aaa".replace("a", "ab"))',
                            ["ab", "aab", "abaa"],
                            "Each of the three a's becomes ab: ababab.",
                            ["How many a's are there?", "Each one is swapped."],
                        ),
                    ],
                ),
                lesson(
                    "str-split",
                    "Split into words",
                    """
.split() breaks a string into a list of words, splitting wherever there are spaces.

"red green blue".split() gives ["red", "green", "blue"].

You can split on something else too: "a,b,c".split(",").
""",
                    """
split walks along the string and cuts it at each separator, collecting the pieces in a list. Once you have a list, you can loop over the words, count them with len, or pick one by index.
""",
                    'sentence = "the quick brown fox"\nwords = sentence.split()\nprint(words)\nprint(len(words))\nprint(words[-1])',
                    "A sentence becomes a list of words.",
                    [
                        walk("words = sentence.split()", "Cuts at the spaces: four words in a list."),
                        walk("print(words)", "['the', 'quick', 'brown', 'fox']"),
                        walk("print(len(words))", "4 words."),
                        walk("print(words[-1])", "The last word: fox"),
                    ],
                    [
                        oops('data = "a,b,c"\nprint(data.split())', "There are no spaces, so split() gives one piece. Split on the comma.", 'data = "a,b,c"\nprint(data.split(","))'),
                    ],
                    [
                        code(
                            "Fill in the blank to split the sentence into words, then print how many there are.",
                            'line = "I love to code"\nwords = line.___()\nprint(len(words))',
                            'line = "I love to code"\nwords = line.split()\nprint(len(words))',
                            [out("4")],
                            [
                                "The method that breaks text into a list of words.",
                                "Replace ___ with split.",
                                "The line is: words = line.split()",
                            ],
                            must=["split"],
                        ),
                        code(
                            "Split csv on commas and print each item on its own line with a loop.",
                            'csv = "milk,eggs,bread"\n# Split, then loop\n',
                            'csv = "milk,eggs,bread"\nfor item in csv.split(","):\n    print(item)',
                            [out("milk\neggs\nbread")],
                            [
                                'csv.split(",") gives a list.',
                                "Loop over that list and print each item.",
                                'The answer is:\nfor item in csv.split(","):\n    print(item)',
                            ],
                            must=["split", "for"],
                            wrong=['print("milk")\nprint("eggs")\nprint("bread")'],
                        ),
                        predict(
                            'print("a-b-c".split("-")[1])',
                            ["a", "-", "a-b-c"],
                            'Splitting on "-" gives ["a", "b", "c"]. Position 1 is b.',
                            ["What list does split make?", "Position 1 is the second item."],
                        ),
                    ],
                ),
                lesson(
                    "str-starts",
                    "Starts with, ends with",
                    """
.startswith(text) is True when a string begins with that text. .endswith(text) checks the end.

"photo.png".endswith(".png") is True.
""",
                    """
These methods answer a yes-or-no question, so they fit right into an if. They're tidier than picking letters out one by one, and they work for any length of text.
""",
                    'file = "song.mp3"\nprint(file.endswith(".mp3"))\nprint(file.startswith("pic"))',
                    "Checking the end and the start of a file name.",
                    [
                        walk('print(file.endswith(".mp3"))', "song.mp3 does end with .mp3: True."),
                        walk('print(file.startswith("pic"))', "It starts with song, not pic: False."),
                    ],
                    [
                        oops('word = "Hello"\nprint(word.startswith("h"))', 'Capitals matter. "Hello" starts with "H", not "h".', 'word = "Hello"\nprint(word.startswith("H"))'),
                    ],
                    [
                        code(
                            'Fill in the blank to check whether name starts with "Dr".',
                            'name = "Dr Who"\nprint(name.___("Dr"))',
                            'name = "Dr Who"\nprint(name.startswith("Dr"))',
                            [out("True")],
                            [
                                "The method checks the beginning.",
                                "Replace ___ with startswith.",
                                'The answer is: print(name.startswith("Dr"))',
                            ],
                            must=["startswith"],
                        ),
                        code(
                            'Loop over files and print only the ones that end with ".png".',
                            'files = ["a.png", "b.txt", "c.png"]\n# Loop and check\n',
                            'files = ["a.png", "b.txt", "c.png"]\nfor f in files:\n    if f.endswith(".png"):\n        print(f)',
                            [out("a.png\nc.png")],
                            [
                                "for f in files:",
                                'Inside: if f.endswith(".png"): then print(f).',
                                'The answer is:\nfor f in files:\n    if f.endswith(".png"):\n        print(f)',
                            ],
                            must=["endswith", "for"],
                            wrong=['print("a.png")\nprint("c.png")'],
                        ),
                        predict(
                            'w = "sunshine"\nprint(w.startswith("sun"), w.endswith("sun"))',
                            ["True True", "False True", "sun sun"],
                            "It starts with sun but ends with shine.",
                            ["Check the start, then the end.", "Each one gives True or False."],
                        ),
                    ],
                ),
                lesson(
                    "str-count",
                    "Count and find",
                    """
.count(text) tells you how many times something appears in a string.

.find(text) tells you the position where it first appears, or -1 if it isn't there.
""",
                    """
count scans the whole string and tallies every match. find stops at the first match and gives its index. -1 is find's way of saying "not found," since no real position is ever negative from find.
""",
                    'text = "mississippi"\nprint(text.count("s"))\nprint(text.find("ss"))\nprint(text.find("z"))',
                    "Counting and finding inside one word.",
                    [
                        walk('print(text.count("s"))', "There are 4 s's."),
                        walk('print(text.find("ss"))', "The first ss starts at position 2."),
                        walk('print(text.find("z"))', "No z, so -1."),
                    ],
                    [],
                    [
                        code(
                            'Fill in the blank to count the letter o.',
                            'word = "balloon"\nprint(word.___("o"))',
                            'word = "balloon"\nprint(word.count("o"))',
                            [out("2")],
                            [
                                "The method that tallies matches.",
                                "Replace ___ with count.",
                                'The answer is: print(word.count("o"))',
                            ],
                            must=["count"],
                        ),
                        code(
                            'The checker types a sentence. Print how many words are in it, using split and len.',
                            'text = input("Sentence? ")\n# Count the words\n',
                            'text = input("Sentence? ")\nprint(len(text.split()))',
                            [out("Sentence? I like dogs\n3", stdin=["I like dogs"]), out("Sentence? Hello\n1", stdin=["Hello"])],
                            [
                                "text.split() gives a list of words.",
                                "len of that list is the word count.",
                                "The answer is: print(len(text.split()))",
                            ],
                            must=["split", "len"],
                        ),
                        predict(
                            'print("hello".find("l"))',
                            ["3", "-1", "l"],
                            "h is 0, e is 1, the first l is at 2.",
                            ["Positions start at 0.", "find gives the first match."],
                        ),
                    ],
                ),
            ],
        )
    ]
