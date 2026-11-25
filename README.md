# Python Coach

Python Coach is an iPhone app that teaches Python by having you type it. Lessons are short. Each one explains an idea, lets you run an example, then asks you to write the code yourself. Python runs on the phone. There is no account, no ads, and no tracking.

It is built for iOS 17 or newer, in SwiftUI.

## What you can do

- Work through 80+ lessons: the core path, then string tools, more loops, tuples, sets, comprehensions, errors, classes, and text games (guessing, rock-paper-scissors, hangman, a quiz). Some steps are multiple-choice checks. Some are "fix the bug" edits.
- Run real Python, including `input()`, and read friendly explanations when something goes wrong.
- Keep a daily streak, earn XP, finish units, and collect badges. A daily challenge and a free-play playground (with saved snippets) stay on the phone too.
- Ask for hints one at a time. A hint never shows the full answer.
- Type in a monospaced editor with basic syntax colors and a row of Python keys above the keyboard (`: ( ) [ ] " ' =` and Tab).
- Use it on iPhone or iPad. Text follows Dynamic Type, and the main controls have VoiceOver labels. Light mode, dark mode, or the system setting.
- Hear a short chime when an exercise passes. The chime follows the silent switch, and you can turn sound and a light haptic off in Settings.

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

`project.yml` is there if you use [XcodeGen](https://github.com/yonaskolb/XcodeGen). You do not need XcodeGen to build. `Scripts/generate_xcodeproj.py` can rewrite the Xcode project, and `Scripts/build_curriculum.py` checks the lesson solutions and regenerates the catalog. Those solutions are not shown in the app.

This repository was prepared in an environment without `xcodebuild`, so the project was not compiled here. The Swift is written for the iOS 17 SDK and avoids newer-only APIs.

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

## Tests

The shared scheme includes the unit tests. In Xcode, choose Product → Test, or press Command-U.

The tests cover lesson checking (output, values, required syntax, timeouts, quizzes, and kid-facing errors), source scanning, syntax tokens, streak dates, levels, badges, the daily challenge calendar, saved playground snippets, Pyodide path mapping, cached-file checks, and SwiftData progress (XP is awarded once, streaks move forward, hints unlock one at a time).

## Privacy

Progress is stored with SwiftData on the device. Settings such as sound and appearance use UserDefaults. The only network call is the optional Pyodide download, plus a repair download if you ask for one in Settings. There is no account and no analytics SDK.
