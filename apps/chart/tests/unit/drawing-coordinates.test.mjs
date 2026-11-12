import test from "node:test";
import assert from "node:assert/strict";

import { resolveCanonicalChartPoint } from "../../src/chart/drawing-coordinates.js";
import * as drawingCoordinates from "../../src/chart/drawing-coordinates.js";
import { positionEndTime } from "../../src/drawings/drawing-math.js";
import { rawTimeToCoordinate } from "../../src/chart/view-transform.js";

test("position projection keeps actual candle spacing beyond a final market gap", () => {
  assert.equal(typeof drawingCoordinates.positionTimeToCoordinate, "function");
  const candles = [{ time: 1000 }, { time: 1030 }, { time: 5000 }];
  for (const spacing of [6, 0.25]) {
    const anchors = [{ rawIndex: 0, coordinate: 0 }, { rawIndex: 2, coordinate: spacing * 2 }];
    const options = { candles, timeframe: 30, barSpacing: spacing,
      timeToCoordinate: time => rawTimeToCoordinate(candles, time, anchors) };
    const start = drawingCoordinates.positionTimeToCoordinate({ ...options, time: 5000 });
    const end = drawingCoordinates.positionTimeToCoordinate({ ...options, time: positionEndTime(candles, 5000, 30) });
    assert.equal(end - start, spacing * 20);
    assert.equal(drawingCoordinates.positionTimeToCoordinate({ ...options, time: 5150 }), start + spacing * 5);
    assert.equal(drawingCoordinates.positionTimeToCoordinate({ ...options, time: 940 }), -spacing * 2);
  }
});

test("persisted position endpoints interpolate after switching to a coarser timeframe", () => {
  const candles = [{time:1200},{time:1260},{time:1320}];
  const options = {candles,timeframe:60,barSpacing:6,
    timeToCoordinate:time=>new Map([[1200,0],[1260,6],[1320,12]]).get(time) ?? null};
  assert.equal(drawingCoordinates.positionTimeToCoordinate({...options,time:1230}),3);
  assert.equal(drawingCoordinates.positionTimeToCoordinate({...options,time:1290}),9);
  assert.equal(drawingCoordinates.positionTimeToCoordinate({...options,time:1200}),0);
});

test("constrained drawing points persist canonical raw time under LOD", () => {
  const point = resolveCanonicalChartPoint({
    x: 125,
    y: 240,
    timeAtCoordinate: () => 1_788_787_290,
    priceAtCoordinate: () => 4401.25,
    fallback: { time: 123, price: 1 },
  });
  assert.deepEqual(point, { x: 125, y: 240, time: 1_788_787_290, price: 4401.25 });
});
