import test from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import fs from "node:fs";
import http from "node:http";
import os from "node:os";
import path from "node:path";
import { Readable } from "node:stream";

import { buildCandleFilename, buildCoverageRecoveryChunks, createFarazCandleApi as createProductionFarazCandleApi, findCandleCoverageGaps, normalizeClearTextSession } from "../../server/faraz-candle-api.js";
import { buildChartVerificationRanges } from "../../src/features/candle-update.js";
import { createRawResourceStore } from "../../server/raw-resource-store.js";

function createFarazCandleApi(options) {
  return createProductionFarazCandleApi({ ...options, localStateRoot: path.join(options.workspaceRoot, "apps", "chart", "state") });
}

async function listenForApi(t, api) {
  const routes = new Map();
  api.configureServer({ middlewares: { use(route, handler) { routes.set(route, handler); } } });
  const server = http.createServer((req, res) => {
    const handler = routes.get(new URL(req.url, "http://localhost").pathname);
    if (handler) return handler(req, res);
    res.statusCode = 404;
    res.end();
  });
  for (let attempt = 0; attempt < 20; attempt++) {
    await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
    const origin = `http://127.0.0.1:${server.address().port}`;
    try {
      await fetch(origin, { method: "HEAD" });
      t.after(() => server.close());
      return origin;
    } catch (error) {
      await new Promise((resolve) => server.close(resolve));
      if (error?.cause?.message !== "bad port") throw error;
    }
  }
  throw new Error("Unable to allocate a browser-compatible test port");
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

function deferred() {
  let resolve;
  const promise = new Promise((yes) => { resolve = yes; });
  return { promise, resolve };
}

function writeFakeSession(workspaceRoot) {
  const secretDir = path.join(path.join(workspaceRoot, "apps", "chart", "state"), "secret");
  fs.mkdirSync(secretDir, { recursive: true });
  const sessionPath = path.join(secretDir, "faraz-session.dpapi.json");
  fs.writeFileSync(sessionPath, JSON.stringify({
    format: "clear-text", "x-access-token": "test-file-token", farazSession: "test-file-cookie",
    storageState: { cookies: [{ name: "farazSession", value: "test-file-cookie", domain: ".faraz.io", path: "/", expires: -1 }], origins: [] },
    historyAuth: null,
  }));
  return sessionPath;
}

function realtimeCandle(time) {
  return { time, open: 1, high: 2, low: 1, close: 2 };
}

function historyResponse(times) {
  return Response.json({ s: "ok", t: times, o: times.map(() => 1), h: times.map(() => 2), l: times.map(() => 1), c: times.map(() => 2) });
}

async function realtimeFixture(t, fetchImpl, { nowSeconds = 120, last = 100, rows = [realtimeCandle(last)], timeframe = "5S" } = {}) {
  const workspaceRoot = fs.mkdtempSync(path.join(os.tmpdir(), "faraz-realtime-"));
  t.after(() => fs.rmSync(workspaceRoot, { recursive: true, force: true }));
  writeFakeSession(workspaceRoot);
  const rootDir = path.join(workspaceRoot, "apps", "chart", "state", "data", "raw");
  const rawStore = createRawResourceStore({ rootDir });
  const old = rawStore.write({ broker: "TEST", symbol: "PAIR", timeframe, candles: rows, source: "test" });
  const origin = await listenForApi(t, createFarazCandleApi({ workspaceRoot, rawStore, fetchImpl, now: () => nowSeconds * 1000 }));
  const post = ({ baseSha256 = old.dataSha256, file = old, lastCandleTime = file.to ?? old.actualRange.to, verifyAll = false, phase, historyPacketLimit, previousTail, ...options } = {}) => fetch(`${origin}/api/candle-files/realtime`, {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ id: file.id, chartId: file.chartId, lastCandleTime, baseSha256, verifyAll, phase, historyPacketLimit, previousTail }), ...options,
  });
  return { rawStore, old, post };
}

test("real-time catch-up publishes one renamed RAW pair with only closed native-timeframe candles", async (t) => {
  const requests = [];
  const { rawStore, old, post } = await realtimeFixture(t, async (url) => {
    requests.push(Object.fromEntries(url.searchParams));
    return historyResponse([103, 108, 113]);
  }, { nowSeconds: 113, last: 103 });
  const coverage = rawStore.recordFarazCoverage(old.id, {
    timeframeSeconds: 5, ranges: [{ from: 103, to: 103, status: "complete" }], checkedThrough: 103, mode: "gap-full",
  }).farazCoverage;

  const response = await post();
  assert.equal(response.status, 200);
  const { file, candles } = await response.json();
  assert.deepEqual(requests.map(request => [request.from, request.to]), [["108", "113"], ["108", "113"], ["103", "108"]]);
  assert.equal(requests[0].symbolName, "TEST_PAIR");
  assert.equal(requests[0].resolution, "5S");
  assert.equal(requests[0].from, "108");
  assert.equal(requests[0].to, "113");
  assert.equal(requests[0].firstDataRequest, "false");
  assert.deepEqual(candles, [realtimeCandle(108)]);
  assert.equal(file.chartId, old.chartId);
  assert.equal(file.from, 103);
  assert.equal(file.to, 108);
  assert.equal(file.count, 2);
  assert.deepEqual(file.metadata.farazCoverage, coverage);
  assert.match(file.id, /TO 1970-01-01 03-31-48\.json$/);
  assert.deepEqual(rawStore.read(file.id), [realtimeCandle(103), realtimeCandle(108)]);
  assert.equal(fs.existsSync(old.dataPath), false);
  assert.equal(fs.existsSync(old.metaPath), false);
  assert.deepEqual(rawStore.list().map(({ id }) => id), [file.id]);

  const stale = await post();
  assert.equal(stale.status, 409);
  assert.equal((await stale.json()).file.id, file.id);
  assert.equal(requests.length, 3);
});

test("recent verification rechecks the union of append windows and excludes the newest candle", async (t) => {
  const rows = Array.from({ length: 1_005 }, (_, index) => realtimeCandle(100 + index * 5));
  // The interval is selected by actual row count, even when a timeframe slot is missing.
  rows.splice(20, 1);
  const previousTail = rows.at(-1).time;
  const newest = previousTail + 10;
  const requests = [];
  let repair = false;
  const { post, rawStore } = await realtimeFixture(t, async (url) => {
    const from = Number(url.searchParams.get("from"));
    const to = Number(url.searchParams.get("to"));
    requests.push([from, to]);
    const times = rows.map(row => row.time).concat(previousTail + 5, newest)
      .filter(time => time >= from && time < to);
    const payload = await historyResponse(times).json();
    const index = times.indexOf(previousTail);
    if (repair && index >= 0) payload.h[index] = 3;
    return Response.json(payload);
  }, { rows, nowSeconds: newest + 5 });
  const initial = await post({ verifyAll: true });
  assert.equal(initial.status, 200);
  const latest = await (await post({ phase: "latest" })).json();
  assert.deepEqual(latest.candles.map(row => row.time), [previousTail + 5, newest]);
  assert.equal(latest.verification.status, "verified");
  repair = true;
  requests.length = 0;
  const response = await post({ phase: "recent", previousTail, file: latest.file, baseSha256: latest.file.metadata.dataSha256 });
  assert.equal(response.status, 200);
  const result = await response.json();
  requests.sort(([left], [right]) => left - right);
  assert.equal(requests[0][0], rows.at(-1001).time);
  assert.equal(requests.at(-1)[1], newest); // FARAZ has an exclusive upper bound.
  assert.ok(requests.every(([from, to]) => to - from <= 1_000 * 5));
  assert.equal(result.verification.checkedCount, 1_002);
  assert.deepEqual(result.corrections, [{ ...realtimeCandle(previousTail), high: 3 }]);
  assert.deepEqual(result.candles, []);
  assert.deepEqual(rawStore.read(result.file.id).at(-1), realtimeCandle(newest));
});

test("recent verification on a short file starts at its first candle and stops at the penultimate candle", async (t) => {
  const requests = [];
  const { old, post } = await realtimeFixture(t, async (url) => {
    const from = Number(url.searchParams.get("from"));
    const to = Number(url.searchParams.get("to"));
    requests.push([from, to]);
    return historyResponse([100, 105, 110].filter(time => time >= from && time < to));
  }, { rows: [realtimeCandle(100), realtimeCandle(105), realtimeCandle(110)], nowSeconds: 115 });
  const response = await post({ phase: "recent", previousTail: 105 });
  assert.equal(response.status, 200);
  assert.deepEqual(requests, [[100, 110]]);
  const result = await response.json();
  assert.equal(result.verification.checkedCount, 2);
  assert.equal(result.file.metadata.dataSha256, old.dataSha256);
  assert.equal((await post({ phase: "recent", previousTail: 110 })).status, 400);
  assert.equal((await post({ phase: "recent", previousTail: 103 })).status, 409);
  assert.deepEqual(requests, [[100, 110]]);
});

test("another tab receives the committed append from its exact RAW cursor without a new FARAZ request", async (t) => {
  let requests = 0;
  const { post, rawStore } = await realtimeFixture(t, async () => {
    requests++;
    return historyResponse([103, 108, 113, 118]);
  }, { nowSeconds: 118, last: 103 });

  const first = await post({ phase: "latest" });
  assert.equal(first.status, 200);
  const committed = await first.json();
  assert.deepEqual(committed.candles, [realtimeCandle(108), realtimeCandle(113)]);
  assert.equal(requests, 2);

  const replay = await post({ phase: "latest" });
  assert.equal(replay.status, 200);
  const caughtUp = await replay.json();
  assert.equal(caughtUp.file.id, committed.file.id);
  assert.equal(caughtUp.file.metadata.dataSha256, committed.file.metadata.dataSha256);
  assert.deepEqual(caughtUp.candles, committed.candles);
  assert.deepEqual(caughtUp.corrections, []);
  assert.deepEqual(caughtUp.gapCandles, []);
  assert.equal(caughtUp.verification.verifiedCount, committed.verification.verifiedCount);
  assert.equal(caughtUp.verification.totalCount, committed.verification.totalCount);

  const fromInventory = await post({ phase: "replay" });
  assert.equal(fromInventory.status, 200);
  assert.deepEqual(await fromInventory.json(), caughtUp);
  const alreadyCurrent = await post({ phase: "replay", file: committed.file, baseSha256: committed.file.metadata.dataSha256 });
  assert.equal(alreadyCurrent.status, 409);

  for (const cursor of [{ lastCandleTime: 108 }, { baseSha256: "0".repeat(64) }, { verifyAll: true }]) {
    const rejected = await post({ phase: "latest", ...cursor });
    assert.equal(rejected.status, 409);
    assert.equal((await rejected.json()).code, "RAW_CHANGED");
  }
  assert.equal(requests, 2);

  const current = rawStore.get(committed.file.id);
  await rawStore.appendLatest(current, [], 5, rawStore.version(current.id), new AbortController().signal,
    { corrections: [{ ...realtimeCandle(103), close: 1.5 }] });
  const afterHistoricalCorrection = await post({ phase: "replay" });
  assert.equal(afterHistoricalCorrection.status, 409);
  assert.equal((await afterHistoricalCorrection.json()).code, "RAW_CHANGED");
  assert.equal(requests, 2);
});

test("live verification repairs history, confirms newly appended OHLC with a second fetch, and supports Verify All", async (t) => {
  const requests = [];
  let latestClose = 1.5;
  const { old, rawStore, post } = await realtimeFixture(t, async (url) => {
    const from = Number(url.searchParams.get("from"));
    requests.push(from);
    if (from === 105 && requests.filter(value => value === 105).length === 1) return historyResponse([105]);
    if (from === 105) return Response.json({ s: "ok", t: [105], o: [1], h: [2], l: [1], c: [1.5] });
    return Response.json({ s: "ok", t: [95, 100, 105], o: [1, 1, 1], h: [2, 2, 2], l: [1, 1, 1], c: [2, latestClose, 1.5] });
  }, { nowSeconds: 110, rows: [realtimeCandle(95), realtimeCandle(100)] });
  const first = await post();
  assert.equal(first.status, 200);
  const result = await first.json();
  assert.equal(result.verification.status, "verified");
  assert.equal(result.verification.verifiedCount, 3);
  assert.deepEqual(result.corrections, [{ ...realtimeCandle(100), close: 1.5 }]);
  assert.equal(result.candles[0].close, 1.5);
  assert.deepEqual(requests, [105, 105, 95]);
  assert.equal(rawStore.read(result.file.id)[1].close, 1.5);
  assert.equal(result.file.chartId, old.chartId);
  assert.equal(JSON.parse(fs.readFileSync(rawStore.resolve(result.file.id).metaPath)).candleVerification.verifiedCount, 3);
  const current = { file: result.file, baseSha256: result.file.metadata.dataSha256 };
  const subsequent = await post(current);
  assert.equal((await subsequent.json()).verification.status, "verified");
  assert.deepEqual(requests, [105, 105, 95]);
  latestClose = 1.75;
  const manual = await post({ ...current, verifyAll: true });
  assert.equal(manual.status, 200);
  const checked = await manual.json();
  assert.equal(checked.file.id, result.file.id);
  assert.equal(checked.corrections[0].close, 1.75);
  assert.equal(rawStore.read(checked.file.id)[1].close, 1.75);
  assert.deepEqual(requests, [105, 105, 95, 95]);
});

test("an unavailable source leaves RAW intact and returns verification status instead of an HTTP error", async (t) => {
  const { old, post } = await realtimeFixture(t, async () => { throw new TypeError("Network offline"); });
  const before = fs.readFileSync(old.dataPath, "utf8");
  const response = await post();
  assert.equal(response.status, 200);
  const result = await response.json();
  assert.equal(result.verification.status, "unavailable");
  assert.deepEqual(result.candles, []);
  assert.equal(fs.readFileSync(old.dataPath, "utf8"), before);
});

test("Verify All fills native-timeframe gaps across packet boundaries and leaves missing source slots alone", async (t) => {
  const requests = [];
  const confirmedTimes = [100, 105, 5095, 5100, 5110];
  const { old, post, rawStore } = await realtimeFixture(t, async (url) => {
    const from = Number(url.searchParams.get("from"));
    const to = Number(url.searchParams.get("to"));
    requests.push([from, to]);
    assert.equal(url.searchParams.get("resolution"), "5S");
    return historyResponse(confirmedTimes.filter(time => time >= from && time < to));
  }, { nowSeconds: 5115, last: 5110, rows: [{ ...realtimeCandle(100), close: 1 }, realtimeCandle(5110)] });
  const response = await post({ verifyAll: true });
  assert.equal(response.status, 200);
  const result = await response.json();
  assert.deepEqual(requests, [[100, 5100], [5100, 5115]]);
  assert.equal(result.file.id, old.id);
  assert.equal(result.file.chartId, old.chartId);
  assert.deepEqual(result.gapCandles.map(row => row.time), [105, 5095, 5100]);
  assert.deepEqual(result.corrections, [realtimeCandle(100)]);
  assert.deepEqual(rawStore.read(old.id), confirmedTimes.map(realtimeCandle));
  assert.deepEqual(result.file.metadata.candleVerification.ranges, [[0, 4]]);
  assert.equal(result.verification.recoveredCount, 3);
  assert.equal(result.verification.correctedCount, 1);
});

test("Verify All overlaps paced packets and publishes only the verified prefix after a packet fails", async (t) => {
  const fourthStarted = deferred();
  const lastCancelled = deferred();
  const release = deferred();
  const starts = [];
  const { old, post, rawStore } = await realtimeFixture(t, async (url, { signal }) => {
    const from = Number(url.searchParams.get("from"));
    starts.push({ from, at: performance.now() });
    if (from === 100) {
      await release.promise;
      return historyResponse([100, 105]);
    }
    if (from === 5100) {
      await release.promise;
      return new Response("Unavailable", { status: 503 });
    }
    if (from === 10100) {
      return historyResponse([10100, 10105]);
    }
    if (from === 15100) {
      fourthStarted.resolve();
      try {
        if (!signal.aborted) await new Promise(resolve => signal.addEventListener("abort", resolve, { once: true }));
        signal.throwIfAborted();
      } finally { lastCancelled.resolve(); }
    }
    assert.fail("A packet beyond the bounded lookahead was started.");
  }, { nowSeconds: 20105, rows: [{ ...realtimeCandle(100), close: 1 }, realtimeCandle(20100)] });

  const pending = post({ verifyAll: true });
  const deadline = AbortSignal.timeout(1_500);
  try {
    await Promise.race([fourthStarted.promise, new Promise((_, reject) =>
      deadline.addEventListener("abort", () => reject(new Error("Verification fetched packets serially")), { once: true }))]);
  } finally {
    // Allow the baseline request to settle even when the concurrency check fails.
    release.resolve();
  }
  const response = await pending;
  assert.equal(response.status, 200);
  const result = await response.json();
  assert.deepEqual(result.verification, {
    status: "unavailable", verifiedCount: 2, totalCount: 3,
    checkedCount: 1, correctedCount: 1, recoveredCount: 1,
  });
  assert.deepEqual(result.corrections, [realtimeCandle(100)]);
  assert.deepEqual(result.gapCandles, [realtimeCandle(105)]);
  assert.deepEqual(rawStore.read(old.id), [100, 105, 20100].map(realtimeCandle));
  assert.deepEqual(result.file.metadata.candleVerification.ranges, [[0, 1]]);
  for (let index = 1; index < starts.length; index++) {
    assert.ok(starts[index].at - starts[index - 1].at >= 29, "FARAZ starts remain paced");
  }
  await lastCancelled.promise;
});

test("a polling stream reports actual work and counts repairs to both historical and new 5S candles", async (t) => {
  let latestRequests = 0;
  const { post } = await realtimeFixture(t, async (url) => {
    assert.equal(url.searchParams.get("resolution"), "5S");
    if (url.searchParams.get("from") === "105" && ++latestRequests === 1) return historyResponse([105]);
    return Response.json({ s: "ok", t: [95, 100, 105], o: [1, 1, 1], h: [2, 2, 2], l: [1, 1, 1], c: [2, 1.5, 1.5] });
  }, { nowSeconds: 110, rows: [realtimeCandle(95), realtimeCandle(100)] });
  const response = await post({ headers: { "Content-Type": "application/json", Accept: "application/x-ndjson" } });
  assert.match(response.headers.get("Content-Type"), /^application\/x-ndjson/);
  const messages = (await response.text()).trim().split("\n").map(JSON.parse);
  const progress = messages.slice(0, -1).map(message => message.progress);
  assert(progress.some(value => value > 0 && value < 100));
  assert.deepEqual(progress, progress.toSorted((left, right) => left - right));
  assert.equal(messages.at(-1).status, 200);
  assert.deepEqual(messages.at(-1).result.verification, {
    status: "verified", verifiedCount: 3, totalCount: 3, checkedCount: 3, correctedCount: 2, recoveredCount: 0,
  });
});

test("a failed confirmation leaves RAW intact so the next poll can append confirmed OHLC", async (t) => {
  let calls = 0;
  const { old, post, rawStore } = await realtimeFixture(t, async (url, options) => {
    calls++;
    assert.equal(url.searchParams.get("from"), "105");
    if (calls === 2) {
      assert.equal(options.cache, "no-store");
      throw new TypeError("Connection lost before confirmation");
    }
    if (calls === 4) return Response.json({ s: "ok", t: [105], o: [1], h: [2], l: [1], c: [1.5] });
    return historyResponse([105]);
  }, { nowSeconds: 110 });
  const first = await (await post({ phase: "latest" })).json();
  assert.equal(first.verification.status, "unavailable");
  assert.equal(first.verification.verifiedCount, 0);
  assert.equal(first.file.id, old.id);
  assert.deepEqual(first.candles, []);
  assert.deepEqual(rawStore.read(old.id), [realtimeCandle(100)]);
  const next = await (await post({ phase: "latest" })).json();
  assert.deepEqual(next.candles, [{ ...realtimeCandle(105), close: 1.5 }]);
  assert.equal(next.verification.verifiedCount, 1);
  assert.equal(next.verification.correctedCount, 1);
  assert.deepEqual(rawStore.read(next.file.id), [realtimeCandle(100), { ...realtimeCandle(105), close: 1.5 }]);
});

test("a partial confirmation appends the matching 1S prefix and retries from the first unmatched candle", async (t) => {
  const requests = [];
  const { post, rawStore } = await realtimeFixture(t, async (url) => {
    assert.equal(url.searchParams.get("resolution"), "1S");
    const from = Number(url.searchParams.get("from"));
    requests.push(from);
    const rows = requests.length === 2 ? [101, 103, 104] : [101, 102, 103, 104];
    return historyResponse(rows.filter(time => time >= from));
  }, { nowSeconds: 105, timeframe: "1S" });
  const first = await (await post({ phase: "latest" })).json();
  assert.deepEqual(first.candles, [realtimeCandle(101)]);
  assert.equal(first.verification.verifiedCount, 1);
  assert.deepEqual(rawStore.read(first.file.id).map(row => row.time), [100, 101]);

  const next = await (await post({ phase: "latest", file: first.file, baseSha256: first.file.metadata.dataSha256 })).json();
  assert.deepEqual(next.candles.map(row => row.time), [102, 103, 104]);
  assert.equal(next.verification.verifiedCount, 4);
  assert.deepEqual(requests, [101, 101, 102, 102]);
  assert.deepEqual(rawStore.read(next.file.id).map(row => row.time), [100, 101, 102, 103, 104]);
});

test("a candle found only in the fresh response keeps later candles pending", async (t) => {
  let requests = 0;
  const { old, post, rawStore } = await realtimeFixture(t, async (url) => {
    requests++;
    const from = Number(url.searchParams.get("from"));
    const times = requests === 1 ? [100] : requests === 2 ? [110] : [105, 110];
    return historyResponse(times.filter(time => time >= from));
  }, { nowSeconds: 115 });
  const prior = await (await post({ verifyAll: true })).json();
  assert.equal(prior.verification.status, "verified");
  const result = await (await post({ phase: "latest" })).json();
  assert.equal(result.verification.status, "pending");
  assert.equal(result.verification.verifiedCount, 1);
  assert.deepEqual(result.candles, []);
  assert.deepEqual(rawStore.read(old.id), [realtimeCandle(100)]);
});

test("a limited history phase verifies one packet and resumes at the next unchecked packet", async (t) => {
  const rows = Array.from({ length: 1001 }, (_, index) => realtimeCandle(100 + index));
  const requests = [];
  const { post } = await realtimeFixture(t, async (url) => {
    const from = Number(url.searchParams.get("from"));
    const to = Number(url.searchParams.get("to"));
    requests.push([from, to]);
    return historyResponse(rows.filter(row => row.time >= from && row.time < to).map(row => row.time));
  }, { nowSeconds: 1101, rows, timeframe: "1S" });
  const first = await (await post({ phase: "history", historyPacketLimit: 1 })).json();
  assert.equal(first.verification.status, "pending");
  assert.equal(first.verification.verifiedCount, 1000);
  assert.deepEqual(requests, [[100, 1100]]);

  const second = await (await post({ phase: "history", historyPacketLimit: 1 })).json();
  assert.equal(second.verification.status, "verified");
  assert.equal(second.verification.verifiedCount, 1001);
  assert.deepEqual(requests, [[100, 1100], [1100, 1101]]);

  const all = await (await post({ phase: "history", historyPacketLimit: 1, verifyAll: true })).json();
  assert.equal(all.verification.checkedCount, 1001);
  assert.deepEqual(requests.slice(2).sort(([left], [right]) => left - right), [[100, 1100], [1100, 1101]]);
});

test("history packet limits are bounded integers scoped to the history phase", async (t) => {
  const { post } = await realtimeFixture(t, async () => { assert.fail("An invalid limit must not fetch FARAZ"); });
  for (const request of [{ phase: "latest", historyPacketLimit: 1 }, { historyPacketLimit: 1 },
    { phase: "history", historyPacketLimit: 0 }, { phase: "history", historyPacketLimit: 9 }, { phase: "history", historyPacketLimit: "1" }]) {
    assert.equal((await post(request)).status, 400);
  }
});

test("history verification can publish a metadata-only update after a single RAW read", async (t) => {
  const { old, post, rawStore } = await realtimeFixture(t, async () => historyResponse([100]), { nowSeconds: 105 });
  assert.equal(rawStore.get(old.id).metadata.dataSha256, old.dataSha256);
  const readFileSync = fs.readFileSync;
  const readFile = fs.promises.readFile;
  let rawReads = 0;
  t.mock.method(fs, "readFileSync", (target, ...args) => {
    if (target === old.dataPath) rawReads++;
    return readFileSync(target, ...args);
  });
  t.mock.method(fs.promises, "readFile", (target, ...args) => {
    if (target === old.dataPath) rawReads++;
    return readFile(target, ...args);
  });

  const result = await (await post({ phase: "history" })).json();
  assert.equal(result.verification.status, "verified");
  assert.equal(rawStore.get(old.id).metadata.candleVerification.verifiedCount, 1);
  assert.equal(rawStore.get(old.id).metadata.dataSha256, old.dataSha256);
  assert.equal(rawReads, 1);
});

test("metadata-only verification rejects a RAW change while staging its sidecar", async (t) => {
  const { old, post, rawStore } = await realtimeFixture(t, async () => historyResponse([100]), { nowSeconds: 105 });
  const originalSidecar = fs.readFileSync(old.metaPath, "utf8");
  const writeFile = fs.promises.writeFile;
  const revised = { ...realtimeCandle(100), close: 1 };
  t.mock.method(fs.promises, "writeFile", async (target, ...args) => {
    await writeFile(target, ...args);
    if (target.endsWith(".meta.tmp")) fs.writeFileSync(old.dataPath, JSON.stringify([revised]));
  });

  const response = await post({ phase: "history" });
  assert.equal(response.status, 409);
  assert.equal((await response.json()).code, "RAW_CHANGED");
  assert.equal(fs.readFileSync(old.metaPath, "utf8"), originalSidecar);
  assert.deepEqual(rawStore.read(old.id), [revised]);
});

test("a missing FARAZ row stays pending and never deletes a stored candle", async (t) => {
  let complete = false;
  const { old, post, rawStore } = await realtimeFixture(t, async () => historyResponse(complete ? [95, 100] : [100]),
    { nowSeconds: 105, rows: [realtimeCandle(95), realtimeCandle(100)] });
  const first = await (await post()).json();
  assert.equal(first.verification.status, "pending");
  assert.equal(first.verification.verifiedCount, 1);
  assert.deepEqual(rawStore.read(old.id), [realtimeCandle(95), realtimeCandle(100)]);
  complete = true;
  const next = await (await post()).json();
  assert.equal(next.verification.status, "verified");
  assert.equal(next.verification.verifiedCount, 2);
});

test("a correction preserves the original JSON bytes of unaffected rows", async (t) => {
  const { old, post, rawStore } = await realtimeFixture(t, async () => historyResponse([95, 100]),
    { nowSeconds: 105, rows: [realtimeCandle(95), realtimeCandle(100)] });
  const prefix = '[\n {"time":95,"open":1.000000000000000000,"high":2,"low":1,"close":2},\n ';
  const bad = { ...realtimeCandle(100), close: 1 };
  fs.writeFileSync(old.dataPath, `${prefix}${JSON.stringify(bad)}\n]\n`);
  const baseSha256 = rawStore.get(old.id).metadata.dataSha256;
  const response = await post({ baseSha256, verifyAll: true });
  assert.equal(response.status, 200);
  assert.equal(fs.readFileSync(old.dataPath, "utf8"), `${prefix}${JSON.stringify(realtimeCandle(100))}\n]\n`);
});

test("malformed FARAZ values cannot overwrite a valid stored candle", async (t) => {
  const { old, post, rawStore } = await realtimeFixture(t,
    async () => Response.json({ s: "ok", t: [100], o: [1], h: [2], l: [0], c: [null] }), { nowSeconds: 105 });
  const result = await (await post({ verifyAll: true })).json();
  assert.equal(result.verification.status, "unavailable");
  assert.equal(result.verification.verifiedCount, 0);
  assert.deepEqual(rawStore.read(old.id), [realtimeCandle(100)]);
});

test("real-time catch-up leaves RAW unchanged while FARAZ has no closed rows", async (t) => {
  let requests = 0;
  const { old, post } = await realtimeFixture(t, async () => {
    requests++;
    return Response.json({ s: "no_data" });
  });
  const initial = fs.statSync(old.dataPath);
  const originalSidecar = fs.readFileSync(old.metaPath, "utf8");
  const response = await post();
  assert.equal(response.status, 200);
  const { file, candles } = await response.json();
  assert.equal(file.id, old.id);
  assert.deepEqual(candles, []);
  assert.equal(fs.statSync(old.dataPath).mtimeMs, initial.mtimeMs);
  assert.equal(fs.readFileSync(old.metaPath, "utf8"), originalSidecar);
  assert.equal(requests, 2);
});

test("real-time catch-up rejects a competing request and discards data after the RAW changes", async (t) => {
  const started = deferred();
  const finish = deferred();
  const { rawStore, old, post } = await realtimeFixture(t, async () => {
    started.resolve();
    await finish.promise;
    return historyResponse([105, 110, 115]);
  });
  const first = post();
  assert.equal(await Promise.race([first.then((response) => response.status), started.promise.then(() => "started")]), "started");
  try {
    const competing = await post();
    assert.equal(competing.status, 409);
    assert.equal((await competing.json()).code, "RAW_BUSY");
    assert.equal(rawStore.remove(old.id), true);
  } finally {
    finish.resolve();
  }
  const response = await first;
  assert.equal(response.status, 409);
  assert.deepEqual(rawStore.list(), []);
});

test("a disconnected real-time catch-up leaves the selected RAW pair intact", async (t) => {
  const started = deferred();
  const cancelled = deferred();
  const { rawStore, old, post } = await realtimeFixture(t, async (_url, { signal }) => {
    started.resolve();
    if (!signal.aborted) await new Promise((resolve) => signal.addEventListener("abort", resolve, { once: true }));
    cancelled.resolve();
    return historyResponse([105, 110, 115]);
  });
  const controller = new AbortController();
  const request = post({ signal: controller.signal });
  assert.equal(await Promise.race([request.then((response) => response.status), started.promise.then(() => "started")]), "started");
  controller.abort();
  await assert.rejects(request, { name: "AbortError" });
  await cancelled.promise;
  assert.deepEqual(rawStore.list().map(({ id }) => id), [old.id]);
  assert.deepEqual(rawStore.read(old.id), [realtimeCandle(100)]);
});

test("a failed real-time RAW publication preserves the prior data and sidecar", async (t) => {
  const { rawStore, old, post } = await realtimeFixture(t, async () => historyResponse([105, 110, 115]));
  const originalSidecar = fs.readFileSync(old.metaPath, "utf8");
  const originalRename = fs.renameSync;
  t.mock.method(fs, "renameSync", (source, target) => {
    if (source.endsWith(".data.tmp")) throw new Error("Simulated RAW publication failure.");
    return originalRename(source, target);
  });
  const response = await post();
  assert.equal(response.status, 500);
  assert.deepEqual(rawStore.read(old.id), [realtimeCandle(100)]);
  assert.equal(fs.readFileSync(old.metaPath, "utf8"), originalSidecar);
  assert.deepEqual(fs.readdirSync(path.dirname(old.dataPath)).sort(), [path.basename(old.dataPath), path.basename(old.metaPath)].sort());
});

test("disconnecting during real-time RAW staging prevents publication", async (t) => {
  const started = deferred();
  const cancelled = deferred();
  const { rawStore, old, post } = await realtimeFixture(t, async () => historyResponse([105, 110, 115]));
  const originalWrite = fs.promises.writeFile;
  t.mock.method(fs.promises, "writeFile", async (target, data, options) => {
    if (target.endsWith(".data.tmp")) {
      started.resolve();
      await new Promise((resolve) => options.signal.addEventListener("abort", resolve, { once: true }));
      cancelled.resolve();
    }
    return originalWrite(target, data, options);
  });
  const controller = new AbortController();
  const request = post({ signal: controller.signal });
  assert.equal(await Promise.race([request.then((response) => response.status), started.promise.then(() => "staging")]), "staging");
  controller.abort();
  await assert.rejects(request, { name: "AbortError" });
  await cancelled.promise;
  assert.deepEqual(rawStore.list().map(({ id }) => id), [old.id]);
  assert.deepEqual(rawStore.read(old.id), [realtimeCandle(100)]);
});

test("real-time catch-up preserves the existing JSON bytes before the closing array bracket", async (t) => {
  const { rawStore, old, post } = await realtimeFixture(t, async () => historyResponse([105]));
  const prefix = '[\n  { "time": 100, "open": 1e0, "high": 2, "low": 1, "close": 2 }\n';
  fs.writeFileSync(old.dataPath, `${prefix}]\n`);
  const response = await post({ baseSha256: rawStore.get(old.id).metadata.dataSha256 });
  assert.equal(response.status, 200);
  const { file } = await response.json();
  const contents = fs.readFileSync(rawStore.resolve(file.id).dataPath);
  assert.ok(contents.toString().startsWith(prefix));
  assert.ok(contents.toString().endsWith("]\n"));
  assert.deepEqual(JSON.parse(contents), [realtimeCandle(100), realtimeCandle(105)]);
  assert.equal(file.metadata.dataSha256, createHash("sha256").update(contents).digest("hex"));
});

test("real-time catch-up rejects a stale RAW checksum even when the file ID and tail match", async (t) => {
  let requests = 0;
  const { rawStore, old, post } = await realtimeFixture(t, async () => {
    requests++;
    return historyResponse([105]);
  });
  const updatedCandle = { ...realtimeCandle(100), open: 2 };
  fs.writeFileSync(old.dataPath, JSON.stringify([updatedCandle]));
  const response = await post();
  assert.equal(response.status, 409);
  const { code, file } = await response.json();
  assert.equal(code, "RAW_CHANGED");
  assert.equal(file.id, old.id);
  assert.notEqual(file.metadata.dataSha256, old.dataSha256);
  assert.deepEqual(rawStore.read(old.id), [updatedCandle]);
  assert.equal(requests, 0);
});

test("removing the only FARAZ session file disconnects an open browser context", async (t) => {
  const workspaceRoot = fs.mkdtempSync(path.join(os.tmpdir(), "faraz-file-authority-"));
  t.after(() => {
    fs.rmSync(workspaceRoot, { recursive: true, force: true });
    fs.rmSync(path.join(workspaceRoot, "apps", "chart", "state"), { recursive: true, force: true });
  });
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

test("FARAZ shutdown closes its owned login browser", async (t) => {
  const workspaceRoot = fs.mkdtempSync(path.join(os.tmpdir(), "faraz-shutdown-"));
  t.after(() => fs.rmSync(workspaceRoot, { recursive: true, force: true }));
  writeFakeSession(workspaceRoot);
  const managed = fakeFarazLoginBrowser();
  const api = createFarazCandleApi({ workspaceRoot, launchBrowser: async () => managed,
    fetchImpl: async () => new Response("{}", { headers: { "content-type": "application/json" } }) });
  const origin = await listenForApi(t, api);
  const opened = await fetch(`${origin}/api/faraz/auth/browser`, { method: "POST" });
  assert.equal(opened.status, 200);
  assert.equal(managed.isClosed(), false);
  await api.shutdown();
  assert.equal(managed.isClosed(), true);
});

test("FARAZ shutdown waits for a launching browser and closes it", async (t) => {
  const workspaceRoot = fs.mkdtempSync(path.join(os.tmpdir(), "faraz-launch-shutdown-"));
  t.after(() => fs.rmSync(workspaceRoot, { recursive: true, force: true }));
  const managed = fakeFarazLoginBrowser();
  const entered = deferred();
  const release = deferred();
  const api = createFarazCandleApi({ workspaceRoot, launchBrowser: async () => {
    entered.resolve();
    await release.promise;
    return managed;
  } });
  const origin = await listenForApi(t, api);
  const opening = fetch(`${origin}/api/faraz/auth/browser`, { method: "POST" });
  await entered.promise;
  const closing = api.shutdown();
  release.resolve();
  await closing;
  await opening;
  assert.equal(managed.isClosed(), true);
});

test("concurrent FARAZ browser requests share one owned launch", async (t) => {
  const workspaceRoot = fs.mkdtempSync(path.join(os.tmpdir(), "faraz-overlap-launch-"));
  t.after(() => fs.rmSync(workspaceRoot, { recursive: true, force: true }));
  const managed = fakeFarazLoginBrowser();
  const entered = deferred();
  const release = deferred();
  let launches = 0;
  const api = createFarazCandleApi({ workspaceRoot, launchBrowser: async () => {
    launches++;
    entered.resolve();
    await release.promise;
    return managed;
  } });
  const routes = new Map();
  api.configureServer({ middlewares: { use(route, handler) { routes.set(route, handler); } } });
  const handler = routes.get("/api/faraz/auth/browser");
  const response = () => ({ statusCode: 200, setHeader() {}, end() {} });
  const firstResponse = response(), secondResponse = response();
  const first = handler({ method: "POST" }, firstResponse);
  await entered.promise;
  const second = handler({ method: "POST" }, secondResponse);
  release.resolve();
  await Promise.all([first, second]);
  assert.deepEqual([firstResponse.statusCode, secondResponse.statusCode], [200, 200]);
  assert.equal(launches, 1);
  await api.shutdown();
  assert.equal(managed.isClosed(), true);
});

test("FARAZ closes a launched browser when context setup fails", async (t) => {
  const workspaceRoot = fs.mkdtempSync(path.join(os.tmpdir(), "faraz-launch-setup-failure-"));
  t.after(() => fs.rmSync(workspaceRoot, { recursive: true, force: true }));
  writeFakeSession(workspaceRoot);
  const managed = fakeFarazLoginBrowser();
  managed.context.setExtraHTTPHeaders = async () => { throw new Error("header setup failed"); };
  const api = createFarazCandleApi({ workspaceRoot, launchBrowser: async () => managed });
  const origin = await listenForApi(t, api);
  const response = await fetch(`${origin}/api/faraz/auth/browser`, { method: "POST" });
  assert.equal(response.status, 500);
  assert.equal(managed.isClosed(), true);
  await api.shutdown();
});

test("FARAZ cannot start an extraction after shutdown during auth probing", async (t) => {
  const workspaceRoot = fs.mkdtempSync(path.join(os.tmpdir(), "faraz-start-shutdown-"));
  t.after(() => fs.rmSync(workspaceRoot, { recursive: true, force: true }));
  writeFakeSession(workspaceRoot);
  const entered = deferred();
  const release = deferred();
  let requests = 0;
  const api = createFarazCandleApi({ workspaceRoot, fetchImpl: async () => {
    requests++;
    if (requests === 1) { entered.resolve(); await release.promise; }
    return new Response("{}", { headers: { "content-type": "application/json" } });
  } });
  const origin = await listenForApi(t, api);
  const starting = fetch(`${origin}/api/faraz/candles/start`, { method: "POST", headers: { "content-type": "application/json" },
    body: JSON.stringify({ mode: "range", symbolName: "TEST:PAIR", resolution: "5S", from: 100, to: 120 }) });
  await entered.promise;
  await api.shutdown();
  release.resolve();
  const response = await starting;
  assert.notEqual(response.status, 202);
  assert.equal(requests, 2); // Probe and profile only; no extraction packets.
});

test("cancelling an extraction aborts the response body after its headers arrived", { timeout: 5_000 }, async t => {
  const workspaceRoot = fs.mkdtempSync(path.join(os.tmpdir(), "faraz-cancel-body-"));
  t.after(() => fs.rmSync(workspaceRoot, { recursive: true, force: true }));
  writeFakeSession(workspaceRoot);
  const reading = deferred();
  const aborted = deferred();
  const api = createFarazCandleApi({ workspaceRoot, fetchImpl: async (url, { signal }) => {
    if (new URL(url).searchParams.get("from") !== "100") {
      return new Response("{}", { headers: { "content-type": "application/json" } });
    }
    return { text: () => new Promise((_, reject) => {
      signal.addEventListener("abort", () => {
        aborted.resolve();
        reject(signal.reason);
      }, { once: true });
      reading.resolve();
    }) };
  } });
  const origin = await listenForApi(t, api);
  const post = (route, body) => fetch(`${origin}/api/faraz/candles/${route}`, {
    method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body),
  });
  try {
    const response = await post("start", { mode: "range", symbolName: "TEST:PAIR", resolution: "5S", from: 100, to: 120 });
    assert.equal(response.status, 202);
    const { id } = await response.json();
    await reading.promise;
    assert.equal((await post("cancel", { id })).status, 200);
    await aborted.promise;
  } finally {
    await api.shutdown();
  }
});

test("FARAZ history cannot use cached credentials after the session file is removed", async (t) => {
  const workspaceRoot = fs.mkdtempSync(path.join(os.tmpdir(), "faraz-history-file-"));
  t.after(() => {
    fs.rmSync(workspaceRoot, { recursive: true, force: true });
    fs.rmSync(path.join(workspaceRoot, "apps", "chart", "state"), { recursive: true, force: true });
  });
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
  t.after(() => {
    fs.rmSync(workspaceRoot, { recursive: true, force: true });
    fs.rmSync(path.join(workspaceRoot, "apps", "chart", "state"), { recursive: true, force: true });
  });
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
  t.after(() => {
    fs.rmSync(workspaceRoot, { recursive: true, force: true });
    fs.rmSync(path.join(workspaceRoot, "apps", "chart", "state"), { recursive: true, force: true });
  });
  const managed = fakeFarazLoginBrowser();
  const api = createFarazCandleApi({ workspaceRoot, launchBrowser: async () => managed,
    fetchImpl: async () => new Response("{}", { headers: { "content-type": "application/json" } }) });
  const origin = await listenForApi(t, api);
  const sessionPath = path.join(path.join(workspaceRoot, "apps", "chart", "state"), "secret", "faraz-session.dpapi.json");

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
  t.after(() => {
    fs.rmSync(workspaceRoot, { recursive: true, force: true });
    fs.rmSync(path.join(workspaceRoot, "apps", "chart", "state"), { recursive: true, force: true });
  });
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
  t.after(() => {
    fs.rmSync(workspaceRoot, { recursive: true, force: true });
    fs.rmSync(path.join(workspaceRoot, "apps", "chart", "state"), { recursive: true, force: true });
  });
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
  t.after(() => {
    fs.rmSync(workspaceRoot, { recursive: true, force: true });
    fs.rmSync(path.join(workspaceRoot, "apps", "chart", "state"), { recursive: true, force: true });
  });
  const secretDir = path.join(path.join(workspaceRoot, "apps", "chart", "state"), "secret");
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

test("FARAZ footer polls share a probe across tabs and bypass retained status on a secret change", async (t) => {
  const workspaceRoot = fs.mkdtempSync(path.join(os.tmpdir(), "faraz-status-poll-"));
  t.after(() => fs.rmSync(workspaceRoot, { recursive: true, force: true }));
  const sessionPath = writeFakeSession(workspaceRoot);
  const signals = [];
  let clock = 100_000;
  const api = createFarazCandleApi({
    workspaceRoot,
    now: () => clock,
    fetchImpl: async (url, options) => {
      const token = options.headers["x-access-token"];
      signals.push({ endpoint: new URL(url).pathname, token });
      return Response.json({ _id: token });
    },
  });
  const origin = await listenForApi(t, api);
  const request = (symbol, passive = true) => fetch(
    `${origin}/api/faraz/auth/status?symbolName=${encodeURIComponent(symbol)}${passive ? "&passive=1" : ""}`,
  ).then(response => response.json());
  const symbols = ["FXCM:USOIL", "FOREXCOM:XAUUSD", "TEST:PAIR"];
  for (const offset of [0, 5_000, 15_000]) {
    clock = 100_000 + offset;
    const responses = await Promise.all(symbols.map(symbol => request(symbol)));
    assert.ok(responses.every(status => status.connected && status.userId === "test-file-token"));
  }
  assert.equal(signals.length, 2, "nine background status requests use one history probe and one profile fetch");
  clock = 130_000;
  await request(symbols[0]);
  assert.equal(signals.length, 4, "a badge refreshes its upstream status after 30 seconds");
  await request(symbols[0], false);
  assert.equal(signals.length, 6, "an explicit check bypasses the badge result");

  fs.writeFileSync(sessionPath, JSON.stringify({ format: "clear-text", "x-access-token": "replacement-token" }));
  assert.equal((await request(symbols[1])).userId, "replacement-token");
  assert.equal(signals.length, 8);
  fs.unlinkSync(sessionPath);
  assert.equal((await request(symbols[2])).state, "not_connected");
  assert.equal(signals.length, 8, "a deleted secret is reflected immediately without FARAZ access");
});

test("removing a FARAZ session during a slow footer probe cannot resurrect its status", { timeout: 5_000 }, async (t) => {
  const workspaceRoot = fs.mkdtempSync(path.join(os.tmpdir(), "faraz-status-race-"));
  t.after(() => fs.rmSync(workspaceRoot, { recursive: true, force: true }));
  writeFakeSession(workspaceRoot);
  const entered = deferred();
  const release = deferred();
  let probeSignal;
  const api = createFarazCandleApi({
    workspaceRoot,
    fetchImpl: async (_url, { signal }) => {
      probeSignal ||= signal;
      entered.resolve();
      await release.promise;
      signal.throwIfAborted();
      return Response.json({});
    },
  });
  const origin = await listenForApi(t, api);
  const statusUrl = `${origin}/api/faraz/auth/status?passive=1`;
  const pending = fetch(statusUrl).then(response => response.json());
  await entered.promise;
  const logout = await fetch(`${origin}/api/faraz/auth/logout`, { method: "POST" });
  assert.equal(logout.status, 200);
  release.resolve();
  assert.equal((await pending).state, "not_connected");
  assert.equal(probeSignal.aborted, true);
});

test("an explicit FARAZ check invalidates a cached footer status in both directions", async (t) => {
  const workspaceRoot = fs.mkdtempSync(path.join(os.tmpdir(), "faraz-status-explicit-"));
  t.after(() => fs.rmSync(workspaceRoot, { recursive: true, force: true }));
  writeFakeSession(workspaceRoot);
  let permitted = true;
  const checkedSymbols = [];
  const api = createFarazCandleApi({
    workspaceRoot,
    fetchImpl: async (url) => {
      const symbol = new URL(url).searchParams.get("symbolName");
      if (symbol) checkedSymbols.push(symbol);
      return Response.json({}, { status: permitted ? 200 : 401 });
    },
  });
  const origin = await listenForApi(t, api);
  const status = (query) => fetch(`${origin}/api/faraz/auth/status?${query}`).then(response => response.json());
  const passive = () => status("passive=1");
  const explicit = () => status("symbolName=FOREXCOM%3AXAUUSD");
  assert.equal((await passive()).connected, true);
  permitted = false;
  assert.equal((await explicit()).connected, false);
  assert.equal((await passive()).connected, false);
  permitted = true;
  assert.equal((await explicit()).connected, true);
  assert.equal((await passive()).connected, true);
  assert.deepEqual(checkedSymbols, ["FXCM_USOIL", "FOREXCOM_XAUUSD", "FXCM_USOIL", "FOREXCOM_XAUUSD", "FXCM_USOIL"]);
});

test("an in-flight FARAZ footer probe yields to a newer explicit check", { timeout: 5_000 }, async (t) => {
  const workspaceRoot = fs.mkdtempSync(path.join(os.tmpdir(), "faraz-status-explicit-race-"));
  t.after(() => fs.rmSync(workspaceRoot, { recursive: true, force: true }));
  writeFakeSession(workspaceRoot);
  const entered = deferred();
  const release = deferred();
  let firstSignal;
  const api = createFarazCandleApi({
    workspaceRoot,
    fetchImpl: async (_url, { signal }) => {
      if (!firstSignal) {
        firstSignal = signal;
        entered.resolve();
        await release.promise;
        return Response.json({});
      }
      return Response.json({}, { status: 401 });
    },
  });
  const origin = await listenForApi(t, api);
  const status = (query) => fetch(`${origin}/api/faraz/auth/status?${query}`).then(response => response.json());
  const pending = status("passive=1");
  await entered.promise;
  try {
    assert.equal((await status("symbolName=FOREXCOM%3AXAUUSD")).connected, false);
  } finally {
    release.resolve();
  }
  assert.equal((await pending).connected, false);
  assert.equal(firstSignal.aborted, true);
});

test("FARAZ shutdown ends a shared slow footer probe without starting another", async (t) => {
  const workspaceRoot = fs.mkdtempSync(path.join(os.tmpdir(), "faraz-status-shutdown-"));
  t.after(() => fs.rmSync(workspaceRoot, { recursive: true, force: true }));
  writeFakeSession(workspaceRoot);
  const release = deferred();
  const requests = [];
  const api = createFarazCandleApi({
    workspaceRoot,
    fetchImpl: async (url, { signal }) => {
      requests.push({ route: new URL(url).pathname, signal });
      await release.promise;
      signal.throwIfAborted();
      return Response.json({});
    },
  });
  let statusHandler;
  api.configureServer({ middlewares: { use(route, handler) {
    if (route === "/api/faraz/auth/status") statusHandler = handler;
  } } });
  const poll = (symbol) => new Promise((resolve, reject) => {
    const res = { setHeader() {}, end(body) { resolve(JSON.parse(body)); } };
    statusHandler({ url: `/?passive=1&symbolName=${symbol}` }, res).catch(reject);
  });
  const pending = [poll("FXCM%3AUSOIL"), poll("FOREXCOM%3AXAUUSD")];
  assert.equal(requests.length, 1, "both tabs wait on the same upstream history probe");
  await api.shutdown();
  release.resolve();
  for (const status of await Promise.all(pending)) assert.equal(status.state, "not_connected");
  assert.equal((await poll("TEST%3APAIR")).state, "not_connected");
  assert.equal(requests.length, 1);
  assert.equal(requests[0].signal.aborted, true);
});

test("logging out during a pending FARAZ browser capture leaves the secret deleted", { timeout: 5_000 }, async (t) => {
  const workspaceRoot = fs.mkdtempSync(path.join(os.tmpdir(), "faraz-capture-logout-"));
  t.after(() => fs.rmSync(workspaceRoot, { recursive: true, force: true }));
  const managed = fakeFarazLoginBrowser();
  const entered = deferred();
  const release = deferred();
  const storageState = managed.context.storageState;
  managed.context.storageState = async () => {
    entered.resolve();
    await release.promise;
    return storageState();
  };
  const api = createFarazCandleApi({
    workspaceRoot, launchBrowser: async () => managed, fetchImpl: async () => Response.json({}),
  });
  const origin = await listenForApi(t, api);
  const auth = `${origin}/api/faraz/auth`;
  assert.equal((await fetch(`${auth}/open`, { method: "POST" })).status, 200);
  const pending = fetch(`${auth}/status?passive=1`).then(response => response.json());
  await entered.promise;
  assert.equal((await fetch(`${auth}/logout`, { method: "POST" })).status, 200);
  release.resolve();
  assert.equal((await pending).state, "not_connected");
  assert.equal(fs.existsSync(path.join(workspaceRoot, "apps/chart/state/secret/faraz-session.dpapi.json")), false);
});

test("a rejected FARAZ session remains editable until explicit logout", async (t) => {
  const workspaceRoot = fs.mkdtempSync(path.join(os.tmpdir(), "faraz-rejected-session-"));
  t.after(() => {
    fs.rmSync(workspaceRoot, { recursive: true, force: true });
    fs.rmSync(path.join(workspaceRoot, "apps", "chart", "state"), { recursive: true, force: true });
  });
  const sessionPath = writeFakeSession(workspaceRoot);
  const api = createFarazCandleApi({ workspaceRoot,
    fetchImpl: async () => new Response("{}", { status: 401, headers: { "content-type": "application/json" } }) });
  const origin = await listenForApi(t, api);

  const status = await fetch(`${origin}/api/faraz/auth/status`).then((response) => response.json());
  assert.equal(status.connected, false);
  assert.equal(status.state, "expired_session");
  assert.equal(fs.existsSync(sessionPath), true);
});

test("signing in replaces a rejected FARAZ session only after verifying the new login", async (t) => {
  const workspaceRoot = fs.mkdtempSync(path.join(os.tmpdir(), "faraz-replace-session-"));
  t.after(() => fs.rmSync(workspaceRoot, { recursive: true, force: true }));
  const sessionPath = writeFakeSession(workspaceRoot);
  const oldSession = fs.readFileSync(sessionPath, "utf8");
  const managed = fakeFarazLoginBrowser();
  const evaluate = managed.page.evaluate;
  let signedIn = false;
  let initialStorageState;
  managed.page.evaluate = async (fn, args) => {
    if (args?.endpoint && !signedIn) return { status: 401, ok: false };
    return evaluate(fn, args);
  };
  const api = createFarazCandleApi({ workspaceRoot, launchBrowser: async ({ storageState }) => {
    initialStorageState = storageState;
    return managed;
  }, fetchImpl: async (_url, { headers }) => {
    const fresh = headers.Cookie === "farazSession=test-browser-cookie" && !headers["x-access-token"];
    return Response.json({}, { status: fresh ? 200 : 401 });
  } });
  const origin = await listenForApi(t, api);
  const auth = `${origin}/api/faraz/auth`;
  const status = () => fetch(`${auth}/status?passive=1`).then(response => response.json());

  assert.equal((await status()).state, "expired_session");
  assert.equal((await fetch(`${auth}/open`, { method: "POST" })).status, 200);
  assert.equal((await status()).state, "waiting_for_login");
  assert.equal(initialStorageState, null);
  assert.equal(fs.readFileSync(sessionPath, "utf8"), oldSession);
  assert.equal(managed.isClosed(), false);

  signedIn = true;
  assert.equal((await status()).state, "saved_session");
  assert.equal(JSON.parse(fs.readFileSync(sessionPath, "utf8")).farazSession, "test-browser-cookie");
  assert.equal(managed.isClosed(), true);
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
  t.after(() => {
    fs.rmSync(workspaceRoot, { recursive: true, force: true });
    fs.rmSync(path.join(workspaceRoot, "apps", "chart", "state"), { recursive: true, force: true });
  });
  const secretDir = path.join(path.join(workspaceRoot, "apps", "chart", "state"), "secret");
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
  t.after(() => {
    fs.rmSync(workspaceRoot, { recursive: true, force: true });
    fs.rmSync(path.join(workspaceRoot, "apps", "chart", "state"), { recursive: true, force: true });
  });
  const secretDir = path.join(path.join(workspaceRoot, "apps", "chart", "state"), "secret");
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
  t.after(() => {
    fs.rmSync(workspaceRoot, { recursive: true, force: true });
    fs.rmSync(path.join(workspaceRoot, "apps", "chart", "state"), { recursive: true, force: true });
  });
  const rawDir = path.join(path.join(workspaceRoot, "apps", "chart", "state"), "data", "raw");
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
  t.after(() => {
    fs.rmSync(workspaceRoot, { recursive: true, force: true });
    fs.rmSync(path.join(workspaceRoot, "apps", "chart", "state"), { recursive: true, force: true });
  });
  const rawDir = path.join(path.join(workspaceRoot, "apps", "chart", "state"), "data", "raw");
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
  t.after(() => {
    fs.rmSync(workspaceRoot, { recursive: true, force: true });
    fs.rmSync(path.join(workspaceRoot, "apps", "chart", "state"), { recursive: true, force: true });
  });
  const rawDir = path.join(path.join(workspaceRoot, "apps", "chart", "state"), "data", "raw");
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
  t.after(() => {
    fs.rmSync(workspaceRoot, { recursive: true, force: true });
    fs.rmSync(path.join(workspaceRoot, "apps", "chart", "state"), { recursive: true, force: true });
  });
  const rawDir = path.join(path.join(workspaceRoot, "apps", "chart", "state"), "data", "raw");
  fs.mkdirSync(rawDir, { recursive: true });
  const fileId = buildCandleFilename("TEST:PAIR", "5S", 100, 105);
  const rawPath = path.join(rawDir, fileId);
  const rows = [100, 105].map((time) => ({ time, open: 1, high: 1, low: 1, close: 1 }));
  fs.writeFileSync(rawPath, JSON.stringify(rows));
  const origin = await listenForApi(t, createFarazCandleApi({ workspaceRoot }));
  const readFile = fs.readFileSync;
  let rawReads = 0;
  t.mock.method(fs, "readFileSync", (file, ...options) => {
    if (file === rawPath) rawReads++;
    return readFile(file, ...options);
  });

  const response = await fetch(`${origin}/api/candle-files/verification`, {
    method: "POST", headers: { "content-type": "application/json" },
    body: JSON.stringify({
      id: fileId, timeframeSeconds: 5, retryCount: 4,
      ranges: [{ from: 100, to: 105, status: "complete" }],
    }),
  });
  const result = await response.json();

  assert.equal(response.status, 200, result.error);
  assert.equal(rawReads, 1);
  assert.equal(result.farazCoverage.chartUpToDate, true);
  assert.deepEqual(result.farazCoverage.ranges.map(({ from, to, status }) => ({ from, to, status })), [
    { from: 100, to: 105, status: "complete" },
  ]);
  assert.deepEqual(JSON.parse(readFile(rawPath, "utf8")), rows);
});

test("chart verification accepts a large set of checked gap ranges", async (t) => {
  const workspaceRoot = fs.mkdtempSync(path.join(os.tmpdir(), "faraz-chart-large-coverage-"));
  t.after(() => {
    fs.rmSync(workspaceRoot, { recursive: true, force: true });
    fs.rmSync(path.join(workspaceRoot, "apps", "chart", "state"), { recursive: true, force: true });
  });
  const rawDir = path.join(path.join(workspaceRoot, "apps", "chart", "state"), "data", "raw");
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
  t.after(() => {
    fs.rmSync(workspaceRoot, { recursive: true, force: true });
    fs.rmSync(path.join(workspaceRoot, "apps", "chart", "state"), { recursive: true, force: true });
  });
  const sessionPath = writeFakeSession(workspaceRoot);
  const readFileSync = fs.readFileSync;
  let sessionReads = 0;
  t.mock.method(fs, "readFileSync", (target, ...args) => {
    // The first request reads the session again while preparing its headers.
    // Slow preparation must not spend the gap between actual request starts.
    if (target === sessionPath && ++sessionReads === 2) {
      Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, 50);
    }
    return readFileSync(target, ...args);
  });
  const calls = [];
  const api = createFarazCandleApi({
    workspaceRoot,
    fetchImpl: async (url) => {
      const request = new URL(url);
      if (request.pathname.endsWith("/authentication/me")) return new Response("{}", { headers: { "content-type": "application/json" } });
      calls.push({ at: performance.now(), from: Number(request.searchParams.get("from")), to: Number(request.searchParams.get("to")), countback: Number(request.searchParams.get("countback")) });
      return new Response(JSON.stringify({ s: "ok", t: [], o: [], h: [], l: [], c: [] }), {
        headers: { "content-type": "application/json" },
      });
    },
  });
  const origin = await listenForApi(t, api);

  const history = (from, to) => fetch(`${origin}/api/faraz/history`, {
    method: "POST", headers: { "content-type": "application/json" },
    body: JSON.stringify({ symbolName: "TEST:PAIR", resolution: "1S", from, to, packetSize: 1, rateLimitMs: 900, retryCount: 0 }),
  });
  const [response, concurrentResponse] = await Promise.all([history(100, 1200), history(1500, 1500)]);
  const candles = await response.json();
  const chartPackets = calls.filter((call) => call.from >= 100 && call.to >= call.from && call.to <= 1200);

  assert.equal(response.status, 200);
  assert.equal(concurrentResponse.status, 200);
  assert.deepEqual(await concurrentResponse.json(), []);
  assert.equal(candles.length, 0);
  assert.equal(calls.length, 3);
  assert.equal(chartPackets.length, 2);
  assert.ok(chartPackets.every((call) => call.countback <= 1000));
  for (let index = 1; index < calls.length; index += 1) {
    const startSpacing = calls[index].at - calls[index - 1].at;
    assert.ok(startSpacing >= 30, `FARAZ packet starts must be paced at 30ms, got ${startSpacing.toFixed(2)}ms`);
  }
});

test("chart history proxy accepts a one-candle recovery range", async (t) => {
  const workspaceRoot = fs.mkdtempSync(path.join(os.tmpdir(), "faraz-chart-history-"));
  t.after(() => {
    fs.rmSync(workspaceRoot, { recursive: true, force: true });
    fs.rmSync(path.join(workspaceRoot, "apps", "chart", "state"), { recursive: true, force: true });
  });
  const secretDir = path.join(path.join(workspaceRoot, "apps", "chart", "state"), "secret");
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
  t.after(() => {
    fs.rmSync(workspaceRoot, { recursive: true, force: true });
    fs.rmSync(path.join(workspaceRoot, "apps", "chart", "state"), { recursive: true, force: true });
  });
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
  t.after(() => {
    fs.rmSync(workspaceRoot, { recursive: true, force: true });
    fs.rmSync(path.join(workspaceRoot, "apps", "chart", "state"), { recursive: true, force: true });
  });
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
  t.after(() => {
    fs.rmSync(workspaceRoot, { recursive: true, force: true });
    fs.rmSync(path.join(workspaceRoot, "apps", "chart", "state"), { recursive: true, force: true });
  });
  const secretDir = path.join(path.join(workspaceRoot, "apps", "chart", "state"), "secret");
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
  t.after(() => {
    fs.rmSync(workspaceRoot, { recursive: true, force: true });
    fs.rmSync(path.join(workspaceRoot, "apps", "chart", "state"), { recursive: true, force: true });
  });
  const secretDir = path.join(path.join(workspaceRoot, "apps", "chart", "state"), "secret");
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
  t.after(() => {
    fs.rmSync(workspaceRoot, { recursive: true, force: true });
    fs.rmSync(path.join(workspaceRoot, "apps", "chart", "state"), { recursive: true, force: true });
  });
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
  t.after(() => {
    fs.rmSync(workspaceRoot, { recursive: true, force: true });
    fs.rmSync(path.join(workspaceRoot, "apps", "chart", "state"), { recursive: true, force: true });
  });
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
  t.after(() => {
    fs.rmSync(workspaceRoot, { recursive: true, force: true });
    fs.rmSync(path.join(workspaceRoot, "apps", "chart", "state"), { recursive: true, force: true });
  });
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
  t.after(() => {
    fs.rmSync(workspaceRoot, { recursive: true, force: true });
    fs.rmSync(path.join(workspaceRoot, "apps", "chart", "state"), { recursive: true, force: true });
  });
  const secretDir = path.join(path.join(workspaceRoot, "apps", "chart", "state"), "secret");
  fs.mkdirSync(secretDir, { recursive: true });
  fs.writeFileSync(path.join(secretDir, "faraz-session.dpapi.json"), JSON.stringify({
    format: "clear-text", "x-access-token": "test-token",
  }));

  const candlePayload = (times) => ({
    s: "ok", t: times, o: times.map(() => 1), h: times.map(() => 1), l: times.map(() => 1), c: times.map(() => 1),
  });
  let historyRequests = 0;
  const api = createFarazCandleApi({
    workspaceRoot,
    fetchImpl: async (url) => {
      const request = new URL(url);
      if (request.pathname.endsWith("/authentication/me")) return new Response("{}", { headers: { "content-type": "application/json" } });
      const from = Number(request.searchParams.get("from"));
      const to = Number(request.searchParams.get("to"));
      if (from > 120) return Response.json(candlePayload([])); // Authentication probe.
      const times = [];
      for (let time = from; time < to; time += 5) times.push(time);
      return new Response(JSON.stringify(candlePayload(++historyRequests === 1 ? times.slice(1) : times)), {
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
  const rows = JSON.parse(fs.readFileSync(path.join(path.join(workspaceRoot, "apps", "chart", "state"), job.savedPath), "utf8"));
  assert.deepEqual(rows.map((row) => row.time), [100, 105, 110, 115, 120]);

  const downloadUrl = `${origin}/api/faraz/candles/download?id=${started.id}`;
  const download = await fetch(downloadUrl);
  assert.equal(download.status, 200);
  assert.match(download.headers.get("content-disposition"), /^attachment;/);
  assert.deepEqual(await download.json(), rows);

  // Hold a RAW read open after the first chunk so client disconnect happens
  // before EOF, regardless of socket buffering or disk speed.
  const stream = new Readable({ read() {} });
  t.mock.method(fs, "createReadStream", () => stream);
  const controller = new AbortController();
  const closed = new Promise((resolve, reject) => {
    const timeout = setTimeout(() => reject(new Error("Disconnected download did not close its RAW stream.")), 1_000);
    stream.once("close", () => { clearTimeout(timeout); resolve(); });
  });
  const pendingDownload = fetch(downloadUrl, { signal: controller.signal });
  stream.push("[");
  const partial = await pendingDownload;
  const reader = partial.body.getReader();
  assert.equal(Buffer.from((await reader.read()).value).toString(), "[");
  controller.abort();
  try {
    await closed;
  } finally {
    reader.releaseLock();
    stream.destroy();
  }
});

test("FARAZ does not publish an incomplete range until the user continues from the first available candle", async (t) => {
  const workspaceRoot = fs.mkdtempSync(path.join(os.tmpdir(), "faraz-exporter-decision-"));
  t.after(() => {
    fs.rmSync(workspaceRoot, { recursive: true, force: true });
    fs.rmSync(path.join(workspaceRoot, "apps", "chart", "state"), { recursive: true, force: true });
  });
  const secretDir = path.join(path.join(workspaceRoot, "apps", "chart", "state"), "secret");
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
      const from = Number(request.searchParams.get("from"));
      const to = Number(request.searchParams.get("to"));
      if (from <= 120) historyRequests++;
      const times = [];
      for (let time = from; time < to; time += 5) if (time !== 100) times.push(time);
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
  const rows = JSON.parse(fs.readFileSync(path.join(path.join(workspaceRoot, "apps", "chart", "state"), continued.savedPath), "utf8"));
  assert.deepEqual(rows.map((row) => row.time), [105, 110, 115, 120]);

  const cancelled = await fetch(`${origin}/api/faraz/candles/start`, {
    method: "POST", headers: { "content-type": "application/json" },
    body: JSON.stringify({ mode: "range", symbolName: "TEST:PAIR", resolution: "5S", from: 100, to: 120, packetSize: 10, rateLimitMs: 30 }),
  }).then(response => response.json());
  const statusUrl = `${origin}/api/faraz/candles/status?id=${cancelled.id}`;
  let pending = cancelled;
  for (let attempt = 0; pending.running && attempt < 100; attempt++) {
    await new Promise(resolve => setTimeout(resolve, 20));
    pending = await fetch(statusUrl).then(response => response.json());
  }
  assert.equal(pending.awaitingCoverageDecision, true);
  const cancel = await fetch(`${origin}/api/faraz/candles/cancel`, {
    method: "POST", headers: { "content-type": "application/json" },
    body: JSON.stringify({ id: cancelled.id }),
  });
  assert.equal(cancel.status, 200);
  const final = await fetch(statusUrl).then(response => response.json());
  assert.equal(final.awaitingCoverageDecision, false);
  assert.equal(final.cancelledByUser, true);
  const staleContinue = await fetch(`${origin}/api/faraz/candles/coverage-decision`, {
    method: "POST", headers: { "content-type": "application/json" },
    body: JSON.stringify({ id: cancelled.id, decision: "continue_from_available" }),
  });
  assert.equal(staleContinue.status, 400);
});

test("FARAZ can save requested candles with source gaps without a second confirmation", async (t) => {
  const base = 1_800_000;
  const available = [1_800_000, 1_800_300, 1_800_900, 1_801_200, 1_801_800];
  const cases = [
    { label: "previous candles", inputs: { mode: "count", candleCount: 4 }, expected: [1_800_300, 1_800_900, 1_801_200, 1_801_800] },
    { label: "time range with automatic saving", inputs: { mode: "range", from: base, saveAvailable: true }, expected: available },
  ];
  for (const { label, inputs, expected } of cases) {
    await t.test(label, async (t) => {
      const workspaceRoot = fs.mkdtempSync(path.join(os.tmpdir(), "faraz-export-with-gaps-"));
      t.after(() => fs.rmSync(workspaceRoot, { recursive: true, force: true }));
      writeFakeSession(workspaceRoot);
      const origin = await listenForApi(t, createFarazCandleApi({
        workspaceRoot,
        fetchImpl: async (url) => historyResponse(available.filter(time =>
          time >= Number(url.searchParams.get("from")) && time < Number(url.searchParams.get("to")))),
      }));
      const started = await fetch(`${origin}/api/faraz/candles/start`, {
        method: "POST", headers: { "content-type": "application/json" },
        body: JSON.stringify({ ...inputs, symbolName: "TEST:PAIR", resolution: "5M", to: 1_802_100, packetSize: 3 }),
      });
      assert.equal(started.status, 202);
      let job = await started.json();
      const statusUrl = `${origin}/api/faraz/candles/status?id=${job.id}`;
      for (let attempt = 0; job.running && attempt < 100; attempt++) {
        await new Promise(resolve => setTimeout(resolve, 20));
        job = await (await fetch(statusUrl)).json();
      }

      assert.equal(job.done, true, job.error || job.stage);
      assert.equal(job.awaitingCoverageDecision, false);
      assert.equal(job.coverageComplete, false);
      assert.ok(job.suspiciousGaps.some(gap => gap.status === "source_gap"));
      assert.deepEqual(JSON.parse(fs.readFileSync(path.join(workspaceRoot, "apps", "chart", "state", job.savedPath), "utf8"))
        .map(row => row.time), expected);
    });
  }
});

test("FARAZ previous candles saves only closed candles when the end is now", async (t) => {
  const workspaceRoot = fs.mkdtempSync(path.join(os.tmpdir(), "faraz-unclosed-export-"));
  t.after(() => fs.rmSync(workspaceRoot, { recursive: true, force: true }));
  writeFakeSession(workspaceRoot);
  const openTimes = [1_801_200, 1_801_500, 1_801_800, 1_802_100];
  const nowSeconds = 1_802_220;
  const origin = await listenForApi(t, createFarazCandleApi({
    workspaceRoot, now: () => nowSeconds * 1000,
    fetchImpl: async (url) => historyResponse(openTimes.filter(time =>
      time >= Number(url.searchParams.get("from")) && time < Number(url.searchParams.get("to")))),
  }));
  const started = await fetch(`${origin}/api/faraz/candles/start`, {
    method: "POST", headers: { "content-type": "application/json" },
    body: JSON.stringify({ mode: "count", candleCount: 2, symbolName: "TEST:PAIR", resolution: "5M", to: nowSeconds }),
  });
  assert.equal(started.status, 202);
  let job = await started.json();
  const statusUrl = `${origin}/api/faraz/candles/status?id=${job.id}`;
  for (let attempt = 0; job.running && attempt < 100; attempt++) {
    await new Promise(resolve => setTimeout(resolve, 20));
    job = await (await fetch(statusUrl)).json();
  }
  assert.equal(job.done, true, job.error || job.stage);
  assert.deepEqual(JSON.parse(fs.readFileSync(path.join(workspaceRoot, "apps", "chart", "state", job.savedPath), "utf8"))
    .map(row => row.time), [1_801_500, 1_801_800]);
});

test("FARAZ exporter snaps a manual range inward to complete timeframe slots", async (t) => {
  const workspaceRoot = fs.mkdtempSync(path.join(os.tmpdir(), "faraz-exporter-snap-"));
  t.after(() => {
    fs.rmSync(workspaceRoot, { recursive: true, force: true });
    fs.rmSync(path.join(workspaceRoot, "apps", "chart", "state"), { recursive: true, force: true });
  });
  writeFakeSession(workspaceRoot);
  const api = createFarazCandleApi({
    workspaceRoot,
    fetchImpl: async (url) => {
      const request = new URL(url);
      if (request.pathname.endsWith("/authentication/me")) return new Response("{}", { headers: { "content-type": "application/json" } });
      const from = Number(request.searchParams.get("from"));
      const to = Number(request.searchParams.get("to"));
      const times = [];
      for (let time = from; time < to; time += 5) times.push(time);
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
  assert.deepEqual(JSON.parse(fs.readFileSync(path.join(path.join(workspaceRoot, "apps", "chart", "state"), job.savedPath), "utf8")).map((row) => row.time), [105, 110, 115]);
});

test("FARAZ exports native resolutions with exclusive packet ends and preserves session timestamps", async (t) => {
  const from = 1_800_000;
  const cases = [
    { frame: "30S", wire: "30S", seconds: 30, offset: 0 },
    { frame: "1M", wire: "1", seconds: 60, offset: 0 },
    { frame: "5M", wire: "5", seconds: 300, offset: 0 },
    { frame: "10M", wire: "10", seconds: 600, offset: 0 },
    { frame: "15M", wire: "15", seconds: 900, offset: 0 },
    { frame: "45M", wire: "45", seconds: 2700, offset: 1800, shift: 900 },
    { frame: "1H", wire: "60", seconds: 3600, offset: 0 },
    { frame: "4H", wire: "240", seconds: 14400, offset: 10800, shift: 3600 },
    { frame: "1D", wire: "1D", seconds: 86400, offset: 0 },
  ];
  for (const { frame, wire, seconds, offset, shift = 0 } of cases) {
    await t.test(frame, async (t) => {
      const workspaceRoot = fs.mkdtempSync(path.join(os.tmpdir(), "faraz-export-resolution-"));
      t.after(() => fs.rmSync(workspaceRoot, { recursive: true, force: true }));
      writeFakeSession(workspaceRoot);
      const start = Math.ceil(from / seconds) * seconds;
      const times = [0, 1, 2, 3, 4].map(index => start + offset + index * seconds + (index >= 2 ? shift : 0));
      const to = times.at(-1);
      const requests = [];
      const origin = await listenForApi(t, createFarazCandleApi({
        workspaceRoot,
        fetchImpl: async (url) => {
          const request = new URL(url);
          const params = request.searchParams;
          if (+params.get("from") > to || request.pathname.endsWith("/authentication/me")) return Response.json({ s: "no_data" });
          const lo = +params.get("from");
          const hi = +params.get("to");
          requests.push([params.get("resolution"), params.get("firstDataRequest"), params.get("latest"), lo, hi]);
          const rows = [times[0] - seconds, ...times, to + 1].filter(time => time >= lo - seconds && time < hi);
          return historyResponse(rows);
        },
      }));
      let job = await fetch(`${origin}/api/faraz/candles/start`, {
        method: "POST", headers: { "content-type": "application/json" },
        body: JSON.stringify({ mode: "range", symbolName: "TEST:PAIR", resolution: frame, from: start, to, packetSize: 2 }),
      }).then(response => response.json());
      const statusUrl = `${origin}/api/faraz/candles/status?id=${job.id}`;
      for (let attempt = 0; job.running && attempt < 100; attempt++) {
        await new Promise(resolve => setTimeout(resolve, 20));
        job = await (await fetch(statusUrl)).json();
      }

      assert.equal(job.done, true, job.error);
      assert.equal(job.outsideRangeRows > 0, true);
      assert.equal(requests.length, 3);
      assert.deepEqual(requests.map(request => request.slice(0, 3)), Array.from({ length: 3 }, () => [wire, "false", "false"]));
      assert.deepEqual(requests.map(request => request.slice(3)), [[start, start + 2 * seconds], [start + 2 * seconds, start + 4 * seconds], [start + 4 * seconds, to + 1]]);
      assert.equal(job.resolution, frame);
      assert.deepEqual(JSON.parse(fs.readFileSync(path.join(workspaceRoot, "apps", "chart", "state", job.savedPath), "utf8")).map(row => row.time), times);
    });
  }
});
