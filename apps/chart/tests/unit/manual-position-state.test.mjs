import test from "node:test";
import assert from "node:assert/strict";
import { drawingArray, normalizeHistorySnapshot } from "../../src/chart/state.js";

test("saved manual long and short drawings retain their order and position levels", () => {
  const line = { id: "line", type: "line" }, rect = { id: "rect", type: "rect" };
  const long = { id: "old-long", type: "long", a: { time: 30, price: 100 }, b: { time: 90, price: 110 }, stopPrice: 95 };
  const short = { id: "old-short", type: "short", a: { time: 30, price: 100 }, b: { time: 90, price: 90 }, stopPrice: 105 };
  const saved = [line, long, rect, short];
  assert.deepEqual(drawingArray({ drawings: saved }), saved);
});

test("undo snapshots retain manual positions and omit retired automatic annotations", () => {
  const native = { id: "native", type: "indicator-label", text: "S" };
  const generated = { id: "indicator:bullish:position:stable", type: "indicator-position",
    positionType: "1.1B", positionEdit: { bars: 34 } };
  const drawings = [{ id: "old", type: "long" }, { id: "measure", type: "measure" }];
  const snapshot = normalizeHistorySnapshot({
    drawings,
    indicatorObjects: [native, generated, { id: "buy", type: "indicator-position" },
      { id: "status", type: "indicator-label", setupStatusKind: "StopAll", text: "T" }],
  }, {});
  assert.deepEqual(snapshot, { drawings, indicatorObjects: [native, generated] });
});

