import test from "node:test";
import assert from "node:assert/strict";

const source = "../../src/chart/primary-structure.js";

test("bearish PH arrow and label preserve both pixel gaps above the high", async () => {
  const { primaryMarkerLayout } = await import(source);
  const marker = primaryMarkerLayout("PH", "bearish", 100, 200);
  assert.equal(marker.shape, "chevrons");
  assert.equal(marker.pointsDown, true);
  assert.equal(marker.bottom, 188);
  assert.equal(marker.top, 176);
  assert.equal(marker.labelY, 166);
  assert.equal(marker.textBaseline, "bottom");
  assert.equal(marker.color, "#056656");
  assert.equal(marker.fontSize, 12);
});

test("bearish PL circle has radius twelve, full opacity and label below", async () => {
  const { primaryMarkerLayout } = await import(source);
  const marker = primaryMarkerLayout("PL", "bearish", 100, 200);
  assert.equal(marker.shape, "circle");
  assert.equal(marker.radius, 12);
  assert.equal(marker.top, 212);
  assert.equal(marker.bottom, 236);
  assert.equal(marker.labelY, 246);
  assert.equal(marker.textBaseline, "top");
  assert.equal(marker.color, "#ec407a");
  assert.equal(marker.opacity, 1);
});

test("bullish PL uses an upward arrow below its low", async () => {
  const { primaryMarkerLayout } = await import(source);
  const marker = primaryMarkerLayout("PL", "bullish", 100, 200);
  assert.equal(marker.shape, "chevrons");
  assert.equal(marker.pointsDown, false);
  assert.equal(marker.top, 212);
  assert.equal(marker.bottom, 224);
  assert.equal(marker.labelY, 234);
});

test("bullish PH uses a filled circle above its high", async () => {
  const { primaryMarkerLayout } = await import(source);
  const marker = primaryMarkerLayout("PH", "bullish", 100, 200);
  assert.equal(marker.shape, "circle");
  assert.equal(marker.top, 164);
  assert.equal(marker.bottom, 188);
  assert.equal(marker.labelY, 154);
});

test("appearance changes alter size, color, opacity and both gaps", async () => {
  const { primaryMarkerLayout } = await import(source);
  const marker = primaryMarkerLayout("PL", "bearish", 10, 100, {
    primaryCircleRadius: 9, primaryCircleColor: "#123456", primaryCircleOpacity: 60,
    primaryGap: 18, primaryLabelGap: 14, primaryLabelSize: 16,
  });
  assert.equal(marker.top, 118);
  assert.equal(marker.bottom, 136);
  assert.equal(marker.labelY, 150);
  assert.equal(marker.color, "#123456");
  assert.equal(marker.opacity, 0.6);
  assert.equal(marker.fontSize, 16);
});

test("unbroken MBL ends after one hundred analysis candles", async () => {
  const { matchingLegEndTime } = await import(source);
  assert.equal(matchingLegEndTime({ sourceIndex: 10, sourceTime: 300, stopIndex: null, stopTime: null }, true, 30), 3300);
});

test("MBL ends on the engine supplied strict crossing candle", async () => {
  const { matchingLegEndTime } = await import(source);
  assert.equal(matchingLegEndTime({ sourceIndex: 10, sourceTime: 300, stopIndex: 15, stopTime: 450 }, false, 30), 450);
});

test("only the latest MBL may extend to a crossing after one hundred candles", async () => {
  const { matchingLegEndTime } = await import(source);
  const leg = { sourceIndex: 10, sourceTime: 300, stopIndex: 160, stopTime: 4800 };
  assert.equal(matchingLegEndTime(leg, true, 30), 4800);
  assert.equal(matchingLegEndTime(leg, false, 30), 3300);
});

test("matching leg renderer does not infer a strict crossing from display OHLC", async () => {
  const { matchingLegEndTime } = await import(source);
  const leg = { sourceIndex: 0, sourceTime: 100, price: "10", low: "1", stopIndex: null };
  assert.equal(matchingLegEndTime(leg, true, 5), 600);
});

test("reset PH labels retain unique stable object identities", async () => {
  const { primaryVisualObjects } = await import(source);
  const group = { primaryHighs: [
    { id: "first", number: 1, sourceIndex: 10, sourceTime: 300, price: "20" },
    { id: "reset", number: 1, sourceIndex: 30, sourceTime: 900, price: "25" },
  ] };
  const original = primaryVisualObjects(group, "bearish");
  const reordered = primaryVisualObjects({ primaryHighs: [...group.primaryHighs].reverse() }, "bearish");
  assert.equal(new Set(original.map(item => item.id)).size, 2);
  assert.equal(original[0].id, reordered[1].id);
  assert.deepEqual(original.map(item => item.text), ["PH-1", "PH-1"]);
});

test("MBL participates in the same object tree contract as existing stop lines", async () => {
  const { primaryVisualObjects } = await import(source);
  const [item] = primaryVisualObjects({ matchingBehaviorLegs: [{ id: "leg", sourceTime: 300, price: "10" }] }, "bearish");
  assert.equal(item.type, "indicator-stop");
  assert.equal(item.name, "MBL");
  assert.equal(item.text, "MBL");
  assert.equal(item.color, "#b22833");
  assert.equal(item.width, 2);
  assert.equal(item.size, 9);
});

test("label ink has an exact ten pixel gap independently of font descent", async () => {
  const { primaryMarkerLayout, primaryLabelLayout } = await import(source);
  const metrics = { width: 30, actualBoundingBoxAscent: 9, actualBoundingBoxDescent: 2 };
  const aboveMarker = primaryMarkerLayout("PH", "bearish", 100, 200);
  const above = primaryLabelLayout(aboveMarker, metrics);
  assert.equal(aboveMarker.top - above.bottom, 10);
  assert.equal(above.baselineY, 164);
  const belowMarker = primaryMarkerLayout("PL", "bearish", 100, 200);
  const below = primaryLabelLayout(belowMarker, metrics);
  assert.equal(below.top - belowMarker.bottom, 10);
  assert.equal(below.baselineY, 255);
  assert.equal(below.left, 85);
  assert.equal(below.right, 115);
});

test("MBL uses the engine candle cap across a session gap", async () => {
  const { matchingLegEndTime } = await import(source);
  const leg = { sourceIndex: 10, sourceTime: 300, capTime: 7300, stopIndex: null };
  assert.equal(matchingLegEndTime(leg, true, 30), 7300);
  const crossed = { ...leg, stopIndex: 60, stopTime: 9000 };
  assert.equal(matchingLegEndTime(crossed, false, 30), 7300);
  assert.equal(matchingLegEndTime(crossed, true, 30), 9000);
});

test("MBL label uses its object's custom text font and color", async () => {
  const { drawPrimaryStructures } = await import(source);
  const drawn = [], measured = [];
  const context = {
    save() {}, restore() {}, setLineDash() {}, beginPath() {}, moveTo() {}, lineTo() {}, stroke() {},
    measureText(text) { measured.push(text); return { width: text.length * 10 }; },
    fillText(text, x, y) { drawn.push({ text, x, y, color: this.fillStyle, font: this.font }); },
  };
  drawPrimaryStructures(context, {
    matchingBehaviorLegs: [{ id: "leg", sourceIndex: 0, sourceTime: 100, capTime: 400, price: "10" }],
  }, {
    direction: "bearish", timeframe: 30, timeToX: time => time, priceToY: price => price,
    objectFor: () => ({ customized: true, text: "Custom MBL", size: 18, color: "#123456", width: 2, lineStyle: "dot" }),
  });
  assert.equal(drawn[0].text, "Custom MBL");
  assert.equal(drawn[0].color, "#123456");
  assert.match(drawn[0].font, /^500 18px /);
  assert.equal(drawn[0].x, 250);
  assert.deepEqual(measured, ["Custom MBL"]);
});

function primaryPaintContext() {
  const labels = [], strokes = [], circles = [];
  return {
    labels, strokes, circles,
    save() {}, restore() {}, setLineDash() {}, beginPath() {}, moveTo() {}, lineTo() {}, fill() {},
    arc(x, y, radius) { circles.push({ x, y, radius }); },
    stroke() { strokes.push(this.strokeStyle); },
    measureText(text) { return { width: text.length * 8, actualBoundingBoxAscent: 9, actualBoundingBoxDescent: 0 }; },
    fillText(text) { labels.push(text); },
  };
}

test("PH marker visibility leaves its independently enabled label visible", async () => {
  const { drawPrimaryStructures } = await import(source);
  const context = primaryPaintContext();
  drawPrimaryStructures(context, { primaryHighs: [{ id: "high", number: 1, sourceTime: 10, price: "20" }] }, {
    direction: "bearish", settings: { phVisible: false, phLabelVisible: true },
    timeframe: 30, timeToX: value => value, priceToY: value => value,
  });
  assert.deepEqual(context.labels, ["PH-1"]);
  assert.deepEqual(context.strokes, []);
});

test("PL circle visibility leaves its independently enabled label visible", async () => {
  const { drawPrimaryStructures } = await import(source);
  const context = primaryPaintContext();
  drawPrimaryStructures(context, { primaryLows: [{ id: "low", number: 2, sourceTime: 10, price: "20" }] }, {
    direction: "bearish", settings: { plVisible: false, plLabelVisible: true },
    timeframe: 30, timeToX: value => value, priceToY: value => value,
  });
  assert.deepEqual(context.labels, ["PL-2"]);
  assert.deepEqual(context.circles, []);
});

test("MBL line visibility leaves its independently enabled label visible", async () => {
  const { drawPrimaryStructures } = await import(source);
  const context = primaryPaintContext();
  drawPrimaryStructures(context, { matchingBehaviorLegs: [{ id: "leg", sourceTime: 10, sourceIndex: 0, price: "20" }] }, {
    direction: "bearish", settings: { mblVisible: false, mblLabelVisible: true },
    timeframe: 30, timeToX: value => value, priceToY: value => value,
  });
  assert.deepEqual(context.labels, ["MBL"]);
  assert.deepEqual(context.strokes, []);
});

test("per-object hidden suppresses both primary marker and label", async () => {
  const { drawPrimaryStructures } = await import(source);
  const context = primaryPaintContext();
  drawPrimaryStructures(context, { primaryHighs: [{ id: "high", number: 1, sourceTime: 10, price: "20" }] }, {
    direction: "bearish", timeframe: 30, timeToX: value => value, priceToY: value => value,
    objectFor: () => ({ hidden: true }),
  });
  assert.deepEqual(context.labels, []);
  assert.deepEqual(context.strokes, []);
});
