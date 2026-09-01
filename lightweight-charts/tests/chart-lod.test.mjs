import assert from "node:assert/strict";
import test from "node:test";
import { buildCandleLod, chooseLodStride, lowerBoundTime } from "../src/chart-lod.js";

const candles = [
  { time: 10, open: 1, high: 3, low: 1, close: 2 },
  { time: 11, open: 2, high: 8, low: 0, close: 4 },
  { time: 12, open: 4, high: 6, low: 3, close: 5 },
  { time: 13, open: 5, high: 7, low: 2, close: 6 },
];

test("LOD aggregation preserves each bucket's first open, extrema and final close", () => {
  assert.deepEqual(buildCandleLod(candles, 0, candles.length, 2), [
    { time: 10, open: 1, high: 8, low: 0, close: 4 },
    { time: 12, open: 4, high: 7, low: 2, close: 6 },
  ]);
  assert.deepEqual(buildCandleLod(candles, 0, candles.length, 1), candles);
});

test("LOD picks power-of-two density and finds source windows by timestamp", () => {
  assert.equal(chooseLodStride(300_000, 1_000), 256);
  assert.equal(lowerBoundTime(candles, 11), 1);
  assert.equal(lowerBoundTime(candles, 11.5), 2);
});
