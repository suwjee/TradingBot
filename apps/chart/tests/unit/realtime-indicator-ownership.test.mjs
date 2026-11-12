import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import vm from "node:vm";

const main = await readFile(new URL("../../src/main.js", import.meta.url), "utf8");
const indicatorFlow = main.slice(main.indexOf("function realtimeIndicatorProblem("),
  main.indexOf("function moveRealtimeIndicatorPreferences("));
const updateFlow = main.slice(main.indexOf("async function runRealtimeChartUpdate("),
  main.indexOf("function setUpdateButtonState("));

function fixture({ candles = [{ time: 330 }], onContinue } = {}) {
  const originalResult = { directions: { bearish: {} } };
  const state = {
    file: { id: "old.json", chartId: "chart", to: 300, timeframe: "5S", metadata: { dataSha256: "old" } },
    raw: [{ time: 300 }],
    data: [{ time: 300 }],
    tf: 30,
    indicator: {
      settings: { direction: "bullish" },
      results: originalResult,
      resultContext: { fileId: "old.json", chartId: "chart", from: 100, to: 200,
        chartTimeframe: 30, analysisTimeframe: 30, direction: "bearish",
        liveSessionId: "checkpoint", sourceFingerprint: "source" },
    },
    indicatorRange: {},
    drawings: [{ id: "position" }],
  };
  const controls = { "#indicatorFrom": { value: "100" }, "#indicatorTo": { value: "200" } };
  const payload = { directions: { bearish: { reactions: [], resets: [] } }, timeframe: 30 };
  const requests = [], rebuilt = [];
  const rawResponse = {
    file: { ...state.file, id: candles.length ? "new.json" : state.file.id,
      to: candles.at(-1)?.time ?? state.file.to, count: state.raw.length + candles.length },
    candles,
  };
  const noop = () => {};
  const sandbox = vm.createContext({
    state, AbortController, performance, symbolLoadController: null, symbolLoadRevision: 1,
    indicatorCalculationOwner: null, realtimeUpdateOwner: null, chartUpdateRunning: false,
    clone: structuredClone, removeInvalidIndicatorCalculations: value => value,
    calculationKey: ({ direction }, from, to) => [direction, from, to].join(":"),
    rebuildIndicatorObjects: options => rebuilt.push(options),
    $: selector => controls[selector], parseTehranInput: Number, inputFromTehran: String,
    setDateTimeValue: (selector, value) => { controls[selector].value = value; },
    scheduleDraw: noop, saveChartIndicatorContext: noop, renderIndicatorInfo: noop,
    log: { chart: { info: noop, warn: noop, error: noop }, indicator: { info: noop, warn: noop, error: noop } },
    applyRealtimeCandles(file, rows) {
      state.file = file;
      state.raw.push(...rows);
      state.data.push(...rows);
    },
    async fetch(url, options) {
      requests.push([url, JSON.parse(options.body)]);
      if (url === "/api/candle-files/realtime")
        return { ok: true, status: 200, json: async () => rawResponse };
      if (onContinue) return onContinue(url, options);
      return {
        ok: true, status: 200, json: async () => payload,
        headers: new Map([["X-QG-Calculation-Id", "new-calculation"], ["X-QG-Source-Fingerprint", "source"]]),
      };
    },
  });
  vm.runInContext(indicatorFlow + updateFlow, sandbox);
  const rawAbort = new AbortController();
  const indicatorAbort = new AbortController();
  return { state, originalResult, payload, requests, rebuilt, controls, indicatorAbort,
    problem: () => vm.runInContext('realtimeIndicatorProblem("chart")', sandbox),
    update() {
      sandbox.request = { chartId: "chart", signal: rawAbort.signal,
        indicatorSignal: indicatorAbort.signal, indicatorCalculation: true };
      return vm.runInContext("runRealtimeChartUpdate(request)", sandbox);
    },
  };
}

test("the accepted checkpoint follows the published RAW rename and retains the chosen start and direction", async () => {
  const chart = fixture();
  assert.equal(chart.problem(), "");
  assert.match(await chart.update(), /Added 1.*Indicator updated/);
  assert.deepEqual(chart.requests[1], ["/api/reactions/continue",
    { id: "new.json", chartId: "chart", sessionId: "checkpoint" }]);
  assert.equal(chart.state.indicator.results, chart.payload);
  assert.equal(chart.state.indicator.resultContext.from, 100);
  assert.equal(chart.state.indicator.resultContext.direction, "bearish");
  assert.equal(chart.state.indicator.resultContext.to, 330);
  assert.equal(chart.state.indicator.resultContext.calculationId, "new-calculation");
  assert.equal(chart.state.indicator.resultContext.fileId, "new.json");
  assert.equal(chart.rebuilt[0].preserveOverrides, true);
  assert.deepEqual(chart.state.drawings, [{ id: "position" }]);
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

test("an expired checkpoint keeps published candles and prior indicator output", async () => {
  const chart = fixture({ onContinue: () => ({ ok: false, status: 410,
    json: async () => ({ error: "Checkpoint expired." }) }) });
  await assert.rejects(chart.update(), /Apply/);
  assert.match(chart.problem(), /Apply/);
  assert.equal(chart.state.file.id, "new.json");
  assert.equal(chart.state.raw.at(-1).time, 330);
  assert.equal(chart.state.indicator.results, chart.originalResult);
  assert.equal(chart.state.indicator.resultContext.liveSessionId, null);
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
