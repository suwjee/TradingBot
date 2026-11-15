import test from "node:test";
import assert from "node:assert/strict";
import { createAlertMonitor, normalizeAlertRule } from "../../src/features/alerts/rules.js";

const rule = normalizeAlertRule({
  id: "rule-1", name: "rule-1", enabled: true, sound: true, seconds: 3,
  steps: [["stopall-1", "stopall-3", "stopall-5"], ["s-blue", "s-red"]],
});
const stop = (number, time, sourceTime = time) => ({ number, sourceTime, decisionEventTime: time });
const s = (color, time, sourceTime = time) => ({ color, sourceTime, decisionEventTime: time });
const payload = (stopAlls, sZones, direction = "bullish") => ({ directions: { [direction]: { stopAlls, sZones } } });

test("matches OR within steps and strict decision chronology across live results", () => {
  const monitor = createAlertMonitor();
  monitor.baseline(10);
  const stopAlls = [stop(3, 12, 6)];
  assert.deepEqual(monitor.advance([rule], payload(stopAlls, [s("red", 12)]), 12), []);
  assert.equal(monitor.progress(rule.id), 1);

  const result = payload(stopAlls, [s("red", 12), s("blue", 14, 9)]);
  assert.deepEqual(monitor.advance([rule], result, 15).map(match => match.events.map(event => event.type)), [
    ["stopall-3", "s-blue"],
  ]);
  assert.deepEqual(monitor.advance([rule], result, 16), []);
  assert.equal(monitor.progress(rule.id), 0);
});

test("handles one or many steps, rearms, and uses only valid events newer than its baseline", () => {
  const monitor = createAlertMonitor();
  const short = { ...rule, id: "short", steps: [["s-red"]] };
  const long = { ...rule, steps: [...rule.steps, ["stopall-2"], ["s-red"]] };
  monitor.baseline(10);
  const result = payload([stop(5, 12), stop(2, 14), stop(1, 2)], [
    s("red", 17), s("red", 15), s("blue", 13), { ...s("red", 16), calculationValid: false },
    s("red", 9), { color: "red", sourceTime: 20 },
  ]);
  assert.deepEqual(monitor.advance([long, short], result, 20).map(match => [match.rule.id, match.events.at(-1).time]), [
    ["rule-1", 15], ["short", 15], ["short", 17],
  ]);
});

test("drops invalidated partial sequences and never mixes directions", () => {
  const monitor = createAlertMonitor();
  monitor.baseline(10);
  monitor.advance([rule], payload([stop(1, 11)], []), 11);
  const result = payload([], [s("red", 12)], "bearish");
  assert.deepEqual(monitor.advance([rule], result, 12), []);
  assert.equal(monitor.progress(rule.id), 1);
  monitor.advance([rule], payload([stop(1, 11)], []), 13);
  assert.deepEqual(monitor.advance([rule], payload([], [s("red", 14)]), 14, { revalidateHistory: true }), []);
  assert.equal(monitor.progress(rule.id), 0);
});

test("a later primary structure can complete a rule after its causal StopAll is hidden", () => {
  const monitor = createAlertMonitor();
  monitor.baseline(10);
  const primary = normalizeAlertRule({ ...rule, steps: [["bearish:stopall-1"], ["ph-2"]] });
  monitor.advance([primary], payload([stop(1, 11)], [], "bearish"), 11);
  const completed = { directions: { bearish: { primaryHighs: [{ number: 2, sourceTime: 11, decisionEventTime: 14 }] } } };
  assert.deepEqual(monitor.advance([primary], completed, 14).map(match => match.events.map(event => event.type)), [
    ["stopall-1", "ph-2"],
  ]);
});

test("editing a rule clears its partial sequence and invalid definitions cannot be saved", () => {
  assert.equal(normalizeAlertRule({ ...rule, steps: [[]] }), null);
  assert.equal(normalizeAlertRule({ ...rule, steps: [["unknown"]] }), null);
  assert.equal(normalizeAlertRule({ ...rule, seconds: 0 }), null);
  const monitor = createAlertMonitor();
  monitor.baseline(10);
  monitor.advance([rule], payload([stop(1, 11)], []), 11);
  monitor.resetRule(rule.id);
  assert.deepEqual(monitor.advance([rule], payload([stop(1, 11)], [s("red", 12)]), 12), []);
});

test("uses Bridge formation times and supports explicitly changing direction between steps", () => {
  const monitor = createAlertMonitor();
  const result = { directions: {
    bullish: {
      reactions: [{ firstTime: 2, breakTime: 5 }], blueLines: [{ sourceTime: 3 }], aZones: [{ sourceTime: 4 }],
      bridgeOutput: {
        reactions: [{ structure: { breakoutCandle: { eventTime: "1970-01-01 03:30:11" } } }],
        blueLines: [{ formedAt: { eventTime: "1970-01-01 03:30:12" } }],
        aZones: [{ reaction: { confirmedAt: { eventTime: "1970-01-01 03:30:13" } } }],
      },
    },
    bearish: { eZones: [{ family: "red", number: 4, sourceTime: 5, decisionEventTime: 14 }],
      primaryHighs: [{ number: 2, sourceTime: 7, decisionEventTime: 15 }],
      primaryLows: [{ number: 3, sourceTime: 8, decisionEventTime: 16 }] },
  } };
  const expanded = normalizeAlertRule({ ...rule, steps: [
    ["bullish:reaction"], ["bullish:blue-line"], ["bullish:a"], ["bearish:e-red"], ["ph-2"], ["pl-3"],
  ] });
  assert.ok(expanded);
  monitor.baseline(10);
  const [match] = monitor.advance([expanded], result, 16);
  assert.deepEqual(match.events.map(event => event.time), [11, 12, 13, 14, 15, 16]);
});

test("uses the published Reset time for Reset Blue and the official break candle when precise confirmation is unavailable", () => {
  const monitor = createAlertMonitor();
  monitor.baseline(10);
  const result = { directions: { bearish: {
    reactions: [{ firstTime: 8, breakTime: 11 }],
    resets: [{ index: 3, time: 12, secondTime: 14, brokenLevel: "20.00" }],
    blueLines: [{ kind: "reset", sourceIndex: 3, sourceTime: 12, brokenLevel: "20.00" }],
    aZones: [{ sourceTime: 15, reactionBreakTime: 17 }],
    bridgeOutput: { blueLines: [{ formedAt: { time: "1970-01-01 03:30:12", eventTime: null } }] },
  } } };
  const expanded = normalizeAlertRule({ ...rule, steps: [["bearish:reaction"], ["bearish:blue-line"], ["bearish:a"]] });
  const [match] = monitor.advance([expanded], result, 18);
  assert.deepEqual(match.events.map(event => event.time), [11, 14, 17]);
});
