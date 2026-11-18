import test from "node:test";
import assert from "node:assert/strict";
import { drawTrueFalseLabel } from "../../src/chart/true-false-label.js";

test("T/F labels are smaller and sit beyond the native label in either direction", () => {
  const rendered = [];
  const ctx = {
    save() {},
    restore() {},
    fillText(text, x, y) {
      const [, weight, size] = /^(\d+) ([\d.]+)px/.exec(this.font);
      rendered.push({ text, x, y, weight: Number(weight), size: Number(size), color: this.fillStyle });
    },
  };
  drawTrueFalseLabel(ctx, "T", true, 12, 20, 40, true);
  drawTrueFalseLabel(ctx, "F", true, 9, 20, 40, false, 700);
  drawTrueFalseLabel(ctx, "T", false, 12, 20, 40, true);
  drawTrueFalseLabel(ctx, undefined, true, 12, 20, 40, true);
  drawTrueFalseLabel(ctx, null, true, 12, 20, 40, true, 700);
  drawTrueFalseLabel(ctx, null, false, 12, 20, 40, true, 700);
  assert.deepEqual(rendered.map(({ text }) => text), ["T", "F", "N/A"]);
  assert.equal(rendered[0].x, 20);
  assert.ok(rendered[0].y > 40);
  assert.ok(rendered[1].y < 40);
  assert.ok(rendered[0].size < 12);
  assert.ok(rendered[1].size < 9);
  assert.deepEqual(rendered.map(({ weight }) => weight), [300, 700, 300]);
  assert.equal(rendered[2].color, "#b8b8b8");
});
