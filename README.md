# Python Coach

Python Coach is an iPhone app that teaches Python by having you type it. Lessons are short. Each one explains an idea, lets you run an example, then asks you to write the code yourself. Python runs on the phone. There is no account, no ads, and no tracking.

It is built for iOS 17 or newer, in SwiftUI.

## How the course works

The course assumes you have never written code. It starts with a short "What is coding?" unit that explains what a program is, how to use the app, and that errors are normal. After that, each lesson teaches one new idea in small steps.

There are 85 lessons in 18 units. The first 16 units are the main path, from `print()` through variables, text, math, `input()`, choices, loops, lists, functions, dictionaries, string tools, error handling, projects, and small text games. The last two units are marked **Bonus**: tuples, sets, list comprehensions, and classes. They come after the main path and you don't need them to finish it.

Each lesson has the same parts:

1. **New words.** Every new term (variable, string, loop, and so on) gets a plain definition and an everyday comparison the first time it shows up.
2. **The idea**, then **Why it works**, which explains what Python is actually doing.
3. **An example you can run**, followed by **Line by line**, a note for each line of the example.
4. **Watch out for**: common beginner mistakes, why each one goes wrong, and the fix. Every one of these was run to make sure the wrong version really fails.
5. **Two or three practices that get a little harder.** The first is almost always a fill-in-the-blank: you replace `___` in the starter code. The later ones ask for more. Some are "Fix the bug" edits.

Practice types:

- **Write code** and **Fix the bug**, checked by running your code. Some checks type answers into `input()` for you, and the feedback says which typed answer didn't work.
- **What will this print?** You read a short program and pick its output. There are 73 of these across the units. The right answer comes from actually running the code.
- **Quick check**: a short multiple-choice question.

Hints unlock one at a time. Early hints are concrete ("Replace ___ with ..."). If you're still stuck, the last hint shows the answer, so you never get trapped.

### Projects

Five projects are split into guided steps. Each step starts from the code you wrote in the step before.

- To-do list (4 steps)
- Grade calculator (4 steps)
- Word counter (4 steps)
- Text adventure (4 steps)
- Bank account class (4 steps, in the Bonus classes unit)

### When something goes wrong

When your code crashes, the app explains the error in plain words. It shows the line Python stopped on, your code on that line, what went wrong, and one thing to try. Python's own message is still there under "What Python said". The explainer covers SyntaxError (missing quotes, brackets or colons, curly quotes, `print` without parentheses, `=` instead of `==`, `else if`), IndentationError, NameError (with "did you mean"), TypeError, IndexError, KeyError, ZeroDivisionError, ValueError, AttributeError, programs that ask for more input than the exercise gives, and code that runs too long. The playground uses the same explainer.

When the output is wrong but nothing crashed, the app says which line is different and whether it's only capital letters or spaces.

### Review

The Review card on Home brings back 5 practices from lessons you've finished. Practices you got wrong come back more often. Ones you haven't seen in a while come back a little more often too. A right answer on the first try earns XP and makes that practice come up less. Project steps are not used in review, because each one builds on the step before.

## Other features

- Run real Python, including `input()`.
- Keep a daily streak, earn XP, finish units, and collect badges. A daily challenge and a free-play playground (with saved snippets) are on the phone too.
- Type in a monospaced editor with basic syntax colors and a row of Python keys above the keyboard (`: ( ) [ ] " ' =` and Tab).
- Use it on iPhone or iPad. Text follows Dynamic Type, and the main controls have VoiceOver labels. Light mode, dark mode, or the system setting.
- Sound is **off** by default. You can turn on a short success chime in Settings; it follows the silent switch. A light haptic is on by default and can be turned off.

## How Python runs offline

The app does not bundle the Python runtime. On the first launch it downloads **Pyodide 0.26.4** (about 14 MB) from the official jsDelivr CDN:

`https://cdn.jsdelivr.net/pyodide/v0.26.4/full/`

These files are saved under Application Support and checked before they are marked ready:

- `pyodide.js`
- `pyodide.asm.js`
- `pyodide.asm.wasm`
- `python_stdlib.zip`
- `pyodide-lock.json`

A hidden `WKWebView` loads them through a custom `pycoach://` URL scheme, so later launches do not use the network. The first screen shows download progress. If the phone is offline before that download finishes, the app says so and lets you try again. After the files are cached, airplane mode is fine.

Pyodide 0.26.4 is pinned because it still runs in the Safari engine shipped with iOS 17. Some newer Pyodide releases crash on iOS because of broken WebAssembly GC support.

Code runs in a web worker. A line tracer stops ordinary infinite loops after a few seconds and explains that in plain language. If the worker is stuck anyway, the page terminates it and starts a fresh one. If the worker cannot start, the same runtime loads on the page and the app can still rebuild the web view to cut off a hang. `input()` does not use the JavaScript prompt. The runtime pauses, SwiftUI asks for an answer, and the program continues.

Pyodide is Mozilla Public License 2.0. The app downloads it; it does not vendor the runtime.

## Build and run

You need a Mac with **Xcode 15.4 or newer** (Xcode 16 is a good choice). The deployment target is iOS 17. Open the committed project:

```
PythonCoach.xcodeproj
```

`project.yml` is there if you use [XcodeGen](https://github.com/yonaskolb/XcodeGen). You do not need XcodeGen to build. `Scripts/generate_xcodeproj.py` can rewrite the Xcode project. Lessons are written in Python under `Scripts/lessons/` and turned into the app's catalog by `Scripts/build_curriculum.py` (see "Checking the lessons" below).

This repository was prepared in an environment without `xcodebuild`, so the app itself has not been compiled or run here. The Foundation-only Swift (catalog, checker, error explainer, review planner, progress models) was compiled and tested with Swift 5.10 on Linux. The SwiftUI and SwiftData code was checked by hand. The Swift is written for the iOS 17 SDK and avoids newer-only APIs.

### Simulator

1. Open `PythonCoach.xcodeproj`.
2. Choose the Python Coach scheme and an iPhone simulator (for example iPhone 16).
3. Press Run.
4. The first launch needs a network connection so Python can download. After that, you can turn the network off and keep using the app.

### A personal iPhone with a free Apple ID

1. On the iPhone, turn on Developer Mode (Settings → Privacy & Security → Developer Mode) and restart if asked.
2. Connect the phone and trust the computer.
3. In Xcode, select the Python Coach target → Signing & Capabilities.
4. Check "Automatically manage signing" and choose your Personal Team (the free Apple ID).
5. If the bundle id is already taken, change `com.pythoncoach.app` to something unique, such as `com.yourname.pythoncoach`.
6. Select your iPhone as the run destination and press Run.
7. If the phone says the developer is not trusted, go to Settings → General → VPN & Device Management and trust your Apple ID.

A free provisioning profile expires after about 7 days. Run the app from Xcode again when it does. This project does not set up App Store signing, certificates, or release archives.

## Checking the lessons

Lessons live in `Scripts/lessons/u01_start.py` through `u18_bonus_classes.py`, one file per unit, written with the small helpers in `Scripts/lessons/dsl.py`. Each practice has a reference solution and, where useful, a list of believable wrong answers. These are not shown in the app.

```
cd Scripts
python3.12 check_lessons.py                     # check everything with CPython 3.12
python3.12 check_lessons.py --pyodide DIR       # check with real Pyodide 0.26.4 under Node
python3.12 build_curriculum.py                  # check, then rewrite CurriculumJSON.swift and PythonHarness.swift
```

For `--pyodide`, `DIR` is a folder where `npm install pyodide@0.26.4` was run (Node 18 or newer).

The check runs every lesson through the same Python harness the app uses, with scripted `input()` answers. It fails the build if any of these are wrong:

- every example runs, and every "Line by line" note matches a real line of the example
- every "Watch out for" fix runs, and every wrong version really crashes or prints something different
- every reference solution passes all of its checks
- every starter, every empty program, and every listed wrong answer fails
- every "What will this print?" answer is the real output, and the wrong choices are different from it
- only the last hint of a practice contains the whole answer
- lessons have the required parts and at least two practices, and the text has no emoji and none of "simply", "obviously" or "just do"

Last run: 85 lessons, 260 practices, 0 failures, on both CPython 3.12 and Pyodide 0.26.4.

`Scripts/swift_parity.sh` goes one step further. It runs every solution, starter, empty program and wrong answer in CPython, then feeds those real runs to the app's own Swift `LessonChecker` and `FriendlyErrors` code (compiled with `swiftc`, which also works on Linux). The Swift checker must reach the same pass or fail decision as the Python one, and every crash in a "Watch out for" example must point at a real line of the learner's code.

## Tests

The shared scheme includes the unit tests. In Xcode, choose Product → Test, or press Command-U.

- `CoachLogicTests` covers the lesson catalog (shape, bonus units last, gentle first practices, no emoji), fill-in-the-blank detection, output and value checks, checks that type `input()` answers, prediction and quick-check grading, output difference wording, the error explainer and its line numbers, review weighting and picking, practice keys, source scanning, syntax colors, streaks, levels, badges, the daily challenge, and Pyodide path mapping. It needs only Foundation, so it also runs with `swift test` on Linux.
- `ProgressStoreTests` covers SwiftData progress: XP is awarded once, streaks move forward, practice code is saved, hints unlock one at a time, misses are counted, project steps carry your code forward, review lowers misses and awards XP, reset clears everything, and sound is off by default. It also covers saved playground snippets and cached-file checks.

## Privacy

Progress is stored with SwiftData on the device. Settings such as sound and appearance use UserDefaults. The only network call is the optional Pyodide download, plus a repair download if you ask for one in Settings. There is no account and no analytics SDK.
