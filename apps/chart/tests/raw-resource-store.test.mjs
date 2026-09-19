import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

test("RAW store writes compact candles with a broker and symbol metadata sidecar", async (t) => {
  const { createRawResourceStore } = await import("../server/raw-resource-store.js");
  const rootDir = fs.mkdtempSync(path.join(os.tmpdir(), "raw-store-"));
  t.after(() => fs.rmSync(rootDir, { recursive: true, force: true }));
  const candles = [
    { time: 100, open: 1, high: 2, low: 1, close: 2 },
    { time: 105, open: 2, high: 3, low: 2, close: 3 },
  ];
  const item = createRawResourceStore({ rootDir }).write({
    broker: "TEST", symbol: "PAIR", timeframe: "5S", candles,
    requestedRange: { from: 100, to: 105 }, source: "faraz",
  });
  assert.match(item.id, /^TEST\/PAIR\/RAW TEST_PAIR 5S FROM \d{4}-\d{2}-\d{2} /);
  assert.deepEqual(JSON.parse(fs.readFileSync(item.dataPath, "utf8")), candles);
  const metadata = JSON.parse(fs.readFileSync(item.metaPath, "utf8"));
  assert.equal(metadata.broker, "TEST");
  assert.equal(metadata.symbol, "PAIR");
  assert.equal(metadata.filename, path.basename(item.dataPath));
  assert.equal(metadata.count, candles.length);
  assert.equal(metadata.dataBytes, fs.statSync(item.dataPath).size);
  assert.equal(metadata.actualRange.from, "1970-01-01 03:31:40 Asia/Tehran");
  assert.equal(metadata.actualRange.to, "1970-01-01 03:31:45 Asia/Tehran");
  assert.equal(metadata.requestedRange.from, "1970-01-01 03:31:40 Asia/Tehran");
  assert.equal(metadata.requestedRange.to, "1970-01-01 03:31:45 Asia/Tehran");
  assert.equal(Object.hasOwn(metadata, "dataMtimeMs"), false);
  assert.equal(JSON.stringify(metadata).includes('"from":100'), false);
  assert.match(metadata.chartId, /^[0-9a-f-]{36}$/i);
  assert.equal(item.chartId, metadata.chartId);
});

test("RAW store heals a missing sidecar with a stable chart ID", async (t) => {
  const { createRawResourceStore } = await import("../server/raw-resource-store.js");
  const rootDir = fs.mkdtempSync(path.join(os.tmpdir(), "raw-chart-id-"));
  t.after(() => fs.rmSync(rootDir, { recursive: true, force: true }));
  const store = createRawResourceStore({ rootDir });
  const item = store.write({ broker: "FXCM", symbol: "ABC", timeframe: "5S", candles: [
    { time: 100, open: 1, high: 1, low: 1, close: 1 },
    { time: 105, open: 1, high: 1, low: 1, close: 1 },
  ] });
  fs.rmSync(item.metaPath);

  const healed = store.list()[0];
  assert.match(healed.chartId, /^[0-9a-f-]{36}$/i);
  assert.equal(JSON.parse(fs.readFileSync(item.metaPath, "utf8")).chartId, healed.chartId);
  assert.equal(store.list()[0].chartId, healed.chartId);
});

test("RAW store replaces an invalid chart ID and preserves an explicit chart ID", async (t) => {
  const { createRawResourceStore } = await import("../server/raw-resource-store.js");
  const rootDir = fs.mkdtempSync(path.join(os.tmpdir(), "raw-chart-id-invalid-"));
  t.after(() => fs.rmSync(rootDir, { recursive: true, force: true }));
  const store = createRawResourceStore({ rootDir });
  const item = store.write({
    broker: "FXCM", symbol: "ABC", timeframe: "5S",
    chartId: "11111111-1111-4111-8111-111111111111",
    candles: [{ time: 100, open: 1, high: 1, low: 1, close: 1 }],
  });
  assert.equal(item.chartId, "11111111-1111-4111-8111-111111111111");
  const metadata = JSON.parse(fs.readFileSync(item.metaPath, "utf8"));
  metadata.chartId = "not-a-uuid";
  fs.writeFileSync(item.metaPath, JSON.stringify(metadata));
  const healed = store.list()[0];
  assert.match(healed.chartId, /^[0-9a-f-]{36}$/i);
  assert.notEqual(healed.chartId, "not-a-uuid");
});

test("RAW store rejects traversal IDs and lists nested logical resources", async (t) => {
  const { createRawResourceStore } = await import("../server/raw-resource-store.js");
  const rootDir = fs.mkdtempSync(path.join(os.tmpdir(), "raw-store-"));
  t.after(() => fs.rmSync(rootDir, { recursive: true, force: true }));
  const store = createRawResourceStore({ rootDir });
  store.write({ broker: "FXCM", symbol: "ABC", timeframe: "5S", candles: [{ time: 100, open: 1, high: 1, low: 1, close: 1 }], source: "faraz" });
  assert.equal(store.resolve("../secret"), null);
  assert.equal(store.list().length, 1);
  assert.equal(store.list()[0].symbol, "ABC");
});

test("RAW store deletion removes the candle file and its metadata sidecar together", async (t) => {
  const { createRawResourceStore } = await import("../server/raw-resource-store.js");
  const rootDir = fs.mkdtempSync(path.join(os.tmpdir(), "raw-store-"));
  t.after(() => fs.rmSync(rootDir, { recursive: true, force: true }));
  const store = createRawResourceStore({ rootDir });
  const item = store.write({ broker: "FXCM", symbol: "ABC", timeframe: "5S", candles: [{ time: 100, open: 1, high: 1, low: 1, close: 1 }] });

  assert.equal(store.remove(item.id), true);
  assert.equal(fs.existsSync(item.dataPath), false);
  assert.equal(fs.existsSync(item.metaPath), false);
  assert.equal(store.list().length, 0);
});

test("RAW store reuses an identical identity but rejects different bytes at the same identity", async (t) => {
  const { createRawResourceStore } = await import("../server/raw-resource-store.js");
  const rootDir = fs.mkdtempSync(path.join(os.tmpdir(), "raw-collision-"));
  t.after(() => fs.rmSync(rootDir, { recursive: true, force: true }));
  const store = createRawResourceStore({ rootDir });
  const first = [{ time: 100, open: 1, high: 1, low: 1, close: 1 }];
  const different = [{ time: 100, open: 2, high: 2, low: 2, close: 2 }];
  const item = store.write({ broker: "FXCM", symbol: "USOIL", timeframe: "5S", candles: first });
  assert.equal(store.write({ broker: "FXCM", symbol: "USOIL", timeframe: "5S", candles: first }).id, item.id);
  assert.throws(() => store.write({ broker: "FXCM", symbol: "USOIL", timeframe: "5S", candles: different }), /different RAW file already exists/i);
});

test("RAW store records a human-readable gap checkpoint while hydrating runtime seconds", async (t) => {
  const { createRawResourceStore } = await import("../server/raw-resource-store.js");
  const rootDir = fs.mkdtempSync(path.join(os.tmpdir(), "raw-store-"));
  t.after(() => fs.rmSync(rootDir, { recursive: true, force: true }));
  const store = createRawResourceStore({ rootDir });
  const item = store.write({
    broker: "FXCM", symbol: "ABC", timeframe: "5S",
    candles: [{ time: 100, open: 1, high: 1, low: 1, close: 1 }, { time: 105, open: 1, high: 1, low: 1, close: 1 }],
  });

  store.recordFarazCoverage(item.id, {
    timeframeSeconds: 5,
    retryCount: 4,
    chartUpToDate: true,
    ranges: [{ from: 100, to: 105, status: "source_missing" }],
  });
  const recorded = store.recordFarazCoverage(item.id, {
    timeframeSeconds: 5,
    retryCount: 4,
    chartUpToDate: true,
    ranges: [{ from: 100, to: 105, status: "complete" }],
  });

  assert.equal(recorded.farazCoverage.chartUpToDate, true);
  assert.equal(recorded.farazCoverage.checkedFrom, 100);
  assert.equal(recorded.farazCoverage.checkedTo, 105);
  assert.deepEqual(recorded.farazCoverage.ranges.map(({ from, to, status }) => ({ from, to, status })), [
    { from: 100, to: 105, status: "complete" },
  ]);
  const persisted = JSON.parse(fs.readFileSync(item.metaPath, "utf8"));
  assert.equal(persisted.farazCoverage.checkedFrom, "1970-01-01 03:31:40 Asia/Tehran");
  assert.equal(persisted.farazCoverage.checkedTo, "1970-01-01 03:31:45 Asia/Tehran");
  assert.deepEqual(persisted.farazCoverage.ranges.map(({ from, to, status }) => ({ from, to, status })), [
    { from: "1970-01-01 03:31:40 Asia/Tehran", to: "1970-01-01 03:31:45 Asia/Tehran", status: "complete" },
  ]);
  assert.equal(/"(?:from|to|checkedFrom|checkedTo)":\s*\d/.test(JSON.stringify(persisted)), false);
});

test("FARAZ empty coverage marks only its own RAW file checked", async (t) => {
  const { createRawResourceStore } = await import("../server/raw-resource-store.js");
  const rootDir = fs.mkdtempSync(path.join(os.tmpdir(), "raw-coverage-scope-"));
  t.after(() => fs.rmSync(rootDir, { recursive: true, force: true }));
  const store = createRawResourceStore({ rootDir });
  const rows = [100, 105].map((time) => ({ time, open: 1, high: 1, low: 1, close: 1 }));
  const first = store.write({ broker: "FXCM", symbol: "ONE", timeframe: "5S", candles: rows });
  const second = store.write({ broker: "FXCM", symbol: "TWO", timeframe: "5S", candles: rows });
  const metadata = store.recordFarazCoverage(first.id, {
    timeframeSeconds: 5, ranges: [{ from: 100, to: 105, status: "source_missing" }],
  });
  assert.equal(metadata.farazCoverage.chartUpToDate, true);
  assert.equal(metadata.farazCoverage.status, "faraz_checked");
  assert.equal(store.list().find((item) => item.id === second.id).metadata.farazCoverage, undefined);
});

test("RAW store persists a readable gap-check checkpoint even when no gaps exist", async (t) => {
  const { createRawResourceStore } = await import("../server/raw-resource-store.js");
  const rootDir = fs.mkdtempSync(path.join(os.tmpdir(), "raw-checkpoint-"));
  t.after(() => fs.rmSync(rootDir, { recursive: true, force: true }));
  const store = createRawResourceStore({ rootDir });
  const rows = [100, 105].map((time) => ({ time, open: 1, high: 1, low: 1, close: 1 }));
  const item = store.write({ broker: "FXCM", symbol: "USOIL", timeframe: "5S", candles: rows });
  const runtime = store.recordFarazCoverage(item.id, { timeframeSeconds: 5, ranges: [], checkedThrough: 105, mode: "gap-full" });
  const persisted = JSON.parse(fs.readFileSync(item.metaPath, "utf8"));

  assert.equal(runtime.farazCoverage.checkedThrough, 105);
  assert.equal(persisted.farazCoverage.checkedThrough, "1970-01-01 03:31:45 Asia/Tehran");
  assert.equal(persisted.farazCoverage.lastMode, "gap-full");
});

test("RAW migration reports first and preserves the legacy file as migrated after applying", async (t) => {
  const { migrateFlatRawFiles } = await import("../server/migrate-raw-resources.js");
  const rootDir = fs.mkdtempSync(path.join(os.tmpdir(), "raw-migrate-"));
  t.after(() => fs.rmSync(rootDir, { recursive: true, force: true }));
  const legacy = path.join(rootDir, "RAW TEST_PAIR 5S FROM 100 TO 105.json");
  fs.writeFileSync(legacy, JSON.stringify([
    { time: 100, open: 1, high: 1, low: 1, close: 1 },
    { time: 105, open: 1, high: 1, low: 1, close: 1 },
  ]));
  assert.equal(migrateFlatRawFiles({ rootDir, apply: false }).candidates.length, 1);
  assert.equal(fs.existsSync(legacy), true);
  const report = migrateFlatRawFiles({ rootDir, apply: true });
  assert.equal(report.moved.length, 1);
  assert.equal(fs.existsSync(`${legacy}.migrated`), true);
  assert.match(report.moved[0].id, /^TEST\/PAIR\//);
});
