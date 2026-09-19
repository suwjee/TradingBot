import test from "node:test";
import assert from "node:assert/strict";

import {
  coordinateToRawTime,
  createViewAnchorCache,
  rawIndexAtTime,
  rawTimeToCoordinate,
  selectDensityMode,
} from "../src/chart/view-transform.js";

const rows = Array.from({ length: 11 }, (_, index) => ({ time: 100 + index * 10 }));
const anchors = [
  { rawIndex: 0, coordinate: 20 },
  { rawIndex: 5, coordinate: 220 },
  { rawIndex: 10, coordinate: 420 },
];

test("omitted raw timestamps interpolate to stable chart coordinates", () => {
  assert.equal(rawTimeToCoordinate(rows, 130, anchors), 140);
  assert.equal(rawTimeToCoordinate(rows, 175, anchors), 320);
  assert.equal(coordinateToRawTime(rows, 140, anchors), 130);
  assert.equal(coordinateToRawTime(rows, 320, anchors), 180);
});

test("coordinate transforms extrapolate at the visible edges", () => {
  assert.equal(rawTimeToCoordinate(rows, 90, anchors), -20);
  assert.equal(rawTimeToCoordinate(rows, 210, anchors), 460);
});

test("raw-time lookup follows chronological source rows across irregular gaps", () => {
  const irregular = [{ time: 100 }, { time: 110 }, { time: 170 }, { time: 180 }];
  assert.equal(rawIndexAtTime(irregular, 140), 1.5);
  assert.equal(rawIndexAtTime(irregular, 175), 2.5);
});

test("density selection has hysteresis and freezes during gestures", () => {
  assert.equal(selectDensityMode({ candlesPerPixel: 2.2, previous: "exact" }), "dense");
  assert.equal(selectDensityMode({ candlesPerPixel: 1.8, previous: "dense" }), "dense");
  assert.equal(selectDensityMode({ candlesPerPixel: 1.5, previous: "dense" }), "exact");
  assert.equal(selectDensityMode({ candlesPerPixel: 9, previous: "dense", gestureActive: true }), "dense");
  assert.equal(selectDensityMode({ candlesPerPixel: 9, previous: "dense" }), "extreme");
});

test("view anchors are built once per projection revision", () => {
  const cache = createViewAnchorCache();
  const display = [{ time: 100 }, { time: 110 }];
  let builds = 0;
  const build = () => { builds += 1; return [{ rawIndex: 0, coordinate: builds }]; };

  assert.equal(cache.get(1, display, build)[0].coordinate, 1);
  assert.equal(cache.get(1, display, build)[0].coordinate, 1);
  assert.equal(builds, 1);

  cache.invalidate();
  assert.equal(cache.get(1, display, build)[0].coordinate, 2);
  assert.equal(cache.get(2, display, build)[0].coordinate, 3);
  assert.equal(cache.get(2, [...display], build)[0].coordinate, 4);
});
