import test from "node:test";
import assert from "node:assert/strict";
import { bindViewportEvents, createViewportScheduler } from "../../src/chart/viewport-events.js";

function fakeScheduler({ data = true, panning = false } = {}) {
  const timers = new Map(), frames = new Map(), renders = [];
  let nextId = 0;
  let currentRange = { from: 100, to: 200 };
  const schedule = createViewportScheduler({
    hasData: () => data,
    isPointerPanning: () => panning,
    getVisibleRange: () => currentRange,
    render: (...args) => renders.push(args),
    setTimeoutFn(callback, delay) {
      const id = ++nextId;
      timers.set(id, { callback, delay });
      return id;
    },
    clearTimeoutFn(id) { timers.delete(id); },
    requestAnimationFrameFn(callback) {
      const id = ++nextId;
      frames.set(id, callback);
      return id;
    },
  });
  function flushTimer() {
    const [, work] = [...timers][0];
    assert.ok(work, "expected one pending timeout");
    timers.clear();
    work.callback();
    return work.delay;
  }
  function flushFrame() {
    const [, callback] = [...frames][0];
    assert.ok(callback, "expected one pending animation frame");
    frames.clear();
    callback();
  }
  return {
    schedule, renders, timers, frames, flushTimer, flushFrame,
    setData(value) { data = value; },
    setPanning(value) { panning = value; },
    setRange(value) { currentRange = value; },
  };
}

test("viewport scheduling preserves default 140ms debounce and latest visible range", () => {
  const clock = fakeScheduler();
  clock.schedule();
  clock.schedule(90);
  assert.equal(clock.timers.size, 1);
  assert.equal(clock.flushTimer(), 90);
  clock.setRange({ from: 140, to: 240 });
  clock.flushFrame();
  assert.deepEqual(clock.renders, [[{ from: 140, to: 240 }, { preserveRange: true }]]);
});

test("viewport scheduling coalesces pending frames, avoids data-less renders and freezes during pointer drag", () => {
  const clock = fakeScheduler();
  clock.setData(false);
  clock.schedule();
  assert.equal(clock.timers.size, 0);
  clock.setData(true);
  clock.schedule(0);
  assert.equal(clock.flushTimer(), 0);
  clock.schedule(140);
  clock.flushTimer();
  assert.equal(clock.frames.size, 1);
  clock.setPanning(true);
  clock.flushFrame();
  assert.equal(clock.renders.length, 0);
  clock.setPanning(false);
  clock.schedule(90);
  assert.equal(clock.flushTimer(), 90);
  clock.flushFrame();
  assert.equal(clock.renders.length, 1);
});

test("viewport logical/time/size and pointer handlers retain original dispatch order and delays", () => {
  const events = new Map(), listeners = new Map(), log = [];
  const timeScale = {
    subscribeVisibleLogicalRangeChange(fn) { events.set("logical", fn); },
    subscribeVisibleTimeRangeChange(fn) { events.set("time", fn); },
    subscribeSizeChange(fn) { events.set("size", fn); },
    unsubscribeVisibleLogicalRangeChange(fn) { assert.strictEqual(events.get("logical"), fn); events.delete("logical"); },
    unsubscribeVisibleTimeRangeChange(fn) { assert.strictEqual(events.get("time"), fn); events.delete("time"); },
    unsubscribeSizeChange(fn) { assert.strictEqual(events.get("size"), fn); events.delete("size"); },
  };
  const shell = {
    addEventListener(event, fn, options) {
      assert.deepEqual(options, { passive: true });
      listeners.set(event, fn);
    },
    removeEventListener(event, fn) {
      assert.strictEqual(listeners.get(event), fn);
      listeners.delete(event);
    },
  };
  const release = bindViewportEvents({
    timeScale, shell,
    invalidateAnchors: () => log.push("invalidate"),
    scheduleDraw: () => log.push("draw"),
    scheduleViewport: (delay = 140) => log.push(`viewport:${delay}`),
    setPointerPanning: (enabled) => log.push(`panning:${enabled}`),
  });
  events.get("logical")();
  events.get("time")();
  events.get("size")();
  listeners.get("pointermove")({ buttons: 0 });
  listeners.get("pointermove")({ buttons: 1 });
  listeners.get("pointerdown")({ button: 2 });
  listeners.get("pointerdown")({ button: 0 });
  listeners.get("pointerup")();
  listeners.get("pointercancel")();
  assert.deepEqual(log, [
    "invalidate", "draw", "viewport:140",
    "invalidate", "draw", "viewport:140",
    "invalidate", "draw", "viewport:0",
    "draw", "panning:true",
    "panning:false", "draw", "viewport:90",
    "panning:false", "viewport:90",
  ]);
  release();
  assert.equal(events.size, 0);
  assert.equal(listeners.size, 0);
});
