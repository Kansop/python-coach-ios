from .dsl import ask, code, has, lesson, oops, out, predict, project, step, term, unit, vals, walk

BANK_1 = "class BankAccount:\n    def __init__(self, owner):\n        self.owner = owner\n        self.balance = 0\n\nacct = BankAccount(\"Ana\")\nprint(acct.owner, acct.balance)"
BANK_2 = "class BankAccount:\n    def __init__(self, owner):\n        self.owner = owner\n        self.balance = 0\n\n    def deposit(self, amount):\n        self.balance += amount\n\nacct = BankAccount(\"Ana\")\nacct.deposit(50)\nprint(acct.owner, acct.balance)"
BANK_3 = "class BankAccount:\n    def __init__(self, owner):\n        self.owner = owner\n        self.balance = 0\n\n    def deposit(self, amount):\n        self.balance += amount\n\n    def withdraw(self, amount):\n        if amount > self.balance:\n            print(\"Not enough money\")\n        else:\n            self.balance -= amount\n\nacct = BankAccount(\"Ana\")\nacct.deposit(50)\nacct.withdraw(80)\nacct.withdraw(20)\nprint(acct.owner, acct.balance)"
BANK_4 = BANK_3.replace("\n\nacct = BankAccount", "\n\n    def report(self):\n        return f\"{self.owner} has ${self.balance}\"\n\nacct = BankAccount").replace("print(acct.owner, acct.balance)", "print(acct.report())")


def units():
    return [
        unit(
            "bonus-classes",
            "Bonus: classes",
            "Make your own kinds of things. For when you feel ready.",
            "cube.fill",
            [
                lesson(
                    "class-init",
                    "A first class",
                    """
A class is a blueprint for making your own kind of thing, called an object. Each object keeps its own data.

class Pet:
    def __init__(self, name):
        self.name = name

pet = Pet("Luna") makes a Pet object, and pet.name is "Luna".

__init__ (two underscores on each side) runs automatically when an object is made. self means "this object."
""",
                    """
Calling Pet("Luna") makes a new object and runs __init__ with self set to that new object and name set to "Luna". self.name = name saves the name inside the object, so it stays with that pet.
""",
                    'class Pet:\n    def __init__(self, name):\n        self.name = name\n\npet = Pet("Luna")\nprint(pet.name)',
                    "A blueprint, and one object made from it.",
                    [
                        walk("class Pet:", "Starts the blueprint for Pet objects."),
                        walk("def __init__(self, name):", "The setup function. It runs when a Pet is made."),
                        walk("self.name = name", "Stores the name inside this pet."),
                        walk('pet = Pet("Luna")', "Makes a Pet named Luna."),
                        walk("print(pet.name)", "Reads the name: Luna"),
                    ],
                    [
                        oops('class Pet:\n    def __init__(self, name):\n        name = name\n\npet = Pet("Luna")\nprint(pet.name)', "Without self., the name is forgotten when __init__ ends. Use self.name = name.", 'class Pet:\n    def __init__(self, name):\n        self.name = name\n\npet = Pet("Luna")\nprint(pet.name)'),
                    ],
                    [
                        code(
                            "Fill in the blank so the name is stored in the object.",
                            'class Pet:\n    def __init__(self, name):\n        ___ = name\n\nprint(Pet("Rex").name)',
                            'class Pet:\n    def __init__(self, name):\n        self.name = name\n\nprint(Pet("Rex").name)',
                            [out("Rex")],
                            ["Store it on self.", "Replace ___ with self.name.", "The line is: self.name = name"],
                            must=["self.name"],
                        ),
                        code(
                            "Make a class Car with __init__(self, color) that stores self.color. Make car = Car(\"red\") and print car.color.",
                            "# class Car here\n",
                            'class Car:\n    def __init__(self, color):\n        self.color = color\n\ncar = Car("red")\nprint(car.color)',
                            [out("red"), out("red\nblue", append='print(Car("blue").color)')],
                            ["class Car: then def __init__(self, color): indented.", "Inside: self.color = color. Then make the car below the class.", 'The answer is:\nclass Car:\n    def __init__(self, color):\n        self.color = color\n\ncar = Car("red")\nprint(car.color)'],
                            must=["class", "self"],
                        ),
                        ask("What does self mean inside a class?", "The object the code is working on", ["The class name", "The person using the app", "A Python keyword for print"], "self is the object itself, so self.name is this object's name.", ["Think: whose name is self.name?", "Each object has its own self."]),
                    ],
                    terms=[
                        term("class", "A blueprint for making your own kind of object.", "a cookie cutter."),
                        term("object", "One thing made from a class, with its own data.", "one cookie."),
                    ],
                ),
                lesson(
                    "class-method",
                    "Methods: things objects can do",
                    """
A method is a function inside a class. Its first parameter is always self, so it can use the object's data:

def speak(self):
    return self.name + " says hi"

Call it with a dot: pet.speak().
""",
                    """
When you write pet.speak(), Python passes pet in as self automatically. That's why you don't write self in the brackets when you call it.
""",
                    'class Pet:\n    def __init__(self, name):\n        self.name = name\n\n    def speak(self):\n        return self.name + " says hi"\n\nprint(Pet("Milo").speak())',
                    "A method that uses the object's own name.",
                    [
                        walk("def speak(self):", "A method. self is the pet it's called on."),
                        walk('return self.name + " says hi"', "Uses this pet's name."),
                        walk('print(Pet("Milo").speak())', "Milo says hi"),
                    ],
                    [
                        oops('class Pet:\n    def speak():\n        return "hi"\n\nprint(Pet().speak())', "Methods need self as their first parameter.", 'class Pet:\n    def speak(self):\n        return "hi"\n\nprint(Pet().speak())'),
                    ],
                    [
                        code(
                            "Fill in the blank so the method can use the object.",
                            'class Robot:\n    def __init__(self, name):\n        self.name = name\n\n    def beep(___):\n        return self.name + " beeps"\n\nprint(Robot("R2").beep())',
                            'class Robot:\n    def __init__(self, name):\n        self.name = name\n\n    def beep(self):\n        return self.name + " beeps"\n\nprint(Robot("R2").beep())',
                            [out("R2 beeps")],
                            ["Every method's first parameter is the same word.", "Replace ___ with self.", "The line is: def beep(self):"],
                            must=["self"],
                        ),
                        code(
                            'Add a method area(self) to Box that returns self.width * self.height.',
                            "class Box:\n    def __init__(self, width, height):\n        self.width = width\n        self.height = height\n\n    # add area here\n",
                            "class Box:\n    def __init__(self, width, height):\n        self.width = width\n        self.height = height\n\n    def area(self):\n        return self.width * self.height",
                            [out("6", append="print(Box(2, 3).area())"), out("0", append="print(Box(0, 9).area())")],
                            ["def area(self): indented inside the class.", "return self.width * self.height", "The method is:\n    def area(self):\n        return self.width * self.height"],
                            must=["def area", "return"],
                        ),
                        predict('class A:\n    def __init__(self):\n        self.n = 1\n\n    def up(self):\n        self.n += 1\n\na = A()\na.up()\na.up()\nprint(a.n)', ["1", "2", "None"], "n starts at 1 and goes up twice: 3.", ["What is n after __init__?", "Each up() adds 1."]),
                    ],
                    terms=[term("method", "A function that belongs to a class.", "a button on a toy that makes it do something.")],
                ),
                lesson(
                    "class-two",
                    "Each object has its own data",
                    """
You can make many objects from one class. Each one keeps its own data, so changing one doesn't change the others.
""",
                    """
self.value belongs to one object. a.value and b.value are stored in different places, like two lockers with the same label on different floors.
""",
                    "class Counter:\n    def __init__(self):\n        self.value = 0\n\na = Counter()\nb = Counter()\na.value = 5\nprint(a.value)\nprint(b.value)",
                    "Two counters. Changing one leaves the other alone.",
                    [
                        walk("a = Counter()", "First object, value 0."),
                        walk("b = Counter()", "Second object, its own value 0."),
                        walk("a.value = 5", "Only a changes."),
                        walk("print(b.value)", "b is still 0."),
                    ],
                    [],
                    [
                        code(
                            'Fill in the blank to make a second Player named "Bo".',
                            'class Player:\n    def __init__(self, name):\n        self.name = name\n\np1 = Player("Ana")\np2 = ___\nprint(p1.name, p2.name)',
                            'class Player:\n    def __init__(self, name):\n        self.name = name\n\np1 = Player("Ana")\np2 = Player("Bo")\nprint(p1.name, p2.name)',
                            [out("Ana Bo")],
                            ["Make it the same way as p1.", 'Replace ___ with Player("Bo").', 'The line is: p2 = Player("Bo")'],
                            must=["Player("],
                        ),
                        code(
                            "Make a list of three Player objects named Ana, Bo, and Cy, then loop over the list and print each name.",
                            'class Player:\n    def __init__(self, name):\n        self.name = name\n\n# make the list, then loop\n',
                            'class Player:\n    def __init__(self, name):\n        self.name = name\n\nteam = [Player("Ana"), Player("Bo"), Player("Cy")]\nfor p in team:\n    print(p.name)',
                            [out("Ana\nBo\nCy")],
                            ['A list can hold objects: [Player("Ana"), ...]', "Loop: for p in team: print(p.name)", 'The answer is:\nteam = [Player("Ana"), Player("Bo"), Player("Cy")]\nfor p in team:\n    print(p.name)'],
                            must=["for", "Player("],
                            wrong=['print("Ana")\nprint("Bo")\nprint("Cy")'],
                        ),
                        predict('class Box:\n    def __init__(self, n):\n        self.n = n\n\nx = Box(1)\ny = Box(2)\nx.n = y.n + 10\nprint(x.n, y.n)', ["11 2", "12 12", "1 2"], "x.n becomes 2 + 10 = 12. y.n stays 2.", ["What is y.n?", "Only x.n changes."]),
                    ],
                ),
                project(
                    "proj-bank",
                    "Project: bank account",
                    """
You'll build a BankAccount class in 4 steps: store the owner and balance, add deposit, add withdraw with a safety check, and add a report.
""",
                    """
A class keeps the balance and the actions that change it together. Nobody can withdraw more than they have, because withdraw checks first.
""",
                    [
                        step(
                            "Step 1. Finish __init__ so each account stores self.owner and starts self.balance at 0.",
                            "class BankAccount:\n    def __init__(self, owner):\n        # store owner, start balance at 0\n        pass\n\nacct = BankAccount(\"Ana\")\nprint(acct.owner, acct.balance)",
                            BANK_1,
                            [out("Ana 0"), out("Ana 0\nBo 0", append='b = BankAccount("Bo")\nprint(b.owner, b.balance)')],
                            ["Replace pass with two lines.", "self.owner = owner and self.balance = 0", "The two lines are:\n        self.owner = owner\n        self.balance = 0"],
                            must=["self.balance"],
                        ),
                        step(
                            "Step 2. Add a method deposit(self, amount) that adds amount to self.balance. Then call acct.deposit(50) before the print.",
                            BANK_1 + "\n\n# Step 2: add deposit inside the class, then deposit 50\n",
                            BANK_2,
                            [out("Ana 50"), out("Ana 50\n15", append='b = BankAccount("Bo")\nb.deposit(5)\nb.deposit(10)\nprint(b.balance)')],
                            ["def deposit(self, amount): inside the class.", "self.balance += amount", "The method is:\n    def deposit(self, amount):\n        self.balance += amount"],
                            must=["def deposit"],
                        ),
                        step(
                            "Step 3. Add withdraw(self, amount). If amount is more than the balance, print Not enough money. Otherwise take it away. Then try acct.withdraw(80) and acct.withdraw(20).",
                            BANK_2 + "\n\n# Step 3: add withdraw with a safety check\n",
                            BANK_3,
                            [out("Not enough money\nAna 30"), has("Not enough money", append='b = BankAccount("Bo")\nb.withdraw(1)'), out("Not enough money\nAna 30\n0", append='c = BankAccount("Cy")\nc.deposit(10)\nc.withdraw(10)\nprint(c.balance)')],
                            ["def withdraw(self, amount): with an if amount > self.balance:", "In the else: self.balance -= amount", 'The method is:\n    def withdraw(self, amount):\n        if amount > self.balance:\n            print("Not enough money")\n        else:\n            self.balance -= amount'],
                            must=["def withdraw", "if"],
                        ),
                        step(
                            'Step 4. Add report(self) that returns a sentence like Ana has $30, using an f-string. Print acct.report() at the end instead.',
                            BANK_3 + "\n\n# Step 4: add report and print it\n",
                            BANK_4,
                            [has("Ana has $30"), has("Bo has $0", append='print(BankAccount("Bo").report())')],
                            ["def report(self): inside the class.", 'return f"{self.owner} has ${self.balance}"', 'The method is:\n    def report(self):\n        return f"{self.owner} has ${self.balance}"'],
                            must=["def report", "return"],
                        ),
                    ],
                    example="class Jar:\n    def __init__(self):\n        self.coins = 0\n\n    def add(self, n):\n        self.coins += n\n\njar = Jar()\njar.add(3)\nprint(jar.coins)",
                    note="A coin jar is a tiny version of a bank account.",
                    walkthrough=[
                        walk("self.coins = 0", "Every jar starts empty."),
                        walk("self.coins += n", "add() changes this jar's coins."),
                        walk("print(jar.coins)", "3"),
                    ],
                ),
            ],
            optional=True,
        )
    ]
