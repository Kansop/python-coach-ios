/* Python Trail online client: sign-in, friends, presence, progress sync, chat. */
const TRAIL_API = "https://python-trail-server.tabletop-luca.workers.dev";
window.TrailOnline = (() => {
  const TOKEN = "token";
  const USER = "user";
  let poll = 0;
  let beat = 0;
  let started = false;

  const token = () => get(TOKEN, "");
  const me = () => get(USER, null);
  const signedIn = () => !!(token() && me());

  async function api(path, opts = {}) {
    const headers = { Accept: "application/json", ...(opts.headers || {}) };
    if (opts.body && !(opts.body instanceof FormData)) {
      headers["Content-Type"] = "application/json";
    }
    if (token()) headers.Authorization = "Bearer " + token();
    const res = await fetch(TRAIL_API + path, {
      method: opts.method || "GET",
      headers,
      body: opts.body ? JSON.stringify(opts.body) : undefined,
    });
    let data = {};
    try {
      data = await res.json();
    } catch {}
    if (!res.ok) {
      const err = new Error(data.error || "Request failed.");
      err.status = res.status;
      if (res.status === 401) signOut(false);
      throw err;
    }
    return data;
  }

  function progressBody() {
    return {
      currentLesson: get("currentLesson", next() >= 0 ? next() : 15),
      completed: [...done],
    };
  }

  let syncChain = Promise.resolve();
  function syncProgress() {
    if (!signedIn()) return Promise.resolve();
    syncChain = syncChain
      .then(() => api("/progress", { method: "POST", body: progressBody() }))
      .catch(() => {});
    return syncChain;
  }

  function setCurrentLesson(i) {
    set("currentLesson", i);
    syncProgress();
  }

  function mergeProgress(remote) {
    if (!remote) return;
    const union = new Set([...done, ...(remote.completed || [])]);
    if (union.size !== done.size || [...union].some((n) => !done.has(n))) {
      done = union;
      set("done", [...done]);
    }
    if (remote.currentLesson != null) set("currentLesson", remote.currentLesson);
  }

  async function signUpOrIn(kind, username, pin) {
    const data = await api(kind === "signup" ? "/signup" : "/login", {
      method: "POST",
      body: { username, pin },
    });
    set(TOKEN, data.token);
    set(USER, data.user);
    mergeProgress(data);
    await syncProgress();
    startHeartbeat();
    return data.user;
  }

  function signOut(server = true) {
    const t = token();
    set(TOKEN, "");
    set(USER, null);
    if (server && t) {
      fetch(TRAIL_API + "/logout", {
        method: "POST",
        headers: { Authorization: "Bearer " + t },
      }).catch(() => {});
    }
  }

  function startHeartbeat() {
    if (started) return;
    started = true;
    const tick = async () => {
      if (signedIn()) {
        try {
          await api("/heartbeat", { method: "POST", body: progressBody() });
        } catch {}
      }
    };
    tick();
    beat = setInterval(tick, 20000);
    document.addEventListener("visibilitychange", () => {
      if (document.visibilityState === "visible") tick();
    });
  }

  function stopPoll() {
    clearTimeout(poll);
  }

  function later(fn, ms) {
    stopPoll();
    poll = setTimeout(fn, ms);
  }

  function initials(name) {
    return String(name || "PT")
      .replace(/[^A-Za-z0-9]/g, "")
      .slice(0, 2)
      .toUpperCase() || "PT";
  }

  function whenSeen(ts) {
    if (!ts) return "Offline";
    const ago = Date.now() - ts;
    if (ago < ONLINE_GAP()) return "Online now";
    const m = Math.round(ago / 60000);
    if (m < 1) return "Last seen just now";
    if (m < 60) return "Last seen " + m + " min ago";
    const h = Math.round(m / 60);
    if (h < 24) return "Last seen " + h + " hr ago";
    const d = Math.round(h / 24);
    return "Last seen " + d + " day" + (d === 1 ? "" : "s") + " ago";
  }

  function ONLINE_GAP() {
    return 45000;
  }

  function lessonLabel(i) {
    if (i == null || !lessons[i]) return "Not started";
    return "Lesson " + (i + 1) + " · " + lessons[i][0];
  }

  function updateFoot() {
    const foot = document.querySelector("#accountfoot");
    if (!foot) return;
    const user = me();
    if (user) {
      foot.innerHTML =
        '<span class="avatar">' +
        esc(initials(user.displayName)) +
        "</span><span>" +
        esc(user.displayName) +
        "<small>Signed in</small></span>";
    } else {
      foot.innerHTML =
        '<span class="avatar">PT</span><span>Trail explorer<small>Personal workspace</small></span>';
    }
  }

  function accountPanel() {
    const user = me();
    if (user) {
      return (
        '<div class="panel lesson" id="accountpanel"><h3>Your account</h3><p>Share this username with your friend: <strong class="code">' +
        esc(user.displayName) +
        "</strong>. You both have the same permissions, and either of you can keep building the app from the shared GitHub repo.</p><p class=\"muted\" id=\"accountstatus\"></p><button class=\"btn\" type=\"button\" id=\"signout\">Sign out</button></div>"
      );
    }
    return (
      '<div class="panel lesson" id="accountpanel"><h3>Sign in to study together</h3><p>Pick a display name and a 4+ character PIN or passcode. No email is needed. Lessons still work offline if you stay signed out.</p><form id="authform" class="authform"><label>Display name <input id="authname" name="username" autocomplete="username" maxlength="20" required></label><label>PIN or passcode <input id="authpin" name="pin" type="password" autocomplete="current-password" minlength="4" maxlength="64" required></label><div class="actions"><button class="btn primary" type="submit" id="signin">Sign in</button><button class="btn" type="submit" id="signup">Create account</button></div><p class="muted" id="accountstatus"></p></form></div>'
    );
  }

  function friendRow(f, actions) {
    const pct = Math.round((f.completedCount / 16) * 100);
    return (
      '<div class="friendrow" data-user="' +
      esc(f.username) +
      '"><span class="avatar">' +
      esc(initials(f.displayName)) +
      '</span><span class="dot ' +
      (f.online ? "on" : "off") +
      '" title="' +
      (f.online ? "Online" : "Offline") +
      '"></span><span class="friendmeta"><strong>' +
      esc(f.displayName) +
      "</strong><small>" +
      esc(whenSeen(f.lastSeen)) +
      " · " +
      esc(lessonLabel(f.currentLesson)) +
      " · " +
      pct +
      "% complete</small></span>" +
      actions +
      "</div>"
    );
  }

  function friendsBody(data) {
    let html = accountPanel();
    if (!signedIn()) {
      html +=
        '<div class="panel lesson"><h3>Send a copy for offline use</h3><p>You can still download a standalone copy and open it in a browser. Progress stays on that device until you sign in.</p><a class="btn primary" href="Python-Trail.html" download="Python-Trail.html" id="download">Download the app</a></div>';
      return html + challenge();
    }
    html +=
      '<div class="panel lesson"><h3>Add a friend</h3><p>Enter their Python Trail username. They will need to accept before you can chat and see each other&apos;s lessons.</p><form id="addfriend" class="authform inlineform"><input id="friendname" name="username" maxlength="20" placeholder="username" autocomplete="off" required><button class="btn primary" type="submit">Add friend</button></form><p class="muted" id="friendstatus"></p>';
    if (data.incoming && data.incoming.length) {
      html += "<h3>Friend requests</h3>" + data.incoming.map((f) => friendRow(f, '<button class="btn primary accept" type="button">Accept</button>')).join("");
    }
    if (data.outgoing && data.outgoing.length) {
      html += "<h3>Waiting for them</h3>" + data.outgoing.map((f) => friendRow(f, '<span class="muted">Request sent</span>')).join("");
    }
    html += "<h3>Friends</h3>";
    if (!data.friends || !data.friends.length) {
      html += "<p class=\"muted\">No friends yet. Add your friend&apos;s username to start.</p>";
    } else {
      html += data.friends
        .map((f) =>
          friendRow(
            f,
            '<a class="btn primary" href="#chat/' +
              encodeURIComponent(f.username) +
              '">Chat</a><button class="btn unfriend" type="button">Remove</button>',
          ),
        )
        .join("");
    }
    html += "</div>" + challenge();
    return html;
  }

  function challenge() {
    return (
      '<div class="panel lesson"><h3>Pair challenge · Build a snack budget</h3><p>One person writes a list of snack prices and a budget. Their partner predicts how much money will be left. Run the code, then swap roles.</p><details><summary>Try these test cases</summary><p>A budget of 20 with prices [4, 3, 5] leaves 8. A budget of 10 with prices [5, 5] leaves 0. What happens if you go over budget?</p></details><p>' +
      btn("#lab", "Open playground", "terminal") +
      "</p></div>"
    );
  }

  function bindAccount(root) {
    const status = root.querySelector("#accountstatus");
    const say = (msg, ok) => {
      if (!status) return;
      status.textContent = msg;
      status.className = ok ? "ok" : "muted";
    };
    const form = root.querySelector("#authform");
    if (form) {
      const run = async (kind) => {
        const username = root.querySelector("#authname").value.trim();
        const pin = root.querySelector("#authpin").value;
        say(kind === "signup" ? "Creating account…" : "Signing in…");
        try {
          await signUpOrIn(kind, username, pin);
          location.hash = "#friends";
          render();
        } catch (err) {
          say(err.message || "Could not sign in.");
        }
      };
      form.addEventListener("submit", (e) => {
        e.preventDefault();
        run(e.submitter && e.submitter.id === "signup" ? "signup" : "login");
      });
    }
    const out = root.querySelector("#signout");
    if (out)
      out.onclick = () => {
        signOut(true);
        render();
      };
  }

  function bindFriends(data) {
    bindAccount(app);
    const form = document.querySelector("#addfriend");
    const status = document.querySelector("#friendstatus");
    if (form) {
      form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const username = document.querySelector("#friendname").value.trim();
        status.textContent = "Sending request…";
        try {
          await api("/friends", { method: "POST", body: { username } });
          render();
        } catch (err) {
          status.textContent = err.message || "Could not add friend.";
        }
      });
    }
    app.querySelectorAll(".accept").forEach((btnEl) => {
      btnEl.onclick = async () => {
        const username = btnEl.closest(".friendrow").dataset.user;
        try {
          await api("/friends/accept", { method: "POST", body: { username } });
          render();
        } catch (err) {
          if (status) status.textContent = err.message;
        }
      };
    });
    app.querySelectorAll(".unfriend").forEach((btnEl) => {
      btnEl.onclick = async () => {
        const username = btnEl.closest(".friendrow").dataset.user;
        if (!confirm("Remove " + username + " from your friends?")) return;
        try {
          await api("/friends/remove", { method: "POST", body: { username } });
          render();
        } catch (err) {
          if (status) status.textContent = err.message;
        }
      };
    });
    if (window.trailWorkerURL && document.querySelector("#download")) {
      document.querySelector("#download").href = location.href.split("#")[0];
    }
  }

  async function renderFriends() {
    let data = { friends: [], incoming: [], outgoing: [] };
    if (signedIn()) {
      try {
        data = await api("/friends");
        mergeProgress(data);
      } catch (err) {
        app.innerHTML =
          title("Study with friends", "Take turns writing code and explaining what it does.") +
          accountPanel() +
          '<div class="panel lesson"><p class="muted">' +
          esc(err.message || "Could not reach the online server. You can keep learning offline.") +
          "</p></div>" +
          challenge();
        bindAccount(app);
        later(renderFriends, 8000);
        return;
      }
    }
    app.innerHTML =
      title(
        "Study with friends",
        signedIn()
          ? "See when your friend is online, what lesson they are on, and send a message."
          : "Sign in to text your friend, see their lesson, and work on the same trail together.",
      ) + friendsBody(data);
    bindFriends(data);
    function scheduleFriends() {
      later(async () => {
        if (location.hash.slice(1).split("/")[0] !== "friends") return;
        const active = document.activeElement;
        const typing = active && (active.id === "friendname" || active.id === "authname" || active.id === "authpin");
        const pending = (document.querySelector("#friendname") || {}).value;
        if (typing || (pending && String(pending).trim())) {
          scheduleFriends();
          return;
        }
        renderFriends();
      }, 5000);
    }
    if (signedIn()) scheduleFriends();
  }

  function bubble(m) {
    const mine = me() && m.from === me().username;
    return (
      '<div class="bubble ' +
      (mine ? "mine" : "theirs") +
      '"><div class="bubblewho">' +
      esc(mine ? "You" : m.from) +
      "</div><div class=\"bubbletext\">" +
      esc(m.text) +
      "</div></div>"
    );
  }

  async function renderChat(name) {
    if (!signedIn()) {
      location.hash = "#friends";
      return;
    }
    const username = decodeURIComponent(name || "");
    app.innerHTML =
      '<div class="lesson chatwrap"><a class="back" href="#friends">‹ Friends</a>' +
      title("Chat", "Loading…") +
      '<div id="chatmeta"></div><div id="chatlog" class="chatlog" aria-live="polite"></div><form id="chatform" class="chatform"><input id="chattext" maxlength="1000" autocomplete="off" placeholder="Write a message"><button class="btn primary" type="submit">Send</button></form><p class="muted" id="chatstatus"></p></div>';
    const log = document.querySelector("#chatlog");
    const status = document.querySelector("#chatstatus");
    let after = 0;
    const paintFriend = (friend) => {
      const head = document.querySelector(".chatwrap .title");
      if (head && friend) {
        head.innerHTML =
          "<h1>" +
          esc(friend.displayName) +
          '</h1><p><span class="dot ' +
          (friend.online ? "on" : "off") +
          '"></span> ' +
          esc(whenSeen(friend.lastSeen)) +
          " · " +
          esc(lessonLabel(friend.currentLesson)) +
          " · " +
          Math.round((friend.completedCount / 16) * 100) +
          "% complete</p>";
      }
    };
    const pull = async () => {
      if (location.hash !== "#chat/" + encodeURIComponent(username) && location.hash !== "#chat/" + username) return;
      try {
        const data = await api("/chats/" + encodeURIComponent(username) + "?after=" + after);
        paintFriend(data.friend);
        for (const m of data.messages || []) {
          log.insertAdjacentHTML("beforeend", bubble(m));
          after = Math.max(after, m.id);
          log.scrollTop = log.scrollHeight;
        }
        if (status && status.textContent === "Connecting…") status.textContent = "";
      } catch (err) {
        if (status) status.textContent = err.message || "Chat is unavailable.";
      }
      later(pull, 2500);
    };
    document.querySelector("#chatform").addEventListener("submit", async (e) => {
      e.preventDefault();
      const input = document.querySelector("#chattext");
      const text = input.value;
      if (!text.trim()) return;
      input.value = "";
      try {
        const data = await api("/chats/" + encodeURIComponent(username), {
          method: "POST",
          body: { text },
        });
        if (data.message) {
          log.insertAdjacentHTML("beforeend", bubble(data.message));
          after = Math.max(after, data.message.id);
          log.scrollTop = log.scrollHeight;
        }
      } catch (err) {
        input.value = text;
        if (status) status.textContent = err.message || "Could not send.";
      }
    });
    status.textContent = "Connecting…";
    pull();
  }

  function onRender(r, i) {
    stopPoll();
    updateFoot();
    if (signedIn()) startHeartbeat();
    if (r === "lesson" && Number.isInteger(i)) setCurrentLesson(i);
    if (r === "friends") {
      renderFriends();
      return true;
    }
    if (r === "chat") {
      renderChat(i);
      return true;
    }
    return false;
  }

  return { onRender, syncProgress, setCurrentLesson, signedIn, startHeartbeat };
})();
