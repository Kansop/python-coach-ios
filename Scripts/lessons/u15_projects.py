from .dsl import has, out, project, step, term, unit, vals, walk


def chain(first_starter, specs):
    """Build project steps. Each later step's backup starter is the step before's answer plus a note."""
    steps = []
    previous = None
    for index, spec in enumerate(specs):
        prompt, note, solution, tests, hints = spec[:5]
        extra = spec[5] if len(spec) > 5 else {}
        starter = first_starter if index == 0 else previous + "\n\n# Step " + str(index + 1) + ": " + note + "\n"
        steps.append(step(prompt, starter, solution, tests, hints, **extra))
        previous = solution
    return steps


TODO_1 = 'todos = ["homework", "feed the cat", "practice"]\nfor task in todos:\n    print("-", task)'
TODO_2 = 'todos = ["homework", "feed the cat", "practice"]\nnumber = 1\nfor task in todos:\n    print(f"{number}. {task}")\n    number += 1'
TODO_3 = 'todos = ["homework", "feed the cat", "practice"]\nnew = input("New task: ")\ntodos.append(new)\nnumber = 1\nfor task in todos:\n    print(f"{number}. {task}")\n    number += 1'
TODO_4 = TODO_3 + '\ndone = int(input("Which number is done? "))\ntodos.pop(done - 1)\nprint("Tasks left:", len(todos))'

GRADE_1 = "scores = [88, 92, 75]\ntotal = 0\nfor s in scores:\n    total += s\nprint(\"Total:\", total)"
GRADE_2 = GRADE_1 + "\naverage = total / len(scores)\nprint(\"Average:\", round(average, 1))"
GRADE_FN = 'def letter(avg):\n    if avg >= 90:\n        return "A"\n    elif avg >= 80:\n        return "B"\n    elif avg >= 70:\n        return "C"\n    else:\n        return "Keep practicing"\n\n'
GRADE_3 = GRADE_FN + GRADE_2 + '\nprint("Grade:", letter(average))'
GRADE_4 = GRADE_FN + 'text = input("Scores with spaces between: ")\nscores = []\nfor part in text.split():\n    scores.append(int(part))\ntotal = 0\nfor s in scores:\n    total += s\nprint("Total:", total)\naverage = total / len(scores)\nprint("Average:", round(average, 1))\nprint("Grade:", letter(average))'

WORDS_1 = 'text = "The cat and the hat sat on the mat."\nwords = text.split()\nprint("Words:", len(words))'
WORDS_2 = 'text = "The cat and the hat sat on the mat."\ntext = text.lower().replace(".", "")\nwords = text.split()\nprint("Words:", len(words))'
WORDS_3 = WORDS_2 + "\ncounts = {}\nfor w in words:\n    counts[w] = counts.get(w, 0) + 1\nprint(counts)"
WORDS_4 = WORDS_3 + '\nbest = ""\nbest_count = 0\nfor w in counts:\n    if counts[w] > best_count:\n        best = w\n        best_count = counts[w]\nprint("Most common:", best, best_count)'

ADV_1 = 'print("You wake up in a dark forest.")\npath = input("Go left or right? ")\nif path == "left":\n    print("You find a cave.")\nelse:\n    print("You find a river.")'
ADV_2 = 'print("You wake up in a dark forest.")\npath = input("Go left or right? ")\nif path == "left":\n    print("You find a cave.")\n    enter = input("Go inside? ")\n    if enter == "yes":\n        print("You find treasure! You win.")\n    else:\n        print("You walk home. The end.")\nelse:\n    print("You find a river.")'
ADV_3 = 'bag = []\nprint("You wake up in a dark forest.")\npath = input("Go left or right? ")\nif path == "left":\n    print("You find a cave.")\n    enter = input("Go inside? ")\n    if enter == "yes":\n        print("You find treasure! You win.")\n        bag.append("treasure")\n    else:\n        print("You walk home. The end.")\nelse:\n    print("You find a river.")\n    bag.append("fish")\nprint("Bag:", bag)'
ADV_4 = 'def play():\n    bag = []\n    print("You wake up in a dark forest.")\n    path = input("Go left or right? ")\n    if path == "left":\n        print("You find a cave.")\n        enter = input("Go inside? ")\n        if enter == "yes":\n            print("You find treasure! You win.")\n            bag.append("treasure")\n        else:\n            print("You walk home. The end.")\n    else:\n        print("You find a river.")\n        bag.append("fish")\n    print("Bag:", bag)\n\nagain = "yes"\nwhile again == "yes":\n    play()\n    again = input("Play again? ")\nprint("Thanks for playing!")'


def units():
    return [
        unit(
            "projects",
            "Projects",
            "Build real programs, one small step at a time.",
            "hammer.fill",
            [
                project(
                    "proj-todo",
                    "Project: to-do list",
                    """
You'll build a to-do list program in 4 steps: show the tasks, number them, add a new task, and remove a finished one.

Each step starts from your own code from the step before, so you keep building on what you made.
""",
                    """
Real programs are built in small pieces. You get one piece working, run it, then add the next. If something breaks, you know it was the last thing you added.
""",
                    chain(
                        'todos = ["homework", "feed the cat", "practice"]\n# Step 1: loop over todos and print each one with "-" in front\n',
                        [
                            (
                                'Step 1. Loop over todos and print each task with a dash in front, like: - homework',
                                "",
                                TODO_1,
                                [out("- homework\n- feed the cat\n- practice")],
                                ["Use for task in todos:", 'Inside the loop: print("-", task)', 'The loop is:\nfor task in todos:\n    print("-", task)'],
                                {"must": ["for"]},
                            ),
                            (
                                "Step 2. Number the tasks instead: 1. homework, 2. feed the cat, and so on. Make number = 1 before the loop, print with an f-string, and add 1 each lap.",
                                "number the tasks",
                                TODO_2,
                                [out("1. homework\n2. feed the cat\n3. practice")],
                                ["Before the loop: number = 1", 'Inside: print(f"{number}. {task}") then number += 1', 'The loop is:\nnumber = 1\nfor task in todos:\n    print(f"{number}. {task}")\n    number += 1'],
                                {"must": ["for", "+="]},
                            ),
                            (
                                'Step 3. Before printing, ask "New task: " and append the answer to todos. The checker types read.',
                                "ask for a new task and append it",
                                TODO_3,
                                [has("4. read", stdin=["read"]), has("4. walk the dog", stdin=["walk the dog"])],
                                ['Ask with new = input("New task: ")', "Then todos.append(new), before the loop.", 'The two new lines go above number = 1:\nnew = input("New task: ")\ntodos.append(new)'],
                                {"must": ["append", "input"]},
                            ),
                            (
                                'Step 4. After the list, ask "Which number is done? ". Remove that task with todos.pop(done - 1). pop(i) removes the item at position i, and positions start at 0, so subtract 1. Then print Tasks left: and the count.',
                                "remove a finished task",
                                TODO_4,
                                [has("Tasks left: 3", stdin=["read", "2"]), vals("todos", stdin=["read", "1"])],
                                ['done = int(input("Which number is done? "))', "todos.pop(done - 1), then print(\"Tasks left:\", len(todos))", 'The new lines are:\ndone = int(input("Which number is done? "))\ntodos.pop(done - 1)\nprint("Tasks left:", len(todos))'],
                                {"must": ["pop", "len"]},
                            ),
                        ],
                    ),
                    example='tasks = ["wash up"]\ntasks.append("read")\nfor t in tasks:\n    print("-", t)',
                    note="A tiny version of what you'll build: a list, a new item, and a loop that prints them.",
                    walkthrough=[
                        walk('tasks = ["wash up"]', "A list with one task."),
                        walk('tasks.append("read")', "Adds a second task to the end."),
                        walk("for t in tasks:", "Visits each task."),
                        walk('print("-", t)', "Prints it with a dash."),
                    ],
                ),
                project(
                    "proj-grades",
                    "Project: grade calculator",
                    """
You'll build a grade calculator in 4 steps: add up scores, find the average, turn it into a letter grade, and read the scores from the person using it.
""",
                    """
An average is the total divided by how many there are. Splitting the work into steps (total, then average, then grade) keeps each part small enough to check on its own.
""",
                    chain(
                        "scores = [88, 92, 75]\ntotal = 0\n# Step 1: add every score to total, then print Total: and the total\n",
                        [
                            (
                                "Step 1. Loop over scores and add each one to total. After the loop, print Total: and the total. It should print Total: 255",
                                "",
                                GRADE_1,
                                [out("Total: 255")],
                                ["for s in scores: then total += s", 'After the loop: print("Total:", total)', 'The code is:\nfor s in scores:\n    total += s\nprint("Total:", total)'],
                                {"must": ["for"]},
                            ),
                            (
                                "Step 2. Work out average = total / len(scores). Print Average: and round(average, 1), which rounds to 1 decimal place. It should print Average: 85.0",
                                "work out the average",
                                GRADE_2,
                                [out("Total: 255\nAverage: 85.0")],
                                ["average = total / len(scores)", 'print("Average:", round(average, 1))', 'The new lines are:\naverage = total / len(scores)\nprint("Average:", round(average, 1))'],
                                {"must": ["len"]},
                            ),
                            (
                                'Step 3. At the top, write a function letter(avg) that returns "A" for 90 or more, "B" for 80 or more, "C" for 70 or more, and "Keep practicing" otherwise. At the end, print Grade: and letter(average).',
                                "add a letter(avg) function at the top, then print the grade",
                                GRADE_3,
                                [out("Total: 255\nAverage: 85.0\nGrade: B"), has("A", append='print(letter(95))'), has("Keep practicing", append='print(letter(50))'), has("C", append='print(letter(70))')],
                                ["def letter(avg): with if avg >= 90: return \"A\"", "Then elif for B and C, and else for Keep practicing.", 'The function is:\ndef letter(avg):\n    if avg >= 90:\n        return "A"\n    elif avg >= 80:\n        return "B"\n    elif avg >= 70:\n        return "C"\n    else:\n        return "Keep practicing"'],
                                {"must": ["def", "return", "elif"]},
                            ),
                            (
                                'Step 4. Instead of a fixed list, ask "Scores with spaces between: ". Split the answer, turn each part into a number with int(), and append it to an empty scores list. The checker types 90 100 95.',
                                "read the scores from input instead",
                                GRADE_4,
                                [has("Total: 285", "Average: 95.0", "Grade: A", stdin=["90 100 95"]), has("Total: 120", "Average: 60.0", "Grade: Keep practicing", stdin=["50 70"])],
                                ['text = input("Scores with spaces between: ") then scores = []', "for part in text.split(): scores.append(int(part))", 'Replace the fixed list with:\ntext = input("Scores with spaces between: ")\nscores = []\nfor part in text.split():\n    scores.append(int(part))'],
                                {"must": ["split", "append", "input"]},
                            ),
                        ],
                    ),
                    example="nums = [4, 6]\ntotal = 0\nfor n in nums:\n    total += n\nprint(total / len(nums))",
                    note="The heart of the project: a total, then an average.",
                    walkthrough=[
                        walk("for n in nums:", "Visit each number."),
                        walk("total += n", "Add it to the total: 10."),
                        walk("print(total / len(nums))", "10 / 2 = 5.0"),
                    ],
                    terms=[term("average", "The total divided by how many there are.", "sharing all the sweets equally: how many each person gets.")],
                ),
                project(
                    "proj-words",
                    "Project: word counter",
                    """
You'll build a word counter in 4 steps: count the words, clean up the text, count each word, and find the most common one.
""",
                    """
Computers see "The" and "the" as different, and "mat." is not the same as "mat". Cleaning the text first, with lower() and replace(), makes the counting fair.
""",
                    chain(
                        'text = "The cat and the hat sat on the mat."\n# Step 1: split text into words and print Words: and how many\n',
                        [
                            (
                                "Step 1. Split text into a list called words, then print Words: and how many there are. It should print Words: 9",
                                "",
                                WORDS_1,
                                [out("Words: 9")],
                                ["words = text.split()", 'print("Words:", len(words))', 'The code is:\nwords = text.split()\nprint("Words:", len(words))'],
                                {"must": ["split", "len"]},
                            ),
                            (
                                'Step 2. Before splitting, clean the text: text = text.lower().replace(".", ""). That makes it lowercase and removes the dot.',
                                "clean the text before splitting",
                                WORDS_2,
                                [out("Words: 9"), vals("words")],
                                ["Put the cleaning line above words = text.split().", 'text = text.lower().replace(".", "")', 'The cleaning line is:\ntext = text.lower().replace(".", "")'],
                                {"must": ["lower", "replace"]},
                            ),
                            (
                                "Step 3. Count each word in a dictionary called counts. Use counts[w] = counts.get(w, 0) + 1 in a loop. Print counts.",
                                "count each word in a dictionary",
                                WORDS_3,
                                [vals("counts")],
                                ["counts = {} before the loop.", "for w in words: counts[w] = counts.get(w, 0) + 1", "The code is:\ncounts = {}\nfor w in words:\n    counts[w] = counts.get(w, 0) + 1\nprint(counts)"],
                                {"must": ["get", "for"]},
                            ),
                            (
                                "Step 4. Find the most common word. Keep best and best_count, loop over counts, and update them when you find a bigger count. Print Most common:, the word, and its count.",
                                "find the most common word",
                                WORDS_4,
                                [has("Most common: the 3")],
                                ['Start with best = "" and best_count = 0.', "for w in counts: if counts[w] > best_count: update both.", 'The code is:\nbest = ""\nbest_count = 0\nfor w in counts:\n    if counts[w] > best_count:\n        best = w\n        best_count = counts[w]\nprint("Most common:", best, best_count)'],
                                {"must": ["for", "if"]},
                            ),
                        ],
                    ),
                    example='counts = {}\nfor w in ["a", "b", "a"]:\n    counts[w] = counts.get(w, 0) + 1\nprint(counts)',
                    note="The counting trick you'll use in step 3.",
                    walkthrough=[
                        walk("counts[w] = counts.get(w, 0) + 1", "Get the count so far (0 for a new word), add 1, save it."),
                        walk("print(counts)", "{'a': 2, 'b': 1}"),
                    ],
                ),
                project(
                    "proj-adventure",
                    "Project: text adventure",
                    """
You'll build a choose-your-own-adventure game in 4 steps: a first choice, a choice inside a choice, a bag that collects items, and a play-again loop.
""",
                    """
A text adventure is a tree of if statements. Each answer picks a branch, and some branches have more choices inside them. Indentation shows which choice belongs inside which.
""",
                    chain(
                        'print("You wake up in a dark forest.")\npath = input("Go left or right? ")\n# Step 1: if path is left, print You find a cave. Otherwise print You find a river.\n',
                        [
                            (
                                "Step 1. If path is left, print You find a cave. Otherwise print You find a river. The checker tries left and right.",
                                "",
                                ADV_1,
                                [has("You find a cave.", stdin=["left"]), has("You find a river.", stdin=["right"])],
                                ['if path == "left":', "else: for the river.", 'The code is:\nif path == "left":\n    print("You find a cave.")\nelse:\n    print("You find a river.")'],
                                {"must": ["if", "else"]},
                            ),
                            (
                                'Step 2. Inside the cave branch, ask "Go inside? ". If the answer is yes, print You find treasure! You win. Otherwise print You walk home. The end.',
                                "add a choice inside the cave",
                                ADV_2,
                                [has("You find treasure! You win.", stdin=["left", "yes"]), has("You walk home. The end.", stdin=["left", "no"]), has("You find a river.", stdin=["right"])],
                                ['Under print("You find a cave."), with the same indent: enter = input("Go inside? ")', 'Then an if enter == "yes": with 8 spaces before its print.', 'The cave branch is:\n    print("You find a cave.")\n    enter = input("Go inside? ")\n    if enter == "yes":\n        print("You find treasure! You win.")\n    else:\n        print("You walk home. The end.")'],
                                {"must": ["input"]},
                            ),
                            (
                                'Step 3. Make bag = [] at the top. Append "treasure" when you win, and "fish" at the river. At the very end, print Bag: and the bag.',
                                "add a bag that collects items",
                                ADV_3,
                                [has("Bag: ['treasure']", stdin=["left", "yes"]), has("Bag: ['fish']", stdin=["right"]), has("Bag: []", stdin=["left", "no"])],
                                ["bag = [] goes on the first line.", 'bag.append("treasure") under the win line, bag.append("fish") under the river line. print("Bag:", bag) at the end with no indent.', 'The last line is: print("Bag:", bag)'],
                                {"must": ["append"]},
                            ),
                            (
                                'Step 4. Put the whole game in a function play(). Below it, make again = "yes", and while again == "yes": call play() and ask again = input("Play again? "). After the loop, print Thanks for playing!',
                                "wrap the game in play() and add a play-again loop",
                                ADV_4,
                                [has("Thanks for playing!", stdin=["right", "no"]), has("You find a river.", "You find treasure! You win.", "Thanks for playing!", stdin=["right", "yes", "left", "yes", "no"])],
                                ["Put def play(): on top and indent every game line by 4 more spaces.", 'Below the function: again = "yes", then while again == "yes":', 'The loop is:\nagain = "yes"\nwhile again == "yes":\n    play()\n    again = input("Play again? ")\nprint("Thanks for playing!")'],
                                {"must": ["def", "while"]},
                            ),
                        ],
                    ),
                    example='door = "red"\nif door == "red":\n    print("A dragon!")\nelse:\n    print("A garden.")',
                    note="One choice, two paths. Your game will have lots of these.",
                    walkthrough=[
                        walk('if door == "red":', "Checks which door."),
                        walk('print("A dragon!")', "The path for red."),
                        walk("else:", "Every other answer goes here."),
                    ],
                ),
            ],
        )
    ]
