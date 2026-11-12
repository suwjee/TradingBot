import test from "node:test";
import assert from "node:assert/strict";

import { normalizeIndicatorRange, moveIndicatorRange } from "../../src/chart/indicator-range.js";

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

test("range snapping breaks ties toward the earlier candle without scanning chart history", () => {
  let reads = 0;
  const history = new Proxy(Array.from({ length: 4096 }, (_, i) => ({ time: 30 * (i + 1) })), {
    get(target, key, receiver) {
      if (/^\d+$/.test(String(key))) reads += 1;
      return Reflect.get(target, key, receiver);
    },
  });
  assert.deepEqual(normalizeIndicatorRange(60015, 90001, history), {
    from: 60000, to: 90000, fromIndex: 1999, toIndex: 2999,
  });
  assert.ok(reads < 100, `range handles read ${reads} candles per update`);
});

test("moving one handle cannot cross the other handle", () => {
  assert.deepEqual(moveIndicatorRange({ fromIndex: 1, toIndex: 3 }, "from", 3, candles), {
    fromIndex: 3, toIndex: 3,
  });
  assert.deepEqual(moveIndicatorRange({ fromIndex: 1, toIndex: 3 }, "to", 0, candles), {
    fromIndex: 1, toIndex: 1,
  });
});
