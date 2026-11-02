import assert from "node:assert/strict";
import { performance } from "node:perf_hooks";
import { representedOrderKeys } from "../../src/chart/indicator-order-keys.js";

const count = 48_000, samples = 7;
const group = { sZones: [], eZones: [], stopAlls: [] };
const lists = [group.sZones, group.eZones, group.stopAlls];
for (let index = 0; index < count; index++) {
  lists[index % 3].push({
    orderFirstIndex: index % 19_000, orderBreakIndex: (index + 6) % 19_000,
    calculationValid: index % 9 !== 0,
  });
}

function previous() {
  return new Set(
    [...(group.sZones || []), ...(group.eZones || []), ...(group.stopAlls || [])]
      .filter((item) => item.calculationValid !== false &&
        item.orderFirstIndex != null && item.orderBreakIndex != null)
      .map((item) => `${item.orderFirstIndex}:${item.orderBreakIndex}`),
  );
}
assert.deepEqual([...representedOrderKeys(group)], [...previous()]);
function measure(label, work) {
  const sampleTimes = [], heapDeltas = [];
  for (let iteration = 0; iteration < samples; iteration++) {
    globalThis.gc?.();
    const beforeHeap = process.memoryUsage().heapUsed;
    const started = performance.now();
    const result = work();
    sampleTimes.push(Number((performance.now() - started).toFixed(3)));
    heapDeltas.push(process.memoryUsage().heapUsed - beforeHeap);
    assert.ok(result.size > 0);
  }
  return {
    label, medianMs: [...sampleTimes].sort((a, b) => a - b)[Math.floor(samples / 2)],
    maxHeapDeltaBytes: Math.max(...heapDeltas), samplesMs: sampleTimes,
  };
}
const legacy = measure("legacy_concatenate_filter_map_set", previous);
const refactored = measure("single_pass_order_keys", () => representedOrderKeys(group));
console.log(JSON.stringify({
  type: "indicator-order-key-presentation", zoneCount: count, repetitions: samples,
  benchmarks: [legacy, refactored],
  caveat: "Node runner-local synthetic microbenchmark only; excludes browser rendering and genuine market RAW.",
}, null, 2));
