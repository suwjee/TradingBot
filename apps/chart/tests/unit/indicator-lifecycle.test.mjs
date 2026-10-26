import test from "node:test";
import assert from "node:assert/strict";

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

test("an applied result becomes invalid when its chart context changes", async () => {
  const { appliedContextMatches } = await import("../../src/features/indicator-lifecycle.js");
  const applied = {
    fileId: "FARAZ/ABC/file.json", symbol: "ABC", chartTimeframe: 5,
    analysisTimeframe: 5, from: 100, to: 200, direction: "bullish",
  };
  assert.equal(appliedContextMatches(applied, { ...applied }), true);
  assert.equal(appliedContextMatches(applied, { ...applied, chartTimeframe: 60 }), false);
  assert.equal(appliedContextMatches(applied, { ...applied, fileId: "FARAZ/XYZ/file.json" }), false);
});

const context = {
  fileId: "FARAZ/ABC/file.json", symbol: "ABC", chartTimeframe: 30,
  analysisTimeframe: 30, from: 100, to: 200, direction: "bearish",
};

test("same chart context cannot reuse a result from earlier calculation source", async () => {
  const { canReuseAppliedCalculation } = await import("../../src/features/indicator-lifecycle.js");
  assert.equal(canReuseAppliedCalculation({ ...context, sourceFingerprint: "source-before" }, context, "source-after"), false);
});

test("unchanged calculation source preserves visual-only result reuse", async () => {
  const { canReuseAppliedCalculation } = await import("../../src/features/indicator-lifecycle.js");
  const applied = { ...context, sourceFingerprint: "current-source", settings: { phVisible: true, primaryArrowColor: "#056656" } };
  const next = { ...context, settings: { phVisible: false, primaryArrowColor: "#123456" } };
  assert.equal(canReuseAppliedCalculation(applied, next, "current-source"), true);
});

test("unverified source identity never enables local result reuse", async () => {
  const { canReuseAppliedCalculation } = await import("../../src/features/indicator-lifecycle.js");
  for (const missing of [undefined, null, "", "   ", 12]) {
    assert.equal(canReuseAppliedCalculation({ ...context, sourceFingerprint: "current-source" }, context, missing), false);
    assert.equal(canReuseAppliedCalculation({ ...context, sourceFingerprint: missing }, context, "current-source"), false);
  }
});

test("matching source identity cannot reuse a different chart context", async () => {
  const { canReuseAppliedCalculation } = await import("../../src/features/indicator-lifecycle.js");
  const applied = { ...context, sourceFingerprint: "current-source" };
  assert.equal(canReuseAppliedCalculation(applied, { ...context, to: 300 }, "current-source"), false);
  assert.equal(canReuseAppliedCalculation(applied, { ...context, direction: "bullish" }, "current-source"), false);
  assert.equal(canReuseAppliedCalculation(null, context, "current-source"), false);
});
