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
  const server = await createServer({ configLoader: "native", server: { port: 0, host: "127.0.0.1", ws: false } });
  await server.listen();
  console.log("TEST_PORT:" + server.httpServer.address().port);
  process.stdin.resume();
  process.stdin.once("end", () => server.close());
`;

async function launch(stateRoot, marketFixture = "") {
  const child = spawn(process.execPath, ["--input-type=module", "-e", startVite], {
    cwd: chart, env: { ...process.env, TRADINGBOT_LOCAL_STATE_ROOT: stateRoot, TRADINGBOT_TEST_MARKET: marketFixture }, windowsHide: true,
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
    const post = (route, body) => fetch(`http://127.0.0.1:${port}/api${route}`, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body), signal: AbortSignal.timeout(90_000),
    });
    return { stop, getReport: id => report(id, "GET"), saveReport: id => report(id, "POST"),
      post: (route, body) => post(`/reactions${route}`, body),
      update: body => post("/candle-files/realtime", body) };
  }
  await stop();
  assert.fail(`Vite did not start. ${stderr}`);
}

async function indicator(response) {
  const payload = await response.json();
  assert.equal(response.status, 200, JSON.stringify(payload));
  const { timings, ...output } = payload;
  return output;
}

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
        assert.deepEqual(await indicator(await server.post("/continue", { id: raw.id, chartId, ...checkpoint })), actual);
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
    const idle = await server.post("/continue", { id: raw.id, chartId, ...checkpoints[0], keepAlive: true });
    await indicator(idle);
    checkpoints[0].sessionId = idle.headers.get("X-QG-Live-Session");
    const ping = await server.post("/continue", { id: raw.id, chartId, ...checkpoints[0], keepAlive: true });
    assert.equal(ping.status, 204);

    const modified = { ...rows[1], close: rows[1].low };
    if (modified.close === rows[1].close) modified.close = rows[1].high;
    assert.notEqual(modified.close, rows[1].close);
    await fs.writeFile(raw.dataPath, JSON.stringify([rows[0], modified, ...rows.slice(2, raw.count)]));
    const rebuild = await server.post("/continue", { id: raw.id, chartId, ...checkpoints[0] });
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
    assert.deepEqual(updated.candles, rows.slice(215));
    const continued = await server.post("/continue", { id: updated.file.id, chartId: raw.chartId, tabId: request.tabId, sessionId, proof });
    const actual = await indicator(continued);
    assert.equal(continued.headers.get("X-QG-Live-Session"), null, "A successful append must reuse its worker");
    const expected = await indicator(await server.post("", { ...request, id: updated.file.id, to: Math.floor(updated.file.to / 30) * 30 }));
    assert.deepEqual(actual, expected);
  } finally {
    if (server) await server.stop();
    assert.equal(path.dirname(stateRoot), directory);
    await fs.rm(stateRoot, { recursive: true, force: true });
  }
});
