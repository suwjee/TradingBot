import test from "node:test";
import assert from "node:assert/strict";
import { createHash, webcrypto } from "node:crypto";
import vm from "node:vm";
import { buildReviewBody, reviewRecords, reviewTime } from "../src/manual-review.js";
import { reviewFixture } from "./manual-review-fixture.mjs";

test("review body embeds the complete unchanged payload, exact decimals, all collections and both directions", async () => {
  const before = JSON.stringify(reviewFixture);
  const snapshot = { source: "test", drawings: [{ id: "line" }], settings: { timeframe: "follow" } };
  const page = await buildReviewBody(reviewFixture, snapshot, webcrypto);
  assert.equal(JSON.stringify(reviewFixture), before);
  assert.match(page.body, new RegExp(createHash("sha256").update(before).digest("hex")));
  assert.equal((page.body.match(/<article class="event"/g) || []).length, 18);
  assert.equal(reviewRecords(reviewFixture).length, 18);
  assert.match(page.body, /StopAll1/); assert.match(page.body, /E2 blue/);
  const firstTime = reviewTime(reviewFixture.directions.bullish.reactions[0].firstTime);
  assert.match(page.body, new RegExp(`<details class="day" open><summary class="day-head"><h2>${firstTime.slice(0, 10)}</h2>`));
  assert.equal(page.body.includes(`<time datetime="${firstTime.replace(" ", "T")}">${firstTime.slice(11)}</time>`), true);
  assert.match(page.body, /<details class="bridge-output"><summary>Bridge output<\/summary><pre>/);
  assert.match(page.body, /12\.1234567890123456789/);
  assert.equal(reviewTime(0), "1970-01-01 03:30:00");
  assert.doesNotThrow(() => new vm.Script(`(${page.runtime})();`));
  assert.doesNotMatch(page.body, /<script src=|@import|fetch\(/);
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
