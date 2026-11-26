import test from "node:test";
import assert from "node:assert/strict";
import { drawIndicator } from "../../src/chart/indicator-renderer.js";

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
  const ctx = {
    save() {},
    restore() {},
    beginPath() {},
    fill() {},
    stroke() {},
    arc(_x, _y, radius) { radii.push(radius); },
    fillText(label) { fontSizes[label] = Number(/ (\d+)px/.exec(this.font)[1]); },
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
          stopAlls: [{ sourceIndex: 4, sourceTime: 120, price: 100, number: 2 }],
        } } },
      },
    },
    indicatorTimeToCoordinate: (time) => time,
    priceToY: (price) => price,
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
  assert.deepEqual(verdicts, [["T", 30, "#048844", "14px"], ["N/A", 60, "#b8b8b8", "14px"],
    ["F", 120, "#994422", "11px"]]);
  verdicts.length = 0;
  Object.assign(settings, { trueFalseVisible: true, foundationTfVisible: false,
    secondaryTfVisible: true, primaryTfVisible: false });
  drawIndicator(200, 200, dependencies);
  assert.deepEqual(verdicts, [["T", 90, "#047857", "9px"]]);
});


test("Foundation repeats show a star above both native marker sides with the StopAll N/A color", () => {
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
    assert.ok(star.y < native.y && star.y < verdict.y);
    assert.equal(star.font, verdict.font);
    assert.equal(star.color, "#909090");
  }

  text.length = 0;
  settings.foundationTfVisible = false;
  drawIndicator(200, 200, dependencies);
  assert.deepEqual(text.map(({ label }) => label), ["S", "E2", "E2"]);
});
