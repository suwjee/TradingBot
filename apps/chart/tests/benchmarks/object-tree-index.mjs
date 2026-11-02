import assert from "node:assert/strict";
import { performance } from "node:perf_hooks";
import { groupDrawingsForTree } from "../../src/chart/object-tree-groups.js";

// Deterministic synthetic UI indexing work. The original unmodified Chart
// implementation filters the entire drawing array for each folder.
const folderCount = 80, drawingCount = 30_000, repetitions = 7;
const folders = [{ id: "manual-unfiled" }, ...Array.from({ length: folderCount - 1 }, (_, i) => ({ id: `folder-${i}` }))];
const names = { line: "Line", rect: "Rectangle", long: "Long Position" };
const drawings = Array.from({ length: drawingCount }, (_, i) => ({
  id: `drawing-${i}`,
  folderId: i % 5 === 0 ? undefined : `folder-${i % (folderCount - 1)}`,
  type: ["line", "rect", "long"][i % 3],
}));

function legacyGroup(query) {
  const map = new Map();
  for (const folder of folders) {
    map.set(folder.id, drawings.filter((drawing) =>
      (drawing.folderId || "manual-unfiled") === folder.id
      && (!query || `${names[drawing.type] || drawing.type}`.toLowerCase().includes(query))));
  }
  return map;
}

function measure(label, work) {
  const samples = [];
  for (let i = 0; i < repetitions; i++) {
    globalThis.gc?.();
    const started = performance.now();
    const result = work();
    assert.equal(result.size, folderCount);
    samples.push(Number((performance.now() - started).toFixed(3)));
  }
  const ordered = [...samples].sort((a, b) => a - b);
  return { label, medianMs: ordered[Math.floor(ordered.length / 2)], samplesMs: samples };
}
for (const query of ["", "long"]) {
  const expected = legacyGroup(query);
  const actual = groupDrawingsForTree(drawings, folders, query, names);
  for (const folder of folders) assert.deepEqual(actual.get(folder.id), expected.get(folder.id));
}
const baseline = measure("original_repeated_filter", () => legacyGroup(""));
const candidate = measure("transient_group_index", () => groupDrawingsForTree(drawings, folders, "", names));
console.log(JSON.stringify({ type: "chart-object-tree-index", folderCount, drawingCount, repetitions, measurements: [baseline, candidate], note: "Synthetic runner-local microbenchmark; no Engine/RAW files or full browser painting included." }, null, 2));
