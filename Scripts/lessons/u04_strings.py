from .dsl import ask, checkpoint, code, fix, lesson, oops, out, predict, term, unit, vals, walk


def units():
    return [
        unit(
            "strings",
            "Strings",
            "Work with text.",
            "textformat",
            [
                lesson(
                    "str-quotes",
                    "Two kinds of quotes",
                    """
A string can use double quotes "like this" or single quotes 'like this'. Both work the same.

The start and end quotes must match. That lets you put one kind of quote inside the other kind: "It's fun" works because the ' is inside double quotes.
""",
                    """
Python looks for the matching quote to know where the text ends. In 'It's fun', the ' in It's looks like the end, so Python gets confused. Using double quotes on the outside avoids that.
""",
                    "print(\"It's my turn\")\nprint('She said \"go\"')",
                    "Each line uses one kind of quote on the outside and the other kind inside.",
                    [
                        walk("print(\"It's my turn\")", "Double quotes outside, so the ' in It's is just a letter."),
                        walk("print('She said \"go\"')", "Single quotes outside, so the double quotes inside get printed."),
                    ],
                    [
                        oops("print('It's my turn')", "The ' in It's ends the string too early. Use double quotes outside.", "print(\"It's my turn\")"),
                        oops("print(\"Hi')", "The quotes don't match. Start and end with the same kind.", "print(\"Hi\")"),
                    ],
                    [
                        code(
                            "Fill in the blank so it prints: I'm ready",
                            'print("___")',
                            "print(\"I'm ready\")",
                            [out("I'm ready")],
                            [
                                "Type I'm ready in place of ___.",
                                "The ' in I'm is fine, because the outside quotes are double quotes.",
                                "The answer is: print(\"I'm ready\")",
                            ],
                            wrong=['print("Im ready")'],
                        ),
                        fix(
                            "This string breaks because of the ' in don't. Fix it so it prints: Don't stop",
                            "print('Don't stop')",
                            "print(\"Don't stop\")",
                            [out("Don't stop")],
                            [
                                "The ' inside don't is ending the string early.",
                                "Switch the outside quotes to double quotes.",
                                "The fixed line is: print(\"Don't stop\")",
                            ],
                        ),
                        ask(
                            "Which line works?",
                            "print('Say \"hi\"')",
                            ["print(\"Say \"hi\"\")", "print('Say hi\")", "print(Say hi)"],
                            "The outside quotes are single, so the double quotes inside are just characters.",
                            ["The outside quotes must match.", "The inside quotes must be the other kind."],
                        ),
                    ],
                ),
                lesson(
                    "str-concat",
                    "Joining text",
                    """
You can join strings together with +. "Ice" + "cream" makes "Icecream".

+ doesn't add a space by itself. If you want one, put it inside the quotes: "Hi " + name.
""",
                    """
With text, + means "stick these together end to end." Python only does exactly what you say, so it won't guess where a space should go. A space is a character too, so you add it yourself.
""",
                    'first = "Sky"\nsecond = "walker"\nprint(first + second)\nprint("Hi " + first)',
                    "Joining two strings, then joining with a space.",
                    [
                        walk('first = "Sky"', 'first holds "Sky".'),
                        walk('second = "walker"', 'second holds "walker".'),
                        walk("print(first + second)", "Sticks them together: Skywalker. No space."),
                        walk('print("Hi " + first)', 'The space is inside "Hi ", so you get Hi Sky.'),
                    ],
                    [
                        oops('name = "Mia"\nprint("Hi" + name)', "No space, so it prints HiMia. Put a space inside the quotes.", 'name = "Mia"\nprint("Hi " + name)'),
                        oops('age = 13\nprint("Age: " + age)', "+ can't join text and a number. Use a comma, or turn the number into text with str(age).", 'age = 13\nprint("Age: " + str(age))'),
                    ],
                    [
                        code(
                            "Fill in the blank so word holds bat + man joined together. It should print batman.",
                            'word = "bat" ___ "man"\nprint(word)',
                            'word = "bat" + "man"\nprint(word)',
                            [vals("word", out="batman")],
                            [
                                "Which symbol joins two strings?",
                                "Replace ___ with +.",
                                'The answer is: word = "bat" + "man"',
                            ],
                            must=["+"],
                        ),
                        code(
                            'name is "Leo". Print Hello, Leo using + to join "Hello, " and name.',
                            'name = "Leo"\n# Print Hello, Leo using +\n',
                            'name = "Leo"\nprint("Hello, " + name)',
                            [out("Hello, Leo")],
                            [
                                'Start with the text "Hello, " (with a space after the comma).',
                                "Then + and the variable name.",
                                'The answer is: print("Hello, " + name)',
                            ],
                            must=["+", "name"],
                            wrong=['name = "Leo"\nprint("Hello," + name)', 'print("Hello, Leo")'],
                        ),
                        predict(
                            'a = "up"\nb = "side"\nprint(b + a)',
                            ["upside", "side up", "b + a"],
                            "b comes first, so it's side then up with no space: sideup.",
                            ["Which variable comes first in the print?", "+ doesn't add a space."],
                        ),
                    ],
                    terms=[
                        term("joining (concatenation)", "Sticking strings together end to end with +.", "snapping two LEGO bricks together."),
                    ],
                ),
                lesson(
                    "str-fstring",
                    "Fill-in text with f-strings",
                    """
An f-string lets you drop variables right into text. Put an f before the opening quote, and put variable names inside curly brackets { }.

f"Hi {name}" becomes Hi Sam if name is "Sam". It works with numbers too, no str() needed.
""",
                    """
The f tells Python: "look inside this text for { } and fill them in." Python swaps each {name} for the value in that variable, then shows the finished text. It's like a form with blanks that Python fills out for you.
""",
                    'name = "Zoe"\nage = 12\nprint(f"{name} is {age} years old")',
                    "One f-string with two blanks filled in.",
                    [
                        walk('name = "Zoe"', 'name holds "Zoe".'),
                        walk("age = 12", "age holds 12."),
                        walk('print(f"{name} is {age} years old")', "Python fills {name} with Zoe and {age} with 12: Zoe is 12 years old"),
                    ],
                    [
                        oops('name = "Zoe"\nprint("Hi {name}")', "Without the f in front, the { } are shown as-is. Add f before the quote.", 'name = "Zoe"\nprint(f"Hi {name}")'),
                    ],
                    [
                        code(
                            "Fill in the blank with the variable name, so it prints: Hi Sam",
                            'name = "Sam"\nprint(f"Hi {___}")',
                            'name = "Sam"\nprint(f"Hi {name}")',
                            [out("Hi Sam")],
                            [
                                "Inside the curly brackets goes the name of the variable.",
                                "Replace ___ with name.",
                                'The answer is: print(f"Hi {name}")',
                            ],
                            must=['f"'],
                        ),
                        code(
                            "pet is Milo and legs is 4. Use one f-string to print: Milo has 4 legs",
                            'pet = "Milo"\nlegs = 4\n# One print with an f-string\n',
                            'pet = "Milo"\nlegs = 4\nprint(f"{pet} has {legs} legs")',
                            [out("Milo has 4 legs")],
                            [
                                'Start with print(f" and put {pet} first.',
                                "Use {legs} where the number goes.",
                                'The answer is: print(f"{pet} has {legs} legs")',
                            ],
                            must=['f"', "pet", "legs"],
                            wrong=['print("Milo has 4 legs")'],
                        ),
                        predict(
                            'x = 3\nprint(f"x is {x}")\nprint("x is {x}")',
                            ["x is 3\nx is 3", "x is {x}\nx is 3", "3 is 3\nx is {x}"],
                            "Only the first line has the f, so only it fills in {x}.",
                            ["Which line has an f before the quote?", "Without the f, curly brackets are shown as they are."],
                        ),
                    ],
                    terms=[
                        term("f-string", 'Text with an f in front, like f"Hi {name}". Variables in { } get filled in.', "a birthday card that says Happy birthday, ____! and you write the name in."),
                    ],
                ),
                lesson(
                    "str-upper",
                    "Text tools: upper and lower",
                    """
Strings come with built-in tools called methods. You use one by writing a dot after the string, then the method name and ( ).

word.upper() gives a SHOUTY copy in capitals. word.lower() gives a quiet copy in lowercase.
""",
                    """
A method is a tool that belongs to a value. The dot means "use this value's tool." upper() makes a new string. It doesn't change the original, so word is still the same afterward unless you save the result with =.
""",
                    'word = "Python"\nprint(word.upper())\nprint(word.lower())\nprint(word)',
                    "Two methods, then the original word, which hasn't changed.",
                    [
                        walk('word = "Python"', 'word holds "Python".'),
                        walk("print(word.upper())", "Shows PYTHON."),
                        walk("print(word.lower())", "Shows python."),
                        walk("print(word)", "Still Python. The methods made new copies."),
                    ],
                    [
                        oops('word = "hi"\nprint(word.upper)', "Without ( ) you're pointing at the tool, not using it. Add the brackets.", 'word = "hi"\nprint(word.upper())'),
                    ],
                    [
                        code(
                            "Fill in the blank with the method that makes capitals, so it prints HELLO.",
                            'word = "hello"\nprint(word.___())',
                            'word = "hello"\nprint(word.upper())',
                            [out("HELLO")],
                            [
                                "The method for capitals is called upper.",
                                "Replace ___ with upper.",
                                "The answer is: print(word.upper())",
                            ],
                            must=["upper"],
                        ),
                        code(
                            'shout is "STOP". Make a variable calm that holds shout in lowercase, then print calm.',
                            'shout = "STOP"\n# Make calm here\n',
                            'shout = "STOP"\ncalm = shout.lower()\nprint(calm)',
                            [vals("calm", out="stop")],
                            [
                                "Use the .lower() method on shout.",
                                "calm = shout.lower()",
                                "The answer is:\ncalm = shout.lower()\nprint(calm)",
                            ],
                            must=["lower"],
                            wrong=['calm = "stop"\nprint(calm)'],
                        ),
                        predict(
                            'name = "Ada"\nname.upper()\nprint(name)',
                            ["ADA", "ada", "name"],
                            "upper() made a capital copy, but it wasn't saved. name still holds Ada.",
                            ["Was the result of upper() saved with =?", "Methods make a new copy. The original stays."],
                        ),
                    ],
                    terms=[
                        term("method", "A tool that belongs to a value. You use it with a dot, like word.upper().", "the buttons on a TV remote. The remote is the value, the button is the tool."),
                    ],
                ),
                lesson(
                    "str-len",
                    "How long is it?",
                    """
len() counts how many characters a string has. Letters, spaces, and punctuation all count.

len("cat") is 3. len("hi there") is 8, because the space counts too.
""",
                    """
A string is a row of characters, one after another. len walks along the row and counts each one, including spaces. It gives back a number you can print or save.
""",
                    'word = "pizza"\nprint(len(word))\nprint(len("hi there"))',
                    "Counting characters, including a space.",
                    [
                        walk('word = "pizza"', "pizza has 5 letters."),
                        walk("print(len(word))", "len counts them and gives 5."),
                        walk('print(len("hi there"))', "h-i, space, t-h-e-r-e: 8 characters."),
                    ],
                    [
                        oops("print(len(12345))", "len works on text, not on plain numbers.", 'print(len("12345"))'),
                    ],
                    [
                        code(
                            "Fill in the blank so it prints how many letters are in the word.",
                            'word = "banana"\nprint(___(word))',
                            'word = "banana"\nprint(len(word))',
                            [out("6")],
                            [
                                "The tool that counts characters is len.",
                                "Replace ___ with len.",
                                "The answer is: print(len(word))",
                            ],
                            must=["len"],
                            wrong=['word = "banana"\nprint(6)'],
                        ),
                        code(
                            'name is "Robot". Make size hold the length of name, then print size.',
                            'name = "Robot"\n# Make size here\n',
                            'name = "Robot"\nsize = len(name)\nprint(size)',
                            [vals("size", out="5")],
                            [
                                "Use len(name).",
                                "Save it with size = ...",
                                "The answer is:\nsize = len(name)\nprint(size)",
                            ],
                            must=["len"],
                            wrong=["size = 5\nprint(size)"],
                        ),
                        predict(
                            'print(len("a b c"))',
                            ["3", "4", "6"],
                            "Three letters and two spaces make 5 characters.",
                            ["Do spaces count?", "Count every character between the quotes."],
                        ),
                    ],
                ),
                lesson(
                    "str-index",
                    "Letters by position",
                    """
Each character in a string has a position number, called an index. Counting starts at 0, not 1.

word[0] is the first character. word[1] is the second. word[-1] is the last one.
""",
                    """
Python counts how many steps from the start: the first letter is 0 steps away, so it's [0]. Negative numbers count from the end, so [-1] means one step back from the end, which is the last letter.
""",
                    'word = "robot"\nprint(word[0])\nprint(word[1])\nprint(word[-1])',
                    "Picking letters out of a word by position.",
                    [
                        walk('word = "robot"', "Positions: r is 0, o is 1, b is 2, o is 3, t is 4."),
                        walk("print(word[0])", "Position 0 is the first letter: r"),
                        walk("print(word[1])", "Position 1 is the second letter: o"),
                        walk("print(word[-1])", "-1 is the last letter: t"),
                    ],
                    [
                        oops('word = "cat"\nprint(word[3])', 'cat has positions 0, 1, and 2. There is no [3], so you get an IndexError.', 'word = "cat"\nprint(word[2])'),
                    ],
                    [
                        code(
                            "Fill in the blank to print the first letter of the word.",
                            'word = "zebra"\nprint(word[___])',
                            'word = "zebra"\nprint(word[0])',
                            [out("z")],
                            [
                                "Counting starts at 0.",
                                "The first position is 0.",
                                "The answer is: print(word[0])",
                            ],
                            wrong=['word = "zebra"\nprint(word[1])'],
                        ),
                        code(
                            'animal is "tiger". Print its last letter using a negative position.',
                            'animal = "tiger"\n# Print the last letter\n',
                            'animal = "tiger"\nprint(animal[-1])',
                            [out("r")],
                            [
                                "The last position can be written as -1.",
                                "Use square brackets after animal.",
                                "The answer is: print(animal[-1])",
                            ],
                            must=["[-1]"],
                            wrong=['print("r")'],
                        ),
                        predict(
                            'w = "code"\nprint(w[2])',
                            ["o", "c", "e"],
                            "c is 0, o is 1, d is 2.",
                            ["Start counting from 0.", "c is position 0."],
                        ),
                    ],
                    terms=[
                        term("index", "A character's position number. The first one is 0.", "floors in some buildings: the ground floor is 0, the next one up is 1."),
                    ],
                ),
                checkpoint(
                    "str-check",
                    "Checkpoint: strings",
                    "Read each program carefully. Watch for spaces, quotes, and the f in f-strings.",
                    [
                        predict(
                            'a = "fire"\nb = "fly"\nprint(a + b)',
                            ["fire fly", "a + b", "fire+fly"],
                            "+ joins strings with no space.",
                            ["Does + add a space?", "Join the two words end to end."],
                        ),
                        predict(
                            'n = 2\nprint(f"{n} dogs")',
                            ["{n} dogs", "n dogs", "2dogs"],
                            "The f-string fills {n} with 2.",
                            ["Is there an f before the quote?", "What's inside n?"],
                        ),
                        predict(
                            's = "Hello"\nprint(s[0], len(s))',
                            ["H 4", "e 5", "Hello 5"],
                            "s[0] is H and the length is 5.",
                            ["What's at position 0?", "How many letters are in Hello?"],
                        ),
                    ],
                ),
            ],
        )
    ]
