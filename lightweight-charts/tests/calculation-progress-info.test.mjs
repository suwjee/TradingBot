import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

const source = readFileSync(new URL("../src/main.js", import.meta.url), "utf8");

test("Info retains the complete calculation trace with elapsed and stage durations", () => {
  assert.match(source, /const events = \[\];/);
  assert.match(source, /elapsedMs: Math\.round\(\(performance\.now\(\) - started\)/);
  assert.match(source, /progressEvents: progressTimer\.events/);
  assert.match(source, /Complete execution log/);
  assert.match(source, /calculationTraceAggregates\(progressTrace/);
});

test("timing stages are dynamic, concise, and expose English hover descriptions", () => {
  assert.match(source, /const calculationStageDescriptions = Object\.freeze/);
  assert.match(source, /Read source file/);
  assert.match(source, /Normalize raw candles/);
  assert.match(source, /calculationStageTitle\(label\)/);
  assert.match(source, /Activity, warnings & errors/);
  assert.match(source, /Progress stream disconnected/);
});

test("the popup declares all planned stages before calculation starts", () => {
  assert.match(source, /function plannedCalculationStages\(direction\)/);
  assert.match(source, /new Map\(plannedStages\.map/);
  assert.match(source, /calculationSteps"\)\.innerHTML = plannedStages\.map/);
  assert.match(source, /Not needed/);
  assert.match(source, /calculationStageKey\(event\.label, event\.status, planned\)/);
  assert.doesNotMatch(source, /id="calculationLog"/);
});

test("the request wrapper records its start before fetch so stage order reflects execution", () => {
  const start = source.indexOf('status: "started", label: "HTTP request and server"');
  const fetchCall = source.indexOf('await fetch("/api/reactions"');
  assert.ok(start > 0 && fetchCall > start);
});
