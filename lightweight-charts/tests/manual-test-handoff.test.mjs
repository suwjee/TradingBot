import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { openManualReviewTab, startManualReviewHandoff } from "../src/manual-test.js";

const entrySource = readFileSync(new URL("../src/manual-test-entry.js", import.meta.url), "utf8");

function hostDouble() {
  const timers = [], posted = [], listeners = [];
  const channel = { closed: false, postMessage(message) { if (!this.closed) posted.push(message); }, close() { this.closed = true; }, set onmessage(handler) { listeners.push(handler); } };
  const host = { open: (...args) => ({ args }), BroadcastChannel: function () { return channel; }, setTimeout: (fn, delay) => { timers.push({ fn, delay }); return timers.length; }, clearTimeout: (id) => { timers.splice(id - 1, 1); } };
  return { host, timers, posted, listeners, channel };
}

test("openManualReviewTab keeps the popup reference so a real blocker is detectable", () => {
  const opened = [], host = { open: (...args) => { opened.push(args); return {}; } };
  openManualReviewTab(host);
  assert.deepEqual(opened, [["/manual-test", "_blank"]]);
});

test("handoff posts the exact payload after the page announces ready", () => {
  const { host, posted, listeners } = hostDouble();
  const payload = { directions: { bullish: { stopAlls: [{ sourceTime: 1 }] } }, timeframe: 30 }, snapshot = { exportedAt: "now" };
  startManualReviewHandoff(payload, snapshot, host);
  listeners.at(-1)({ data: { type: "review-ready" } });
  assert.deepEqual(posted, [{ type: "review-payload", payload, snapshot }]);
});

test("a missing page times out with a notice and no delivery", () => {
  const { host, timers, posted, channel } = hostDouble(), notices = [];
  startManualReviewHandoff({ directions: {} }, {}, host, (message) => notices.push(message));
  timers[0].fn();
  assert.match(notices.at(-1), /did not respond/); assert.equal(posted.length, 0); assert.equal(channel.closed, true);
});

test("the page entry uses the same channel and never fetches", () => {
  assert.match(entrySource, /new BroadcastChannel\("qg-manual-test"\)/);
  assert.match(entrySource, /"review-ready"/); assert.match(entrySource, /"review-payload"/);
  assert.doesNotMatch(entrySource, /fetch\(/); assert.match(entrySource, /buildReviewBody/);
  assert.match(entrySource, /window\.opener = null/);
});
