import test from "node:test";
import assert from "node:assert/strict";

test("integrity detector flags only complete aligned slots outside a closure", async () => {
  const { findActionableGaps } = await import("../server/raw-integrity.js");
  const candles = [
    { time: 100, open: 1, high: 1, low: 1, close: 1 },
    { time: 105, open: 1, high: 1, low: 1, close: 1 },
    { time: 115, open: 1, high: 1, low: 1, close: 1 },
    { time: 120, open: 1, high: 1, low: 1, close: 1 },
    { time: 135, open: 1, high: 1, low: 1, close: 1 },
  ];
  const gaps = findActionableGaps(candles, 5, (time) => time === 125 || time === 130);
  assert.deepEqual(gaps, [{ from: 110, to: 110, missingCandles: 1 }]);
});

test("integrity detector does not invent sub-timeframe gaps", async () => {
  const { findActionableGaps } = await import("../server/raw-integrity.js");
  const candles = [
    { time: 100, open: 1, high: 1, low: 1, close: 1 },
    { time: 105, open: 1, high: 1, low: 1, close: 1 },
  ];
  assert.deepEqual(findActionableGaps(candles, 5, () => false), []);
});
