import test from "node:test";
import assert from "node:assert/strict";
import { existsSync, mkdtempSync, mkdirSync, readFileSync, readdirSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { EventEmitter } from "node:events";
import { Readable } from "node:stream";
import { buildCandleFilename, createFarazCandleApi, mergeCandles, normalizeClearTextSession, normalizeHistoryPayload, normalizeHistoryPayloadDetails, parseResolutionToSeconds, verifySavedCandles } from "../plugins/faraz-candle-api.js";

test("FARAZ resolution parser accepts extension-compatible values", () => {
  assert.equal(parseResolutionToSeconds("1S"), 1);
  assert.equal(parseResolutionToSeconds("30s"), 30);
  assert.equal(parseResolutionToSeconds("15M"), 900);
  assert.equal(parseResolutionToSeconds("4H"), 14_400);
  assert.equal(parseResolutionToSeconds("60"), 60);
  assert.throws(() => parseResolutionToSeconds("tick"), /Timeframe/);
});

test("chart update accepts a large candle batch, appends it, and renames the RAW file", async () => {
  const workspaceRoot = mkdtempSync(join(tmpdir(), "faraz-chart-update-"));
  const rawDir = join(workspaceRoot, "market-data", "raw");
  mkdirSync(rawDir, { recursive: true });
  const start = 1_780_000_000;
  const existing = Array.from({ length: 2 }, (_, index) => ({ time: start + index, open: 10, high: 11, low: 9, close: 10 }));
  const additions = Array.from({ length: 3_000 }, (_, index) => {
    const value = 10 + (index % 10) / 100;
    return { time: start + 2 + index, open: value, high: value + 1, low: value - 1, close: value };
  });
  const oldId = "RAW TEST_SYMBOL 1S FROM 2026-09-04 00-00-00 TO 2026-09-04 00-00-01.json";
  writeFileSync(join(rawDir, oldId), JSON.stringify(existing));
  const routes = new Map();
  createFarazCandleApi({ workspaceRoot }).configureServer({ middlewares: { use(route, handler) { routes.set(route, handler); } } });
  const request = Readable.from([JSON.stringify({ id: oldId, newCandles: additions, lastCandleTime: additions.at(-1).time })]);
  request.method = "POST";
  request.url = "";
  const response = { headers: {}, setHeader(name, value) { this.headers[name] = value; }, end(body) { this.body = JSON.parse(body); } };
  await routes.get("/api/candle-files/update")(request, response);
  assert.equal(response.body.ok, true, JSON.stringify(response.body));
  assert.equal(response.body.added, additions.length);
  assert.equal(readdirSync(rawDir).length, 1);
  const newId = response.body.newId;
  assert.match(newId, /TO \d{4}-\d{2}-\d{2} \d{2}-\d{2}-\d{2}\.json$/);
  assert.equal(JSON.parse(readFileSync(join(rawDir, newId), "utf8")).length, existing.length + additions.length);
  rmSync(workspaceRoot, { recursive: true, force: true });
});

test("history payload normalization keeps only finite OHLC-valid candles", () => {
  const candles = normalizeHistoryPayload({ result: {
    t: [100, 101, 102],
    o: [10, 10, 10],
    h: [12, 9, 12],
    l: [9, 8, 11],
    c: [11, 8.5, 10],
  } });
  assert.deepEqual(candles, [{ time: 100, open: 10, high: 12, low: 9, close: 11 }]);
  assert.deepEqual(normalizeHistoryPayload({ result: { t: [], o: [], h: [], l: [], c: [] } }), []);
  assert.equal(normalizeHistoryPayloadDetails({ result: { t: [100, 101], o: [10], h: [12], l: [9], c: [11] } }).rejectedRows, 1);
  assert.throws(() => normalizeHistoryPayloadDetails({ result: { unexpected: true } }), /candle arrays/);
});

test("merge is chronological, range-bounded, unique, and reports conflicts", () => {
  const a = { time: 101, open: 2, high: 3, low: 1, close: 2.5 };
  const duplicate = { ...a };
  const conflict = { ...a, close: 2.4 };
  const before = { time: 99, open: 1, high: 1, low: 1, close: 1 };
  const after = { time: 103, open: 4, high: 4, low: 4, close: 4 };
  const merged = mergeCandles([[after, a], [before, duplicate, conflict]], 100, 103);
  assert.deepEqual(merged.candles, [a, after]);
  assert.equal(merged.duplicates, 2);
  assert.equal(merged.conflicts, 1);
});

test("raw candle filename matches inventory format and is valid on Windows", () => {
  const first = Date.parse("2026-08-18T00:35:01Z") / 1000;
  const last = Date.parse("2026-09-01T20:59:31Z") / 1000;
  const filename = buildCandleFilename("FOREXCOM:XAUUSD", "1s", first, last);
  assert.equal(filename, "RAW FOREXCOM_XAUUSD 1S FROM 2026-08-18 04-05-01 TO 2026-09-02 00-29-31.json");
  assert.doesNotMatch(filename, /[:*?"<>|]/);
});

test("saved RAW checker validates chronological OHLC rows, requested bounds, Tehran dates, and timeframe", () => {
  const rows = [
    { time: 1_788_213_600, open: 10, high: 12, low: 9, close: 11 },
    { time: 1_788_213_630, open: 11, high: 13, low: 10, close: 12 },
  ];
  const result = verifySavedCandles(rows, { from: rows[0].time, to: rows.at(-1).time, timeframeSeconds: 30 });
  assert.equal(result.valid, true);
  assert.equal(result.checks.every((check) => check.passed), true);
  assert.match(result.checks.find((check) => check.key === "firstLast").detail, /Tehran/);
  assert.equal(verifySavedCandles([...rows].reverse(), { from: rows[0].time, to: rows.at(-1).time, timeframeSeconds: 30 }).checks.find((check) => check.key === "chronology").passed, false);
  assert.equal(verifySavedCandles(rows, { from: rows[0].time, to: rows.at(-1).time, timeframeSeconds: 60 }).checks.find((check) => check.key === "timeframe").passed, false);
});

test("clear-text FARAZ session accepts manually supplied token and cookie", () => {
  const session = normalizeClearTextSession({
    version: 2,
    "x-access-token": "eyJheader.payload.signature",
    farazSession: "s%3Amanually-editable.cookie",
    historyAuth: { host: "faraz.io", endpoint: "https://faraz.io/api/customer/trading-view/history" },
  });
  assert.equal(session.credentials.xAccessToken, "eyJheader.payload.signature");
  assert.equal(session.credentials.farazSession, "s%3Amanually-editable.cookie");
  assert.equal(session.storageState.cookies[0].name, "farazSession");
  assert.equal(session.historyAuth.host, "faraz.io");
  assert.equal(normalizeClearTextSession({ version: 2 }), null);
});

test("status validates without a browser, migrates clear text to DPAPI, and logout removes the session", async () => {
  const workspaceRoot = mkdtempSync(join(tmpdir(), "faraz-session-"));
  const secretDir = join(workspaceRoot, "primary-cache", "secret");
  const secretPath = join(secretDir, "faraz-session.dpapi.json");
  mkdirSync(secretDir, { recursive: true });
  writeFileSync(secretPath, JSON.stringify({ version: 2, format: "clear-text", "x-access-token": "manual-token", farazSession: "manual-cookie" }));
  const routes = new Map();
  let browserLaunches = 0;
  const fetchImpl = async (input) => {
    const url = new URL(input);
    if (url.pathname === "/api/public/authentication/me") {
      return {
        ok: true,
        status: 200,
        headers: { get: () => "application/json" },
        text: async () => JSON.stringify({ _id: "user-example-42", name: "Example User", phone: "+10000000000", token: "must-not-leak" }),
      };
    }
    return { ok: true, status: 200, headers: { get: () => "application/json" } };
  };
  createFarazCandleApi({ workspaceRoot, fetchImpl, launchBrowser: async () => { browserLaunches++; throw new Error("Browser launch is not allowed for status or logout."); } })
    .configureServer({ middlewares: { use(route, handler) { routes.set(route, handler); } } });
  const call = async (route, method = "GET") => {
    const response = { headers: {}, setHeader(name, value) { this.headers[name] = value; }, end(body) { this.body = JSON.parse(body); } };
    await routes.get(route)({ method, url: "" }, response);
    return response.body;
  };
  const status = await call("/api/faraz/auth/status");
  assert.equal(status.connected, true);
  assert.equal(status.userId, "user-example-42");
  assert.equal(status.userName, "Example User");
  assert.equal(status.phone, "+10000000000");
  assert.equal(Object.hasOwn(status, "token"), false);
  assert.equal(browserLaunches, 0);
  const migrated = JSON.parse(readFileSync(secretPath, "utf8"));
  assert.equal(migrated.protection, "windows-dpapi-current-user");
  assert.equal(typeof migrated.payload, "string");
  assert.equal(Object.hasOwn(migrated, "farazSession"), false);
  assert.equal((await call("/api/faraz/auth/logout", "POST")).ok, true);
  assert.equal(existsSync(secretPath), false);
  assert.equal((await call("/api/faraz/auth/status")).connected, false);
  assert.equal(browserLaunches, 0);
  rmSync(workspaceRoot, { recursive: true, force: true });
});

test("a successful interactive capture closes and kills its one owned browser server", async () => {
  const workspaceRoot = mkdtempSync(join(tmpdir(), "faraz-browser-lifecycle-"));
  const routes = new Map();
  const page = new EventEmitter();
  page.url = () => "https://faraz.io/account/login";
  page.isClosed = () => false;
  page.goto = async () => {};
  page.bringToFront = async () => {};
  page.evaluate = async () => ({ status: 200, ok: true, contentType: "application/json", redirectedToLogin: false });
  const context = new EventEmitter();
  context.pages = () => [page];
  context.cookies = async () => [{ name: "farazSession", value: "cookie", domain: ".faraz.io", path: "/", expires: -1 }];
  context.storageState = async () => ({ cookies: [{ name: "farazSession", value: "cookie", domain: ".faraz.io", path: "/", expires: -1 }], origins: [] });
  context.setExtraHTTPHeaders = async () => {};
  const browser = new EventEmitter();
  let connected = true, browserCloses = 0, serverCloses = 0, serverKills = 0, launches = 0;
  browser.isConnected = () => connected;
  browser.close = async () => { connected = false; browserCloses++; };
  const browserServer = { close: async () => { serverCloses++; }, kill: async () => { serverKills++; } };
  const fetchImpl = async () => ({ ok: true, status: 200, headers: { get: () => "application/json" } });
  createFarazCandleApi({ workspaceRoot, fetchImpl, launchBrowser: async () => { launches++; return { browser, context, browserServer }; } })
    .configureServer({ middlewares: { use(route, handler) { routes.set(route, handler); } } });
  const call = async (route, method = "GET") => {
    const response = { setHeader() {}, end(body) { this.body = JSON.parse(body); } };
    await routes.get(route)({ method, url: "" }, response);
    return response.body;
  };
  assert.equal((await call("/api/faraz/auth/open", "POST")).ok, true);
  assert.equal(launches, 1);
  assert.equal((await call("/api/faraz/auth/status")).connected, true);
  assert.equal(browserCloses, 1);
  assert.equal(serverCloses, 1);
  assert.equal(serverKills, 1);
  const savedEnvelope = JSON.parse(readFileSync(join(workspaceRoot, "primary-cache", "secret", "faraz-session.dpapi.json"), "utf8"));
  assert.equal(savedEnvelope.protection, "windows-dpapi-current-user");
  assert.equal((await call("/api/faraz/auth/status")).connected, true);
  assert.equal(launches, 1);
  rmSync(workspaceRoot, { recursive: true, force: true });
});

test("range extraction validates primary packets before atomic publication", async () => {
  const workspaceRoot = mkdtempSync(join(tmpdir(), "faraz-complete-range-"));
  const secretDir = join(workspaceRoot, "primary-cache", "secret");
  mkdirSync(secretDir, { recursive: true });
  writeFileSync(join(secretDir, "faraz-session.dpapi.json"), JSON.stringify({ version: 2, format: "clear-text", "x-access-token": "token", farazSession: "cookie" }));
  const candles = [
    { time: 1_788_213_600, open: 10, high: 12, low: 9, close: 11 },
    { time: 1_788_213_630, open: 11, high: 13, low: 10, close: 12 },
    { time: 1_788_213_660, open: 12, high: 14, low: 11, close: 13 },
    { time: 1_788_213_690, open: 13, high: 15, low: 12, close: 14 },
  ];
  let historyRequests = 0;
  const fetchImpl = async (input) => {
    historyRequests++;
    const url = new URL(input);
    const from = Number(url.searchParams.get("from")), to = Number(url.searchParams.get("to"));
    const rows = candles.filter((candle) => candle.time >= from && candle.time <= to);
    const result = rows.length ? {
      t: rows.map((row) => row.time), o: rows.map((row) => row.open), h: rows.map((row) => row.high),
      l: rows.map((row) => row.low), c: rows.map((row) => row.close),
    } : { s: "no_data" };
    return { ok: true, status: 200, headers: { get: () => "application/json" }, text: async () => JSON.stringify({ result }) };
  };
  const routes = new Map();
  createFarazCandleApi({ workspaceRoot, fetchImpl }).configureServer({ middlewares: { use(route, handler) { routes.set(route, handler); } } });
  const call = async (route, { method = "GET", url = "", body = null } = {}) => {
    const request = body == null ? new EventEmitter() : Readable.from([JSON.stringify(body)]);
    request.method = method; request.url = url;
    const response = { setHeader() {}, end(value) { this.body = JSON.parse(value); } };
    await routes.get(route)(request, response);
    return response.body;
  };
  const started = await call("/api/faraz/candles/start", { method: "POST", body: {
    mode: "range", symbolName: "FOREXCOM:XAUUSD", resolution: "30S", from: candles[0].time,
    to: candles.at(-1).time, packetSize: 2, rateLimitMs: 30, host: "faraz.io",
  } });
  let job;
  for (let attempt = 0; attempt < 100; attempt++) {
    job = await call("/api/faraz/candles/status", { url: `?id=${started.id}` });
    if (!job.running) break;
    await new Promise((resolve) => setTimeout(resolve, 20));
  }
  assert.equal(job.done, true, job.error);
  assert.ok(Number.isFinite(job.receivedRows) && job.receivedRows >= candles.length, "primary received rows are counted without NaN");
  assert.equal(job.candleCountResult, candles.length);
  assert.equal(job.validation.every((check) => check.passed), true);
  assert.ok(historyRequests >= 3, "status probe and primary packets must both run");
  const savedFiles = readdirSync(join(workspaceRoot, "market-data", "raw")).filter((name) => name.endsWith(".json"));
  assert.equal(savedFiles.length, 1);
  assert.deepEqual(JSON.parse(readFileSync(join(workspaceRoot, "market-data", "raw", savedFiles[0]), "utf8")), candles);
  rmSync(workspaceRoot, { recursive: true, force: true });
});

test("a HTTP-200 primary omission is retained without a second replay", async () => {
  const workspaceRoot = mkdtempSync(join(tmpdir(), "faraz-shifted-recovery-"));
  const secretDir = join(workspaceRoot, "primary-cache", "secret");
  mkdirSync(secretDir, { recursive: true });
  writeFileSync(join(secretDir, "faraz-session.dpapi.json"), JSON.stringify({ version: 2, format: "clear-text", "x-access-token": "token", farazSession: "cookie" }));
  const candles = [100, 130, 160, 190].map((time, index) => ({ time, open: 10 + index, high: 12 + index, low: 9 + index, close: 11 + index }));
  const fetchImpl = async (input) => {
    const url = new URL(input);
    const from = Number(url.searchParams.get("from")), to = Number(url.searchParams.get("to"));
    // Reproduce a valid HTTP-200 primary response with no rows for its first
    // interval.  The exporter must not create or fetch data a second time.
    const rows = from === 100 ? [] : candles.filter((candle) => candle.time >= from && candle.time <= to);
    const result = rows.length ? {
      t: rows.map((row) => row.time), o: rows.map((row) => row.open), h: rows.map((row) => row.high),
      l: rows.map((row) => row.low), c: rows.map((row) => row.close),
    } : { s: "no_data" };
    return { ok: true, status: 200, headers: { get: () => "application/json" }, text: async () => JSON.stringify({ result }) };
  };
  const routes = new Map();
  createFarazCandleApi({ workspaceRoot, fetchImpl }).configureServer({ middlewares: { use(route, handler) { routes.set(route, handler); } } });
  const call = async (route, { method = "GET", url = "", body = null } = {}) => {
    const request = body == null ? new EventEmitter() : Readable.from([JSON.stringify(body)]);
    request.method = method; request.url = url;
    const response = { setHeader() {}, end(value) { this.body = JSON.parse(value); } };
    await routes.get(route)(request, response);
    return response.body;
  };
  const started = await call("/api/faraz/candles/start", { method: "POST", body: {
    mode: "range", symbolName: "FOREXCOM:XAUUSD", resolution: "30S", from: 100, to: 190,
    packetSize: 2, rateLimitMs: 30, host: "faraz.io",
  } });
  let job;
  for (let attempt = 0; attempt < 100; attempt++) {
    job = await call("/api/faraz/candles/status", { url: `?id=${started.id}` });
    if (!job.running) break;
    await new Promise((resolve) => setTimeout(resolve, 20));
  }
  assert.equal(job.done, true, job.error);
  assert.equal(job.candleCountResult, 2);
  assert.match(job.logs.map((entry) => entry.message).join("\n"), /No second HTTP-200 replay was sent/);
  const savedFiles = readdirSync(join(workspaceRoot, "market-data", "raw")).filter((name) => name.endsWith(".json"));
  assert.equal(savedFiles.length, 1);
  assert.deepEqual(JSON.parse(readFileSync(join(workspaceRoot, "market-data", "raw", savedFiles[0]), "utf8")), candles.slice(2));
  rmSync(workspaceRoot, { recursive: true, force: true });
});

test("a persistent HTTP-200 suspicious gap is recorded without retry and does not fail extraction", async () => {
  const workspaceRoot = mkdtempSync(join(tmpdir(), "faraz-retained-gap-"));
  const secretDir = join(workspaceRoot, "primary-cache", "secret");
  mkdirSync(secretDir, { recursive: true });
  writeFileSync(join(secretDir, "faraz-session.dpapi.json"), JSON.stringify({ version: 2, format: "clear-text", "x-access-token": "token", farazSession: "cookie" }));
  // FARAZ never has the 160-second candle: this must remain a reported gap,
  // rather than converting a successfully validated export into an error.
  const candles = [100, 130, 190].map((time, index) => ({ time, open: 10 + index, high: 12 + index, low: 9 + index, close: 11 + index }));
  let historyRequests = 0;
  const fetchImpl = async (input) => {
    historyRequests++;
    const url = new URL(input);
    const from = Number(url.searchParams.get("from")), to = Number(url.searchParams.get("to"));
    const rows = candles.filter((candle) => candle.time >= from && candle.time <= to);
    const result = rows.length ? {
      t: rows.map((row) => row.time), o: rows.map((row) => row.open), h: rows.map((row) => row.high),
      l: rows.map((row) => row.low), c: rows.map((row) => row.close),
    } : { s: "no_data" };
    return { ok: true, status: 200, headers: { get: () => "application/json" }, text: async () => JSON.stringify({ result }) };
  };
  const routes = new Map();
  createFarazCandleApi({ workspaceRoot, fetchImpl }).configureServer({ middlewares: { use(route, handler) { routes.set(route, handler); } } });
  const call = async (route, { method = "GET", url = "", body = null } = {}) => {
    const request = body == null ? new EventEmitter() : Readable.from([JSON.stringify(body)]);
    request.method = method; request.url = url;
    const response = { setHeader() {}, end(value) { this.body = JSON.parse(value); } };
    await routes.get(route)(request, response);
    return response.body;
  };
  const started = await call("/api/faraz/candles/start", { method: "POST", body: {
    mode: "range", symbolName: "FOREXCOM:XAUUSD", resolution: "30S", from: 100, to: 190,
    packetSize: 10, rateLimitMs: 30, host: "faraz.io",
  } });
  let job;
  for (let attempt = 0; attempt < 100; attempt++) {
    job = await call("/api/faraz/candles/status", { url: `?id=${started.id}` });
    if (!job.running) break;
    await new Promise((resolve) => setTimeout(resolve, 20));
  }
  assert.equal(job.done, true, job.error);
  assert.equal(job.candleCountResult, candles.length);
  assert.deepEqual(job.suspiciousGaps.map((gap) => ({ remainingCandles: gap.remainingCandles, status: gap.status })), [{ remainingCandles: 1, status: "retained" }]);
  const messages = job.logs.map((entry) => entry.message).join("\n");
  assert.doesNotMatch(messages, /Suspicious-gap retry/);
  assert.match(messages, /retained without retry because the packet returned HTTP 200/);
  assert.ok(historyRequests >= 2, "primary collection and independent verification must both run");
  rmSync(workspaceRoot, { recursive: true, force: true });
});
