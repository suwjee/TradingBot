import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";

const source = readFileSync(new URL("../src/main.js", import.meta.url), "utf8").replaceAll("\r\n", "\n");
const section = (from, to) => source.slice(source.indexOf(from), source.indexOf(to, source.indexOf(from)));

function visibilityHarness() {
  const payload = { timeframe: 30, directions: { bearish: { reactions: [], stopAlls: [{ number: 1, price: "82.4090" }] } } };
  const objects = [{ id: "indicator:bearish:stopall:0", hidden: true, color: "#123456" }];
  const state = { file: { id: "source" }, drawings: [{ id: "manual-line" }], indicator: {
    enabled: true, results: payload, calculationKey: "existing-key", objects,
    selectedObjectId: objects[0].id, hitBoxes: [{ objectId: objects[0].id }], loading: false,
  } };
  const saved = new Map([["market-canvas:reaction-indicator", JSON.stringify({ enabled: true, settings: { direction: "bearish" }, from: "unchanged" })]]);
  const controls = { "#indicatorEnabled": { checked: false }, "#indicatorBtn": { classList: { toggle(_, active) { this.active = active; } } },
    "[data-direction].active": { dataset: { direction: "bearish" } } };
  const frames = [];
  const context = vm.createContext({ state, performance, $: (id) => controls[id],
    localStorage: { getItem: (key) => saved.get(key), setItem: (key, value) => saved.set(key, value) },
    updateToolbar() {}, indicatorStatus() {}, log: { indicator: { info() {} } },
    drawAll() { frames.push({ enabled: state.indicator.enabled, payload: state.indicator.results }); },
    fetch() { assert.fail("Visibility must never request calculation"); },
  });
  vm.runInContext(section("function setIndicatorVisibility(", "function formatDuration("), context);
  vm.runInContext(section('$("#indicatorEnabled").onchange', '$("#applyIndicator").onclick'), context);
  return { context, state, payload, objects, controls, frames, saved };
}

test("indicator switch labels remain clickable without widening exporter checkbox targets", () => {
  const context = vm.createContext({});
  vm.runInContext(
    section("function allowsCheckboxLabelToggle(", "document.addEventListener"),
    context,
  );
  const label = (className) => ({
    matches: (selector) => selector.split(", ").includes(`.${className}`),
  });
  assert.equal(context.allowsCheckboxLabelToggle(label("master-switch")), true);
  assert.equal(context.allowsCheckboxLabelToggle(label("module-row")), true);
  assert.equal(context.allowsCheckboxLabelToggle(label("candle-toggle-row")), false);
  assert.equal(context.allowsCheckboxLabelToggle(null), false);
});

test("master off/on restores the exact cached payload and preserves manual drawings and overrides", () => {
  const h = visibilityHarness(); const bytes = JSON.stringify(h.payload);
  h.controls["#indicatorEnabled"].onchange();
  assert.equal(h.state.indicator.enabled, false);
  assert.equal(h.state.indicator.hitBoxes.length, 0);
  assert.equal(h.state.indicator.selectedObjectId, null);
  h.controls["#indicatorEnabled"].checked = true;
  h.controls["#indicatorEnabled"].onchange();
  assert.equal(h.state.indicator.enabled, true);
  assert.equal(h.state.indicator.results, h.payload);
  assert.equal(JSON.stringify(h.state.indicator.results), bytes);
  assert.equal(h.state.indicator.objects, h.objects);
  assert.equal(h.state.indicator.calculationKey, "existing-key");
  assert.equal(h.state.drawings[0].id, "manual-line");
  assert.equal(h.controls["#indicatorBtn"].classList.active, true);
  assert.deepEqual(h.frames.map((frame) => frame.enabled), [false, true]);
  assert.equal(JSON.parse(h.saved.get("market-canvas:reaction-indicator")).from, "unchanged");
});

test("Apply while disabled keeps the cache available for the next On", async () => {
  const h = visibilityHarness();
  vm.runInContext(section("async function calculateIndicator()", '$("#indicatorBtn").onclick = openIndicator'), h.context);
  await h.context.calculateIndicator();
  assert.equal(h.state.indicator.results, h.payload);
  h.context.setIndicatorVisibility(true);
  assert.equal(h.state.indicator.enabled, true);
});

test("Apply with unchanged calculation inputs re-enables cached drawings without fetching", async () => {
  const h = visibilityHarness();
  h.controls["#indicatorEnabled"].checked = true;
  h.controls["#indicatorFrom"] = { value: "100" };
  h.controls["#indicatorTo"] = { value: "200" };
  h.state.raw = [{ time: 100 }, { time: 200 }];
  h.state.indicator.enabled = false;
  let visualUpdates = 0;
  Object.assign(h.context, { parseTehranInput: Number,
    indicatorSettings: () => ({ timeframe: "30", direction: "bearish" }),
    calculationKey: () => "existing-key", applyVisualSettings() { visualUpdates++; },
    toast() {}, pushIndicatorActivity() {},
  });
  vm.runInContext(section("async function calculateIndicator()", '$("#indicatorBtn").onclick = openIndicator'), h.context);
  await h.context.calculateIndicator();
  assert.equal(h.state.indicator.enabled, true);
  assert.equal(h.state.indicator.results, h.payload);
  assert.equal(visualUpdates, 1);
});

test("visibility tolerates blocked browser storage and does not pretend absent results exist", () => {
  const h = visibilityHarness();
  h.context.localStorage.getItem = () => { throw new Error("storage denied"); };
  h.context.setIndicatorVisibility(false); h.context.setIndicatorVisibility(true);
  assert.equal(h.state.indicator.enabled, true);
  h.state.indicator.results = null; h.context.setIndicatorVisibility(true);
  assert.equal(h.state.indicator.enabled, false);
});

test("manual drawings stay anchored to time and price, not a stale logical index", () => {
  const calls = { logical: 0 };
  const context = vm.createContext({
    state: { data: [{ time: 100 }, { time: 160 }], tf: 60 },
    chart: {
      timeScale: () => ({
        timeToCoordinate: (time) => time === 120 ? 48 : null,
        logicalToCoordinate() { calls.logical++; return 999; },
        options: () => ({ barSpacing: 8 }),
      }),
    },
    series: { priceToCoordinate: (price) => price * 2 },
    log: { chart: { warn() {} } },
  });
  vm.runInContext(
    section("function validDrawingPoint(", "function validStoredDrawing(") +
      section("function xy(", "function rgba("),
    context,
  );
  const rendered = context.xy({ time: 120, price: 25, logical: 999 });
  assert.equal(rendered.x, 48);
  assert.equal(rendered.y, 50);
  assert.equal(calls.logical, 0);
});

test("moving a drawing never changes its legacy logical metadata", () => {
  const context = vm.createContext({ clone: (value) => structuredClone(value) });
  vm.runInContext(section("function shiftPoint(", "function selectDrawingTool("), context);
  const point = { time: 100, price: 25, logical: 42 };
  assert.equal(context.shiftPoint(point, 30, -5), true);
  assert.deepEqual(point, { time: 130, price: 20, logical: 42 });
});

test("mobile swipe/cancel suppresses tool click, but fresh taps and keyboard activation still work", () => {
  const handlers = {};
  const drawingToolbar = { addEventListener(type, handler) { handlers[type] = handler; } };
  const context = vm.createContext({ drawingToolbar, window: { matchMedia: () => ({ matches: true }) } });
  vm.runInContext(section("let toolbarTouch = null", 'window.matchMedia("(max-width: 760px)").addEventListener'), context);
  let prevented = 0, stopped = 0;
  const click = { detail: 1, preventDefault() { prevented++; }, stopImmediatePropagation() { stopped++; } };
  const down = { pointerType: "touch", pointerId: 5, clientX: 200, clientY: 20 };
  handlers.pointerdown(down);
  handlers.pointermove({ ...down, clientX: 240 }); handlers.pointerup(); handlers.click(click);
  assert.equal(prevented, 1); assert.equal(stopped, 1);
  handlers.pointerdown(down); handlers.pointercancel(); handlers.click(click);
  assert.equal(prevented, 2);
  handlers.pointerdown(down); handlers.pointerup(); handlers.click(click);
  assert.equal(prevented, 2);
  handlers.pointerdown(down); handlers.pointercancel(); handlers.click({ ...click, detail: 0 });
  assert.equal(prevented, 2);
});

test("StopAll label is above bearish marker and below bullish marker, with equal gap", () => {
  const paint = section('      if (!settings.stopAllVisible || object?.hidden', '    if (settings.orderStopVisible)');
  const body = paint.slice(0, paint.lastIndexOf("    }"));
  const labels = [];
  const ctx = { save() {}, restore() {}, beginPath() {}, arc() {}, fill() {}, stroke() {},
    fillText(text, x, y) { labels.push({ text, x, y, baseline: this.textBaseline }); } };
  const context = vm.createContext({ ctx, state: { indicator: { hitBoxes: [] } }, object: null, objectId: "marker",
    settings: { stopAllVisible: true, stopAllRadius: 8, stopAllGap: 16, stopAllSize: 20 },
    zone: { number: 1 }, x: 100, y: 200, rgba: () => "#ff9800", offsetIndicatorPoint: (_, x, y) => ({ x, y }),
  });
  for (const bullish of [true, false]) {
    context.bullish = bullish;
    vm.runInContext(`for (let once = 0; once < 1; once++) { ${body} }`, context);
  }
  assert.deepEqual(labels, [{ text: "1", x: 100, y: 224, baseline: "top" }, { text: "1", x: 100, y: 176, baseline: "bottom" }]);
});

test("pinned panels resize beyond the handle, ignore other pointers and persist on release", () => {
  for (const id of ["indicatorModal", "objectTree"]) {
    const events = {}, attributes = {}, panelWidths = { [id]: 300 }, writes = [];
    const handle = { setAttribute(key, value) { attributes[key] = value; },
      addEventListener(type, fn) { this[type] = fn; }, setPointerCapture() {}, hasPointerCapture: () => false };
    const panel = { id, querySelector: () => null, prepend() {}, classList: { contains: () => true } };
    const context = vm.createContext({ document: { createElement: () => handle }, PANEL_MIN_WIDTH: 270, PANEL_MAX_WIDTH: 560,
      panelWidths, panelWidthLimit: () => 560,
      applyPinnedPanelWidth(panel, width, persist) { panelWidths[panel.id] = Math.max(270, Math.min(560, width)); if (persist) writes.push(panelWidths[panel.id]); },
      requestAnimationFrame(fn) { fn(); return 1; }, cancelAnimationFrame() {},
      window: { addEventListener(type, fn) { events[type] = fn; }, removeEventListener(type) { delete events[type]; } },
    });
    vm.runInContext(section("function ensurePanelResizeHandle(", "function setPanelPinned("), context);
    context.ensurePanelResizeHandle(panel);
    handle.pointerdown({ button: 0, pointerId: 1, clientX: 900, preventDefault() {} });
    events.pointermove({ pointerId: 2, clientX: 300 });
    assert.equal(panelWidths[id], 300);
    events.pointermove({ pointerId: 1, clientX: 760 });
    assert.equal(panelWidths[id], 440);
    events.pointerup({ type: "pointerup", pointerId: 1 });
    assert.deepEqual(writes, [440]); assert.equal(Object.keys(events).length, 0);
    handle.keydown({ key: "ArrowRight", preventDefault() {} });
    assert.equal(panelWidths[id], 428);
    handle.keydown({ key: "End", preventDefault() {} });
    assert.equal(panelWidths[id], 560);
  }
});
