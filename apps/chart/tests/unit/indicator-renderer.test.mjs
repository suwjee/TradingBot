import test from "node:test";
import assert from "node:assert/strict";
import { drawIndicator } from "../../src/chart/indicator-renderer.js";

test("A, S, E and StopAll render at the default dimensions and honor style overrides", () => {
  const fontSizes = {};
  const radii = [];
  const ctx = {
    save() {},
    restore() {},
    beginPath() {},
    fill() {},
    stroke() {},
    arc(_x, _y, radius) { radii.push(radius); },
    fillText(label) { fontSizes[label] = Number(/ (\d+)px/.exec(this.font)[1]); },
  };
  const settings = { aVisible: true, sVisible: true, eVisible: true, stopAllVisible: true };
  const dependencies = {
    ctx,
    state: {
      indicator: {
        enabled: true,
        settings,
        results: { directions: { bullish: {
          reactions: [],
          aZones: [{ sourceIndex: 1, sourceTime: 30, price: 100 }],
          sZones: [{ sourceIndex: 2, sourceTime: 60, price: 100 }],
          eZones: [{ sourceIndex: 3, sourceTime: 90, price: 100, number: 1 }],
          stopAlls: [{ sourceIndex: 4, sourceTime: 120, price: 100, number: 2 }],
        } } },
      },
    },
    indicatorTimeToCoordinate: (time) => time,
    priceToY: (price) => price,
    indicatorObject: () => null,
    offsetIndicatorPoint: (_object, x, y) => ({ x, y }),
    rgba: () => "#fff",
  };

  drawIndicator(200, 200, dependencies);
  assert.deepEqual(fontSizes, { A: 10, S: 10, E1: 10, 2: 14 });
  assert.deepEqual(radii, [5]);

  Object.assign(settings, { aSize: 12, sSize: 13, eSize: 16, stopAllSize: 20, stopAllRadius: 8 });
  drawIndicator(200, 200, dependencies);
  assert.deepEqual(fontSizes, { A: 12, S: 13, E1: 16, 2: 20 });
  assert.deepEqual(radii, [5, 8]);
});
