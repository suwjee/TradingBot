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

export function createRealtimeChartScheduler({ runUpdate, indicatorProblem, render, now = () => performance.now() }) {
  let chartId = null;
  let enabled = false;
  let intervalMs = DEFAULT_INTERVAL_MS;
  let indicatorCalculation = false;
  let indicatorError = "";
  let status = "";
  let failed = false;
  let active = null;
  let queued = false;
  let intervalAnchor = 0;
  let nextDue = null;
  let timer;

  function notify() {
    render({
      hasChart: Boolean(chartId), enabled, intervalMs, indicatorCalculation, indicatorError, status, failed,
      busy: enabled && Boolean(active),
      remainingMs: nextDue === null ? null : Math.max(0, nextDue - now()),
    });
  }

  function wake() {
    if (nextDue === null) return;
    clearTimeout(timer);
    const remainingMs = nextDue - now();
    if (remainingMs <= 0) {
      nextDue = null;
      void check();
      return;
    }
    notify();
    timer = setTimeout(wake, Math.min(remainingMs, 1000));
  }

  function scheduleNext() {
    const elapsedMs = now() - intervalAnchor;
    const intervals = Math.max(1, Math.ceil(elapsedMs / intervalMs));
    nextDue = intervalAnchor + intervals * intervalMs;
    wake();
  }

  async function check() {
    if (!enabled) return;
    clearTimeout(timer);
    nextDue = null;
    if (active) {
      queued = true;
      status = "Waiting for the previous check to finish…";
      notify();
      return;
    }
    queued = false;
    if (indicatorCalculation) {
      indicatorError = indicatorProblem(chartId) || "";
      indicatorCalculation = !indicatorError;
    }

    const abort = new AbortController();
    const indicatorAbort = indicatorCalculation ? new AbortController() : null;
    const request = { chartId, signal: abort.signal, indicatorCalculation, indicatorSignal: indicatorAbort?.signal };
    active = { abort, indicatorAbort };
    intervalAnchor = now();
    status = "Checking for new candles…";
    failed = false;
    notify();
    try {
      const result = await runUpdate(request);
      if (!abort.signal.aborted && !indicatorAbort?.signal.aborted)
        status = result || "Checked for new candles.";
    } catch (error) {
      if (!abort.signal.aborted && !indicatorAbort?.signal.aborted) {
        status = error?.message || "Could not check for new candles.";
        failed = true;
        if (indicatorCalculation) {
          indicatorError = indicatorProblem(chartId) || "";
          indicatorCalculation = !indicatorError;
        }
      }
    } finally {
      active = null;
      if (queued) void check();
      else if (enabled) scheduleNext();
    }
  }

  function enable() {
    if (enabled || !chartId) return;
    enabled = true;
    void check();
  }

  function stop() {
    enabled = false;
    queued = false;
    nextDue = null;
    clearTimeout(timer);
    active?.abort.abort();
    active?.indicatorAbort?.abort();
    status = "";
    failed = false;
    indicatorError = "";
    notify();
  }

  function contextChanged(nextChartId) {
    chartId = nextChartId;
    intervalMs = DEFAULT_INTERVAL_MS;
    indicatorCalculation = false;
    stop();
  }

  function setInterval(nextInterval) {
    if (!INTERVALS.has(nextInterval) || intervalMs === nextInterval) return;
    intervalMs = nextInterval;
    intervalAnchor = now();
    if (enabled && !active) scheduleNext();
    else notify();
  }

  function setIndicatorCalculation(nextValue) {
    if (!enabled) return;
    const wasEnabled = indicatorCalculation;
    indicatorError = nextValue ? indicatorProblem(chartId) || "" : "";
    indicatorCalculation = nextValue && !indicatorError;
    if (!indicatorCalculation && active?.indicatorAbort && !active.indicatorAbort.signal.aborted) {
      active.indicatorAbort.abort();
      status = "Indicator check canceled.";
    }
    if (indicatorCalculation && !wasEnabled) {
      void check();
      return;
    }
    notify();
  }

  return { enable, stop, contextChanged, setInterval, setIndicatorCalculation, wake };
}

function updateText(element, text) {
  if (element.textContent !== text) element.textContent = text;
}

export function mountRealtimeChart({ trigger, runUpdate, indicatorProblem, getChartId }) {
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
        <select id="realtimeChartInterval">${[...INTERVALS].map(([ms, label]) => `<option value="${ms}">${label}</option>`).join("")}</select>
      </div>
      <div class="realtime-chart-option">
        <label for="realtimeChartIndicator">Indicator Calculation</label>
        <label class="master-switch">
          <input type="checkbox" role="switch" id="realtimeChartIndicator" aria-describedby="realtimeChartIndicatorError">
          <span aria-hidden="true"></span>
        </label>
      </div>
    </fieldset>
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
  const indicator = menu.querySelector("#realtimeChartIndicator");
  const indicatorError = menu.querySelector("#realtimeChartIndicatorError");
  const status = menu.querySelector("[data-status]");
  const countdown = menu.querySelector("[data-countdown]");
  let open = false;
  let enabled = false;

  function setOpen(next, restoreFocus = false) {
    open = setAnchoredPopoverOpen({ menu, trigger, open: next });
    if (!open && restoreFocus) trigger.focus();
  }

  const scheduler = createRealtimeChartScheduler({
    runUpdate,
    indicatorProblem,
    render(view) {
      enabled = view.enabled;
      toggle.disabled = !view.hasChart;
      updateText(toggle, enabled ? "Disable" : "Enable");
      options.disabled = !enabled;
      if (Number(interval.value) !== view.intervalMs) interval.value = String(view.intervalMs);
      indicator.checked = view.indicatorCalculation;
      indicator.setAttribute("aria-invalid", String(Boolean(view.indicatorError)));
      updateText(indicatorError, view.indicatorError);
      updateText(status, view.hasChart ? view.status : "Open a RAW chart to enable live updates.");
      status.classList.toggle("realtime-chart-error", view.failed);
      trigger.classList.toggle("is-live", enabled);
      trigger.title = enabled ? "Real-time Chart (enabled)" : "Real-time Chart";

      const remainingSeconds = Math.ceil((view.remainingMs ?? 0) / 1000);
      const minutes = Math.floor(remainingSeconds / 60);
      const seconds = String(remainingSeconds % 60).padStart(2, "0");
      updateText(countdown, view.remainingMs === null ? "" : `Next check in ${minutes}:${seconds}`);
      const fill = view.busy ? 1 : 1 - (view.remainingMs ?? view.intervalMs) / view.intervalMs;
      trigger.style.setProperty("--realtime-chart-fill", `${360 * fill}deg`);
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
  return { contextChanged, stop: scheduler.stop };
}
