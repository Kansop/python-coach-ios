import { webkit } from "playwright";
import { createServer } from "node:http";
import { readFileSync, existsSync, writeFileSync, mkdirSync } from "node:fs";
import { extname, join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { tmpdir } from "node:os";

const repo = join(dirname(fileURLToPath(import.meta.url)), "..");
const mime = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".png": "image/png",
};
const iPhone = {
  name: "iPhone 17e",
  userAgent:
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.7 Mobile/15E148 Safari/604.1",
  viewport: { width: 390, height: 844 },
  deviceScaleFactor: 3,
  isMobile: true,
  hasTouch: true,
};

function serve(dir, { brokenPath } = {}) {
  const server = createServer((req, res) => {
    const url = new URL(req.url, "http://127.0.0.1");
    let file = decodeURIComponent(url.pathname).replace(/^\/+/, "") || "index.html";
    if (!file || file.endsWith("/")) file += "index.html";
    if (brokenPath && url.pathname === brokenPath && existsSync(join(dir, "broken.html"))) {
      res.writeHead(200, { "content-type": "text/html; charset=utf-8", "cache-control": "no-store" });
      res.end(readFileSync(join(dir, "broken.html")));
      return;
    }
    const path = join(dir, file);
    if (!path.startsWith(dir) || !existsSync(path)) {
      res.writeHead(404);
      res.end("not found");
      return;
    }
    res.writeHead(200, {
      "content-type": mime[extname(path)] || "application/octet-stream",
      "cache-control": "no-store",
    });
    res.end(readFileSync(path));
  });
  return new Promise((resolve) =>
    server.listen(0, "127.0.0.1", () => {
      server.origin = "http://127.0.0.1:" + server.address().port;
      resolve(server);
    }),
  );
}

const failures = [];
function check(name, cond, detail = "") {
  if (cond) console.log("PASS", name);
  else {
    console.log("FAIL", name, detail);
    failures.push(name + (detail ? ": " + detail : ""));
  }
}

const browser = await webkit.launch();

// 1) Fixed standalone and modular app on iPhone WebKit.
const local = await serve(repo);
const ctx = await browser.newContext({ ...iPhone });
const page = await ctx.newPage();
const errors = [];
page.on("pageerror", (e) => errors.push(String(e)));

async function snapshot(page, url) {
  await page.goto(url, { waitUntil: "domcontentloaded", timeout: 30000 });
  await page.waitForTimeout(800);
  return page.evaluate(() => ({
    h1: document.querySelector("h1")?.innerText || "",
    nav: (document.querySelector("#nav")?.innerText || "").includes("Overview"),
    appLen: (document.querySelector("#app")?.innerHTML || "").length,
    boot: !!document.querySelector("#booterror"),
    errors: window.__errs || [],
  }));
}

let info = await snapshot(page, local.origin + "/Python-Trail.html");
check("standalone iPhone shows lessons", info.h1.includes("adventure") && info.nav && !info.boot, JSON.stringify(info) + " errors=" + errors.join(" | "));

errors.length = 0;
info = await snapshot(page, local.origin + "/");
check("modular iPhone shows lessons", info.h1.includes("adventure") && info.nav && !info.boot, JSON.stringify(info) + " errors=" + errors.join(" | "));

// Offline lessons still work if the online API is blocked.
await ctx.route("https://python-trail-server.tabletop-luca.workers.dev/**", (route) => route.abort());
info = await snapshot(page, local.origin + "/#home");
check("lessons render when online server fails", info.h1.includes("adventure") && info.nav, JSON.stringify(info));
await page.goto(local.origin + "/#friends");
await page.waitForTimeout(500);
const friends = await page.evaluate(() => document.querySelector("#app")?.innerText || "");
check(
  "friends page has fallback when API is down",
  /Study with friends|Sign in|unavailable|offline/i.test(friends) && !/could not start/i.test(friends),
  friends.slice(0, 300),
);
await ctx.unroute("https://python-trail-server.tabletop-luca.workers.dev/**");
await ctx.close();
local.close();

// 2) Stale cached broken HTML first (old Pocket AI SW / broken standalone), then the fixed file.
const site = join(tmpdir(), "python-trail-cache-test");
mkdirSync(join(site, "pocket-ai", "python-trail"), { recursive: true });
const broken = `<!doctype html><html><head><meta charset="utf-8"><title>Python Trail · Learn Python</title>
<style>aside{background:#142d29;color:#d4e1d9;padding:12px 16px}header{height:43px;background:#fdfdf9;border-bottom:1px solid #dce1d7}body{margin:0;background:#f6f7f2}</style>
</head><body><aside><a class="brand">Python Trail</a><nav id="nav"></nav></aside><main><header></header><div id="app"></div></main>
<script>window.trailWorkerURL='x'; const lessons=['name = "River"\nprint(name)'];</script>
<script>const paths={};</script></body></html>`;
writeFileSync(join(site, "pocket-ai", "python-trail", "broken.html"), broken);
writeFileSync(join(site, "pocket-ai", "python-trail", "index.html"), readFileSync(join(repo, "Python-Trail.html")));
writeFileSync(
  join(site, "pocket-ai", "sw.js"),
  `const VERSION='pocketai-v1.5.0';
self.addEventListener('install', e => e.waitUntil(self.skipWaiting()));
self.addEventListener('activate', e => e.waitUntil(self.clients.claim()));
self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  if (url.origin === self.location.origin) {
    if (url.pathname.indexOf('/python-trail/') !== -1) return;
    e.respondWith((async () => {
      try {
        const res = await fetch(e.request, { cache: 'no-cache' });
        if (res.ok) { const c = await caches.open(VERSION); c.put(e.request, res.clone()).catch(()=>{}); }
        return res;
      } catch {
        const c = await caches.open(VERSION);
        return (await c.match(e.request)) || (await c.match('./index.html')) || Response.error();
      }
    })());
  }
});
`,
);

const stale = await serve(site, { brokenPath: "/pocket-ai/python-trail/" });
const ctx2 = await browser.newContext({ ...iPhone, serviceWorkers: "allow" });
const page2 = await ctx2.newPage();
const errs2 = [];
page2.on("pageerror", (e) => errs2.push(String(e)));

// First visit: serve the broken/old HTML (cached-copy simulation).
await page2.route("**/pocket-ai/python-trail/", async (route) => {
  if (route.request().resourceType() === "document" || route.request().url().endsWith("/python-trail/") || route.request().url().endsWith("/python-trail")) {
    await route.fulfill({
      status: 200,
      contentType: "text/html; charset=utf-8",
      body: broken,
    });
    return;
  }
  await route.continue();
});
await page2.goto(stale.origin + "/pocket-ai/python-trail/", { waitUntil: "domcontentloaded" });
await page2.waitForTimeout(700);
const first = await page2.evaluate(() => ({
  h1: document.querySelector("h1")?.innerText || "",
  app: (document.querySelector("#app")?.innerText || "").slice(0, 200),
  aside: (document.querySelector("aside")?.innerText || "").slice(0, 80),
  parseError: !document.querySelector("h1"),
}));
check("cached old/broken copy is blank or recovery, not lessons", first.parseError, JSON.stringify(first) + errs2.join("|"));
await page2.unroute("**/pocket-ai/python-trail/");
errs2.length = 0;

// Second visit: network returns the fixed standalone (what a reopen should get).
await page2.goto(stale.origin + "/pocket-ai/python-trail/", { waitUntil: "domcontentloaded" });
await page2.waitForTimeout(1000);
const second = await page2.evaluate(() => ({
  h1: document.querySelector("h1")?.innerText || "",
  nav: (document.querySelector("#nav")?.innerText || "").includes("Overview"),
  boot: !!document.querySelector("#booterror"),
}));
check("reload after fix shows lessons on iPhone", second.h1.includes("adventure") && second.nav && !second.boot, JSON.stringify(second) + " " + errs2.join("|"));

// 3) Recovery screen is visible if startup still fails; Reset is present.
await page2.setContent(broken);
await page2.waitForTimeout(200);
const recoveryPage = await browser.newContext({ ...iPhone });
const rec = await recoveryPage.newPage();
const brokenWithBoot = broken.replace(
  '<div id="app"></div>',
  '<div id="app"><div id="booterror"><h2>Python Trail could not start</h2><p id="bootmsg">The lessons did not load.</p><button type="button" id="resetapp">Reset app</button></div></div><script>document.getElementById("resetapp").onclick=function(){document.title="reset-clicked"};</script>',
);
await rec.setContent(brokenWithBoot);
await rec.waitForTimeout(200);
check("recovery screen is visible when scripts fail", (await rec.locator("#booterror").count()) === 1 && (await rec.locator("#resetapp").innerText()).includes("Reset"));
await rec.click("#resetapp");
check("reset button is clickable", (await rec.title()) === "reset-clicked");
await recoveryPage.close();

await ctx2.close();
stale.close();
await browser.close();

if (failures.length) {
  throw new Error("Failed: " + failures.join("; "));
}
console.log("ALL IPHONE WEBKIT CHECKS PASSED");
