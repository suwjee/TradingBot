import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";

import { rawInventoryPresentation, sortRawInventory } from "../src/features/raw-inventory.js";
import { fullChartId, shortChartId } from "../src/ui/chart-identity.js";

test("chart identity presentation keeps the full metadata value and an eight-character display label", () => {
  const full = "39c0ddad-ae8f-4538-bc8f-6247f140eae9";
  assert.equal(fullChartId(full), full);
  assert.equal(shortChartId(full), "39C0DDAD");
  assert.equal(shortChartId("ch-a71c55"), "CHA71C55");
  assert.equal(shortChartId(""), "NULL");
});

test("RAW inventory presents nested resource metadata without exposing a directory path as its name", () => {
  const row = rawInventoryPresentation({
    id: "FXCM/USOIL/RAW FXCM_USOIL 5S FROM 2026-09-11 02-53-30 TO 2026-09-15 11-03-45.json",
    chartId: "11111111-1111-4111-8111-111111111111",
    broker: "FXCM", symbol: "USOIL", timeframe: "5S", count: 2, bytes: 1048576,
    from: 100, to: 105,
  }, (time) => `T${time}`);

  assert.equal(row.filename, "RAW FXCM_USOIL 5S FROM 2026-09-11 02-53-30 TO 2026-09-15 11-03-45.json");
  assert.equal(row.title, "FXCM:USOIL");
  assert.equal(row.chartId, "11111111-1111-4111-8111-111111111111");
  assert.equal(row.detail, "5S · 2 candles · 1.00 MB");
  assert.equal(row.range, "T100 → T105");
});

test("RAW inventory keeps the exact filename separate from the broker-free symbol", () => {
  const row = rawInventoryPresentation({
    id: "FXCM/USOIL/RAW FXCM_USOIL 5S FROM 2026-09-11 02-53-30 TO 2026-09-15 11-03-45.json",
    broker: "FXCM", symbol: "FXCM:USOIL",
  }, (time) => `T${time}`);

  assert.equal(row.filename, "RAW FXCM_USOIL 5S FROM 2026-09-11 02-53-30 TO 2026-09-15 11-03-45.json");
  assert.equal(row.symbol, "USOIL");
});

test("RAW inventory sorts a data table by broker, symbol, and updated date", () => {
  const items = [
    { id: "b", broker: "FOREXCOM", symbol: "XAUUSD", updatedAt: "2026-09-14T00:00:00.000Z" },
    { id: "a", broker: "FXCM", symbol: "USOIL", updatedAt: "2026-09-15T00:00:00.000Z" },
  ];

  assert.deepEqual(sortRawInventory(items, { key: "broker", direction: "asc" }).map((item) => item.id), ["b", "a"]);
  assert.deepEqual(sortRawInventory(items, { key: "updatedAt", direction: "desc" }).map((item) => item.id), ["a", "b"]);
  assert.deepEqual(sortRawInventory([{ id: "twelve", count: 12 }, { id: "two", count: 2 }], { key: "count", direction: "asc" }).map((item) => item.id), ["two", "twelve"]);
});

test("RAW inventory exposes From and To as sortable timestamp columns", () => {
  const exporterSource = fs.readFileSync(path.resolve("src/features/candle-export.js"), "utf8");

  assert.match(exporterSource, /data-raw-sort-key="from"/);
  assert.match(exporterSource, /data-raw-sort-key="to"/);
  assert.deepEqual(sortRawInventory([
    { id: "later", from: 20, to: 40 },
    { id: "earlier", from: 10, to: 30 },
  ], { key: "from", direction: "asc" }).map((item) => item.id), ["earlier", "later"]);
  assert.deepEqual(sortRawInventory([
    { id: "later", from: 20, to: 40 },
    { id: "earlier", from: 10, to: 30 },
  ], { key: "to", direction: "desc" }).map((item) => item.id), ["later", "earlier"]);
});

test("RAW table leads with its exact filename and receives live inventory changes", () => {
  const exporterSource = fs.readFileSync(path.resolve("src/features/candle-export.js"), "utf8");
  const mainSource = fs.readFileSync(path.resolve("src/main.js"), "utf8");

  assert.match(exporterSource, /data-raw-sort-key="filename">File name/);
  assert.match(exporterSource, /const cells = \[row\.filename, row\.symbol,/);
  assert.match(exporterSource, /syncRawInventory\(items\)/);
  assert.match(mainSource, /candleExportController\?\.syncRawInventory\(nextInventory\)/);
  assert.match(mainSource, /function setUpdateButtonState\(state\)/);
});

test("symbol rows display compact IDs with an accessible copy action and collapsible groups", () => {
  const source = fs.readFileSync(path.resolve("src/main.js"), "utf8");

  assert.match(source, /shortChartId\(item\.chartId\)/);
  assert.match(source, /data-copy-chart-id=/);
  assert.match(source, /data-symbol-group=/);
  assert.match(source, /collapsedSymbolGroups/);
});

test("FARAZ current-time controls expose a live timestamp outside the hidden date row", () => {
  const source = fs.readFileSync(path.resolve("src/features/candle-export.js"), "utf8");

  assert.match(source, /data-current-time-output="count"/);
  assert.match(source, /data-current-time-output="range"/);
  assert.match(source, /renderReadableTimes\(\)/);
  assert.match(source, /Date\.now\(\) \/ 1000/);
});

test("RAW file names use compact table typography", () => {
  const styles = fs.readFileSync(path.resolve("src/styles/candle-export.css"), "utf8");

  assert.match(styles, /\.candle-raw-table td:first-child[^}]*font-size:\s*11px/);
});
