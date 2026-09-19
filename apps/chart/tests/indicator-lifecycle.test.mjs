import test from "node:test";
import assert from "node:assert/strict";

test("saved indicator preferences never restore an active calculation", async () => {
  const { restoreIndicatorLifecycle } = await import("../src/features/indicator-lifecycle.js");
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
  const { appliedContextMatches } = await import("../src/features/indicator-lifecycle.js");
  const applied = {
    fileId: "FARAZ/ABC/file.json", symbol: "ABC", chartTimeframe: 5,
    analysisTimeframe: 5, from: 100, to: 200, direction: "bullish",
  };
  assert.equal(appliedContextMatches(applied, { ...applied }), true);
  assert.equal(appliedContextMatches(applied, { ...applied, chartTimeframe: 60 }), false);
  assert.equal(appliedContextMatches(applied, { ...applied, fileId: "FARAZ/XYZ/file.json" }), false);
});
