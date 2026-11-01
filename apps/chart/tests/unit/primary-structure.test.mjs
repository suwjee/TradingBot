import test from "node:test";
import assert from "node:assert/strict";

const source = "../../src/chart/primary-structure.js";

test("trend icon bottom has one hundred pixel clearance from the fiftieth candle high", async () => {
  const { trendTransitionLayout } = await import(source);
  const marker = trendTransitionLayout({ sourceTime: 100, iconCandleTime: 900, iconCandleHigh: "10" },
    { timeToX: time => time / 2, priceToY: () => 300, height: 700 });
  assert.equal(marker.lineX, 50);
  assert.deepEqual(marker.icon, { left: 436, top: 172, right: 464, bottom: 200, size: 28 });
  assert.equal(marker.lineBottom, 700);
});

test("missing fiftieth candle shows the boundary line without inventing an icon target", async () => {
  const { trendTransitionLayout } = await import(source);
  const marker = trendTransitionLayout({ sourceTime: 100, iconCandleTime: null, iconCandleHigh: null },
    { timeToX: time => time, priceToY: () => 300, height: 700 });
  assert.equal(marker.lineX, 100);
  assert.equal(marker.icon, null);
});

test("pixel icon geometry remains fixed after price and time zoom", async () => {
  const { trendTransitionLayout } = await import(source);
  const marker = trendTransitionLayout({ sourceTime: 100, iconCandleTime: 900, iconCandleHigh: "10" },
    { timeToX: time => time * 2, priceToY: () => 510, height: 700 });
  assert.equal(marker.icon.right - marker.icon.left, 28);
  assert.equal(marker.icon.bottom - marker.icon.top, 28);
  assert.equal(marker.icon.bottom, 410);
  assert.equal((marker.icon.left + marker.icon.right) / 2, 1800);
});

test("explicit bullish PH circle radius survives layout and drawing", async () => {
  const { primaryMarkerLayout, drawPrimaryStructures } = await import(source);
  assert.equal(primaryMarkerLayout("PH", "bullish", 20, 200, { primaryCircleRadius: 20 }).radius, 20);
  const context = primaryPaintContext();
  drawPrimaryStructures(context, { primaryHighs: [{ number: 1, sourceTime: 20, price: "200" }] }, {
    direction: "bullish", settings: { primaryCircleRadius: 20 },
    timeToX: value => value, priceToY: value => value,
  });
  assert.equal(context.circles[0].radius, 20);
});

test("historical hit regions and selection use the same vertical paint boundary", async () => {
  const { clipHistoricalHitBoxes } = await import(source);
  const original = [
    { shape: "rect", left: 90, right: 120, top: 10, bottom: 30 },
    { shape: "point", x: 105, y: 20, radius: 10 },
    { shape: "line", x1: 80, y1: 0, x2: 120, y2: 40 },
    { shape: "rect", left: 110, right: 130, top: 10, bottom: 30 },
  ];
  const hits = clipHistoricalHitBoxes(original, 100);
  assert.equal(hits.length, 3);
  assert.equal(hits[0].right, 100);
  assert.equal(hits[1].clipRight, 100);
  assert.deepEqual([hits[2].x2, hits[2].y2], [100, 20]);
  assert.equal(original[0].right, 120);
  assert.deepEqual(clipHistoricalHitBoxes(original, -1), []);
});

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

test("bearish PL circle has radius four, full opacity and label below", async () => {
  const { primaryMarkerLayout } = await import(source);
  const marker = primaryMarkerLayout("PL", "bearish", 100, 200);
  assert.equal(marker.shape, "circle");
  assert.equal(marker.radius, 4);
  assert.equal(marker.top, 212);
  assert.equal(marker.bottom, 220);
  assert.equal(marker.labelY, 230);
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
  assert.equal(marker.color, "#ec407a");
});

test("bullish PH uses a filled circle above its high", async () => {
  const { primaryMarkerLayout } = await import(source);
  const marker = primaryMarkerLayout("PH", "bullish", 100, 200);
  assert.equal(marker.shape, "circle");
  assert.equal(marker.top, 180);
  assert.equal(marker.bottom, 188);
  assert.equal(marker.labelY, 170);
  assert.equal(marker.color, "#056656");
  assert.equal(marker.radius, 4);
});

test("circle opacity remains a shape setting in both directions", async () => {
  const { primaryMarkerLayout } = await import(source);
  const settings = { primaryCircleOpacity: 25 };
  assert.equal(primaryMarkerLayout("PH", "bullish", 0, 0, settings).opacity, 0.25);
  assert.equal(primaryMarkerLayout("PL", "bullish", 0, 0, settings).opacity, 1);
  assert.equal(primaryMarkerLayout("PL", "bearish", 0, 0, settings).opacity, 0.25);
  assert.equal(primaryMarkerLayout("PH", "bearish", 0, 0, settings).opacity, 1);
});

test("bearish trend icon top is one hundred pixels below the fiftieth candle low", async () => {
  const { trendTransitionLayout } = await import(source);
  const marker = trendTransitionLayout({ direction: "bearish", sourceTime: 100,
    iconCandleTime: 900, iconCandleLow: "10" },
    { timeToX: time => time / 2, priceToY: () => 300, height: 700 });
  assert.deepEqual(marker.icon, { left: 436, top: 400, right: 464, bottom: 428, size: 28 });
});

test("bearish trend paints the red line and a downward reflected arrow", async () => {
  const { drawTrendTransitions } = await import(source);
  const strokes = [], scales = [], fills = [];
  const ctx = { save() {}, restore() {}, beginPath() {}, closePath() {},
    moveTo() {}, lineTo() {}, setLineDash() {}, translate() {},
    scale(x, y) { scales.push([x, y]); },
    stroke() { strokes.push(this.strokeStyle); }, fill() { fills.push(this.fillStyle); } };
  drawTrendTransitions(ctx, { trendTransitions: [{ direction: "bearish", sourceTime: 10,
    iconCandleTime: 20, iconCandleLow: "30" }] },
    { timeToX: value => value, priceToY: value => value, height: 700 });
  assert.deepEqual(strokes, ["#f23645", "#f23645"]);
  assert.deepEqual(fills, ["#f23645"]);
  assert.deepEqual(scales, [[1.4, -1.4]]);
});

test("repeated regimes retain separate clip bounds and aggregate object indexes", async () => {
  const { indicatorCalculationSegments } = await import(source);
  const first = { reactions: [{ firstIndex: 1 }], blueLines: [{ sourceIndex: 2 }],
    calculationEndTime: 100 };
  const last = { reactions: [{ firstIndex: 50 }], blueLines: [], calculationStartTime: 200 };
  const segments = indicatorCalculationSegments({ directions: {
    bearish: { reactions: [...first.reactions, ...last.reactions], calculationSegments: [first, last] },
  } });
  assert.equal(segments.length, 2);
  assert.equal(segments[0].group, first);
  assert.equal(segments[1].group, last);
  assert.equal(segments[1].objectOffsets.reactions, 1);
  assert.equal(segments[1].objectOffsets.blueLines, 1);
  assert.equal(segments[1].group.calculationEndTime, undefined);
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

test("unbroken MBL ends after four hundred analysis candles", async () => {
  const { matchingLegEndTime } = await import(source);
  assert.equal(matchingLegEndTime({ sourceIndex: 10, sourceTime: 300, stopIndex: null, stopTime: null }, true, 30), 12300);
});

test("MBL ends on the engine supplied strict crossing candle", async () => {
  const { matchingLegEndTime } = await import(source);
  assert.equal(matchingLegEndTime({ sourceIndex: 10, sourceTime: 300, stopIndex: 15, stopTime: 450 }, false, 30), 450);
});

test("both latest and earlier MBL stop at the four hundred candle cap", async () => {
  const { matchingLegEndTime } = await import(source);
  const leg = { sourceIndex: 10, sourceTime: 300, stopIndex: 510, stopTime: 15300 };
  assert.equal(matchingLegEndTime(leg, true, 30), 12300);
  assert.equal(matchingLegEndTime(leg, false, 30), 12300);
});

test("matching leg renderer does not infer a strict crossing from display OHLC", async () => {
  const { matchingLegEndTime } = await import(source);
  const leg = { sourceIndex: 0, sourceTime: 100, price: "10", low: "1", stopIndex: null };
  assert.equal(matchingLegEndTime(leg, true, 5), 2100);
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
  assert.equal(below.baselineY, 239);
  assert.equal(below.left, 85);
  assert.equal(below.right, 115);
});

test("MBL uses the engine candle cap across a session gap", async () => {
  const { matchingLegEndTime } = await import(source);
  const leg = { sourceIndex: 10, sourceTime: 300, capTime: 7300, stopIndex: null };
  assert.equal(matchingLegEndTime(leg, true, 30), 7300);
  const crossed = { ...leg, stopIndex: 60, stopTime: 9000 };
  assert.equal(matchingLegEndTime(crossed, false, 30), 7300);
  assert.equal(matchingLegEndTime(crossed, true, 30), 7300);
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
