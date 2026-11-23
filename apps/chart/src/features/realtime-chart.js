import { icon } from "../ui/icons.js";
import { positionAnchoredPopover, setAnchoredPopoverOpen } from "../ui/popover.js";

const INTERVALS = new Map([
  [1_000, "1s"],
  [5_000, "5s"],
  [30_000, "30s"],
  [60_000, "1m"],
  [120_000, "2m"],
  [180_000, "3m"],
  [300_000, "5m"],
  [600_000, "10m"],
  [900_000, "15m"],
]);
const DEFAULT_INTERVAL_MS = 60_000;
const FULL_VERIFICATION_INTERVAL_MS = 600_000;
const POLL_OFFSET_MS = 2_000;

function formatInterval(ms) {
  if (ms % 86_400_000 === 0) return `${ms / 86_400_000}d`;
  if (ms % 3_600_000 === 0) return `${ms / 3_600_000}h`;
  if (ms % 60_000 === 0) return `${ms / 60_000}m`;
  return `${ms / 1_000}s`;
}

function pollingIntervals(minimumMs) {
  const values = [...INTERVALS.keys()];
  if (minimumMs && !INTERVALS.has(minimumMs)) values.push(minimumMs);
  return values.sort((a, b) => a - b).map(ms => ({
    ms, label: INTERVALS.get(ms) ?? formatInterval(ms), disabled: ms < minimumMs,
  }));
}

function candleCoverage(verification) {
  const { verifiedCount, totalCount } = verification ?? {};
  if (!Number.isSafeInteger(verifiedCount) || !Number.isSafeInteger(totalCount) || totalCount <= 0) return null;
  if (verifiedCount >= totalCount) return 100;
  return Math.max(0, Math.min(99, Math.round(verifiedCount / totalCount * 100)));
}

export function createRealtimeChartScheduler({ runUpdate, render, onVerificationComplete, now = Date.now }) {
  let chartId = null;
  let enabled = false;
  let minimumIntervalMs = 0;
  let intervals = pollingIntervals(minimumIntervalMs);
  let intervalMs = DEFAULT_INTERVAL_MS;
  let indicatorCalculation = false;
  let indicatorError = "";
  let liveCalculationError = "";
  let realtimeError = "";
  let status = "";
  let indicatorStatus = "";
  let indicatorUpdate = null;
  let indicatorOperation = null;
  let indicatorProgress = null;
  let scope = new AbortController();
  let indicatorAbort = null;
  let failed = false;
  let verification = null;
  let progress = null;
  let verifyAllProgress = null;
  let verifyAllOutcome = "idle";
  let active = null;
  let queued = false;
  let verifyAllQueued = false;
  let nextDue = null;
  let nextFullVerification = null;
  let timer;

  function nextBoundary(time) {
    const offset = new Date(time).getTimezoneOffset() * 60_000;
    return (Math.floor((time - offset - POLL_OFFSET_MS) / intervalMs) + 1) * intervalMs + offset + POLL_OFFSET_MS;
  }

  function notify() {
    const time = now();
    const currentCheck = active?.signal === scope.signal ? active : null;
    const verifyAllRemainingMs = nextFullVerification === null ? null : Math.max(0, nextFullVerification - time);
    const verifyAllWaiting = verifyAllQueued || (Boolean(active) && verifyAllRemainingMs === 0);
    const verifyAllState = currentCheck?.verifyAll ? "running" : verifyAllWaiting ? "queued" : verifyAllOutcome;
    render({
      hasChart: Boolean(chartId), enabled, intervalMs, intervals, minimumIntervalMs,
      indicatorCalculation, indicatorError, indicatorProgress, liveCalculationError, realtimeError,
      status: failed ? status : [status, indicatorStatus].filter(Boolean).join(" "), failed,
      verification, verificationPercent: candleCoverage(verification), progress,
      busy: enabled && Boolean(currentCheck && !currentCheck.verifyAll && !currentCheck.indicatorOnly),
      verifyingAll: verifyAllWaiting || Boolean(currentCheck?.verifyAll),
      remainingMs: nextDue === null ? null : Math.max(0, nextDue - time),
      verifyAllRemainingMs, verifyAllState,
      verifyAllProgress: verifyAllState === "queued" ? null : verifyAllProgress,
    });
  }

  function wake() {
    if (!enabled) return;
    clearTimeout(timer);
    const time = now();
    // Re-align after a backward clock jump. An overdue timer makes one check,
    // then the next boundary is scheduled after that check finishes.
    if (nextDue - time > intervalMs) nextDue = nextBoundary(time);
    if (nextFullVerification - time > FULL_VERIFICATION_INTERVAL_MS)
      nextFullVerification = time + FULL_VERIFICATION_INTERVAL_MS;
    if (active) {
      notify();
      if (time < nextFullVerification)
        timer = setTimeout(wake, Math.min(1000, nextFullVerification - time));
      return;
    }
    if (nextDue === null) return;
    const remainingMs = nextDue - time;
    if (nextFullVerification !== null && time >= nextFullVerification) {
      void check("verify");
      return;
    }
    if (remainingMs <= 0) {
      nextDue = null;
      void check("poll");
      return;
    }
    notify();
    timer = setTimeout(wake, Math.min(remainingMs, nextFullVerification - time, 1000));
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
    function finish(nextStatus, error = "") {
      if (signal.aborted || indicatorUpdate !== update) return;
      indicatorUpdate = null;
      indicatorStatus = nextStatus;
      liveCalculationError = error;
      notify();
    }
    void update.then(result => finish(result?.status || "", result?.indicatorError),
      error => finish("Indicator update deferred. Retrying at the next check.", error?.message || "Indicator calculation failed."));
  }

  function resetIndicatorProgress() {
    indicatorOperation = null;
    indicatorProgress = null;
  }

  async function check(kind) {
    if (!chartId || (!enabled && !verifyAllQueued)) return;
    if (active) {
      if (kind === "indicator") queued = true;
      status = "Waiting for the previous check to finish…";
      notify();
      return;
    }
    clearTimeout(timer);
    nextDue = null;
    queued = false;
    const manualVerification = verifyAllQueued;
    const verifyAll = manualVerification || (enabled && nextFullVerification !== null && now() >= nextFullVerification);
    verifyAllQueued = false;
    if (verifyAll && enabled) nextFullVerification = now() + FULL_VERIFICATION_INTERVAL_MS;
    const { signal } = scope;
    const indicatorSignal = getIndicatorSignal();
    const indicatorOnly = kind === "indicator" && !verifyAll;
    const checkRun = { verifyAll, indicatorOnly, signal };
    const setCheckProgress = value => {
      if (verifyAll) verifyAllProgress = value;
      else if (!indicatorOnly) progress = value;
    };
    const reportProgress = value => {
      const previous = verifyAll ? verifyAllProgress : progress;
      if (active !== checkRun || signal.aborted || !Number.isInteger(value) || value <= previous || value > 99) return;
      setCheckProgress(value);
      notify();
    };
    const reportVerification = value => {
      if (active !== checkRun || signal.aborted || !value) return;
      verification = value;
      notify();
    };
    function reportIndicatorProgress({ operationId, percent, stage, outcome = "running" }) {
      if (!operationId || signal.aborted || !indicatorSignal || indicatorSignal.aborted) return;
      if (outcome === "started") {
        indicatorOperation = { checkRun, operationId };
        indicatorProgress = null;
      } else if (indicatorOperation?.checkRun !== checkRun || indicatorOperation.operationId !== operationId) {
        return;
      }
      if (outcome === "started" || outcome === "running") {
        const lastPercent = indicatorProgress?.percent ?? 0;
        const nextPercent = Number.isFinite(percent) ? Math.max(lastPercent, Math.min(99, Math.round(percent))) : lastPercent;
        indicatorProgress = { percent: nextPercent, stage: stage || indicatorProgress?.stage || "" };
      } else {
        resetIndicatorProgress();
        if (outcome === "applied") indicatorProgress = { percent: 100, stage: stage || "Complete" };
        if (outcome === "deferred") indicatorProgress = { percent: null, stage: stage || "Deferred" };
      }
      notify();
    }
    const request = { chartId, signal, indicatorCalculation: Boolean(indicatorSignal), indicatorSignal, pollIntervalMs: intervalMs, reportIndicatorProgress,
      ...(verifyAll ? { verifyAll: true } : {}), ...(indicatorOnly ? { indicatorOnly: true } : { reportProgress, reportVerification }) };
    active = checkRun;
    setCheckProgress(0);
    if (verifyAll) verifyAllOutcome = "idle";
    if (!indicatorUpdate) indicatorStatus = "";
    status = verifyAll ? "Verifying all candles…" : kind === "indicator" ? "Updating indicator…" : "Checking for new candles…";
    failed = false;
    notify();
    if (enabled) timer = setTimeout(wake, Math.min(1000, nextFullVerification - now()));
    try {
      const result = await runUpdate(request);
      if (!signal.aborted && !indicatorOnly) {
        realtimeError = result?.verification?.status === "unavailable" ? "Market data verification is unavailable." : "";
      }
      if (!signal.aborted && result?.verification) {
        verification = result.verification;
        if (!indicatorOnly) {
          const offline = verification.status === "unavailable";
          setCheckProgress(offline ? null : 100);
          if (verifyAll && offline) verifyAllOutcome = "offline";
          if (manualVerification && verification.status !== "unavailable") onVerificationComplete?.(verification);
        }
      } else if (!signal.aborted) setCheckProgress(null);
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
            resetIndicatorProgress();
          }
        }
      }
    } catch (error) {
      if (!signal.aborted) {
        setCheckProgress(null);
        if (verifyAll) verifyAllOutcome = "failed";
      }
      if (!signal.aborted && (!indicatorOnly || !indicatorSignal?.aborted)) {
        status = error?.message || "Could not check for new candles.";
        if (indicatorOnly) liveCalculationError = status;
        else realtimeError = status;
        failed = true;
      }
    } finally {
      active = null;
      if (verifyAllQueued) void check("verify");
      else if (enabled && !verifyAll && now() >= nextFullVerification) void check("verify");
      else if (queued && enabled) void check("indicator");
      else if (enabled) {
        if (verifyAll && now() >= nextFullVerification) nextFullVerification = now() + FULL_VERIFICATION_INTERVAL_MS;
        scheduleNext();
      }
      else notify();
    }
  }

  function enable() {
    if (enabled || !chartId) return;
    enabled = true;
    nextFullVerification = now() + FULL_VERIFICATION_INTERVAL_MS;
    if (active) { wake(); return; }
    scheduleNext();
  }

  function stop() {
    enabled = false;
    queued = false;
    verifyAllQueued = false;
    nextDue = null;
    nextFullVerification = null;
    clearTimeout(timer);
    scope.abort();
    scope = new AbortController();
    indicatorAbort?.abort();
    indicatorAbort = null;
    indicatorUpdate = null;
    indicatorStatus = "";
    resetIndicatorProgress();
    status = "";
    failed = false;
    indicatorError = "";
    liveCalculationError = "";
    realtimeError = "";
    progress = null;
    verifyAllProgress = null;
    verifyAllOutcome = "idle";
    notify();
  }

  function contextChanged(nextChartId, sourceTimeframeSeconds, savedVerification = null) {
    chartId = nextChartId;
    const sourceIntervalMs = sourceTimeframeSeconds * 1_000;
    minimumIntervalMs = chartId && Number.isSafeInteger(sourceIntervalMs) && sourceIntervalMs > 0 ? sourceIntervalMs : 0;
    intervals = pollingIntervals(minimumIntervalMs);
    intervalMs = Math.max(DEFAULT_INTERVAL_MS, minimumIntervalMs);
    indicatorCalculation = false;
    verification = savedVerification;
    stop();
    enable();
  }

  function verifyAll() {
    if (!chartId || active?.verifyAll || verifyAllQueued) return;
    verifyAllQueued = true;
    void check("verify");
  }

  function setInterval(nextInterval) {
    if (intervalMs === nextInterval) return;
    if (!intervals.some(({ ms, disabled }) => ms === nextInterval && !disabled)) {
      notify();
      return;
    }
    intervalMs = nextInterval;
    if (enabled && !active) scheduleNext();
    else notify();
  }

  function setIndicatorCalculation(nextValue) {
    if (!enabled) return;
    const wasEnabled = indicatorCalculation;
    indicatorError = "";
    liveCalculationError = "";
    indicatorCalculation = nextValue;
    if (!indicatorCalculation) resetIndicatorProgress();
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

  function requestIndicatorUpdate({ repair = false } = {}) {
    if (enabled && (indicatorCalculation || repair)) void check("indicator");
  }

  function useStoredVerification(nextChartId, value) {
    if (nextChartId !== chartId || !value) return;
    verification = value;
    notify();
  }

  return { enable, stop, contextChanged, setInterval, setIndicatorCalculation, verifyAll, wake, getIndicatorSignal,
    requestIndicatorUpdate, useStoredVerification };
}

function updateText(element, text) {
  if (element.textContent !== text) element.textContent = text;
}

function formatCountdown(ms) {
  const seconds = Math.ceil(ms / 1000);
  return `${String(Math.floor(seconds / 60)).padStart(2, "0")}:${String(seconds % 60).padStart(2, "0")}`;
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

export function mountRealtimeChart({ trigger, footerTrigger, runUpdate, getChartId, getSourceTimeframeSeconds, getStoredVerification,
  onVerificationComplete, onStateChange }) {
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
      <span class="realtime-chart-emblem" aria-hidden="true">${icon("activity", 19)}</span>
      <div class="realtime-chart-heading">
        <strong id="realtimeChartTitle">Real-time Chart</strong>
        <span class="realtime-chart-mode" data-live-mode></span>
      </div>
      <button class="btn" type="button" data-enable>Enable</button>
    </header>
    <section class="realtime-chart-section" aria-labelledby="realtimeChartPollingTitle">
      <div class="realtime-chart-row">
        <h2 id="realtimeChartPollingTitle">Candle polling</h2>
        <select id="realtimeChartInterval" aria-label="Polling interval" aria-describedby="realtimeChartMinimumInterval" disabled></select>
      </div>
      <div class="realtime-chart-poll-meta">
        <span>Next poll <b data-countdown role="timer"></b></span>
        <span id="realtimeChartMinimumInterval" hidden></span>
        <span data-poll-progress role="progressbar" aria-label="Candle check progress" aria-valuemin="0" aria-valuemax="100" hidden></span>
      </div>
    </section>
    <section class="realtime-chart-section realtime-chart-verification" aria-labelledby="realtimeChartVerificationTitle" data-verify-panel>
      <div class="realtime-chart-row">
        <h2 id="realtimeChartVerificationTitle">Full verification</h2>
        <button class="btn" type="button" data-verify-all>Verify All</button>
      </div>
      <div class="realtime-chart-metrics">
        <div>
          <span class="realtime-chart-metric-label">Next Verify All</span>
          <b data-verify-countdown role="timer"></b>
        </div>
        <div>
          <span class="realtime-chart-metric-label">Progress</span>
          <div class="realtime-chart-meter">
            <b data-verify-progress aria-hidden="true"></b>
            <progress data-verify-meter max="100" value="0" aria-label="Verify All progress" hidden></progress>
            <span data-verify-result></span>
          </div>
        </div>
      </div>
      <div class="realtime-chart-coverage" data-verification role="status">
        <i aria-hidden="true"></i>
        <span>Candles verified</span>
        <b data-verification-value></b>
      </div>
    </section>
    <section class="realtime-chart-section realtime-chart-indicator" aria-labelledby="realtimeChartIndicatorTitle">
      <div class="realtime-chart-row">
        <h2 id="realtimeChartIndicatorTitle"><label for="realtimeChartIndicator">Indicator Calculation</label></h2>
        <span data-indicator-progress role="progressbar" aria-label="Indicator calculation progress" aria-describedby="realtimeChartIndicatorStage" aria-valuemin="0" aria-valuemax="100" hidden></span>
        <label class="master-switch">
          <input type="checkbox" role="switch" id="realtimeChartIndicator" aria-describedby="realtimeChartIndicatorError" disabled>
          <span aria-hidden="true"></span>
        </label>
      </div>
      <p id="realtimeChartIndicatorStage" class="realtime-chart-detail" role="status" hidden></p>
      <p class="realtime-chart-error" id="realtimeChartIndicatorError" role="status"></p>
    </section>
    <p data-status class="realtime-chart-feedback" role="status"></p>`;
  const preview = document.createElement("div");
  preview.id = "realtimeChartPreview";
  preview.className = "popover realtime-chart-preview";
  preview.hidden = true;
  preview.setAttribute("role", "tooltip");
  preview.innerHTML = `<span>Next poll</span><b data-next-poll></b>
    <span>Full verification</span><b data-next-verification></b>`;
  document.body.append(menu, preview);

  trigger.classList.add("realtime-chart-button");
  trigger.innerHTML = `<span class="realtime-chart-icon" aria-hidden="true">${icon("activity", 13)}</span>`;
  trigger.setAttribute("aria-label", "Real-time Chart");
  const triggers = [trigger, footerTrigger];
  for (const button of triggers) {
    button.setAttribute("aria-haspopup", "dialog");
    button.setAttribute("aria-controls", menu.id);
    button.setAttribute("aria-expanded", "false");
  }
  footerTrigger.setAttribute("aria-describedby", preview.id);

  const toggle = menu.querySelector("[data-enable]");
  const liveMode = menu.querySelector("[data-live-mode]");
  const interval = menu.querySelector("#realtimeChartInterval");
  const minimumInterval = menu.querySelector("#realtimeChartMinimumInterval");
  const progress = menu.querySelector("[data-poll-progress]");
  const indicator = menu.querySelector("#realtimeChartIndicator");
  const indicatorProgress = menu.querySelector("[data-indicator-progress]");
  const indicatorStage = menu.querySelector("#realtimeChartIndicatorStage");
  const indicatorError = menu.querySelector("#realtimeChartIndicatorError");
  const status = menu.querySelector("[data-status]");
  const countdown = menu.querySelector("[data-countdown]");
  const verifyAll = menu.querySelector("[data-verify-all]");
  const verifyPanel = menu.querySelector("[data-verify-panel]");
  const verifyCountdown = menu.querySelector("[data-verify-countdown]");
  const verifyMeter = menu.querySelector("[data-verify-meter]");
  const verifyProgress = menu.querySelector("[data-verify-progress]");
  const verifyResult = menu.querySelector("[data-verify-result]");
  const verification = menu.querySelector("[data-verification]");
  const verificationValue = menu.querySelector("[data-verification-value]");
  const previewPoll = preview.querySelector("[data-next-poll]");
  const previewVerification = preview.querySelector("[data-next-verification]");
  let displayedIntervals;
  let open = false;
  let enabled = false;
  let anchor = trigger;
  let previewTimer;

  function setOpen(next, restoreFocus = false, nextAnchor = anchor) {
    if (restoreFocus) anchor.focus();
    if (nextAnchor !== anchor) anchor.setAttribute("aria-expanded", "false");
    anchor = nextAnchor;
    open = setAnchoredPopoverOpen({ menu, trigger: anchor, open: next });
    if (open) hidePreview();
  }

  function showPreview() {
    window.clearTimeout(previewTimer);
    if (open) return;
    preview.hidden = false;
    positionAnchoredPopover({ menu: preview, trigger: footerTrigger, gap: 5 });
  }

  function hidePreview() {
    window.clearTimeout(previewTimer);
    preview.hidden = true;
  }

  function queuePreviewHide() {
    window.clearTimeout(previewTimer);
    if (document.activeElement !== footerTrigger) previewTimer = window.setTimeout(hidePreview, 150);
  }

  function renderProgress(element, value) {
    element.hidden = value == null;
    if (element.hidden) element.removeAttribute("aria-valuenow");
    else element.setAttribute("aria-valuenow", String(value));
    updateText(element, element.hidden ? "" : `${value}%`);
  }

  const scheduler = createRealtimeChartScheduler({
    runUpdate,
    onVerificationComplete,
    render(view) {
      enabled = view.enabled;
      toggle.disabled = !view.hasChart;
      updateText(toggle, enabled ? "Disable" : "Enable");
      toggle.classList.toggle("primary", view.hasChart && !enabled);
      liveMode.dataset.active = String(enabled);
      updateText(liveMode, enabled ? "Live updates on" : view.hasChart ? "Paused" : "No RAW chart");
      interval.disabled = !enabled;
      indicator.disabled = !enabled;
      if (view.intervals !== displayedIntervals) {
        displayedIntervals = view.intervals;
        interval.replaceChildren(...displayedIntervals.map(({ ms, label, disabled }) => {
          const option = document.createElement("option");
          option.value = String(ms);
          option.textContent = label;
          option.disabled = disabled;
          return option;
        }));
        minimumInterval.hidden = view.minimumIntervalMs <= 1_000;
        updateText(minimumInterval, minimumInterval.hidden ? "" : `RAW minimum ${formatInterval(view.minimumIntervalMs)}`);
      }
      if (Number(interval.value) !== view.intervalMs) interval.value = String(view.intervalMs);
      renderProgress(progress, view.busy ? view.progress : null);
      indicator.checked = view.indicatorCalculation;
      indicator.setAttribute("aria-invalid", String(Boolean(view.indicatorError || view.liveCalculationError)));
      renderProgress(indicatorProgress, view.indicatorProgress?.percent);
      const stage = view.indicatorProgress?.stage || "";
      indicatorStage.hidden = !stage;
      updateText(indicatorStage, stage);
      updateText(indicatorError, view.indicatorError || view.liveCalculationError);
      const transient = ["Checking for new candles…", "Verifying all candles…", "Waiting for the previous check to finish…"];
      updateText(status, !view.hasChart ? "Open a RAW chart to enable live updates."
        : transient.includes(view.status) ? "" : view.status);
      status.classList.toggle("realtime-chart-error", view.failed);
      trigger.classList.toggle("is-live", enabled);
      const verificationStatus = view.verification?.status;
      const offline = verificationStatus === "unavailable";
      trigger.classList.toggle("verification-unavailable", offline);
      trigger.title = offline ? "Real-time Chart · Candle verification unavailable"
        : enabled ? "Real-time Chart (enabled)" : "Real-time Chart";
      verification.dataset.state = verificationStatus || "idle";
      verifyAll.disabled = !view.hasChart || view.verifyingAll;
      const { verifyAllState, verifyAllProgress, verifyAllRemainingMs } = view;
      verifyPanel.dataset.state = verifyAllState;
      updateText(verifyAll, verifyAllState === "queued" ? "Queued" : verifyAllState === "running" ? "Verifying…" : "Verify All");
      const verificationTime = verifyAllState === "queued" ? "Queued" : verifyAllRemainingMs === null
        ? (view.hasChart ? "Paused" : "—") : verifyAllRemainingMs === 0 && verifyAllState === "running"
          ? "After this run" : formatCountdown(verifyAllRemainingMs);
      updateText(verifyCountdown, verificationTime);
      updateText(previewVerification, verifyAllState === "running" ? "Verifying…" : verificationTime);
      verifyMeter.hidden = verifyAllProgress === null;
      verifyProgress.hidden = verifyMeter.hidden;
      verifyResult.hidden = !verifyMeter.hidden;
      if (!verifyMeter.hidden && verifyMeter.value !== verifyAllProgress) verifyMeter.value = verifyAllProgress;
      updateText(verifyProgress, verifyMeter.hidden ? "" : `${verifyAllProgress}%`);
      updateText(verifyResult, verifyAllState === "offline" ? "Offline" : verifyAllState === "failed" ? "Failed" : "—");
      const coverage = view.verificationPercent === null ? "—" : `${view.verificationPercent}%`;
      updateText(verificationValue, offline && view.verificationPercent !== null ? `${coverage} · Offline`
        : offline ? "Offline" : coverage);

      const pollTime = view.busy ? "Checking…" : view.remainingMs === null ? "—" : formatCountdown(view.remainingMs);
      updateText(countdown, pollTime);
      updateText(previewPoll, view.hasChart && !view.enabled ? "Paused" : pollTime);
      const fill = view.busy ? 1 : 1 - (view.remainingMs ?? view.intervalMs) / view.intervalMs;
      trigger.style.setProperty("--realtime-chart-fill", `${360 * fill}deg`);
      onStateChange?.(view);
    },
  });

  for (const button of triggers) {
    button.addEventListener("click", () => {
      setOpen(!open || anchor !== button, false, button);
      if (open) (toggle.disabled ? menu : toggle).focus();
    });
  }
  footerTrigger.addEventListener("pointerenter", event => {
    if (event.pointerType !== "touch") showPreview();
  });
  footerTrigger.addEventListener("pointerleave", queuePreviewHide);
  footerTrigger.addEventListener("focus", showPreview);
  footerTrigger.addEventListener("blur", hidePreview);
  preview.addEventListener("pointerenter", showPreview);
  preview.addEventListener("pointerleave", queuePreviewHide);
  toggle.addEventListener("click", () => {
    if (enabled) scheduler.stop();
    else scheduler.enable();
  });
  interval.addEventListener("change", () => scheduler.setInterval(Number(interval.value)));
  indicator.addEventListener("change", () => {
    scheduler.setIndicatorCalculation(indicator.checked);
    const chartId = getChartId();
    if (!chartId) return;
    try {
      sessionStorage.setItem(`market-canvas:${chartId}:realtime-indicator`, String(indicator.checked));
    } catch { /* The scheduler already applied the tab's current preference. */ }
  });
  verifyAll.addEventListener("click", scheduler.verifyAll);

  function closeOutside(event) {
    if (open && !menu.contains(event.target) && !triggers.some(button => button.contains(event.target))) setOpen(false);
  }
  function reposition(event) {
    if (open && !(event.target instanceof window.Node && menu.contains(event.target))) setOpen(true);
    if (!preview.hidden) showPreview();
  }
  document.addEventListener("click", closeOutside);
  document.addEventListener("focusin", closeOutside);
  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape" || (!open && preview.hidden)) return;
    event.preventDefault();
    event.stopPropagation();
    if (open) setOpen(false, true);
    hidePreview();
  }, true);
  document.addEventListener("scroll", reposition, { capture: true, passive: true });
  window.addEventListener("resize", reposition, { passive: true });
  window.visualViewport?.addEventListener("resize", reposition, { passive: true });
  window.visualViewport?.addEventListener("scroll", reposition, { passive: true });
  new window.ResizeObserver(() => {
    if (open) setOpen(true);
  }).observe(menu);
  document.addEventListener("fullscreenchange", () => {
    setOpen(false);
    hidePreview();
  });
  document.addEventListener("visibilitychange", () => {
    if (!document.hidden) scheduler.wake();
  });

  function contextChanged() {
    const chartId = getChartId();
    scheduler.contextChanged(chartId, chartId ? getSourceTimeframeSeconds?.() : undefined,
      chartId ? getStoredVerification?.() : null);
    if (chartId) {
      try {
        if (sessionStorage.getItem(`market-canvas:${chartId}:realtime-indicator`) === "true") {
          scheduler.setIndicatorCalculation(true);
        }
      } catch { /* The default preference is available without storage. */ }
    }
    if (open) setOpen(false, menu.contains(document.activeElement));
    hidePreview();
  }
  contextChanged();
  return { contextChanged, stop: scheduler.stop, getIndicatorSignal: scheduler.getIndicatorSignal,
    requestIndicatorUpdate: scheduler.requestIndicatorUpdate, useStoredVerification: scheduler.useStoredVerification };
}
