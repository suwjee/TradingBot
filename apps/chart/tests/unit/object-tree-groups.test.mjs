import test from "node:test";
import assert from "node:assert/strict";
import { groupDrawingsForTree } from "../../src/chart/object-tree-groups.js";

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
