import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import vm from "node:vm";
import { readRealtimeUpdate } from "../../src/features/realtime-chart.js";

const main = await readFile(new URL("../../src/main.js", import.meta.url), "utf8");
const indicatorFlow = main.slice(main.indexOf("let chartUpdateRunning = false;") + "let chartUpdateRunning = false;".length,
  main.indexOf("function moveRealtimeIndicatorPreferences("));
const updateFlow = main.slice(main.indexOf("async function runRealtimeChartUpdate("),
  main.indexOf("function setUpdateButtonState("));
const tabId = "same-tab-fixture";
const proof = to => ({ chartId: "chart", tabId, to,
  request: { from: 100, to: 200, direction: "bearish", timeframe: 30, chartTimeframe: 30, blueLines: true, bridgeOutput: true } });

function fixture({ candles = [{ time: 330 }], corrections = [], onContinue, nextRaw, marketAvailable = true, historyPending = false, alertsReady = false } = {}) {
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
      resultContext: { fileId: "old.json", chartId: "chart", from: 100, to: 200,
        chartTimeframe: 30, analysisTimeframe: 30, direction: "bearish",
        liveSessionId: "checkpoint", liveProof: proof(200), sourceFingerprint: "source" },
    },
    indicatorRange: {},
    drawings: [{ id: "position" }],
  };
  const controls = { "#indicatorFrom": { value: "100" }, "#indicatorTo": { value: "200" }, "#indicatorEnabled": { checked: false } };
  const payload = { directions: { bearish: { reactions: [], resets: [] } }, timeframe: 30 };
  const requests = [], rebuilt = [], failures = [], alertPublications = [];
  const rawResponse = {
    file: { ...state.file, id: candles.length ? "new.json" : state.file.id,
      to: candles.at(-1)?.time ?? state.file.to, count: state.raw.length + candles.length },
    candles,
    corrections,
  };
  const noop = () => {};
  const sandbox = vm.createContext({
    state, AbortController, AbortSignal, performance, readRealtimeUpdate, symbolLoadController: null, symbolLoadRevision: 1, liveIndicatorTabId: tabId,
    alertLiveReady: alertsReady, formatSymbolWithBroker: file => file.id,
    alertController: {
      baseline: time => alertPublications.push({ kind: "baseline", time }),
      advance: (result, time, symbol) => alertPublications.push({ kind: "advance", result, time, symbol }),
    },
    indicatorCalculationOwner: null, realtimeUpdateOwner: null, chartUpdateRunning: false,
    lowerBoundTime: (rows, time) => rows.findIndex(row => row.time >= time),
    clone: structuredClone, removeInvalidIndicatorCalculations: value => value,
    calculationKey: ({ direction }, from, to) => [direction, from, to].join(":"),
    rebuildIndicatorObjects: options => rebuilt.push(options),
    $: selector => controls[selector], parseTehranInput: Number, inputFromTehran: String,
    setDateTimeValue: (selector, value) => { controls[selector].value = value; },
    scheduleDraw: noop, saveChartIndicatorContext: noop, renderIndicatorInfo: noop,
    indicatorSettings: () => ({}), setIndicatorVisibility: enabled => { state.indicator.enabled = enabled; },
    log: { chart: { info: noop, warn: noop, error: name => failures.push(name) }, indicator: { info: noop, warn: noop, error: noop } },
    applyRealtimeCandles(file, rows, corrected) {
      state.file = file;
      for (const row of corrected) state.raw[state.raw.findIndex(old => old.time === row.time)] = row;
      state.raw.push(...rows);
      state.data.push(...rows);
    },
    async fetch(url, options) {
      requests.push([url, JSON.parse(options.body)]);
      if (url === "/api/candle-files/realtime") {
        if (nextRaw) return { status: 200, json: async () => nextRaw(state, JSON.parse(options.body)) };
        const phase = JSON.parse(options.body).phase;
        if (historyPending && phase === "history") {
          assert.equal(state.raw.at(-1).time, 330);
          return { status: 200, json: async () => ({ file: state.file, candles: [], verification: { status: "verified" } }) };
        }
        return marketAvailable ? { ok: true, status: 200, json: async () => historyPending
          ? { ...rawResponse, verification: { status: "pending" } } : rawResponse }
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
});

test("a historical repair refreshes the alert baseline without evaluating a trigger", async () => {
  const chart = fixture({ alertsReady: true, candles: [], corrections: [{ time: 300 }] });
  chart.state.indicator.resultContext.to = 300;
  await chart.update({ indicatorCalculation: false, verifyAll: true });
  assert.deepEqual(chart.alertPublications, [{ kind: "baseline", time: 300 }]);
});

test("the accepted checkpoint follows the published RAW rename and retains the chosen start and direction", async () => {
  const chart = fixture();
  assert.match(await chart.update(), /Added 1.*Indicator updated/);
  assert.deepEqual(chart.requests[1], ["/api/reactions/continue",
    { id: "new.json", chartId: "chart", sessionId: "checkpoint", tabId, proof: proof(200) }]);
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

test("a poll displays appended rows before requesting historical verification", async () => {
  const chart = fixture({ historyPending: true });
  await chart.update({ indicatorCalculation: false });
  assert.deepEqual(chart.requests.map(([, body]) => body.phase), ["latest", "history"]);
  assert.equal(chart.requests[1][1].id, "new.json");
  assert.equal(chart.requests[1][1].lastCandleTime, 330);
  assert.equal(chart.state.raw.at(-1).time, 330);
});

test("latest candles can start a continuation while historical verification is pending", async () => {
  let finishHistory;
  const chart = fixture({
    nextRaw(state, { phase }) {
      if (phase === "history") return new Promise(resolve => { finishHistory = resolve; });
      return { file: { ...state.file, id: "330.json", to: 330, count: 2 }, candles: [{ time: 330 }], verification: { status: "pending" } };
    },
  });
  const poll = chart.update();
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(chart.state.raw.at(-1).time, 330);
  assert.equal(chart.requests.filter(([url]) => url === "/api/reactions/continue").length, 1);
  assert.equal(chart.state.indicator.results, chart.originalResult);
  finishHistory({ file: { ...chart.state.file }, candles: [], verification: { status: "verified" } });
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
  assert.equal(chart.requests.length, 1);
  assert.deepEqual(chart.failures, []);
  assert.equal(chart.state.file.id, "new.json");
  assert.equal(chart.state.raw.at(-1).time, 330);
  assert.equal(chart.state.indicator.results, null);
});

test("a hidden calculation does not start live indicator work", async () => {
  const chart = fixture();
  chart.state.indicator.enabled = false;
  const result = await chart.update();
  assert.match(result.indicatorError, /Apply in this tab/);
  assert.equal(chart.requests.length, 1);
});

test("the tab's in-memory calculation can recover a missing worker and adopts the replacement token", async () => {
  const chart = fixture({ onContinue: async () => ({ ok: true, status: 200, json: async () => chart.payload,
    headers: new Map([["X-QG-Live-Session", "recovered"], ["X-QG-Calculation-Id", "new-calculation"],
      ["X-QG-Source-Fingerprint", "source"], ["X-QG-Live-Proof", JSON.stringify(proof(330))]]) }) });
  Object.assign(chart.state.indicator.resultContext, { liveSessionId: null, calculationId: "saved" });
  assert.match(await chart.update(), /Indicator updated/);
  assert.deepEqual(chart.requests[1][1], { id: "new.json", chartId: "chart", tabId, sessionId: null, proof: proof(200) });
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
  assert.deepEqual(chart.requests[1][1], { id: "old.json", chartId: "chart", tabId, sessionId: "checkpoint", proof: proof(200) });
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
