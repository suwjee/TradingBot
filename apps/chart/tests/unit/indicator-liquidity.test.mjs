import assert from "node:assert/strict";
import test from "node:test";
import { drawLiquidityLines } from "../../src/chart/indicator-liquidity.js";

const level = { sourceTime: 10, price: "100.125", visibleFrom: 30, lineEndTime: 210 };

function paint(levels, settings = {}) {
  const lines = [], labels = [];
  const ctx = {
    save() {}, restore() {}, beginPath() {}, rect() {}, clip() {}, setLineDash() {},
    moveTo(x, y) { lines.push(["move", x, y]); },
    lineTo(x, y) { lines.push(["line", x, y]); },
    measureText() { return { width: 34 }; },
    fillText(...args) { labels.push([...args, this.font]); },
    stroke() { lines.push([this.strokeStyle, this.lineWidth]); },
  };
  drawLiquidityLines(ctx, levels, {
    settings, timeToX: time => time, priceToY: price => price - 50, labelSizeAt: () => 10,
    width: 250, height: 120,
  });
  return { lines, labels };
}

test("liquidity uses a half-pixel grey line with a small centered label", () => {
  assert.deepEqual(paint([level]), {
    lines: [["move", 10, 50.5], ["line", 88, 50.5], ["move", 132, 50.5],
      ["line", 210, 50.5], ["#b8b8b8", 0.5]],
    labels: [["$$$", 110, 50.5, "500 10px system-ui, sans-serif"]],
  });
});

test("liquidity respects collected, active and repeated visibility and skips unpublished lines", () => {
  const collected = { ...level, collectedTime: 50 };
  const repeated = { ...collected, repeatGroupSourceTime: 5 };
  const unpublished = { ...level, visibleFrom: null };
  assert.equal(paint([level, collected, repeated, unpublished]).labels.length, 3);
  assert.equal(paint([level, collected, repeated], { liquidityCollectedVisible: false }).labels.length, 1);
  assert.equal(paint([level, collected, repeated], { liquidityActiveVisible: false }).labels.length, 2);
  assert.equal(paint([level, collected, repeated], { liquidityRepeatedVisible: false }).labels.length, 2);
});
