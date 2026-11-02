import assert from "node:assert/strict";
import { performance } from "node:perf_hooks";
import { partitionObjectTreeSelection } from "../../src/chart/object-tree-selection.js";

const drawings = Array.from({ length: 20_000 }, (_, i) => ({ id: "manual:" + i }));
const indicators = new Map(Array.from({ length: 10_000 }, (_, i) => ["indicator:" + i, {}]));
const selected = Array.from({ length: 800 }, (_, i) => i % 3 === 0 ? "indicator:" + i : "manual:" + (i * 11));
function previous() {
  return {
    manualIds: selected.filter((id) => drawings.some((drawing) => drawing.id === id)),
    indicatorIds: selected.filter((id) => indicators.has(id)),
  };
}
function next() {
  return partitionObjectTreeSelection(selected, drawings, indicators);
}
assert.deepEqual(previous(), next());
function measure(label, fn) {
  const samples = [];
  for (let i = 0; i < 7; i++) {
    globalThis.gc?.();
    const start = performance.now();
    const result = fn();
    assert.ok(result.manualIds.length > 0);
    samples.push(Number((performance.now() - start).toFixed(3)));
  }
  return { label, medianMs: [...samples].sort((a, b) => a - b)[3], samples };
}
console.log(JSON.stringify({
  kind: "object-tree-multi-select", drawings: drawings.length, selected: selected.length,
  measurements: [measure("legacy_repeated_some", previous), measure("transient_set", next)],
  note: "Same-process synthetic presentation microbenchmark, not a trading/Engine output benchmark.",
}, null, 2));
