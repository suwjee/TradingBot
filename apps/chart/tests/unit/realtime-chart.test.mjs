import assert from "node:assert/strict";
import test from "node:test";
import { createRealtimeChartScheduler } from "../../src/features/realtime-chart.js";

function createScheduler(t, options = {}) {
  t.mock.timers.enable({ apis: ["Date", "setTimeout"], now: 0 });
  const requests = [];
  let view;
  const scheduler = createRealtimeChartScheduler({
    now: options.now ?? Date.now,
    indicatorProblem: options.indicatorProblem ?? (() => ""),
    async runUpdate(request) {
      requests.push(request);
      return options.runUpdate ? options.runUpdate(request) : "Checked for new candles.";
    },
    render: (state) => { view = state; },
  });
  t.after(scheduler.stop);
  scheduler.contextChanged("raw-chart-a");
  return { scheduler, requests, get view() { return view; } };
}

const settle = () => new Promise((resolve) => setImmediate(resolve));

test("enabling runs an immediate check and then observes the selected interval", async (t) => {
  const fixture = createScheduler(t);
  fixture.scheduler.enable();
  assert.equal(fixture.requests.length, 1);
  assert.equal(fixture.requests[0].chartId, "raw-chart-a");
  assert.equal(fixture.requests[0].indicatorCalculation, false);
  await settle();
  assert.equal(fixture.view.status, "Checked for new candles.");

  fixture.scheduler.setInterval(30_000);
  assert.equal(fixture.view.remainingMs, 30_000);
  t.mock.timers.tick(29_999);
  assert.equal(fixture.requests.length, 1);
  t.mock.timers.tick(1);
  assert.equal(fixture.requests.length, 2);
});

test("switching RAW aborts the old check and serializes a new live session", async (t) => {
  const releases = [];
  const fixture = createScheduler(t, {
    runUpdate: () => new Promise((resolve) => releases.push(resolve)),
  });
  fixture.scheduler.enable();
  t.mock.timers.tick(90_000);
  assert.equal(fixture.requests.length, 1);

  fixture.scheduler.contextChanged("raw-chart-b");
  assert.equal(fixture.requests[0].signal.aborted, true);
  assert.equal(fixture.view.enabled, false);
  fixture.scheduler.enable();
  assert.equal(fixture.requests.length, 1);

  releases[0]("Old chart updated.");
  await settle();
  assert.equal(fixture.requests.length, 2);
  assert.equal(fixture.requests[1].chartId, "raw-chart-b");
  assert.notEqual(fixture.view.status, "Old chart updated.");
  releases[1]("Current chart updated.");
  await settle();
  assert.equal(fixture.view.status, "Current chart updated.");
});

test("a long check skips missed intervals and resumes at the next scheduled start", async (t) => {
  let finishFirst;
  const fixture = createScheduler(t, {
    runUpdate: () => new Promise((resolve) => { finishFirst = resolve; }),
  });
  fixture.scheduler.setInterval(30_000);
  fixture.scheduler.enable();
  t.mock.timers.tick(75_000);
  assert.equal(fixture.requests.length, 1);
  finishFirst("Checked for new candles.");
  await settle();
  assert.equal(fixture.view.remainingMs, 15_000);
  t.mock.timers.tick(14_999);
  assert.equal(fixture.requests.length, 1);
  t.mock.timers.tick(1);
  assert.equal(fixture.requests.length, 2);
});

test("waking after browser timer throttling performs only one overdue check", async (t) => {
  let elapsedWhileThrottled = 0;
  const fixture = createScheduler(t, { now: () => Date.now() + elapsedWhileThrottled });
  fixture.scheduler.enable();
  await settle();
  elapsedWhileThrottled = 180_000;
  fixture.scheduler.wake();
  assert.equal(fixture.requests.length, 2);
  await settle();

  t.mock.timers.tick(59_999);
  assert.equal(fixture.requests.length, 2);
  t.mock.timers.tick(1);
  assert.equal(fixture.requests.length, 3);
});

test("an ineligible indicator option reports manual Apply and continues candle polling", async (t) => {
  const problem = "Apply the indicator manually before enabling live calculation.";
  const fixture = createScheduler(t, { indicatorProblem: () => problem });
  fixture.scheduler.enable();
  await settle();

  fixture.scheduler.setIndicatorCalculation(true);
  assert.equal(fixture.view.indicatorCalculation, false);
  assert.equal(fixture.view.indicatorError, problem);
  assert.equal(fixture.view.enabled, true);
  t.mock.timers.tick(60_000);
  assert.equal(fixture.requests.length, 2);
  assert.equal(fixture.requests[1].indicatorCalculation, false);
});

test("enabling indicator continuation checks immediately and revalidates before later polls", async (t) => {
  let problem = "";
  const fixture = createScheduler(t, { indicatorProblem: () => problem });
  fixture.scheduler.enable();
  await settle();
  fixture.scheduler.setIndicatorCalculation(true);
  assert.equal(fixture.requests.length, 2);
  assert.equal(fixture.requests[1].indicatorCalculation, true);
  await settle();

  problem = "Apply the indicator manually for the current range.";
  t.mock.timers.tick(60_000);
  assert.equal(fixture.requests[2].indicatorCalculation, false);
  assert.equal(fixture.view.indicatorError, problem);
});

test("turning indicator calculation off cancels only the indicator request", async (t) => {
  let finishIndicator;
  const fixture = createScheduler(t, {
    runUpdate: ({ indicatorCalculation }) => indicatorCalculation
      ? new Promise((resolve) => { finishIndicator = resolve; })
      : "Candles updated.",
  });
  fixture.scheduler.enable();
  await settle();
  fixture.scheduler.setIndicatorCalculation(true);
  assert.equal(fixture.requests[1].indicatorCalculation, true);

  fixture.scheduler.setIndicatorCalculation(false);
  assert.equal(fixture.requests[1].indicatorSignal.aborted, true);
  assert.equal(fixture.requests[1].signal.aborted, false);
  finishIndicator("Indicators updated.");
  await settle();
  assert.notEqual(fixture.view.status, "Indicators updated.");
  t.mock.timers.tick(60_000);
  assert.equal(fixture.requests[2].indicatorCalculation, false);
});

test("a newly requested indicator check waits for the active RAW check", async (t) => {
  let finishRaw;
  const fixture = createScheduler(t, {
    runUpdate: ({ indicatorCalculation }) => indicatorCalculation
      ? "Indicator updated."
      : new Promise(resolve => { finishRaw = resolve; }),
  });
  fixture.scheduler.enable();
  fixture.scheduler.setIndicatorCalculation(true);
  assert.equal(fixture.requests.length, 1);
  assert.equal(fixture.requests[0].signal.aborted, false);
  finishRaw("Candles updated.");
  await settle();
  assert.equal(fixture.requests.length, 2);
  assert.equal(fixture.requests[1].indicatorCalculation, true);
  assert.equal(fixture.view.status, "Indicator updated.");
});

test("a lost checkpoint turns off indicator continuation immediately", async (t) => {
  let problem = "";
  const fixture = createScheduler(t, {
    indicatorProblem: () => problem,
    runUpdate({ indicatorCalculation }) {
      if (!indicatorCalculation) return "Candles updated.";
      problem = "Apply again to start a new live calculation.";
      throw new Error(problem);
    },
  });
  fixture.scheduler.enable();
  await settle();
  fixture.scheduler.setIndicatorCalculation(true);
  await settle();
  assert.equal(fixture.view.indicatorCalculation, false);
  assert.equal(fixture.view.indicatorError, problem);
  assert.equal(fixture.view.enabled, true);
});

test("a polling failure is displayed and subsequent checks continue until disabled", async (t) => {
  let attempts = 0;
  const fixture = createScheduler(t, {
    runUpdate() {
      if (++attempts === 1) throw new Error("FARAZ session expired.");
      return "Checked for new candles.";
    },
  });
  fixture.scheduler.enable();
  await settle();
  assert.equal(fixture.view.status, "FARAZ session expired.");
  assert.equal(fixture.view.failed, true);
  t.mock.timers.tick(60_000);
  await settle();
  assert.equal(fixture.view.status, "Checked for new candles.");
  assert.equal(fixture.view.failed, false);

  fixture.scheduler.stop();
  t.mock.timers.tick(120_000);
  assert.equal(fixture.requests.length, 2);
  assert.equal(fixture.view.enabled, false);
});
