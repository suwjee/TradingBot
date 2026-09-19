import test from "node:test";
import assert from "node:assert/strict";

import { calculateMeasureStats, calculatePositionLevels } from "../src/drawings/drawing-math.js";

test("measure stats include duration, candle count, price delta, and percentage", () => {
  assert.deepEqual(calculateMeasureStats({ time: 100, price: 100 }, { time: 220, price: 110 }, 60), {
    durationSeconds: 120,
    bars: 2,
    priceDelta: 10,
    percentage: 10,
    durationLabel: "2m",
  });
});

test("long and short position levels expose target, stop, and risk reward", () => {
  assert.deepEqual(calculatePositionLevels("long", 100, 110), {
    entry: 100, target: 110, stop: 90, risk: 10, reward: 10, riskReward: 1,
  });
  assert.deepEqual(calculatePositionLevels("short", 100, 90), {
    entry: 100, target: 90, stop: 110, risk: 10, reward: 10, riskReward: 1,
  });
});
