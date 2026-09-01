import test from "node:test";
import assert from "node:assert/strict";
import { updateStageAggregate } from "../src/calculation-progress.js";

test("repeated calculation stages retain first-seen order and sum every duration", () => {
  const stages = new Map();
  updateStageAggregate(stages, "S • Bullish", "S • Bullish", { status: "started" });
  updateStageAggregate(stages, "S • Bullish", "S • Bullish", { status: "completed", durationMs: 12.25 });
  updateStageAggregate(stages, "E • Bullish", "E • Bullish", { status: "completed", durationMs: 4 });
  updateStageAggregate(stages, "S • Bullish", "S • Bullish", { status: "started" });
  const { aggregate, created } = updateStageAggregate(stages, "S • Bullish", "S • Bullish", { status: "completed", durationMs: 7.75 });

  assert.equal(created, false);
  assert.deepEqual([...stages.keys()], ["S • Bullish", "E • Bullish"]);
  assert.equal(aggregate.runs, 2);
  assert.equal(aggregate.totalDurationMs, 20);
  assert.equal(aggregate.active, false);
});
