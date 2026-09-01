import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";

// Execute the installed library's own color selector, not a copied comparison.
const library = readFileSync(new URL("../node_modules/lightweight-charts/dist/lightweight-charts.development.mjs", import.meta.url), "utf8");
const start = library.indexOf("const barStyleFnMap = {");
const end = library.indexOf("class SeriesBarColorer", start);
assert.ok(start >= 0 && end > start, "Review color contract after a library upgrade");
const select = vm.runInNewContext(`${library.slice(start, end)}; barStyleFnMap.Candlestick`, {
  ensure: (value) => { assert.notEqual(value, undefined); return value; },
  ensureNotNull: (value) => { assert.notEqual(value, null); return value; },
});

test("installed Lightweight Charts uses up body, border and wick for dojis", () => {
  const style = { upColor: "UP", downColor: "DOWN", borderUpColor: "UP_BORDER",
    borderDownColor: "DOWN_BORDER", wickUpColor: "UP_WICK", wickDownColor: "DOWN_WICK" };
  for (const [open, close, side] of [[9,10,"UP"], [10,9,"DOWN"], [10,10,"UP"], [0,-0,"UP"]]) {
    const colors = select(() => ({ _internal_value: [open,11,-1,close] }), style, 0);
    assert.equal(colors._internal_barColor, side);
    assert.equal(colors._internal_barBorderColor, `${side}_BORDER`);
    assert.equal(colors._internal_barWickColor, `${side}_WICK`);
  }
});

test("chart aggregation and OHLC display retain up color on a 30-second doji", () => {
  const source = readFileSync(new URL("../src/main.js", import.meta.url), "utf8");
  const nodes = Object.fromEntries(["#o", "#h", "#l", "#c"].map(id => [id, { style: {} }]));
  const context = vm.createContext({ $: id => nodes[id], Intl });
  vm.runInContext(source.slice(source.indexOf("function aggregate("), source.indexOf("function renderTf(")), context);
  const bars = context.aggregate([
    { time: 1800000000, open: 10, high: 12, low: 9, close: 11 },
    { time: 1800000029, open: 11, high: 11, low: 8, close: 10 },
  ], 30);
  assert.equal(bars.length, 1);
  assert.equal(bars[0].open, bars[0].close);
  assert.equal(bars[0].color, undefined); // No per-candle override of library colors.
  context.setOHLC(bars[0]);
  for (const node of Object.values(nodes)) assert.equal(node.style.color, "var(--chart-bullish)");
});
