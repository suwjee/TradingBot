import test from "node:test";
import assert from "node:assert/strict";
import { appendCandleBuckets } from "../../src/chart/candle-buckets.js";

const bar = (time, open, high, low, close) => ({ time, open, high, low, close });

test("new closed RAW candles complete the current display bucket and start the next one", () => {
  const prior = [bar(90, 10, 12, 9, 11), bar(120, 11, 13, 10, 12)];
  const result = appendCandleBuckets(prior, [
    bar(135, 12, 15, 11, 14),
    bar(145, 14, 16, 8, 9),
    bar(150, 9, 10, 7, 8),
  ], 30);
  assert.deepEqual(result.changed, [bar(120, 11, 16, 8, 9), bar(150, 9, 10, 7, 8)]);
  assert.deepEqual(result.data, [prior[0], ...result.changed]);
  assert.deepEqual(prior[1], bar(120, 11, 13, 10, 12));
});

test("market gaps introduce no synthetic display candles", () => {
  const prior = [bar(120, 11, 13, 10, 12)];
  const next = bar(1800, 15, 16, 13, 14);
  const result = appendCandleBuckets(prior, [next], 30);
  assert.deepEqual(result.changed, [next]);
  assert.deepEqual(result.data, [...prior, next]);
});
