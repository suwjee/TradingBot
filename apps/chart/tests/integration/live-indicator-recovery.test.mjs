import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { once } from "node:events";
import fs from "node:fs/promises";
import path from "node:path";
import { createInterface } from "node:readline";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { createRawResourceStore } from "../../server/raw-resource-store.js";
import { createAlertMonitor, normalizeAlertRule } from "../../src/features/alerts/rules.js";

const chart = fileURLToPath(new URL("../../", import.meta.url));
const startVite = `
  import { createServer } from "vite";
  import fs from "node:fs/promises";
  if (process.env.TRADINGBOT_TEST_MARKET) {
    const rows = JSON.parse(await fs.readFile(process.env.TRADINGBOT_TEST_MARKET, "utf8"));
    globalThis.fetch = async (input) => {
      const url = new URL(input);
      if (url.pathname !== "/api/customer/trading-view/history") throw new Error("Unexpected upstream test route");
      const selected = rows.filter(row => row.time >= Number(url.searchParams.get("from"))
        && row.time <= Number(url.searchParams.get("to")));
      return Response.json({ s: "ok", t: selected.map(row => row.time), o: selected.map(row => row.open),
        h: selected.map(row => row.high), l: selected.map(row => row.low), c: selected.map(row => row.close) });
    };
  }
  const heldPath = process.env.TRADINGBOT_TEST_HOLD_RAW;
  let gatePlugin;
  if (heldPath) {
    let release, reads = 0, cancelled = 0, holdAt = 1;
    const readFile = fs.readFile;
    fs.readFile = async (file, options) => {
      if (file !== heldPath || ++reads !== holdAt) return readFile(file, options);
      const signal = options?.signal;
      function abort() { cancelled++; release(); }
      try {
        await new Promise(resolve => {
          release = resolve;
          signal?.addEventListener("abort", abort, { once: true });
          if (signal?.aborted) abort();
        });
        signal?.throwIfAborted();
      } finally {
        signal?.removeEventListener("abort", abort);
      }
      return readFile(file, options);
    };
    gatePlugin = { name: "test-raw-read-gate", configureServer(server) {
      server.middlewares.use("/__test/raw-read-gate", (req, res) => {
        if (req.method === "POST") release?.();
        if (req.method === "PUT") holdAt = reads + 1;
        res.setHeader("Content-Type", "application/json");
        res.end(JSON.stringify({ reads, cancelled }));
      });
    } };
  }
  const server = await createServer({ configLoader: "native", plugins: [gatePlugin],
    server: { port: 0, host: "127.0.0.1", ws: false } });
  await server.listen();
  console.log("TEST_PORT:" + server.httpServer.address().port);
  process.stdin.resume();
  process.stdin.once("end", () => server.close());
`;

async function launch(stateRoot, marketFixture = "", holdRaw = "") {
  const child = spawn(process.execPath, ["--input-type=module", "-e", startVite], {
    cwd: chart, env: { ...process.env, TRADINGBOT_LOCAL_STATE_ROOT: stateRoot,
      TRADINGBOT_TEST_MARKET: marketFixture, TRADINGBOT_TEST_HOLD_RAW: holdRaw }, windowsHide: true,
  });
  const closed = once(child, "close");
  const output = createInterface({ input: child.stdout });
  let stderr = "";
  child.stderr.on("data", bytes => { stderr += bytes; });
  async function stop() {
    child.stdin.end();
    const [exitCode] = await closed;
    assert.equal(exitCode, 0, stderr);
  }
  for await (const line of output) {
    if (!line.startsWith("TEST_PORT:")) continue;
    const port = Number(line.slice("TEST_PORT:".length));
    const report = (id, method) => fetch(`http://127.0.0.1:${port}/api/info/${id}`, { method });
    const post = (route, body, signal = AbortSignal.timeout(90_000)) => fetch(`http://127.0.0.1:${port}/api${route}`, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body), signal,
    });
    return { stop, getReport: id => report(id, "GET"), saveReport: id => report(id, "POST"),
      post: (route, body, signal) => post(`/reactions${route}`, body, signal),
      update: body => post("/candle-files/realtime", body),
      rawReadGate: (method = "GET") => fetch(`http://127.0.0.1:${port}/__test/raw-read-gate`, { method })
        .then(response => response.json()),
      progress: requestId => fetch(`http://127.0.0.1:${port}/api/reactions/progress?requestId=${encodeURIComponent(requestId)}`,
        { signal: AbortSignal.timeout(30_000) }) };
  }
  await stop();
  assert.fail(`Vite did not start. ${stderr}`);
}

async function* progressEvents(response) {
  assert.equal(response.status, 200);
  assert.match(response.headers.get("Content-Type"), /^text\/event-stream/);
  const reader = response.body.pipeThrough(new TextDecoderStream()).getReader();
  let pending = "";
  try {
    for (;;) {
      const { done, value } = await reader.read();
      if (done) return;
      pending += value;
      let end;
      while ((end = pending.indexOf("\n\n")) >= 0) {
        const message = pending.slice(0, end);
        pending = pending.slice(end + 2);
        if (!message.startsWith("data: ")) continue;
        yield JSON.parse(message.slice(6));
      }
    }
  } finally {
    await reader.cancel();
  }
}

async function indicatorProgress(response) {
  const events = [];
  for await (const event of progressEvents(response)) {
    events.push(event);
    if (event.status === "finished" || event.status === "failed") return events;
  }
  assert.fail("Engine progress ended without a terminal event");
}

async function indicator(response) {
  const payload = await response.json();
  assert.equal(response.status, 200, JSON.stringify(payload));
  const { timings, ...output } = payload;
  return output;
}

test("disconnecting calculation tabs releases abandoned work and retains identical surviving requests", {
  skip: process.platform !== "win32" && "Selected-range Engine input uses Windows named pipes",
  timeout: 30_000,
}, async t => {
  const directory = path.resolve(chart, "state", "tmp");
  await fs.mkdir(directory, { recursive: true });
  const stateRoot = await fs.mkdtemp(path.join(directory, "live-disconnect-test-"));
  t.after(async () => {
    assert.equal(path.dirname(stateRoot), directory);
    await fs.rm(stateRoot, { recursive: true, force: true });
  });
  const start = 1_795_000_020;
  const rows = Array.from({ length: 650 }, (_, index) => {
    const close = 100 + index % 7;
    return { time: start + index * 5, open: close, high: close + 1, low: close - 1, close };
  });
  const store = createRawResourceStore({ rootDir: path.join(stateRoot, "data", "raw") });
  const raw = store.write({ broker: "TEST", symbol: "DISCONNECT", timeframe: "5S", candles: rows });
  const server = await launch(stateRoot, "", raw.dataPath);
  const request = { direction: "bullish", timeframe: 30, chartTimeframe: 30, blueLines: true, from: start,
    to: Math.floor(rows.at(-1).time / 30) * 30 };
  const clients = [];
  async function waitForRawRead(reads, cancelled) {
    for (let attempt = 0; attempt < 100; attempt++) {
      const status = await server.rawReadGate();
      if (status.reads === reads && status.cancelled === cancelled) return;
      await new Promise(resolve => setTimeout(resolve, 10));
    }
    assert.fail(`Expected ${reads} admitted RAW reads and ${cancelled} cancellations`);
  }
  async function startRecovery(tabId, expectedEvents, requestId = `request-${tabId}`) {
    const client = new AbortController();
    const stream = expectedEvents ? progressEvents(await server.progress(requestId)) : null;
    const pending = server.post("/continue", { id: raw.id, chartId: raw.chartId, tabId,
      proof: { chartId: raw.chartId, tabId, request, to: request.to }, requestId }, client.signal);
    pending.catch(() => {});
    clients.push({ client, stream, pending });
    for (const expected of expectedEvents || []) assert.equal((await stream.next()).value?.label, expected);
    return { client, stream, pending };
  }
  async function cancelledProgress(stream) {
    assert.deepEqual(await stream.next(), { done: false, value: { status: "failed", label: "Calculation cancelled" } });
    assert.equal((await stream.next()).done, true);
  }
  async function disconnect({ client, stream, pending }) {
    client.abort();
    await assert.rejects(pending, { name: "AbortError" });
    if (stream) await cancelledProgress(stream);
  }
  try {
    const validating = "Validate RAW checkpoint";
    const first = await startRecovery("tab-first", [validating, "Recover live Engine checkpoint"]);
    assert.deepEqual(await server.rawReadGate(), { reads: 1, cancelled: 0 });
    const queued = await startRecovery("tab-abandoned", [validating]);
    const survivor = await startRecovery("tab-survivor");
    await disconnect(queued);
    assert.deepEqual(await server.rawReadGate(), { reads: 1, cancelled: 0 });
    await disconnect(first);
    const response = await survivor.pending;
    await indicator(response);
    assert.match(response.headers.get("X-QG-Live-Session"), /^[a-f0-9]{32}$/);
    assert.deepEqual(await server.rawReadGate(), { reads: 2, cancelled: 1 });

    await server.rawReadGate("PUT");
    const recoveryEvents = [validating, "Recover live Engine checkpoint"];
    const original = await startRecovery("tab-retry", recoveryEvents);
    const duplicate = await startRecovery("tab-retry", recoveryEvents, "request-tab-retry-duplicate");
    await disconnect(original);
    assert.deepEqual(await server.rawReadGate("POST"), { reads: 3, cancelled: 1 });
    const continued = await duplicate.pending;
    await indicator(continued);
    assert.match(continued.headers.get("X-QG-Live-Session"), /^[a-f0-9]{32}$/);
    let finished = false;
    for await (const event of duplicate.stream) {
      assert.notEqual(event.status, "failed");
      if (event.status === "finished") {
        finished = true;
        break;
      }
    }
    assert.equal(finished, true);
    assert.deepEqual(await server.rawReadGate(), { reads: 3, cancelled: 1 });

    await server.rawReadGate("PUT");
    const applyId = "request-abandoned-apply";
    const controller = new AbortController();
    const pending = server.post("", { ...request, to: request.to - 30, id: raw.id,
      chartId: raw.chartId, requestId: applyId }, controller.signal);
    pending.catch(() => {});
    clients.push({ client: controller, pending });
    await waitForRawRead(4, 1);
    await disconnect({ client: controller, pending });
    await waitForRawRead(4, 2);
    const late = progressEvents(await server.progress(applyId));
    try { await cancelledProgress(late); }
    finally { await late.return(); }
    assert.equal((await server.progress(applyId)).status, 204);
    assert.deepEqual(await server.rawReadGate(), { reads: 4, cancelled: 2 });
  } finally {
    for (const { client, stream } of clients) {
      client.abort();
      await stream?.return();
    }
    try { await server.rawReadGate("POST"); }
    finally { await server.stop(); }
  }
});

test("a tab catches up after five minutes and recovers across a restart without calculation files", {
  skip: process.platform !== "win32" && "Selected-range Engine input uses Windows named pipes",
  timeout: 180_000,
}, async () => {
  const directory = path.resolve(chart, "state", "tmp");
  await fs.mkdir(directory, { recursive: true });
  const stateRoot = await fs.mkdtemp(path.join(directory, "live-recovery-test-"));
  const store = createRawResourceStore({ rootDir: path.join(stateRoot, "data", "raw") });
  const rawFixture = process.env.TRADINGBOT_LIVE_TEST_RAW;
  const rows = rawFixture ? JSON.parse(await fs.readFile(rawFixture, "utf8")) : Array.from({ length: 650 }, (_, i) => {
    const mid = 100 + (i * 13 % 41) - i / 17;
    const open = mid + (i % 3), close = mid - (i % 2);
    return { time: 1_795_000_020 + i * 5, open, high: Math.max(open, close) + i % 7,
      low: Math.min(open, close) - i % 5, close };
  });
  const initialCount = rows.length - 100;
  let raw = store.get(store.write({ broker: "TEST", symbol: "RECOVERY", timeframe: "5S", candles: rows.slice(0, initialCount) }).id);
  const chartId = raw.chartId;
  const requests = ["bullish", "bearish"].map(direction => ({ chartId, direction, timeframe: direction === "bullish" ? 30 : 60,
    chartTimeframe: 30, from: Math.floor(rows[18].time / 30) * 30,
    to: Math.floor(rows[initialCount - 42].time / 30) * 30, blueLines: true }));
  let server;
  async function restart() {
    await server.stop();
    server = null;
    server = await launch(stateRoot);
  }
  try {
    server = await launch(stateRoot);
    const cache = path.join(stateRoot, "cache", "indicator-calculations");
    // Opening a report explicitly saves its immutable snapshot. Polling and
    // recovery must leave ordinary calculation caches alone.
    const cacheFiles = async () => (await fs.readdir(cache, { recursive: true }))
      .filter(entry => entry !== "live" && !/^live[\\/]/.test(entry));
    const legacyResponse = await server.post("", { ...requests[0], id: raw.id });
    const baseline = await indicator(legacyResponse);
    const legacyId = legacyResponse.headers.get("X-QG-Calculation-Id");
    const legacyFile = path.join(cache, legacyId);
    const legacyContents = await fs.readFile(legacyFile, "utf8");
    await fs.writeFile(legacyFile, JSON.stringify({ timeframe: 30, directions: {}, marker: "disk-cache" }));
    const freshResponse = await server.post("", { ...requests[0], id: raw.id });
    assert.deepEqual(await indicator(freshResponse), baseline);
    assert.equal(freshResponse.headers.get("X-QG-Cache"), "bypass");
    assert.notEqual(freshResponse.headers.get("X-QG-Calculation-Id"), legacyId);
    const originalCacheFiles = await cacheFiles();

    const emptyTab = { chartId, tabId: "unapplied-tab" };
    const missing = await server.post("/continue", { id: raw.id, ...emptyTab, calculationId: legacyId });
    assert.equal(missing.status, 404);
    assert.equal((await missing.json()).code, "NO_INDICATOR_CALCULATION");

    const checkpoints = [];
    const openedReports = [];
    const alertMonitors = requests.map(({ direction }) => {
      const rule = normalizeAlertRule({ id: direction, name: direction, enabled: true, sound: false,
        seconds: 3, steps: [[`${direction}:reaction`]] });
      const monitor = createAlertMonitor();
      monitor.baseline(raw.to);
      return { rule, monitor, matches: 0 };
    });
    for (const [index, request] of requests.entries()) {
      const tabId = "applied-tab-" + index;
      const response = await server.post("", { ...request, tabId, id: raw.id, liveSession: true });
      const actual = await indicator(response);
      if (index === 0) assert.deepEqual(actual, baseline);
      assert.equal(response.headers.get("X-QG-Cache"), "bypass");
      const sessionId = response.headers.get("X-QG-Live-Session");
      const proof = JSON.parse(response.headers.get("X-QG-Live-Proof"));
      const reportId = response.headers.get("X-QG-Calculation-Id");
      assert(sessionId && proof);
      assert.match(reportId, /^live\/[a-f0-9]{32}$/);
      const report = await server.getReport(reportId);
      assert.equal(report.status, 200);
      assert.equal((await report.json()).snapshot.calculation.direction, request.direction);
      const saved = await server.saveReport(reportId);
      assert.equal(saved.status, 200);
      openedReports.push(reportId);
      checkpoints.push({ sessionId, proof, tabId });
    }
    assert.deepEqual(await cacheFiles(), originalCacheFiles);
    assert.match(await fs.readFile(legacyFile, "utf8"), /disk-cache/);
    await fs.writeFile(legacyFile, legacyContents);

    const otherTab = await server.post("/continue", { id: raw.id, ...checkpoints[0], ...emptyTab });
    assert.equal(otherTab.status, 404);
    assert.equal((await otherTab.json()).code, "NO_INDICATOR_CALCULATION");

    for (const count of [initialCount + 60, initialCount + 73]) {
      const oldId = raw.id;
      raw = await store.appendLatest(raw, rows.slice(raw.count, count), 5, store.version(raw.id), new AbortController().signal);
      assert.notEqual(raw.id, oldId);
      assert.equal(raw.chartId, chartId);
      const restarted = count !== initialCount + 60;
      if (restarted) await restart();
      for (const [index, checkpoint] of checkpoints.entries()) {
        const before = await cacheFiles();
        const response = await server.post("/continue", { id: raw.id, chartId, ...checkpoint });
        const actual = await indicator(response);
        assert.notEqual(response.headers.get("X-QG-Calculation-Id"), openedReports[index]);
        const alert = alertMonitors[index];
        const matches = alert.monitor.advance([alert.rule], actual, raw.to);
        alert.matches += matches.length;
        assert.ok(matches.every(({ events: [event] }) => event.direction === requests[index].direction && event.time > rows[initialCount - 1].time));
        assert.deepEqual(alert.monitor.advance([alert.rule], actual, raw.to), []);
        if (restarted) {
          const sessionId = response.headers.get("X-QG-Live-Session");
          assert(sessionId && sessionId !== checkpoint.sessionId);
          checkpoint.sessionId = sessionId;
        }
        checkpoint.proof = JSON.parse(response.headers.get("X-QG-Live-Proof"));
        assert.equal(checkpoint.proof.request.from, requests[index].from);
        assert.equal(checkpoint.proof.request.direction, requests[index].direction);
        assert.equal(checkpoint.proof.to, Math.floor(raw.to / 30) * 30);
        assert.deepEqual(await cacheFiles(), before);
        const expected = await indicator(await server.post("", { ...requests[index], id: raw.id, to: checkpoint.proof.to }));
        assert.deepEqual(actual, expected);
        const repeated = await server.post("/continue", { id: raw.id, chartId, ...checkpoint });
        assert.deepEqual(await indicator(repeated), actual);
        assert.notEqual(repeated.headers.get("X-QG-Calculation-Id"), response.headers.get("X-QG-Calculation-Id"));
      }
    }
    if (!rawFixture) assert.ok(alertMonitors.some(alert => alert.matches > 0),
      `The synthetic live extension should trigger Reaction rules, got ${alertMonitors.map(alert => alert.matches).join(", ")}.`);
    await restart();
    for (const [index, reportId] of openedReports.entries()) {
      const report = await server.getReport(reportId);
      assert.equal(report.status, 200);
      assert.equal((await report.json()).snapshot.calculation.to, requests[index].to);
    }
    const idleRequestId = "restart-current-range";
    const idleProgress = await server.progress(idleRequestId);
    const [idle, idleEvents] = await Promise.all([
      server.post("/continue", { id: raw.id, chartId, ...checkpoints[0], keepAlive: true, requestId: idleRequestId }),
      indicatorProgress(idleProgress),
    ]);
    assert.equal(idleEvents.filter(event =>
      event.status === "started" && event.label === "Build live market chronology").length, 1);
    await indicator(idle);
    checkpoints[0].sessionId = idle.headers.get("X-QG-Live-Session");
    const ping = await server.post("/continue", { id: raw.id, chartId, ...checkpoints[0], keepAlive: true });
    assert.equal(ping.status, 204);

    const modified = { ...rows[1], close: rows[1].low };
    if (modified.close === rows[1].close) modified.close = rows[1].high;
    assert.notEqual(modified.close, rows[1].close);
    await fs.writeFile(raw.dataPath, JSON.stringify([rows[0], modified, ...rows.slice(2, raw.count)]));
    const requestId = "historical-revision-recovery";
    const recoveryProgress = await server.progress(requestId);
    const [rebuild, recoveryEvents] = await Promise.all([
      server.post("/continue", { id: raw.id, chartId, ...checkpoints[0], requestId }),
      indicatorProgress(recoveryProgress),
    ]);
    assert.equal(recoveryEvents.filter(event =>
      event.status === "started" && event.label === "Build live market chronology").length, 1);
    const actual = await indicator(rebuild);
    const expected = await indicator(await server.post("", { ...requests[0], id: raw.id,
      to: Math.floor(raw.to / 30) * 30 }));
    assert.deepEqual(actual, expected);

    const fresh = await server.post("/continue", { id: raw.id, ...emptyTab });
    assert.equal(fresh.status, 404);
    assert.equal((await fresh.json()).code, "NO_INDICATOR_CALCULATION");
  } finally {
    if (server) await server.stop();
    assert.equal(path.dirname(stateRoot), directory);
    await fs.rm(stateRoot, { recursive: true, force: true });
  }
});

test("a confirmed realtime append continues in the same worker and matches a fresh Apply", {
  skip: process.platform !== "win32" && "Selected-range Engine input uses Windows named pipes",
  timeout: 45_000,
}, async () => {
  const directory = path.resolve(chart, "state", "tmp");
  await fs.mkdir(directory, { recursive: true });
  const stateRoot = await fs.mkdtemp(path.join(directory, "live-append-test-"));
  const store = createRawResourceStore({ rootDir: path.join(stateRoot, "data", "raw") });
  const first = Math.floor(Date.now() / 30_000) * 30 - 1_200;
  const rows = Array.from({ length: 220 }, (_, index) => {
    const price = 100 + (index * 13 % 41);
    return { time: first + index * 5, open: price, high: price + 2, low: price - 2, close: price + 1 };
  });
  const marketFixture = path.join(stateRoot, "market.json");
  const secrets = path.join(stateRoot, "secret");
  await fs.mkdir(secrets);
  await fs.writeFile(path.join(secrets, "faraz-session.dpapi.json"), JSON.stringify({ format: "clear-text",
    "x-access-token": "test-token", farazSession: "test-session", storageState: { cookies: [], origins: [] } }));
  await fs.writeFile(marketFixture, JSON.stringify(rows));
  const raw = store.get(store.write({ broker: "TEST", symbol: "APPEND", timeframe: "5S", candles: rows.slice(0, 215) }).id);
  const request = { id: raw.id, chartId: raw.chartId, tabId: "realtime-append-tab", direction: "bullish",
    timeframe: 30, chartTimeframe: 30, from: first, to: Math.floor(raw.to / 30) * 30, blueLines: true };
  let server;
  try {
    server = await launch(stateRoot, marketFixture);
    const seed = await server.post("", { ...request, liveSession: true });
    await indicator(seed);
    const sessionId = seed.headers.get("X-QG-Live-Session");
    const proof = JSON.parse(seed.headers.get("X-QG-Live-Proof"));
    assert.ok(sessionId && proof);
    const response = await server.update({ id: raw.id, chartId: raw.chartId, lastCandleTime: raw.to,
      baseSha256: raw.metadata.dataSha256, phase: "latest" });
    const updated = await response.json();
    assert.equal(response.status, 200, JSON.stringify(updated));
    assert.equal(updated.supportsRecentVerification, true);
    assert.deepEqual(updated.candles, rows.slice(215));
    const replayResponse = await server.update({ id: raw.id, chartId: raw.chartId, lastCandleTime: raw.to,
      baseSha256: raw.metadata.dataSha256, phase: "replay" });
    const replayed = await replayResponse.json();
    assert.equal(replayResponse.status, 200, JSON.stringify(replayed));
    assert.deepEqual(replayed.candles, updated.candles);
    assert.equal(replayed.file.metadata.dataSha256, updated.file.metadata.dataSha256);
    const recentResponse = await server.update({ id: replayed.file.id, chartId: raw.chartId,
      lastCandleTime: replayed.file.to, baseSha256: replayed.file.metadata.dataSha256, phase: "recent", previousTail: raw.to });
    const recent = await recentResponse.json();
    assert.equal(recentResponse.status, 200, JSON.stringify(recent));
    assert.equal(recent.verification.checkedCount, rows.length - 1);
    assert.deepEqual(recent.corrections, []);
    assert.equal(recent.file.metadata.dataSha256, replayed.file.metadata.dataSha256);
    const requestId = "verified-realtime-progress";
    const progressResponse = await server.progress(requestId);
    const [continued, events] = await Promise.all([
      server.post("/continue", { id: replayed.file.id, chartId: raw.chartId, tabId: request.tabId, sessionId, proof, requestId }),
      indicatorProgress(progressResponse),
    ]);
    const actual = await indicator(continued);
    assert.equal(continued.headers.get("X-QG-Live-Session"), null, "A successful append must reuse its worker");
    assert.equal(events.at(-1).status, "finished");
    assert.ok(events.some(event => event.status === "started" && event.label === "Reaction geometry • Bullish"));
    const completed = events.filter(event => event.completedStages !== undefined);
    assert.deepEqual(completed.map(event => event.completedStages), [1, 2, 3, 4, 5]);
    assert.ok(completed.every(event => event.totalStages === 6));
    const expected = await indicator(await server.post("", { ...request, id: updated.file.id, to: Math.floor(updated.file.to / 30) * 30 }));
    assert.deepEqual(actual, expected);
    const reportId = continued.headers.get("X-QG-Calculation-Id");
    const report = await server.getReport(reportId);
    const review = await report.json();
    assert.equal(report.status, 200);
    assert.equal(review.snapshot.calculation.calculationId, reportId);
    const { timings, ...reviewed } = review.payload;
    assert.deepEqual(reviewed, actual);
  } finally {
    if (server) await server.stop();
    assert.equal(path.dirname(stateRoot), directory);
    await fs.rm(stateRoot, { recursive: true, force: true });
  }
});
