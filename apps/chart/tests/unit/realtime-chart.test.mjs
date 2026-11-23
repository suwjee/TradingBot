import assert from "node:assert/strict";
import test from "node:test";
import { createRealtimeChartScheduler, readRealtimeUpdate } from "../../src/features/realtime-chart.js";

function createScheduler(t, options = {}) {
  t.mock.timers.enable({ apis: ["Date", "setTimeout"], now: options.start ?? 0 });
  const requests = [];
  let view;
  const scheduler = createRealtimeChartScheduler({
    now: options.now ?? Date.now,
    onVerificationComplete: options.onVerificationComplete,
    async runUpdate(request) {
      requests.push(request);
      return options.runUpdate ? options.runUpdate(request) : "Checked for new candles.";
    },
    render: (state) => { view = state; },
  });
  t.after(scheduler.stop);
  scheduler.contextChanged("raw-chart-a", options.sourceTimeframeSeconds);
  return { scheduler, requests, get view() { return view; } };
}

const settle = () => new Promise((resolve) => setImmediate(resolve));

test("progress is streamed before completion, and a final error retains its application status", async () => {
  let input;
  const response = new Response(new ReadableStream({ start(controller) { input = controller; } }), {
    headers: { "Content-Type": "application/x-ndjson; charset=utf-8" },
  });
  const encoder = new TextEncoder();
  const observed = [];
  const update = readRealtimeUpdate(response, progress => observed.push(progress));
  input.enqueue(encoder.encode('{"progress":0}\n{"pro'));
  input.enqueue(encoder.encode('gress":65}\n'));
  await settle();
  assert.deepEqual(observed, [0, 65]);
  input.enqueue(encoder.encode('{"status":409,"result":{"code":"RAW_CHANGED"}}\n'));
  assert.deepEqual(await update, { status: 409, result: { code: "RAW_CHANGED" } });
});

test("polling starts enabled, shows progress, and only Verify All sends a notification", async (t) => {
  const notices = [];
  let finish;
  const fixture = createScheduler(t, {
    onVerificationComplete: result => notices.push(result),
    runUpdate({ reportProgress }) {
      reportProgress(40);
      reportProgress(20);
      return new Promise(resolve => { finish = resolve; });
    },
  });
  assert.equal(fixture.view.enabled, true);
  t.mock.timers.tick(2_000);
  assert.equal(fixture.view.progress, 40);
  assert.equal(notices.length, 0);
  const verification = { status: "verified", checkedCount: 13, correctedCount: 2 };
  finish({ verification });
  await settle();
  assert.equal(fixture.view.progress, 100);
  assert.deepEqual(notices, []);
  fixture.scheduler.verifyAll();
  assert.equal(fixture.requests[1].verifyAll, true);
  finish({ verification });
  await settle();
  assert.deepEqual(notices, [verification]);
  fixture.scheduler.stop();
  assert.equal(fixture.view.progress, null);
});

test("Verify All works while polling is off and reports an unavailable connection without a poll failure", async (t) => {
  const fixture = createScheduler(t, { runUpdate: () => ({ status: "", verification: { status: "unavailable" } }) });
  fixture.scheduler.stop();
  fixture.scheduler.verifyAll();
  assert.equal(fixture.requests[0].verifyAll, true);
  assert.equal(fixture.view.verifyingAll, true);
  await settle();
  assert.equal(fixture.view.verifyingAll, false);
  assert.equal(fixture.view.verification.status, "unavailable");
  assert.equal(fixture.view.failed, false);
  assert.equal(fixture.view.status, "");
  assert.equal(fixture.view.remainingMs, null);
});

test("live calculation failures are tracked independently and clear after the next successful update", async (t) => {
  let indicatorCheck = 0;
  const fixture = createScheduler(t, {
    runUpdate({ indicatorOnly }) {
      if (!indicatorOnly) return { verification: { status: "unavailable" } };
      const indicatorError = ++indicatorCheck === 1 ? "Live Engine is unavailable." : "";
      return { indicatorUpdate: Promise.resolve({ indicatorError }) };
    },
  });
  t.mock.timers.tick(2_000);
  await settle();
  assert.match(fixture.view.realtimeError, /unavailable/i);
  fixture.scheduler.setIndicatorCalculation(true);
  await settle();
  assert.equal(fixture.view.liveCalculationError, "Live Engine is unavailable.");
  assert.equal(fixture.view.indicatorCalculation, true);
  fixture.scheduler.requestIndicatorUpdate();
  await settle();
  assert.equal(fixture.view.liveCalculationError, "");
  assert.match(fixture.view.realtimeError, /unavailable/i);
});

test("background Verify All runs every ten minutes independently of the candle interval", async (t) => {
  const notices = [];
  const fixture = createScheduler(t, { sourceTimeframeSeconds: 3_600, start: new Date(2026, 10, 20).getTime(),
    onVerificationComplete: result => notices.push(result),
    runUpdate: () => ({ verification: { status: "verified" } }) });
  t.mock.timers.tick(2_000);
  await settle();
  assert.equal(fixture.requests.length, 1);
  assert.equal(fixture.requests[0].verifyAll, undefined);
  t.mock.timers.tick(597_999);
  assert.equal(fixture.requests.length, 1);
  t.mock.timers.tick(1);
  assert.equal(fixture.requests[1]?.verifyAll, true);
  await settle();
  assert.deepEqual(notices, []);
  t.mock.timers.tick(600_000);
  assert.equal(fixture.requests[2]?.verifyAll, true);
  await settle();
  fixture.scheduler.stop();
  t.mock.timers.tick(600_000);
  assert.equal(fixture.requests.length, 3);
});

test("an overdue background Verify All waits for an active poll in the same chart", async (t) => {
  let finishPoll;
  const fixture = createScheduler(t, { runUpdate: ({ verifyAll }) => verifyAll ? "" :
    new Promise(resolve => { finishPoll = resolve; }) });
  t.mock.timers.tick(2_000);
  t.mock.timers.tick(600_000);
  assert.equal(fixture.requests.length, 1);
  finishPoll("");
  await settle();
  assert.equal(fixture.requests[1]?.verifyAll, true);
});

test("Verify All countdown, progress and coverage stay separate from a running candle poll", async (t) => {
  const finishes = [];
  const fixture = createScheduler(t, { runUpdate(request) {
    request.reportProgress(request.verifyAll ? 38 : 17);
    return new Promise(resolve => finishes.push(resolve));
  } });
  assert.equal(fixture.view.verifyAllRemainingMs, 600_000);
  assert.equal(fixture.view.verifyAllProgress, null);
  t.mock.timers.tick(2_000);
  assert.equal(fixture.view.progress, 17);
  t.mock.timers.tick(3_000);
  assert.equal(fixture.view.verifyAllRemainingMs, 595_000);
  t.mock.timers.tick(595_000);
  assert.equal(fixture.view.verifyAllState, "queued");
  assert.equal(fixture.view.verifyAllProgress, null);
  finishes.shift()({ verification: { status: "pending", verifiedCount: 8, totalCount: 10 } });
  await settle();
  assert.equal(fixture.view.verifyAllState, "running");
  assert.equal(fixture.view.verifyAllProgress, 38);
  assert.equal(fixture.view.progress, 100);
  assert.equal(fixture.view.verificationPercent, 80);
  finishes.shift()({ verification: { status: "pending", verifiedCount: 9, totalCount: 10 } });
  await settle();
  assert.equal(fixture.view.verifyAllState, "idle");
  assert.equal(fixture.view.verifyAllProgress, 100);
  assert.equal(fixture.view.verifyAllRemainingMs, 600_000);
  assert.equal(fixture.view.verificationPercent, 90);
});

test("Verify All with realtime disabled leaves automatic indicator calculation paused", async (t) => {
  const fixture = createScheduler(t);
  fixture.scheduler.setIndicatorCalculation(true);
  await settle();
  fixture.scheduler.stop();
  fixture.scheduler.verifyAll();
  const request = fixture.requests.at(-1);
  assert.equal(request.verifyAll, true);
  assert.equal(request.indicatorCalculation, false);
  assert.equal(request.indicatorSignal, undefined);
  await settle();
});

test("every interval polls at the local wall-clock boundary plus two seconds", async (t) => {
  const start = new Date(2026, 10, 13, 6, 12, 37).getTime();
  const minute = (hour, minute, second) => new Date(2026, 10, 13, hour, minute, second).getTime();
  const fixture = createScheduler(t, { start });
  for (const [interval, expected] of [
    [1_000, minute(6, 12, 38)], [5_000, minute(6, 12, 42)],
    [30_000, minute(6, 13, 2)], [60_000, minute(6, 13, 2)],
    [120_000, minute(6, 14, 2)], [180_000, minute(6, 15, 2)],
    [300_000, minute(6, 15, 2)], [600_000, minute(6, 20, 2)], [900_000, minute(6, 15, 2)],
  ]) {
    fixture.scheduler.setInterval(interval);
    fixture.scheduler.enable();
    assert.equal(fixture.requests.length, 0);
    assert.equal(fixture.view.remainingMs, expected - start);
    fixture.scheduler.stop();
  }
  fixture.scheduler.setInterval(60_000);
  fixture.scheduler.enable();
  t.mock.timers.tick(24_999);
  assert.equal(fixture.requests.length, 0);
  t.mock.timers.tick(1);
  assert.equal(Date.now(), minute(6, 13, 2));
  assert.equal(fixture.requests.length, 1);
  await settle();
  t.mock.timers.tick(60_000);
  assert.equal(Date.now(), minute(6, 14, 2));
  assert.equal(fixture.requests.length, 2);
});

test("a RAW chart starts at one minute when legal and rejects shorter-than-native polling", async (t) => {
  const fixture = createScheduler(t, { sourceTimeframeSeconds: 5 });
  assert.equal(fixture.view.intervalMs, 60_000);
  fixture.scheduler.setInterval(1_000);
  assert.equal(fixture.view.intervalMs, 60_000);
  fixture.scheduler.setInterval(5_000);
  assert.equal(fixture.view.intervalMs, 5_000);
  t.mock.timers.tick(2_000);
  assert.equal(fixture.requests[0].pollIntervalMs, 5_000);
  await settle();
});

test("polling offers the exact native interval when the source changes or exceeds all presets", async (t) => {
  const fixture = createScheduler(t, { sourceTimeframeSeconds: 17, start: new Date(2026, 10, 13).getTime() });
  assert.deepEqual(fixture.view.intervals.find(({ ms }) => ms === 17_000), {
    ms: 17_000, label: "17s", disabled: false,
  });
  assert.equal(fixture.view.intervals.find(({ ms }) => ms === 5_000).disabled, true);
  fixture.scheduler.setInterval(17_000);
  assert.equal(fixture.view.intervalMs, 17_000);

  fixture.scheduler.contextChanged("raw-chart-b", 3_600);
  assert.equal(fixture.view.intervalMs, 3_600_000);
  assert.equal(fixture.view.intervals.some(({ ms }) => ms === 17_000), false);
  assert.deepEqual(fixture.view.intervals.filter(({ disabled }) => !disabled), [
    { ms: 3_600_000, label: "1h", disabled: false },
  ]);
  fixture.scheduler.setInterval(900_000);
  assert.equal(fixture.view.intervalMs, 3_600_000);
  t.mock.timers.tick(2_000);
  assert.equal(fixture.requests[0].pollIntervalMs, 3_600_000);
  await settle();
});

test("coverage follows verified candles independently of completed request packets", async (t) => {
  let finish;
  const fixture = createScheduler(t, {
    runUpdate({ reportProgress, reportVerification }) {
      reportProgress(85);
      reportVerification?.({ status: "pending", verifiedCount: 0, totalCount: 2_000 });
      return new Promise(resolve => { finish = resolve; });
    },
  });
  assert.equal(fixture.view.verificationPercent, null);
  t.mock.timers.tick(2_000);
  assert.equal(fixture.view.verificationPercent, 0);
  assert.equal(fixture.view.progress, 85);
  finish({ verification: { status: "pending", verifiedCount: 1_999, totalCount: 2_000 } });
  await settle();
  assert.equal(fixture.view.verificationPercent, 99);
  assert.equal(fixture.view.progress, 100);
  assert.equal(fixture.view.remainingMs, 60_000);
  fixture.scheduler.verifyAll();
  finish({ verification: { status: "unavailable", verifiedCount: 2_000, totalCount: 2_000 } });
  await settle();
  assert.equal(fixture.view.verificationPercent, 100);
  assert.equal(fixture.view.progress, 100);
  assert.equal(fixture.view.verifyAllProgress, null);
  assert.equal(fixture.view.verifyAllState, "offline");
  fixture.scheduler.verifyAll();
  finish({ verification: { status: "verified", verifiedCount: 0, totalCount: 0 } });
  await settle();
  assert.equal(fixture.view.verificationPercent, null);
});

test("stored coverage appears on load and follows replay for the current chart", (t) => {
  const fixture = createScheduler(t);
  const { scheduler } = fixture;
  scheduler.contextChanged("saved", 5, { status: "pending", verifiedCount: 6, totalCount: 10 });
  assert.equal(fixture.view.verificationPercent, 60);
  scheduler.useStoredVerification("previous", { verifiedCount: 2, totalCount: 2 });
  assert.equal(fixture.view.verificationPercent, 60);
  scheduler.useStoredVerification("saved", { status: "pending", verifiedCount: 9, totalCount: 12 });
  assert.equal(fixture.view.verificationPercent, 75);
});

test("a slow one-second check keeps RAW acquisition single-flight", async (t) => {
  let finish;
  const fixture = createScheduler(t, { sourceTimeframeSeconds: 1,
    runUpdate: () => new Promise(resolve => { finish = resolve; }),
  });
  fixture.scheduler.setInterval(1_000);
  t.mock.timers.tick(1_000);
  t.mock.timers.tick(7_500);
  assert.equal(fixture.requests.length, 1);
  finish("Checked for new candles.");
  await settle();
  assert.equal(fixture.view.remainingMs, 500);
  t.mock.timers.tick(500);
  assert.equal(fixture.requests.length, 2);
});

test("switching RAW aborts the old check and serializes a new live session", async (t) => {
  const releases = [];
  const fixture = createScheduler(t, {
    runUpdate: () => new Promise((resolve) => releases.push(resolve)),
  });
  fixture.scheduler.enable();
  t.mock.timers.tick(2_000);
  t.mock.timers.tick(88_000);
  assert.equal(fixture.requests.length, 1);

  fixture.scheduler.contextChanged("raw-chart-b");
  assert.equal(fixture.requests[0].signal.aborted, true);
  assert.equal(fixture.view.enabled, true);
  assert.equal(fixture.requests.length, 1);

  releases[0]("Old chart updated.");
  await settle();
  assert.equal(fixture.requests.length, 1);
  t.mock.timers.tick(32_000);
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
  t.mock.timers.tick(2_000);
  t.mock.timers.tick(73_000);
  assert.equal(fixture.requests.length, 1);
  finishFirst("Checked for new candles.");
  await settle();
  assert.equal(fixture.view.remainingMs, 17_000);
  t.mock.timers.tick(16_999);
  assert.equal(fixture.requests.length, 1);
  t.mock.timers.tick(1);
  assert.equal(fixture.requests.length, 2);
});

test("waking after browser timer throttling runs one catch-up poll and preserves wall-clock alignment", async (t) => {
  let elapsedWhileThrottled = 0;
  const fixture = createScheduler(t, { now: () => Date.now() + elapsedWhileThrottled });
  fixture.scheduler.enable();
  t.mock.timers.tick(2_000);
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
  const fixture = createScheduler(t, { runUpdate: ({ indicatorCalculation }) => indicatorCalculation
    ? { status: "Candles updated.", indicatorError: problem } : "Candles updated." });
  fixture.scheduler.enable();
  t.mock.timers.tick(2_000);
  await settle();

  fixture.scheduler.setIndicatorCalculation(true);
  await settle();
  assert.equal(fixture.view.indicatorCalculation, false);
  assert.equal(fixture.view.indicatorError, problem);
  assert.equal(fixture.view.enabled, true);
  t.mock.timers.tick(60_000);
  assert.equal(fixture.requests.length, 3);
  assert.equal(fixture.requests[2].indicatorCalculation, false);
});

test("reenabling indicator calculation after five minutes checks immediately", async (t) => {
  const fixture = createScheduler(t);
  fixture.scheduler.enable();
  t.mock.timers.tick(2_000);
  await settle();
  fixture.scheduler.setIndicatorCalculation(true);
  assert.equal(fixture.requests.length, 2);
  assert.equal(fixture.requests[1].indicatorCalculation, true);
  await settle();

  fixture.scheduler.setIndicatorCalculation(false);
  for (let minute = 0; minute < 5; minute++) {
    t.mock.timers.tick(60_000);
    await settle();
    assert.equal(fixture.requests.at(-1).indicatorCalculation, false);
  }
  const count = fixture.requests.length;
  fixture.scheduler.setIndicatorCalculation(true);
  assert.equal(fixture.requests.length, count + 1);
  assert.equal(fixture.requests.at(-1).indicatorOnly, true);
  assert.equal(fixture.requests.at(-1).indicatorCalculation, true);
  await settle();
  assert.equal(fixture.view.indicatorError, "");
});

test("turning indicator calculation off cancels only the indicator request", async (t) => {
  let finishIndicator;
  const fixture = createScheduler(t, {
    runUpdate: ({ indicatorCalculation }) => indicatorCalculation
      ? new Promise((resolve) => { finishIndicator = resolve; })
      : "Candles updated.",
  });
  fixture.scheduler.enable();
  t.mock.timers.tick(2_000);
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
  t.mock.timers.tick(2_000);
  fixture.scheduler.setIndicatorCalculation(true);
  assert.equal(fixture.requests.length, 1);
  assert.equal(fixture.requests[0].signal.aborted, false);
  finishRaw("Candles updated.");
  await settle();
  assert.equal(fixture.requests.length, 2);
  assert.equal(fixture.requests[1].indicatorCalculation, true);
  assert.equal(fixture.view.status, "Indicator updated.");
});

test("a missing prior calculation turns off the indicator while the successful RAW result stays visible", async (t) => {
  const problem = "Run an indicator calculation with Apply before enabling automatic continuation.";
  const fixture = createScheduler(t, {
    runUpdate({ indicatorCalculation }) {
      if (!indicatorCalculation) return "Candles updated.";
      return { status: "Added 13 closed 5S candles.", indicatorError: problem };
    },
  });
  fixture.scheduler.enable();
  t.mock.timers.tick(2_000);
  await settle();
  fixture.scheduler.setIndicatorCalculation(true);
  await settle();
  assert.equal(fixture.view.indicatorCalculation, false);
  assert.equal(fixture.view.indicatorError, problem);
  assert.equal(fixture.view.enabled, true);
  assert.equal(fixture.view.status, "Added 13 closed 5S candles.");
  assert.equal(fixture.view.failed, false);
});

test("a temporary indicator error stays separate and the next poll retries", async (t) => {
  let indicatorChecks = 0;
  const fixture = createScheduler(t, { runUpdate({ indicatorCalculation }) {
    if (!indicatorCalculation) return "Candles updated.";
    if (++indicatorChecks === 1) return "Added 13 closed 5S candles. Indicator update deferred. Retrying.";
    return "Indicator updated.";
  } });
  fixture.scheduler.enable();
  t.mock.timers.tick(2_000);
  await settle();
  fixture.scheduler.setIndicatorCalculation(true);
  await settle();
  assert.match(fixture.view.status, /Added 13 closed 5S candles.*Retrying/);
  assert.equal(fixture.view.indicatorError, "");
  assert.equal(fixture.view.indicatorCalculation, true);
  t.mock.timers.tick(60_000);
  await settle();
  assert.equal(indicatorChecks, 2);
  assert.equal(fixture.view.indicatorError, "");
  assert.equal(fixture.view.status, "Indicator updated.");
});

test("candle countdown and verification proceed during deferred indicator completion", async (t) => {
  let completeIndicator;
  const indicatorUpdate = new Promise(resolve => { completeIndicator = resolve; });
  const verification = { status: "verified" };
  const fixture = createScheduler(t, {
    runUpdate: ({ indicatorOnly }) => indicatorOnly ? { indicatorUpdate } : { status: "Candles updated.", verification },
  });
  fixture.scheduler.setIndicatorCalculation(true);
  await settle();
  assert.match(fixture.view.status, /Updating indicator/);
  t.mock.timers.tick(2_000);
  await settle();
  assert.equal(fixture.view.verification, verification);
  assert.equal(fixture.view.remainingMs, 60_000);
  assert.equal(fixture.view.busy, false);
  fixture.scheduler.setIndicatorCalculation(false);
  assert.equal(fixture.requests[0].indicatorSignal.aborted, true);
  assert.equal(fixture.requests[0].signal.aborted, false);
  completeIndicator({ status: "The canceled indicator updated." });
  await settle();
  assert.doesNotMatch(fixture.view.status, /The canceled indicator updated/);
});

test("indicator progress follows the running operation through newer candle checks", async (t) => {
  const finishChecks = [];
  const fixture = createScheduler(t, {
    sourceTimeframeSeconds: 1,
    runUpdate: () => ({ indicatorUpdate: new Promise(resolve => { finishChecks.push(resolve); }) }),
  });
  fixture.scheduler.setInterval(1_000);
  fixture.scheduler.setIndicatorCalculation(true);
  const first = fixture.requests[0].reportIndicatorProgress;
  first?.({ operationId: "one", outcome: "started", percent: 0, stage: "Preparing" });
  first?.({ operationId: "one", percent: 47, stage: "Calculating" });
  assert.equal(fixture.view.indicatorProgress?.percent, 47);
  assert.equal(fixture.view.indicatorProgress.stage, "Calculating");
  await settle();

  t.mock.timers.tick(1_000);
  await settle();
  assert.equal(fixture.view.indicatorProgress.percent, 47);
  const second = fixture.requests[1].reportIndicatorProgress;
  second({ operationId: "two", percent: 91, stage: "Unowned progress" });
  assert.equal(fixture.view.indicatorProgress.percent, 47);
  first({ operationId: "one", percent: 100, stage: "Finalizing" });
  assert.equal(fixture.view.indicatorProgress.percent, 99);
  first({ operationId: "one", outcome: "applied", stage: "Complete" });
  assert.equal(fixture.view.indicatorProgress.percent, 100);

  second({ operationId: "two", outcome: "started", percent: 0, stage: "Preparing" });
  assert.equal(fixture.view.indicatorProgress.percent, 0);
  first({ operationId: "one", outcome: "deferred", stage: "Old calculation" });
  assert.equal(fixture.view.indicatorProgress.stage, "Preparing");
  second({ operationId: "two", outcome: "deferred", stage: "Retrying" });
  assert.equal(fixture.view.indicatorProgress.percent, null);
  assert.equal(fixture.view.indicatorProgress.stage, "Retrying");
  second({ operationId: "two", percent: 90, stage: "Outdated progress" });
  assert.equal(fixture.view.indicatorProgress.stage, "Retrying");
  fixture.scheduler.setIndicatorCalculation(false);
  assert.equal(fixture.view.indicatorProgress, null);
  second({ operationId: "two", outcome: "started", percent: 0, stage: "Old calculation" });
  assert.equal(fixture.view.indicatorProgress, null);
  finishChecks.forEach(resolve => resolve());
  await settle();
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
  t.mock.timers.tick(2_000);
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
