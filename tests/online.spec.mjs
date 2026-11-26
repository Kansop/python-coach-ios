import { webkit, chromium } from "playwright";
import assert from "node:assert/strict";
import { createServer } from "node:http";
import { readFileSync, existsSync } from "node:fs";
import { extname, join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const repo = join(dirname(fileURLToPath(import.meta.url)), "..");

const mime = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".png": "image/png",
  ".txt": "text/plain",
};

function serve(dir) {
  const server = createServer((req, res) => {
    const url = new URL(req.url, "http://127.0.0.1");
    let file = decodeURIComponent(url.pathname).replace(/^\/+/, "");
    if (!file || file.endsWith("/")) file = (file || "") + "index.html";
    const path = join(dir, file);
    if (!path.startsWith(dir) || !existsSync(path)) {
      res.writeHead(404);
      res.end("not found");
      return;
    }
    res.writeHead(200, { "content-type": mime[extname(path)] || "application/octet-stream" });
    res.end(readFileSync(path));
  });
  return new Promise((resolve) =>
    server.listen(0, "127.0.0.1", () => {
      const { port } = server.address();
      server.base = "http://127.0.0.1:" + port;
      resolve(server);
    }),
  );
}

let origin = "";

const stamp = Date.now().toString(36);
const users = [
  { name: "Luca" + stamp.slice(-6), pin: "mi1234", lessons: [0] },
  { name: "Friend" + stamp.slice(-6), pin: "fl5678", lessons: [] },
];

async function signUp(page, user, kind = "signup") {
  await page.goto(origin + "/#friends");
  await page.waitForSelector("#authform");
  await page.fill("#authname", user.name);
  await page.fill("#authpin", user.pin);
  await page.click(kind === "signup" ? "#signup" : "#signin");
  await page.waitForSelector("#signout", { timeout: 20000 });
  await assert.doesNotReject(async () => {
    const shown = await page.locator("#accountpanel strong").innerText();
    assert.equal(shown, user.name);
  });
}

async function completeFirstLesson(page) {
  await page.goto(origin + "/#lesson/0");
  await page.waitForSelector("#code");
  await page.fill("#code", 'print("Hello, team!")');
  await page.click("#run");
  await page.waitForSelector(".ok", { timeout: 20000 });
}

const failures = [];
function check(name, cond, detail = "") {
  if (cond) console.log("PASS", name);
  else {
    console.log("FAIL", name, detail);
    failures.push(name + (detail ? ": " + detail : ""));
  }
}

const server = await serve(repo);
origin = server.base;
async function launch() {
  try {
    return await chromium.launch({ channel: "chrome" });
  } catch {
    return await webkit.launch();
  }
}
const browser = await launch();
const contextA = await browser.newContext();
const contextB = await browser.newContext();
const a = await contextA.newPage();
const b = await contextB.newPage();
a.setDefaultTimeout(20000);
b.setDefaultTimeout(20000);

try {
  // Offline mode still works while signed out.
  await a.goto(origin + "/#home");
  const home = await a.locator("h1").innerText();
  check("offline home renders", /adventure starts here|Welcome back|Summit reached/i.test(home), home);
  await a.goto(origin + "/#friends");
  check("signed-out friends shows auth form", await a.locator("#authform").count() === 1);

  await signUp(a, users[0]);
  await signUp(b, users[1]);
  check("two accounts signed in", (await a.locator("#signout").count()) === 1 && (await b.locator("#signout").count()) === 1);

  await completeFirstLesson(a);
  check("lesson 1 complete locally", (await a.locator(".ok").count()) >= 1);

  await a.goto(origin + "/#friends");
  await a.waitForSelector("#addfriend");
  await a.fill("#friendname", users[1].name);
  await a.click('#addfriend button[type="submit"]');
  await a.waitForFunction((name) => document.body.innerText.includes("Waiting") || document.body.innerText.includes(name), users[1].name, { timeout: 15000 });

  await b.goto(origin + "/#friends");
  await b.waitForSelector(".accept", { timeout: 20000 });
  await b.click(".accept");
  await b.waitForSelector('a[href^="#chat/"]', { timeout: 15000 });
  check("friend request accepted", (await b.locator('a[href^="#chat/"]').count()) >= 1);

  // B should see A's lesson progress. Poll may take a couple of seconds.
  await b.waitForFunction(() => document.body.innerText.includes("% complete") && document.body.innerText.includes("Lesson 1"), null, { timeout: 20000 });
  const friendsText = await b.locator(".friendrow").innerText();
  check("friend sees current lesson and progress", /Lesson 1/.test(friendsText) && /6% complete|7% complete/.test(friendsText), friendsText);
  check("friend shows online dot", (await b.locator(".friendrow .dot.on").count()) >= 1, await b.locator(".friendrow").innerHTML());

  await b.click('a[href^="#chat/"]');
  await b.waitForSelector("#chatform");
  await a.goto(origin + "/#friends");
  await a.waitForSelector('a[href^="#chat/"]');
  await a.click('a[href^="#chat/"]');
  await a.waitForSelector("#chatform");

  const payload = `<img src=x onerror=alert(1)> hi from ${users[0].name}`;
  await a.fill("#chattext", payload);
  await a.click('#chatform button[type="submit"]');
  await a.waitForFunction((text) => document.querySelector(".bubbletext")?.textContent.includes(text), "hi from " + users[0].name);
  await b.waitForFunction((text) => document.querySelector(".bubbletext")?.textContent.includes(text), "hi from " + users[0].name, { timeout: 20000 });

  const htmlA = await a.locator(".bubbletext").first().innerHTML();
  const htmlB = await b.locator(".bubbletext").first().innerHTML();
  const textB = await b.locator(".bubbletext").first().innerText();
  check("chat delivered to friend", textB.includes("hi from " + users[0].name), textB);
  check("chat text is escaped (no XSS)", !htmlA.includes("<img") && !htmlB.includes("<img") && htmlA.includes("&lt;img"), htmlA + " || " + htmlB);

  await b.fill("#chattext", "See you from Florida");
  await b.click('#chatform button[type="submit"]');
  await a.waitForFunction(() => document.body.innerText.includes("See you from Florida"), null, { timeout: 20000 });
  check("reply delivered", (await a.locator(".bubbletext").count()) >= 2);

  // Presence on chat header
  const header = await b.locator(".chatwrap .title").innerText();
  check("chat header shows presence/progress", /Online now|Last seen/.test(header) && /% complete/.test(header), header);

  if (failures.length) {
    throw new Error("Failed: " + failures.join("; "));
  }
  console.log("ALL PLAYWRIGHT CHECKS PASSED");
} finally {
  await browser.close();
  server.close();
}
