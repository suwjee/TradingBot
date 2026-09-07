import test from "node:test";
import assert from "node:assert/strict";
import { createHash, webcrypto } from "node:crypto";
import vm from "node:vm";
import { buildInfoPayload, buildReviewBody, formatInfoYaml, reviewRecords, reviewTime } from "../src/manual-review.js";
import { reviewFixture } from "./manual-review-fixture.mjs";

test("info body preserves the source payload and displays only the manual-review projection", async () => {
  const before = JSON.stringify(reviewFixture);
  const snapshot = { source: "test", drawings: [{ id: "line" }], settings: { timeframe: "follow" } };
  const page = await buildReviewBody(reviewFixture, snapshot, webcrypto);
  assert.equal(JSON.stringify(reviewFixture), before);
  assert.match(page.body, new RegExp(createHash("sha256").update(before).digest("hex")));
  assert.equal((page.body.match(/<article class="event"/g) || []).length, 18);
  assert.equal(reviewRecords(reviewFixture).length, 18);
  assert.match(page.body, /StopAll1/); assert.match(page.body, /E2 blue/);
  const firstTime = reviewTime(reviewFixture.directions.bullish.reactions[0].firstTime);
  assert.match(page.body, new RegExp(`<details class="day"><summary class="day-head"><h2>${firstTime.slice(0, 10)}</h2>`));
  assert.equal(page.body.includes(`<time datetime="${firstTime.replace(" ", "T")}">${firstTime.slice(11)}</time>`), true);
  assert.match(page.body, /<details class="bridge-output" data-bridge-id="bullish:reactions:0"><summary>Bridge output<\/summary><div class="bridge-placeholder"><\/div>/);
  assert.match(JSON.stringify(page.bridgeData), /12\.1234567890123456789/);
  assert.match(page.body, /Record collections/);
  assert.equal(page.bridgeData["bullish:reactions:0"].type, "Reaction");
  assert.doesNotMatch(page.body, /untouched: true/);
  assert.match(page.body, /Calculation timeframe/);
  assert.match(page.body, /Source file/);
  assert.doesNotMatch(page.body, /A chronological manual comparison workspace/);
  assert.equal(reviewTime(0), "1970-01-01 03:30:00");
  assert.doesNotThrow(() => new vm.Script(`(${page.runtime})();`));
  assert.doesNotMatch(page.body, /<script src=|@import|fetch\(/);
});

test("every known collection projects review evidence and removes indexes and internal extras", () => {
  const payload = {
    engine: "projection-contract-test", version: "reaction-v1", blueLineVersion: "blue-v1",
    aVersion: "a-v1", sVersion: "s-v1", eVersion: "e-v1", stopAllVersion: "stop-v1",
    timeframe: 30, actualFrom: 100, actualTo: 1000,
    directions: { bullish: {
      reactions: [{ firstIndex: 1, firstTime: 100, boxTopSourceIndex: 2, boxTopSourceTime: 110,
        boxTop: "12.50", boxBottomSourceIndex: 3, boxBottomSourceTime: 120,
        boxBottom: "10.25", breakIndex: 4, breakTime: 130, mode: "B", extra: "internal" }],
      resets: [{ index: 5, time: 140, secondTime: 141, brokenLevel: "10.25", fromFirstIndex: 1 }],
      blueLines: [{ direction: "bullish", kind: "scale", reactionNumber: 1,
        previousStrikeCount: 1, strikeCount: 2, fibonacciLevel: "11.75", sourceIndex: 6,
        sourceTime: 150, sourceExtreme: "12.70", linePrice: "12.10", startTime: 150, endTime: 200 }],
      aZones: [{ direction: "bullish", blue1Ordinal: 1, blue2Ordinal: 2,
        blue1SourceTime: 150, blue2SourceTime: 180, blue1StopTime: 190, blue2StopTime: 210,
        blue1StopLevel: "11.50", blue2StopLevel: "11.80", continuationLevel: "12.00",
        continuationSourceIndex: 7, continuationSourceTime: 170, triggerIndex: 8,
        triggerTime: 220, triggerEventTime: 221, reactionNumber: 3, reactionFirstTime: 200,
        reactionBreakTime: 215, sourceIndex: 9, sourceTime: 221, price: "12.20" }],
      sZones: [{ direction: "bullish", color: "red", formationType: "type3", aOrdinal: 1,
        aSourceIndex: 9, aSourceTime: 221, aPrice: "12.20", aStopIndex: 10, aStopTime: 230,
        aStopEventTime: 231, resetReactionNumber: 4, resetTime: 235,
        orderDirection: "bullish", orderReactionNumber: 5, orderMode: "A",
        orderFirstIndex: 11, orderFirstTime: 240, orderBreakIndex: 12, orderBreakTime: 250,
        orderConfirmationTime: 251, orderBoxTop: "12.40", orderBoxTopSourceIndex: 11,
        orderBoxTopSourceTime: 240, orderBoxBottom: "11.90", orderBoxBottomSourceIndex: 12,
        orderBoxBottomSourceTime: 245, orderStopLevel: "11.80", orderStopSourceIndex: 13,
        orderStopSourceTime: 246, sourceIndex: 14, sourceTime: 260, price: "12.30",
        decisionIndex: 15, decisionTime: 259, decisionEventTime: 260 }],
      eZones: [{ direction: "bullish", family: "blue", number: 2, parentType: "S1",
        parentSourceIndex: 14, parentSourceTime: 260, parentPrice: "12.30", parentStopIndex: 16,
        parentStopTime: 270, parentStopEventTime: 271, orderDirection: "bullish",
        orderReactionNumber: 5, orderMode: "B", orderCauses: ["parent-stop", "reset-leg"],
        orderParentStopCauseTime: 271, orderResetLegResetTime: 235, orderResetLegBreakTime: 250,
        orderFirstIndex: 11, orderFirstTime: 240, orderBreakIndex: 12, orderBreakTime: 250,
        orderConfirmationTime: 251, orderBoxTop: "12.40", orderBoxTopSourceIndex: 11,
        orderBoxTopSourceTime: 240, orderBoxBottom: "11.90", orderBoxBottomSourceIndex: 12,
        orderBoxBottomSourceTime: 245, orderStopLevel: "11.80", orderStopSourceIndex: 13,
        orderStopSourceTime: 246, sourceIndex: 17, sourceTime: 280, price: "12.60",
        decisionIndex: 18, decisionTime: 279, decisionEventTime: 280 }],
      stopAlls: [{ direction: "bullish", number: 1, sourceIndex: 19, sourceTime: 300,
        price: "12.80", decisionIndex: 20, decisionTime: 299, decisionEventTime: 300,
        gateType: "sequence-group-stop", gateEventTime: 295, stoppedBehaviorType: "E",
        stoppedBehaviorKey: "E2 blue", stoppedBehaviorCount: 2, underlyingEFamily: "blue",
        underlyingENumber: 2, orderDirection: "bullish", orderReactionNumber: 5,
        orderMode: "B", orderCauses: ["parent-stop"], orderParentStopCauseTime: 271,
        orderFirstIndex: 11, orderFirstTime: 240, orderBreakIndex: 12, orderBreakTime: 250,
        orderConfirmationTime: 251, orderBoxTop: "12.40", orderBoxTopSourceIndex: 11,
        orderBoxTopSourceTime: 240, orderBoxBottom: "11.90", orderBoxBottomSourceIndex: 12,
        orderBoxBottomSourceTime: 245, orderStopLevel: "11.80", orderStopSourceIndex: 13,
        orderStopSourceTime: 246, stopIndex: 21, stopTime: 320, stopEventTime: 321 }],
      orderAudit: [{ direction: "bullish", reactionNumber: 5, reactionMode: "B",
        firstIndex: 11, firstTime: 240, breakIndex: 12, breakTime: 250, stopLevel: "11.80",
        stopSourceIndex: 13, stopSourceTime: 246, stopHitIndex: 21, stopHitTime: 320,
        stopHitEventTime: 321, causes: [{ kind: "parent-stop", parentType: "S1",
          parentFamily: "blue", eventTime: 271, parentSourceTime: 260 }] }],
    } },
    timings: { bridgeTotalMs: 1.2 }, internalCacheKey: "must-not-leak",
  };
  const before = structuredClone(payload);
  const info = buildInfoPayload(payload);
  assert.deepEqual(payload, before);
  assert.deepEqual(Object.keys(info.directions.bullish), [
    "reactions", "resets", "blueLines", "aStructures", "sStructures",
    "eStructures", "stopAllEvents", "orderAudit",
  ]);
  assert.equal(info.directions.bullish.reactions[0].structure.boxTop.price, "12.50");
  assert.equal(info.directions.bullish.reactions[0].mode, "Normal");
  assert.equal(info.directions.bullish.resets[0].reactionStartedAt.time, "1970-01-01 03:31:40");
  assert.equal(info.directions.bullish.blueLines[0].line.price, "12.10");
  assert.equal(info.directions.bullish.blueLines[0].stop.time, "1970-01-01 03:33:20");
  assert.equal(info.directions.bullish.blueLines[0].stop.price, "12.70");
  assert.equal(info.directions.bullish.aStructures[0].blueLines.second.formedAt.time, "1970-01-01 03:33:00");
  assert.equal(info.directions.bullish.aStructures[0].stop.time, "1970-01-01 03:33:51");
  assert.equal(info.directions.bullish.sStructures[0].reset.time, "1970-01-01 03:33:55");
  assert.equal(info.directions.bullish.sStructures[0].order.mode, "Leg start");
  assert.equal(info.directions.bullish.sStructures[0].stop.time, "1970-01-01 03:34:31");
  assert.deepEqual(info.directions.bullish.eStructures[0].order.causes, ["Parent stop", "Reset leg"]);
  assert.equal(info.directions.bullish.eStructures[0].stop.time, "1970-01-01 03:34:55");
  assert.equal(info.directions.bullish.stopAllEvents[0].stop.time, "1970-01-01 03:35:21");
  assert.equal(info.directions.bullish.orderAudit[0].causes[0].parentFormedAt.time, "1970-01-01 03:34:20");
  const allKeys = [];
  const visit = (value) => {
    if (!value || typeof value !== "object") return;
    for (const [key, item] of Object.entries(value)) { allKeys.push(key); visit(item); }
  };
  visit(info);
  assert.equal(allKeys.some((key) => /index$/i.test(key)), false);
  assert.equal(allKeys.some((key) => /number$/i.test(key)), false);
  assert.equal(allKeys.includes("epoch"), false);
  assert.equal(allKeys.includes("Tehran"), false);
  assert.equal(allKeys.includes("timings"), false);
  assert.equal(allKeys.includes("internalCacheKey"), false);
  assert.equal(allKeys.includes("extra"), false);
  const yaml = formatInfoYaml(info.directions.bullish.reactions[0]);
  assert.match(yaml, /\n\nstructure:\n {4}boxTop:\n {8}time: "1970-01-01 03:31:50"\n {8}price: "12\.50"/);
  assert.equal(yaml.split("\n").filter((line) => line.trimStart() !== line).every((line) => line.search(/\S/) % 4 === 0), true);
});

test("hostile strings cannot break out of markup or record attributes", async () => {
  const payload = structuredClone(reviewFixture);
  const attack = '</script><script>alert("bad")</script><img src=x onerror=alert(1)>';
  payload.directions.bullish.eZones[0].family = attack;
  payload.extra = { attack, nullValue: null, escaped: "\u2028\u2029" };
  const page = await buildReviewBody(payload, { attack }, webcrypto);
  assert.doesNotMatch(page.body, /<img/);
  assert.doesNotMatch(page.body, /<script\b/);
  assert.match(page.body, /&lt;img src=x onerror=alert\(1\)&gt;/);
});

test("empty/unknown collections stay exportable without invented events", async () => {
  const payload = { timeframe: 60, directions: { bullish: { eZones: [], futureBehavior: [{ extra: true }] } } };
  const page = await buildReviewBody(payload, {}, webcrypto);
  assert.match(page.body, /Undated/); assert.match(page.body, /futureBehavior/);
  const empty = await buildReviewBody({ directions: {} }, {}, webcrypto);
  assert.match(empty.body, /No events in the cached payload/);
});

test("the built page contains no candle arrays and shares the runtime the page invokes", async () => {
  const page = await buildReviewBody(reviewFixture, { currentChart: { source: {}, timeframe: 60 } }, webcrypto);
  assert.doesNotMatch(page.body, /sourceCandles|calculationRangeCandles/);
  assert.equal(typeof page.styles, "string"); assert.match(page.styles, /\.event\{/);
  assert.match(page.body, /ASIA\/TEHRAN/);
  assert.equal(page.reviewId, "standalone");
});
