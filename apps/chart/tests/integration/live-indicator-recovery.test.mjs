import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { once } from "node:events";
import fs from "node:fs/promises";
import path from "node:path";
import { createInterface } from "node:readline";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { createRawResourceStore } from "../../server/raw-resource-store.js";

const chart = fileURLToPath(new URL("../../", import.meta.url));
const startVite = `
  import { createServer } from "vite";
  const server = await createServer({ configLoader: "native", server: { port: 0, host: "127.0.0.1", ws: false } });
  await server.listen();
  console.log("TEST_PORT:" + server.httpServer.address().port);
  process.stdin.resume();
  process.stdin.once("end", () => server.close());
`;

async function launch(stateRoot) {
  const child = spawn(process.execPath, ["--input-type=module", "-e", startVite], {
    cwd: chart, env: { ...process.env, TRADINGBOT_LOCAL_STATE_ROOT: stateRoot }, windowsHide: true,
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
    return { stop, post: (route, body) => fetch(`http://127.0.0.1:${port}/api/reactions${route}`, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body), signal: AbortSignal.timeout(90_000),
    }) };
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

test("restart recovers manual and advanced live checkpoints across RAW renames", {
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
  const initialCount = rows.length - 50;
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
    const missing = await server.post("/continue", { id: raw.id, chartId, sessionId: null });
    assert.equal(missing.status, 400);
    const invalid = await server.post("/continue", { id: raw.id, chartId, sessionId: null, calculationId: "../30s/bullish/1-2--0123456789abcdef.json" });
    assert.equal(invalid.status, 410);
    const checkpoints = [];
    for (const request of requests) {
      const response = await server.post("", { ...request, id: raw.id, liveSession: true });
      await indicator(response);
      const sessionId = response.headers.get("X-QG-Live-Session");
      const calculationId = response.headers.get("X-QG-Calculation-Id");
      assert(sessionId && calculationId);
      checkpoints.push({ sessionId, calculationId });
    }
    for (const count of [initialCount + 13, initialCount + 26]) {
      const oldId = raw.id;
      raw = await store.appendLatest(raw, rows.slice(raw.count, count), 5, store.version(raw.id), new AbortController().signal);
      assert.notEqual(raw.id, oldId);
      assert.equal(raw.chartId, chartId);
      await restart();
      for (const [index, checkpoint] of checkpoints.entries()) {
        const response = await server.post("/continue", { id: raw.id, chartId, ...checkpoint });
        const actual = await indicator(response);
        const sessionId = response.headers.get("X-QG-Live-Session");
        assert(sessionId && sessionId !== checkpoint.sessionId);
        checkpoint.sessionId = sessionId;
        checkpoint.calculationId = response.headers.get("X-QG-Calculation-Id");
        const to = Math.floor(raw.to / 30) * 30;
        const expected = await indicator(await server.post("", { ...requests[index], id: raw.id, to }));
        assert.deepEqual(actual, expected);
        assert.deepEqual(await indicator(await server.post("/continue", { id: raw.id, chartId, ...checkpoint })), actual);
      }
    }
    await restart();
    const idle = await server.post("/continue", { id: raw.id, chartId, ...checkpoints[0], keepAlive: true });
    await indicator(idle);
    const idleSession = idle.headers.get("X-QG-Live-Session");
    assert(idleSession && idleSession !== checkpoints[0].sessionId);
    const ping = await server.post("/continue", { id: raw.id, chartId, sessionId: idleSession, keepAlive: true });
    assert.equal(ping.status, 204);
    const modified = { ...rows[1], close: rows[1].low };
    if (modified.close === rows[1].close) modified.close = rows[1].high;
    assert.notEqual(modified.close, rows[1].close);
    await fs.writeFile(raw.dataPath, JSON.stringify([rows[0], modified, ...rows.slice(2, raw.count)]));
    await restart();
    const rewrite = await server.post("/continue", { id: raw.id, chartId, ...checkpoints[0] });
    const problem = await rewrite.json();
    assert.equal(rewrite.status, 409, JSON.stringify(problem));
    assert.equal(problem.code, "RAW_CHANGED");
  } finally {
    if (server) await server.stop();
    assert.equal(path.dirname(stateRoot), directory);
    await fs.rm(stateRoot, { recursive: true, force: true });
  }
});
