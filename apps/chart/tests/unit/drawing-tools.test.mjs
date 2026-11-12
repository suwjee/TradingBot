import test from "node:test";
import assert from "node:assert/strict";

import { calculateMeasureStats, calculatePositionLevels } from "../../src/drawings/drawing-math.js";
import * as drawingMath from "../../src/drawings/drawing-math.js";
import * as chartState from "../../src/chart/state.js";

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

test("position levels retain independently supplied stops in both directions", () => {
  assert.deepEqual(calculatePositionLevels("long", 100, 120, 95), {
    entry: 100, target: 120, stop: 95, risk: 5, reward: 20, riskReward: 4,
  });
  assert.deepEqual(calculatePositionLevels("short", 100, 80, 105), {
    entry: 100, target: 80, stop: 105, risk: 5, reward: 20, riskReward: 4,
  });
  assert.equal(calculatePositionLevels("long", 100, 120, 100), null);
  assert.equal(calculatePositionLevels("short", 100, 80, 95), null);
});

test("new positions start at four R and resizing either region preserves the other", () => {
  assert.equal(typeof drawingMath.initialPositionLevels, "function");
  assert.equal(typeof drawingMath.editPositionLevel, "function");
  for (const type of ["long", "short"]) {
    const sign = type === "long" ? 1 : -1;
    const initial = drawingMath.initialPositionLevels(type, 100, 100 + sign * 20);
    assert.equal(initial.riskReward, 4);
    const drawing = { type, a: { time: 1000, price: 100 }, b: { time: 1600, price: initial.target }, stopPrice: initial.stop };
    const targetEdit = drawingMath.editPositionLevel(drawing, "target", 100 + sign * 10);
    assert.equal(targetEdit.stopPrice, initial.stop);
    assert.equal(calculatePositionLevels(type, 100, targetEdit.b.price, targetEdit.stopPrice).riskReward, 2);
    const stopEdit = drawingMath.editPositionLevel(targetEdit, "stop", 100 - sign * 10);
    assert.equal(stopEdit.b.price, targetEdit.b.price);
    assert.equal(calculatePositionLevels(type, 100, stopEdit.b.price, stopEdit.stopPrice).riskReward, 1);
    assert.equal(drawingMath.editPositionLevel(drawing, "stop", 100), null);
    assert.equal(drawingMath.editPositionLevel(drawing, "target", 100 - sign), null);
    assert.equal(drawing.b.price, initial.target, "Editing must not mutate the prior undo snapshot");
  }
});

test("position width counts actual candles across market gaps and supports future space", () => {
  assert.equal(typeof drawingMath.positionEndTime, "function");
  const candles = Array.from({ length: 30 }, (_, i) => ({ time: 1000 + i * 30 + (i >= 10 ? 3600 : 0) }));
  assert.equal(drawingMath.positionEndTime(candles, candles[2].time, 30), candles[22].time);
  assert.equal(drawingMath.positionEndTime(candles, candles[25].time, 30), candles[29].time + 16 * 30);
  assert.equal(drawingMath.positionEndTime([], 1000, 30), 1600);
});

test("horizontal position handles change only their own time boundary", () => {
  assert.equal(typeof drawingMath.editPositionTime, "function");
  for (const type of ["long", "short"]) {
    const drawing = { type, a: { time: 1000, price: 100 }, b: { time: 1600, price: type === "long" ? 120 : 80 }, stopPrice: type === "long" ? 95 : 105 };
    const extended = drawingMath.editPositionTime(drawing, "end", 2200);
    assert.equal(extended.a.time, 1000);
    assert.equal(extended.b.time, 2200);
    const shortened = drawingMath.editPositionTime(extended, "start", 1300);
    assert.equal(shortened.a.time, 1300);
    assert.equal(shortened.b.time, 2200);
    for (const edited of [extended, shortened]) {
      assert.equal(edited.a.price, drawing.a.price);
      assert.equal(edited.b.price, drawing.b.price);
      assert.equal(edited.stopPrice, drawing.stopPrice);
    }
    assert.equal(drawingMath.editPositionTime(drawing, "end", 1000), null);
    assert.equal(drawingMath.editPositionTime(drawing, "start", 1600), null);
    assert.equal(drawing.b.time, 1600);
  }
});

test("editable position width measures candles rather than elapsed gap time", () => {
  assert.equal(typeof drawingMath.positionWidthBars, "function");
  const candles = Array.from({ length: 30 }, (_, i) => ({ time: 1000 + i * 30 + (i >= 10 ? 3600 : 0) }));
  assert.equal(drawingMath.positionWidthBars(candles, candles[2].time, candles[22].time, 30), 20);
  assert.equal(drawingMath.positionWidthBars(candles, candles[25].time, candles[29].time + 16 * 30, 30), 20);
  assert.equal(drawingMath.positionWidthBars([], 1000, 2200, 30), 40);
});

test("moving a resized position across a market gap preserves its candle width and price offsets", () => {
  assert.equal(typeof drawingMath.translatePosition, "function");
  const candles = Array.from({ length: 30 }, (_, i) => ({ time: 1000 + i * 30 + (i >= 10 ? 3600 : 0) }));
  const drawing = { type: "long", a: { time: candles[1].time, price: 100 }, b: { time: candles[9].time, price: 120 }, stopPrice: 95 };
  const moved = drawingMath.translatePosition(drawing, candles, 30, 1, 2);
  assert.equal(moved.a.time, candles[2].time);
  assert.equal(moved.b.time, candles[10].time);
  assert.equal(drawingMath.positionWidthBars(candles, moved.a.time, moved.b.time, 30), 8);
  assert.deepEqual([moved.a.price,moved.b.price,moved.stopPrice],[102,122,97]);
  assert.equal(drawing.b.time,candles[9].time);
  const back = drawingMath.translatePosition(moved,candles,30,-1,-2);
  assert.deepEqual(back,drawing);
});

test("legacy reversed position endpoints use one effective right edge for controls and editing", () => {
  assert.equal(typeof drawingMath.positionRightTime, "function");
  const legacy = { type: "long", a: { time: 1600, price: 100 }, b: { time: 1000, price: 120 } };
  const right = drawingMath.positionRightTime(legacy, [], 30);
  assert.equal(right,2200);
  assert.equal(drawingMath.positionWidthBars([],legacy.a.time,right,30),20);
  const edited = drawingMath.editPositionTime(legacy,"start",1630,right);
  assert.equal(edited.a.time,1630);
  assert.equal(edited.b.time,2200);
  assert.equal(legacy.b.time,1000);
});

test("saved toolbar order keeps custom tools and places positions immediately after Measure", () => {
  assert.equal(typeof chartState.drawingToolOrder, "function");
  const definitions = [["cursor"], ["line"], ["long"], ["short"], ["rect"], ["measure"]];
  const saved = ["rect", "long", "cursor", "measure", "line", "short"];
  assert.deepEqual(chartState.drawingToolOrder(definitions, saved), ["rect", "cursor", "line", "measure", "long", "short"]);
  assert.deepEqual(chartState.drawingToolOrder(definitions, ["line", "cursor", "rect", "measure"]), ["line", "cursor", "rect", "measure", "long", "short"]);
  assert.deepEqual(chartState.drawingToolOrder(definitions, null), ["cursor", "line", "rect", "measure", "long", "short"]);
  assert.deepEqual(saved, ["rect", "long", "cursor", "measure", "line", "short"]);
});
