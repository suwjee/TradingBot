import test from "node:test";
import assert from "node:assert/strict";

import { startVisibleClock } from "../../src/features/visible-clock.js";

function clockHarness(visibility = "visible") {
  let intervalId = 0;
  const scheduled = new Map();
  const listeners = new Map();
  const ticks = [];
  const page = {
    visibilityState: visibility,
    addEventListener(event, listener) { listeners.set(event, listener); },
    removeEventListener(event, listener) {
      if (listeners.get(event) === listener) listeners.delete(event);
    },
    setVisibility(next) { this.visibilityState = next; listeners.get("visibilitychange")?.(); },
  };
  const stop = startVisibleClock({
    document: page,
    tick() { ticks.push(ticks.length + 1); },
    intervalMs: 1000,
    setIntervalFn(callback, delay) {
      assert.equal(delay, 1000);
      const id = ++intervalId;
      scheduled.set(id, callback);
      return id;
    },
    clearIntervalFn(id) { scheduled.delete(id); },
  });
  return { page, ticks, scheduled, stop };
}

test("visible UI clock renders immediately and owns exactly one periodic timer", () => {
  const view = clockHarness();
  assert.equal(view.ticks.length, 1);
  assert.equal(view.scheduled.size, 1);
  [...view.scheduled.values()][0]();
  assert.equal(view.ticks.length, 2);
  view.page.setVisibility("visible");
  assert.equal(view.ticks.length, 3);
  assert.equal(view.scheduled.size, 1);
  view.stop();
  assert.equal(view.scheduled.size, 0);
});

test("hidden UI clock performs no work and resumes without duplicate timers", () => {
  const view = clockHarness("hidden");
  assert.equal(view.ticks.length, 0);
  assert.equal(view.scheduled.size, 0);
  view.page.setVisibility("visible");
  assert.equal(view.ticks.length, 1);
  assert.equal(view.scheduled.size, 1);
  view.page.setVisibility("hidden");
  assert.equal(view.scheduled.size, 0);
  view.page.setVisibility("visible");
  assert.equal(view.ticks.length, 2);
  assert.equal(view.scheduled.size, 1);
  view.stop();
  assert.equal(view.scheduled.size, 0);
  view.page.setVisibility("visible");
  assert.equal(view.ticks.length, 2);
});
