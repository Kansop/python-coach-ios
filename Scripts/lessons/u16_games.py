from .dsl import ask, code, fix, has, lesson, oops, out, predict, term, unit, vals, walk


def units():
    built = _units()
    stdin = {"game-guess": ["3", "9", "7"], "game-rps": ["rock"], "game-hangman": ["a"], "game-quiz": ["4", "Paris"]}
    for item in built[0]["lessons"]:
        item["exampleStdin"] = stdin.get(item["id"], [])
    return built


def _units():
    return [
        unit(
            "games",
            "Text games",
            "Small games made of input, choices, and loops.",
            "gamecontroller.fill",
            [
                lesson(
                    "game-guess",
                    "Number guessing",
                    """
A guessing game uses three ideas you already know: input() to get a guess, if to compare it, and a while loop to keep going until the guess is right.
""",
                    """
The loop's condition is "the guess is wrong." Each lap gives a clue (too high or too low) and asks again. When the guess is right, the condition turns False and the loop ends.
""",
                    'secret = 7\nguess = int(input("Guess 1 to 10: "))\nwhile guess != secret:\n    if guess < secret:\n        print("Too low")\n    else:\n        print("Too high")\n    guess = int(input("Guess again: "))\nprint("You got it!")',
                    "Run it and play. The secret is 7.",
                    [
                        walk("while guess != secret:", "Keep going while the guess is wrong."),
                        walk("if guess < secret:", "Give a clue."),
                        walk('guess = int(input("Guess again: "))', "Ask again, so the loop can end."),
                        walk('print("You got it!")', "Only reached with the right guess."),
                    ],
                    [],
                    [
                        code(
                            "Fill in the blank with the clue for a guess that's too big.",
                            'secret = 5\nguess = int(input("Guess: "))\nif guess < secret:\n    print("Too low")\nelif guess > secret:\n    print(___)\nelse:\n    print("Correct")',
                            'secret = 5\nguess = int(input("Guess: "))\nif guess < secret:\n    print("Too low")\nelif guess > secret:\n    print("Too high")\nelse:\n    print("Correct")',
                            [has("Too high", stdin=["8"]), has("Too low", stdin=["1"]), has("Correct", stdin=["5"])],
                            ["The opposite of Too low.", 'Replace ___ with "Too high".', 'The line is: print("Too high")'],
                        ),
                        code(
                            "Make the full game: secret is 4. Keep asking until the guess is right, saying Too low or Too high each time. Then print You got it!",
                            'secret = 4\nguess = int(input("Guess: "))\n# Loop until the guess is right\n\nprint("You got it!")',
                            'secret = 4\nguess = int(input("Guess: "))\nwhile guess != secret:\n    if guess < secret:\n        print("Too low")\n    else:\n        print("Too high")\n    guess = int(input("Guess: "))\nprint("You got it!")',
                            [has("Too low", "Too high", "You got it!", stdin=["1", "9", "4"]), out("Guess: 4\nYou got it!", stdin=["4"])],
                            ["while guess != secret:", "Inside: the clue if/else, then ask again with input.", 'The loop is:\nwhile guess != secret:\n    if guess < secret:\n        print("Too low")\n    else:\n        print("Too high")\n    guess = int(input("Guess: "))'],
                            must=["while"],
                        ),
                        code(
                            "Add a counter: count how many guesses it took, and print Guesses: and the count at the end. The first guess counts as 1.",
                            'secret = 4\nguess = int(input("Guess: "))\ntries = 1\nwhile guess != secret:\n    guess = int(input("Guess: "))\n    # add 1 to tries here\nprint("Guesses:", tries)',
                            'secret = 4\nguess = int(input("Guess: "))\ntries = 1\nwhile guess != secret:\n    guess = int(input("Guess: "))\n    tries += 1\nprint("Guesses:", tries)',
                            [has("Guesses: 3", stdin=["1", "2", "4"]), has("Guesses: 1", stdin=["4"])],
                            ["Each time the loop asks again, one more guess happened.", "Inside the loop: tries += 1", "The line under the second input is: tries += 1"],
                            must=["+="],
                        ),
                    ],
                ),
                lesson(
                    "game-rps",
                    "Rock, paper, scissors",
                    """
In rock, paper, scissors, rock beats scissors, scissors beats paper, and paper beats rock.

A program can decide the winner with if, elif, and else, using and to check two things at once.
""",
                    """
There are only three ways to win. If it's a tie, say so first. Then check the three winning pairs. If none of those matched, the other player won.
""",
                    'me = input("rock, paper, or scissors? ")\ncpu = "scissors"\nif me == cpu:\n    print("Tie")\nelif me == "rock" and cpu == "scissors":\n    print("You win")\nelse:\n    print("You lose")',
                    "The computer always picks scissors in this example.",
                    [
                        walk("if me == cpu:", "Same pick is a tie."),
                        walk('elif me == "rock" and cpu == "scissors":', "Both parts must be True for a win here."),
                        walk("else:", "Everything else, in this small version, is a loss."),
                    ],
                    [],
                    [
                        code(
                            "Fill in the blank: paper beats rock.",
                            'me = "paper"\ncpu = "rock"\nif me == "paper" and cpu == ___:\n    print("You win")',
                            'me = "paper"\ncpu = "rock"\nif me == "paper" and cpu == "rock":\n    print("You win")',
                            [out("You win")],
                            ["Which one does paper beat?", 'Replace ___ with "rock".', 'The line is: if me == "paper" and cpu == "rock":'],
                        ),
                        code(
                            "Write beats(a, b) that returns True when a beats b. There are three winning pairs.",
                            "def beats(a, b):\n    # return True for the three winning pairs\n    return False",
                            'def beats(a, b):\n    if a == "rock" and b == "scissors":\n        return True\n    if a == "scissors" and b == "paper":\n        return True\n    if a == "paper" and b == "rock":\n        return True\n    return False',
                            [out("True\nTrue\nTrue", append='print(beats("rock", "scissors"))\nprint(beats("scissors", "paper"))\nprint(beats("paper", "rock"))'), out("False\nFalse\nFalse", append='print(beats("rock", "paper"))\nprint(beats("rock", "rock"))\nprint(beats("paper", "scissors"))')],
                            ["Use one if for each winning pair, each returning True.", 'Example: if a == "rock" and b == "scissors": return True', 'The function is:\ndef beats(a, b):\n    if a == "rock" and b == "scissors":\n        return True\n    if a == "scissors" and b == "paper":\n        return True\n    if a == "paper" and b == "rock":\n        return True\n    return False'],
                            must=["return", "and"],
                            wrong=["def beats(a, b):\n    return True", 'def beats(a, b):\n    return a == "rock"'],
                        ),
                        predict(
                            'me = "rock"\ncpu = "paper"\nif me == cpu:\n    print("Tie")\nelif me == "rock" and cpu == "scissors":\n    print("Win")\nelse:\n    print("Lose")',
                            ["Tie", "Win", "Win\nLose"],
                            "Not a tie, and cpu isn't scissors, so the else runs.",
                            ["Is me equal to cpu?", "Are both parts of the and True?"],
                        ),
                    ],
                ),
                lesson(
                    "game-hangman",
                    "Hangman",
                    """
Hangman shows a word with blanks for the letters you haven't guessed yet. You can build that display with a loop over the word: show the letter if it's been guessed, otherwise show _.
""",
                    """
The loop visits each letter of the secret word. For each one, in checks whether it's in the guessed list. Joining the pieces together builds the display one character at a time.
""",
                    'word = "cat"\nguessed = ["a"]\nshown = ""\nfor ch in word:\n    if ch in guessed:\n        shown += ch\n    else:\n        shown += "_"\nprint(shown)',
                    "Only a has been guessed, so you see _a_.",
                    [
                        walk('shown = ""', "Start with empty text."),
                        walk("for ch in word:", "Visit c, a, t."),
                        walk("if ch in guessed:", "Has this letter been guessed?"),
                        walk("shown += ch", "Yes: show the letter."),
                        walk('shown += "_"', "No: show a blank."),
                    ],
                    [],
                    [
                        code(
                            "Fill in the blank so a guessed letter is shown.",
                            'word = "dog"\nguessed = ["o", "g"]\nshown = ""\nfor ch in word:\n    if ch in guessed:\n        shown += ___\n    else:\n        shown += "_"\nprint(shown)',
                            'word = "dog"\nguessed = ["o", "g"]\nshown = ""\nfor ch in word:\n    if ch in guessed:\n        shown += ch\n    else:\n        shown += "_"\nprint(shown)',
                            [out("_og")],
                            ["Add the letter itself.", "Replace ___ with ch.", "The line is: shown += ch"],
                            wrong=['word = "dog"\nguessed = ["o", "g"]\nshown = ""\nfor ch in word:\n    if ch in guessed:\n        shown += "o"\n    else:\n        shown += "_"\nprint(shown)'],
                        ),
                        code(
                            "Write show(word, guessed) that returns the display string. The checker tries different words.",
                            "def show(word, guessed):\n    shown = \"\"\n    # loop over word\n    return shown",
                            'def show(word, guessed):\n    shown = ""\n    for ch in word:\n        if ch in guessed:\n            shown += ch\n        else:\n            shown += "_"\n    return shown',
                            [out("_a_a_a", append='print(show("banana", ["a"]))'), out("____", append='print(show("tree", []))'), out("tree", append='print(show("tree", ["t", "r", "e"]))')],
                            ["Use the same loop as the example, inside the function.", "Indent the loop by 4 spaces, its insides by 8 or 12.", 'The loop is:\n    for ch in word:\n        if ch in guessed:\n            shown += ch\n        else:\n            shown += "_"'],
                            must=["for", "return"],
                        ),
                        code(
                            'The checker types one letter. If it\'s in word, print Yes! Otherwise print Nope. Then lives goes down by 1 for a wrong guess, and print Lives: and lives.',
                            'word = "python"\nlives = 3\nletter = input("Letter: ")\n# check the letter\n',
                            'word = "python"\nlives = 3\nletter = input("Letter: ")\nif letter in word:\n    print("Yes!")\nelse:\n    print("Nope")\n    lives -= 1\nprint("Lives:", lives)',
                            [has("Yes!", "Lives: 3", stdin=["p"]), has("Nope", "Lives: 2", stdin=["z"])],
                            ["if letter in word:", "In the else: print Nope and lives -= 1.", 'The code is:\nif letter in word:\n    print("Yes!")\nelse:\n    print("Nope")\n    lives -= 1\nprint("Lives:", lives)'],
                            must=["if", "in"],
                        ),
                    ],
                ),
                lesson(
                    "game-quiz",
                    "Score a quiz",
                    """
A quiz asks questions, checks each answer, and keeps score. You can store the questions and answers in a list of pairs and loop over them.
""",
                    """
Each lap of the loop handles one question: ask it, compare the answer, and add a point if it's right. The score variable lives outside the loop so it keeps counting.
""",
                    'score = 0\nif input("2 + 2? ") == "4":\n    score += 1\nif input("Capital of France? ") == "Paris":\n    score += 1\nprint("Score:", score)',
                    "Two questions, one point each.",
                    [
                        walk("score = 0", "No points yet."),
                        walk('if input("2 + 2? ") == "4":', 'The answer is text, so compare it to "4" in quotes.'),
                        walk("score += 1", "A point for a right answer."),
                    ],
                    [
                        oops('if input("2 + 2? ") == 4:\n    print("right")\nelse:\n    print("wrong")', 'input gives text. "4" (text) is not equal to 4 (number). Compare to "4".', 'if input("2 + 2? ") == "4":\n    print("right")\nelse:\n    print("wrong")', stdin=["4"]),
                    ],
                    [
                        code(
                            "Fill in the blank so a right answer earns a point.",
                            'score = 0\nif input("3 x 3? ") == "9":\n    score ___ 1\nprint("Score:", score)',
                            'score = 0\nif input("3 x 3? ") == "9":\n    score += 1\nprint("Score:", score)',
                            [has("Score: 1", stdin=["9"]), has("Score: 0", stdin=["6"])],
                            ["Use the add shortcut.", "Replace ___ with +=.", "The line is: score += 1"],
                        ),
                        code(
                            "Loop over questions. Each item is a pair in round brackets: (question, answer). for q, a in questions: takes each pair apart, so q is the question and a is the answer. Ask each question, add 1 to score for each right answer, then print Score: and the score.",
                            'questions = [("Sky color? ", "blue"), ("Legs on a spider? ", "8")]\nscore = 0\nfor q, a in questions:\n    # ask q, compare with a\n    pass\nprint("Score:", score)',
                            'questions = [("Sky color? ", "blue"), ("Legs on a spider? ", "8")]\nscore = 0\nfor q, a in questions:\n    if input(q) == a:\n        score += 1\nprint("Score:", score)',
                            [has("Score: 2", stdin=["blue", "8"]), has("Score: 1", stdin=["red", "8"]), has("Score: 0", stdin=["red", "6"])],
                            ["Each lap, q is the question and a is the answer.", "if input(q) == a: then score += 1", "The loop body is:\n    if input(q) == a:\n        score += 1"],
                            must=["for", "input"],
                        ),
                        code(
                            "Make the quiz forgiving: strip spaces and ignore capitals before comparing. Use .strip().lower() on the answer.",
                            'score = 0\nanswer = input("Planet we live on? ")\nif answer == "earth":\n    score += 1\nprint("Score:", score)',
                            'score = 0\nanswer = input("Planet we live on? ")\nanswer = answer.strip().lower()\nif answer == "earth":\n    score += 1\nprint("Score:", score)',
                            [has("Score: 1", stdin=["  Earth "]), has("Score: 1", stdin=["EARTH"]), has("Score: 0", stdin=["Mars"])],
                            ["Clean the answer before the if.", "answer = answer.strip().lower()", "The new line goes under the input: answer = answer.strip().lower()"],
                            must=["strip", "lower"],
                        ),
                    ],
                ),
            ],
        )
    ]
