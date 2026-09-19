import test from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import fs from "node:fs";
import http from "node:http";
import os from "node:os";
import path from "node:path";

import { buildCandleFilename, buildCoverageRecoveryChunks, createFarazCandleApi, findCandleCoverageGaps, normalizeClearTextSession } from "../server/faraz-candle-api.js";
import { buildChartVerificationRanges } from "../src/features/candle-update.js";

async function listenForApi(t, api) {
  const routes = new Map();
  api.configureServer({ middlewares: { use(route, handler) { routes.set(route, handler); } } });
  const server = http.createServer((req, res) => {
    const handler = routes.get(new URL(req.url, "http://localhost").pathname);
    if (handler) return handler(req, res);
    res.statusCode = 404;
    res.end();
  });
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  t.after(() => server.close());
  return `http://127.0.0.1:${server.address().port}`;
}

function fakeFarazLoginBrowser({ logoutStatus = 200, profileStatusAfterLogout = 401 } = {}) {
  let closed = false;
  const siteRequests = [];
  const browserProbeEndpoints = [];
  const cookies = [{ name: "farazSession", value: "test-browser-cookie", domain: ".faraz.io", path: "/", expires: -1 }];
  let pageUrl = "about:blank";
  const page = {
    url: () => pageUrl,
    isClosed: () => false,
    on() {},
    async goto(url) { pageUrl = url; },
    async bringToFront() {},
    async evaluate(_fn, args) {
      if (args?.endpoint) {
        browserProbeEndpoints.push(args.endpoint);
        return { status: 200, ok: true, contentType: "application/json", redirectedToLogin: false };
      }
      if (args?.logoutEndpoint) {
        siteRequests.push({ endpoint: args.logoutEndpoint, browser: "login-browser" });
        return { logoutStatus, profileStatus: profileStatusAfterLogout };
      }
      return "";
    },
  };
  const context = {
    pages: () => [page],
    newPage: async () => page,
    on() {},
    setExtraHTTPHeaders: async () => {},
    cookies: async () => cookies,
    storageState: async () => ({ cookies, origins: [] }),
  };
  const browser = {
    on() {},
    isConnected: () => !closed,
    async close() { closed = true; },
  };
  return { browser, context, page, siteRequests, browserProbeEndpoints, isClosed: () => closed };
}

function writeFakeSession(workspaceRoot) {
  const secretDir = path.join(workspaceRoot, "runtime", "cache", "secret");
  fs.mkdirSync(secretDir, { recursive: true });
  const sessionPath = path.join(secretDir, "faraz-session.dpapi.json");
  fs.writeFileSync(sessionPath, JSON.stringify({
    format: "clear-text", "x-access-token": "test-file-token", farazSession: "test-file-cookie",
    storageState: { cookies: [{ name: "farazSession", value: "test-file-cookie", domain: ".faraz.io", path: "/", expires: -1 }], origins: [] },
    historyAuth: null,
  }));
  return sessionPath;
}

test("removing the only FARAZ session file disconnects an open browser context", async (t) => {
  const workspaceRoot = fs.mkdtempSync(path.join(os.tmpdir(), "faraz-file-authority-"));
  t.after(() => fs.rmSync(workspaceRoot, { recursive: true, force: true }));
  const sessionPath = writeFakeSession(workspaceRoot);
  const managed = fakeFarazLoginBrowser();
  const api = createFarazCandleApi({ workspaceRoot, launchBrowser: async () => managed,
    fetchImpl: async () => new Response("{}", { headers: { "content-type": "application/json" } }) });
  const origin = await listenForApi(t, api);
  await fetch(`${origin}/api/faraz/auth/browser`, { method: "POST" });
  fs.unlinkSync(sessionPath);

  const status = await fetch(`${origin}/api/faraz/auth/status`).then((response) => response.json());
  assert.equal(status.connected, false);
  assert.equal(status.state, "not_connected");
  assert.equal(fs.existsSync(sessionPath), false);
});

test("FARAZ history cannot use cached credentials after the session file is removed", async (t) => {
  const workspaceRoot = fs.mkdtempSync(path.join(os.tmpdir(), "faraz-history-file-"));
  t.after(() => fs.rmSync(workspaceRoot, { recursive: true, force: true }));
  const sessionPath = writeFakeSession(workspaceRoot);
  const managed = fakeFarazLoginBrowser();
  let historyRequests = 0;
  const api = createFarazCandleApi({ workspaceRoot, launchBrowser: async () => managed,
    fetchImpl: async () => { historyRequests++; return new Response("{}", { headers: { "content-type": "application/json" } }); } });
  const origin = await listenForApi(t, api);
  await fetch(`${origin}/api/faraz/auth/browser`, { method: "POST" });
  fs.unlinkSync(sessionPath);

  const response = await fetch(`${origin}/api/faraz/history`, { method: "POST", headers: { "content-type": "application/json" },
    body: JSON.stringify({ symbolName: "TEST:PAIR", resolution: "5S", from: 100, to: 110 }) });
  assert.equal(response.status, 401);
  assert.equal(historyRequests, 0);
  assert.equal(fs.existsSync(sessionPath), false);
});

test("signing in immediately after manual deletion starts a fresh login browser", async (t) => {
  const workspaceRoot = fs.mkdtempSync(path.join(os.tmpdir(), "faraz-fresh-login-"));
  t.after(() => fs.rmSync(workspaceRoot, { recursive: true, force: true }));
  const sessionPath = writeFakeSession(workspaceRoot);
  const oldBrowser = fakeFarazLoginBrowser();
  const newBrowser = fakeFarazLoginBrowser();
  let launches = 0;
  const api = createFarazCandleApi({ workspaceRoot,
    launchBrowser: async () => (++launches === 1 ? oldBrowser : newBrowser),
    fetchImpl: async () => new Response("{}", { headers: { "content-type": "application/json" } }) });
  const origin = await listenForApi(t, api);
  await fetch(`${origin}/api/faraz/auth/browser`, { method: "POST" });
  fs.unlinkSync(sessionPath);

  const opened = await fetch(`${origin}/api/faraz/auth/open`, { method: "POST" });
  assert.equal(opened.status, 200);
  assert.equal(launches, 2);
  assert.equal(oldBrowser.isClosed(), true);
  const status = await fetch(`${origin}/api/faraz/auth/status`).then((response) => response.json());
  assert.equal(status.connected, true);
  assert.equal(fs.existsSync(sessionPath), true);
  assert.equal(newBrowser.isClosed(), true);
});

test("FARAZ login saves clear text then closes the temporary browser", async (t) => {
  const workspaceRoot = fs.mkdtempSync(path.join(os.tmpdir(), "faraz-same-browser-"));
  t.after(() => fs.rmSync(workspaceRoot, { recursive: true, force: true }));
  const managed = fakeFarazLoginBrowser();
  const api = createFarazCandleApi({ workspaceRoot, launchBrowser: async () => managed,
    fetchImpl: async () => new Response("{}", { headers: { "content-type": "application/json" } }) });
  const origin = await listenForApi(t, api);
  const sessionPath = path.join(workspaceRoot, "runtime", "cache", "secret", "faraz-session.dpapi.json");

  const opened = await fetch(`${origin}/api/faraz/auth/open`, { method: "POST" });
  assert.equal(opened.status, 200);
  const status = await fetch(`${origin}/api/faraz/auth/status`).then((response) => response.json());
  assert.equal(status.connected, true);
  assert.deepEqual(managed.browserProbeEndpoints, ["https://faraz.io/api/public/authentication/me"]);
  assert.equal(JSON.parse(fs.readFileSync(sessionPath, "utf8")).format, "clear-text");
  assert.equal(managed.isClosed(), true);

  const logout = await fetch(`${origin}/api/faraz/auth/logout`, { method: "POST" });
  assert.equal(logout.status, 200);
  assert.deepEqual(managed.siteRequests, []);
  assert.equal(fs.existsSync(sessionPath), false);
  assert.equal(managed.isClosed(), true);
});

test("FARAZ local logout clears an invalid website session without contacting FARAZ", async (t) => {
  const workspaceRoot = fs.mkdtempSync(path.join(os.tmpdir(), "faraz-logout-retry-"));
  t.after(() => fs.rmSync(workspaceRoot, { recursive: true, force: true }));
  const sessionPath = writeFakeSession(workspaceRoot);
  const managed = fakeFarazLoginBrowser({ logoutStatus: 500, profileStatusAfterLogout: 200 });
  const api = createFarazCandleApi({ workspaceRoot, launchBrowser: async () => managed });
  const origin = await listenForApi(t, api);
  await fetch(`${origin}/api/faraz/auth/open`, { method: "POST" });

  const logout = await fetch(`${origin}/api/faraz/auth/logout`, { method: "POST" });
  assert.equal(logout.status, 200);
  assert.equal(fs.existsSync(sessionPath), false);
  assert.equal(managed.isClosed(), true);
  assert.deepEqual(managed.siteRequests, []);
});

test("FARAZ local logout does not require the original login browser", async (t) => {
  const workspaceRoot = fs.mkdtempSync(path.join(os.tmpdir(), "faraz-wrong-browser-"));
  t.after(() => fs.rmSync(workspaceRoot, { recursive: true, force: true }));
  const sessionPath = writeFakeSession(workspaceRoot);
  const otherBrowser = fakeFarazLoginBrowser();
  const api = createFarazCandleApi({ workspaceRoot, launchBrowser: async () => otherBrowser });
  const origin = await listenForApi(t, api);
  await fetch(`${origin}/api/faraz/auth/browser`, { method: "POST" });

  const logout = await fetch(`${origin}/api/faraz/auth/logout`, { method: "POST" });
  assert.equal(logout.status, 200);
  assert.equal(fs.existsSync(sessionPath), false);
  assert.equal(otherBrowser.siteRequests.length, 0);
});

test("editable clear-text FARAZ sessions stay readable and manual changes take effect", async (t) => {
  const workspaceRoot = fs.mkdtempSync(path.join(os.tmpdir(), "faraz-editable-session-"));
  t.after(() => fs.rmSync(workspaceRoot, { recursive: true, force: true }));
  const secretDir = path.join(workspaceRoot, "runtime", "cache", "secret");
  fs.mkdirSync(secretDir, { recursive: true });
  const sessionPath = path.join(secretDir, "faraz-session.dpapi.json");
  const session = {
    format: "clear-text",
    "x-access-token": "first-test-token",
    farazSession: "",
    storageState: { cookies: [], origins: [] },
    historyAuth: null,
  };
  fs.writeFileSync(sessionPath, JSON.stringify(session));
  const observedTokens = [];
  const api = createFarazCandleApi({
    workspaceRoot,
    fetchImpl: async (url, options) => {
      const request = new URL(url);
      if (request.pathname.endsWith("/trading-view/history")) {
        observedTokens.push(options.headers["x-access-token"]);
      }
      return new Response("{}", { headers: { "content-type": "application/json" } });
    },
  });
  const origin = await listenForApi(t, api);

  const firstStatus = await fetch(`${origin}/api/faraz/auth/status`).then((response) => response.json());
  assert.equal(firstStatus.connected, true);
  assert.equal(JSON.parse(fs.readFileSync(sessionPath, "utf8")).format, "clear-text");

  session["x-access-token"] = "edited-test-token";
  fs.writeFileSync(sessionPath, JSON.stringify(session));
  const secondStatus = await fetch(`${origin}/api/faraz/auth/status`).then((response) => response.json());
  assert.equal(secondStatus.connected, true);
  assert.deepEqual(observedTokens, ["first-test-token", "edited-test-token"]);
  assert.equal(JSON.parse(fs.readFileSync(sessionPath, "utf8")).format, "clear-text");
});

test("a rejected FARAZ session remains editable until explicit logout", async (t) => {
  const workspaceRoot = fs.mkdtempSync(path.join(os.tmpdir(), "faraz-rejected-session-"));
  t.after(() => fs.rmSync(workspaceRoot, { recursive: true, force: true }));
  const sessionPath = writeFakeSession(workspaceRoot);
  const api = createFarazCandleApi({ workspaceRoot,
    fetchImpl: async () => new Response("{}", { status: 401, headers: { "content-type": "application/json" } }) });
  const origin = await listenForApi(t, api);

  const status = await fetch(`${origin}/api/faraz/auth/status`).then((response) => response.json());
  assert.equal(status.connected, false);
  assert.equal(status.state, "expired_session");
  assert.equal(fs.existsSync(sessionPath), true);
});

test("manually edited top-level FARAZ session replaces a stale stored cookie", () => {
  const restored = normalizeClearTextSession({
    format: "clear-text",
    farazSession: "edited-test-session",
    storageState: { cookies: [{ name: "farazSession", value: "old-test-session", domain: ".faraz.io", path: "/" }], origins: [] },
  });
  assert.equal(restored.credentials.farazSession, "edited-test-session");
  assert.equal(restored.storageState.cookies[0].value, "edited-test-session");
});

test("invalid manually edited FARAZ session is preserved during an auth action", async (t) => {
  const workspaceRoot = fs.mkdtempSync(path.join(os.tmpdir(), "faraz-invalid-session-"));
  t.after(() => fs.rmSync(workspaceRoot, { recursive: true, force: true }));
  const secretDir = path.join(workspaceRoot, "runtime", "cache", "secret");
  fs.mkdirSync(secretDir, { recursive: true });
  const sessionPath = path.join(secretDir, "faraz-session.dpapi.json");
  const malformed = "{bad manual edit";
  fs.writeFileSync(sessionPath, malformed);
  const api = createFarazCandleApi({ workspaceRoot, launchBrowser: async () => { throw new Error("Browser must not launch for an invalid session."); } });
  const origin = await listenForApi(t, api);

  const response = await fetch(`${origin}/api/faraz/auth/open`, { method: "POST" });
  assert.equal(response.status, 500);
  assert.equal(fs.readFileSync(sessionPath, "utf8"), malformed);
});

test("legacy Windows DPAPI FARAZ session migrates once to editable clear text", { skip: process.platform !== "win32" }, async (t) => {
  const workspaceRoot = fs.mkdtempSync(path.join(os.tmpdir(), "faraz-legacy-session-"));
  t.after(() => fs.rmSync(workspaceRoot, { recursive: true, force: true }));
  const secretDir = path.join(workspaceRoot, "runtime", "cache", "secret");
  fs.mkdirSync(secretDir, { recursive: true });
  const sessionPath = path.join(secretDir, "faraz-session.dpapi.json");
  const legacyPayload = JSON.stringify({
    version: 2, "x-access-token": "legacy-test-token", farazSession: "",
    storageState: { cookies: [], origins: [] }, historyAuth: null,
  });
  const protectedPayload = execFileSync("powershell.exe", ["-NoProfile", "-Command",
    "Add-Type -AssemblyName System.Security;$value=[Console]::In.ReadToEnd();$bytes=[Text.Encoding]::UTF8.GetBytes($value);$protected=[Security.Cryptography.ProtectedData]::Protect($bytes,$null,[Security.Cryptography.DataProtectionScope]::CurrentUser);[Convert]::ToBase64String($protected)"],
  { input: legacyPayload, encoding: "utf8" }).trim();
  fs.writeFileSync(sessionPath, JSON.stringify({ version: 2, protection: "windows-dpapi-current-user", payload: protectedPayload }));
  const observedTokens = [];
  const api = createFarazCandleApi({ workspaceRoot, fetchImpl: async (_url, options) => {
    observedTokens.push(options.headers["x-access-token"]);
    return new Response("{}", { headers: { "content-type": "application/json" } });
  } });
  const origin = await listenForApi(t, api);

  const response = await fetch(`${origin}/api/faraz/auth/status`);
  assert.equal(response.status, 200);
  const converted = JSON.parse(fs.readFileSync(sessionPath, "utf8"));
  assert.equal(converted.format, "clear-text");
  assert.equal(converted.version, 3);
  assert.equal(converted["x-access-token"], "legacy-test-token");
  assert.ok(observedTokens.length > 0);
  assert.ok(observedTokens.every((token) => token === "legacy-test-token"));
  const migratedContents = fs.readFileSync(sessionPath, "utf8");
  await fetch(`${origin}/api/faraz/auth/status`);
  assert.equal(fs.readFileSync(sessionPath, "utf8"), migratedContents);
});

test("chart file update inserts an internal 5-second candle in chronological order", async (t) => {
  const workspaceRoot = fs.mkdtempSync(path.join(os.tmpdir(), "faraz-chart-update-"));
  t.after(() => fs.rmSync(workspaceRoot, { recursive: true, force: true }));
  const rawDir = path.join(workspaceRoot, "data", "raw");
  fs.mkdirSync(rawDir, { recursive: true });
  const fileId = buildCandleFilename("TEST:PAIR", "5S", 100, 120);
  const row = (time) => ({ time, open: 1, high: 1, low: 1, close: 1 });
  fs.writeFileSync(path.join(rawDir, fileId), JSON.stringify([row(100), row(105), row(115), row(120)]));
  const origin = await listenForApi(t, createFarazCandleApi({ workspaceRoot }));

  const response = await fetch(`${origin}/api/candle-files/update`, {
    method: "POST", headers: { "content-type": "application/json" },
    body: JSON.stringify({ id: fileId, newCandles: [row(110)], lastCandleTime: 120 }),
  });
  const result = await response.json();

  assert.equal(response.status, 200, result.error);
  assert.equal(result.added, 1);
  assert.deepEqual(JSON.parse(fs.readFileSync(path.join(rawDir, fileId), "utf8")).map(({ time }) => time), [100, 105, 110, 115, 120]);
});

test("chart file update accepts one large byte-safe append as a single atomic write", async (t) => {
  const workspaceRoot = fs.mkdtempSync(path.join(os.tmpdir(), "faraz-chart-large-update-"));
  t.after(() => fs.rmSync(workspaceRoot, { recursive: true, force: true }));
  const rawDir = path.join(workspaceRoot, "data", "raw");
  fs.mkdirSync(rawDir, { recursive: true });
  const fileId = buildCandleFilename("TEST:PAIR", "5S", 100, 100);
  const row = (time) => ({ time, open: 1.123456789, high: 1.123456789, low: 1.123456789, close: 1.123456789 });
  const newCandles = Array.from({ length: 6_000 }, (_, index) => row(105 + index * 5));
  fs.writeFileSync(path.join(rawDir, fileId), JSON.stringify([row(100)]));
  const origin = await listenForApi(t, createFarazCandleApi({ workspaceRoot }));

  const response = await fetch(`${origin}/api/candle-files/update`, {
    method: "POST", headers: { "content-type": "application/json" },
    body: JSON.stringify({ id: fileId, newCandles, lastCandleTime: newCandles.at(-1).time }),
  });
  const result = await response.json();

  assert.equal(response.status, 200, result.error);
  assert.equal(result.received, newCandles.length);
  const savedId = result.newId || fileId;
  const savedRows = JSON.parse(fs.readFileSync(path.join(rawDir, savedId), "utf8"));
  assert.equal(savedRows.length, newCandles.length + 1);
  assert.equal(savedRows.at(-1).time, newCandles.at(-1).time);
});

test("chart append carries per-file FARAZ coverage into the renamed RAW resource", async (t) => {
  const workspaceRoot = fs.mkdtempSync(path.join(os.tmpdir(), "faraz-chart-coverage-rename-"));
  t.after(() => fs.rmSync(workspaceRoot, { recursive: true, force: true }));
  const rawDir = path.join(workspaceRoot, "data", "raw");
  fs.mkdirSync(rawDir, { recursive: true });
  const fileId = buildCandleFilename("TEST:PAIR", "5S", 100, 100);
  const row = (time) => ({ time, open: 1, high: 1, low: 1, close: 1 });
  fs.writeFileSync(path.join(rawDir, fileId), JSON.stringify([row(100)]));
  const origin = await listenForApi(t, createFarazCandleApi({ workspaceRoot }));
  const post = (route, body) => fetch(`${origin}${route}`, {
    method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body),
  });
  const firstCheck = await post("/api/candle-files/verification", {
    id: fileId, timeframeSeconds: 5, ranges: [{ from: 100, to: 100, status: "complete" }],
  });
  assert.equal(firstCheck.status, 200);
  const appended = await post("/api/candle-files/update", {
    id: fileId, newCandles: [row(105)], lastCandleTime: 105,
  });
  const update = await appended.json();
  assert.equal(appended.status, 200, update.error);
  const newId = update.newId || fileId;
  const finalCheck = await post("/api/candle-files/verification", {
    id: newId, timeframeSeconds: 5, ranges: [{ from: 105, to: 105, status: "complete" }],
  });
  const metadata = await finalCheck.json();
  assert.equal(finalCheck.status, 200, metadata.error);
  assert.equal(metadata.farazCoverage.chartUpToDate, true);
  assert.deepEqual(buildChartVerificationRanges([row(100), row(105)], 5, 105, metadata.farazCoverage), []);
  assert.deepEqual(JSON.parse(fs.readFileSync(path.join(rawDir, newId), "utf8")).map(({ time }) => time), [100, 105]);
  const diskMetadata = JSON.parse(fs.readFileSync(path.join(rawDir, `${newId}.meta.json`), "utf8"));
  assert.match(diskMetadata.actualRange.from, /^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} Asia\/Tehran$/);
  assert.match(diskMetadata.actualRange.to, /^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} Asia\/Tehran$/);
  assert.match(diskMetadata.farazCoverage.ranges[0].from, /Asia\/Tehran$/);
  assert.match(diskMetadata.farazCoverage.ranges[0].to, /Asia\/Tehran$/);
  assert.equal("dataMtimeMs" in diskMetadata, false);
});

test("chart verification persists FARAZ checked coverage without changing RAW candles", async (t) => {
  const workspaceRoot = fs.mkdtempSync(path.join(os.tmpdir(), "faraz-chart-coverage-"));
  t.after(() => fs.rmSync(workspaceRoot, { recursive: true, force: true }));
  const rawDir = path.join(workspaceRoot, "data", "raw");
  fs.mkdirSync(rawDir, { recursive: true });
  const fileId = buildCandleFilename("TEST:PAIR", "5S", 100, 105);
  const rows = [100, 105].map((time) => ({ time, open: 1, high: 1, low: 1, close: 1 }));
  fs.writeFileSync(path.join(rawDir, fileId), JSON.stringify(rows));
  const origin = await listenForApi(t, createFarazCandleApi({ workspaceRoot }));

  const response = await fetch(`${origin}/api/candle-files/verification`, {
    method: "POST", headers: { "content-type": "application/json" },
    body: JSON.stringify({
      id: fileId, timeframeSeconds: 5, retryCount: 4,
      ranges: [{ from: 100, to: 105, status: "complete" }],
    }),
  });
  const result = await response.json();

  assert.equal(response.status, 200, result.error);
  assert.equal(result.farazCoverage.chartUpToDate, true);
  assert.deepEqual(result.farazCoverage.ranges.map(({ from, to, status }) => ({ from, to, status })), [
    { from: 100, to: 105, status: "complete" },
  ]);
  assert.deepEqual(JSON.parse(fs.readFileSync(path.join(rawDir, fileId), "utf8")), rows);
});

test("chart verification accepts a large set of checked gap ranges", async (t) => {
  const workspaceRoot = fs.mkdtempSync(path.join(os.tmpdir(), "faraz-chart-large-coverage-"));
  t.after(() => fs.rmSync(workspaceRoot, { recursive: true, force: true }));
  const rawDir = path.join(workspaceRoot, "data", "raw");
  fs.mkdirSync(rawDir, { recursive: true });
  const fileId = buildCandleFilename("TEST:PAIR", "5S", 100, 105);
  const rows = [100, 105].map((time) => ({ time, open: 1, high: 1, low: 1, close: 1 }));
  fs.writeFileSync(path.join(rawDir, fileId), JSON.stringify(rows));
  const origin = await listenForApi(t, createFarazCandleApi({ workspaceRoot }));
  const ranges = Array.from({ length: 2_400 }, (_, index) => ({
    from: 110 + index * 5, to: 110 + index * 5, status: "source_missing",
  }));
  const body = JSON.stringify({ id: fileId, timeframeSeconds: 5, retryCount: 4, ranges });
  assert.ok(body.length > 100_000, "coverage exceeds the generic JSON-body limit");

  const response = await fetch(`${origin}/api/candle-files/verification`, {
    method: "POST", headers: { "content-type": "application/json" }, body,
  });
  const result = await response.json();

  assert.equal(response.status, 200, result.error);
  assert.equal(result.farazCoverage.ranges.length, ranges.length);
  assert.deepEqual(result.farazCoverage.ranges.at(0)?.from, ranges[0].from);
  assert.deepEqual(result.farazCoverage.ranges.at(-1)?.to, ranges.at(-1).to);
  assert.deepEqual(JSON.parse(fs.readFileSync(path.join(rawDir, fileId), "utf8")), rows);
});

test("chart updates use 1000-candle FARAZ packets paced by at least 30ms", async (t) => {
  const workspaceRoot = fs.mkdtempSync(path.join(os.tmpdir(), "faraz-chart-transport-"));
  t.after(() => fs.rmSync(workspaceRoot, { recursive: true, force: true }));
  writeFakeSession(workspaceRoot);
  const calls = [];
  const api = createFarazCandleApi({
    workspaceRoot,
    fetchImpl: async (url) => {
      const request = new URL(url);
      if (request.pathname.endsWith("/authentication/me")) return new Response("{}", { headers: { "content-type": "application/json" } });
      calls.push({ at: Date.now(), from: Number(request.searchParams.get("from")), to: Number(request.searchParams.get("to")), countback: Number(request.searchParams.get("countback")) });
      return new Response(JSON.stringify({ s: "ok", t: [], o: [], h: [], l: [], c: [] }), {
        headers: { "content-type": "application/json" },
      });
    },
  });
  const origin = await listenForApi(t, api);

  const response = await fetch(`${origin}/api/faraz/history`, {
    method: "POST", headers: { "content-type": "application/json" },
    body: JSON.stringify({ symbolName: "TEST:PAIR", resolution: "1S", from: 100, to: 1200, packetSize: 1, rateLimitMs: 900, retryCount: 0 }),
  });
  const candles = await response.json();
  const chartPackets = calls.filter((call) => call.from >= 100 && call.to >= call.from && call.to <= 1200);

  assert.equal(response.status, 200);
  assert.equal(candles.length, 0);
  assert.equal(chartPackets.length, 2);
  assert.ok(chartPackets.every((call) => call.countback <= 1000));
  assert.ok(chartPackets[1].at - chartPackets[0].at >= 28, "FARAZ packet starts must be paced at 30ms");
});

test("chart history proxy accepts a one-candle recovery range", async (t) => {
  const workspaceRoot = fs.mkdtempSync(path.join(os.tmpdir(), "faraz-chart-history-"));
  t.after(() => fs.rmSync(workspaceRoot, { recursive: true, force: true }));
  const secretDir = path.join(workspaceRoot, "runtime", "cache", "secret");
  fs.mkdirSync(secretDir, { recursive: true });
  fs.writeFileSync(path.join(secretDir, "faraz-session.dpapi.json"), JSON.stringify({
    format: "clear-text", "x-access-token": "test-token",
  }));
  const api = createFarazCandleApi({
    workspaceRoot,
    fetchImpl: async (url) => {
      const request = new URL(url);
      if (request.pathname.endsWith("/authentication/me")) return new Response("{}", { headers: { "content-type": "application/json" } });
      const from = Number(request.searchParams.get("from"));
      const to = Number(request.searchParams.get("to"));
      const times = [from === to ? from : to];
      return new Response(JSON.stringify({ s: "ok", t: times, o: [1], h: [1], l: [1], c: [1] }), {
        headers: { "content-type": "application/json" },
      });
    },
  });
  const origin = await listenForApi(t, api);

  const response = await fetch(`${origin}/api/faraz/history`, {
    method: "POST", headers: { "content-type": "application/json" },
    body: JSON.stringify({ symbolName: "TEST:PAIR", resolution: "5S", from: 110, to: 110 }),
  });

  assert.equal(response.status, 200);
  assert.deepEqual((await response.json()).map(({ time }) => time), [110]);
});

test("chart history checks faraz.io when the session has no captured history host", async (t) => {
  const workspaceRoot = fs.mkdtempSync(path.join(os.tmpdir(), "faraz-chart-default-host-"));
  t.after(() => fs.rmSync(workspaceRoot, { recursive: true, force: true }));
  writeFakeSession(workspaceRoot);
  const hosts = [];
  const origin = await listenForApi(t, createFarazCandleApi({
    workspaceRoot,
    fetchImpl: async (url) => {
      hosts.push(new URL(url).host);
      return new Response(JSON.stringify({ s: "no_data" }), { headers: { "content-type": "application/json" } });
    },
  }));
  const response = await fetch(`${origin}/api/faraz/history`, {
    method: "POST", headers: { "content-type": "application/json" },
    body: JSON.stringify({ symbolName: "FOREXCOM:XAUUSD", resolution: "1S", from: 100, to: 110, retryCount: 0 }),
  });
  assert.equal(response.status, 200);
  assert.deepEqual(hosts, ["faraz.io"]);
});

test("chart history does not mark a historical packet missing with firstDataRequest", async (t) => {
  const workspaceRoot = fs.mkdtempSync(path.join(os.tmpdir(), "faraz-chart-first-data-"));
  t.after(() => fs.rmSync(workspaceRoot, { recursive: true, force: true }));
  writeFakeSession(workspaceRoot);
  const flags = [];
  const origin = await listenForApi(t, createFarazCandleApi({
    workspaceRoot,
    fetchImpl: async (url) => {
      const request = new URL(url);
      flags.push(request.searchParams.get("firstDataRequest"));
      return new Response(JSON.stringify(request.searchParams.get("firstDataRequest") === "true"
        ? { s: "no_data" }
        : { s: "ok", t: [100, 101], o: [1, 1], h: [1, 1], l: [1, 1], c: [1, 1] }),
      { headers: { "content-type": "application/json" } });
    },
  }));
  const response = await fetch(`${origin}/api/faraz/history`, {
    method: "POST", headers: { "content-type": "application/json" },
    body: JSON.stringify({ symbolName: "FOREXCOM:XAUUSD", resolution: "1S", from: 100, to: 101, retryCount: 0 }),
  });
  assert.equal(response.status, 200);
  assert.deepEqual((await response.json()).map(({ time }) => time), [100, 101]);
  assert.deepEqual(flags, ["false"]);
});

test("chart history proxy never retries an HTTP-200 partial candle packet", async (t) => {
  const workspaceRoot = fs.mkdtempSync(path.join(os.tmpdir(), "faraz-chart-history-gap-"));
  t.after(() => fs.rmSync(workspaceRoot, { recursive: true, force: true }));
  const secretDir = path.join(workspaceRoot, "runtime", "cache", "secret");
  fs.mkdirSync(secretDir, { recursive: true });
  fs.writeFileSync(path.join(secretDir, "faraz-session.dpapi.json"), JSON.stringify({
    format: "clear-text", "x-access-token": "test-token",
  }));
  let historyRequests = 0;
  const api = createFarazCandleApi({
    workspaceRoot,
    fetchImpl: async (url) => {
      const request = new URL(url);
      if (request.pathname.endsWith("/authentication/me")) return new Response("{}", { headers: { "content-type": "application/json" } });
      historyRequests++;
      const from = Number(request.searchParams.get("from"));
      const to = Number(request.searchParams.get("to"));
      const times = [];
      for (let time = from; time <= to; time += 5) {
        if (time !== 105) times.push(time);
      }
      return new Response(JSON.stringify({
        s: "ok", t: times, o: times.map(() => 1), h: times.map(() => 1), l: times.map(() => 1), c: times.map(() => 1),
      }), { headers: { "content-type": "application/json" } });
    },
  });
  const origin = await listenForApi(t, api);

  const response = await fetch(`${origin}/api/faraz/history`, {
    method: "POST", headers: { "content-type": "application/json" },
    body: JSON.stringify({ symbolName: "TEST:PAIR", resolution: "5S", from: 100, to: 110 }),
  });

  assert.equal(response.status, 200);
  assert.deepEqual((await response.json()).map(({ time }) => time), [100, 110]);
  assert.equal(historyRequests, 1);
});

test("chart history proxy never retries an empty HTTP-200 endpoint interval", async (t) => {
  const workspaceRoot = fs.mkdtempSync(path.join(os.tmpdir(), "faraz-chart-market-gap-"));
  t.after(() => fs.rmSync(workspaceRoot, { recursive: true, force: true }));
  const secretDir = path.join(workspaceRoot, "runtime", "cache", "secret");
  fs.mkdirSync(secretDir, { recursive: true });
  fs.writeFileSync(path.join(secretDir, "faraz-session.dpapi.json"), JSON.stringify({
    format: "clear-text", "x-access-token": "test-token",
  }));
  let historyRequests = 0;
  const api = createFarazCandleApi({
    workspaceRoot,
    fetchImpl: async (url) => {
      const request = new URL(url);
      if (request.pathname.endsWith("/authentication/me")) return new Response("{}", { headers: { "content-type": "application/json" } });
      historyRequests++;
      return new Response(JSON.stringify({ s: "no_data" }), { headers: { "content-type": "application/json" } });
    },
  });
  const origin = await listenForApi(t, api);
  const response = await fetch(`${origin}/api/faraz/history`, {
    method: "POST", headers: { "content-type": "application/json" },
    body: JSON.stringify({ symbolName: "TEST:PAIR", resolution: "5S", from: 100, to: 110 }),
  });

  assert.equal(response.status, 200);
  assert.deepEqual(await response.json(), []);
  // A successful empty source packet is authoritative, so no replay or
  // separate credential-probe request is sent for this chart update.
  assert.equal(historyRequests, 1);
});

test("chart history retries a transport failure for four total attempts then stops", async (t) => {
  const workspaceRoot = fs.mkdtempSync(path.join(os.tmpdir(), "faraz-chart-transport-failure-"));
  t.after(() => fs.rmSync(workspaceRoot, { recursive: true, force: true }));
  writeFakeSession(workspaceRoot);
  let requests = 0;
  const origin = await listenForApi(t, createFarazCandleApi({
    workspaceRoot,
    fetchImpl: async () => { requests++; throw new Error("Connection interrupted"); },
  }));
  const response = await fetch(`${origin}/api/faraz/history`, {
    method: "POST", headers: { "content-type": "application/json" },
    body: JSON.stringify({ symbolName: "TEST:PAIR", resolution: "5S", from: 100, to: 105, retryCount: 4 }),
  });
  assert.equal(response.status, 502);
  assert.match((await response.json()).error, /Connection interrupted/);
  assert.equal(requests, 4);
});

test("chart history retries invalid HTTP-200 JSON for four total attempts", async (t) => {
  const workspaceRoot = fs.mkdtempSync(path.join(os.tmpdir(), "faraz-chart-invalid-json-"));
  t.after(() => fs.rmSync(workspaceRoot, { recursive: true, force: true }));
  writeFakeSession(workspaceRoot);
  let requests = 0;
  const origin = await listenForApi(t, createFarazCandleApi({
    workspaceRoot,
    fetchImpl: async () => { requests++; return new Response("not-json", { status: 200 }); },
  }));
  const response = await fetch(`${origin}/api/faraz/history`, {
    method: "POST", headers: { "content-type": "application/json" },
    body: JSON.stringify({ symbolName: "TEST:PAIR", resolution: "5S", from: 100, to: 105 }),
  });
  assert.equal(response.status, 502);
  const error = (await response.json()).error;
  assert.match(error, /invalid JSON/i);
  assert.match(error, /4 attempts/i);
  assert.equal(requests, 4);
});

test("chart history retries a non-200 packet then saves its source-timeframe candles", async (t) => {
  const workspaceRoot = fs.mkdtempSync(path.join(os.tmpdir(), "faraz-chart-http-retry-"));
  t.after(() => fs.rmSync(workspaceRoot, { recursive: true, force: true }));
  writeFakeSession(workspaceRoot);
  let requests = 0;
  const origin = await listenForApi(t, createFarazCandleApi({
    workspaceRoot,
    fetchImpl: async () => {
      requests++;
      if (requests === 1) return new Response("unavailable", { status: 503 });
      return new Response(JSON.stringify({ s: "ok", t: [100, 105], o: [1, 1], h: [1, 1], l: [1, 1], c: [1, 1] }), {
        headers: { "content-type": "application/json" },
      });
    },
  }));
  const response = await fetch(`${origin}/api/faraz/history`, {
    method: "POST", headers: { "content-type": "application/json" },
    body: JSON.stringify({ symbolName: "TEST:PAIR", resolution: "5S", from: 100, to: 105, retryCount: 1 }),
  });
  assert.equal(response.status, 200);
  assert.deepEqual((await response.json()).map(({ time }) => time), [100, 105]);
  assert.equal(requests, 2);
});

test("FARAZ coverage detects leading, internal, and trailing missing candles", () => {
  const gaps = findCandleCoverageGaps([
    { time: 105, open: 1, high: 1, low: 1, close: 1 },
    { time: 110, open: 1, high: 1, low: 1, close: 1 },
  ], { from: 100, to: 124, timeframeSeconds: 5 });

  assert.deepEqual(gaps.map(({ from, to, missingCandles }) => ({ from, to, missingCandles })), [
    { from: 100, to: 100, missingCandles: 1 },
    { from: 115, to: 120, missingCandles: 2 },
  ]);
});

test("FARAZ coverage recovery replays each missing interval with surrounding candles", () => {
  const chunks = buildCoverageRecoveryChunks([
    { from: 100, to: 110, missingCandles: 3 },
  ], { from: 100, to: 124, timeframeSeconds: 5, startIndex: 9 });

  assert.deepEqual(chunks, [{
    index: 9,
    from: 100,
    to: 115,
    countback: 4,
    firstDataRequest: false,
    latest: false,
    recovery: true,
  }]);
});

test("FARAZ coverage recovery coalesces scattered gaps into bounded packet windows", () => {
  const chunks = buildCoverageRecoveryChunks([
    { from: 105, to: 105, missingCandles: 1 },
    { from: 115, to: 115, missingCandles: 1 },
    { from: 135, to: 135, missingCandles: 1 },
  ], { from: 100, to: 140, timeframeSeconds: 5, packetSize: 5, startIndex: 20 });

  assert.deepEqual(chunks, [
    {
      index: 20,
      from: 100,
      to: 120,
      countback: 5,
      firstDataRequest: false,
      latest: false,
      recovery: true,
    },
    {
      index: 21,
      from: 130,
      to: 140,
      countback: 3,
      firstDataRequest: false,
      latest: false,
      recovery: true,
    },
  ]);
});

test("FARAZ exporter replays a successful response that starts after the requested range", async (t) => {
  const workspaceRoot = fs.mkdtempSync(path.join(os.tmpdir(), "faraz-exporter-"));
  t.after(() => fs.rmSync(workspaceRoot, { recursive: true, force: true }));
  const secretDir = path.join(workspaceRoot, "runtime", "cache", "secret");
  fs.mkdirSync(secretDir, { recursive: true });
  fs.writeFileSync(path.join(secretDir, "faraz-session.dpapi.json"), JSON.stringify({
    format: "clear-text", "x-access-token": "test-token",
  }));

  const candlePayload = (times) => ({
    s: "ok", t: times, o: times.map(() => 1), h: times.map(() => 1), l: times.map(() => 1), c: times.map(() => 1),
  });
  const api = createFarazCandleApi({
    workspaceRoot,
    fetchImpl: async (url) => {
      const request = new URL(url);
      if (request.pathname.endsWith("/authentication/me")) return new Response("{}", { headers: { "content-type": "application/json" } });
      const from = Number(request.searchParams.get("from"));
      const to = Number(request.searchParams.get("to"));
      const firstDataRequest = request.searchParams.get("firstDataRequest") === "true";
      const times = [];
      for (let time = from; time <= to; time += 5) times.push(time);
      return new Response(JSON.stringify(candlePayload(firstDataRequest ? times.filter((time) => time !== 100) : times)), {
        headers: { "content-type": "application/json" },
      });
    },
  });
  const routes = new Map();
  api.configureServer({ middlewares: { use(route, handler) { routes.set(route, handler); } } });
  const server = http.createServer((req, res) => {
    const route = new URL(req.url, "http://localhost").pathname;
    const handler = routes.get(route);
    if (handler) return handler(req, res);
    res.statusCode = 404;
    res.end();
  });
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  t.after(() => server.close());
  const origin = `http://127.0.0.1:${server.address().port}`;
  const started = await fetch(`${origin}/api/faraz/candles/start`, {
    method: "POST", headers: { "content-type": "application/json" },
    body: JSON.stringify({ mode: "range", symbolName: "TEST:PAIR", resolution: "5S", from: 100, to: 120, packetSize: 10, rateLimitMs: 30 }),
  }).then((response) => response.json());
  let job = started;
  for (let attempt = 0; job.running && attempt < 100; attempt++) {
    await new Promise((resolve) => setTimeout(resolve, 20));
    job = await fetch(`${origin}/api/faraz/candles/status?id=${encodeURIComponent(started.id)}`).then((response) => response.json());
  }

  assert.equal(job.done, true);
  assert.equal(job.coverageComplete, true);
  assert.equal(job.suspiciousGaps[0].status, "recovered");
  const rows = JSON.parse(fs.readFileSync(path.join(workspaceRoot, job.savedPath), "utf8"));
  assert.deepEqual(rows.map((row) => row.time), [100, 105, 110, 115, 120]);
});

test("FARAZ does not publish an incomplete range until the user continues from the first available candle", async (t) => {
  const workspaceRoot = fs.mkdtempSync(path.join(os.tmpdir(), "faraz-exporter-decision-"));
  t.after(() => fs.rmSync(workspaceRoot, { recursive: true, force: true }));
  const secretDir = path.join(workspaceRoot, "runtime", "cache", "secret");
  fs.mkdirSync(secretDir, { recursive: true });
  fs.writeFileSync(path.join(secretDir, "faraz-session.dpapi.json"), JSON.stringify({
    format: "clear-text", "x-access-token": "test-token",
  }));

  let historyRequests = 0;
  const api = createFarazCandleApi({
    workspaceRoot,
    fetchImpl: async (url) => {
      const request = new URL(url);
      if (request.pathname.endsWith("/authentication/me")) return new Response("{}", { headers: { "content-type": "application/json" } });
      if (request.pathname.endsWith("/trading-view/history") && Number(request.searchParams.get("to")) <= 120) historyRequests++;
      const from = Number(request.searchParams.get("from"));
      const to = Number(request.searchParams.get("to"));
      const times = [];
      for (let time = from; time <= to; time += 5) if (time !== 100) times.push(time);
      return new Response(JSON.stringify({ s: "ok", t: times, o: times.map(() => 1), h: times.map(() => 1), l: times.map(() => 1), c: times.map(() => 1) }), {
        headers: { "content-type": "application/json" },
      });
    },
  });
  const routes = new Map();
  api.configureServer({ middlewares: { use(route, handler) { routes.set(route, handler); } } });
  const server = http.createServer((req, res) => {
    const handler = routes.get(new URL(req.url, "http://localhost").pathname);
    if (handler) return handler(req, res);
    res.statusCode = 404;
    res.end();
  });
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  t.after(() => server.close());
  const origin = `http://127.0.0.1:${server.address().port}`;
  const started = await fetch(`${origin}/api/faraz/candles/start`, {
    method: "POST", headers: { "content-type": "application/json" },
    body: JSON.stringify({ mode: "range", symbolName: "TEST:PAIR", resolution: "5S", from: 100, to: 120, packetSize: 10, rateLimitMs: 30 }),
  }).then((response) => response.json());
  let job = started;
  for (let attempt = 0; job.running && attempt < 100; attempt++) {
    await new Promise((resolve) => setTimeout(resolve, 20));
    job = await fetch(`${origin}/api/faraz/candles/status?id=${encodeURIComponent(started.id)}`).then((response) => response.json());
  }

  assert.equal(job.done, false);
  assert.equal(job.awaitingCoverageDecision, true);
  assert.equal(job.continueFrom, 105);
  assert.equal(job.savedPath, undefined);
  assert.equal(historyRequests, 2, "one primary request and one no-progress coverage replay");

  const continued = await fetch(`${origin}/api/faraz/candles/coverage-decision`, {
    method: "POST", headers: { "content-type": "application/json" },
    body: JSON.stringify({ id: started.id, decision: "continue_from_available" }),
  }).then((response) => response.json());
  assert.equal(continued.done, true);
  assert.equal(continued.effectiveRequestedFrom, 105);
  const rows = JSON.parse(fs.readFileSync(path.join(workspaceRoot, continued.savedPath), "utf8"));
  assert.deepEqual(rows.map((row) => row.time), [105, 110, 115, 120]);
});

test("FARAZ exporter snaps a manual range inward to complete timeframe slots", async (t) => {
  const workspaceRoot = fs.mkdtempSync(path.join(os.tmpdir(), "faraz-exporter-snap-"));
  t.after(() => fs.rmSync(workspaceRoot, { recursive: true, force: true }));
  writeFakeSession(workspaceRoot);
  const api = createFarazCandleApi({
    workspaceRoot,
    fetchImpl: async (url) => {
      const request = new URL(url);
      if (request.pathname.endsWith("/authentication/me")) return new Response("{}", { headers: { "content-type": "application/json" } });
      const from = Number(request.searchParams.get("from"));
      const to = Number(request.searchParams.get("to"));
      const times = [];
      for (let time = from; time <= to; time += 5) times.push(time);
      return new Response(JSON.stringify({ s: "ok", t: times, o: times.map(() => 1), h: times.map(() => 1), l: times.map(() => 1), c: times.map(() => 1) }), { headers: { "content-type": "application/json" } });
    },
  });
  const origin = await listenForApi(t, api);
  const started = await fetch(`${origin}/api/faraz/candles/start`, {
    method: "POST", headers: { "content-type": "application/json" },
    body: JSON.stringify({ mode: "range", symbolName: "TEST:PAIR", resolution: "5S", from: 102, to: 119, packetSize: 10, rateLimitMs: 30 }),
  }).then((response) => response.json());
  let job = started;
  for (let attempt = 0; job.running && attempt < 100; attempt++) {
    await new Promise((resolve) => setTimeout(resolve, 20));
    job = await fetch(`${origin}/api/faraz/candles/status?id=${encodeURIComponent(started.id)}`).then((response) => response.json());
  }
  assert.equal(job.done, true, job.error);
  assert.equal(job.originalRequestedFrom, 102);
  assert.equal(job.originalRequestedTo, 119);
  assert.equal(job.requestedFrom, 105);
  assert.equal(job.requestedTo, 115);
  assert.deepEqual(JSON.parse(fs.readFileSync(path.join(workspaceRoot, job.savedPath), "utf8")).map((row) => row.time), [105, 110, 115]);
});
