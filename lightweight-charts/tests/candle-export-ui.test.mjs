import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

const main = readFileSync(new URL("../src/main.js", import.meta.url), "utf8");
const ui = readFileSync(new URL("../src/candle-export.js", import.meta.url), "utf8");
const api = readFileSync(new URL("../plugins/faraz-candle-api.js", import.meta.url), "utf8");
const appCss = readFileSync(new URL("../src/styles/app.css", import.meta.url), "utf8");

test("FARAZ Exporter is directly below Dashboard and replaces the chart surface", () => {
  const dashboard = main.indexOf('["dashboard", "Dashboard", "dashboardBtn"]');
  const candle = main.indexOf('["exportCandles", "FARAZ Exporter", "candleExportBtn"]');
  const chart = main.indexOf('["candlestick_chart", "Chart", "chartNavBtn"]');
  assert.ok(dashboard >= 0 && dashboard < candle && candle < chart);
  assert.match(main, /root: \$\("\.chart-shell"\)/);
  assert.match(main, /selectWorkspaceNavigation\("candleExportBtn"\)/);
  assert.match(main, /candleExportBtn" \? icon\(name, 18\) : materialIcon\(name\)/);
  assert.match(ui, /FARAZ Exporter/);
});

test("authentication gates every extraction control and raw credentials stay absent from the UI", () => {
  assert.match(ui, /fieldset id="candleExportControls"[^>]*disabled/);
  assert.match(ui, /Export settings are locked until a valid FARAZ session is detected/);
  assert.match(ui, /controls\.disabled = !connected/);
  assert.doesNotMatch(ui, /document\.cookie|localStorage.*token|cookieValue|authorizationValue/i);
  assert.match(api, /primary-cache", "secret/);
  assert.match(api, /format: "clear-text"/);
  assert.doesNotMatch(ui, /id="candleExportClose"/);
});

test("count and exact Tehran range modes use the shared workstation picker", () => {
  assert.match(ui, /candleModeCount/);
  assert.match(ui, /candleModeRange/);
  assert.match(ui, /openDateTimePicker\("#candleRangeFrom"\)/);
  assert.match(ui, /parseTehranInput/);
  assert.match(ui, /UTC\+3\.5 Tehran/);
  assert.match(ui, /candleModeRange" class="active/);
});

test("source controls use fixed safety limits and icon actions", () => {
  assert.match(ui, /id="candleExportPacketSize" type="number" min="1" max="1000" value="1000"/);
  assert.match(ui, /id="candleExportRate" type="number" min="30"/);
  assert.match(ui, /candleSymbolAdd/);
  assert.match(ui, /candleSymbolRemove/);
  assert.match(ui, /FOREXCOM:XAUUSD/);
  assert.match(ui, /FXCM:USOIL/);
  assert.doesNotMatch(ui, /candleExportAdjust/);
  assert.match(ui, /The two default symbols cannot be removed/);
});

test("session controls support confirmed logout and footer connection state", () => {
  assert.match(ui, /Sign out of FARAZ/);
  assert.match(ui, /window\.confirm\("Sign out of FARAZ/);
  assert.match(ui, /\/api\/faraz\/auth\/logout/);
  assert.match(main, /farazStatusFooter/);
  assert.match(api, /clearStoredSession/);
  assert.match(api, /auth\/logout/);
  assert.doesNotMatch(api, /void authStatus\(\)\.catch/);
  assert.match(api, /never launch a browser or migrate an old profile/);
});

test("export settings and active operation survive chart navigation", () => {
  assert.match(ui, /qg:candle-export:v1/);
  assert.match(ui, /currentJobId/);
  assert.match(ui, /persistState\(\)/);
  assert.match(ui, /restoreState\(\)/);
});

test("native context menu is blocked only while the chart surface is active", () => {
  assert.match(main, /shell\.classList\.contains\("candle-export-active"\)\) return;\s*event\.preventDefault\(\)/);
});

test("FARAZ failures stay in the complete log, not the status heading", () => {
  assert.match(api, /timeoutMs: REQUEST_TIMEOUT_MS/);
  assert.doesNotMatch(api, /MAX_LOGS/);
  assert.doesNotMatch(ui, /logs\.slice\(-100\)/);
  assert.doesNotMatch(ui, /candleStatusMessage/);
  assert.match(api, /Packet \$\{chunk\.index \+ 1\}/);
  assert.match(api, /const retryable = true/);
});

test("FARAZ request context follows the last real FARAZ history request but is not required for manual credentials", () => {
  assert.match(api, /function captureHistoryRequest/);
  assert.match(api, /historyAuth\?\.adjustType \|\| "2"/);
  assert.match(api, /historyHost: historyAuth\?\.host/);
  assert.match(api, /firstDataRequest: chunk\.firstDataRequest, latest: chunk\.latest/);
  assert.doesNotMatch(api, /FARAZ history context is unavailable/);
  assert.match(api, /function endpointSymbolName/);
  assert.match(api, /endpoint: `\$\{url\.origin\}\$\{url\.pathname\}`/);
  assert.match(api, /auth\/browser/);
});

test("Exporter clears stale extraction state and limits checkbox activation to its control", () => {
  assert.doesNotMatch(ui, /<label class="candle-toggle-row">/);
  assert.match(ui, /id="candleStatusIcon"[^>]*data-state="idle"/);
  assert.match(ui, /function clearExtractionStatus\(\)/);
  assert.match(ui, /Extraction was not found/);
  assert.match(ui, /void refreshAuth\(\)/);
  assert.match(ui, /if \(visible\) refreshAuth\(\)/);
  assert.match(ui, /candleOpenFaraz/);
  assert.match(main, /Only the native checkbox hit target can toggle it/);
  assert.match(main, /label:has\(input\[type="checkbox"\]\)/);
  assert.match(ui, /candleValidationList/);
  assert.match(ui, /Saved file check/);
  assert.match(ui, /candleOpenFile/);
  assert.doesNotMatch(ui, /Download JSON/);
  assert.match(api, /verifySavedCandles/);
  assert.match(api, /candles\/open/);
});

test("header actions remain at fixed positions and timeframe pinning has no cap", () => {
  assert.match(main, /else pinnedTimeframes\.push\(seconds\)/);
  assert.doesNotMatch(main, /Only three timeframes can be pinned/);
  assert.match(ui, /icon\("web", 18\)/);
  assert.match(appCss, /\.top-actions \{ position: absolute; right: 6px/);
  assert.match(appCss, /\.top-drawing-tools \{[\s\S]*position: absolute; left: 50%/);
});

test("notifications pause while hovered and drawing controls are chart-only", () => {
  assert.match(main, /#toast"\)\.addEventListener\("mouseenter"/);
  assert.match(main, /#toast"\)\.addEventListener\("mouseleave"/);
  assert.match(main, /function setDrawingToolsActive\(active\)/);
  assert.match(main, /setDrawingToolsActive\(false\)/);
  assert.match(main, /if \(!chartWorkspaceActive\(\)\) return;/);
});

test("FARAZ belongs with Cache and side panels close outside chart", () => {
  assert.match(main, /status-cache[^]*status-faraz/);
  assert.match(main, /function chartWorkspaceActive\(\)/);
  assert.match(main, /if \(!chartWorkspaceActive\(\)\) return;/);
});

test("zoom culling is limited to reactions and Blue Lines", () => {
  const drawIndicator = main.slice(main.indexOf("function drawIndicator()"), main.indexOf("function drawIndicatorSelection()"));
  assert.equal((drawIndicator.match(/if \(!isTime(?:Range)?Visible/g) || []).length, 2);
  assert.match(drawIndicator, /reaction\.firstTime, reaction\.breakTime/);
  assert.match(drawIndicator, /blueLine\.sourceTime/);
});
