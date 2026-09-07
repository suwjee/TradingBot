import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";
import { drawingArray, normalizeHistorySnapshot, restoredTimeframe, CHART_TIMEFRAME_KEY, indicatorControlId } from "../src/chart-state.js";

const source = readFileSync(new URL("../src/main.js", import.meta.url), "utf8").replaceAll("\r\n", "\n");
const section = (start, end) => source.slice(source.indexOf(start), source.indexOf(end, source.indexOf(start)));
const drawing = { id: "line-1", type: "line", a: { time: 1780000000, price: 12.345 }, b: { time: 1780000030, price: 15 }, stroke: "#123456", extensionField: { preserve: true } };
const indicator = { id: "indicator:bullish:e:0", color: "#aabbcc", hidden: true, locked: false };
function harness() {
  const buttons = Object.fromEntries(["undoBtn", "redoBtn"].map((id) => [`#${id}`, { click() { this.onclick(); } }]));
  const state = { drawings: [structuredClone(drawing)], history: [], redo: [], file: { id: "file-a" },
    selected: "line-1", selectedIds: ["line-1"], treeSelectedIds: ["line-1"],
    indicator: { objects: [structuredClone(indicator)], selectedObjectId: indicator.id } };
  const saved = new Map(), calls = [];
  const context = vm.createContext({ state, structuredClone, drawingArray, normalizeHistorySnapshot, indicatorControlId,
    CHART_TIMEFRAME_KEY, localStorage: { getItem: (key) => saved.get(key), setItem: (key, value) => saved.set(key, value) },
    $: (id) => buttons[id], log: { chart: { warn() {}, error() {} } },
    updateToolbar() { calls.push("toolbar"); }, renderObjectTree() { state.drawings.filter(() => true); calls.push("tree"); },
    drawAll() { state.drawings.find(() => true); calls.push("draw"); }, saveDrawings() { calls.push(structuredClone(state.drawings)); } });
  vm.runInContext(section("function checkpoint()", "function resize()"), context);
  vm.runInContext(section('$("#undoBtn").onclick', 'if ($("#lockAllBtn"))'), context);
  return { state, saved, calls, context, buttons };
}

test("toolbar undo/redo restores drawings AND indicator appearance, selections and map", () => {
  const h = harness(); h.context.checkpoint();
  h.state.drawings[0].a.price = 50; h.state.indicator.objects[0].color = "#ffffff";
  h.buttons["#undoBtn"].click();
  assert.deepEqual(h.state.drawings, [drawing]);
  assert.deepEqual(h.state.indicator.objects, [indicator]);
  assert.equal(h.state.indicator.objectMap.get(indicator.id), h.state.indicator.objects[0]);
  assert.equal(h.state.selected, null); assert.equal(h.state.selectedIds.length, 0);
  assert.equal(h.state.indicator.selectedObjectId, null);
  h.buttons["#redoBtn"].click();
  assert.equal(h.state.drawings[0].a.price, 50); assert.equal(h.state.indicator.objects[0].color, "#ffffff");
  assert.ok(h.calls.includes("draw"));
  h.buttons["#undoBtn"].click(); h.context.checkpoint();
  assert.equal(h.state.redo.length, 0);
});

test("legacy array history, nested corrupt snapshots and malformed fields preserve valid data", () => {
  const h = harness(); h.state.history.push([{ ...drawing, stroke: "#abcdef" }]);
  h.buttons["#undoBtn"].click();
  assert.equal(h.state.drawings[0].stroke, "#abcdef"); assert.deepEqual(h.state.indicator.objects, [indicator]);
  h.state.history.push({ drawings: { drawings: [drawing] }, indicatorObjects: "invalid" });
  h.buttons["#undoBtn"].click(); assert.deepEqual(h.state.drawings, [drawing]);
  h.state.history.push({ drawings: { unknown: true } });
  h.buttons["#undoBtn"].click(); assert.deepEqual(h.state.drawings, [drawing]);
  assert.deepEqual(h.state.indicator.objects, [indicator]);
  h.state.drawings[0].extensionField.preserve = false;
  assert.equal(drawing.extensionField.preserve, true);
  for (let i = 0; i < 90; i++) h.context.checkpoint();
  assert.equal(h.state.history.length, 80);
});

test("persisted snapshot recovery retains valid drawings despite localStorage failure", async () => {
  const h = harness();
  h.context.fetch = async () => ({ ok: true, json: async () => ({ drawings: { drawings: [drawing, { invalid: true }] } }) });
  h.context.localStorage.setItem = () => { throw new Error("quota"); };
  vm.runInContext(section("function storageKey()", "function saveDrawings()") + section("function validDrawingPoint(", "function checkpoint()"), h.context);
  await h.context.loadDrawings(); assert.deepEqual(h.state.drawings, [drawing]);
  h.context.fetch = async () => ({ ok: true, json: async () => ({ unknown: true }) });
  await h.context.loadDrawings(); assert.deepEqual(h.state.drawings, [drawing]);
});

test("late drawing load cannot replace the newly selected source", async () => {
  const h = harness(); let resolve;
  h.context.fetch = () => new Promise((done) => { resolve = done; });
  vm.runInContext(section("function storageKey()", "function saveDrawings()") + section("function validDrawingPoint(", "function checkpoint()"), h.context);
  const pending = h.context.loadDrawings();
  h.state.file = { id: "file-b" }; h.state.drawings = [];
  resolve({ ok: true, json: async () => [drawing] }); await pending;
  assert.equal(h.state.drawings.length, 0); assert.equal(h.saved.size, 0);
});

test("keyboard routes the shared restore and leaves text-field undo alone", () => {
  const h = harness(); let keydown;
  h.context.document = { activeElement: { matches: () => false }, addEventListener: (_, fn) => { keydown = fn; } };
  h.context.cancelDrawingTool = () => {};
  vm.runInContext(section('document.addEventListener("keydown", (e) => {\n  if (', "setInterval("), h.context);
  h.context.checkpoint(); h.state.drawings = [];
  let prevented = false;
  const key = { key: "z", ctrlKey: true, preventDefault() { prevented = true; } };
  keydown(key); assert.deepEqual(h.state.drawings, [drawing]); assert.equal(prevented, true);
  keydown({ ...key, shiftKey: true }); assert.equal(h.state.drawings.length, 0);
  keydown(key); keydown({ ...key, key: "y" }); assert.equal(h.state.drawings.length, 0);
  h.context.document.activeElement.matches = () => true; prevented = false;
  keydown(key); assert.equal(prevented, false); assert.equal(h.state.drawings.length, 0);
});

test("chart timeframe selection survives reload; unsupported values fall back", () => {
  const h = harness();
  Object.assign(h.context, { sourceTimeframeSeconds: () => 5, renderTimeframeControls() {}, renderTf() {}, toast() {} });
  vm.runInContext(section("function selectTimeframe(", "renderTimeframeControls();"), h.context);
  h.context.selectTimeframe(300, "5m");
  assert.equal(restoredTimeframe(h.context.localStorage, [{ s: 30 }, { s: 300 }]), 300);
  h.context.selectTimeframe(1, "1s"); assert.equal(h.state.tf, 300);
  h.saved.set(CHART_TIMEFRAME_KEY, "bad"); assert.equal(restoredTimeframe(h.context.localStorage, [{ s: 30 }]), 30);
  assert.equal(restoredTimeframe({ getItem() { throw new Error("denied"); } }, []), 30);
});

test("saved indicator timeframe maps to the real form control, not an absent timeframe id", () => {
  assert.equal(indicatorControlId("timeframe"), "indicatorTf");
  assert.equal(indicatorControlId("bullFill"), "bullFill");
  assert.match(section("function openIndicator(", "async function calculateIndicator()"), /indicatorControlId\(id\)/);
  assert.match(source, /tf: restoredTimeframe\(localStorage, TF\)/);
});

test("Reset labels and audit-only stop lines stay hidden while audit order boxes render", () => {
  const objectSection = section("function rebuildIndicatorObjects()", "function indicatorOffset(");
  const drawSection = section("function drawIndicator()", "function renderObjectTree()");
  const stopSection = section("if (settings.orderStopVisible)", "const representedOrderKeys");
  assert.doesNotMatch(objectSection, /indicator:\$\{direction\}:reset:/);
  assert.doesNotMatch(drawSection, /for \(const \[resetIndex, reset\]/);
  assert.match(objectSection, /group\.orderAudit \|\| \[\]/);
  assert.match(objectSection, /indicator:\$\{direction\}:audit-order:/);
  assert.match(drawSection, /for \(const \[auditIndex, order\] of \(group\.orderAudit \|\| \[\]\)\.entries\(\)\)/);
  assert.match(drawSection, /representedOrderKeys\.has\(key\)/);
  assert.doesNotMatch(stopSection, /group\.orderAudit/);
  assert.match(stopSection, /group\.sZones/);
  assert.match(stopSection, /group\.eZones/);
  assert.match(stopSection, /group\.stopAlls/);
});

test("Calculation report opens the exact persisted cache identity without fetching or recalculating", async () => {
  const h = harness(); const payload = { directions: { bullish: { stopAlls: [] } }, timeframe: 30 };
  h.state.tf = 60;
  h.state.raw = [{ time: 1780000000, open: 12.3, high: 12.4, low: 12.1, close: 12.2 }];
  h.state.data = [{ time: 1779999960, open: 12.3, high: 12.4, low: 12.1, close: 12.2 }];
  h.state.indicator.results = payload; h.state.indicator.settings = { timeframe: "follow" };
  h.state.indicator.resultContext = { from: 1780000000, to: 1780000000, calculationId: "TEST/30s/bullish/1-30--0123456789abcdef.json" };
  let opened, notices = [];
  Object.assign(h.context, { window: {}, chartSettings: {},
    openManualReviewTab: (context, host) => { opened = { context, host }; return { focus() {} }; },
    fetch() { assert.fail("Export must never fetch"); }, calculateIndicator() { assert.fail("Export must never calculate"); },
    aggregate() { assert.fail("Export must never reaggregate cached candles"); },
    toast(message) { notices.push(message); } });
  h.context.log.chart.info = () => {};
  vm.runInContext(section("async function exportChartData()", '$("#reportBtn").onclick'), h.context);
  await h.context.exportChartData();
  assert.equal(opened.host, h.context.window);
  assert.equal(opened.context.calculationId, "TEST/30s/bullish/1-30--0123456789abcdef.json");
  h.state.indicator.results = null; opened = undefined;
  await h.context.exportChartData(); assert.equal(opened, undefined);
  assert.match(notices.at(-1), /Calculate the indicator/);
});

test("Calculation report reports a blocked tab", async () => {
  const h = harness(); const payload = { directions: { bullish: { stopAlls: [] } }, timeframe: 30 };
  h.state.indicator.results = payload; h.state.indicator.resultContext = { calculationId: "TEST/30s/bullish/1-30--0123456789abcdef.json" };
  const notices = [], errors = [];
  Object.assign(h.context, { window: {}, chartSettings: {},
    openManualReviewTab: () => null,
    toast(message) { notices.push(message); } });
  h.context.log.chart.error = (event, error) => { errors.push([event, error]); };
  vm.runInContext(section("async function exportChartData()", '$("#reportBtn").onclick'), h.context);
  await h.context.exportChartData();
  assert.match(notices.at(-1), /Could not open the calculation report/);
  assert.equal(errors.length, 1); assert.equal(errors[0][0], "CALCULATION_REPORT_OPEN_FAILED");
});

test("indicator From handle follows its selected time after the chart viewport pans", () => {
  const handles = {
    "#indicatorRangeHandles": { classList: { toggle() {} }, setAttribute() {} },
    "#rangeFromHandle": { style: {}, querySelector: () => ({ textContent: "" }), setAttribute() {} },
    "#rangeToHandle": { style: {}, querySelector: () => ({ textContent: "" }), setAttribute() {} },
    "#rangeFromGuide": { style: {}, querySelector: () => null },
    "#rangeToGuide": { style: {}, querySelector: () => null },
    "#indicatorFrom": { value: "" },
    "#indicatorTo": { value: "" },
  };
  let fromX = 200;
  const context = vm.createContext({
    $: (selector) => handles[selector],
    chartWorkspaceActive: () => true,
    chartElement: { clientWidth: 400 },
    state: {
      data: Array.from({ length: 10 }, (_, index) => ({ time: 100 + index * 10 })),
      indicatorRange: { from: 120, to: 180, dragging: null, preview: false },
    },
    chart: { timeScale: () => ({ timeToCoordinate: (time) => time === 120 ? fromX : 320 }) },
    parseTehranInput: () => NaN,
    formatTehran: (time) => String(time),
  });
  vm.runInContext(section("function syncIndicatorRangeHandles()", "function commitIndicatorRangeInputs()"), context);
  context.syncIndicatorRangeHandles();
  assert.equal(handles["#rangeFromHandle"].style.left, "200px");
  fromX = 120;
  context.syncIndicatorRangeHandles();
  assert.equal(handles["#rangeFromHandle"].style.left, "120px");
});
