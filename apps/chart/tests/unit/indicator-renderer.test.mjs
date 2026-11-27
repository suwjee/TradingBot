import test from "node:test";
import assert from "node:assert/strict";
import { drawIndicator, indicatorDecorationObjects } from "../../src/chart/indicator-renderer.js";

test("reaction numbers and verdict decorations have separate paint and hit regions", () => {
  const settings = {
    reactionVisible: true, bullWidth: 1, bullOpacity: 20,
    numberEnabled: true, numberMode: "reset", numberSize: 10, numberWeight: 400, numberGap: 4, numberColor: "#123456",
    eVisible: true, eGap: 12,
  };
  const group = {
    reactions: [
      { firstIndex: 1, firstTime: 10, boxTopSourceTime: 10, breakTime: 25, boxTop: 50, boxBottom: 40 },
      { firstIndex: 4, firstTime: 30, boxTopSourceTime: 30, breakTime: 50, boxTop: 50, boxBottom: 40 },
    ],
    resets: [{ index: 3 }],
    eZones: [{ sourceIndex: 5, sourceTime: 70, price: 50, number: 1, trueFalse: "F",
      trueFalseRepeated: true, trueFalseRepeatCount: 2, trueFalseRepeatF: true }],
  };
  const direction = "bullish";
  const decorations = indicatorDecorationObjects(group, direction, settings, { reactions: 0, eZones: 0 });
  assert.deepEqual(decorations.map(item => [item.id, item.text]), [
    ["indicator:bullish:reaction:0:number", "1"], ["indicator:bullish:reaction:1:number", "1"],
    ["indicator:bullish:e:0:verdict", "F"], ["indicator:bullish:e:0:stars", "**"], ["indicator:bullish:e:0:x", "X"],
  ]);
  const objects = new Map(decorations.map(item => [item.id, item]));
  Object.assign(objects.get("indicator:bullish:e:0:stars"), { hidden: true });
  Object.assign(objects.get("indicator:bullish:e:0:x"), { customized: true, xOffset: 20, text: "Moved", color: "#800080" });
  objects.set("indicator:bullish:e:0", { hidden: true });
  const paint = [];
  const ctx = {
    save() {}, restore() {}, beginPath() {}, rect() {}, fill() {}, stroke() {}, setLineDash() {},
    fillText(text, x, y) { paint.push([text, x, y, this.fillStyle]); },
  };
  const state = { tf: 30, indicator: { enabled: true, settings, results: { directions: { [direction]: group } } } };
  drawIndicator(300, 200, {
    ctx, state, indicatorTimeToCoordinate: value => value, priceToY: value => 100 - value,
    overlayPriceCoordinate: value => 100 - value, indicatorObject: id => objects.get(id),
    indicatorOffsetPixels: () => ({ x: 0, y: 0 }),
    offsetIndicatorPoint: (item, x, y) => ({ x: x + (item?.xOffset ?? 0), y }),
    dash: () => [], rgba: () => "#fff",
  });
  assert.deepEqual(paint, [["1", 17.5, 64, "#123456"], ["1", 40, 64, "#123456"],
    ["F", 70, 75, "#be123c"], ["Moved", 90, 85, "#800080"]]);
  const hits = state.indicator.hitBoxes.map(hit => hit.objectId);
  assert.ok(hits.includes("indicator:bullish:reaction:1:number"));
  assert.ok(hits.includes("indicator:bullish:e:0:x"));
  assert.ok(!hits.includes("indicator:bullish:e:0") && !hits.includes("indicator:bullish:e:0:stars"));
});

test("moved and partially customized indicator objects inherit missing appearance fields", () => {
  const fills = [], strokes = [], rects = [];
  const ctx = {
    save() {}, restore() {}, beginPath() {}, moveTo() {}, lineTo() {},
    setLineDash(value) { this.lineDash = value; },
    rect(...value) { rects.push(value); },
    fill() { fills.push(this.fillStyle); },
    stroke() { strokes.push([this.strokeStyle, this.lineWidth, this.lineDash]); },
  };
  const settings = {
    reactionVisible: true, bullFill: "#112233", bullBorder: "#334455", bullOpacity: 20,
    bullWidth: 2, bullLineStyle: "dash", blueLineEnabled: true, blueColor: "#2288cc",
    blueOpacity: 25, blueWidth: 3, blueLineStyle: "solid", orderVisible: true,
    orderFill: "#334455", orderColor: "#667788", orderOpacity: 35, orderWidth: 4, orderLineStyle: "dot",
  };
  const group = {
    reactions: [{ firstIndex: 1, boxTopSourceTime: 10, breakTime: 30, boxTop: 80, boxBottom: 70 }],
    blueLines: [{ startTime: 20, endTime: 50, linePrice: 75 }],
    orderAudit: [{ firstIndex: 2, breakIndex: 3, boxTopSourceTime: 30, boxBottomSourceTime: 30,
      breakTime: 50, boxTop: 65, boxBottom: 60 }],
  };
  const objects = {
    "indicator:bullish:reaction:0": { customized: true, offsetTime: 5, offsetPrice: 2, color: "#aabbcc", opacity: 0 },
    "indicator:bullish:blue:0": { customized: true, offsetTime: 7 },
    "indicator:bullish:audit-order:2:3": { customized: true, width: 5 },
  };
  const dependencies = {
    ctx,
    state: { tf: 30, indicator: { enabled: true, settings, results: { directions: { bullish: group } } } },
    indicatorTimeToCoordinate: time => time,
    overlayPriceCoordinate: price => price,
    priceToY: price => price,
    indicatorObject: id => objects[id],
    indicatorOffsetPixels: object => ({ x: object.offsetTime ?? 0, y: object.offsetPrice ?? 0 }),
    offsetIndicatorRect: (_object, x1, y1, x2, y2) => ({ x1, y1, x2, y2 }),
    rgba: (color, alpha) => `${color.slice(1)}/${alpha}`,
    dash: name => name,
  };
  drawIndicator(200, 200, dependencies);
  assert.deepEqual(rects[0], [15, 72, 20, 10]);
  assert.deepEqual(fills, ["112233/0", "334455/0.35"]);
  assert.deepEqual(strokes, [["#aabbcc", 2, "dash"], ["2288cc/0.25", 3, "solid"], ["#667788", 5, "dot"]]);
});

test("A, S, E and StopAll render at the default dimensions and honor style overrides", () => {
  const fontSizes = {};
  const radii = [];
  const liquiditySizes = [];
  const ctx = {
    save() {},
    restore() {},
    beginPath() {},
    fill() {},
    stroke() {},
    rect() {}, clip() {}, setLineDash() {}, moveTo() {}, lineTo() {},
    measureText() { return { width: 18 }; },
    arc(_x, _y, radius) { radii.push(radius); },
    fillText(label) {
      const size = Number(/ (\d+)px/.exec(this.font)[1]);
      if (label === "$$$") liquiditySizes.push(size);
      else fontSizes[label] = size;
    },
  };
  const settings = { aVisible: true, sVisible: true, eVisible: true, stopAllVisible: true };
  const dependencies = {
    ctx,
    state: {
      indicator: {
        enabled: true,
        settings,
        results: { directions: { bullish: {
          reactions: [],
          aZones: [{ sourceIndex: 1, sourceTime: 30, price: 100 }],
          sZones: [{ sourceIndex: 2, sourceTime: 60, price: 100 }],
          eZones: [{ sourceIndex: 3, sourceTime: 90, price: 100, number: 1 }],
          liquidity: [60, 90].map(sourceTime => ({ sourceTime, price: 100, visibleFrom: 120, lineEndTime: 190 })),
          stopAlls: [{ sourceIndex: 4, sourceTime: 120, price: 100, number: 2 }],
        } } },
      },
    },
    indicatorTimeToCoordinate: (time) => time,
    priceToY: (price) => price,
    overlayPriceCoordinate: (price) => price,
    indicatorObject: () => null,
    offsetIndicatorPoint: (_object, x, y) => ({ x, y }),
    rgba: () => "#fff",
  };

  drawIndicator(200, 200, dependencies);
  assert.deepEqual(fontSizes, { A: 10, S: 10, E1: 10, 2: 14 });
  assert.deepEqual(radii, [5]);

  Object.assign(settings, { aSize: 12, sSize: 13, eSize: 16, stopAllSize: 20, stopAllRadius: 8 });
  drawIndicator(200, 200, dependencies);
  assert.deepEqual(fontSizes, { A: 12, S: 13, E1: 16, 2: 20 });
  assert.deepEqual(radii, [5, 8]);
  assert.deepEqual(liquiditySizes, [10, 10, 13, 16]);

  dependencies.indicatorObject = id => id === "indicator:bullish:e:0" ? { customized: true, size: 19 } : null;
  drawIndicator(200, 200, dependencies);
  assert.deepEqual(liquiditySizes.slice(-2), [13, 19]);
  assert.equal(fontSizes.E1, 19);
});

test("verdict visibility and appearance are independent for Foundation, Secondary and PH-PL", () => {
  const verdicts = [];
  const ctx = {
    save() {}, restore() {}, beginPath() {}, fill() {}, stroke() {}, arc() {},
    setLineDash() {}, moveTo() {}, lineTo() {}, measureText() { return { width: 20 }; },
    fillText(text, x) {
      if (["T", "F", "N/A"].includes(text)) verdicts.push([text, x, this.fillStyle, this.font.split(" ")[1]]);
    },
  };
  const settings = { aVisible: true, sVisible: true, eVisible: true, stopAllVisible: true,
    trueFalseVisible: false, foundationTfVisible: true, foundationTfTrueColor: "#048844",
    foundationTfSize: 14, secondaryTfVisible: false, primaryTfVisible: true, primaryTfFalseColor: "#994422" };
  const dependencies = {
    ctx,
    state: { tf: 30, indicator: { enabled: true, settings, results: { directions: { bullish: {
      reactions: [],
      sZones: [{ sourceIndex: 1, sourceTime: 30, price: 100, trueFalse: "T" }],
      eZones: [{ sourceIndex: 2, sourceTime: 60, price: 100, number: 1, trueFalse: null }],
      stopAlls: [{ sourceIndex: 3, sourceTime: 90, price: 100, number: 2, trueFalse: "T" }],
      primaryLows: [{ number: 3, sourceTime: 120, price: 100, trueFalse: "F" }],
    } } } } },
    indicatorTimeToCoordinate: time => time,
    priceToY: price => price,
    indicatorObject: () => null,
    offsetIndicatorPoint: (_object, x, y) => ({ x, y }),
    rgba: () => "#fff",
  };
  drawIndicator(200, 200, dependencies);
  assert.deepEqual(verdicts, [["T", 30, "#048844", "14px"], ["N/A", 60, "#808080", "14px"],
    ["F", 120, "#994422", "11px"]]);
  verdicts.length = 0;
  Object.assign(settings, { trueFalseVisible: true, foundationTfVisible: false,
    secondaryTfVisible: true, primaryTfVisible: false });
  drawIndicator(200, 200, dependencies);
  assert.deepEqual(verdicts, [["T", 90, "#047857", "9px"]]);
});


test("Foundation repeat stars extend beyond the verdict using the StopAll N/A color", () => {
  const text = [];
  const ctx = {
    save() {}, restore() {},
    fillText(label, x, y) { text.push({ label, x, y, font: this.font, color: this.fillStyle }); },
  };
  const settings = {
    sVisible: true, eVisible: true, sGap: 12, eGap: 12,
    foundationTfVisible: true, foundationTfSize: 11,
    foundationTfNaColor: "#778899", secondaryTfNaColor: "#909090", secondaryTfVisible: false,
  };
  const dependencies = {
    ctx,
    state: { tf: 30, indicator: { enabled: true, settings, results: { directions: {
      bullish: { reactions: [], sZones: [{ sourceIndex: 1, sourceTime: 30, price: 100, trueFalse: "T", trueFalseRepeated: true }] },
      bearish: { reactions: [], eZones: [
        { sourceIndex: 2, sourceTime: 60, price: 100, number: 2, trueFalse: "F", trueFalseRepeated: true },
        { sourceIndex: 3, sourceTime: 90, price: 100, number: 2, trueFalse: "F" },
      ] },
    } } } },
    indicatorTimeToCoordinate: time => time,
    priceToY: price => price,
    indicatorObject: () => null,
    offsetIndicatorPoint: (_object, x, y) => ({ x, y }),
    rgba: () => "#fff",
  };

  drawIndicator(200, 200, dependencies);

  const stars = text.filter(({ label }) => label === "*");
  assert.deepEqual(stars.map(({ x }) => x), [30, 60]);
  for (const star of stars) {
    const native = text.find(({ label, x }) => x === star.x && (label === "S" || label === "E2"));
    const verdict = text.find(({ label, x }) => x === star.x && (label === "T" || label === "F"));
    const sign = star.x === 30 ? 1 : -1;
    assert.ok(sign * (star.y - native.y) > 0 && sign * (star.y - verdict.y) > 0);
    assert.equal(star.font, verdict.font);
    assert.equal(star.color, "#909090");
  }

  text.length = 0;
  settings.foundationTfVisible = false;
  drawIndicator(200, 200, dependencies);
  assert.deepEqual(text.map(({ label }) => label), ["S", "E2", "E2"]);
});

test("indicator positions draw mirrored 4R and mark their type beyond the stop", () => {
  const rectangles = [], labels = [], clips = [], entryLines = [];
  const ctx = {
    save() {}, restore() {}, beginPath() {}, clip() {}, setLineDash() {},
    fillRect(...rect) { rectangles.push(rect); },
    strokeRect() {},
    rect(...rect) { clips.push(rect); },
    moveTo(...point) { entryLines.push(point); },
    lineTo(...point) { entryLines.push(point); },
    stroke() {},
    fillText(text, x, y) { labels.push({ text, x, y, baseline: this.textBaseline }); },
  };
  const coordinates = new Map([[100, 20], [900, 40], [1680, 280], [2340, 520], [2400, 540]]);
  const draw = (position) => ({ reactions: [], positions: [position] });
  const buy = draw({ id: "buy-1", type: "1.1B", side: "buy", entryTime: 100,
    entryPrice: "100.00", stopPrice: "97.50", targetPrice: "110" });
  buy.calculationEndTime = 1680;
  const sell = draw({ id: "sell-1", type: "3.3S", side: "sell", entryTime: 900,
    entryPrice: "101.25", stopPrice: "104.25", targetPrice: "89.25" });
  const state = {
    tf: 30,
    data: [100, 130, 900, 930].map(time => ({ time })),
    indicator: { enabled: true, settings: {}, results: { timeframe: 5, directions: {
      bullish: { calculationSegments: [buy] },
      bearish: sell,
    } } },
  };
  drawIndicator(600, 200, {
    ctx, state,
    indicatorTimeToCoordinate: (time) => coordinates.get(time) ?? null,
    overlayPriceCoordinate: (price) => 150 - price,
  });
  assert.deepEqual(rectangles, [
    [20, 40, 500, 10], [20, 50, 500, 2.5],
    [40, 48.75, 500, 12], [40, 45.75, 500, 3],
  ]);
  assert.deepEqual(entryLines, [[20, 50], [520, 50], [40, 48.75], [540, 48.75]]);
  assert.deepEqual(clips, [[0, 0, 280, 200]]);
  assert.deepEqual(labels.map(({ text, x, baseline }) => ({ text, x, baseline })), [
    { text: "1.1B", x: 270, baseline: "top" },
    { text: "3.3S", x: 290, baseline: "bottom" },
  ]);
  assert.ok(labels[0].y > 52.5);
  assert.ok(labels[1].y < 45.75);
  assert.deepEqual(state.indicator.hitBoxes.map(hit => ({
    id: hit.objectId, left: hit.left, right: hit.right, top: hit.top, bottom: hit.bottom,
  })), [
    { id: "indicator:bullish:position:buy-1", left: 20, right: 520, top: 40, bottom: 52.5 },
    { id: "indicator:bearish:position:sell-1", left: 40, right: 540, top: 45.75, bottom: 60.75 },
  ]);
});

test("position visibility, retained pre-entry stops and edited geometry drive paint and hit testing", () => {
  const labels = [];
  const ctx = {
    save() {}, restore() {}, beginPath() {}, clip() {}, rect() {}, setLineDash() {},
    fillRect() {}, strokeRect() {}, moveTo() {}, lineTo() {}, stroke() {},
    fillText(text, x, y) { labels.push({ text, x, y }); },
  };
  const buy = { id: "early", type: "2.2B", side: "buy", entryTime: 10, entryPrice: "100",
    stopPrice: "105", targetPrice: "120", preEntryStop: true };
  const normal = { ...buy, id: "hidden", type: "2.1B", stopPrice: "95" };
  const archived = { ...buy, id: "legacy", type: "Type-3B" };
  const edited = { ...buy, id: "edited" };
  const state = { tf: 1, data: [], indicator: { enabled: true, settings: { position2_1BVisible: false },
    results: { directions: { bullish: { reactions: [], positions: [buy, normal, archived, edited] } } } } };
  drawIndicator(300, 200, {
    ctx, state,
    indicatorTimeToCoordinate: time => time,
    overlayPriceCoordinate: price => 150 - price,
    indicatorObject: id => id.endsWith(":edited") ? {
      positionEdit: { time: 80, entry: 90, target: 112, stop: 83, bars: 15 },
    } : undefined,
  });
  assert.deepEqual(labels, [{ text: "2.2B", x: 35, y: 53 }, { text: "2.2B", x: 87.5, y: 70 }]);
  const [earlyHit, editedHit] = state.indicator.hitBoxes;
  assert.equal(state.indicator.hitBoxes.length, 2);
  assert.equal(earlyHit.bottom, 50);
  assert.equal(editedHit.right, 95);
  assert.deepEqual(editedHit.handles.filter(handle => handle.level === "stop"), [
    { x: 80, y: 67, level: "stop" }, { x: 95, y: 67, level: "stop" },
  ]);
  assert.equal(edited.entryPrice, "100");
});

test("Basic ordinal marks follow the verdict outward and use the Secondary N/A style", () => {
  const text = [];
  const ctx = {
    save() {}, restore() {},
    fillText(label, x, y) {
      text.push({ label, x, y, font: this.font, color: this.fillStyle, baseline: this.textBaseline });
    },
  };
  const dependencies = {
    ctx,
    state: { tf: 30, indicator: {
      enabled: true,
      settings: { sVisible: true, eVisible: true, sGap: 12, eGap: 12,
        foundationTfSize: 11, secondaryTfNaColor: "#909090" },
      results: { directions: {
        bullish: { reactions: [], sZones: [
          { sourceIndex: 1, sourceTime: 30, price: 100, trueFalse: "T",
            trueFalseRepeated: true, trueFalseRepeatCount: 2 },
        ] },
        bearish: { reactions: [], eZones: [
          { sourceIndex: 2, sourceTime: 60, price: 100, number: 2, trueFalse: "F",
            trueFalseRepeatCount: 3, trueFalseRepeatF: true },
          { sourceIndex: 3, sourceTime: 90, price: 100, number: 3, trueFalse: "F" },
        ] },
      } },
    } },
    indicatorTimeToCoordinate: time => time,
    priceToY: price => price,
    indicatorObject: () => null,
    offsetIndicatorPoint: (_object, x, y) => ({ x, y }),
  };
  drawIndicator(200, 200, dependencies);
  assert.deepEqual(text.map(({ label }) => label), ["S", "T", "**", "E2", "F", "***", "X", "E3", "F"]);
  assert.ok(text[2].y > text[1].y);
  assert.ok(text[6].y < text[5].y && text[5].y < text[4].y);
  for (const [mark, verdict] of [[text[2], text[1]], [text[5], text[4]], [text[6], text[4]]]) {
    assert.equal(mark.font, verdict.font);
    assert.equal(mark.color, "#909090");
    assert.equal(mark.baseline, verdict.baseline);
  }
});
