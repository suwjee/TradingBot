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
