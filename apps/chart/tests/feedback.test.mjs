import test from "node:test";
import assert from "node:assert/strict";

import {
  createCaptureFeedback,
  farazActivityNotice,
  farazExtractionOutcome,
  farazLoginWaitingDetail,
  indicatorApplyProblem,
  indicatorNotificationType,
  notificationPresentation,
} from "../src/ui/feedback.js";

test("FARAZ action feedback distinguishes progress from completed local changes", () => {
  assert.deepEqual(farazActivityNotice("start"), { message: "FARAZ extraction started.", type: "info" });
  assert.deepEqual(farazActivityNotice("cancel"), { message: "FARAZ cancellation requested.", type: "info" });
  assert.deepEqual(farazActivityNotice("reset"), { message: "FARAZ exporter settings restored.", type: "success" });
});

test("FARAZ sign-in explains that the temporary browser closes after local persistence", () => {
  assert.equal(
    farazLoginWaitingDetail({ connected: false, state: "waiting_for_login" }),
    "Complete sign-in in the FARAZ browser. After the local session is saved, that browser closes automatically.",
  );
  assert.equal(farazLoginWaitingDetail({ connected: false, state: "not_connected" }), null);
});

test("FARAZ source coverage gaps are never presented as a successful extraction", () => {
  assert.deepEqual(farazExtractionOutcome({ done: true, coverageComplete: false, candleCountResult: 42 }), {
    state: "error",
    message: "42 candles were saved, but FARAZ still has unresolved source gaps.",
    type: "error",
  });
});

test("FARAZ continuation confirms the saved available-data range", () => {
  assert.deepEqual(farazExtractionOutcome({
    done: true,
    coverageComplete: false,
    continuedFromAvailable: true,
    candleCountResult: 42,
  }), {
    state: "success",
    message: "42 candles were saved from the first available FARAZ candle.",
    type: "success",
  });
});

test("FARAZ symbol feedback identifies the affected symbol", () => {
  assert.deepEqual(farazActivityNotice("symbol-added", "FXCM:EURUSD"), {
    message: "FXCM:EURUSD added to FARAZ symbols.",
    type: "success",
  });
  assert.deepEqual(farazActivityNotice("symbol-removed", "FXCM:EURUSD"), {
    message: "FXCM:EURUSD removed from FARAZ symbols.",
    type: "success",
  });
});

test("applying while the indicator is off reports the off state before other validation", () => {
  assert.equal(indicatorApplyProblem({ enabled: false, direction: null }), "Turn the indicator on before applying.");
  assert.equal(indicatorApplyProblem({ enabled: false, direction: "bullish" }), "Turn the indicator on before applying.");
});

test("indicator apply guard reports a missing direction only after the indicator is on", () => {
  assert.equal(indicatorApplyProblem({ enabled: true, direction: null }), "Select a trend direction.");
  assert.equal(indicatorApplyProblem({ enabled: true, direction: "bullish" }), null);
});

test("indicator configuration notifications allow errors only", () => {
  assert.equal(indicatorNotificationType("error"), "error");
  assert.equal(indicatorNotificationType("info"), null);
  assert.equal(indicatorNotificationType("success"), null);
  assert.equal(indicatorNotificationType("auto"), null);
});

test("notification presentation exposes stable semantic labels and icons", () => {
  assert.deepEqual(notificationPresentation("success"), {
    title: "Completed",
    icon: "check",
    duration: 3600,
  });
  assert.deepEqual(notificationPresentation("error"), {
    title: "Action needed",
    icon: "warning",
    duration: 5200,
  });
  assert.deepEqual(notificationPresentation("info"), {
    title: "Notice",
    icon: "info",
    duration: 4000,
  });
});

test("capture feedback restarts an active flash and removes it after the final timer", () => {
  const classes = new Set();
  const element = {
    classList: {
      add: (value) => classes.add(value),
      remove: (value) => classes.delete(value),
    },
  };
  const callbacks = new Map();
  const cleared = [];
  let nextTimer = 0;
  const feedback = createCaptureFeedback({
    setTimer(callback) {
      nextTimer += 1;
      callbacks.set(nextTimer, callback);
      return nextTimer;
    },
    clearTimer(timer) {
      cleared.push(timer);
      callbacks.delete(timer);
    },
  });

  feedback.flash(element);
  assert.equal(classes.has("capture-flash-active"), true);
  feedback.flash(element);
  assert.deepEqual(cleared, [1]);
  callbacks.get(2)();
  assert.equal(classes.has("capture-flash-active"), false);
});
