import test from "node:test";
import assert from "node:assert/strict";
import { groupDrawingsForTree, groupIndicatorRowsForTree } from "../../src/chart/object-tree-groups.js";

const names = { line: "Line", long: "Long Position", rect: "Rectangle" };

function originalFilter(drawings, folder, query) {
  return drawings.filter((drawing) =>
    (drawing.folderId || "manual-unfiled") === folder.id &&
    (!query || `${names[drawing.type] || drawing.type}`.toLowerCase().includes(query)));
}

test("Object Tree grouping exactly preserves historical per-folder filter and order", () => {
  const folders = [
    { id: "manual-unfiled", name: "Drawings" },
    { id: "alpha" }, { id: "beta" }, { id: "alpha" },
    { id: "__proto__" }, { id: "empty" },
  ];
  const drawings = Array.from({ length: 180 }, (_, i) => ({
    id: `drawing-${i}`,
    type: ["line", "long", "rect", "custom"][i % 4],
    folderId: [undefined, "alpha", "beta", "orphan", "__proto__", ""][i % 6],
    hidden: i % 5 === 0,
  }));
  for (const query of ["", "line", "long", "custom", "position", "zz", "draw"]) {
    const groups = groupDrawingsForTree(drawings, folders, query, names);
    for (const folder of folders) {
      const expected = originalFilter(drawings, folder, query);
      assert.deepEqual(groups.get(folder.id), expected);
      assert.equal(groups.get(folder.id)?.every((item) => drawings.includes(item)), true);
    }
  }
});

test("Object Tree grouping never mutates the original drawing array or creates hidden folder entries", () => {
  const first = Object.freeze({ id: "a", folderId: "selected", type: "line" });
  const second = Object.freeze({ id: "b", folderId: "missing", type: "rect" });
  const drawings = Object.freeze([first, second]);
  const groups = groupDrawingsForTree(drawings, [{ id: "selected" }], "", names);
  assert.deepEqual([...groups.keys()], ["selected"]);
  assert.strictEqual(groups.get("selected")[0], first);
  assert.equal(groups.has("missing"), false);
  assert.strictEqual(drawings[0], first);
});

test("Object Tree grouping preserves numeric row indices within each folder", () => {
  const folders = [{ id: "manual-unfiled" }, { id: "a" }];
  const rows = [
    { id: "x", type: "line", folderId: "a" },
    { id: "y", type: "line" },
    { id: "z", type: "long", folderId: "a" },
  ];
  const groups = groupDrawingsForTree(rows, folders, "", names);
  assert.deepEqual(groups.get("a").map((item, index) => [item.id, index + 1]), [["x", 1], ["z", 2]]);
  assert.deepEqual(groups.get("manual-unfiled").map((item, index) => [item.id, index + 1]), [["y", 1]]);
});

test("one-pass indicator grouping matches independent legacy visibility and direction filters", () => {
  const items = [
    { id: "indicator:bullish:reaction:1", name: "Reaction 1", type: "indicator-reaction" },
    { id: "indicator:bearish:blue:4", name: "Blue", type: "indicator-blue" },
    { id: "indicator:bullish:bearish:shared:3", name: "Shared", type: "indicator-label" },
    { id: "indicator:neutral:line:8", name: "Neutral", type: "indicator-blue" },
    { id: "indicator:bullish:blue:9", name: "ABC", type: "indicator-blue" },
  ];
  for (const query of ["", "reaction", "blue", "sh", "AB", "none"]) {
    const normalized = query.toLowerCase();
    const expected = items.filter((item) => !normalized || `${item.name} ${item.type}`.toLowerCase().includes(normalized));
    const actual = groupIndicatorRowsForTree(items, normalized);
    assert.deepEqual(actual.visible, expected);
    for (const direction of ["bullish", "bearish"]) {
      assert.deepEqual(actual.byDirection[direction], expected.filter((item) => item.id.includes(`:${direction}:`)));
    }
    assert.strictEqual(actual.visible[0], expected[0]);
  }
});

test("Object Tree selection Set membership preserves Array#includes semantics for IDs", () => {
  const selected = ["first", "second", "first", NaN, -0, null];
  const selectedSet = new Set(selected);
  for (const id of ["first", "second", "third", NaN, +0, null, undefined]) {
    assert.equal(selectedSet.has(id), selected.includes(id));
  }
});

test("indicator Object Tree grouping skips sparse slots like the original Array#filter", () => {
  const objects = new Array(5);
  objects[1] = { id: "indicator:bullish:blue:1", name: "Blue", type: "indicator-blue" };
  objects[4] = { id: "indicator:bearish:reaction:2", name: "Reaction", type: "indicator-reaction" };
  const original = objects.filter((item) => Boolean(item));
  const grouped = groupIndicatorRowsForTree(objects);
  assert.deepEqual(grouped.visible, original);
  assert.deepEqual(grouped.byDirection.bullish, [objects[1]]);
  assert.deepEqual(grouped.byDirection.bearish, [objects[4]]);
});
