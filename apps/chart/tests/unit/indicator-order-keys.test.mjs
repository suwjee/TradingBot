import test from "node:test";
import assert from "node:assert/strict";
import { representedOrderKeys } from "../../src/chart/indicator-order-keys.js";

function original(group) {
  return new Set(
    [...(group.sZones || []), ...(group.eZones || []), ...(group.stopAlls || [])]
      .filter((item) => item.calculationValid !== false &&
        item.orderFirstIndex != null && item.orderBreakIndex != null)
      .map((item) => `${item.orderFirstIndex}:${item.orderBreakIndex}`),
  );
}

test("order-audit suppression keys preserve the exact legacy join, filters and Set identity", () => {
  const cases = [
    {},
    { sZones: [], eZones: [], stopAlls: [] },
    { sZones: [
      { orderFirstIndex: 0, orderBreakIndex: 0 },
      { orderFirstIndex: 0, orderBreakIndex: 0 },
      { orderFirstIndex: 0, orderBreakIndex: 3, calculationValid: false },
      { orderFirstIndex: null, orderBreakIndex: 4 },
      { orderFirstIndex: 1, orderBreakIndex: undefined },
    ], eZones: [
      { orderFirstIndex: "2", orderBreakIndex: 8 },
      { orderFirstIndex: 3, orderBreakIndex: 10 },
    ], stopAlls: [
      { orderFirstIndex: -1, orderBreakIndex: 22 },
      { orderFirstIndex: 2, orderBreakIndex: 8 },
    ] },
  ];
  for (const source of cases) {
    assert.deepEqual([...representedOrderKeys(source)], [...original(source)]);
  }
});

test("order-audit suppression keys are never persisted on mutable calculation segments", () => {
  const source = { sZones: [{ orderFirstIndex: 1, orderBreakIndex: 7 }] };
  const first = representedOrderKeys(source);
  source.sZones.push({ orderFirstIndex: 2, orderBreakIndex: 8 });
  const second = representedOrderKeys(source);
  assert.deepEqual([...first], ["1:7"]);
  assert.deepEqual([...second], ["1:7", "2:8"]);
  assert.deepEqual(Object.keys(source), ["sZones"]);
});

test("mixed Engine directions and alternating segments retain independent suppression membership", () => {
  const bullish = { sZones: [{ orderFirstIndex: 2, orderBreakIndex: 7 }] };
  const bearish = { eZones: [{ orderFirstIndex: 2, orderBreakIndex: 9 }] };
  assert.deepEqual([...representedOrderKeys(bullish)], [...original(bullish)]);
  assert.deepEqual([...representedOrderKeys(bearish)], [...original(bearish)]);
  assert.equal(representedOrderKeys(bullish).has("2:9"), false);
  assert.equal(representedOrderKeys(bearish).has("2:7"), false);
});

test("sparse arrays follow original spread behavior", () => {
  const sparse = new Array(3);
  sparse[1] = { orderFirstIndex: 1, orderBreakIndex: 5 };
  assert.throws(() => original({ sZones: sparse }), TypeError);
  assert.throws(() => representedOrderKeys({ sZones: sparse }), TypeError);
});
