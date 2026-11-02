import assert from "node:assert/strict";
import { performance } from "node:perf_hooks";
import { groupDrawingsForTree, groupIndicatorRowsForTree } from "../../src/chart/object-tree-groups.js";

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

// Additional allocation-sensitive render traversal comparison. This measures
// iteration only (not canvas paint); drawOne is presentation-only.
const renderDrawings = drawings.map((drawing, index) => ({ ...drawing, hidden: index % 4 === 0 }));
const legacyVisible = () => {
  let sum = 0;
  renderDrawings.filter((drawing) => !drawing.hidden).forEach((drawing) => { sum += drawing.id.length; });
  return sum;
};
const directVisible = () => {
  let sum = 0;
  for (const drawing of renderDrawings) {
    if (drawing.hidden) continue;
    sum += drawing.id.length;
  }
  return sum;
};
const expectedVisible = legacyVisible();
assert.equal(expectedVisible, directVisible());
function measureTraversal(label, walk) {
  const samples = [];
  for (let i = 0; i < repetitions; i++) {
    globalThis.gc?.();
    const started = performance.now();
    assert.equal(walk(), expectedVisible);
    samples.push(Number((performance.now() - started).toFixed(3)));
  }
  return { label, medianMs: [...samples].sort((a, b) => a - b)[Math.floor(samples.length / 2)], samplesMs: samples };
}
const oldTraversal = measureTraversal("visible_drawings_filter_array", legacyVisible);
const newTraversal = measureTraversal("visible_drawings_direct_iteration", directVisible);
console.log(JSON.stringify({
  type: "chart-presentation-loop",
  folderCount, drawingCount, repetitions,
  measurements: [baseline, candidate, oldTraversal, newTraversal],
  note: "Synthetic same-run microbenchmark for indexing/iteration only; excludes canvas painting, full browser, Engine and RAW files.",
}, null, 2));

const indicatorObjects = Array.from({ length: 30_000 }, (_, index) => ({
  id: `indicator:${index % 2 ? "bullish" : "bearish"}:reaction:${index}`,
  name: index % 4 === 0 ? "Blue" : "Reaction",
  type: "indicator-reaction",
}));
const priorIndicators = () => {
  const visible = indicatorObjects.filter((item) => `${item.name} ${item.type}`.toLowerCase().includes("blue"));
  return { visible, byDirection: {
    bullish: visible.filter((item) => item.id.includes(":bullish:")),
    bearish: visible.filter((item) => item.id.includes(":bearish:")),
  } };
};
const nextIndicators = () => groupIndicatorRowsForTree(indicatorObjects, "blue");
assert.deepEqual(nextIndicators(), priorIndicators());
function timeValue(label, work) {
  const elapsed = [];
  for (let index = 0; index < repetitions; index++) {
    globalThis.gc?.();
    const started = performance.now();
    const result = work();
    assert.ok(result);
    elapsed.push(Number((performance.now() - started).toFixed(3)));
  }
  return { label, medianMs: [...elapsed].sort((a, b) => a - b)[Math.floor(repetitions / 2)], samplesMs: elapsed };
}
const oldIndicators = timeValue("indicator_original_filters", priorIndicators);
const groupedIndicators = timeValue("indicator_single_pass_groups", nextIndicators);

const allIds = drawings.slice(0, 8_000).map((item) => item.id);
const selectedIds = drawings.slice(0, 800).map((item) => item.id);
const priorSelection = () => allIds.filter((id) => selectedIds.includes(id));
const nextSelection = () => {
  const selected = new Set(selectedIds);
  return allIds.filter((id) => selected.has(id));
};
assert.deepEqual(nextSelection(), priorSelection());
const oldSelection = timeValue("tree_selection_array_includes", priorSelection);
const newSelection = timeValue("tree_selection_set_membership", nextSelection);
console.log(JSON.stringify({
  type: "chart-tree-indicator-selection",
  indicatorCount: indicatorObjects.length,
  selectionCandidates: allIds.length,
  selectedCount: selectedIds.length,
  repetitions,
  measurements: [oldIndicators, groupedIndicators, oldSelection, newSelection],
  note: "Same-run synthetic presentation-only comparison; no chart DOM/canvas paint or Engine behavior included.",
}, null, 2));
