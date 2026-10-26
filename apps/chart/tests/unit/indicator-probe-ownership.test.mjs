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
    analysisTimeframe: 30, from: 100, to: 200, direction: "bearish", sourceFingerprint: "old-source" };
  const state = { file: { id: "A.json", chartId: "A", symbol: "A" }, tf: 30,
    raw: [{ time: 0 }, { time: 300 }], data: [],
    indicator: { loading: false, results: {}, resultContext: context }, indicatorRange: {} };
  const posts = [], probes = [], applied = [];
  const noop = () => {};
  const sandbox = { ...lifecycle, state, inputs, controls, posts, performance, AbortController, setTimeout, clearTimeout, clearInterval,
    $: selector => selector === "[data-direction].active" ? { dataset: { direction: inputs.direction } }
      : controls[selector.replace(/^#/, "")] ||= { dataset: {}, focus: noop, classList: { toggle: noop } },
    indicatorApplyProblem: () => null, indicatorSettings: () => ({ ...inputs }),
    parseTehranInput: Number, normalizeIndicatorRange: () => null, calculationKey: () => "key",
    clone: value => structuredClone(value), indicatorStatus: noop, indicatorToast: noop,
    log: { indicator: { info: noop, warn: noop, error: noop } },
    setIndicatorVisibility: value => applied.push(["visible", value]), applyVisualSettings: value => applied.push(["settings", value]),
    pushIndicatorActivity: noop, createUniqueId: () => "request", formatTehran: String,
    startCalculationProgress: () => ({ events: [], recordEvent: noop, source: { close: noop } }), stopCalculationProgress: noop,
    setCalculationProgress: noop,
    buildIndicatorCalculationRequest: value => value,
    fetch: (url, options) => {
      if (url === "/api/reactions/source") return new Promise(resolve => probes.push(resolve));
      posts.push(JSON.parse(options.body));
      return new Promise(() => {});
    },
  };
  const runtime = vm.createContext(sandbox);
  const invalidateStart = main.indexOf("function invalidateIndicatorCalculation() {");
  const invalidate = invalidateStart < 0 ? "" : main.slice(invalidateStart, main.indexOf("\nfunction clearActiveIndicatorCalculation()", invalidateStart));
  vm.runInContext(`let indicatorCalculationOwner = null;\n${invalidate}\n${actualCalculate}`, runtime);
  return { state, controls, inputs, posts, probes, applied, runtime,
    calculate: () => vm.runInContext("calculateIndicator()", runtime),
    resolve: (fingerprint = "new-source", index = 0) => probes[index]({ ok: true, json: async () => ({ sourceFingerprint: fingerprint }) }),
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
  test(`pending Source probe abandons stale ${name}`, async () => {
    const h = harness();
    const running = h.calculate();
    change(h);
    h.resolve();
    await new Promise(resolve => setImmediate(resolve));
    assert.equal(h.posts.length, 0, "A stale selection must not submit an Engine request");
    assert.equal(h.applied.length, 0, "A stale selection must not restore old visibility/settings");
    await running;
  });
}

test("unchanged selection still reuses a verified calculation after the probe", async () => {
  const h = harness();
  const running = h.calculate();
  h.resolve("old-source");
  await running;
  assert.equal(h.posts.length, 0);
  assert.deepEqual(h.applied.map(item => item[0]), ["visible", "settings"]);
  assert.equal(h.state.indicator.loading, false);
  assert.equal(h.controls.applyIndicator.disabled, false);
});

test("an older probe cannot clear a newer operation's loading state", async () => {
  const h = harness();
  const first = h.calculate();
  h.state.indicator.loading = false;
  const second = h.calculate();
  assert.equal(h.probes.length, 2);
  h.resolve("new-source", 0);
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(h.posts.length, 0);
  assert.equal(h.state.indicator.loading, true);
  assert.equal(h.controls.applyIndicator.disabled, true);
  h.resolve("old-source", 1);
  await second;
  await first;
});

test("selection invalidation cancels a probe even when all values return to their originals", async () => {
  const h = harness();
  const running = h.calculate();
  vm.runInContext("invalidateIndicatorCalculation()", h.runtime);
  h.resolve("old-source");
  await running;
  assert.equal(h.posts.length, 0);
  assert.equal(h.applied.length, 0);
  assert.equal(h.state.indicator.loading, false);
});
