import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import vm from "node:vm";
import * as lifecycle from "../../src/features/indicator-lifecycle.js";

const main = await readFile(new URL("../../src/main.js", import.meta.url), "utf8");
const functionStart = main.indexOf("async function calculateIndicator() {");
const actualCalculate = main.slice(functionStart, main.indexOf('\n$("#indicatorBtn").onclick = openIndicator;', functionStart));

function harness() {
  const controls = { indicatorFrom: { value: "100" }, indicatorTo: { value: "200" },
    indicatorEnabled: { checked: true }, applyIndicator: { disabled: false } };
  const inputs = { direction: "bearish", timeframe: "30" };
  const context = { fileId: "A.json", chartId: "A", symbol: "A", chartTimeframe: 30,
    analysisTimeframe: 30, from: 100, to: 200, direction: "bearish", sourceFingerprint: "old-source",
    liveSessionId: "checkpoint" };
  const state = { file: { id: "A.json", chartId: "A", symbol: "A" }, tf: 30,
    raw: [{ time: 0 }, { time: 300 }], data: [],
    indicator: { loading: false, results: {}, resultContext: context }, indicatorRange: {} };
  const posts = [], replies = [], applied = [];
  const noop = () => {};
  const sandbox = { ...lifecycle, state, inputs, controls, posts, performance, AbortController, setTimeout, clearTimeout, clearInterval,
    liveIndicatorTabId: "manual-apply-tab",
    $: selector => selector === "[data-direction].active" ? { dataset: { direction: inputs.direction } }
      : controls[selector.replace(/^#/, "")] ||= { dataset: {}, focus: noop, setAttribute: noop, classList: { toggle: noop } },
    indicatorApplyProblem: () => null, indicatorSettings: () => ({ ...inputs }),
    parseTehranInput: Number, normalizeIndicatorRange: () => null, calculationKey: () => "key",
    clone: value => structuredClone(value), indicatorStatus: noop, indicatorToast: noop,
    log: { indicator: { info: noop, warn: noop, error: (_event, error) => { throw error; } } },
    setIndicatorVisibility: value => applied.push(["visible", value]),
    removeInvalidIndicatorCalculations: value => { applied.push(value); return value; },
    localStorage: { setItem: noop },
    rebuildIndicatorObjects: noop, drawAll: noop, syncAlertMonitoring: noop,
    alertLiveReady: false, renderIndicatorInfo: noop, setFooterCacheStatus: noop, window: {},
    pushIndicatorActivity: noop, createUniqueId: () => "request", formatTehran: String,
    startCalculationProgress: () => ({ events: [], recordEvent: noop, source: { close: noop } }), stopCalculationProgress: noop,
    setCalculationProgress: noop,
    buildIndicatorCalculationRequest: value => value,
    fetch: (url, options) => {
      assert.equal(url, "/api/reactions");
      assert.equal(options.cache, "no-store");
      posts.push(JSON.parse(options.body));
      return new Promise(resolve => replies.push(resolve));
    },
  };
  const runtime = vm.createContext(sandbox);
  const invalidateStart = main.indexOf("function invalidateIndicatorCalculation() {");
  const invalidate = invalidateStart < 0 ? "" : main.slice(invalidateStart, main.indexOf("\nfunction clearActiveIndicatorCalculation()", invalidateStart));
  vm.runInContext(`let indicatorCalculationOwner = null;
let realtimeUpdateOwner = null;
let symbolLoadRevision = 0;
${invalidate}\n${actualCalculate}`, runtime);
  return { state, controls, inputs, posts, applied, runtime,
    calculate: () => vm.runInContext("calculateIndicator()", runtime),
    resolve: (index = 0) => replies[index]({ ok: true,
      headers: { get: () => null }, json: async () => ({ directions: {} }) }),
  };
}

for (const [name, change] of [
  ["file and timeframe selection", h => { h.state.file = { id: "B.json", chartId: "B", symbol: "B" }; h.state.tf = 60; h.state.indicator.results = null; h.state.indicator.resultContext = null; }],
  ["in-place source rename", h => { h.state.file.id = "renamed.json"; }],
  ["RAW revision", h => { h.state.raw = [...h.state.raw]; }],
  ["in-place RAW extension", h => { h.state.raw.push({ time: 330 }); }],
  ["analysis candle revision", h => { h.state.data = [...h.state.data]; }],
  ["range input", h => { h.controls.indicatorTo.value = "210"; }],
  ["direction input", h => { h.inputs.direction = "bullish"; }],
  ["cleared result context", h => { h.state.indicator.resultContext = null; }],
]) {
  test(`pending calculation abandons stale ${name}`, async () => {
    const h = harness();
    const running = h.calculate();
    change(h);
    h.resolve();
    await new Promise(resolve => setImmediate(resolve));
    assert.equal(h.posts.length, 1);
    assert.equal(h.applied.length, 0, "A stale response must not update the applied indicator");
    await running;
  });
}

test("Apply requests a fresh calculation even when its existing result matches", async () => {
  const h = harness();
  const running = h.calculate();
  assert.equal(h.posts.length, 1);
  assert.equal(h.posts[0].tabId, "manual-apply-tab");
  assert.equal(h.posts[0].liveSession, true);
  h.resolve();
  await running;
  assert.equal(h.applied.length, 1);
  assert.equal(h.state.indicator.loading, false);
});

test("an older response cannot clear a newer operation's loading state", async () => {
  const h = harness();
  const first = h.calculate();
  h.state.indicator.loading = false;
  const second = h.calculate();
  assert.equal(h.posts.length, 2);
  h.resolve();
  await first;
  assert.equal(h.applied.length, 0);
  assert.equal(h.state.indicator.loading, true);
  assert.equal(h.controls.applyIndicator.disabled, true);
  h.resolve(1);
  await second;
});

test("selection invalidation ignores a pending response even when all values return to their originals", async () => {
  const h = harness();
  const running = h.calculate();
  vm.runInContext("invalidateIndicatorCalculation()", h.runtime);
  h.resolve();
  await running;
  assert.equal(h.posts.length, 1);
  assert.equal(h.applied.length, 0);
  assert.equal(h.state.indicator.loading, false);
});

test("manual Apply waits for an in-flight real-time RAW publication", async () => {
  const h = harness();
  let finish;
  h.runtime.realtimeFinished = new Promise(resolve => { finish = resolve; });
  vm.runInContext("realtimeUpdateOwner = { finished: realtimeFinished }", h.runtime);
  const running = h.calculate();
  assert.equal(h.posts.length, 0);
  vm.runInContext("realtimeUpdateOwner = null", h.runtime);
  finish();
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(h.posts.length, 1);
  h.resolve();
  await running;
  assert.equal(h.applied.length, 1);
});

test("manual Apply waiting for a live update abandons a changed chart selection", async () => {
  const h = harness();
  let finish;
  h.runtime.realtimeFinished = new Promise(resolve => { finish = resolve; });
  vm.runInContext("realtimeUpdateOwner = { finished: realtimeFinished }", h.runtime);
  const running = h.calculate();
  vm.runInContext("symbolLoadRevision += 1; realtimeUpdateOwner = null", h.runtime);
  finish();
  await running;
  assert.equal(h.posts.length, 0);
});

test("manual Apply does not use a RAW file that needs to be reloaded after a live update", async () => {
  const h = harness();
  let finish;
  h.runtime.realtimeFinished = new Promise(resolve => { finish = resolve; });
  vm.runInContext("realtimeUpdateOwner = { finished: realtimeFinished }", h.runtime);
  const running = h.calculate();
  vm.runInContext("realtimeUpdateOwner = null", h.runtime);
  finish(true);
  await running;
  assert.equal(h.posts.length, 0);
});
