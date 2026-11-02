import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

import { createCalculationCoordinator } from "../../server/calculation-coordinator.js";
import { createRawResourceStore } from "../../server/raw-resource-store.js";

function sample(time, price = 10) {
  return { time, open: price, high: price + 1, low: price - 1, close: price };
}

test("queued calculations preserve FIFO order and exact results under backlog pressure", async () => {
  const coordinator = createCalculationCoordinator({ maxActive: 1 });
  const numberOfJobs = 4000;
  let release;
  const block = new Promise((resolve) => { release = resolve; });
  const active = coordinator.run("blocked", () => block);
  const ordering = [];
  const work = Array.from({ length: numberOfJobs }, (_, index) => coordinator.run(`queued-${index}`, async () => {
    ordering.push(index);
    return index;
  }));
  const duplicate = coordinator.run("queued-1234", () => {
    throw new Error("Duplicate queued key must not execute twice.");
  });
  assert.deepEqual(coordinator.stats(), { active: 1, pending: numberOfJobs, inFlight: numberOfJobs + 1 });
  release("finished");
  const values = await Promise.all([active, ...work, duplicate]);
  assert.equal(values[0], "finished");
  assert.deepEqual(values.slice(1, -1), Array.from({ length: numberOfJobs }, (_, i) => i));
  assert.deepEqual(ordering, Array.from({ length: numberOfJobs }, (_, i) => i));
  assert.equal(values.at(-1), 1234);
  assert.deepEqual(coordinator.stats(), { active: 0, pending: 0, inFlight: 0 });
});

test("closing a large pending queue rejects every job and prevents late execution", async () => {
  const coordinator = createCalculationCoordinator();
  let activeSignal;
  const active = coordinator.run("active", (_publish, signal) => {
    activeSignal = signal;
    return new Promise((_resolve, reject) => {
      signal.addEventListener("abort", () => reject(new Error("aborted")), { once: true });
    });
  });
  let started = 0;
  const queued = Array.from({ length: 4000 }, (_, index) => coordinator.run(`pending-${index}`, () => {
    started++;
    return index;
  }));
  assert.equal(coordinator.stats().pending, 4000);
  coordinator.close();
  assert.equal(activeSignal.aborted, true);
  const results = await Promise.allSettled([active, ...queued]);
  assert.deepEqual(results.map((r) => r.status), Array(4001).fill("rejected"));
  assert.equal(started, 0);
  assert.deepEqual(coordinator.stats(), { active: 0, pending: 0, inFlight: 0 });
});

test("RAW validation preserves numeric coercion and rejects malformed schema, OHLC and chronology", (t) => {
  const rootDir = fs.mkdtempSync(path.join(os.tmpdir(), "tradingbot-raw-validation-"));
  t.after(() => fs.rmSync(rootDir, { recursive: true, force: true }));
  const store = createRawResourceStore({ rootDir });
  const first = {
    time: "1700000000", open: "10", high: "11", low: "9", close: "10",
  };
  const valid = [first, sample(1700000005)];
  const saved = store.write({ broker: "FIXTURE", symbol: "VALID", timeframe: "5S", candles: valid });
  assert.deepEqual(store.read(saved.id), valid);
  const cases = [
    [sample(1700000000), { ...sample(1700000005), extra: 1 }],
    [sample(1700000000), { ...sample(1700000005), high: 9 }],
    [sample(1700000000), { ...sample(1700000005), low: 11 }],
    [sample(1700000000), { ...sample(1700000005), close: "NaN" }],
    [sample(1700000000), sample(1700000000)],
    [sample(1700000005), sample(1700000000)],
    [sample(1700000000), { ...sample(1700000005), time: 1700000005.5 }],
  ];
  for (const candles of cases) {
    assert.throws(() => store.write({ broker: "FIXTURE", symbol: "INVALID", timeframe: "5S", candles }), /RAW candle 2/);
  }
  assert.equal(store.list().length, 1);
});
