import test from "node:test";
import assert from "node:assert/strict";

import { aggregate } from "../../src/chart/candle-aggregation.js";

const rows = [
  { time: 100, open: 10, high: 12, low: 9, close: 11 },
  { time: 105, open: 11, high: 14, low: 10, close: 12 },
  { time: 110, open: 12, high: 13, low: 8, close: 9 },
  { time: 115, open: 9, high: 10, low: 7, close: 8 },
  { time: 120, open: 8, high: 9, low: 6, close: 7 },
];

test("source-timeframe presentation reuses canonical rows without cloning", () => {
  assert.strictEqual(aggregate(rows, 1), rows);
});

test("chart-timeframe presentation keeps exact bucket OHLC, ordering and close ownership", () => {
  const original = structuredClone(rows);
  const bars = aggregate(rows, 10);
  assert.deepEqual(bars, [
    { time: 100, open: 10, high: 14, low: 9, close: 12 },
    { time: 110, open: 12, high: 13, low: 7, close: 8 },
    { time: 120, open: 8, high: 9, low: 6, close: 7 },
  ]);
  assert.deepEqual(rows, original);
  assert.notStrictEqual(bars[0], rows[0]);
});

test("presentation aggregation keeps bucket timestamp and Number conversion for numeric-string OHLC", () => {
  const sample = [
    { time: "100", open: "1", high: "2", low: "0.5", close: "1.5" },
    { time: "105", open: "1.5", high: "3", low: "1", close: "2" },
  ];
  assert.deepEqual(aggregate(sample, 30), [
    { time: 90, open: 1, high: 3, low: 0.5, close: 2 },
  ]);
});

test("empty source produces empty chart series", () => {
  assert.deepEqual(aggregate([], 30), []);
});
