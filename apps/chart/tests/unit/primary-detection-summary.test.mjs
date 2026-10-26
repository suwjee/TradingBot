import test from "node:test";
import assert from "node:assert/strict";

test("primary summary reports finalized counts and explains an empty waiting result", async () => {
  const { primaryDetectionSummary } = await import("../../src/features/primary-detection-summary.js");
  const summary = primaryDetectionSummary({ primaryHighs: [], primaryLows: [], matchingBehaviorLegs: [], primaryStatus: "waiting-for-stopall-break" });
  assert.deepEqual([summary.highs, summary.lows, summary.legs], [0, 0, 0]);
  assert.equal(summary.statusLabel, "Waiting for price to cross a qualified StopAll level.");
});

test("primary summary counts populated engine arrays without recalculating results", async () => {
  const { primaryDetectionSummary } = await import("../../src/features/primary-detection-summary.js");
  const summary = primaryDetectionSummary({ primaryHighs: [{}, {}, {}, {}], primaryLows: [{}, {}], matchingBehaviorLegs: [{}], primaryStatus: "waiting-for-ph-order-stop" });
  assert.deepEqual([summary.highs, summary.lows, summary.legs], [4, 2, 1]);
  assert.equal(summary.statusLabel, "Waiting for a valid PH order to stop.");
});

test("primary summary explains all published waiting and terminal statuses", async () => {
  const { primaryDetectionSummary } = await import("../../src/features/primary-detection-summary.js");
  const cases = [
    ["waiting-for-matching-behaviors", "Waiting for a qualified matching-behavior leg."],
    ["waiting-for-structure-break", "Waiting for price to cross the latest PH or PL level."],
    ["waiting-for-pl-order-stop", "Waiting for a valid PL order to stop."],
    ["post-pl3-orders-only", "Evaluating valid orders after PL-3."],
    ["ambiguous-raw-boundary-order", "The available RAW candles cannot determine which event happened first."],
  ];
  for (const [primaryStatus, expected] of cases) assert.equal(primaryDetectionSummary({ primaryStatus }).statusLabel, expected);
});

test("older or uncalculated directional results have an explicit unavailable summary", async () => {
  const { primaryDetectionSummary } = await import("../../src/features/primary-detection-summary.js");
  assert.equal(primaryDetectionSummary({}).statusLabel, "PH/PL was not calculated for this result.");
  assert.equal(primaryDetectionSummary({ primaryStatus: "future-status" }).statusLabel, "PH/PL status is not available.");
});
