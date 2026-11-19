import assert from "node:assert/strict";
import test from "node:test";
import { startLiveIndicatorProgress } from "../../src/features/indicator-live-progress.js";

test("live progress follows Engine stages and reaches 100 only after applying the result", () => {
  const events = [];
  let closed = 0;
  const source = { close() { closed++; } };
  const progress = startLiveIndicatorProgress({ operationId: "calculation-one", signal: new AbortController().signal,
    report: event => events.push(event), connect: url => {
      assert.match(url, /requestId=calculation-one$/);
      return source;
    } });
  const send = event => source.onmessage({ data: JSON.stringify(event) });
  send({ status: "started", label: "Continue Reaction geometry" });
  send({ status: "completed", label: "Reaction geometry and ownership ready", completedStages: 2, totalStages: 6 });
  send({ status: "started", label: "E • Bullish • initial" });
  send({ status: "completed", label: "Repeated feedback pass" });
  send({ status: "finished", label: "Response ready" });
  assert.deepEqual(events.map(({ outcome, percent, stage }) => [outcome, percent, stage]), [
    ["started", 0, "Preparing calculation"], ["running", 0, "Continue Reaction geometry"],
    ["running", 33, "Reaction geometry and ownership ready"], ["running", 33, "E • Bullish • initial"],
    ["running", 33, "Validating result"],
  ]);
  progress.finish("applied");
  assert.equal(events.at(-1).outcome, "applied");
  assert.equal(events.at(-1).percent, 100);
  assert.equal(closed, 1);
});

test("abort closes the progress connection and ignores replayed events", () => {
  const controller = new AbortController();
  const events = [];
  let closed = 0;
  const source = { close() { closed++; } };
  const progress = startLiveIndicatorProgress({ operationId: "calculation-two", signal: controller.signal,
    report: event => events.push(event), connect: () => source });
  const receive = source.onmessage;
  controller.abort();
  receive({ data: '{"status":"finished","label":"Response ready"}' });
  progress.finish("applied");
  assert.equal(closed, 1);
  assert.deepEqual(events.map(event => event.outcome), ["started", "idle"]);
});
