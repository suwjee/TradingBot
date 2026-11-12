import assert from "node:assert/strict";
import test from "node:test";
import { createLiveEngineSessions, startLiveEngineWorker } from "../../server/live-engine-sessions.js";

const indicator = marker => ({ timeframe: 30, directions: { bullish: { marker } } });
const seedArgs = { chartId: "chart", sourceFingerprint: "engine", request: { from: 100 } };

function fixture(t, options = {}) {
  const sessions = createLiveEngineSessions(options);
  t.after(sessions.close);
  let closes = 0;
  const paths = [];
  const worker = (ready = true) => ({
    seed: Promise.resolve({ type: "seed", payload: indicator("seed"), ready }),
    async update(path) { paths.push(path); return indicator(path); },
    close() { closes += 1; },
  });
  return { sessions, paths, worker, get closes() { return closes; } };
}

function snapshot(sessionId, overrides = {}) {
  return { sessionId, chartId: "chart", sourceFingerprint: "engine",
    rawSha256: "digest", data: "current.json", ...overrides };
}

const publishPayload = (payload, request) => ({ payload, request });
const validate = async () => {};
const defaultHooks = { validate, publish: publishPayload };

test("an unsupported seed returns its ordinary result without issuing a live token", async t => {
  const f = fixture(t);
  const seed = await f.sessions.seed(seedArgs, () => f.worker(false));
  assert.deepEqual(seed, { payload: indicator("seed"), sessionId: null });
  assert.equal(f.closes, 1);
});

test("a token is scoped to the same chart and Engine fingerprint", async t => {
  const f = fixture(t);
  const { sessionId } = await f.sessions.seed(seedArgs, f.worker);
  assert.match(sessionId, /^[a-f0-9]{32}$/);
  await assert.rejects(f.sessions.advance(snapshot(sessionId, { chartId: "other" }), defaultHooks), { status: 410 });
  assert.equal(f.closes, 0);
  await assert.rejects(f.sessions.advance(snapshot(sessionId, { sourceFingerprint: "different" }), defaultHooks), { status: 409 });
  await assert.rejects(f.sessions.advance(snapshot(sessionId), defaultHooks), { status: 410 });
  assert.equal(f.closes, 1);
  assert.deepEqual(f.paths, []);
});

test("a same-RAW retry replays the complete response without advancing the worker or republishing", async t => {
  const f = fixture(t);
  const { sessionId } = await f.sessions.seed(seedArgs, f.worker);
  let validated = 0, published = 0;
  const hooks = { validate: async () => { validated += 1; }, publish: (...args) => {
    published += 1;
    return publishPayload(...args);
  } };
  const first = await f.sessions.advance(snapshot(sessionId), hooks);
  const replay = await f.sessions.advance(snapshot(sessionId), hooks);
  assert.equal(replay, first);
  assert.equal(replay.payload.directions.bullish.marker, "current.json");
  assert.equal(replay.request.from, 100);
  assert.deepEqual(f.paths, ["current.json"]);
  assert.equal(published, 1);
  assert(validated >= 3);
});

test("a failed report write can retry with the same result without rerunning Engine", async t => {
  const f = fixture(t);
  const { sessionId } = await f.sessions.seed(seedArgs, f.worker);
  await assert.rejects(f.sessions.advance(snapshot(sessionId), {
    validate, publish: () => { throw new Error("Could not write report"); },
  }), /Could not write report/);
  const result = await f.sessions.advance(snapshot(sessionId), defaultHooks);
  assert.equal(result.payload.directions.bullish.marker, "current.json");
  assert.deepEqual(f.paths, ["current.json"]);
});

test("a transient RAW race retains the same Engine checkpoint for retry", async t => {
  const f = fixture(t);
  let calls = 0;
  const { sessionId } = await f.sessions.seed(seedArgs, () => ({
    ...f.worker(),
    async update(_path, sha256) {
      assert.equal(sha256, "digest");
      if (++calls === 1) throw Object.assign(new Error("RAW changed"), { code: "RAW_RETRY" });
      return indicator("accepted");
    },
  }));
  await assert.rejects(f.sessions.advance(snapshot(sessionId), defaultHooks), { code: "RAW_RETRY" });
  assert.equal((await f.sessions.advance(snapshot(sessionId), defaultHooks)).payload.directions.bullish.marker, "accepted");
  assert.equal(f.closes, 0);
});

test("overlapping advances are serialized and identical requests share a result", async t => {
  const f = fixture(t);
  let complete;
  const { sessionId } = await f.sessions.seed(seedArgs, () => ({
    ...f.worker(),
    update: () => new Promise(resolve => { complete = resolve; }),
  }));
  const first = f.sessions.advance(snapshot(sessionId), defaultHooks);
  const same = f.sessions.advance(snapshot(sessionId), defaultHooks);
  await assert.rejects(f.sessions.advance(snapshot(sessionId, { rawSha256: "other" }), defaultHooks), { status: 429 });
  complete(indicator("done"));
  assert.equal(await first, await same);
});

test("bounded sessions evict idle workers and expired checkpoints cannot continue", async t => {
  let now = 0;
  const f = fixture(t, { maxSessions: 1, idleTtlMs: 1_000, now: () => now });
  const first = await f.sessions.seed(seedArgs, f.worker);
  const second = await f.sessions.seed(seedArgs, f.worker);
  assert.equal(f.closes, 1);
  await assert.rejects(f.sessions.advance(snapshot(first.sessionId), defaultHooks), { status: 410 });
  now = 1001;
  await assert.rejects(f.sessions.advance(snapshot(second.sessionId), defaultHooks), { status: 410 });
  assert.equal(f.closes, 2);
});

test("an active market can keep its checkpoint while no candles arrive", async t => {
  let now = 0;
  const f = fixture(t, { idleTtlMs: 1_000, now: () => now });
  const { sessionId } = await f.sessions.seed(seedArgs, f.worker);
  now = 900;
  f.sessions.keepAlive(snapshot(sessionId));
  now = 1500;
  assert.doesNotThrow(() => f.sessions.keepAlive(snapshot(sessionId)));
  assert.deepEqual(f.paths, []);
  now = 2501;
  assert.throws(() => f.sessions.keepAlive(snapshot(sessionId)), { status: 410 });
});

test("a child sends a JSON-line seed and accepts exactly one absolute RAW update argument", async t => {
  const source = `
    const emit = payload => console.log(JSON.stringify(payload));
    emit({ type: "seed", ready: true, payload: { directions: {} } });
    const input = require("node:readline").createInterface({ input: process.stdin });
    input.on("line", line => {
      const request = JSON.parse(line);
      emit({ type: "update", payload: { directions: {}, data: request.data } });
    });
  `;
  const worker = startLiveEngineWorker({ command: process.execPath, args: ["-e", source] });
  t.after(worker.close);
  assert.equal((await worker.seed).ready, true);
  const result = await worker.update("X:/current RAW.json");
  assert.equal(result.data, "X:/current RAW.json");
});
