import test from "node:test";
import assert from "node:assert/strict";
import { collectProjectedStrokePoints } from "../../src/drawings/stroke-projection.js";

function priorImplementation(drawing, project, valid) {
  const points = (drawing.points || []).map(project).filter(valid);
  if (drawing.type === "path" && drawing.preview) {
    const preview = project(drawing.preview);
    if (valid(preview)) points.push(preview);
  }
  return points;
}

test("brush and path points preserve strict prior map/filter output order and preview policy", () => {
  const project = (p) => p == null ? null : ({ x: p.time * 2, y: p.price * 4 });
  const valid = (p) => p && p.x != null && p.y != null;
  const examples = [
    { type: "brush", points: [] },
    { type: "path", points: [], preview: { time: 5, price: 3 } },
    { type: "brush", points: [null, { time: 1, price: 2 }, undefined, { time: 2, price: 3 }] },
    { type: "path", points: [null, { time: 1, price: 2 }, null], preview: { time: 4, price: 9 } },
    { type: "path", points: [null, { time: 1, price: 2 }, null], preview: false },
    { type: "path", points: [null, { time: 1, price: 2 }, null], preview: null },
    { type: "brush", points: [], preview: { time: 5, price: 6 } },
  ];
  for (const drawing of examples) {
    assert.deepEqual(collectProjectedStrokePoints(drawing, project, valid), priorImplementation(drawing, project, valid));
  }
});

test("stroke projection preserves map callback order and skips sparse positions", () => {
  const points = new Array(7);
  points[0] = { x: 0 };
  points[3] = { x: 3 };
  points[6] = { x: 6 };
  const before = [], after = [];
  const oldProject = (point, index, collection) => {
    before.push([index, collection === points]);
    return point?.x ?? null;
  };
  const newProject = (point, index, collection) => {
    after.push([index, collection === points]);
    return point?.x ?? null;
  };
  const drawing = { type: "brush", points };
  const valid = (value) => value != null;
  assert.deepEqual(collectProjectedStrokePoints(drawing, newProject, valid), priorImplementation(drawing, oldProject, valid));
  assert.deepEqual(after, before);
  assert.deepEqual(after, [[0, true], [3, true], [6, true]]);
});

test("selected path handles use the same projected point references and optional preview", () => {
  const drawing = {
    type: "path", locked: false,
    points: [{ x: 1 }, { x: 2 }, { x: 3 }],
    preview: { x: 4 },
  };
  let calls = 0;
  const project = (point) => { calls++; return { x: point.x, y: 20 }; };
  const result = collectProjectedStrokePoints(drawing, project, (p) => Boolean(p?.x));
  assert.equal(calls, 4);
  assert.deepEqual(result.map((p) => p.x), [1, 2, 3, 4]);
  assert.deepEqual(drawing.points.map((p) => p.x), [1, 2, 3]);
});
