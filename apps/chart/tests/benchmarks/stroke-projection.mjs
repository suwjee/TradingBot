import assert from "node:assert/strict";
import { performance } from "node:perf_hooks";
import { collectProjectedStrokePoints } from "../../src/drawings/stroke-projection.js";

// Draw-operation projection only; deliberately excludes market chronology and Canvas paint.
const samples = 9, count = 50_000;
const drawing = {
  type: "path",
  points: Array.from({ length: count }, (_, index) => index % 13 === 0 ? null : ({ time: 1_700_000_000 + index * 5, price: 100 + index / 1_000 })),
  preview: { time: 1_700_400_000, price: 105 },
};
const project = (p) => p ? { x: p.time / 5, y: p.price * 3 } : null;
const valid = (p) => p && p.x != null && p.y != null;
const legacy = () => {
  const pts = (drawing.points || []).map(project).filter(valid);
  if (drawing.type === "path" && drawing.preview) {
    const preview = project(drawing.preview);
    if (valid(preview)) pts.push(preview);
  }
  return pts;
};
const candidate = () => collectProjectedStrokePoints(drawing, project, valid);

function measure(label, run) {
  const times = [];
  for (let i = 0; i < samples; i++) {
    globalThis.gc?.();
    const start = performance.now();
    const projected = run();
    const last = projected.at(-1);
    assert.equal(last?.x, drawing.preview.time / 5);
    times.push(Number((performance.now() - start).toFixed(3)));
  }
  const sorted = [...times].sort((a, b) => a - b);
  return { label, medianMs: sorted[Math.floor(sorted.length / 2)], samplesMs: times };
}
assert.deepEqual(candidate(), legacy());
const first = measure("original_map_filter", legacy);
const second = measure("single_pass_projection", candidate);
console.log(JSON.stringify({
  type: "drawing-stroke-projection",
  points: count,
  samples,
  measurements: [first, second],
  note: "Same-run synthetic microbenchmark; not a real-time frame-rate, GPU, or workstation RAM measurement.",
}, null, 2));
