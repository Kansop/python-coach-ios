# Python Trail

Learn Python from scratch with 16 interactive lessons, a playground and two projects.

[Open the live app](https://kansop.github.io/pocket-ai/python-trail/) or [download a standalone copy](https://github.com/Kansop/python-coach-ios/raw/refs/heads/python-trail/Python-Trail.html) and open the saved HTML file in a browser. Lessons and the editor also run offline. Each browser saves its own progress until you sign in.

To develop locally, run `python -m http.server 8000` from this directory and open http://localhost:8000. The bundled Python runtime is Skulpt (see LICENSE.txt). Rebuild the standalone file with `python3 build-standalone.py`.
If the live page is ever blank on a phone, tap **Reset app** if you see it, or close the Safari tab completely and open the link again.


## Study together online

You and a friend can sign in from different places, text each other, see when the other person is online, and see which lesson they are on.

1. Open the live app and go to **Study with friends**.
2. Create an account with a display name and a 4+ character PIN or passcode. There is no email sign-up.
3. Share your username. Add each other and accept the request. After that, both of you have the same permissions: you can chat, see each other's progress, and keep learning.
4. Stay signed out if you only want the offline lessons. Signing out does not erase local progress on that device.

The free Cloudflare Worker at https://python-trail-server.tabletop-luca.workers.dev stores accounts (PIN hashes, never the raw PIN), friend requests, chat, presence, and lesson progress. Chat text is stored as plain text and escaped before it is shown, so messages cannot run as code. The worker lives in `server/` and uses its own D1 database named `python-trail`. Do not point it at the TableTop or DealerDesk workers or databases.

## Share the repo and build on it

This project lives on the `python-trail` branch of [Kansop/python-coach-ios](https://github.com/Kansop/python-coach-ios). Collaborators with write access, including lucashananigans, can clone it from their own GitHub account and use Cursor, Grok Bot, or any other AI to change the lessons, the app, or the worker.

```bash
git clone -b python-trail https://github.com/Kansop/python-coach-ios.git
cd python-coach-ios
```

After you accept the GitHub invite, push branches and open pull requests against `python-trail`. On a personal GitHub repository the highest collaborator access is write, which is enough to edit the code, use an AI on your clone, and open pull requests. Luca remains the repository owner.

To deploy worker changes (from someone already logged into the Python Trail Cloudflare account):

```bash
cd server
npx wrangler deploy
```

To run the two-user online checks (Playwright, already used during development):

```bash
npm install playwright
node tests/online.spec.mjs
```
