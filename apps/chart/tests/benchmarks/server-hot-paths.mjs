// Standalone reproducible infrastructure benchmark. Not a correctness oracle.
// Run: node --expose-gc tests/benchmarks/server-hot-paths.mjs
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { performance } from "node:perf_hooks";

import { createCalculationCoordinator } from "../../server/calculation-coordinator.js";
import { createRawResourceStore } from "../../server/raw-resource-store.js";

const fixtureLength = 40_000;
const queueLength = 20_000;
const iterations = 5;

function median(samples) {
  const values = [...samples].sort((a, b) => a - b);
  return values[Math.floor(values.length / 2)];
}

async function measure(name, operation) {
  const samples = [];
  for (let i = 0; i < iterations; i++) {
    globalThis.gc?.();
    const start = performance.now();
    await operation();
    samples.push(Number((performance.now() - start).toFixed(3)));
  }
  return { name, medianMs: median(samples), samplesMs: samples };
}

async function benchmarkQueue() {
  let release;
  const blocked = new Promise((resolve) => { release = resolve; });
  const coordinator = createCalculationCoordinator({ maxActive: 1 });
  const first = coordinator.run("blocking", () => blocked);
  const queued = [];
  for (let i = 0; i < queueLength; i++) {
    queued.push(coordinator.run(`job-${i}`, () => i));
  }
  assert.deepEqual(coordinator.stats(), { active: 1, pending: queueLength, inFlight: queueLength + 1 });
  release("ok");
  const result = await Promise.all([first, ...queued]);
  assert.equal(result[0], "ok");
  assert.equal(result[1], 0);
  assert.equal(result.at(-1), queueLength - 1);
  assert.deepEqual(coordinator.stats(), { active: 0, pending: 0, inFlight: 0 });
}

function buildFixture() {
  const start = 1_700_000_000;
  return Array.from({ length: fixtureLength }, (_, index) => ({
    time: start + index * 5, open: 10, high: 11, low: 9, close: 10,
  }));
}

async function main() {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), "tradingbot-phase2-bench-"));
  try {
    const store = createRawResourceStore({ rootDir: directory });
    const candles = buildFixture();
    const stored = store.write({ broker: "BENCH", symbol: "PAIR", timeframe: "5S", candles });
    const raw = await measure("raw_read_parse_validate", () => {
      const parsed = store.read(stored.id);
      assert.equal(parsed.length, fixtureLength);
      assert.equal(parsed.at(-1).time, candles.at(-1).time);
    });
    const queue = await measure("fifo_queue_drain", benchmarkQueue);
    console.log(JSON.stringify({
      kind: "TradingBot non-engine hot-path benchmark",
      fixtureLength, queueLength, iterations,
      measurements: [raw, queue],
      note: "Times are runner-local; compare only similar runners and retain full samples. No market/Engine output is benchmarked.",
    }, null, 2));
  } finally {
    fs.rmSync(directory, { recursive: true, force: true });
  }
}

await main();
