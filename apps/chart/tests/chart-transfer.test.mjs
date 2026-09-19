import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

const candles = [
  { time: 100, open: 1, high: 2, low: 1, close: 2 },
  { time: 105, open: 2, high: 3, low: 2, close: 3 },
];

test("chart transfer bundle preserves the current RAW identity and drawings", async () => {
  const { createChartTransferBundle, validateChartTransferBundle } = await import("../server/chart-transfer.js");
  const bundle = createChartTransferBundle({
    item: {
      id: "FXCM/PAIR/RAW FXCM_PAIR 5S FROM 1970-01-01 03-31-40 TO 1970-01-01 03-31-45.json",
      broker: "FXCM",
      symbol: "PAIR",
      timeframe: "5S",
      metadata: { schemaVersion: 2, source: "faraz" },
    },
    candles,
    drawings: [{ id: "line-1", type: "trend", a: { time: 100, price: 1 }, b: { time: 105, price: 3 } }],
    drawingFilename: "RAW FXCM_PAIR 5S FROM 1970-01-01 03-31-40 TO 1970-01-01 03-31-45--1234567890abcdef.json",
  });

  assert.equal(bundle.kind, "tradingbot-chart-transfer");
  assert.equal(bundle.version, 1);
  assert.equal(bundle.manifest.sourceId, "FXCM/PAIR/RAW FXCM_PAIR 5S FROM 1970-01-01 03-31-40 TO 1970-01-01 03-31-45.json");
  assert.equal(bundle.manifest.rawFile, "RAW FXCM_PAIR 5S FROM 1970-01-01 03-31-40 TO 1970-01-01 03-31-45.json");
  assert.equal(bundle.manifest.metadataFile, "RAW FXCM_PAIR 5S FROM 1970-01-01 03-31-40 TO 1970-01-01 03-31-45.json.meta.json");
  assert.equal(bundle.manifest.drawingsFile, "RAW FXCM_PAIR 5S FROM 1970-01-01 03-31-40 TO 1970-01-01 03-31-45--1234567890abcdef.json");
  assert.deepEqual(validateChartTransferBundle(bundle).raw, candles);
  assert.equal(validateChartTransferBundle(bundle).drawings.length, 1);
});

test("chart transfer validation rejects malformed or unsafe bundles", async () => {
  const { validateChartTransferBundle } = await import("../server/chart-transfer.js");
  assert.throws(() => validateChartTransferBundle({}), /invalid chart transfer bundle/i);
  assert.throws(() => validateChartTransferBundle({
    kind: "tradingbot-chart-transfer",
    version: 1,
    manifest: { broker: "FXCM", symbol: "PAIR", timeframe: "5S", rawFile: "..\\raw.json", metadataFile: "meta.json", drawingsFile: "drawings.json" },
    raw: candles,
    drawings: [],
  }), /invalid chart transfer bundle/i);
  assert.throws(() => validateChartTransferBundle({
    kind: "tradingbot-chart-transfer",
    version: 1,
    manifest: { broker: "FXCM", symbol: "PAIR", timeframe: "5S", rawFile: "raw.json", metadataFile: "meta.json", drawingsFile: "drawings.json" },
    raw: candles,
    drawings: { bad: true },
  }), /invalid chart transfer bundle/i);
});

test("chart transfer import writes the canonical RAW resource and drawings together", async (t) => {
  const { createRawResourceStore } = await import("../server/raw-resource-store.js");
  const { createChartTransferBundle, importChartTransferBundle } = await import("../server/chart-transfer.js");
  const rootDir = fs.mkdtempSync(path.join(os.tmpdir(), "chart-transfer-"));
  t.after(() => fs.rmSync(rootDir, { recursive: true, force: true }));
  const store = createRawResourceStore({ rootDir });
  const source = createChartTransferBundle({
    item: {
      id: "FXCM/PAIR/RAW FXCM_PAIR 5S FROM 1970-01-01 03-31-40 TO 1970-01-01 03-31-45.json",
      broker: "FXCM", symbol: "PAIR", timeframe: "5S",
      metadata: { chartId: "123e4567-e89b-42d3-a456-426614174000", source: "faraz" },
    },
    candles,
    drawings: [{ id: "line-1", type: "trend", a: { time: 100, price: 1 } }],
    drawingFilename: "RAW FXCM_PAIR 5S FROM 1970-01-01 03-31-40 TO 1970-01-01 03-31-45--1234567890abcdef.json",
  });
  let saved = null;
  const result = importChartTransferBundle({ bundle: source, rawStore: store, saveDrawings: (item, drawings) => { saved = { item, drawings }; } });
  assert.equal(result.item.id, source.manifest.sourceId);
  assert.equal(result.item.chartId, "123e4567-e89b-42d3-a456-426614174000");
  assert.deepEqual(store.read(result.item.id), candles);
  assert.deepEqual(saved.drawings, source.drawings);
  assert.equal(store.list().find((item) => item.id === result.item.id).metadata.source, "transfer");
});
