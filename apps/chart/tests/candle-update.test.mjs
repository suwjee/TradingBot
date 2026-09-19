import test from "node:test";
import assert from "node:assert/strict";

import {
  buildChartUpdateRanges,
  buildChartUpdatePackets,
  buildGapDetectionRanges,
  buildLatestCandleRange,
  classifyFarazCoverage,
  mapWithConcurrency,
  buildUnverifiedChartUpdateRanges,
  buildChartVerificationRanges,
  chunkCandleUpdates,
  chunkCandleUpdatesByBytes,
  mergeChartCandles,
} from "../src/features/candle-update.js";

const candle = (time, close = 1) => ({ time, open: close, high: close, low: close, close });

test("full gap detection requests only the exclusive missing source-timeframe slots", () => {
  assert.deepEqual(buildGapDetectionRanges([candle(100), candle(120)], 5, { mode: "full" }), [
    { kind: "gap", from: 105, to: 115, missingCandles: 3 },
  ]);
});

test("since-check gap detection starts after the durable checkpoint and falls back to full", () => {
  const rows = [candle(100), candle(120), candle(140), candle(150)];
  assert.deepEqual(buildGapDetectionRanges(rows, 5, { mode: "since", checkedThrough: 120 }), [
    { kind: "gap", from: 125, to: 135, missingCandles: 3 },
    { kind: "gap", from: 145, to: 145, missingCandles: 1 },
  ]);
  assert.deepEqual(buildGapDetectionRanges(rows, 5, { mode: "since" }), buildGapDetectionRanges(rows, 5, { mode: "full" }));
});

test("latest-candle update stops at the final fully closed RAW timeframe candle", () => {
  assert.deepEqual(buildLatestCandleRange([candle(100), candle(105)], 5, 119), {
    kind: "latest", from: 110, to: 110, missingCandles: 1,
  });
  assert.equal(buildLatestCandleRange([candle(100), candle(105)], 5, 109), null);
});

test("chart updates request every internal source-timeframe gap before the latest range", () => {
  assert.deepEqual(buildChartUpdateRanges([
    candle(100), candle(105), candle(120),
  ], 5, 132), [
    { kind: "gap", from: 110, to: 115, missingCandles: 2 },
    { kind: "latest", from: 125, to: 130, missingCandles: 2 },
  ]);
});

test("chart updates preserve the raw timeframe when locating a single missing candle", () => {
  assert.deepEqual(buildChartUpdateRanges([
    candle(100), candle(110),
  ], 5, 111), [
    { kind: "gap", from: 105, to: 105, missingCandles: 1 },
  ]);
});

test("chart updates skip only source ranges already verified in the RAW metadata", () => {
  const candles = [candle(100), candle(105), candle(120)];
  const coverage = {
    timeframeSeconds: 5,
    ranges: [
      { from: 110, to: 115, status: "complete" },
      { from: 125, to: 125, status: "source_missing" },
    ],
  };

  assert.deepEqual(buildUnverifiedChartUpdateRanges(candles, 5, 132, coverage), [
    { kind: "latest", from: 130, to: 130, missingCandles: 1 },
  ]);
});

test("chart verification audits the full RAW interval once and later requests only unchecked slots", () => {
  const rows = [candle(100), candle(105), candle(120)];
  assert.deepEqual(buildChartVerificationRanges(rows, 5, 132), [
    { kind: "audit", from: 100, to: 120, missingCandles: 5 },
    { kind: "latest", from: 125, to: 130, missingCandles: 2 },
  ]);
  assert.deepEqual(buildChartVerificationRanges(rows, 5, 132, {
    timeframeSeconds: 5,
    ranges: [
      { from: 100, to: 105, status: "complete" },
      { from: 110, to: 115, status: "source_missing" },
    ],
  }), [
    { kind: "audit", from: 120, to: 120, missingCandles: 1 },
    { kind: "latest", from: 125, to: 130, missingCandles: 2 },
  ]);
  assert.deepEqual(buildChartVerificationRanges(rows, 5, 120, {
    timeframeSeconds: 5, ranges: [{ from: 100, to: 120, status: "complete" }],
  }), []);
});

test("FARAZ coverage records both complete and confirmed-missing source slots", () => {
  assert.deepEqual(classifyFarazCoverage([
    candle(100), candle(110),
  ], { from: 100, to: 110, timeframeSeconds: 5 }), [
    { from: 100, to: 100, status: "complete" },
    { from: 105, to: 105, status: "source_missing" },
    { from: 110, to: 110, status: "complete" },
  ]);
});

test("chart update packets run concurrently while preserving their result order", async () => {
  let active = 0;
  let peak = 0;
  const result = await mapWithConcurrency(["first", "second", "third", "fourth"], async (value) => {
    active++;
    peak = Math.max(peak, active);
    await new Promise((resolve) => setTimeout(resolve, value === "first" ? 12 : 2));
    active--;
    return value.toUpperCase();
  }, 2);

  assert.deepEqual(result, ["FIRST", "SECOND", "THIRD", "FOURTH"]);
  assert.equal(peak, 2);
});

test("chart update merge inserts recovered candles chronologically without replacing saved rows", () => {
  const existing = [candle(100, 1), candle(110, 3)];
  const incoming = [candle(105, 2), candle(110, 99), candle(115, 4)];

  assert.deepEqual(mergeChartCandles(existing, incoming), [
    candle(100, 1), candle(105, 2), candle(110, 3), candle(115, 4),
  ]);
});

test("chart update gaps are coalesced and split into bounded source-timeframe packets", () => {
  const ranges = [
    { kind: "gap", from: 100, to: 105, missingCandles: 2 },
    { kind: "gap", from: 115, to: 130, missingCandles: 4 },
  ];

  assert.deepEqual(buildChartUpdatePackets(ranges, 5, 5), [
    { from: 100, to: 120, requestedCandles: 5, targetMissingCandles: 4, kinds: ["gap"] },
    { from: 125, to: 130, requestedCandles: 2, targetMissingCandles: 2, kinds: ["gap"] },
  ]);
});

test("chart updates split a large chronological append into bounded ordered requests", () => {
  const rows = [100, 105, 110, 115, 120].map((time) => candle(time));

  assert.deepEqual(chunkCandleUpdates(rows, 2).map((batch) => batch.map((row) => row.time)), [
    [100, 105],
    [110, 115],
    [120],
  ]);
});

test("chart updates use byte-bounded batches so large appends need far fewer safe writes", () => {
  const rows = Array.from({ length: 12 }, (_, index) => ({
    ...candle(100 + index * 5),
    // A deliberately uneven payload proves the limit is based on transport
    // size rather than a fixed candle count.
    note: "x".repeat(index % 3 === 0 ? 40 : 2),
  }));
  const maximumPayloadBytes = 170;
  const requestOverheadBytes = 35;
  const chunks = chunkCandleUpdatesByBytes(rows, { maximumPayloadBytes, requestOverheadBytes });

  assert.deepEqual(chunks.flatMap((batch) => batch.map((row) => row.time)), rows.map((row) => row.time));
  assert.ok(chunks.length < rows.length, "multiple candles should share a transport request");
  for (const batch of chunks) {
    const arrayBytes = new TextEncoder().encode(JSON.stringify(batch)).byteLength;
    assert.ok(arrayBytes + requestOverheadBytes <= maximumPayloadBytes);
  }
});
