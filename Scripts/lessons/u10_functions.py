from .dsl import ask, checkpoint, code, fix, has, lesson, oops, out, predict, term, unit, vals, walk


def units():
    return [
        unit(
            "functions",
            "Functions",
            "Name a chunk of code and reuse it.",
            "function",
            [
                lesson(
                    "fn-define",
                    "Making a function",
                    """
A function is a chunk of code with a name. You make it once with def, then run it whenever you want by calling its name with ( ).

def cheer():
    print("Go team!")

cheer()

The def line ends with a colon, and the code inside is indented.
""",
                    """
def only teaches Python the recipe. Nothing runs yet. The code inside runs each time you call the function by writing its name with brackets. That's why you can define it once and use it many times.
""",
                    'def cheer():\n    print("Go team!")\n    print("Woo!")\n\ncheer()\ncheer()',
                    "Define once, call twice.",
                    [
                        walk("def cheer():", "Starts a function called cheer. Nothing is shown yet."),
                        walk('print("Go team!")', "Inside the function, indented."),
                        walk("cheer()", "Calls the function. Its two lines run. The second call runs them again."),
                    ],
                    [
                        oops('def hello():\n    print("Hi")', "This only defines the function. You need to call it with hello() to see anything.", 'def hello():\n    print("Hi")\n\nhello()'),
                        oops('def hello():\n    print("Hi")\n\nhello', "Without ( ), Python doesn't run the function.", 'def hello():\n    print("Hi")\n\nhello()'),
                    ],
                    [
                        code(
                            "Fill in the blank to call the function.",
                            'def wave():\n    print("Hello!")\n\n___',
                            'def wave():\n    print("Hello!")\n\nwave()',
                            [out("Hello!")],
                            [
                                "To call a function, write its name and brackets.",
                                "Replace ___ with wave().",
                                "The last line is: wave()",
                            ],
                            must=["def", "wave()"],
                        ),
                        code(
                            "Define a function called rules that prints No running, then call it 2 times.",
                            "# Define rules, then call it twice\n",
                            'def rules():\n    print("No running")\n\nrules()\nrules()',
                            [out("No running\nNo running")],
                            [
                                "Start with: def rules():",
                                "Indent the print. Then, with no indent, write rules() twice.",
                                'The answer is:\ndef rules():\n    print("No running")\n\nrules()\nrules()',
                            ],
                            must=["def"],
                            wrong=['print("No running")\nprint("No running")'],
                        ),
                        predict(
                            'def a():\n    print("A")\n\nprint("start")\na()',
                            ["A\nstart", "start", "start\nA\nA"],
                            "def doesn't run anything. start prints, then a() runs and prints A.",
                            ["Does def print anything by itself?", "When is a() called?"],
                        ),
                    ],
                    terms=[
                        term("function", "A named chunk of code you can run whenever you want.", "a recipe card in a drawer. You can cook it any time."),
                        term("call", "Running a function by writing its name with ( ).", "taking the recipe card out and cooking it."),
                    ],
                ),
                lesson(
                    "fn-params",
                    "Giving a function information",
                    """
A function can take information. Put a name inside the brackets of the def line. That name is called a parameter:

def greet(name):
    print("Hi", name)

When you call greet("Mo"), name holds "Mo" while the function runs. The value you pass in is called an argument.
""",
                    """
The parameter is like an empty variable that gets filled in each time you call the function. greet("Mo") fills name with "Mo". greet("Lu") fills it with "Lu". Same recipe, different ingredient.
""",
                    'def greet(name):\n    print("Hi", name)\n\ngreet("Mo")\ngreet("Lu")',
                    "One function, two different names.",
                    [
                        walk("def greet(name):", "name is a parameter, a slot for information."),
                        walk('print("Hi", name)', "Uses whatever was passed in."),
                        walk('greet("Mo")', 'name holds "Mo" this time: Hi Mo'),
                        walk('greet("Lu")', 'Now name holds "Lu": Hi Lu'),
                    ],
                    [
                        oops('def greet(name):\n    print("Hi", name)\n\ngreet()', "greet needs a value for name, but none was given. Put one in the brackets.", 'def greet(name):\n    print("Hi", name)\n\ngreet("Mo")'),
                    ],
                    [
                        code(
                            'Fill in the blank so the function is called with "Ivy".',
                            'def hello(name):\n    print("Hello", name)\n\nhello(___)',
                            'def hello(name):\n    print("Hello", name)\n\nhello("Ivy")',
                            [out("Hello Ivy")],
                            [
                                "Put the value to pass inside the brackets.",
                                'It\'s text, so use quotes: "Ivy"',
                                'The last line is: hello("Ivy")',
                            ],
                            must=["def"],
                        ),
                        code(
                            "Write a function square(n) that prints n * n. Call it with 3 and then with 5.",
                            "# Define square, then call it twice\n",
                            "def square(n):\n    print(n * n)\n\nsquare(3)\nsquare(5)",
                            [out("9\n25")],
                            [
                                "def square(n):",
                                "Inside: print(n * n). Then call square(3) and square(5).",
                                "The answer is:\ndef square(n):\n    print(n * n)\n\nsquare(3)\nsquare(5)",
                            ],
                            must=["def"],
                            wrong=["print(9)\nprint(25)"],
                        ),
                        code(
                            "A function can take two parameters. Write add(a, b) that prints a + b, then call add(2, 3).",
                            "# Define add with two parameters\n",
                            "def add(a, b):\n    print(a + b)\n\nadd(2, 3)",
                            [out("5"), out("5\n10", append="add(4, 6)")],
                            [
                                "def add(a, b): with a comma between the parameters.",
                                "Inside: print(a + b). Then add(2, 3).",
                                "The answer is:\ndef add(a, b):\n    print(a + b)\n\nadd(2, 3)",
                            ],
                            must=["def"],
                            wrong=["print(5)"],
                        ),
                    ],
                    terms=[
                        term("parameter", "A name in the def line's brackets that holds information passed in.", "a blank on a form, like Name: _____."),
                        term("argument", "The actual value you pass in when you call the function.", "what you write in the blank."),
                    ],
                ),
                lesson(
                    "fn-return",
                    "Giving a value back",
                    """
return sends a value back from a function to the code that called it. Then you can save it, print it, or use it in math:

def double(n):
    return n * 2

result = double(4)   # result is 8

A function stops as soon as it reaches return.
""",
                    """
print shows a value on the screen, but the rest of your program can't use it. return hands the value back, like a vending machine handing you a snack. Where the call was, Python puts the returned value.
""",
                    "def double(n):\n    return n * 2\n\nresult = double(4)\nprint(result)\nprint(double(10) + 1)",
                    "Using the returned value in two ways.",
                    [
                        walk("def double(n):", "A function with one parameter."),
                        walk("return n * 2", "Works out n * 2 and sends it back."),
                        walk("result = double(4)", "double(4) gives back 8, which is saved in result."),
                        walk("print(double(10) + 1)", "double(10) gives 20, plus 1 is 21."),
                    ],
                    [
                        oops("def double(n):\n    print(n * 2)\n\nx = double(4)\nprint(x + 1)", "The function prints but doesn't return, so x is None and the math fails. Use return.", "def double(n):\n    return n * 2\n\nx = double(4)\nprint(x + 1)"),
                    ],
                    [
                        code(
                            "Fill in the blank so the function gives back n + 10.",
                            "def add_ten(n):\n    ___ n + 10\n\nprint(add_ten(5))",
                            "def add_ten(n):\n    return n + 10\n\nprint(add_ten(5))",
                            [out("15"), out("15\n10", append="print(add_ten(0))")],
                            [
                                "The word that sends a value back is return.",
                                "Replace ___ with return.",
                                "The line is: return n + 10",
                            ],
                            must=["return"],
                        ),
                        code(
                            "Write triple(n) that returns n * 3. The checker will call it with different numbers.",
                            "def triple(n):\n    # return n times 3\n    pass",
                            "def triple(n):\n    return n * 3",
                            [out("12", append="print(triple(4))"), out("0\n30", append="print(triple(0))\nprint(triple(10))")],
                            [
                                "Replace pass with a return line.",
                                "return n * 3",
                                "The answer is:\ndef triple(n):\n    return n * 3",
                            ],
                            must=["return"],
                            wrong=["def triple(n):\n    print(n * 3)", "def triple(n):\n    return 12"],
                        ),
                        fix(
                            "This function prints instead of returning, so the total fails. Fix it so it prints 15.",
                            "def price(items):\n    print(items * 5)\n\ntotal = price(2) + price(1)\nprint(total)",
                            "def price(items):\n    return items * 5\n\ntotal = price(2) + price(1)\nprint(total)",
                            [out("15")],
                            [
                                "The function needs to give back its answer.",
                                "Change print to return inside the function.",
                                "The function's line should be: return items * 5",
                            ],
                            must=["return"],
                        ),
                    ],
                    terms=[
                        term("return", "Sends a value back from a function to where it was called.", "a vending machine handing you the snack you paid for."),
                    ],
                ),
                lesson(
                    "fn-reuse",
                    "Functions that decide",
                    """
Functions can use if, loops, and anything else you know. A function that answers a question often returns True or False:

def is_even(n):
    return n % 2 == 0

Functions keep your code tidy: write the idea once, give it a good name, and use it everywhere.
""",
                    """
n % 2 == 0 is already a True or False answer, so you can return it directly. Once a function works, you can trust it and stop thinking about how it works inside. That's how big programs stay manageable.
""",
                    'def is_even(n):\n    return n % 2 == 0\n\nfor n in range(1, 5):\n    if is_even(n):\n        print(n, "is even")',
                    "A function used inside a loop and an if.",
                    [
                        walk("return n % 2 == 0", "Gives back True for even numbers, False for odd."),
                        walk("for n in range(1, 5):", "Try 1, 2, 3, 4."),
                        walk("if is_even(n):", "Calls the function. Its answer decides the if."),
                        walk('print(n, "is even")', "Runs for 2 and 4."),
                    ],
                    [
                        oops("def bigger(a, b):\n    if a > b:\n        return a\n\nprint(bigger(2, 5))", "When a is not bigger, the function reaches the end without a return and gives back None. Return b in that case.", "def bigger(a, b):\n    if a > b:\n        return a\n    return b\n\nprint(bigger(2, 5))"),
                    ],
                    [
                        code(
                            "Fill in the blank so the function returns True when n is bigger than 10.",
                            "def is_big(n):\n    return n ___ 10\n\nprint(is_big(50))",
                            "def is_big(n):\n    return n > 10\n\nprint(is_big(50))",
                            [out("True"), out("True\nFalse", append="print(is_big(3))"), out("True\nFalse", append="print(is_big(10))")],
                            [
                                "Which symbol means greater than?",
                                "Replace ___ with >.",
                                "The line is: return n > 10",
                            ],
                            must=["return"],
                        ),
                        code(
                            "Write smaller(a, b) that returns whichever number is smaller.",
                            "def smaller(a, b):\n    # return the smaller one\n    pass",
                            "def smaller(a, b):\n    if a < b:\n        return a\n    return b",
                            [out("2", append="print(smaller(2, 9))"), out("1", append="print(smaller(5, 1))"), out("4", append="print(smaller(4, 4))")],
                            [
                                "Use if a < b: and return a inside it.",
                                "After the if, return b.",
                                "The answer is:\ndef smaller(a, b):\n    if a < b:\n        return a\n    return b",
                            ],
                            must=["return", "if"],
                            wrong=["def smaller(a, b):\n    return a", "def smaller(a, b):\n    if a < b:\n        return a"],
                        ),
                        code(
                            "Write count_vowels(word) that returns how many of its letters are in \"aeiou\".",
                            "def count_vowels(word):\n    count = 0\n    # loop over word\n    return count",
                            'def count_vowels(word):\n    count = 0\n    for ch in word:\n        if ch in "aeiou":\n            count += 1\n    return count',
                            [out("2", append='print(count_vowels("hello"))'), out("0", append='print(count_vowels("xyz"))'), out("5", append='print(count_vowels("aeiou"))')],
                            [
                                "Loop with for ch in word:",
                                'Inside the loop: if ch in "aeiou": then count += 1.',
                                'The loop is:\n    for ch in word:\n        if ch in "aeiou":\n            count += 1',
                            ],
                            must=["for", "return"],
                            wrong=["def count_vowels(word):\n    return 2"],
                        ),
                    ],
                ),
                checkpoint(
                    "fn-check",
                    "Checkpoint: functions",
                    "Remember: def only defines. Calling runs it. return gives a value back.",
                    [
                        predict("def f(x):\n    return x + 1\n\nprint(f(f(1)))", ["2", "f(2)", "11"], "f(1) is 2, then f(2) is 3.", ["Work from the inside out.", "What is f(1)?"]),
                        predict('def hi():\n    print("hi")\n\nhi()\nhi()', ["hi", "hihi", "None"], "Two calls, two lines.", ["How many times is hi() called?", "Each call prints once."]),
                        predict("def g(n):\n    return n * 2\n    print(n)\n\nprint(g(5))", ["5\n10", "5", "None"], "return stops the function, so the print inside never runs.", ["What happens when a function reaches return?", "Does the inside print run?"]),
                    ],
                ),
            ],
        )
    ]
