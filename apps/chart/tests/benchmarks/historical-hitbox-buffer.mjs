import assert from "node:assert/strict";
import { performance } from "node:perf_hooks";
import { clipHistoricalHitBoxes, clipHistoricalHitBoxesInPlace } from "../../src/chart/primary-structure.js";

const count = 80_000, samples = 7, right = 250;
const hits = Array.from({ length: count }, (_, index) => ({
  objectId: "indicator:bullish:blue:" + index,
  shape: index % 3 === 0 ? "rect" : index % 3 === 1 ? "point" : "line",
  left: index % 300, right: (index % 300) + 70,
  x: index % 300, y: index % 100, radius: 12,
  x1: index % 320, y1: 20, x2: (index % 320) + 100, y2: 120,
}));
const prefix = [{ objectId: "prior-segment" }];
const small = hits.slice(0, 10_000);
const reference = [...prefix, ...clipHistoricalHitBoxes(small, right)];
const check = [...prefix, ...small];
clipHistoricalHitBoxesInPlace(check, prefix.length, right);
assert.deepEqual(check, reference);

function measure(label, fn) {
  const times = [];
  let maxHeapDeltaBytes = 0;
  for (let i = 0; i < samples; i++) {
    globalThis.gc?.();
    const beforeHeap = process.memoryUsage().heapUsed;
    const started = performance.now();
    const buffer = fn();
    times.push(Number((performance.now() - started).toFixed(3)));
    maxHeapDeltaBytes = Math.max(maxHeapDeltaBytes, process.memoryUsage().heapUsed - beforeHeap);
    assert.equal(buffer[0].objectId, "prior-segment");
  }
  return { label, medianMs: [...times].sort((a, b) => a - b)[Math.floor(samples / 2)], samplesMs: times, maxHeapDeltaBytes };
}
const legacy = measure("old_splice_flatMap_spread_10k", () => {
  const buffer = [...prefix, ...small];
  buffer.push(...clipHistoricalHitBoxes(buffer.splice(1), right));
  return buffer;
});
const optimized = measure("new_inplace_10k", () => {
  const buffer = [...prefix, ...small];
  clipHistoricalHitBoxesInPlace(buffer, 1, right);
  return buffer;
});
const large = measure("new_inplace_80k", () => {
  const buffer = [...prefix, ...hits];
  clipHistoricalHitBoxesInPlace(buffer, 1, right);
  return buffer;
});
console.log(JSON.stringify({
  type: "indicator-historical-hitboxes",
  samples, referenceBatch: small.length, stressBatch: hits.length,
  results: [legacy, optimized, large],
  warning: "Synthetic Node microbenchmark; heap deltas include GC/JIT effects, not a browser retained-heap measurement.",
}, null, 2));
