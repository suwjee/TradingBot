import test from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, mkdirSync, rmSync, writeFileSync, existsSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { buildCandleFilename, createFarazCandleApi, mergeCandles, normalizeClearTextSession, normalizeHistoryPayload, parseResolutionToSeconds, verifySavedCandles } from "../plugins/faraz-candle-api.js";

test("FARAZ resolution parser accepts extension-compatible values", () => {
  assert.equal(parseResolutionToSeconds("1S"), 1);
  assert.equal(parseResolutionToSeconds("30s"), 30);
  assert.equal(parseResolutionToSeconds("15M"), 900);
  assert.equal(parseResolutionToSeconds("4H"), 14_400);
  assert.equal(parseResolutionToSeconds("60"), 60);
  assert.throws(() => parseResolutionToSeconds("tick"), /Timeframe/);
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

test("status and logout do not launch a browser, and logout removes the clear-text session", async () => {
  const workspaceRoot = mkdtempSync(join(tmpdir(), "faraz-session-"));
  const secretDir = join(workspaceRoot, "primary-cache", "secret");
  const secretPath = join(secretDir, "faraz-session.dpapi.json");
  mkdirSync(secretDir, { recursive: true });
  writeFileSync(secretPath, JSON.stringify({ version: 2, format: "clear-text", "x-access-token": "manual-token", farazSession: "manual-cookie" }));
  const routes = new Map();
  let browserLaunches = 0;
  createFarazCandleApi({ workspaceRoot, launchBrowser: async () => { browserLaunches++; throw new Error("Browser launch is not allowed for status or logout."); } })
    .configureServer({ middlewares: { use(route, handler) { routes.set(route, handler); } } });
  const call = async (route, method = "GET") => {
    const response = { headers: {}, setHeader(name, value) { this.headers[name] = value; }, end(body) { this.body = JSON.parse(body); } };
    await routes.get(route)({ method, url: "" }, response);
    return response.body;
  };
  assert.equal((await call("/api/faraz/auth/status")).connected, true);
  assert.equal(browserLaunches, 0);
  assert.equal((await call("/api/faraz/auth/logout", "POST")).ok, true);
  assert.equal(existsSync(secretPath), false);
  assert.equal((await call("/api/faraz/auth/status")).connected, false);
  assert.equal(browserLaunches, 0);
  rmSync(workspaceRoot, { recursive: true, force: true });
});
