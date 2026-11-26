/**
 * Python Trail online server.
 * Accounts (display name + PIN), friends, 1:1 chat, presence, and lesson sync.
 * All users have equal permissions. Free-plan Worker + D1 (python-trail).
 */
const SESSION_MS = 90 * 24 * 60 * 60 * 1000;
const ONLINE_MS = 45 * 1000;
const MSG_MAX = 1000;
const MSG_RATE = { limit: 20, window: 60 };
const AUTH_RATE = { limit: 15, window: 600 };
const SIGNUP_RATE = { limit: 5, window: 3600 };

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, DELETE, OPTIONS",
  "Access-Control-Allow-Headers": "Authorization, Content-Type",
  "Access-Control-Max-Age": "86400",
};

export default {
  async fetch(request, env) {
    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: CORS });
    }
    try {
      await migrate(env.DB);
      return await route(request, env);
    } catch (err) {
      const msg = String(err && err.message ? err.message : err);
      const status = err && err.status ? err.status : 500;
      if (status >= 500) console.error("python-trail-server", msg);
      return json({ error: status >= 500 ? "Server error." : msg }, status);
    }
  },
};

async function route(request, env) {
  const url = new URL(request.url);
  const path = url.pathname.replace(/\/+$/, "") || "/";
  const method = request.method;

  if (method === "GET" && path === "/") {
    return json({ ok: true, name: "python-trail-server" });
  }

  if (method === "POST" && path === "/signup") {
    return signup(request, env);
  }
  if (method === "POST" && path === "/login") {
    return login(request, env);
  }

  const user = await authUser(request, env);
  if (!user) return json({ error: "Sign in to continue." }, 401);

  if (method === "POST" && path === "/logout") {
    const token = bearer(request);
    if (token) {
      await env.DB.prepare("DELETE FROM sessions WHERE token_hash = ?")
        .bind(await sha256hex(token))
        .run();
    }
    return json({ ok: true });
  }

  if (method === "GET" && path === "/me") {
    await touch(env, user, null);
    return json({ user: publicUser(user), ...progressOf(user) });
  }

  if (method === "POST" && path === "/heartbeat") {
    const body = await readJson(request);
    await touch(env, user, body);
    return json({ ok: true, serverTime: Date.now() });
  }

  if (method === "POST" && path === "/progress") {
    const body = await readJson(request);
    await touch(env, user, body);
    return json({ ok: true, ...progressOf(await loadPresence(env, user)) });
  }

  if (method === "GET" && path === "/friends") {
    await touch(env, user, null);
    return json(await friendPayload(env, user));
  }

  if (method === "POST" && path === "/friends") {
    return addFriend(request, env, user);
  }
  if (method === "POST" && path === "/friends/accept") {
    return acceptFriend(request, env, user);
  }
  if (method === "POST" && path === "/friends/remove") {
    return removeFriend(request, env, user);
  }

  const chat = path.match(/^\/chats\/([A-Za-z0-9_]{3,20})$/);
  if (chat && method === "GET") {
    return getChat(url, env, user, chat[1]);
  }
  if (chat && method === "POST") {
    return sendChat(request, env, user, chat[1]);
  }

  return json({ error: "Not found." }, 404);
}

async function migrate(db) {
  if (migrate.ok) return;
  const statements = [
    `CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      username TEXT NOT NULL UNIQUE,
      display_name TEXT NOT NULL,
      pin_salt TEXT NOT NULL,
      pin_hash TEXT NOT NULL,
      created_at INTEGER NOT NULL
    )`,
    `CREATE TABLE IF NOT EXISTS sessions (
      token_hash TEXT PRIMARY KEY,
      user_id INTEGER NOT NULL,
      created_at INTEGER NOT NULL,
      expires_at INTEGER NOT NULL,
      FOREIGN KEY (user_id) REFERENCES users(id)
    )`,
    `CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id)`,
    `CREATE TABLE IF NOT EXISTS presence (
      user_id INTEGER PRIMARY KEY,
      last_seen INTEGER NOT NULL,
      current_lesson INTEGER,
      completed TEXT NOT NULL DEFAULT '[]',
      FOREIGN KEY (user_id) REFERENCES users(id)
    )`,
    `CREATE TABLE IF NOT EXISTS friends (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      from_id INTEGER NOT NULL,
      to_id INTEGER NOT NULL,
      status TEXT NOT NULL DEFAULT 'pending',
      created_at INTEGER NOT NULL,
      UNIQUE(from_id, to_id),
      FOREIGN KEY (from_id) REFERENCES users(id),
      FOREIGN KEY (to_id) REFERENCES users(id)
    )`,
    `CREATE INDEX IF NOT EXISTS idx_friends_to ON friends(to_id, status)`,
    `CREATE INDEX IF NOT EXISTS idx_friends_from ON friends(from_id, status)`,
    `CREATE TABLE IF NOT EXISTS messages (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      lo_id INTEGER NOT NULL,
      hi_id INTEGER NOT NULL,
      sender_id INTEGER NOT NULL,
      body TEXT NOT NULL,
      created_at INTEGER NOT NULL,
      FOREIGN KEY (sender_id) REFERENCES users(id)
    )`,
    `CREATE INDEX IF NOT EXISTS idx_messages_thread ON messages(lo_id, hi_id, id)`,
    `CREATE TABLE IF NOT EXISTS rate_limits (
      key TEXT NOT NULL,
      window_start INTEGER NOT NULL,
      count INTEGER NOT NULL,
      PRIMARY KEY (key, window_start)
    )`,
  ];
  for (const sql of statements) await db.prepare(sql).run();
  migrate.ok = true;
}

async function signup(request, env) {
  const ip = clientIp(request);
  await rateLimit(env, "signup:" + ip, SIGNUP_RATE);
  const body = await readJson(request);
  const display = normalizeDisplay(body.username);
  const username = display.toLowerCase();
  const pin = normalizePin(body.pin);
  const existing = await env.DB.prepare("SELECT id FROM users WHERE username = ?")
    .bind(username)
    .first();
  if (existing) fail("That username is already taken.", 409);
  const salt = hex(crypto.getRandomValues(new Uint8Array(16)));
  const pin_hash = await hashPin(pin, salt);
  const now = Date.now();
  const result = await env.DB.prepare(
    "INSERT INTO users (username, display_name, pin_salt, pin_hash, created_at) VALUES (?, ?, ?, ?, ?)",
  )
    .bind(username, display, salt, pin_hash, now)
    .run();
  const user = {
    id: result.meta.last_row_id,
    username,
    display_name: display,
    current_lesson: null,
    completed: "[]",
    last_seen: now,
  };
  await env.DB.prepare(
    "INSERT INTO presence (user_id, last_seen, current_lesson, completed) VALUES (?, ?, NULL, '[]')",
  )
    .bind(user.id, now)
    .run();
  const token = await issueSession(env, user.id, now);
  return json({ token, user: publicUser(user), completed: [], currentLesson: null });
}

async function login(request, env) {
  const body = await readJson(request);
  const username = String(body.username || "").trim().toLowerCase();
  const pin = String(body.pin || "");
  await rateLimit(env, "login:" + clientIp(request) + ":" + username, AUTH_RATE);
  const row = await env.DB.prepare("SELECT * FROM users WHERE username = ?")
    .bind(username)
    .first();
  if (!row) fail("Username or PIN is incorrect.", 401);
  const ok = await hashPin(pin, row.pin_salt);
  if (!timingSafeEqual(ok, row.pin_hash)) fail("Username or PIN is incorrect.", 401);
  const now = Date.now();
  const user = await loadPresence(env, row);
  await touch(env, user, null);
  const token = await issueSession(env, user.id, now);
  return json({ token, user: publicUser(user), ...progressOf(user) });
}

async function addFriend(request, env, user) {
  const body = await readJson(request);
  const name = String(body.username || "").trim().toLowerCase();
  if (!/^[a-z0-9_]{3,20}$/.test(name)) fail("Enter a valid username.", 400);
  if (name === user.username) fail("You cannot add yourself.", 400);
  const other = await env.DB.prepare("SELECT * FROM users WHERE username = ?")
    .bind(name)
    .first();
  if (!other) fail("No account has that username.", 404);
  const existing = await friendship(env, user.id, other.id);
  if (existing && existing.status === "accepted") {
    return json({ ok: true, status: "accepted" });
  }
  if (existing && existing.to_id === user.id && existing.status === "pending") {
    await env.DB.prepare("UPDATE friends SET status = 'accepted' WHERE id = ?")
      .bind(existing.id)
      .run();
    return json({ ok: true, status: "accepted" });
  }
  if (existing && existing.from_id === user.id && existing.status === "pending") {
    return json({ ok: true, status: "pending" });
  }
  await env.DB.prepare(
    "INSERT INTO friends (from_id, to_id, status, created_at) VALUES (?, ?, 'pending', ?)",
  )
    .bind(user.id, other.id, Date.now())
    .run();
  return json({ ok: true, status: "pending" });
}

async function acceptFriend(request, env, user) {
  const body = await readJson(request);
  const name = String(body.username || "").trim().toLowerCase();
  const other = await env.DB.prepare("SELECT * FROM users WHERE username = ?")
    .bind(name)
    .first();
  if (!other) fail("No account has that username.", 404);
  const row = await env.DB.prepare(
    "SELECT * FROM friends WHERE from_id = ? AND to_id = ? AND status = 'pending'",
  )
    .bind(other.id, user.id)
    .first();
  if (!row) fail("There is no request to accept.", 404);
  await env.DB.prepare("UPDATE friends SET status = 'accepted' WHERE id = ?")
    .bind(row.id)
    .run();
  return json({ ok: true, status: "accepted" });
}

async function removeFriend(request, env, user) {
  const body = await readJson(request);
  const name = String(body.username || "").trim().toLowerCase();
  const other = await env.DB.prepare("SELECT * FROM users WHERE username = ?")
    .bind(name)
    .first();
  if (!other) fail("No account has that username.", 404);
  await env.DB.prepare(
    "DELETE FROM friends WHERE (from_id = ? AND to_id = ?) OR (from_id = ? AND to_id = ?)",
  )
    .bind(user.id, other.id, other.id, user.id)
    .run();
  return json({ ok: true });
}

async function getChat(url, env, user, name) {
  const other = await requireFriend(env, user, name);
  const after = Number(url.searchParams.get("after") || 0) || 0;
  const lo = Math.min(user.id, other.id);
  const hi = Math.max(user.id, other.id);
  const rows = await env.DB.prepare(
    "SELECT id, sender_id, body, created_at FROM messages WHERE lo_id = ? AND hi_id = ? AND id > ? ORDER BY id ASC LIMIT 200",
  )
    .bind(lo, hi, after)
    .all();
  await touch(env, user, null);
  const presence = await loadPresence(env, other);
  return json({
    friend: serializeFriend(presence),
    messages: (rows.results || []).map((m) => ({
      id: m.id,
      from: m.sender_id === user.id ? user.username : other.username,
      text: m.body,
      at: m.created_at,
    })),
  });
}

async function sendChat(request, env, user, name) {
  await rateLimit(env, "msg:" + user.id, MSG_RATE);
  const other = await requireFriend(env, user, name);
  const body = await readJson(request);
  const text = String(body.text || "").trim();
  if (!text) fail("Type a message first.", 400);
  if (text.length > MSG_MAX) fail("Messages can be at most 1000 characters.", 400);
  if ([...text].some((ch) => {
    const c = ch.codePointAt(0);
    return c < 9 || (c > 10 && c < 13) || (c > 13 && c < 32);
  })) {
    fail("Message has disallowed characters.", 400);
  }
  const now = Date.now();
  const lo = Math.min(user.id, other.id);
  const hi = Math.max(user.id, other.id);
  const result = await env.DB.prepare(
    "INSERT INTO messages (lo_id, hi_id, sender_id, body, created_at) VALUES (?, ?, ?, ?, ?)",
  )
    .bind(lo, hi, user.id, text, now)
    .run();
  await touch(env, user, null);
  return json({
    message: {
      id: result.meta.last_row_id,
      from: user.username,
      text,
      at: now,
    },
  });
}

async function requireFriend(env, user, name) {
  const other = await env.DB.prepare("SELECT * FROM users WHERE username = ?")
    .bind(String(name || "").toLowerCase())
    .first();
  if (!other) fail("No account has that username.", 404);
  const row = await friendship(env, user.id, other.id);
  if (!row || row.status !== "accepted") fail("You can only chat with friends.", 403);
  return loadPresence(env, other);
}

async function friendship(env, a, b) {
  return env.DB.prepare(
    "SELECT * FROM friends WHERE (from_id = ? AND to_id = ?) OR (from_id = ? AND to_id = ?)",
  )
    .bind(a, b, b, a)
    .first();
}

async function friendPayload(env, user) {
  const rows = await env.DB.prepare(
    "SELECT * FROM friends WHERE from_id = ? OR to_id = ?",
  )
    .bind(user.id, user.id)
    .all();
  const ids = new Set();
  const incoming = [];
  const outgoing = [];
  const accepted = [];
  for (const row of rows.results || []) {
    if (row.status === "accepted") {
      ids.add(row.from_id === user.id ? row.to_id : row.from_id);
    } else if (row.to_id === user.id) {
      incoming.push(row.from_id);
    } else {
      outgoing.push(row.to_id);
    }
  }
  const allIds = [...new Set([...ids, ...incoming, ...outgoing])];
  const people = new Map();
  if (allIds.length) {
    const placeholders = allIds.map(() => "?").join(",");
    const found = await env.DB.prepare(
      `SELECT u.id, u.username, u.display_name, p.last_seen, p.current_lesson, p.completed
       FROM users u LEFT JOIN presence p ON p.user_id = u.id
       WHERE u.id IN (${placeholders})`,
    )
      .bind(...allIds)
      .all();
    for (const p of found.results || []) people.set(p.id, p);
  }
  const pack = (idList) =>
    idList
      .map((id) => people.get(id))
      .filter(Boolean)
      .map(serializeFriend);
  return {
    user: publicUser(user),
    ...progressOf(user),
    friends: pack([...ids]),
    incoming: pack(incoming),
    outgoing: pack(outgoing),
  };
}

function serializeFriend(row) {
  const completed = parseCompleted(row.completed);
  return {
    username: row.username,
    displayName: row.display_name,
    online: !!(row.last_seen && Date.now() - row.last_seen < ONLINE_MS),
    lastSeen: row.last_seen || null,
    currentLesson: row.current_lesson == null ? null : Number(row.current_lesson),
    completed,
    completedCount: completed.length,
  };
}

function publicUser(user) {
  return { username: user.username, displayName: user.display_name };
}

function progressOf(user) {
  const completed = parseCompleted(user.completed);
  return {
    currentLesson: user.current_lesson == null ? null : Number(user.current_lesson),
    completed,
  };
}

function parseCompleted(value) {
  try {
    const list = JSON.parse(value || "[]");
    if (!Array.isArray(list)) return [];
    return [
      ...new Set(
        list
          .map((n) => Number(n))
          .filter((n) => Number.isInteger(n) && n >= 0 && n <= 15),
      ),
    ].sort((a, b) => a - b);
  } catch {
    return [];
  }
}

async function touch(env, user, body) {
  const now = Date.now();
  let current =
    body && body.currentLesson != null && Number.isInteger(Number(body.currentLesson))
      ? Number(body.currentLesson)
      : user.current_lesson;
  if (current != null && (current < 0 || current > 15)) current = user.current_lesson;
  let completed = parseCompleted(user.completed);
  if (body && Array.isArray(body.completed)) {
    completed = [
      ...new Set([...completed, ...parseCompleted(JSON.stringify(body.completed))]),
    ].sort((a, b) => a - b);
  }
  const jsonDone = JSON.stringify(completed);
  await env.DB.prepare(
    `INSERT INTO presence (user_id, last_seen, current_lesson, completed)
     VALUES (?, ?, ?, ?)
     ON CONFLICT(user_id) DO UPDATE SET
       last_seen = excluded.last_seen,
       current_lesson = excluded.current_lesson,
       completed = excluded.completed`,
  )
    .bind(user.id, now, current, jsonDone)
    .run();
  user.last_seen = now;
  user.current_lesson = current;
  user.completed = jsonDone;
}

async function loadPresence(env, user) {
  const row = await env.DB.prepare("SELECT * FROM presence WHERE user_id = ?")
    .bind(user.id)
    .first();
  return {
    ...user,
    last_seen: row ? row.last_seen : null,
    current_lesson: row ? row.current_lesson : null,
    completed: row ? row.completed : "[]",
  };
}

async function issueSession(env, userId, now) {
  const token = hex(crypto.getRandomValues(new Uint8Array(32)));
  await env.DB.prepare(
    "INSERT INTO sessions (token_hash, user_id, created_at, expires_at) VALUES (?, ?, ?, ?)",
  )
    .bind(await sha256hex(token), userId, now, now + SESSION_MS)
    .run();
  return token;
}

async function authUser(request, env) {
  const token = bearer(request);
  if (!token) return null;
  const row = await env.DB.prepare(
    `SELECT u.*, p.last_seen, p.current_lesson, p.completed
     FROM sessions s
     JOIN users u ON u.id = s.user_id
     LEFT JOIN presence p ON p.user_id = u.id
     WHERE s.token_hash = ? AND s.expires_at > ?`,
  )
    .bind(await sha256hex(token), Date.now())
    .first();
  return row || null;
}

function bearer(request) {
  const h = request.headers.get("Authorization") || "";
  const m = h.match(/^Bearer\s+([A-Fa-f0-9]{64})$/);
  return m ? m[1].toLowerCase() : null;
}

async function rateLimit(env, key, { limit, window }) {
  const windowStart = Math.floor(Date.now() / 1000 / window) * window;
  try {
    await env.DB.prepare(
      `INSERT INTO rate_limits (key, window_start, count) VALUES (?, ?, 1)
       ON CONFLICT(key, window_start) DO UPDATE SET count = count + 1`,
    )
      .bind(key, windowStart)
      .run();
  } catch {
    // If the table is mid-migrate, skip rather than blocking the request.
    return;
  }
  const row = await env.DB.prepare(
    "SELECT count FROM rate_limits WHERE key = ? AND window_start = ?",
  )
    .bind(key, windowStart)
    .first();
  if (row && row.count > limit) fail("Too many attempts. Try again in a bit.", 429);
  if (Math.random() < 0.02) {
    await env.DB.prepare("DELETE FROM rate_limits WHERE window_start < ?")
      .bind(windowStart - window * 3)
      .run();
  }
}

function normalizeDisplay(value) {
  const name = String(value || "").trim();
  if (!/^[A-Za-z0-9_]{3,20}$/.test(name)) {
    fail("Usernames must be 3–20 letters, numbers, or underscores.", 400);
  }
  return name;
}

function normalizePin(value) {
  const pin = String(value ?? "");
  if (pin.length < 4 || pin.length > 64) fail("Choose a PIN or passcode of at least 4 characters.", 400);
  if (/\s/.test(pin)) fail("The PIN cannot contain spaces.", 400);
  return pin;
}

async function hashPin(pin, saltHex) {
  const enc = new TextEncoder();
  const key = await crypto.subtle.importKey("raw", enc.encode(pin), "PBKDF2", false, ["deriveBits"]);
  const bits = await crypto.subtle.deriveBits(
    { name: "PBKDF2", salt: bytes(saltHex), iterations: 8000, hash: "SHA-256" },
    key,
    256,
  );
  return hex(new Uint8Array(bits));
}

async function sha256hex(text) {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(text));
  return hex(new Uint8Array(buf));
}

function timingSafeEqual(a, b) {
  if (typeof a !== "string" || typeof b !== "string" || a.length !== b.length) return false;
  let out = 0;
  for (let i = 0; i < a.length; i++) out |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return out === 0;
}

function hex(bytesArr) {
  return [...bytesArr].map((b) => b.toString(16).padStart(2, "0")).join("");
}

function bytes(hexStr) {
  const out = new Uint8Array(hexStr.length / 2);
  for (let i = 0; i < out.length; i++) out[i] = parseInt(hexStr.slice(i * 2, i * 2 + 2), 16);
  return out;
}

function clientIp(request) {
  return request.headers.get("CF-Connecting-IP") || "unknown";
}

async function readJson(request) {
  const text = await request.text();
  if (text.length > 16_384) fail("Request is too large.", 413);
  if (!text) return {};
  try {
    const data = JSON.parse(text);
    if (data && typeof data === "object") return data;
  } catch {}
  fail("Send JSON in the request body.", 400);
}

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json; charset=utf-8", ...CORS },
  });
}

function fail(message, status) {
  const err = new Error(message);
  err.status = status;
  throw err;
}
