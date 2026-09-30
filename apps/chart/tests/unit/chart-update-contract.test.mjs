import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";

const mainSource = fs.readFileSync(path.resolve("src/main.js"), "utf8");
const exporterSource = fs.readFileSync(path.resolve("src/features/candle-export.js"), "utf8");
const appCss = fs.readFileSync(path.resolve("src/styles/app.css"), "utf8");
const viteSource = fs.readFileSync(path.resolve("vite.config.js"), "utf8");

test("chart updates send the FARAZ request with the selected broker and symbol", () => {
  assert.match(mainSource, /const symbol = formatSymbolWithBroker\(state\.file\);/);
});

test("symbol selection leaves Update Chart Data idle until its own FARAZ update", () => {
  assert.match(mainSource, /renderTf\(\);\s*setUpdateButtonState\("idle"\);\s*log\.chart\.info\("SYMBOL_LOAD_COMPLETED"/);
  assert.doesNotMatch(mainSource, /setRawGapWarning\(/);
  assert.doesNotMatch(mainSource, /updateResolutionModal/);
  assert.match(mainSource, /buildGapDetectionRanges\(state\.raw, rawTimeframeSeconds/);
  assert.match(mainSource, /buildLatestCandleRange\(state\.raw, rawTimeframeSeconds, now\)/);
});

test("Update Chart Data opens a required single-choice operation dialog", () => {
  assert.match(mainSource, /id="updateChoiceModal"/);
  assert.match(mainSource, /type="radio" name="chartUpdateMode" value="gap-full"/);
  assert.match(mainSource, /type="radio" name="chartUpdateMode" value="gap-since"/);
  assert.match(mainSource, /type="radio" name="chartUpdateMode" value="latest"/);
  assert.match(mainSource, /id="runChartUpdate"/);
  assert.match(mainSource, /runChartUpdate\(selectedChartUpdateMode\(\)\)/);
});

test("FARAZ session checks repair a persisted broker-free chart symbol", () => {
  assert.match(exporterSource, /function farazSymbol\(value\)/);
  assert.match(exporterSource, /saved\.symbols\.filter\(isQualifiedFarazSymbol\)/);
  assert.match(exporterSource, /normalizeFarazSymbol\(value, defaultSymbol\)/);
  assert.match(exporterSource, /symbolName: farazSymbol\(\$id\(view, "candleExportSymbol"\)\.value\.trim\(\)\)/);
});

test("choosing a newer symbol aborts the obsolete chart-file request", () => {
  assert.match(mainSource, /symbolLoadController\?\.abort\(\)/);
  assert.match(mainSource, /signal:\s*controller\.signal/);
  assert.match(mainSource, /if \(loadRevision !== symbolLoadRevision\) return;/);
});

test("symbol inventory exposes non-secret RAW coverage metadata to chart updates", () => {
  assert.match(viteSource, /metadata:\s*item\.metadata,/);
});

test("loading one chart resolves only its requested RAW file instead of scanning the inventory", () => {
  const candleEndpoint = viteSource.split("server.middlewares.use('/api/candles'")[1]
    .split("server.middlewares.use('/api/reactions/cache'")[0];
  assert.match(candleEndpoint, /const resource = rawStore\.resolve\(id\);/);
  assert.doesNotMatch(candleEndpoint, /inventory\(\)\.find/);
});

test("chart import and export keep the source filenames in the transfer manifest", () => {
  assert.match(mainSource, /chartTransferBtn/);
  assert.match(mainSource, /showDirectoryPicker\(\{ mode: "readwrite" \}\)/);
  assert.match(mainSource, /bundle\.manifest\.rawFile/);
  assert.match(mainSource, /bundle\.manifest\.metadataFile/);
  assert.match(mainSource, /bundle\.manifest\.drawingsFile/);
  assert.match(viteSource, /\/api\/chart-transfer\/export/);
  assert.match(viteSource, /drawingFilename: path\.basename\(target\)/);
  assert.match(viteSource, /\/api\/chart-transfer\/import/);
});

test("deleting a chart removes its RAW file and durable chart artifacts", () => {
  const deleteEndpoint = viteSource.split("server.middlewares.use('/api/candle-files/delete'")[1]
    .split("server.middlewares.use('/api/candle-files/cut'")[0];
  assert.match(deleteEndpoint, /rawStore\.remove\(valid\.id\)/);
  assert.match(deleteEndpoint, /removeChartArtifacts\(valid\)/);
  assert.match(mainSource, /market-canvas:\$\{item\.chartId \|\| item\.id\}:drawings/);
});

test("inventory refreshes coalesce while a symbols request is already running", () => {
  assert.match(mainSource, /let inventoryRefreshPromise = null/);
  assert.match(mainSource, /if \(inventoryRefreshPromise\) return inventoryRefreshPromise/);
  assert.match(mainSource, /trackedRefresh = refresh\.finally/);
});
