import test from "node:test";
import assert from "node:assert/strict";

import { resolveCanonicalChartPoint } from "../src/chart/drawing-coordinates.js";

test("constrained drawing points persist canonical raw time under LOD", () => {
  const point = resolveCanonicalChartPoint({
    x: 125,
    y: 240,
    timeAtCoordinate: () => 1_788_787_290,
    priceAtCoordinate: () => 4401.25,
    fallback: { time: 123, price: 1 },
  });
  assert.deepEqual(point, { x: 125, y: 240, time: 1_788_787_290, price: 4401.25 });
});
