import test from "node:test";
import assert from "node:assert/strict";
import { clipHistoricalHitBoxes, clipHistoricalHitBoxesInPlace } from "../../src/chart/primary-structure.js";

function legacyClip(hits, right) {
  if (right < 0) return [];
  return hits.flatMap((hit) => {
    const clipped = { ...hit, clipRight: right };
    if (hit.shape === "rect") {
      if (hit.left >= right) return [];
      clipped.right = Math.min(hit.right, right);
    } else if (hit.shape === "point") {
      if (hit.x - (hit.radius || 12) >= right) return [];
    } else if (hit.shape === "line") {
      if (Math.min(hit.x1, hit.x2) >= right) return [];
      if (Math.max(hit.x1, hit.x2) > right) {
        const y = hit.y1 + (right - hit.x1) * (hit.y2 - hit.y1) / (hit.x2 - hit.x1);
        const end = hit.x1 > right ? "1" : "2";
        clipped[`x${end}`] = right;
        clipped[`y${end}`] = y;
      }
    }
    return [clipped];
  });
}
const hits = [
  { objectId: "a", shape: "rect", left: 20, right: 200, top: 10, bottom: 30 },
  { objectId: "b", shape: "rect", left: 100, right: 300, top: 10, bottom: 30 },
  { objectId: "c", shape: "line", x1: 10, y1: 1, x2: 170, y2: 9 },
  { objectId: "d", shape: "line", x1: 170, y1: 9, x2: 10, y2: 1 },
  { objectId: "e", shape: "line", x1: 100, y1: 9, x2: 100, y2: 1 },
  { objectId: "f", shape: "point", x: 95, y: 10, radius: 12 },
  { objectId: "g", shape: "point", x: 140, y: 10, radius: 12 },
  { objectId: "h", shape: "circle", x: 95, y: 50 },
  { objectId: "i", shape: "line", x1: -10, y1: 0, x2: 2, y2: 5 },
];

test("exported original clipping contract remains byte-equivalent for all historical boundary cases", () => {
  for (const right of [-1, 0, 20, 80, 100, 170, 1_000, NaN]) {
    assert.deepEqual(clipHistoricalHitBoxes(hits, right), legacyClip(hits, right));
  }
  const sparse = new Array(5);
  sparse[1] = hits[0]; sparse[4] = hits[2];
  assert.deepEqual(clipHistoricalHitBoxes(sparse, 110), legacyClip(sparse, 110));
});

test("in-place hitbox clipping exactly reproduces original splice+push semantics without mutating prefix", () => {
  const prefix = [{ objectId: "old-bullish", viewRevision: 12 }, { objectId: "old-bearish" }];
  for (const right of [-1, 0, 20, 100, 170, 1_000, NaN]) {
    const source = structuredClone(hits);
    const target = [...prefix, ...source];
    const expected = [...prefix, ...legacyClip(source, right)];
    assert.strictEqual(clipHistoricalHitBoxesInPlace(target, prefix.length, right), target);
    assert.deepEqual(target, expected);
    assert.strictEqual(target[0], prefix[0]);
    assert.strictEqual(target[1], prefix[1]);
    assert.deepEqual(source, hits);
    for (let i = prefix.length; i < target.length; i++)
      assert.notStrictEqual(target[i], source.find((x) => x.objectId === target[i].objectId));
  }
});

test("large hitbox segments avoid argument-spread limits while retaining all object identities", () => {
  const total = 150_000;
  const segment = Array.from({ length: total }, (_, index) => ({
    objectId: `indicator:bullish:blue:${index}`,
    shape: "line", x1: index % 250, x2: 450, y1: 2, y2: 20,
  }));
  const buffer = [{ objectId: "existing" }, ...segment];
  const original = [...segment];
  clipHistoricalHitBoxesInPlace(buffer, 1, 200);
  assert.equal(buffer.length, 1 + segment.filter((h) => h.x1 < 200).length);
  assert.equal(buffer[0].objectId, "existing");
  assert.equal(buffer[1].objectId, original[0].objectId);
  assert.notStrictEqual(buffer[1], original[0]);
  assert.equal(buffer.at(-1).clipRight, 200);
});

test("sparse segment preserves historical flatMap skipping missing entries", () => {
  const buffer = [{ id: "prefix" }, hits[0], , hits[2], , hits[7]];
  const result = [...buffer.slice(0, 1), ...legacyClip(buffer.slice(1), 125)];
  clipHistoricalHitBoxesInPlace(buffer, 1, 125);
  assert.deepEqual(buffer, result);
});
