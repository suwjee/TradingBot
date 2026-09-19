const presentations = {
  success: { title: "Completed", icon: "check", duration: 3600 },
  error: { title: "Action needed", icon: "warning", duration: 5200 },
  info: { title: "Notice", icon: "info", duration: 4000 },
};

export function farazActivityNotice(activity, detail = "") {
  const symbol = String(detail || "").trim();
  const notices = {
    start: { message: "FARAZ extraction started.", type: "info" },
    cancel: { message: "FARAZ cancellation requested.", type: "info" },
    reset: { message: "FARAZ exporter settings restored.", type: "success" },
    "symbol-added": { message: `${symbol} added to FARAZ symbols.`, type: "success" },
    "symbol-removed": { message: `${symbol} removed from FARAZ symbols.`, type: "success" },
  };
  return notices[activity] || null;
}

export function farazLoginWaitingDetail({ connected, state } = {}) {
  if (connected || state !== "waiting_for_login") return null;
  return "Complete sign-in in the FARAZ browser. After the local session is saved, that browser closes automatically.";
}

export function farazExtractionOutcome({ done, coverageComplete, continuedFromAvailable, candleCountResult } = {}) {
  const candleCount = Number(candleCountResult || 0).toLocaleString("en-US");
  if (done && continuedFromAvailable) {
    return {
      state: "success",
      message: `${candleCount} candles were saved from the first available FARAZ candle.`,
      type: "success",
    };
  }
  if (done && coverageComplete === false) {
    return {
      state: "error",
      message: `${candleCount} candles were saved, but FARAZ still has unresolved source gaps.`,
      type: "error",
    };
  }
  if (done) return { state: "success", message: `${candleCount} candles are ready`, type: "success" };
  return { state: "error", message: "Extraction stopped", type: "error" };
}

export function indicatorApplyProblem({ enabled, direction } = {}) {
  if (!enabled) return "Turn the indicator on before applying.";
  if (!["bullish", "bearish"].includes(direction)) return "Select a trend direction.";
  return null;
}

export function notificationPresentation(type) {
  return presentations[type] || presentations.info;
}

export function indicatorNotificationType(type) {
  return type === "error" ? "error" : null;
}

export function createCaptureFeedback({
  setTimer = globalThis.setTimeout,
  clearTimer = globalThis.clearTimeout,
} = {}) {
  let timer = null;
  return {
    flash(element) {
      if (!element) return;
      if (timer != null) clearTimer(timer);
      element.classList.remove("capture-flash-active");
      // Restart the animation even when captures happen in quick succession.
      void element.offsetWidth;
      element.classList.add("capture-flash-active");
      timer = setTimer(() => {
        element.classList.remove("capture-flash-active");
        timer = null;
      }, 520);
    },
  };
}
