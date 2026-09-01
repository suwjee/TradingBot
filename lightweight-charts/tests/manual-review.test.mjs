import test from "node:test";
import assert from "node:assert/strict";
import { createHash, webcrypto } from "node:crypto";
import vm from "node:vm";
import { renderManualReview, reviewRecords, saveManualReview, reviewTime } from "../src/manual-review.js";
import { reviewFixture } from "./manual-review-fixture.mjs";
const embedded = (html, id) => JSON.parse(html.match(new RegExp(`<script type="application/json" id="${id}">([\\s\\S]*?)</script>`))[1]);

test("export embeds the complete unchanged payload, exact decimals, all collections and both directions", async () => {
  const before = JSON.stringify(reviewFixture);
  const snapshot = { source: "test", drawings: [{ id: "line" }], settings: { timeframe: "follow" } };
  const html = await renderManualReview(reviewFixture, snapshot, webcrypto);
  assert.deepEqual(embedded(html, "indicator-payload"), reviewFixture);
  assert.deepEqual(embedded(html, "chart-snapshot"), snapshot);
  assert.equal(JSON.stringify(reviewFixture), before);
  assert.match(html, new RegExp(createHash("sha256").update(before).digest("hex")));
  assert.equal((html.match(/<article class="event"/g) || []).length, 18);
  assert.equal(reviewRecords(reviewFixture).length, 18);
  assert.match(html, /StopAll1/); assert.match(html, /E2 blue/);
  const firstTime = reviewTime(reviewFixture.directions.bullish.reactions[0].firstTime);
  assert.match(html, new RegExp(`<details class="day" open><summary class="day-head"><h2>${firstTime.slice(0, 10)}</h2>`));
  assert.equal(html.includes(`<time datetime="${firstTime.replace(" ", "T")}">${firstTime.slice(11)}</time>`), true);
  assert.match(html, /<details class="bridge-output"><summary>Bridge output<\/summary><pre>/);
  assert.match(html, /12\.1234567890123456789/);
  assert.equal(reviewTime(0), "1970-01-01 03:30:00");
  const script = html.match(/<script>\(([\s\S]*)\)\(\);<\/script>/)[1];
  assert.doesNotThrow(() => new vm.Script(`(${script})();`));
  assert.doesNotMatch(html, /<script src=|@import|fetch\(/);
});

test("hostile strings cannot break out of embedded JSON, markup, or record attributes", async () => {
  const payload = structuredClone(reviewFixture);
  const attack = '</script><script>alert("bad")</script><img src=x onerror=alert(1)>';
  payload.directions.bullish.eZones[0].family = attack;
  payload.extra = { attack, nullValue: null, escaped: "\u2028\u2029" };
  const html = await renderManualReview(payload, { attack }, webcrypto);
  assert.deepEqual(embedded(html, "indicator-payload"), payload);
  assert.equal(embedded(html, "chart-snapshot").attack, attack);
  assert.equal((html.match(/<script\b/g) || []).length, 3);
  assert.doesNotMatch(html, /<img/);
});

test("empty/unknown collections stay exportable without invented events", async () => {
  const payload = { timeframe: 60, directions: { bullish: { eZones: [], futureBehavior: [{ extra: true }] } } };
  const html = await renderManualReview(payload, {}, webcrypto);
  assert.deepEqual(embedded(html, "indicator-payload"), payload);
  assert.match(html, /Undated/); assert.match(html, /futureBehavior/);
  const empty = await renderManualReview({ directions: {} }, {}, webcrypto);
  assert.match(empty, /No events in the cached payload/);
});

test("Save As captures before waiting and writes the exact cached payload without requests", async () => {
  const payload = structuredClone(reviewFixture); let resolvePicker, capturedBlob, closed = false, options;
  const snapshot = { currentChart: {
    timeframe: 60,
    sourceCandles: [{ time: 1780000000, open: 12.3, high: 12.4, low: 12.1, close: 12.2 }],
    candles: [{ time: 1779999960, open: 12.3, high: 12.4, low: 12.1, close: 12.2 }],
  } };
  const originalSnapshot = structuredClone(snapshot);
  const host = { crypto: webcrypto, showSaveFilePicker: (opts) => { options = opts; return new Promise((resolve) => { resolvePicker = resolve; }); } };
  const pending = saveManualReview(payload, snapshot, host);
  payload.directions.bullish.eZones = [];
  snapshot.currentChart.sourceCandles[0].close = 99;
  snapshot.currentChart.candles = [];
  snapshot.currentChart.timeframe = 300;
  resolvePicker({ createWritable: async () => ({ write: async (blob) => { capturedBlob = blob; }, close: async () => { closed = true; } }) });
  assert.equal(await pending, "saved"); assert.equal(closed, true);
  assert.match(options.suggestedName, /^manualTest-\d{4}_\d{2}_\d{2} \d{2}_\d{2}_\d{2}\.html$/);
  assert.deepEqual(embedded(await capturedBlob.text(), "indicator-payload"), reviewFixture);
  const exportedSnapshot = embedded(await capturedBlob.text(), "chart-snapshot");
  assert.equal(Number.isFinite(Date.parse(exportedSnapshot.exportedAt)), true);
  delete exportedSnapshot.exportedAt;
  assert.deepEqual(exportedSnapshot, originalSnapshot);
});

test("picker cancellation is quiet and creates neither HTML nor a download", async () => {
  const host = { showSaveFilePicker: async () => { throw Object.assign(new Error("cancel"), { name: "AbortError" }); } };
  assert.equal(await saveManualReview(reviewFixture, {}, host, () => assert.fail("cancel notification")), "cancelled");
});

test("unsupported/blocked picker explains fallback and downloads only HTML", async () => {
  for (const blocked of [false, true]) {
    let blob, clicked = false, notice;
    const anchor = { click() { clicked = true; }, remove() {} };
    const host = { crypto: webcrypto, document: { createElement: () => anchor, body: { append() {} } },
      URL: { createObjectURL(value) { blob = value; return "blob:test"; }, revokeObjectURL() {} }, setTimeout(fn) { fn(); } };
    if (blocked) host.showSaveFilePicker = async () => { throw Object.assign(new Error("blocked"), { name: "SecurityError" }); };
    assert.equal(await saveManualReview(reviewFixture, {}, host, (message) => { notice = message; }), "downloaded");
    assert.match(notice, /Save As is unavailable.*choose a path/);
    assert.equal(clicked, true); assert.match(anchor.download, /^manualTest-\d{4}_\d{2}_\d{2} \d{2}_\d{2}_\d{2}\.html$/);
    assert.deepEqual(embedded(await blob.text(), "indicator-payload"), reviewFixture);
  }
});

test("write failure aborts the transaction, reports failure and never silently downloads", async () => {
  let aborted = false;
  const host = { crypto: webcrypto, showSaveFilePicker: async () => ({ createWritable: async () => ({
    write: async () => { throw new Error("disk full"); }, abort: async () => { aborted = true; },
  }) }) };
  await assert.rejects(saveManualReview(reviewFixture, {}, host), /disk full/);
  assert.equal(aborted, true);
});
