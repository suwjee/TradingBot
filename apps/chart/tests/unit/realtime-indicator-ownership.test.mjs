import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import vm from "node:vm";
import { readRealtimeUpdate } from "../../src/features/realtime-chart.js";
import { errorDetails } from "../../src/features/diagnostic-details.js";
import { startLiveIndicatorProgress } from "../../src/features/indicator-live-progress.js";
import { engineCalculationDuration } from "../../src/features/indicator-lifecycle.js";

const main = await readFile(new URL("../../src/main.js", import.meta.url), "utf8");
const indicatorFlow = main.slice(main.indexOf("let chartUpdateRunning = false;") + "let chartUpdateRunning = false;".length,
  main.indexOf("function moveRealtimeIndicatorPreferences("));
const updateFlow = main.slice(main.indexOf("async function runRealtimeChartUpdate("),
  main.indexOf("function setUpdateButtonState("));
const inventoryFlow = main.slice(main.indexOf("let inventoryRefreshPromise = null;"), main.indexOf("async function loadFile("));
const tabId = "same-tab-fixture";
const proof = to => ({ chartId: "chart", tabId, to,
  request: { from: 100, to: 200, direction: "bearish", timeframe: 30, chartTimeframe: 30, blueLines: true, bridgeOutput: true } });

function fixture({ candles = [{ time: 330 }], corrections = [], onContinue, checkService, nextRaw, nextRecent, marketAvailable = true,
  candleConflict, refreshInventory,
  alertsReady = false, connectProgress = () => null, supportsRecentVerification = () => true } = {}) {
  const originalResult = { directions: { bearish: {} } };
  const state = {
    file: { id: "old.json", chartId: "chart", to: 300, timeframe: "5S", metadata: { dataSha256: "old" } },
    raw: [{ time: 300 }],
    data: [{ time: 300 }],
    tf: 30,
    indicator: {
      enabled: true,
      settings: { direction: "bullish" },
      results: originalResult,
      objects: [{ id: "old-result-object" }],
      resultContext: { fileId: "old.json", chartId: "chart", from: 100, to: 200,
        chartTimeframe: 30, analysisTimeframe: 30, direction: "bearish",
        liveSessionId: "checkpoint", liveProof: proof(200), sourceFingerprint: "source" },
    },
    indicatorRange: {},
    drawings: [{ id: "position" }],
  };
  const controls = { "#indicatorFrom": { value: "100" }, "#indicatorTo": { value: "200" }, "#indicatorEnabled": { checked: false } };
  const payload = { directions: { bearish: { reactions: [], resets: [] } }, timeframe: 30,
    timings: { bridgeTotalMs: 62_500 } };
  const requests = [], rebuilt = [], failures = [], alertPublications = [];
  const rawResponse = {
    file: { ...state.file, id: candles.length ? "new.json" : state.file.id,
      to: candles.at(-1)?.time ?? state.file.to, count: state.raw.length + candles.length },
    candles,
    corrections,
  };
  const noop = () => {};
  let progressRequestCount = 0;
  const sandbox = vm.createContext({
    state, AbortController, AbortSignal, performance, readRealtimeUpdate, engineCalculationDuration, errorDetails,
    setTimeout: callback => setImmediate(callback), clearTimeout: clearImmediate, LOCAL_CHART_RESTART_GRACE_MS: 75_000,
    symbolLoadController: null, symbolLoadRevision: 1,
    liveIndicatorTabId: tabId,
    createUniqueId: () => ++progressRequestCount === 1 ? "live-progress-fixture" : `live-progress-fixture-${progressRequestCount}`,
    startLiveIndicatorProgress: options => startLiveIndicatorProgress({ ...options, connect: connectProgress }),
    alertLiveReady: alertsReady, formatSymbolWithBroker: file => file.id,
    alertController: {
      baseline: time => alertPublications.push({ kind: "baseline", time }),
      advance: (result, time, symbol) => alertPublications.push({ kind: "advance", result, time, symbol }),
    },
    indicatorCalculationOwner: null, indicatorRestoreController: null, indicatorCacheClearing: false,
    realtimeUpdateOwner: null, chartUpdateRunning: false, setFooterCacheStatus: noop,
    lowerBoundTime: (rows, time) => rows.findIndex(row => row.time >= time),
    clone: structuredClone, removeInvalidIndicatorCalculations: value => value,
    calculationKey: ({ direction }, from, to) => [direction, from, to].join(":"),
    rebuildIndicatorObjects: options => rebuilt.push(options),
    $: selector => controls[selector], parseTehranInput: Number, inputFromTehran: String,
    setDateTimeValue: (selector, value) => { controls[selector].value = value; },
    scheduleDraw: noop, saveChartIndicatorContext: noop, renderIndicatorInfo: noop, renderObjectTree: noop, updateToolbar: noop,
    pushIndicatorActivity: noop,
    indicatorSettings: () => ({}), setIndicatorVisibility: enabled => { state.indicator.enabled = enabled; },
    log: { chart: { info: noop, warn: noop, error: name => failures.push(name) },
      indicator: { info: noop, warn: name => failures.push(name), error: noop } },
    refreshSymbolInventory: async () => refreshInventory?.(state),
    applyRealtimeCandles(file, rows, corrected, gapCandles = []) {
      state.file = file;
      for (const row of corrected) state.raw[state.raw.findIndex(old => old.time === row.time)] = row;
      state.raw.push(...rows, ...gapCandles);
      if (gapCandles.length) state.raw.sort((a, b) => a.time - b.time);
      state.data = state.raw.slice();
    },
    async fetch(url, options) {
      if (url === "/api/reactions/source") return checkService?.(options) ?? { ok: false, status: 503 };
      requests.push([url, JSON.parse(options.body)]);
      if (url === "/api/candle-files/realtime") {
        const body = JSON.parse(options.body);
        if (candleConflict) return { status: 409, json: async () => ({ code: candleConflict }) };
        if (body.phase === "recent") {
          return { status: 200, json: async () => nextRecent ? nextRecent(state, body) :
            { file: { ...state.file, count: state.raw.length }, candles: [], verification: { status: "verified" } } };
        }
        const response = async () => ({
          ...(supportsRecentVerification() && { supportsRecentVerification: true }),
          ...(nextRaw ? await nextRaw(state, body) : rawResponse),
        });
        if (nextRaw) return { status: 200, json: response };
        return marketAvailable ? { ok: true, status: 200, json: response }
          : { ok: false, status: 503, json: async () => ({ error: "FARAZ unavailable." }) };
      }
      if (onContinue) return onContinue(url, options);
      return {
        ok: true, status: 200, json: async () => payload,
        headers: new Map([["X-QG-Calculation-Id", "new-calculation"], ["X-QG-Source-Fingerprint", "source"],
          ["X-QG-Live-Proof", JSON.stringify(proof(state.raw.at(-1).time))]]),
      };
    },
  });
  vm.runInContext(indicatorFlow + updateFlow, sandbox);
  const rawAbort = new AbortController();
  const indicatorAbort = new AbortController();
  return { state, originalResult, payload, requests, rebuilt, controls, indicatorAbort, failures, alertPublications,
    async update(overrides) {
      sandbox.request = { chartId: "chart", signal: rawAbort.signal,
        indicatorSignal: indicatorAbort.signal, indicatorCalculation: true, ...overrides };
      const raw = await vm.runInContext("runRealtimeChartUpdate(request)", sandbox);
      if (!raw?.indicatorUpdate) return raw;
      const indicator = await raw.indicatorUpdate;
      const status = [raw.status, indicator?.status].filter(Boolean).join(" ");
      return raw.verification ? { status, verification: raw.verification } : status;
    },
  };
}

test("an accepted continuation publishes the result to the alert monitor with the closed RAW tail", async () => {
  const chart = fixture({ alertsReady: true });
  await chart.update();
  assert.deepEqual(chart.alertPublications, [{ kind: "advance", result: chart.payload, time: 330, symbol: "new.json" }]);
  assert.equal(chart.state.indicator.lastCalculation?.durationMs, 62_500);
});

test("inventory applies a proven RAW rename as an append and immediately requests indicator continuation", async () => {
  const previous = { id: "old.json", chartId: "chart", count: 1, from: 300, to: 300, metadata: { dataSha256: "old" } };
  const coverage = { verifiedCount: 1, totalCount: 2, status: "pending" };
  const updated = { ...previous, id: "new.json", count: 2, to: 330,
    metadata: { dataSha256: "new", candleVerification: coverage } };
  const state = { file: previous, raw: [{ time: 300 }], inventory: [previous] };
  const requests = [], actions = [];
  const sandbox = vm.createContext({
    state, AbortController, AbortSignal, setTimeout, clearTimeout, inventoryRefreshPromise: null,
    realtimeUpdateOwner: null, indicatorCalculationOwner: null, realtimePublicationRevision: 0,
    symbolLoadRevision: 0, symbolLoadController: null, inventorySignature: JSON.stringify, candleExportController: null,
    renderSymbolList() {}, log: { chart: { info() {}, warn() {} } },
    realtimeChart: { requestIndicatorUpdate: () => actions.push("continue"),
      useStoredVerification: (chartId, value) => actions.push([chartId, value]) },
    applyRealtimeCandles(file, candles) { actions.push("append"); state.file = file; state.raw.push(...candles); },
    loadFile: () => actions.push("reload"),
    fetch: async (url, options) => {
      if (url === "/api/symbols") return { ok: true, json: async () => [updated] };
      requests.push([url, JSON.parse(options.body)]);
      return { ok: true, json: async () => ({ file: updated, candles: [{ time: 330 }] }) };
    },
  });
  vm.runInContext(inventoryFlow, sandbox);
  await vm.runInContext("refreshSymbolInventory()", sandbox);
  assert.deepEqual(requests, [["/api/candle-files/realtime", {
    id: "old.json", chartId: "chart", lastCandleTime: 300, baseSha256: "old", phase: "replay",
  }]]);
  assert.deepEqual(actions, ["append", ["chart", coverage], "continue"]);
  assert.equal(state.file, updated);
  assert.equal(state.raw.at(-1).time, 330);
});

test("startup retries an inventory timeout during the response body once", async () => {
  const item = { id: "loaded.json", chartId: "loaded" };
  const state = { file: null, inventory: [] };
  const timeout = Object.assign(new Error("Inventory response timed out"), { name: "TimeoutError" });
  let attempts = 0;
  const sandbox = vm.createContext({
    state, AbortSignal, inventoryRefreshPromise: null, realtimeUpdateOwner: null, indicatorCalculationOwner: null,
    realtimePublicationRevision: 0, inventorySignature: JSON.stringify, candleExportController: null,
    renderSymbolList() {}, log: { chart: { info() {} } },
    async fetch(url) {
      assert.equal(url, "/api/symbols");
      const attempt = ++attempts;
      return { ok: true, async json() { if (attempt === 1) throw timeout; return [item]; } };
    },
  });
  vm.runInContext(inventoryFlow, sandbox);
  await vm.runInContext("refreshSymbolInventory({ initial: true })", sandbox);
  assert.equal(attempts, 2);
  assert.deepEqual(state.inventory, [item]);
});

test("background inventory treats the server restart as transient and reports a prolonged outage once", async () => {
  let now = 1_000;
  let offline = true;
  const warnings = [];
  const state = { file: null, inventory: [] };
  const sandbox = vm.createContext({
    state, AbortSignal, Date: { now: () => now }, LOCAL_CHART_RESTART_GRACE_MS: 75_000,
    indicatorCalculationOwner: null, realtimeUpdateOwner: null, realtimePublicationRevision: 0, journalUnavailable: false,
    errorDetails, log: { chart: { warn: event => warnings.push(event) } },
    async fetch() {
      if (offline) throw new TypeError("Failed to fetch");
      return { ok: true, async json() { return []; } };
    },
  });
  vm.runInContext(inventoryFlow, sandbox);
  const refresh = () => vm.runInContext("refreshSymbolInventory({ background: true })", sandbox);
  assert.equal(await refresh(), false);
  now += 9_000;
  assert.equal(await refresh(), false);
  assert.deepEqual(warnings, []);
  now += 66_000;
  await refresh();
  await refresh();
  assert.deepEqual(warnings, ["LOCAL_CHART_SERVICE_UNAVAILABLE"]);
  offline = false;
  await refresh();
  offline = true;
  now += 1_000;
  await refresh();
  assert.deepEqual(warnings, ["LOCAL_CHART_SERVICE_UNAVAILABLE"]);
});

test("a historical repair refreshes the alert baseline without evaluating a trigger", async () => {
  const chart = fixture({ alertsReady: true, candles: [], corrections: [{ time: 300 }] });
  chart.state.indicator.resultContext.to = 300;
  await chart.update({ indicatorCalculation: false, verifyAll: true });
  assert.deepEqual(chart.alertPublications, [{ kind: "baseline", time: 300 }]);
});

test("the accepted checkpoint follows the published RAW rename and retains the chosen start and direction", async () => {
  const chart = fixture();
  assert.match((await chart.update()).status, /Added 1.*Indicator updated/);
  assert.deepEqual(chart.requests.find(([url]) => url === "/api/reactions/continue"), ["/api/reactions/continue",
    { id: "new.json", chartId: "chart", sessionId: "checkpoint", tabId, proof: proof(200), rawSha256: "old" }]);
  assert.equal(chart.state.indicator.results, chart.payload);
  assert.equal(chart.state.indicator.resultContext.from, 100);
  assert.equal(chart.state.indicator.resultContext.direction, "bearish");
  assert.equal(chart.state.indicator.resultContext.to, 330);
  assert.equal(chart.state.indicator.resultContext.calculationId, "new-calculation");
  assert.equal(chart.state.indicator.resultContext.fileId, "new.json");
  assert.equal(chart.rebuilt[0].preserveOverrides, true);
  assert.deepEqual(chart.state.drawings, [{ id: "position" }]);
});

test("indicator-only activation leaves the candle acquisition clock untouched", async () => {
  const chart = fixture();
  assert.match(await chart.update({ indicatorOnly: true }), /Indicator updated/);
  assert.deepEqual(chart.requests.map(([url]) => url), ["/api/reactions/continue"]);
});

test("a superseded continuation refreshes the RAW without clearing the applied result or logging a warning", async () => {
  let refreshed = 0;
  const chart = fixture({ refreshInventory: () => { refreshed += 1; }, onContinue: async () => ({
    ok: false, status: 409, json: async () => ({ code: "RAW_SNAPSHOT_SUPERSEDED" }),
  }) });
  const status = await chart.update({ indicatorOnly: true });
  assert.match(status, /Synchronizing/);
  assert.equal(refreshed, 1);
  assert.equal(chart.state.indicator.results, chart.originalResult);
  assert.deepEqual(chart.failures, []);
});

test("Live reconnects with the same checkpoint after a dropped request or response body", async () => {
  let attempts = 0;
  const events = [];
  const chart = fixture({ alertsReady: true, onContinue: async () => {
    attempts += 1;
    if (attempts === 1) throw new TypeError("Failed to fetch");
    return { ok: true, status: 200, json: async () => {
      if (attempts === 2) throw new TypeError("Network error reading the response");
      return chart.payload;
    }, headers: new Map([["X-QG-Source-Fingerprint", "source"], ["X-QG-Live-Session", "recovered"],
      ["X-QG-Live-Proof", JSON.stringify(proof(300))]]) };
  } });
  assert.match(await chart.update({ indicatorOnly: true, reportIndicatorProgress: event => events.push(event) }), /Indicator updated/);
  assert.equal(chart.requests.length, 3);
  for (const [url, { requestId, ...request }] of chart.requests) {
    assert.equal(url, "/api/reactions/continue");
    assert.deepEqual(request, { id: "old.json", chartId: "chart", tabId, sessionId: "checkpoint", proof: proof(200), rawSha256: "old" });
    assert.ok(requestId);
  }
  assert.equal(new Set(chart.requests.map(([, request]) => request.requestId)).size, 3);
  assert.equal(chart.state.indicator.resultContext.liveSessionId, "recovered");
  assert.equal(chart.state.indicator.results, chart.payload);
  assert.equal(chart.alertPublications.length, 1);
  assert.equal(events.at(-1).percent, 100);
  assert.deepEqual(chart.failures, []);
});

test("Live waits for server readiness after the short retries are exhausted, then applies without manual Apply", async () => {
  let attempts = 0;
  let readinessChecks = 0;
  const chart = fixture({
    async checkService() {
      if (++readinessChecks === 1) throw new TypeError("Failed to fetch");
      return { ok: true, status: 200 };
    },
    async onContinue() {
      if (++attempts < 4) throw new TypeError("Failed to fetch");
      return { ok: true, status: 200, json: async () => chart.payload,
        headers: new Map([["X-QG-Source-Fingerprint", "source"], ["X-QG-Live-Session", "recovered"],
          ["X-QG-Live-Proof", JSON.stringify(proof(300))]]) };
    },
  });
  assert.match(await chart.update({ indicatorOnly: true }), /Indicator updated/);
  assert.equal(readinessChecks, 2);
  assert.equal(attempts, 4);
  assert.ok(chart.requests.every(([url, request]) => url === "/api/reactions/continue" && request.sessionId === "checkpoint"));
  assert.equal(chart.state.indicator.resultContext.liveSessionId, "recovered");
  assert.deepEqual(chart.failures, []);
});

test("an extended disconnect keeps the last result and records a single diagnostic until recovery", async () => {
  let fail = true;
  const chart = fixture({ onContinue: async () => {
    if (fail) throw new TypeError("Failed to fetch");
    return { ok: true, status: 200, json: async () => chart.payload,
      headers: new Map([["X-QG-Source-Fingerprint", "source"], ["X-QG-Live-Proof", JSON.stringify(proof(300))]]) };
  } });
  await chart.update({ indicatorOnly: true });
  await chart.update({ indicatorOnly: true });
  assert.equal(chart.requests.length, 6);
  assert.equal(chart.state.indicator.results, chart.originalResult);
  assert.deepEqual(chart.failures, ["REALTIME_INDICATOR_CONNECTION_UNAVAILABLE"]);
  fail = false;
  await chart.update({ indicatorOnly: true });
  assert.equal(chart.requests.length, 7);
  assert.equal(chart.state.indicator.results, chart.payload);
});

test("automatic candle polling waits for or synchronizes with a competing tab quietly", async () => {
  let refreshed = 0;
  const busy = fixture({ candleConflict: "RAW_BUSY", refreshInventory: () => { refreshed += 1; } });
  const changed = fixture({ candleConflict: "RAW_CHANGED", refreshInventory: () => { refreshed += 1; } });
  assert.match((await busy.update()).status, /Another check/);
  assert.match((await changed.update({ verifyAll: true, manualVerification: false })).status, /Synchronizing/);
  assert.equal(refreshed, 1);
  for (const chart of [busy, changed]) {
    assert.deepEqual(chart.requests.map(([url]) => url), ["/api/candle-files/realtime"]);
    assert.deepEqual(chart.failures, []);
    assert.equal(chart.state.indicator.results, chart.originalResult);
  }
});

test("a poll displays appended rows before requesting recent verification", async () => {
  const chart = fixture({ nextRecent(state) {
    assert.equal(state.raw.at(-1).time, 330);
    return { file: state.file, candles: [], verification: { status: "verified" } };
  } });
  await chart.update({ indicatorCalculation: false });
  assert.deepEqual(chart.requests.map(([, body]) => body.phase), ["latest", "recent"]);
  assert.equal(chart.requests[1][1].id, "new.json");
  assert.equal(chart.requests[1][1].lastCandleTime, 330);
  assert.equal(chart.requests[1][1].previousTail, 300);
  assert.equal(chart.state.raw.at(-1).time, 330);
});

test("an older server can commit an append and the browser resumes its pending window after restart", async () => {
  let updatedServer = false;
  const chart = fixture({
    supportsRecentVerification: () => updatedServer,
    nextRaw(state) {
      const candles = state.file.to === 300 ? [{ time: 330 }] : [];
      return { file: { ...state.file, to: candles.at(-1)?.time ?? state.file.to, count: state.raw.length + candles.length },
        candles, verification: { status: "verified" } };
    },
  });
  const oldServerResult = await chart.update();
  assert.match(oldServerResult.status, /Restart TradingBot/);
  assert.match(oldServerResult.status, /Indicator updated/);
  assert.deepEqual(chart.requests.filter(([url]) => url === "/api/candle-files/realtime").map(([, body]) => body.phase), ["latest"]);
  assert.equal(chart.state.raw.at(-1).time, 330);
  updatedServer = true;
  const update = await chart.update({ indicatorCalculation: false });
  assert.doesNotMatch(update.status, /Restart TradingBot/);
  assert.equal(chart.requests.at(-1)[1].phase, "recent");
  assert.equal(chart.requests.at(-1)[1].previousTail, 300);
  assert.deepEqual(chart.failures, []);
});

test("a source outage leaves recent verification pending even when the next poll has no append", async () => {
  let shouldAppend = true;
  let unavailable = true;
  const chart = fixture({
    nextRaw(state) {
      const candles = shouldAppend ? [{ time: 330 }] : [];
      shouldAppend = false;
      return { file: { ...state.file, to: candles.at(-1)?.time ?? state.file.to, count: state.raw.length + candles.length },
        candles, verification: { status: "verified" } };
    },
    nextRecent(state) {
      const status = unavailable ? "unavailable" : "verified";
      unavailable = false;
      return { file: state.file, candles: [], verification: { status } };
    },
  });
  for (let poll = 0; poll < 3; poll++) await chart.update({ indicatorCalculation: false });
  assert.deepEqual(chart.requests.map(([, body]) => [body.phase, body.previousTail]), [
    ["latest", undefined], ["recent", 300], ["latest", undefined], ["recent", 300], ["latest", undefined],
  ]);
});

test("indicator progress remains below 100 until the current result passes chart validation", async () => {
  const events = [];
  let respond;
  const source = { close() {} };
  const chart = fixture({ connectProgress: () => source, onContinue: () => new Promise(resolve => { respond = resolve; }) });
  const poll = chart.update({ reportIndicatorProgress: event => events.push(event) });
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(chart.requests.at(-1)[1].requestId, "live-progress-fixture");
  source.onmessage({ data: JSON.stringify({ status: "completed", label: "Bullish lifecycle ready", completedStages: 3, totalStages: 6 }) });
  assert.equal(events.at(-1).percent, 50);
  assert.equal(chart.state.indicator.results, chart.originalResult);
  respond({ ok: true, status: 200, json: async () => chart.payload,
    headers: new Map([["X-QG-Source-Fingerprint", "source"], ["X-QG-Live-Proof", JSON.stringify(proof(330))]]) });
  await poll;
  assert.equal(events.at(-1).percent, 100);
  assert.equal(events.at(-1).outcome, "applied");
  assert.equal(chart.state.indicator.results, chart.payload);
});

test("latest candles can start a continuation while recent verification is pending", async () => {
  let finishRecent;
  const chart = fixture({
    nextRecent() { return new Promise(resolve => { finishRecent = resolve; }); },
    nextRaw(state) {
      return { file: { ...state.file, id: "330.json", to: 330, count: 2 }, candles: [{ time: 330 }], verification: { status: "pending" } };
    },
  });
  const poll = chart.update();
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(chart.state.raw.at(-1).time, 330);
  assert.equal(chart.requests.filter(([url]) => url === "/api/reactions/continue").length, 1);
  assert.equal(chart.state.indicator.results, chart.originalResult);
  finishRecent({ file: { ...chart.state.file }, candles: [], verification: { status: "verified" } });
  await poll;
  assert.equal(chart.requests.filter(([url]) => url === "/api/reactions/continue").length, 1);
  assert.equal(chart.state.indicator.resultContext.to, 330);
});

test("Verify All corrects a visible result within its original manual range when automatic continuation is off", async () => {
  const chart = fixture({ candles: [], corrections: [{ time: 300, close: 2 }] });
  chart.state.indicator.resultContext.to = 300;
  chart.state.indicator.resultContext.liveProof = proof(300);
  assert.match(await chart.update({ indicatorCalculation: false, verifyAll: true }), /Corrected 1 candle\..*Indicator updated/);
  const [endpoint, request] = chart.requests[1];
  assert.equal(endpoint, "/api/reactions");
  assert.equal(request.from, 100);
  assert.equal(request.to, 300);
  assert.equal(request.direction, "bearish");
  assert.equal(request.liveSession, true);
  assert.equal(chart.state.raw[0].close, 2);
});

test("a recent verification correction outside the old range invalidates Live and retries a full Apply", async () => {
  let corrected = false;
  let rebuildAttempts = 0;
  const chart = fixture({ alertsReady: true,
    nextRaw(state) {
      const candles = state.raw.at(-1).time < 330 ? [{ time: 330 }] : [];
      return { file: { ...state.file, id: "new.json", to: 330, count: 2 }, candles };
    },
    nextRecent(state) {
      corrected = true;
      return { file: { ...state.file, count: 2, metadata: { dataSha256: "repaired" } },
        candles: [], corrections: [{ time: 300, close: 42 }], verification: { status: "verified" } };
    },
    async onContinue(url) {
      if (url === "/api/reactions" && ++rebuildAttempts === 1)
        return { ok: false, status: 503, json: async () => ({ error: "Engine busy" }) };
      return { ok: true, status: 200, json: async () => chart.payload, headers: new Map([
        ["X-QG-Source-Fingerprint", "source"], ["X-QG-Live-Proof", JSON.stringify(proof(330))],
        ["X-QG-Live-Session", "repaired-session"],
      ]) };
    },
  });
  chart.state.indicator.selectedObjectId = "old-result-object";
  await chart.update();
  assert.equal(corrected, true);
  assert.equal(chart.state.raw[0].close, 42);
  assert.equal(chart.state.indicator.results, chart.originalResult);
  assert.equal(chart.state.indicator.objects[0].id, "old-result-object");
  assert.equal(chart.state.indicator.selectedObjectId, null);
  assert.deepEqual(chart.alertPublications, []);
  await chart.update();
  assert.equal(rebuildAttempts, 2);
  const fullRequests = chart.requests.filter(([url]) => url === "/api/reactions").map(([, request]) => request);
  for (const request of fullRequests) {
    assert.equal(request.id, "new.json");
    assert.equal(request.from, 100);
    assert.equal(request.to, 330);
    assert.equal(request.direction, "bearish");
    assert.equal(request.liveSession, true);
  }
  assert.equal(chart.state.indicator.results, chart.payload);
  assert.equal(chart.state.indicator.resultContext.liveSessionId, "repaired-session");
  assert.deepEqual(chart.alertPublications, [{ kind: "baseline", time: 330 }]);
});

test("restoring a missing historical candle rebuilds once without automatic continuation", async () => {
  const chart = fixture({ alertsReady: true, nextRaw(state) {
    return { file: { ...state.file, count: 3 }, candles: [], gapCandles: [{ time: 305 }],
      verification: { status: "verified" } };
  } });
  chart.state.raw.push({ time: 330 });
  chart.state.file.to = 330;
  chart.state.indicator.resultContext.to = 330;
  await chart.update({ verifyAll: true, indicatorCalculation: false });
  assert.deepEqual(chart.state.raw.map(row => row.time), [300, 305, 330]);
  assert.deepEqual(chart.requests.map(([url]) => url), ["/api/candle-files/realtime", "/api/reactions"]);
  assert.equal(chart.requests[1][1].to, 330);
  assert.deepEqual(chart.alertPublications, [{ kind: "baseline", time: 330 }]);
});

test("a new continuation can catch up to the existing RAW tail with no new candles", async () => {
  const chart = fixture({ candles: [] });
  chart.controls["#indicatorTo"].value = "250";
  assert.match(await chart.update(), /Indicator updated/);
  assert.equal(chart.requests.length, 2);
  assert.equal(chart.controls["#indicatorTo"].value, "250", "pending manual range edit is retained");
  await chart.update();
  assert.equal(chart.requests.filter(([url]) => url === "/api/reactions/continue").length, 1);
});

test("only a calculation present in this tab can activate continuation", async () => {
  const chart = fixture();
  chart.state.indicator.resultContext = null;
  chart.state.indicator.results = null;
  const result = await chart.update();
  assert.match(result.status, /Added 1/);
  assert.match(result.indicatorError, /Apply/);
  assert.deepEqual(chart.requests.map(([, body]) => body.phase), ["latest", "recent"]);
  assert.deepEqual(chart.failures, []);
  assert.equal(chart.state.file.id, "new.json");
  assert.equal(chart.state.raw.at(-1).time, 330);
  assert.equal(chart.state.indicator.results, null);
});

test("a hidden calculation does not start live indicator work", async () => {
  const chart = fixture();
  chart.state.indicator.enabled = false;
  const result = await chart.update();
  assert.match(result.indicatorError, /with Apply/);
  assert.deepEqual(chart.requests.map(([, body]) => body.phase), ["latest", "recent"]);
});

test("the tab's in-memory calculation can recover a missing worker and adopts the replacement token", async () => {
  const chart = fixture({ onContinue: async () => ({ ok: true, status: 200, json: async () => chart.payload,
    headers: new Map([["X-QG-Live-Session", "recovered"], ["X-QG-Calculation-Id", "new-calculation"],
      ["X-QG-Source-Fingerprint", "source"], ["X-QG-Live-Proof", JSON.stringify(proof(330))]]) }) });
  Object.assign(chart.state.indicator.resultContext, { liveSessionId: null, calculationId: "saved" });
  assert.match((await chart.update()).status, /Indicator updated/);
  assert.deepEqual(chart.requests.find(([url]) => url === "/api/reactions/continue")[1],
    { id: "new.json", chartId: "chart", tabId, sessionId: null, proof: proof(200), rawSha256: "old" });
  assert.equal(chart.state.indicator.resultContext.liveSessionId, "recovered");
});

test("activation catches up this tab's calculation even if market acquisition is unavailable", async () => {
  const chart = fixture({ marketAvailable: false, onContinue: async () => ({ ok: true, status: 200,
    json: async () => chart.payload, headers: new Map([
      ["X-QG-Live-Proof", JSON.stringify(proof(300))],
      ["X-QG-Live-Session", "recovered"], ["X-QG-Calculation-Id", "saved"], ["X-QG-Source-Fingerprint", "source"],
    ]) }) });
  const result = await chart.update();
  assert.match(result.status, /Indicator updated/);
  assert.equal(result.verification.status, "unavailable");
  assert.deepEqual(chart.requests[1][1], { id: "old.json", chartId: "chart", tabId, sessionId: "checkpoint", proof: proof(200), rawSha256: "old" });
  assert.equal(chart.state.indicator.resultContext.chartTimeframe, 30);
  assert.equal(chart.state.indicator.resultContext.direction, "bearish");
});

test("a canceled or stale continuation cannot publish an indicator result", async () => {
  let release;
  const chart = fixture({ onContinue: () => new Promise(resolve => { release = resolve; }) });
  const running = chart.update();
  await new Promise(resolve => setImmediate(resolve));
  chart.indicatorAbort.abort();
  release({ ok: true, status: 200, json: async () => chart.payload, headers: new Map() });
  await running;
  assert.equal(chart.state.file.id, "new.json");
  assert.equal(chart.state.indicator.results, chart.originalResult);
  assert.equal(chart.rebuilt.length, 0);
});

test("successive RAW polls commit their candles while one continuation is blocked", async () => {
  const advances = [];
  const chart = fixture({ alertsReady: true,
    nextRaw(state) {
      const to = state.file.to + 30;
      return { file: { ...state.file, id: `${to}.json`, to, count: state.raw.length + 1 }, candles: [{ time: to }] };
    },
    onContinue(url, options) {
      return new Promise(resolve => advances.push({ ...JSON.parse(options.body), resolve }));
    },
  });
  const first = chart.update();
  await new Promise(resolve => setImmediate(resolve));
  assert.deepEqual(chart.state.raw.map(row => row.time), [300, 330]);
  assert.equal(advances.length, 1);
  const second = chart.update();
  await new Promise(resolve => setImmediate(resolve));
  const third = chart.update();
  await new Promise(resolve => setImmediate(resolve));
  assert.deepEqual(chart.state.raw.map(row => row.time), [300, 330, 360, 390]);
  assert.equal(advances.length, 1);

  const complete = (advance, to) => advance.resolve({ ok: true, status: 200, json: async () => chart.payload,
    headers: new Map([["X-QG-Source-Fingerprint", "source"], ["X-QG-Live-Proof", JSON.stringify(proof(to))]]) });
  complete(advances[0], 330);
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(chart.state.indicator.resultContext.to, 330);
  assert.equal(advances.length, 2);
  assert.equal(advances[1].id, "390.json");
  assert.equal(advances[1].proof.to, 330);
  complete(advances[1], 390);
  await Promise.all([first, second, third]);
  assert.deepEqual(chart.alertPublications.map(event => event.time), [330, 390]);
});

test("a continuation waits for an overlapping verification and cannot publish superseded prices", async () => {
  let finishVerification;
  const advances = [];
  const chart = fixture({ alertsReady: true,
    nextRaw(state, { verifyAll }) {
      if (verifyAll) return new Promise(resolve => { finishVerification = resolve; });
      return { file: { ...state.file, id: "330.json", to: 330, count: 2 }, candles: [{ time: 330 }] };
    },
    onContinue(url) {
      return new Promise(resolve => advances.push({ url, resolve }));
    },
  });
  chart.state.indicator.resultContext.to = 300;
  const first = chart.update();
  await new Promise(resolve => setImmediate(resolve));
  const verification = chart.update({ verifyAll: true, indicatorCalculation: false });
  await new Promise(resolve => setImmediate(resolve));
  const complete = (advance, to) => advance.resolve({ ok: true, status: 200, json: async () => chart.payload,
    headers: new Map([["X-QG-Source-Fingerprint", "source"], ["X-QG-Live-Proof", JSON.stringify(proof(to))]]) });
  complete(advances[0], 330);
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(chart.state.indicator.results, chart.originalResult);
  assert.deepEqual(chart.alertPublications, []);
  finishVerification({ file: { ...chart.state.file, metadata: { dataSha256: "corrected" } }, candles: [], corrections: [{ time: 300, close: 42 }] });
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(chart.state.raw[0].close, 42);
  assert.equal(chart.state.indicator.results, chart.originalResult);
  assert.equal(advances.length, 2);
  assert.equal(advances[1].url, "/api/reactions");
  complete(advances[1], 300);
  await Promise.all([first, verification]);
  assert.equal(chart.state.indicator.resultContext.to, 300);
  assert.deepEqual(chart.alertPublications, [{ kind: "baseline", time: 330 }]);
});

test("recovery under a changed Engine source establishes a new alert baseline", async () => {
  const chart = fixture({ alertsReady: true, onContinue: async () => ({ ok: true, status: 200,
    json: async () => chart.payload, headers: new Map([
      ["X-QG-Source-Fingerprint", "revised-source"], ["X-QG-Live-Proof", JSON.stringify(proof(330))],
      ["X-QG-Live-Session", "recovered"],
    ]) }) });
  await chart.update();
  assert.equal(chart.state.indicator.resultContext.sourceFingerprint, "revised-source");
  assert.deepEqual(chart.alertPublications, [{ kind: "baseline", time: 330 }]);
});

test("a pending Engine source refresh covers newly appended candles when automatic calculation is enabled", async () => {
  const chart = fixture({ alertsReady: true,
    onContinue: async (url, options) => {
      const request = JSON.parse(options.body);
      const to = url === "/api/reactions/continue" ? 330 : request.to;
      return { ok: true, status: 200, json: async () => chart.payload, headers: new Map([
        ["X-QG-Source-Fingerprint", "revised-source"], ["X-QG-Live-Proof", JSON.stringify(proof(to))],
        ["X-QG-Live-Session", "recovered"],
      ]) };
    },
  });
  chart.state.indicator.resultContext.needsSourceRefresh = true;
  await chart.update();
  assert.equal(chart.state.indicator.resultContext.to, 330);
  assert.equal(chart.state.indicator.resultContext.liveRawTo, 330);
  assert.equal(chart.state.indicator.resultContext.sourceFingerprint, "revised-source");
  assert.deepEqual(chart.alertPublications, [{ kind: "baseline", time: 330 }]);
});
