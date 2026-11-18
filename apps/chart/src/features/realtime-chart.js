import { icon } from "../ui/icons.js";
import { setAnchoredPopoverOpen } from "../ui/popover.js";

const INTERVALS = new Map([
  [30_000, "30s"],
  [60_000, "1m"],
  [120_000, "2m"],
  [180_000, "3m"],
  [300_000, "5m"],
  [600_000, "10m"],
  [900_000, "15m"],
]);
const DEFAULT_INTERVAL_MS = 60_000;
const POLL_OFFSET_MS = 2_000;

export function createRealtimeChartScheduler({ runUpdate, render, onVerificationComplete, now = Date.now }) {
  let chartId = null;
  let enabled = false;
  let intervalMs = DEFAULT_INTERVAL_MS;
  let indicatorCalculation = false;
  let indicatorError = "";
  let status = "";
  let indicatorStatus = "";
  let indicatorUpdate = null;
  let scope = new AbortController();
  let indicatorAbort = null;
  let failed = false;
  let verification = null;
  let progress = null;
  let active = null;
  let queued = false;
  let verifyAllQueued = false;
  let nextDue = null;
  let timer;

  function nextBoundary(time) {
    const offset = new Date(time).getTimezoneOffset() * 60_000;
    return (Math.floor((time - offset - POLL_OFFSET_MS) / intervalMs) + 1) * intervalMs + offset + POLL_OFFSET_MS;
  }

  function notify() {
    render({
      hasChart: Boolean(chartId), enabled, intervalMs, indicatorCalculation, indicatorError,
      status: failed ? status : [status, indicatorStatus].filter(Boolean).join(" "), failed, verification, progress,
      busy: enabled && Boolean(active), verifyingAll: verifyAllQueued || Boolean(active?.verifyAll),
      remainingMs: nextDue === null ? null : Math.max(0, nextDue - now()),
    });
  }

  function wake() {
    if (nextDue === null) return;
    clearTimeout(timer);
    const time = now();
    // Re-align after a backward clock jump. An overdue timer makes one check,
    // then the next boundary is scheduled after that check finishes.
    if (nextDue - time > intervalMs) nextDue = nextBoundary(time);
    const remainingMs = nextDue - time;
    if (remainingMs <= 0) {
      nextDue = null;
      void check("poll");
      return;
    }
    notify();
    timer = setTimeout(wake, Math.min(remainingMs, 1000));
  }

  function scheduleNext() {
    nextDue = nextBoundary(now());
    wake();
  }

  function watchIndicatorUpdate(update, signal) {
    if (!update) {
      if (!indicatorUpdate) indicatorStatus = "";
      return;
    }
    indicatorUpdate = update;
    indicatorStatus = "Updating indicator…";
    function finish(nextStatus) {
      if (signal.aborted || indicatorUpdate !== update) return;
      indicatorUpdate = null;
      indicatorStatus = nextStatus;
      notify();
    }
    void update.then(result => finish(result?.status || ""), () => finish("Indicator update deferred. Retrying at the next check."));
  }

  async function check(kind) {
    if (!chartId || (!enabled && !verifyAllQueued)) return;
    clearTimeout(timer);
    nextDue = null;
    if (active) {
      if (kind === "indicator") queued = true;
      status = "Waiting for the previous check to finish…";
      notify();
      return;
    }
    queued = false;
    const verifyAll = verifyAllQueued;
    verifyAllQueued = false;
    const { signal } = scope;
    if (indicatorCalculation) indicatorAbort ||= new AbortController();
    const indicatorSignal = indicatorAbort?.signal;
    const indicatorOnly = kind === "indicator" && !verifyAll;
    const checkRun = { verifyAll, indicatorOnly };
    const reportProgress = value => {
      if (active !== checkRun || signal.aborted || !Number.isInteger(value) || value <= progress || value > 99) return;
      progress = value;
      notify();
    };
    const request = { chartId, signal, indicatorCalculation, indicatorSignal,
      ...(verifyAll ? { verifyAll: true } : {}), ...(indicatorOnly ? { indicatorOnly: true } : { reportProgress }) };
    active = checkRun;
    if (!indicatorOnly) progress = 0;
    if (!indicatorUpdate) indicatorStatus = "";
    status = verifyAll ? "Verifying all candles…" : kind === "indicator" ? "Updating indicator…" : "Checking for new candles…";
    failed = false;
    notify();
    try {
      const result = await runUpdate(request);
      if (!signal.aborted && result?.verification) {
        verification = result.verification;
        if (!indicatorOnly) {
          progress = verification.status === "unavailable" ? null : 100;
          if (verifyAll && verification.status !== "unavailable") onVerificationComplete?.(verification);
        }
      } else if (!signal.aborted && !indicatorOnly) progress = null;
      if (!signal.aborted && (!indicatorOnly || !indicatorSignal?.aborted)) {
        status = (typeof result === "string" ? result : result?.status)
          || (result?.verification || indicatorOnly ? "" : "Checked for new candles.");
        watchIndicatorUpdate(result?.indicatorUpdate, signal);
        if (indicatorSignal && !indicatorSignal.aborted) {
          indicatorError = result?.indicatorError || "";
          indicatorCalculation = !indicatorError;
          if (indicatorError) {
            indicatorAbort.abort();
            indicatorAbort = null;
          }
        }
      }
    } catch (error) {
      if (!signal.aborted && !indicatorOnly) progress = null;
      if (!signal.aborted && (!indicatorOnly || !indicatorSignal?.aborted)) {
        status = error?.message || "Could not check for new candles.";
        failed = true;
      }
    } finally {
      active = null;
      if (verifyAllQueued) void check("verify");
      else if (queued && enabled) void check("indicator");
      else if (enabled) scheduleNext();
      else notify();
    }
  }

  function enable() {
    if (enabled || !chartId) return;
    enabled = true;
    scheduleNext();
  }

  function stop() {
    enabled = false;
    queued = false;
    verifyAllQueued = false;
    nextDue = null;
    clearTimeout(timer);
    scope.abort();
    scope = new AbortController();
    indicatorAbort?.abort();
    indicatorAbort = null;
    indicatorUpdate = null;
    indicatorStatus = "";
    status = "";
    failed = false;
    indicatorError = "";
    progress = null;
    notify();
  }

  function contextChanged(nextChartId) {
    chartId = nextChartId;
    intervalMs = DEFAULT_INTERVAL_MS;
    indicatorCalculation = false;
    verification = null;
    stop();
    enable();
  }

  function verifyAll() {
    if (!chartId || active?.verifyAll || verifyAllQueued) return;
    verifyAllQueued = true;
    void check("verify");
  }

  function setInterval(nextInterval) {
    if (!INTERVALS.has(nextInterval) || intervalMs === nextInterval) return;
    intervalMs = nextInterval;
    if (enabled && !active) scheduleNext();
    else notify();
  }

  function setIndicatorCalculation(nextValue) {
    if (!enabled) return;
    const wasEnabled = indicatorCalculation;
    indicatorError = "";
    indicatorCalculation = nextValue;
    if (!indicatorCalculation && indicatorAbort) {
      indicatorAbort.abort();
      indicatorAbort = null;
      if (indicatorUpdate || (active && wasEnabled)) indicatorStatus = "Indicator check canceled.";
      if (active?.indicatorOnly) status = "";
      indicatorUpdate = null;
    }
    if (indicatorCalculation && !wasEnabled) {
      void check("indicator");
      return;
    }
    notify();
  }

  function getIndicatorSignal() {
    return enabled && indicatorCalculation ? (indicatorAbort ||= new AbortController()).signal : undefined;
  }

  return { enable, stop, contextChanged, setInterval, setIndicatorCalculation, verifyAll, wake, getIndicatorSignal };
}

function updateText(element, text) {
  if (element.textContent !== text) element.textContent = text;
}

export async function readRealtimeUpdate(response, reportProgress) {
  if (!response.headers?.get("Content-Type")?.startsWith("application/x-ndjson")) {
    return { status: response.status, result: await response.json() };
  }
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let pending = "";
  try {
    while (true) {
      const { value, done } = await reader.read();
      pending += decoder.decode(value, { stream: !done });
      let end;
      while ((end = pending.indexOf("\n")) >= 0) {
        const event = JSON.parse(pending.slice(0, end));
        pending = pending.slice(end + 1);
        if (Number.isInteger(event.status)) return event;
        reportProgress?.(event.progress);
      }
      if (done) throw new TypeError("The candle check ended without a result.");
    }
  } finally {
    await reader.cancel().catch(() => {});
    reader.releaseLock();
  }
}

export function mountRealtimeChart({ trigger, runUpdate, getChartId, onVerificationComplete, onStateChange }) {
  const document = trigger.ownerDocument;
  const window = document.defaultView;
  const menu = document.createElement("section");
  menu.id = "realtimeChartPopup";
  menu.className = "popover realtime-chart-popover hidden";
  menu.tabIndex = -1;
  menu.setAttribute("role", "dialog");
  menu.setAttribute("aria-labelledby", "realtimeChartTitle");
  menu.innerHTML = `
    <header class="realtime-chart-header">
      <strong id="realtimeChartTitle">Real-time Chart</strong>
      <button class="btn" type="button" data-enable>Enable</button>
    </header>
    <fieldset class="realtime-chart-options" aria-label="Live update options" disabled>
      <div class="realtime-chart-option">
        <label for="realtimeChartInterval">Polling interval</label>
        <div class="realtime-chart-interval">
          <select id="realtimeChartInterval">${[...INTERVALS].map(([ms, label]) => `<option value="${ms}">${label}</option>`).join("")}</select>
          <span data-poll-progress role="progressbar" aria-label="Candle check progress" aria-valuemin="0" aria-valuemax="100" hidden></span>
        </div>
      </div>
      <div class="realtime-chart-option">
        <label for="realtimeChartIndicator">Indicator Calculation</label>
        <label class="master-switch">
          <input type="checkbox" role="switch" id="realtimeChartIndicator" aria-describedby="realtimeChartIndicatorError">
          <span aria-hidden="true"></span>
        </label>
      </div>
    </fieldset>
    <div class="realtime-chart-option realtime-chart-verification">
      <span data-verification role="status"><i aria-hidden="true"></i><span data-verification-label></span></span>
      <button class="btn" type="button" data-verify-all>Verify All</button>
    </div>
    <p class="realtime-chart-error" id="realtimeChartIndicatorError" role="status"></p>
    <div class="realtime-chart-feedback">
      <p data-status role="status"></p>
      <p data-countdown></p>
    </div>`;
  document.body.append(menu);

  trigger.classList.add("realtime-chart-button");
  trigger.innerHTML = `<span class="realtime-chart-icon" aria-hidden="true">${icon("activity", 13)}</span>`;
  trigger.setAttribute("aria-label", "Real-time Chart");
  trigger.setAttribute("aria-haspopup", "dialog");
  trigger.setAttribute("aria-controls", menu.id);
  trigger.setAttribute("aria-expanded", "false");

  const toggle = menu.querySelector("[data-enable]");
  const options = menu.querySelector("fieldset");
  const interval = menu.querySelector("#realtimeChartInterval");
  const progress = menu.querySelector("[data-poll-progress]");
  const indicator = menu.querySelector("#realtimeChartIndicator");
  const indicatorError = menu.querySelector("#realtimeChartIndicatorError");
  const status = menu.querySelector("[data-status]");
  const countdown = menu.querySelector("[data-countdown]");
  const verifyAll = menu.querySelector("[data-verify-all]");
  const verification = menu.querySelector("[data-verification]");
  const verificationLabel = menu.querySelector("[data-verification-label]");
  let open = false;
  let enabled = false;

  function setOpen(next, restoreFocus = false) {
    open = setAnchoredPopoverOpen({ menu, trigger, open: next });
    if (!open && restoreFocus) trigger.focus();
  }

  const scheduler = createRealtimeChartScheduler({
    runUpdate,
    onVerificationComplete,
    render(view) {
      enabled = view.enabled;
      toggle.disabled = !view.hasChart;
      updateText(toggle, enabled ? "Disable" : "Enable");
      options.disabled = !enabled;
      if (Number(interval.value) !== view.intervalMs) interval.value = String(view.intervalMs);
      progress.hidden = view.progress === null;
      if (!progress.hidden) {
        progress.setAttribute("aria-valuenow", String(view.progress));
        updateText(progress, `${view.progress}%`);
      }
      indicator.checked = view.indicatorCalculation;
      indicator.setAttribute("aria-invalid", String(Boolean(view.indicatorError)));
      updateText(indicatorError, view.indicatorError);
      updateText(status, view.hasChart ? view.status : "Open a RAW chart to enable live updates.");
      status.classList.toggle("realtime-chart-error", view.failed);
      trigger.classList.toggle("is-live", enabled);
      const verificationStatus = view.verification?.status;
      const offline = verificationStatus === "unavailable";
      trigger.classList.toggle("verification-unavailable", offline);
      trigger.title = offline ? "Real-time Chart · Candle verification unavailable"
        : enabled ? "Real-time Chart (enabled)" : "Real-time Chart";
      verification.dataset.state = verificationStatus || "idle";
      verifyAll.disabled = !view.hasChart || view.verifyingAll;
      updateText(verificationLabel, offline ? "Verification unavailable"
        : verificationStatus === "verified" ? "Candles verified"
        : verificationStatus === "pending" ? `${view.verification.verifiedCount.toLocaleString("en-US")} / ${view.verification.totalCount.toLocaleString("en-US")} verified`
        : "Candle verification");

      const remainingSeconds = Math.ceil((view.remainingMs ?? 0) / 1000);
      const minutes = Math.floor(remainingSeconds / 60);
      const seconds = String(remainingSeconds % 60).padStart(2, "0");
      updateText(countdown, view.remainingMs === null ? "" : `Next check in ${minutes}:${seconds}`);
      const fill = view.busy ? 1 : 1 - (view.remainingMs ?? view.intervalMs) / view.intervalMs;
      trigger.style.setProperty("--realtime-chart-fill", `${360 * fill}deg`);
      onStateChange?.(view);
    },
  });

  trigger.addEventListener("click", () => {
    setOpen(!open);
    if (open) (toggle.disabled ? menu : toggle).focus();
  });
  toggle.addEventListener("click", () => {
    if (enabled) scheduler.stop();
    else scheduler.enable();
  });
  interval.addEventListener("change", () => scheduler.setInterval(Number(interval.value)));
  indicator.addEventListener("change", () => scheduler.setIndicatorCalculation(indicator.checked));
  verifyAll.addEventListener("click", scheduler.verifyAll);

  function closeOutside(event) {
    if (open && !menu.contains(event.target) && !trigger.contains(event.target)) setOpen(false);
  }
  function reposition(event) {
    if (open && !(event.target instanceof window.Node && menu.contains(event.target))) setOpen(true);
  }
  document.addEventListener("click", closeOutside);
  document.addEventListener("focusin", closeOutside);
  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape" || !open) return;
    event.preventDefault();
    event.stopPropagation();
    setOpen(false, true);
  }, true);
  document.addEventListener("scroll", reposition, { capture: true, passive: true });
  window.addEventListener("resize", reposition, { passive: true });
  window.visualViewport?.addEventListener("resize", reposition, { passive: true });
  window.visualViewport?.addEventListener("scroll", reposition, { passive: true });
  new window.ResizeObserver(() => {
    if (open) setOpen(true);
  }).observe(menu);
  document.addEventListener("fullscreenchange", () => setOpen(false));
  document.addEventListener("visibilitychange", () => {
    if (!document.hidden) scheduler.wake();
  });

  function contextChanged() {
    scheduler.contextChanged(getChartId());
    if (open) setOpen(false, menu.contains(document.activeElement));
  }
  contextChanged();
  return { contextChanged, stop: scheduler.stop, getIndicatorSignal: scheduler.getIndicatorSignal };
}
