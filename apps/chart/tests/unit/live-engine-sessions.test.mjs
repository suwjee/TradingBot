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
    async update(bytes) { const marker = bytes.toString(); paths.push(marker); return indicator(marker); },
    close() { closes += 1; },
  });
  return { sessions, paths, worker, get closes() { return closes; } };
}

function snapshot(sessionId, overrides = {}) {
  return { sessionId, chartId: "chart", sourceFingerprint: "engine",
    rawSha256: "digest", data: "current.json", ...overrides };
}

const publishPayload = (payload, request) => ({ payload, request });
const validate = async includeBytes => includeBytes ? Buffer.from("current.json") : undefined;
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
  const hooks = { validate: async includeBytes => { validated += 1; return validate(includeBytes); }, publish: (...args) => {
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
    async update(_bytes, sha256) {
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

test("a worker update sends the exact RAW bytes and digest without a file path", async t => {
  const source = `
    const emit = payload => console.log(JSON.stringify(payload));
    emit({ type: "seed", ready: true, payload: { directions: {} } });
    let input = Buffer.alloc(0);
    process.stdin.on("data", chunk => {
      input = Buffer.concat([input, chunk]);
      const newline = input.indexOf(10);
      if (newline < 0) return;
      const header = JSON.parse(input.subarray(0, newline));
      if (!Number.isSafeInteger(header.bytes)) process.exit(1);
      if (input.length - newline - 1 < header.bytes) return;
      const end = newline + 1 + header.bytes;
      const raw = input.subarray(newline + 1, end).toString("hex");
      input = input.subarray(end);
      emit({ type: "update", payload: { directions: {}, header, raw } });
    });
  `;
  const worker = startLiveEngineWorker({ command: process.execPath, args: ["-e", source] });
  t.after(worker.close);
  assert.equal((await worker.seed).ready, true);
  await assert.rejects(worker.update("X:/current RAW.json", "a".repeat(64)), TypeError);
  const raw = Buffer.from('\ufeff[\r\n {"close":1.00,"note":"نفت"}\r\n]\n');
  for (const bytes of [raw, Buffer.from("[1]")]) {
    const sha256 = "a".repeat(64);
    const result = await worker.update(bytes, sha256);
    assert.deepEqual(result.header, { bytes: bytes.length, sha256 });
    assert.equal(result.raw, bytes.toString("hex"));
  }
});
