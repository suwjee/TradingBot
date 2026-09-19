import test from "node:test";
import assert from "node:assert/strict";

import { normalizeIndicatorRange, moveIndicatorRange } from "../src/chart/indicator-range.js";

const candles = [10, 20, 30, 40].map((time) => ({ time }));

test("indicator range snaps both endpoints to inclusive candle times", () => {
  assert.deepEqual(normalizeIndicatorRange(11, 39, candles), {
    from: 10, to: 40, fromIndex: 0, toIndex: 3,
  });
});

test("indicator range permits a single selected candle", () => {
  assert.deepEqual(normalizeIndicatorRange(29, 31, candles), {
    from: 30, to: 30, fromIndex: 2, toIndex: 2,
  });
});

test("moving one handle cannot cross the other handle", () => {
  assert.deepEqual(moveIndicatorRange({ fromIndex: 1, toIndex: 3 }, "from", 3, candles), {
    fromIndex: 3, toIndex: 3,
  });
  assert.deepEqual(moveIndicatorRange({ fromIndex: 1, toIndex: 3 }, "to", 0, candles), {
    fromIndex: 1, toIndex: 1,
  });
});
