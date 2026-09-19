import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

function candles() {
  return [100, 105, 110, 115].map((time, index) => ({
    time, open: index + 1, high: index + 2, low: index + 1, close: index + 2,
  }));
}

test("RAW cut selects inclusive candle endpoints and preserves chart ID in replace mode", async (t) => {
  const { createRawResourceStore } = await import("../server/raw-resource-store.js");
  const rootDir = fs.mkdtempSync(path.join(os.tmpdir(), "raw-cut-replace-"));
  t.after(() => fs.rmSync(rootDir, { recursive: true, force: true }));
  const store = createRawResourceStore({ rootDir });
  const original = store.write({ broker: "FXCM", symbol: "ABC", timeframe: "5S", candles: candles() });

  const result = store.cut(original.id, { from: 105, to: 110, mode: "replace" });
  assert.equal(result.mode, "replace");
  assert.equal(result.chartId, original.chartId);
  assert.equal(result.newId, "FXCM/ABC/RAW FXCM_ABC 5S FROM 1970-01-01 03-31-45 TO 1970-01-01 03-31-50.json");
  assert.deepEqual(store.read(result.newId), candles().slice(1, 3));
  assert.equal(store.resolve(original.id), null);
});

test("RAW cut creates a new chart identity without copying the original sidecar", async (t) => {
  const { createRawResourceStore } = await import("../server/raw-resource-store.js");
  const rootDir = fs.mkdtempSync(path.join(os.tmpdir(), "raw-cut-new-"));
  t.after(() => fs.rmSync(rootDir, { recursive: true, force: true }));
  const store = createRawResourceStore({ rootDir });
  const original = store.write({ broker: "FXCM", symbol: "ABC", timeframe: "5S", candles: candles() });

  const result = store.cut(original.id, { from: 105, to: 110, mode: "new" });
  assert.equal(result.mode, "new");
  assert.notEqual(result.chartId, original.chartId);
  assert.equal(store.resolve(original.id)?.id, original.id);
  assert.deepEqual(store.read(result.newId), candles().slice(1, 3));
});

test("each distinct new RAW cut receives its own chart identity", async (t) => {
  const { createRawResourceStore } = await import("../server/raw-resource-store.js");
  const rootDir = fs.mkdtempSync(path.join(os.tmpdir(), "raw-cut-identities-"));
  t.after(() => fs.rmSync(rootDir, { recursive: true, force: true }));
  const store = createRawResourceStore({ rootDir });
  const original = store.write({ broker: "FXCM", symbol: "ABC", timeframe: "5S", candles: candles() });

  const first = store.cut(original.id, { from: 100, to: 105, mode: "new" });
  const second = store.cut(original.id, { from: 110, to: 115, mode: "new" });
  assert.notEqual(first.newId, second.newId);
  assert.notEqual(first.chartId, second.chartId);
  assert.notEqual(first.chartId, original.chartId);
  assert.notEqual(second.chartId, original.chartId);
});

test("RAW cut rejects an empty or reversed selection", async (t) => {
  const { createRawResourceStore } = await import("../server/raw-resource-store.js");
  const rootDir = fs.mkdtempSync(path.join(os.tmpdir(), "raw-cut-invalid-"));
  t.after(() => fs.rmSync(rootDir, { recursive: true, force: true }));
  const store = createRawResourceStore({ rootDir });
  const original = store.write({ broker: "FXCM", symbol: "ABC", timeframe: "5S", candles: candles() });
  assert.throws(() => store.cut(original.id, { from: 111, to: 110, mode: "replace" }), /ordered/i);
  assert.throws(() => store.cut(original.id, { from: 116, to: 120, mode: "new" }), /no candles/i);
});
