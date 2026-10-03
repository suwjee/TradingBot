import test from "node:test";
import assert from "node:assert/strict";

import { mergeChartUpdateCandles } from "../../server/chart-update-merge.js";

function row(time, close = time) {
  return { time, open: close, high: close + 1, low: close - 1, close };
}

test("chart update merge keeps existing rows on duplicate timestamps", () => {
  const existing = [row(5), row(15), row(25)];
  const incoming = [row(5, 500), row(10), row(25, 2500), row(30)];
  const result = mergeChartUpdateCandles(existing, incoming);
  assert.deepEqual(result.candles.map((candle) => candle.time), [5, 10, 15, 25, 30]);
  assert.equal(result.candles[0], existing[0]);
  assert.equal(result.candles[3], existing[2]);
  assert.deepEqual({ added: result.added, ignoredExisting: result.ignoredExisting }, { added: 2, ignoredExisting: 2 });
});

test("chart update merge matches the prior Map and sort result across gaps", () => {
  const existing = Array.from({ length: 5000 }, (_, index) => row(index * 10 + 5));
  const incoming = Array.from({ length: 3500 }, (_, index) => row(index * 15 + 5, -index));
  const byTime = new Map(existing.map((candle) => [candle.time, candle]));
  for (const candle of incoming) if (!byTime.has(candle.time)) byTime.set(candle.time, candle);
  const expected = [...byTime.values()].sort((left, right) => left.time - right.time);
  const result = mergeChartUpdateCandles(existing, incoming);
  assert.deepEqual(result.candles, expected);
  assert.equal(result.added, expected.length - existing.length);
  assert.equal(result.ignoredExisting, incoming.length - result.added);
});

test("seeded valid updates match the former Map and sort oracle", () => {
  let seed = 0xcee55;
  const next = (limit) => { seed = (Math.imul(seed, 1103515245) + 12345) >>> 0; return seed % limit; };
  for (let caseIndex = 0; caseIndex < 400; caseIndex++) {
    const existing = [];
    const incoming = [];
    for (let time = 5; time < 405; time += 5) {
      if (next(4) === 0) existing.push(row(time, time));
      if (next(4) === 0) incoming.push(row(time, -time));
    }
    const byTime = new Map(existing.map((candle) => [candle.time, candle]));
    let added = 0;
    let ignoredExisting = 0;
    for (const candle of incoming) {
      if (byTime.has(candle.time)) ignoredExisting++;
      else { byTime.set(candle.time, candle); added++; }
    }
    const expected = [...byTime.values()].sort((left, right) => left.time - right.time);
    const actual = mergeChartUpdateCandles(existing, incoming);
    assert.equal(JSON.stringify(actual.candles), JSON.stringify(expected), `case ${caseIndex}`);
    assert.deepEqual({ added: actual.added, ignoredExisting: actual.ignoredExisting },
      { added, ignoredExisting }, `case ${caseIndex}`);
  }
});
