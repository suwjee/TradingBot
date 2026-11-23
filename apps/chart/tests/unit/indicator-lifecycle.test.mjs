import test from "node:test";
import assert from "node:assert/strict";
import { engineCalculationDuration } from "../../src/features/indicator-lifecycle.js";

test("indicator timing belongs to the calculation payload and can be absent in older cached data", () => {
  assert.equal(engineCalculationDuration({ timings: { bridgeTotalMs: 61_250, phasesMs: { Prepare: 25 } } }), 61_250);
  assert.equal(engineCalculationDuration({ timings: { bridgeTotalMs: 0 } }), 0);
  assert.equal(engineCalculationDuration({ timings: { bridgeTotalMs: -1 } }), null);
  assert.equal(engineCalculationDuration({ timings: { phasesMs: { Prepare: 250 } } }), null);
  assert.equal(engineCalculationDuration({}), null);
});

test("saved indicator preferences never restore an active calculation", async () => {
  const { restoreIndicatorLifecycle } = await import("../../src/features/indicator-lifecycle.js");
  const restored = restoreIndicatorLifecycle({
    form: { controls: { indicatorTf: "follow" }, direction: "bullish" },
    enabled: true,
    resultContext: { fileId: "FARAZ/ABC/file.json" },
  });

  assert.deepEqual(restored.form, { controls: { indicatorTf: "follow" }, direction: "bullish" });
  assert.equal(restored.active, false);
  assert.equal(restored.resultContext, null);
});

test("legacy visibility settings migrate to the three verdict groups and linked primary items", async () => {
  const { migrateIndicatorVisibility } = await import("../../src/features/indicator-lifecycle.js");
  assert.deepEqual(migrateIndicatorVisibility({
    trueFalseVisible: false, secondaryTfVisible: true,
    phVisible: false, phLabelVisible: false, plVisible: false, plLabelVisible: true,
    mblGroupVisible: false, mblVisible: true, indicatorTf: "follow",
  }), {
    foundationTfVisible: false, secondaryTfVisible: true, primaryTfVisible: false,
    phGroupVisible: false, plGroupVisible: true, mblGroupVisible: false, indicatorTf: "follow",
  });
  assert.deepEqual(migrateIndicatorVisibility({}), {});
});
