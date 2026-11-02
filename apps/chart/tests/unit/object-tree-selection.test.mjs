import test from "node:test";
import assert from "node:assert/strict";
import { partitionObjectTreeSelection } from "../../src/chart/object-tree-selection.js";

function legacy(selected, drawings, map) {
  return {
    manualIds: selected.filter((id) => drawings.some((drawing) => drawing.id === id)),
    indicatorIds: selected.filter((id) => map.has(id)),
  };
}

test("selection partition preserves source ordering, repeated IDs and dual ownership", () => {
  const drawings = [{ id: "d2" }, { id: "d1" }, { id: "shared" }];
  const indicators = new Map([["i1", {}], ["shared", {}]]);
  const selections = [
    ["d1", "i1", "missing", "shared", "d1", "d2"],
    ["shared", "shared"], [],
    ["missing", "i1", "i1"],
  ];
  for (const selected of selections) {
    assert.deepEqual(partitionObjectTreeSelection(selected, drawings, indicators), legacy(selected, drawings, indicators));
  }
});

test("selection partition reads current drawing references each call and does not modify inputs", () => {
  const drawings = [{ id: "a" }];
  const map = new Map([["i", {}]]);
  const selected = Object.freeze(["a", "i"]);
  const before = partitionObjectTreeSelection(selected, drawings, map);
  assert.deepEqual(before, { manualIds: ["a"], indicatorIds: ["i"] });
  drawings[0] = { id: "b" };
  assert.deepEqual(partitionObjectTreeSelection(selected, drawings, map), { manualIds: [], indicatorIds: ["i"] });
});
