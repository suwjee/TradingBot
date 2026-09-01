import {
  createChart,
  CandlestickSeries,
  CrosshairMode,
} from "lightweight-charts";
import { icon } from "./ui/icons.js";
import { drawingArray, normalizeHistorySnapshot, CHART_TIMEFRAME_KEY, restoredTimeframe, indicatorControlId } from "./chart-state.js";
import { buildCandleLod, chooseLodStride, lowerBoundTime } from "./chart-lod.js";
import { updateStageAggregate } from "./calculation-progress.js";
import { saveManualReview } from "./manual-review.js";
import { initCandleExport } from "./candle-export.js";
import "./styles/tokens.css";
import "./styles/app.css";
import "./drawings/drawing.css";
import "./drawings/object-tree.css";
import "../../indicator/indicator-settings/frontend/reaction-detector.css";
import "./styles/qg-modern.css";

// Checkboxes remain keyboard-accessible, but a broad label/row click must not
// change their value.  Only the native checkbox hit target can toggle it.
document.addEventListener("click", (event) => {
  const target = event.target instanceof Element ? event.target : null;
  if (!target || target.matches('input[type="checkbox"]')) return;
  const checkboxLabel = target.closest('label:has(input[type="checkbox"])');
  // The compact indicator power switch intentionally exposes its styled span
  // as the click target.  Other setting rows remain non-toggleable by label.
  if (checkboxLabel?.classList.contains("master-switch")) return;
  if (checkboxLabel) event.preventDefault();
}, true);

function humanizeEvent(event) {
  return String(event || "")
    .toLowerCase()
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}
const runtimeErrors = [];
function formatSystemDateTime(value) {
  const date = value instanceof Date ? value : new Date(value);
  if (Number.isNaN(date.getTime())) return "—";
  const pad = (part) => String(part).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
}
function refreshRuntimeHealth() {
  const control = document.querySelector("#healthStatus");
  const label = document.querySelector("#healthLabel");
  const hasErrors = runtimeErrors.length > 0;
  if (label) label.textContent = hasErrors ? "Error" : "Healthy";
  if (control) {
    control.dataset.state = hasErrors ? "error" : "healthy";
    control.setAttribute("aria-label", hasErrors ? `${runtimeErrors.length} application errors. Open error log.` : "Application healthy. No errors recorded.");
  }
}
function recordRuntimeError(scope, payload) {
  runtimeErrors.unshift({ scope, ...payload, recordedAt: Date.now() });
  if (runtimeErrors.length > 100) runtimeErrors.length = 100;
  refreshRuntimeHealth();
}
function createLogger(scope) {
  const emit = (level, event, details = {}) => {
    const payload = {
      time: new Date().toISOString(),
      level: level.toUpperCase(),
      event,
      ...details,
    };
    const method = level === "error" ? "error" : level === "warn" ? "warn" : level === "debug" ? "debug" : "info";
    console[method](`[${scope}] [${payload.time}] [${payload.level}] ${event}`, payload);
    const status = document.querySelector("#latestEvent");
    if (status && level !== "debug") {
      status.dataset.level = level;
      status.textContent = humanizeEvent(event);
      status.title = `${payload.time} • ${event}`;
    }
    if (level === "error") recordRuntimeError(scope, payload);
  };
  return {
    debug: (event, details) => emit("debug", event, details),
    info: (event, details) => emit("info", event, details),
    warn: (event, details) => emit("warn", event, details),
    error: (event, error, details = {}) => emit("error", event, {
      ...details,
      error: error instanceof Error ? error.message : String(error),
      stack: error instanceof Error ? error.stack : undefined,
    }),
  };
}
const log = {
  chart: createLogger("CHART"),
  indicator: createLogger("INDICATOR"),
};
window.addEventListener("error", (event) => {
  const signature = `${event.filename || ""} ${event.message || ""} ${event.error?.stack || ""}`;
  const scope = /indicator|reaction/i.test(signature) ? log.indicator : log.chart;
  scope.error("UNCAUGHT_ERROR", event.error || event.message, {
    source: event.filename,
    line: event.lineno,
    column: event.colno,
  });
});
window.addEventListener("unhandledrejection", (event) => {
  const signature = String(event.reason?.stack || event.reason || "");
  (/indicator|reaction/i.test(signature) ? log.indicator : log.chart)
    .error("UNHANDLED_PROMISE_REJECTION", event.reason);
});

const TF = [
  { l: "1s", s: 1 },
  { l: "3s", s: 3 },
  { l: "5s", s: 5 },
  { l: "10s", s: 10 },
  { l: "15s", s: 15 },
  { l: "30s", s: 30 },
  { l: "1m", s: 60 },
  { l: "3m", s: 180 },
  { l: "5m", s: 300 },
  { l: "10m", s: 600 },
  { l: "15m", s: 900 },
  { l: "30m", s: 1800 },
  { l: "45m", s: 2700 },
  { l: "1H", s: 3600 },
  { l: "4H", s: 14400 },
  { l: "1D", s: 86400 },
];
const DRAWING_TOOL_ORDER_KEY = "qg:drawing-tool-order:v1";
const drawingToolDefinitions = [
  ["cursor", "Cursor"],
  ["line", "Trend line"],
  ["hline", "Horizontal line"],
  ["vline", "Vertical line"],
  ["hray", "Horizontal ray"],
  ["fib", "Fibo retracement"],
  ["brush", "Brush"],
  ["rect", "Rectangle"],
  ["circle", "Circle"],
  ["long", "Long position"],
  ["short", "Short position"],
  ["text", "Text"],
  ["path", "Path"],
];
const drawingToolById = new Map(drawingToolDefinitions);
const drawingTools = (() => {
  try {
    const saved = JSON.parse(localStorage.getItem(DRAWING_TOOL_ORDER_KEY) || "null");
    if (Array.isArray(saved) && saved.length === drawingToolDefinitions.length) {
      const ids = saved.filter((id) => drawingToolById.has(id));
      if (new Set(ids).size === drawingToolDefinitions.length) return ids;
    }
  } catch {}
  return drawingToolDefinitions.map(([id]) => id);
})();
const materialIcon = (name) => `<span class="material-symbols-outlined" aria-hidden="true">${name}</span>`;
const stitchDrawingIcon = (name) => {
  const paths = {
    line: '<svg viewBox="0 0 28 28" aria-hidden="true"><path d="M7.354 21.354l14-14-.707-.707-14 14zM22.5 8c-1.381 0-2.5-1.119-2.5-2.5S21.119 3 22.5 3 25 4.119 25 5.5 23.881 8 22.5 8zm-17 17C4.119 25 3 23.881 3 22.5S4.119 20 5.5 20 8 21.119 8 22.5 6.881 25 5.5 25z"/></svg>',
    vline: '<svg viewBox="0 0 28 28" aria-hidden="true"><path d="M15 12.5V4h-1v8.5zm-1 4V25h1v-8.5zM14.5 16A2.5 2.5 0 1 1 14.5 11a2.5 2.5 0 0 1 0 5z"/></svg>',
    hline: '<svg viewBox="0 0 28 28" aria-hidden="true"><path d="M8.5 15H25v-1H8.5zM6.5 17A2.5 2.5 0 1 1 6.5 12a2.5 2.5 0 0 1 0 5z"/></svg>',
    brush: '<svg viewBox="0 0 28 28" aria-hidden="true"><path d="m1.789 23 .859-.854.221-.228c.18-.19.38-.409.597-.655.619-.704 1.238-1.478 1.815-2.298.982-1.396 1.738-2.776 2.177-4.081 1.234-3.667 5.957-4.716 8.923-1.263 3.251 3.785-.037 9.38-5.379 9.38zm9.211-1c4.544 0 7.272-4.642 4.621-7.728-2.45-2.853-6.225-2.015-7.216.931-.474 1.408-1.273 2.869-2.307 4.337-.599.852-1.241 1.653-1.882 2.383l-.068.078zM18.182 6.002l-1.419 1.286c-1.031.935-1.075 2.501-.096 3.48l1.877 1.877c.976.976 2.553.954 3.513-.045l5.65-5.874-.721-.693-5.65 5.874c-.574.596-1.507.609-2.086.031l-1.877-1.877c-.574-.574-.548-1.48.061-2.032l1.419-1.286z"/></svg>',
    rect: '<svg viewBox="0 0 28 28" aria-hidden="true"><path d="M7.5 6h13v-1h-13zM7.5 23h13v-1h-13zM5 7.5v13h1v-13zM22 7.5v13h1v-13zM5.5 8A2.5 2.5 0 1 1 5.5 3a2.5 2.5 0 0 1 0 5zm17 0A2.5 2.5 0 1 1 22.5 3a2.5 2.5 0 0 1 0 5zm0 17a2.5 2.5 0 1 1 0-5 2.5 2.5 0 0 1 0 5zm-17 0a2.5 2.5 0 1 1 0-5 2.5 2.5 0 0 1 0 5z"/></svg>',
    circle: '<svg viewBox="0 0 28 28" aria-hidden="true"><circle cx="14" cy="14" r="8.5" fill="none" stroke="currentColor" stroke-width="2"/></svg>',
    fib: '<svg viewBox="0 0 28 28" aria-hidden="true"><path d="M4.5 5a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3zM2 6.5A2.5 2.5 0 0 1 6.95 6H24v1H6.95A2.5 2.5 0 0 1 2 6.5zm2.5 8.5a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3zM2 16.5a2.5 2.5 0 0 1 4.95-.5h13.1a2.5 2.5 0 1 1 0 1H6.95A2.5 2.5 0 0 1 2 16.5zm18 1.5a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5zm-15.5 3a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3zM2 22.5a2.5 2.5 0 0 1 4.95-.5H24v1H6.95A2.5 2.5 0 0 1 2 22.5z"/></svg>',
    measure: '<svg viewBox="0 0 28 28" aria-hidden="true"><path d="M4.5 24a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3zM2 22.5a2.5 2.5 0 0 0 4.95.5H24v-1H6.95A2.5 2.5 0 0 0 2 22.5zm2.5-8.5a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3zM2 12.5a2.5 2.5 0 0 0 4.95.5h13.1a2.5 2.5 0 1 0 0-1H6.95A2.5 2.5 0 0 0 2 12.5zM22.5 14a2.5 2.5 0 1 1 0-5 2.5 2.5 0 0 1 0 5zM4.5 8a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3zM2 6.5A2.5 2.5 0 0 0 6.95 7H24V6H6.95A2.5 2.5 0 0 0 2 6.5z"/></svg>',
    text: '<svg viewBox="0 0 28 28" aria-hidden="true"><path d="M8 6.5c0-.28.22-.5.5-.5H14v16h-2v1h5v-1h-2V6h5.5c.28 0 .5.22.5.5V9h1V6.5c0-.83-.67-1.5-1.5-1.5h-12C7.67 5 7 5.67 7 6.5V9h1z"/></svg>',
    arrow: '<svg viewBox="0 0 28 28" aria-hidden="true"><path d="M11 10.5a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0zm4 7a1.5 1.5 0 1 1 3 0 1.5 1.5 0 0 1-3 0zm11-8.8V13h1V7h-6v1h4.3l-7.42 7.41a2.49 2.49 0 0 0-2.76 0l-3.53-3.53a2.5 2.5 0 1 0-4.17 0L1 18.29l.7.71 6.42-6.41a2.49 2.49 0 0 0 2.76 0l3.53 3.53a2.5 2.5 0 1 0 4.17 0z"/></svg>',
  };
  Object.assign(paths, {
    cursor: '<svg viewBox="0 0 28 28" aria-hidden="true"><g fill="currentColor"><path d="M18 15h8v-1h-8z"/><path d="M14 18v8h1v-8zM14 3v8h1V3zM3 15h8v-1H3z"/></g></svg>',
    line: '<svg viewBox="0 0 28 28" aria-hidden="true"><g fill="currentColor" fill-rule="nonzero"><path d="M7.354 21.354l14-14-.707-.707-14 14z"/><path d="M22.5 7c.828 0 1.5-.672 1.5-1.5S23.328 4 22.5 4 21 4.672 21 5.5 21.672 7 22.5 7zm0 1c-1.381 0-2.5-1.119-2.5-2.5S21.119 3 22.5 3 25 4.119 25 5.5 23.881 8 22.5 8zM5.5 24c.828 0 1.5-.672 1.5-1.5S6.328 21 5.5 21 4 21.672 4 22.5 4.672 24 5.5 24zm0 1C4.119 25 3 23.881 3 22.5S4.119 20 5.5 20 8 21.119 8 22.5 6.881 25 5.5 25z"/></g></svg>',
    fib: '<svg viewBox="0 0 28 28" aria-hidden="true"><g fill="currentColor" fill-rule="nonzero"><path d="M3 5h22V4H3zM3 17h22v-1H3zM3 11h19.5v-1H3zM5.5 23H25v-1H5.5z"/><path d="M3.5 24c.828 0 1.5-.672 1.5-1.5S4.328 21 3.5 21 2 21.672 2 22.5 2.672 24 3.5 24zm0 1C2.119 25 1 23.881 1 22.5S2.119 20 3.5 20 6 21.119 6 22.5 4.881 25 3.5 25zm21-13c.828 0 1.5-.672 1.5-1.5S25.328 9 24.5 9s-1.5.672-1.5 1.5.672 1.5 1.5 1.5zm0 1c-1.381 0-2.5-1.119-2.5-2.5S23.119 8 24.5 8 27 9.119 27 10.5 25.881 13 24.5 13z"/></g></svg>',
    vline: '<svg viewBox="0 0 28 28" aria-hidden="true"><g fill="currentColor" fill-rule="nonzero"><path d="M15 12.5V4h-1v8.5zM14 16.5V25h1v-8.5z"/><path d="M14.5 16c.828 0 1.5-.672 1.5-1.5s-.672-1.5-1.5-1.5-1.5.672-1.5 1.5.672 1.5 1.5 1.5zm0 1c-1.381 0-2.5-1.119-2.5-2.5s1.119-2.5 2.5-2.5 2.5 1.119 2.5 2.5-1.119 2.5-2.5 2.5z"/></g></svg>',
    measure: '<svg viewBox="0 0 28 28" aria-hidden="true"><path fill="currentColor" d="M5.5 20c1.2 0 2.22.86 2.45 2H25v1H7.95a2.5 2.5 0 1 1-2.45-3m0 1a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3M25 18H5v-1h20zm-11-4h3v1h-4V9h1zM5.5 4c1.2 0 2.22.86 2.45 2H25v1H7.95A2.5 2.5 0 1 1 5.5 4m0 1a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3"/></svg>',
    arrow: '<svg viewBox="0 0 28 28" aria-hidden="true"><g fill="currentColor"><path fill-rule="nonzero" d="M7.354 21.354l14-14-.707-.707-14 14z"/><path d="m21 7-8 3 5 5z"/><path fill-rule="nonzero" d="M22.5 7c.828 0 1.5-.672 1.5-1.5S23.328 4 22.5 4 21 4.672 21 5.5 21.672 7 22.5 7zm0 1c-1.381 0-2.5-1.119-2.5-2.5S21.119 3 22.5 3 25 4.119 25 5.5 23.881 8 22.5 8zM5.5 24c.828 0 1.5-.672 1.5-1.5S6.328 21 5.5 21 4 21.672 4 22.5 4.672 24 5.5 24zm0 1C4.119 25 3 23.881 3 22.5S4.119 20 5.5 20 8 21.119 8 22.5 6.881 25 5.5 25z"/></g></svg>',
    hline: '<svg viewBox="0 0 28 28" aria-hidden="true"><g fill="currentColor" fill-rule="nonzero"><path d="M4 15h8.5v-1H4zM16.5 15H25v-1h-8.5z"/><path d="M14.5 16c.828 0 1.5-.672 1.5-1.5s-.672-1.5-1.5-1.5-1.5.672-1.5 1.5.672 1.5 1.5 1.5zm0 1c-1.381 0-2.5-1.119-2.5-2.5s1.119-2.5 2.5-2.5 2.5 1.119 2.5 2.5-1.119 2.5-2.5 2.5z"/></g></svg>',
    path: '<svg viewBox="0 0 28 28" aria-hidden="true"><path fill="currentColor" d="M11 10.5a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0zm4 7a1.5 1.5 0 1 1 3 0 1.5 1.5 0 0 1-3 0zm11-8.8V13h1V7h-6v1h4.3l-7.42 7.41a2.49 2.49 0 0 0-2.76 0l-3.53-3.53a2.5 2.5 0 1 0-4.17 0L1 18.29l.7.71 6.42-6.41a2.49 2.49 0 0 0 2.76 0l3.53 3.53a2.5 2.5 0 1 0 4.17 0z"/></svg>',
  });
  Object.assign(paths, {
    hray: '<svg viewBox="0 0 28 28" aria-hidden="true"><g fill="currentColor" fill-rule="nonzero"><path d="M8.5 15h16.5v-1h-16.5z"/><path d="M6.5 16c.828 0 1.5-.672 1.5-1.5s-.672-1.5-1.5-1.5-1.5.672-1.5 1.5.672 1.5 1.5 1.5zm0 1c-1.381 0-2.5-1.119-2.5-2.5s1.119-2.5 2.5-2.5 2.5 1.119 2.5 2.5-1.119 2.5-2.5 2.5z"/></g></svg>',
    long: '<svg viewBox="0 0 28 28" aria-hidden="true"><path fill="currentColor" fill-rule="evenodd" clip-rule="evenodd" d="M4.5 5a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3zM2 6.5A2.5 2.5 0 0 1 6.95 6H24v1H6.95A2.5 2.5 0 0 1 2 6.5zM4.5 15a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3zM2 16.5a2.5 2.5 0 0 1 4.95-.5h13.1a2.5 2.5 0 1 1 0 1H6.95A2.5 2.5 0 0 1 2 16.5zM22.5 15a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3zm-18 6a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3zM2 22.5a2.5 2.5 0 0 1 4.95-.5H24v1H6.95A2.5 2.5 0 0 1 2 22.5z"/><path fill="currentColor" fill-rule="evenodd" clip-rule="evenodd" d="M22.4 8.94l-1.39.63-.41-.91 1.39-.63.41.91zm-4 1.8l-1.39.63-.41-.91 1.39-.63.41.91zm-4 1.8l-1.4.63-.4-.91 1.39-.63.41.91zm-4 1.8l-1.4.63-.4-.91 1.39-.63.41.91z"/></svg>',
    short: '<svg viewBox="0 0 28 28" aria-hidden="true"><path fill="currentColor" fill-rule="evenodd" clip-rule="evenodd" d="M4.5 24a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3zM2 22.5a2.5 2.5 0 0 0 4.95.5H24v-1H6.95a2.5 2.5 0 0 0-4.95.5zM4.5 14a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3zM2 12.5a2.5 2.5 0 0 0 4.95.5h13.1a2.5 2.5 0 1 0 0-1H6.95a2.5 2.5 0 0 0-4.95.5zM22.5 14a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3zm-18-6a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3zM2 6.5a2.5 2.5 0 0 0 4.95.5H24V6H6.95A2.5 2.5 0 0 0 2 6.5z"/><path fill="currentColor" fill-rule="evenodd" clip-rule="evenodd" d="M22.4 20.06l-1.39-.63-.41.91 1.39.63.41-.91zm-4-1.8l-1.39-.63-.41.91 1.39.63.41-.91zm-4-1.8l-1.4-.63-.4.91 1.39.63.41-.91zm-4-1.8L9 14.03l-.4.91 1.39.63.41-.91z"/></svg>',
  });
  return paths[name] || materialIcon(name);
};
const TIMEFRAME_PIN_KEY = "qg:pinned-timeframes:v1";
const pinnedTimeframes = (() => {
  try {
    const saved = JSON.parse(localStorage.getItem(TIMEFRAME_PIN_KEY) || "null");
    if (Array.isArray(saved)) {
      const valid = [...new Set(saved.map(Number))].filter((seconds) =>
        TF.some((item) => item.s === seconds),
      );
      if (valid.length) return valid;
    }
  } catch {}
  return [5, 30, 60];
})();
const navigationItems = [
  ["dashboard", "Dashboard", "dashboardBtn"],
  ["exportCandles", "FARAZ Exporter", "candleExportBtn"],
  ["candlestick_chart", "Chart", "chartNavBtn"],
  ["tune", "Indicator settings", "indicatorBtn"],
  ["layers", "Object tree", "objectTreeBtn"],
  ["notifications", "Alert", "alertBtn"],
  ["history", "Trading history", "historyBtn"],
  ["terminal", "Logs", "navLogs"],
  ["settings", "Chart settings", "settingsNavBtn"],
  ["account_circle", "User profile", "profileBtn"],
];
const state = {
  inventory: [],
  file: null,
  raw: [],
  data: [],
  chartRender: null,
  pointerIsPanning: false,
  tf: restoredTimeframe(localStorage, TF),
  tool: "cursor",
  drawings: [],
  draft: null,
  history: [],
  hover: null,
  theme: "light",
  chartTimeFormat: "compact",
  magnet: false,
  drawingsVisible: true,
  drawingsLocked: false,
  treeSelectedIds: [],
  objectFolders: [],
  collapsedObjectFolders: [],
    indicator: {
    enabled: false,
    results: null,
    loading: false,
    settings: null,
    calculationKey: null,
      hitBoxes: [],
      objects: [],
      objectMap: new Map(),
      selectedObjectId: null,
      activity: [],
      lastCalculation: null,
  },
};
const TEHRAN = "Asia/Tehran";
const OBJECT_TREE_KEY = "qg:object-tree:v1";
try {
  const storedTree = JSON.parse(localStorage.getItem(OBJECT_TREE_KEY) || "{}");
  state.objectFolders = Array.isArray(storedTree.folders)
    ? storedTree.folders.filter((folder) => folder?.id && folder?.name)
    : [];
  state.collapsedObjectFolders = Array.isArray(storedTree.collapsed)
    ? storedTree.collapsed
    : [];
} catch {}
function saveObjectTreePreferences() {
  localStorage.setItem(OBJECT_TREE_KEY, JSON.stringify({
    folders: state.objectFolders,
    collapsed: state.collapsedObjectFolders,
  }));
}
const tehranDateTime = new Intl.DateTimeFormat("en-CA", {
  timeZone: TEHRAN,
  year: "numeric",
  month: "2-digit",
  day: "2-digit",
  hour: "2-digit",
  minute: "2-digit",
  second: "2-digit",
  hourCycle: "h23",
});
const tehranTick = new Intl.DateTimeFormat("en-GB", {
  timeZone: TEHRAN,
  month: "short",
  day: "2-digit",
  hour: "2-digit",
  minute: "2-digit",
  second: "2-digit",
  hourCycle: "h23",
});
function formatTehran(time, axis = false) {
  const date = new Date(Number(time) * 1000);
  return (axis ? tehranTick : tehranDateTime).format(date).replace(",", "");
}
function formatChartAxisTime(time) {
  const parts = tehranDateTime
    .formatToParts(new Date(Number(time) * 1000))
    .reduce((output, part) => ((output[part.type] = part.value), output), {});
  const monthName = new Intl.DateTimeFormat("en-US", {
    timeZone: TEHRAN,
    month: "short",
  }).format(new Date(Number(time) * 1000));
  const hhmm = `${parts.hour}:${parts.minute}`;
  if (state.chartTimeFormat === "time") return `${hhmm}:${parts.second}`;
  if (state.chartTimeFormat === "numeric") return `${parts.day}/${parts.month} ${hhmm}`;
  if (state.chartTimeFormat === "full")
    return `${parts.year}-${parts.month}-${parts.day} ${hhmm}:${parts.second}`;
  return `${parts.day} ${monthName} ${hhmm}`;
}
function parseTehranInput(value) {
  const m = value.match(
    /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})(?::(\d{2}))?$/,
  );
  if (!m) return NaN;
  return Math.floor(
    (Date.UTC(+m[1], +m[2] - 1, +m[3], +m[4], +m[5], +(m[6] || 0)) - 12600000) /
      1000,
  );
}
function inputFromTehran(time) {
  if (!Number.isFinite(Number(time))) {
    log.chart.warn("INVALID_TIME_FOR_TEHRAN_INPUT", { time });
    return "";
  }
  const parts = tehranDateTime
    .formatToParts(new Date(Number(time) * 1000))
    .reduce((o, p) => ((o[p.type] = p.value), o), {});
  if (!parts.year || !parts.month || !parts.day) {
    log.chart.error("TEHRAN_DATE_PARTS_MISSING", new Error("Date formatter returned incomplete parts"), { time, parts });
    return "";
  }
  return `${parts.year}-${parts.month}-${parts.day}T${parts.hour}:${parts.minute}:${parts.second}`;
}

document.querySelector("#app").innerHTML = `<main class="app">
 <header class="topbar">
 <div class="topbar-scroll">
 <div class="topbar-left"><button class="control symbol-control" id="symbolBtn" aria-label="Select symbol">FXCM:USOIL ${materialIcon("expand_more")}</button><div class="divider"></div><div class="timeframes" aria-label="Pinned timeframes"></div></div>
 <div class="top-drawing-tools" aria-label="Drawing tools. Drag to reorder, or use Alt plus Left or Right Arrow."></div>
 <div class="top-actions"><button class="icon-btn" id="undoBtn" title="Undo" aria-label="Undo">${materialIcon("undo")}</button><button class="icon-btn" id="redoBtn" title="Redo" aria-label="Redo">${materialIcon("redo")}</button><button class="icon-btn" id="hideAllBtn" title="Hide drawings" aria-label="Hide drawings" aria-pressed="false">${materialIcon("visibility")}</button><div class="divider"></div><button class="icon-btn" id="fullscreenBtn" title="Full screen" aria-label="Full screen">${materialIcon("fullscreen")}</button><button class="icon-btn" id="reloadIndicatorBtn" title="Reload indicator cache" aria-label="Reload indicator cache">${materialIcon("refresh")}</button><button class="icon-btn" id="exportDataBtn" title="Export data" aria-label="Export data">${materialIcon("download")}</button><button class="icon-btn" id="gotoBtn" title="Go to date" aria-label="Go to date">${materialIcon("event")}</button></div></div></header>
 <section class="workspace"><aside class="leftbar" aria-label="Workspace navigation">${navigationItems.map(([name, label, id]) => `<button class="tool nav-item ${id === "chartNavBtn" ? "active" : ""}" id="${id}" data-label="${label}" title="${label}" aria-label="${label}">${id === "candleExportBtn" ? icon(name, 18) : materialIcon(name)}</button>`).join("")}</aside>
 <div class="chart-shell"><div id="chart" class="chart"></div><canvas id="draw" class="drawing-layer"></canvas><div class="chart-head"><div class="instrument"><span id="chartSymbol">—</span><span class="badge" id="chartTf">1m</span></div><div class="ohlc" aria-label="Open high low close"><span>O <b id="o">—</b></span><span>H <b id="h">—</b></span><span>L <b id="l">—</b></span><span>C <b id="c">—</b></span></div></div><div id="loading" class="loading"><div class="loader-card"><div class="spinner"></div><div class="progress" id="progress">Loading market data...</div></div></div></div></section>
 <footer class="statusbar" aria-label="Workstation status"><div class="status-cluster status-runtime" aria-label="Runtime status"><button class="status-group status-health" id="healthStatus" type="button" data-state="healthy" title="Application health"><i class="dot" aria-hidden="true"></i><b id="healthLabel">Healthy</b></button><button class="status-group status-state status-indicator" id="indicatorStatusFooter" type="button" data-state="inactive" title="Open indicator settings" aria-label="Open indicator settings"><i class="dot" aria-hidden="true"></i><b>Indicator</b></button><span class="status-group status-state status-cache" id="cacheStatusFooter" data-state="idle" title="No indicator calculation source yet"><i class="dot" aria-hidden="true"></i><b>Cache</b></span><span class="status-group status-state status-faraz" id="farazStatusFooter" data-state="inactive" title="FARAZ session is not configured"><i class="dot" aria-hidden="true"></i><b>FARAZ</b></span></div><span class="status-separator" aria-hidden="true"></span><div class="status-cluster status-market" aria-label="Visible chart range"><span class="status-group status-data" title="Candle count for the selected chart timeframe"><span id="candleCount">0 candles</span></span><span class="status-group status-range" title="First and last candle in local system time"><span>From <time id="chartFrom">—</time></span><span>To <time id="chartTo">—</time></span></span></div><span class="status-separator" aria-hidden="true"></span><time class="status-clock" id="clock" title="Local workstation time"></time></footer></main>
 <div id="symbolMenu" class="popover symbol-menu hidden"><div class="searchbox">${icon("search", 17)}<input id="symbolSearch" placeholder="Search local symbols"></div><div id="symbolList"></div></div>
 <div id="gotoModal" class="modal-backdrop hidden"><div class="modal goto-dialog" role="dialog" aria-modal="true" aria-labelledby="gotoTitle"><div class="modal-title"><span id="gotoTitle">Go to date and time</span><button class="icon-btn modal-close" aria-label="Close">${icon("close")}</button></div><p>Jump to an exact candle in Tehran time.</p><div class="field"><label>Tehran date & time</label><button class="date-field" id="gotoPickerButton"><b id="gotoInputDisplay">Select date & time</b>${icon("calendar",16)}</button><input type="hidden" id="gotoInput"></div><div class="modal-actions"><button class="btn modal-close">Cancel</button><button class="btn primary" id="gotoApply">Go to candle</button></div></div></div>
 <div id="chartSettings" class="settings-backdrop hidden"><section class="settings-panel modern-chart-settings" role="dialog" aria-modal="true" aria-labelledby="chartSettingsTitle"><header><div class="settings-title-icon">${icon("chartSettings",20)}</div><div><strong id="chartSettingsTitle">Chart settings</strong><small>Display, scales and interaction</small></div><button id="closeSettings" aria-label="Close">${icon("close",18)}</button></header><div class="settings-body"><div class="settings-section"><h3>Canvas</h3><div class="color-grid"><label>Background<input id="backgroundColor" type="color" value="#ffffff"></label><label>Axis text<input id="axisTextColor" type="color" value="#5f636e"></label></div></div><div class="settings-section"><h3>Candles</h3><div class="color-grid"><label>Bullish<input id="upColor" type="color" value="#089981"></label><label>Bearish<input id="downColor" type="color" value="#f23645"></label><label>Wick up<input id="wickUpColor" type="color" value="#089981"></label><label>Wick down<input id="wickDownColor" type="color" value="#f23645"></label></div></div><div class="settings-section"><h3>Time and scales</h3><label class="settings-select"><span><b>Time format</b><small>Applied to the bottom chart axis</small></span><select id="timeFormat"><option value="compact">DD MMM HH:mm</option><option value="numeric">DD/MM HH:mm</option><option value="time">HH:mm:ss</option><option value="full">YYYY-MM-DD HH:mm:ss</option></select></label><label class="settings-toggle"><span><b>Price scale border</b><small>Right axis divider</small></span><input id="priceBorderEnabled" type="checkbox" checked></label><label class="settings-toggle"><span><b>Time scale border</b><small>Bottom axis divider</small></span><input id="timeBorderEnabled" type="checkbox" checked></label></div><div class="settings-section"><h3>Interaction</h3><label class="settings-toggle"><span><b>Crosshair</b><small>Show precise tracking guides</small></span><input id="crosshairEnabled" type="checkbox" checked></label><label class="settings-toggle"><span><b>Unlimited zoom out</b><small>Compress the full available history</small></span><input id="unlimitedZoom" type="checkbox" checked></label><button id="resetChartSettings" class="settings-reset">Restore defaults</button></div></div></section></div><div id="toast" class="toast hidden"><span id="toastMessage"></span><button id="toastClose" type="button" aria-label="Close notification">${icon("close", 16)}</button></div><div id="errorLogModal" class="modal-backdrop error-log-backdrop hidden"><section class="modal error-log-dialog" role="dialog" aria-modal="true" aria-labelledby="errorLogTitle"><header class="modal-title"><div><strong id="errorLogTitle">Error log</strong><small id="errorLogSummary">No errors recorded</small></div><button id="closeErrorLog" class="icon-btn" type="button" aria-label="Close error log">${icon("close", 18)}</button></header><div id="errorLogList" class="error-log-list"></div><footer class="modal-actions"><button id="copyErrorLogs" class="btn primary" type="button">Copy all errors</button></footer></section></div>`;

const $ = (s) => document.querySelector(s);
const $$ = (s) => [...document.querySelectorAll(s)];
const escapeHtml = (value) => String(value ?? "").replace(/[&<>"']/g, (character) => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
})[character]);
function errorLogText() {
  return runtimeErrors.map((entry) => {
    const { scope, time, level, event, error, stack, recordedAt, ...details } = entry;
    return [
      `[${formatSystemDateTime(recordedAt)}] ${scope} • ${level} • ${event}`,
      error ? `Error: ${error}` : "",
      Object.keys(details).length ? `Details: ${JSON.stringify(details, null, 2)}` : "",
      stack ? `Stack:\n${stack}` : "",
    ].filter(Boolean).join("\n");
  }).join("\n\n────────────────────────────────\n\n");
}
function renderErrorLog() {
  const list = $("#errorLogList");
  $("#errorLogSummary").textContent = runtimeErrors.length
    ? `${runtimeErrors.length} recorded error${runtimeErrors.length === 1 ? "" : "s"}`
    : "No errors recorded";
  list.innerHTML = runtimeErrors.length ? runtimeErrors.map((entry) => {
    const { scope, level, event, error, stack, recordedAt, time, ...details } = entry;
    const detailText = Object.keys(details).length ? JSON.stringify(details, null, 2) : "No additional details.";
    return `<article class="error-log-entry"><header><span>${escapeHtml(scope)}</span><time>${escapeHtml(formatSystemDateTime(recordedAt))}</time></header><strong>${escapeHtml(humanizeEvent(event))}</strong>${error ? `<p>${escapeHtml(error)}</p>` : ""}<pre>${escapeHtml(detailText)}${stack ? `\n\n${escapeHtml(stack)}` : ""}</pre></article>`;
  }).join("") : '<div class="error-log-empty">No application errors have been recorded in this session.</div>';
}
function closeErrorLog() { $("#errorLogModal").classList.add("hidden"); }
$("#healthStatus").onclick = () => { renderErrorLog(); $("#errorLogModal").classList.remove("hidden"); };
$("#closeErrorLog").onclick = closeErrorLog;
$("#errorLogModal").onclick = (event) => { if (event.target === $("#errorLogModal")) closeErrorLog(); };
$("#copyErrorLogs").onclick = async () => {
  const text = errorLogText();
  if (!text) return toast("No errors to copy", "info");
  try {
    await navigator.clipboard.writeText(text);
    toast("Error log copied", "success");
  } catch (error) {
    log.chart.error("ERROR_LOG_COPY_FAILED", error);
    toast("Unable to copy the error log", "error");
  }
};
refreshRuntimeHealth();
function renderDrawingToolbar(focusTool) {
  const toolbar = $(".top-drawing-tools");
  if (!toolbar) return;
  const reorderEnabled = !window.matchMedia("(max-width: 760px)").matches;
  toolbar.innerHTML = drawingTools.map((id) => {
    const label = drawingToolById.get(id);
    const reorderHint = reorderEnabled ? ". Drag to reorder; Alt plus Left or Right Arrow also reorders." : "";
    return `<button class="tool ${state.tool === id ? "active" : ""}" type="button" draggable="${reorderEnabled}" data-tool="${id}" data-drawing-tool="${id}" data-label="${label}" title="${label}" aria-label="${label}${reorderHint}">${stitchDrawingIcon(id)}</button>`;
  }).join("");
  if (focusTool) toolbar.querySelector(`[data-drawing-tool="${focusTool}"]`)?.focus();
}
renderDrawingToolbar();
const WIDTH_LEVELS = [0.25, 0.5, 0.75, 1, 1.5, 2, 3];
function widthLevelOptions(defaultPx) {
  const closestLevel = WIDTH_LEVELS.reduce(
    (best, value, index) =>
      Math.abs(value - defaultPx) < Math.abs(WIDTH_LEVELS[best] - defaultPx) ? index : best,
    0,
  );
  return WIDTH_LEVELS.map(
    (value, index) =>
      `<option value="${value}"${index === closestLevel ? " selected" : ""}>${value}</option>`,
  ).join("");
}
function widthRow(id, label, defaultPx) {
  return `<div class="setting-row style-width-row"><label>${label}</label><select id="${id}">${widthLevelOptions(defaultPx)}</select></div>`;
}
function lineStyleRow(id, defaultValue) {
  return `<div class="setting-row"><label>Line style</label><select id="${id}"><option value="solid"${defaultValue === "solid" ? " selected" : ""}>Solid</option><option value="dash"${defaultValue === "dash" ? " selected" : ""}>Dashed</option><option value="dot"${defaultValue === "dot" ? " selected" : ""}>Dotted</option></select></div>`;
}
function fontSizeRow(id, label, defaultPx) {
  return `<label class="range-label"><span>${label} <b id="${id}Value">${defaultPx}px</b></span><input id="${id}" type="range" min="8" max="28" value="${defaultPx}"></label>`;
}
function rangeRow(id, label, min, max, defaultValue, unit = "") {
  return `<label class="range-label"><span>${label} <b id="${id}Value">${defaultValue}${unit}</b></span><input id="${id}" type="range" min="${min}" max="${max}" value="${defaultValue}"></label>`;
}
function swatchRow(entries) {
  return `<div class="style-grid">${entries
    .map(([id, label, , value]) => `<label>${label}<input id="${id}" type="color" value="${value}"></label>`)
    .join("")}</div>`;
}
function appearancePopup(key, title, summary, rows, resetIds = []) {
  const conciseTitle = title.replace(/\s+(appearance|color)$/i, "");
  return `<div class="appearance-control">
    <button type="button" class="appearance-trigger" data-appearance-open="${key}" aria-expanded="false" aria-controls="appearance-${key}">
      <span><b>${conciseTitle}</b></span><span class="appearance-preview" data-appearance-preview="${key}"></span>
    </button>
    <div id="appearance-${key}" class="appearance-popup-backdrop hidden" data-appearance-popup="${key}">
      <section class="appearance-popup" role="dialog" aria-modal="true" aria-labelledby="appearance-${key}-title">
        <header><div><strong id="appearance-${key}-title">${conciseTitle}</strong></div><button type="button" data-appearance-close aria-label="Close appearance settings">${icon("close", 17)}</button></header>
        <div class="appearance-popup-body">${rows.join("")}</div>
        <footer><button type="button" class="style-reset-btn" data-style-reset="${resetIds.join(",")}">${icon("refresh", 14)} Reset</button><button type="button" class="primary" data-appearance-close>Done</button></footer>
      </section>
    </div>
  </div>`;
}
function styleModule(key, title, rows, resetIds = []) {
  const reset = resetIds.length
    ? `<button type="button" class="style-reset-btn" data-style-reset="${resetIds.join(",")}" title="Reset to defaults">${icon("refresh", 14)}</button>`
    : "";
  return `<section class="style-module" data-style-module="${key}"><header class="style-module-header"><strong>${title}</strong><div class="style-module-actions">${reset}<span class="style-chevron">${icon("chevron", 14)}</span></div></header><div class="style-module-body">${rows.join("")}</div></section>`;
}
document.body.insertAdjacentHTML(
  "beforeend",
  `<div id="drawingToolbar" class="drawing-toolbar hidden"><span class="toolbar-grip">⋮⋮</span><input id="objectText" class="object-text hidden" type="text" maxlength="24" aria-label="Object text"><select id="objectSize" class="object-size hidden" aria-label="Text size"><option>9</option><option>11</option><option>13</option><option>14</option><option>16</option></select><input id="strokeColor" type="color" value="#2962ff" title="Line color" aria-label="Line color and opacity"><input id="fillColor" type="color" value="#2962ff" title="Fill color" aria-label="Fill color and opacity"><select id="lineWidth" title="Line width"><option value="0.5">0.5</option><option value="0.75">0.75</option><option value="1">1</option><option value="2">2</option></select><select id="lineStyle" title="Line style"><option value="solid">Solid</option><option value="dash">Dashed</option><option value="dot">Dotted</option></select><label class="opacity-control hidden"><span>Opacity</span><input id="fillOpacity" type="range" min="0" max="1" step="0.01" value="0.1"></label><button id="lockDrawing" title="Lock" aria-label="Lock drawing">${icon("lock", 18)}</button><button id="copyDrawing" title="Duplicate" aria-label="Duplicate drawing">${icon("copy", 18)}</button><button id="deleteDrawing" class="danger" title="Delete" aria-label="Delete drawing">${icon("trash", 18)}</button></div>`,
);
const chart = createChart($("#chart"), {
  layout: {
    background: { color: "#ffffff" },
    textColor: "#5f636e",
    fontSize: 10,
    attributionLogo: false,
    fontFamily:
      'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif',
  },
  grid: { vertLines: { visible: false }, horzLines: { visible: false } },
  crosshair: {
    mode: CrosshairMode.Normal,
    vertLine: {
      color: "#9598a1",
      width: 1,
      style: 3,
      labelBackgroundColor: "#2962ff",
    },
    horzLine: {
      color: "#9598a1",
      width: 1,
      style: 3,
      labelBackgroundColor: "#2962ff",
    },
  },
  rightPriceScale: {
    borderColor: "#e4e7ed",
    scaleMargins: { top: 0.12, bottom: 0.1 },
  },
  timeScale: {
    borderColor: "#e4e7ed",
    timeVisible: true,
    secondsVisible: true,
    rightOffset: 8,
    barSpacing: 8,
    minBarSpacing: 0.01,
  },
  handleScroll: {
    mouseWheel: true,
    pressedMouseMove: true,
    horzTouchDrag: true,
    vertTouchDrag: true,
  },
  handleScale: { axisPressedMouseMove: true, mouseWheel: true, pinch: true },
  kineticScroll: { mouse: true, touch: true },
  localization: { locale: "en-US" },
});
const series = chart.addSeries(CandlestickSeries, {
  upColor: "#089981",
  downColor: "#f23645",
  borderUpColor: "#089981",
  borderDownColor: "#f23645",
  wickUpColor: "#089981",
  wickDownColor: "#f23645",
  priceLineVisible: false,
  lastValueVisible: false,
});
const CHART_SETTINGS_KEY = "market-canvas:chart-settings:v1";
const chartSettingsDefaults = {
  theme: "light",
  backgroundColor: "#ffffff",
  axisTextColor: "#5f636e",
  upColor: "#089981",
  downColor: "#f23645",
  wickUpColor: "#089981",
  wickDownColor: "#f23645",
  crosshair: true,
  priceBorder: true,
  timeBorder: true,
  watermark: false,
  unlimitedZoom: true,
  timeFormat: "compact",
};
let chartSettings = { ...chartSettingsDefaults };
try {
  chartSettings = {
    ...chartSettingsDefaults,
    ...JSON.parse(localStorage.getItem(CHART_SETTINGS_KEY) || "{}"),
  };
} catch {
  chartSettings = { ...chartSettingsDefaults };
}

function applyChartSettings(persist = true) {
  state.theme = "light";
  chartSettings.theme = "light";
  document.documentElement.dataset.theme = "light";
  state.chartTimeFormat = chartSettings.timeFormat;
  chart.applyOptions({
    layout: {
      background: { color: chartSettings.backgroundColor },
      textColor: chartSettings.axisTextColor,
      fontSize: 10,
      fontFamily:
        'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif',
    },
    crosshair: {
      mode: chartSettings.crosshair
        ? CrosshairMode.Normal
        : CrosshairMode.Hidden,
      vertLine: { visible: chartSettings.crosshair },
      horzLine: { visible: chartSettings.crosshair },
    },
    rightPriceScale: {
      borderVisible: chartSettings.priceBorder,
      borderColor: "#e4e7ed",
    },
    timeScale: {
      borderVisible: chartSettings.timeBorder,
      borderColor: "#e4e7ed",
      minBarSpacing: chartSettings.unlimitedZoom ? 0.01 : 0.5,
      tickMarkFormatter: (time) => formatChartAxisTime(time),
    },
  });
  series.applyOptions({
    upColor: chartSettings.upColor,
    downColor: chartSettings.downColor,
    borderUpColor: chartSettings.upColor,
    borderDownColor: chartSettings.downColor,
    wickUpColor: chartSettings.wickUpColor,
    wickDownColor: chartSettings.wickDownColor,
    priceLineVisible: false,
    lastValueVisible: false,
  });
  const watermark = $("#chartWatermark");
  if (watermark) {
    watermark.textContent = state.file ? parseName(state.file) : "QG";
    watermark.classList.toggle("hidden", !chartSettings.watermark);
  }
  if (persist)
    localStorage.setItem(CHART_SETTINGS_KEY, JSON.stringify(chartSettings));
  requestAnimationFrame(drawAll);
}
document.body.insertAdjacentHTML(
  "beforeend",
  `<aside id="objectTree" class="object-tree hidden"><header><div><strong>Object Tree</strong><small id="objectCount">0 objects</small></div><div class="tree-header-actions"><button id="newObjectFolder" title="New folder" aria-label="New folder">${icon("folder", 17)}${icon("plus", 12)}</button><button id="closeObjectTree" title="Close object tree" aria-label="Close object tree">${icon("close", 18)}</button></div></header><div class="object-search searchbox">${icon("search", 15)}<input id="objectSearch" placeholder="Search objects" aria-label="Search objects"></div><div id="objectList" class="object-list" aria-label="Object tree"></div><footer><button id="lockAllObjects" title="Lock selected, or all when no objects are selected">${icon("lock", 15)}<span>Lock all</span></button><button id="deleteAllObjects" class="danger" title="Delete selected, or all when no objects are selected">${icon("trash", 15)}<span>Delete all</span></button></footer></aside>`,
);
chartSettings.watermark = false;
document.body.insertAdjacentHTML(
  "beforeend",
  `<div id="indicatorModal" class="indicator-backdrop hidden"><section class="indicator-panel"><header><div class="indicator-logo">${icon("layers", 20)}</div><div><strong>Reaction Detector</strong><small>Unified algorithm • v9.1.0</small></div><label class="master-switch"><input id="indicatorEnabled" type="checkbox"><span></span></label><button id="closeIndicator" class="indicator-close">${icon("close", 18)}</button></header><nav><button class="active" data-indicator-tab="inputs">Inputs</button><button data-indicator-tab="style">Style</button><button data-indicator-tab="labels">Numbers</button></nav><div class="indicator-body"><div class="indicator-tab active" data-indicator-page="inputs"><div class="setting-block"><label>Reaction direction</label><div class="segment"><button class="active" data-direction="bullish">Bullish</button><button data-direction="bearish">Bearish</button><button data-direction="both">Both</button></div></div><div class="setting-grid"><div><label>From • Tehran</label><input id="indicatorFrom" type="datetime-local" step="1"></div><div><label>To • Tehran</label><input id="indicatorTo" type="datetime-local" step="1"></div></div><div class="setting-block"><label>Calculation timeframe</label><select id="indicatorTf"><option value="follow">Follow chart timeframe</option>${TF.map((t) => `<option value="${t.s}">${t.l}</option>`).join("")}</select><p>Follow mode recalculates automatically whenever the chart timeframe changes.</p></div><div class="engine-note"><span>${icon("info", 16)}</span><div><strong>Exact Python engine</strong><p>Uses Reaction-detection-new.py with 1-second intrabar chronology and exact Decimal comparisons.</p></div></div></div><div class="indicator-tab" data-indicator-page="style"><div class="style-card bullish-style"><div class="style-title"><i></i><strong>Bullish boxes</strong></div><div class="style-row"><label>Fill<input id="bullFill" type="color" value="#22ab94"></label><label>Border<input id="bullBorder" type="color" value="#089981"></label></div><label class="range-label"><span>Fill opacity <b id="bullOpacityValue">14%</b></span><input id="bullOpacity" type="range" min="0" max="100" value="14"></label><label class="range-label"><span>Border width <b id="bullWidthValue">1px</b></span><input id="bullWidth" type="range" min="0.25" max="3" step="0.25" value="1"></label></div><div class="style-card bearish-style"><div class="style-title"><i></i><strong>Bearish boxes</strong></div><div class="style-row"><label>Fill<input id="bearFill" type="color" value="#f23645"></label><label>Border<input id="bearBorder" type="color" value="#d9273e"></label></div><label class="range-label"><span>Fill opacity <b id="bearOpacityValue">14%</b></span><input id="bearOpacity" type="range" min="0" max="100" value="14"></label><label class="range-label"><span>Border width <b id="bearWidthValue">1px</b></span><input id="bearWidth" type="range" min="0.25" max="3" step="0.25" value="1"></label></div></div><div class="indicator-tab" data-indicator-page="labels"><label class="toggle-row"><div><strong>Number reactions</strong><small>Show sequence labels above/below every box</small></div><input id="numberEnabled" type="checkbox" checked><span></span></label><div class="setting-block"><label>Numbering sequence</label><select id="numberMode"><option value="continuous">Continuous across selected range</option><option value="reset">Restart from 1 after every Reset</option></select></div><div class="setting-grid three"><label>Distance<input id="numberGap" type="number" min="2" max="80" value="12"><small>pixels</small></label><label>Color<input id="numberColor" type="color" value="#131722"></label><label>Weight<select id="numberWeight"><option value="500">Medium</option><option value="600" selected>Semibold</option><option value="700">Bold</option></select></label></div><label class="range-label"><span>Text size <b id="numberSizeValue">12px</b></span><input id="numberSize" type="range" min="9" max="24" value="12"></label></div></div><footer><div id="indicatorStatus"><i></i><span>Indicator is disabled</span></div><button id="cancelIndicator">Cancel</button><button id="applyIndicator" class="primary">Apply & calculate</button></footer></section></div>`,
);
$("#indicatorModal header small").textContent = "Unified algorithm • v9.2.1";
$("#indicatorModal").innerHTML = `
<section class="indicator-panel" role="dialog" aria-modal="true" aria-labelledby="indicatorTitle">
  <header class="indicator-header"><div class="indicator-logo">${icon("layers", 20)}</div><div class="indicator-heading"><strong id="indicatorTitle">QG Indicator</strong><small></small></div><label class="master-switch" title="Enable indicator"><input id="indicatorEnabled" type="checkbox"><span></span></label><button id="closeIndicator" class="indicator-close" aria-label="Close">${icon("close", 18)}</button></header>
  <nav class="indicator-tabs"><button class="active" data-indicator-tab="inputs">Inputs</button><button data-indicator-tab="style">Appearance</button><button data-indicator-tab="labels">Labels</button><button data-indicator-tab="info">Info <span id="infoBadge">0</span></button></nav>
  <div class="indicator-body">
    <div class="indicator-tab active" data-indicator-page="inputs"><div class="section-heading"><strong>Detection setup</strong><span>Calculation settings</span></div><div class="setting-block"><label>Reaction direction</label><div class="segment"><button class="active" data-direction="bullish">Bullish</button><button data-direction="bearish">Bearish</button><button data-direction="both">Both</button></div></div><div class="range-card"><div class="range-card-title">${icon("calendar", 17)}<div><strong>Analysis range</strong></div></div><div class="setting-grid time-grid"><label><span>From</span><button class="date-field" id="indicatorFromButton" type="button"><b id="indicatorFromDisplay">Select start</b>${icon("calendar", 16)}</button><input id="indicatorFrom" type="hidden"></label><div class="range-arrow">→</div><label><span>To</span><button class="date-field" id="indicatorToButton" type="button"><b id="indicatorToDisplay">Select end</b>${icon("calendar", 16)}</button><input id="indicatorTo" type="hidden"></label></div><div class="range-shortcuts"><button data-range="visible">Visible chart</button><button data-range="all">All available data</button></div></div><div class="setting-block"><label>Calculation timeframe</label><select id="indicatorTf"><option value="follow">Follow chart timeframe</option>${TF.map((t) => `<option value="${t.s}">${t.l}</option>`).join("")}</select><p></p></div><div class="engine-note"><span>${icon("info", 16)}</span><div><strong>Exact calculation pipeline</strong><p>Reaction → Blue Line → A → S using Python Decimal and lower-timeframe chronology.</p></div></div></div>
    <div class="indicator-tab" data-indicator-page="style"><div class="section-heading"><strong>Box appearance</strong><span>Box styles apply instantly</span></div><label class="toggle-row"><div><strong>Show Blue Lines</strong><small>Calculate the selected direction when you Apply</small></div><input id="blueLineEnabled" type="checkbox" checked><span></span></label><div class="style-card bullish-style"><div class="style-title"><i></i><div><strong>Bullish boxes</strong><small>Light mint • distinct from candles</small></div></div><div class="style-row"><label>Fill<input id="bullFill" type="color" value="#86efac"></label><label>Border<input id="bullBorder" type="color" value="#22c55e"></label></div><label class="range-label"><span>Fill opacity <b id="bullOpacityValue">20%</b></span><input id="bullOpacity" type="range" min="0" max="100" value="20"></label><label class="range-label"><span>Border width <b id="bullWidthValue">0.25px</b></span><input id="bullWidth" type="range" min="0.25" max="3" step="0.25" value="0.25"></label></div><div class="style-card bearish-style"><div class="style-title"><i></i><div><strong>Bearish boxes</strong><small>Light coral • distinct from candles</small></div></div><div class="style-row"><label>Fill<input id="bearFill" type="color" value="#fca5a5"></label><label>Border<input id="bearBorder" type="color" value="#ef4444"></label></div><label class="range-label"><span>Fill opacity <b id="bearOpacityValue">20%</b></span><input id="bearOpacity" type="range" min="0" max="100" value="20"></label><label class="range-label"><span>Border width <b id="bearWidthValue">0.25px</b></span><input id="bearWidth" type="range" min="0.25" max="3" step="0.25" value="0.25"></label></div></div>
    <div class="indicator-tab" data-indicator-page="labels"><div class="section-heading"><strong>Reaction labels</strong><span>Live visual settings</span></div><label class="toggle-row"><div><strong>Number reactions</strong><small>Bullish below • Bearish above</small></div><input id="numberEnabled" type="checkbox" checked><span></span></label><div class="setting-block"><label>Numbering sequence</label><select id="numberMode"><option value="continuous">Continuous across selected range</option><option value="reset">Restart from 1 after every Reset</option></select></div><div class="setting-grid three"><label>Distance<input id="numberGap" type="number" min="2" max="80" value="12"><small>px</small></label><label>Color<input id="numberColor" type="color" value="#334155"></label><label>Weight<select id="numberWeight"><option value="500">Medium</option><option value="600" selected>Semibold</option><option value="700">Bold</option></select></label></div><label class="range-label"><span>Text size <b id="numberSizeValue">12px</b></span><input id="numberSize" type="range" min="9" max="24" value="12"></label></div>
    <div class="indicator-tab" data-indicator-page="info"><div class="section-heading"><strong>Detection summary</strong><span>Expand a group for complete details</span></div><div id="indicatorInfo" class="indicator-info"><div class="info-empty">Run the pipeline to see Reaction, Blue Line, A, S, Reset, range and engine details.</div></div></div>
  </div>
  <footer><div id="indicatorStatus"><i></i><span>Indicator is disabled</span></div><button id="cancelIndicator">Close</button><button id="applyIndicator" class="primary">Apply & calculate</button></footer>
  <div id="indicatorLoading" class="indicator-loading hidden" role="dialog" aria-modal="true" aria-labelledby="calculationTitle"><section class="calculation-card"><header class="progress-header"><div><span class="calculation-kicker">LOCAL PYTHON PIPELINE</span><strong id="calculationTitle">Calculation in progress</strong></div><span id="calculationPercent">0%</span></header><div class="calculation-overview"><p id="calculationStage">Preparing calculation…</p><div class="calculation-track"><i id="calculationBar"></i></div><div class="calculation-summary"><span id="calculationRemaining">Waiting for pipeline stages</span><time id="calculationElapsed">Elapsed 0.0s</time></div></div><div class="calculation-scroll-region" tabindex="0" aria-label="Calculation stages"><section class="calculation-stage-wrap"><header><div><strong>Processing stages</strong><small>Exact timing updates in place</small></div><span id="calculationStageCount">0 planned</span></header><ol id="calculationSteps" aria-label="Calculation stages" aria-live="polite"></ol></section></div></section></div>
  <div id="dateTimePicker" class="datetime-picker hidden"><div class="picker-card"><header><div><strong id="pickerTitle">Select date & time</strong><small>Asia/Tehran</small></div><button id="pickerClose" aria-label="Close">${icon("close", 17)}</button></header><section class="calendar-section"><div class="picker-value-row"><span id="pickerDateValue"></span></div><div class="month-nav"><strong id="pickerMonth"></strong><div><button id="pickerPrev" aria-label="Previous month">‹</button><button id="pickerNext" aria-label="Next month">›</button></div></div><div class="weekday-row"><span>Mo</span><span>Tu</span><span>We</span><span>Th</span><span>Fr</span><span>Sa</span><span>Su</span></div><div id="pickerDays" class="picker-days"></div></section><section class="time-section" aria-label="Time"><div class="time-selects"><label><span>Hour</span><select id="pickerHour" aria-label="Hour">${Array.from({ length: 24 }, (_, i) => `<option value="${String(i).padStart(2, "0")}">${String(i).padStart(2, "0")}</option>`).join("")}</select></label><label><span>Minute</span><select id="pickerMinute" aria-label="Minute">${Array.from({ length: 60 }, (_, i) => `<option value="${String(i).padStart(2, "0")}">${String(i).padStart(2, "0")}</option>`).join("")}</select></label><label><span>Second</span><select id="pickerSecond" aria-label="Second">${Array.from({ length: 60 }, (_, i) => `<option value="${String(i).padStart(2, "0")}">${String(i).padStart(2, "0")}</option>`).join("")}</select></label></div></section><footer><button id="pickerToday">Today</button><span></span><button id="pickerCancel">Cancel</button><button id="pickerSave" class="primary">Apply</button></footer></div></div>
</section>`;
// Shared FARAZ-style picker is used by indicator ranges and Go To.
// These dialogs must live at the document root.  Keeping them inside the
// resizable/pinnable side panel makes fixed positioning relative to that panel
// in some browser layouts, which can clip the calculation card at the viewport
// edge instead of centering it.
document.body.append($("#dateTimePicker"), $("#indicatorLoading"));
$(".picker-card").setAttribute("role", "dialog");
$(".picker-card").setAttribute("aria-modal", "false");
$(".picker-card").setAttribute("aria-labelledby", "pickerTitle");
$("#indicatorTitle").textContent = "QG Indicator";
$(".indicator-heading small").remove();
$(".indicator-logo")?.remove();
$(".indicator-tabs").innerHTML =
  '<button class="active" data-indicator-tab="inputs">Inputs</button><button data-indicator-tab="style">Style</button><button data-indicator-tab="info">Info <span id="infoBadge">0</span></button>';
$("#indicatorModal .indicator-header").insertAdjacentHTML(
  "beforeend",
  `<button id="pinIndicatorPanel" class="panel-pin" type="button" title="Pin panel" aria-label="Pin indicator settings" aria-pressed="false">${icon("pin", 17)}</button>`,
);
$(".master-switch").after($("#pinIndicatorPanel"));
$("#objectTree header").insertAdjacentHTML(
  "beforeend",
  `<button id="pinObjectTree" class="panel-pin" type="button" title="Pin panel" aria-label="Pin object tree" aria-pressed="false">${icon("pin", 17)}</button>`,
);
$("#objectTree").setAttribute("role", "dialog");
$("#objectTree").setAttribute("aria-label", "Object tree");
$("#objectTree").setAttribute("aria-modal", "true");
$(".workspace").append($("#objectTree"), $("#indicatorModal"));
let candleExportController = null;
function selectWorkspaceNavigation(activeId) {
  $$(".leftbar .nav-item").forEach((button) => {
    const active = button.id === activeId;
    button.classList.toggle("active", active);
    button.setAttribute("aria-pressed", String(active));
  });
}
function showChartWorkspace() {
  candleExportController?.close();
  selectWorkspaceNavigation("chartNavBtn");
  setDrawingToolsActive(true);
  requestAnimationFrame(resize);
}
function chartWorkspaceActive() {
  return !$(".chart-shell").classList.contains("candle-export-active");
}
candleExportController = initCandleExport({
  root: $(".chart-shell"),
  icon,
  toast,
  getDefaults: () => ({ symbol: state.file?.symbol || "", timeframeSeconds: state.tf }),
  inputFromTehran,
  parseTehranInput,
  setDateTimeValue,
  openDateTimePicker,
  onConnectionChange: (connected, status) => {
    const footer = $("#farazStatusFooter");
    footer.dataset.state = connected ? "active" : "inactive";
    footer.title = connected ? `FARAZ session active · ${status.host || "faraz.io"}` : "FARAZ session is not configured";
  },
});
$("#candleExportBtn").onclick = () => {
  closeSidePanel($("#objectTree"));
  closeSidePanel($("#indicatorModal"));
  selectWorkspaceNavigation("candleExportBtn");
  setDrawingToolsActive(false);
  candleExportController.open();
};
$("#chartNavBtn").onclick = showChartWorkspace;
$(".indicator-body").innerHTML = `
  <div class="indicator-tab active" data-indicator-page="inputs">
    <section class="tv-section"><h3>Detection</h3>
      <div class="setting-row trend-row"><label>Trend <small>Required</small></label><div class="segment compact trend-segment"><button aria-pressed="false" data-direction="bullish">Bullish</button><button aria-pressed="false" data-direction="bearish">Bearish</button></div></div>
      <div class="setting-row"><label>Analysis timeframe</label><select id="indicatorTf"><option value="follow">Follow chart timeframe</option>${TF.map((t) => `<option value="${t.s}">${t.l}</option>`).join("")}</select></div>
    </section>
    <section class="tv-section"><h3>Range</h3>
      <div class="range-dates"><label><span>From • Asia/Tehran</span><button class="date-field" id="indicatorFromButton"><b id="indicatorFromDisplay">Select start</b>${icon("calendar", 16)}</button><input id="indicatorFrom" type="hidden"></label><label><span>To • Asia/Tehran</span><button class="date-field" id="indicatorToButton"><b id="indicatorToDisplay">Select end</b>${icon("calendar", 16)}</button><input id="indicatorTo" type="hidden"></label></div>
      <div class="range-shortcuts"><button data-range="all">All available data</button><button data-range="visible">Visible chart</button></div>
    </section>
    <section class="tv-section"><h3>Modules</h3>
      ${[
        ["reactionVisible", "Reaction", ""],
        ["blueLineEnabled", "Blue Line", ""],
        ["aVisible", "A zone", ""],
        ["sVisible", "S module", ""],
        ["eVisible", "E module", ""],
        ["stopAllVisible", "StopAll module", ""],
        ["eStopVisible", "E stop lines", ""],
        ["orderVisible", "Order reactions", ""],
        ["orderStopVisible", "Order stops", ""],
      ].map(([id, title]) => `<label class="module-row"><span><b>${title}</b></span><input id="${id}" class="module-toggle-input" type="checkbox" aria-label="Toggle ${title}"${id === "eStopVisible" ? "" : " checked"}><span class="module-toggle" aria-hidden="true"></span></label>`).join("")}
    </section>
  </div>
  <div class="indicator-tab" data-indicator-page="style">
    <section class="style-group" data-style-group="foundation"><button type="button" class="style-group-header" aria-expanded="true"><span><strong>Foundation</strong><small>Reaction • Blue Line • A</small></span><span class="style-group-chevron">${icon("chevron", 16)}</span></button><div class="style-group-body">
      ${styleModule("reaction", "Bullish reaction", [appearancePopup("reaction-bull", "Bullish reaction appearance", "Fill, opacity and border", [swatchRow([["bullFill", "Fill", "color", "#86efac"], ["bullBorder", "Border", "color", "#22c55e"]]), rangeRow("bullOpacity", "Fill opacity", 0, 100, 20, "%"), widthRow("bullWidth", "Border width", 0.25), lineStyleRow("bullLineStyle", "solid")], ["bullFill", "bullBorder", "bullOpacity", "bullWidth", "bullLineStyle"])])}
      ${styleModule("reaction-bear", "Bearish reaction", [appearancePopup("reaction-bear", "Bearish reaction appearance", "Fill, opacity and border", [swatchRow([["bearFill", "Fill", "color", "#fca5a5"], ["bearBorder", "Border", "color", "#ef4444"]]), rangeRow("bearOpacity", "Fill opacity", 0, 100, 20, "%"), widthRow("bearWidth", "Border width", 0.25), lineStyleRow("bearLineStyle", "solid")], ["bearFill", "bearBorder", "bearOpacity", "bearWidth", "bearLineStyle"])])}
      ${styleModule("blue", "Blue Line", [appearancePopup("blue", "Blue Line appearance", "Color, width and line style", [swatchRow([["blueColor", "Line color", "color", "#06b6d4"]]), rangeRow("blueOpacity", "Opacity", 0, 100, 100, "%"), widthRow("blueWidth", "Line width", 3), lineStyleRow("blueLineStyle", "solid")], ["blueColor", "blueOpacity", "blueWidth", "blueLineStyle"])])}
      ${styleModule("a", "A label", [appearancePopup("a", "A label color", "Label color", [swatchRow([["aColor", "Label color", "color", "#7c3aed"]])], ["aColor"]), fontSizeRow("aSize", "Font size", 12), rangeRow("aGap", "Distance from candle", 4, 32, 12, "px")])}
    </div>
    </section>
    <section class="style-group" data-style-group="se"><button type="button" class="style-group-header" aria-expanded="true"><span><strong>S & E behaviors</strong><small>S • E</small></span><span class="style-group-chevron">${icon("chevron", 16)}</span></button><div class="style-group-body">
      ${styleModule("s", "S labels", [appearancePopup("s", "S label colors", "Bullish and bearish colors", [swatchRow([["sBullColor", "Bullish", "color", "#2563eb"], ["sBearColor", "Bearish", "color", "#f23645"]])], ["sBullColor", "sBearColor"]), fontSizeRow("sSize", "Font size", 12), rangeRow("sGap", "Distance from candle", 4, 32, 12, "px")])}
      ${styleModule("e", "E labels", [appearancePopup("e", "E label colors", "Blue and red family colors", [swatchRow([["eBlueColor", "Blue family", "color", "#1e3a8a"], ["eRedColor", "Red family", "color", "#7f1d1d"]])], ["eBlueColor", "eRedColor"]), fontSizeRow("eSize", "Font size", 12), rangeRow("eGap", "Distance from candle", 4, 32, 12, "px")])}
      ${styleModule("e-stop", "E stop lines", [appearancePopup("e-stop", "E stop line appearance", "Color, width and dotted style", [swatchRow([["eStopColor", "Line color", "color", "#111111"]]), widthRow("eStopWidth", "Line width", 1), lineStyleRow("eStopLineStyle", "dot")], ["eStopColor", "eStopWidth", "eStopLineStyle"])])}
    </div>
    </section>
    <section class="style-group" data-style-group="stopall"><button type="button" class="style-group-header" aria-expanded="true"><span><strong>StopAll</strong><small>StopAll</small></span><span class="style-group-chevron">${icon("chevron", 16)}</span></button><div class="style-group-body">
      ${styleModule("stopall", "StopAll marker", [appearancePopup("stopall", "StopAll appearance", "Fill, opacity and border", [swatchRow([["stopAllFill", "Fill", "color", "#ff9800"], ["stopAllBorder", "Border", "color", "#ff9800"]]), rangeRow("stopAllOpacity", "Fill opacity", 0, 100, 20, "%"), widthRow("stopAllWidth", "Border width", 0.25)], ["stopAllFill", "stopAllBorder", "stopAllOpacity", "stopAllWidth"]), fontSizeRow("stopAllSize", "Label font size", 15), rangeRow("stopAllRadius", "Circle radius", 4, 16, 8, "px"), rangeRow("stopAllGap", "Label distance", 4, 32, 16, "px")])}
    </div>
    </section>
    <section class="style-group" data-style-group="order"><button type="button" class="style-group-header" aria-expanded="true"><span><strong>Order reactions</strong><small>Order Reaction</small></span><span class="style-group-chevron">${icon("chevron", 16)}</span></button><div class="style-group-body">
      ${styleModule("order", "Order reaction boxes", [appearancePopup("order", "Order reaction appearance", "Fill, opacity and border", [swatchRow([["orderFill", "Fill", "color", "#d1d3d6"], ["orderColor", "Border", "color", "#8a8f98"]]), rangeRow("orderOpacity", "Fill opacity", 0, 100, 20, "%"), widthRow("orderWidth", "Border width", 0.25), lineStyleRow("orderLineStyle", "solid")], ["orderFill", "orderColor", "orderOpacity", "orderWidth", "orderLineStyle"])])}
      ${styleModule("order-stop", "Order stop lines", [appearancePopup("order-stop", "Order stop line appearance", "Color, width and dotted style", [swatchRow([["orderStopColor", "Line color", "color", "#ef4444"]]), widthRow("orderStopWidth", "Line width", 1), lineStyleRow("orderStopLineStyle", "dot")], ["orderStopColor", "orderStopWidth", "orderStopLineStyle"]), `<div class="setting-row"><label>Unbroken stop cap</label><input id="orderStopCap" type="number" min="1" max="200" value="200"></div>`])}
    </div>
    </section>
  </div>
  <div class="indicator-tab" data-indicator-page="info">
    <section class="tv-section">
      <h3>Detection summary</h3>
      <div id="indicatorInfo" class="indicator-info"><div class="info-empty">Run the pipeline to see Reaction, Blue Line, A, S, E, StopAll, range and engine details.</div></div>
    </section>
  </div>`;
$$(".style-module-header").forEach((header) => {
  header.addEventListener("click", (event) => {
    if (event.target.closest("[data-style-reset]")) return;
    header.closest(".style-module").classList.toggle("collapsed");
  });
});
$$(".style-group-header").forEach((header) => {
  header.addEventListener("click", () => {
    const group = header.closest(".style-group");
    const collapsed = group.classList.toggle("collapsed");
    header.setAttribute("aria-expanded", String(!collapsed));
  });
});
function closeAppearancePopup(popup) {
  if (!popup) return;
  popup.classList.add("hidden");
  const key = popup.dataset.appearancePopup;
  const trigger = $(`[data-appearance-open="${key}"]`);
  trigger?.setAttribute("aria-expanded", "false");
  trigger?.focus();
}
function refreshAppearancePreviews() {
  $$("[data-color-input]").forEach((trigger) => {
    const input = $("#" + trigger.dataset.colorInput);
    if (input) trigger.style.setProperty("--swatch", input.value);
  });
  $$("[data-appearance-preview]").forEach((preview) => {
    const popup = $(`[data-appearance-popup="${preview.dataset.appearancePreview}"]`);
    const colors = [...popup.querySelectorAll("input[type='color']")].map((input) => input.value);
    preview.style.background = colors.length > 1
      ? `linear-gradient(135deg, ${colors[0]} 0 50%, ${colors[1]} 50% 100%)`
      : colors[0] || "var(--tv-border)";
  });
}
$$("[data-appearance-open]").forEach((trigger) => {
  trigger.addEventListener("click", () => {
    const popup = $(`[data-appearance-popup="${trigger.dataset.appearanceOpen}"]`);
    document.body.append(popup);
    popup.classList.remove("hidden");
    trigger.setAttribute("aria-expanded", "true");
    popup.querySelector("input, select, button")?.focus();
  });
});
$$("[data-appearance-popup]").forEach((popup) => {
  popup.addEventListener("click", (event) => {
    if (event.target === popup || event.target.closest("[data-appearance-close]"))
      closeAppearancePopup(popup);
  });
});
document.addEventListener("keydown", (event) => {
  const popup = $("[data-appearance-popup]:not(.hidden)");
  if (!popup) return;
  if (event.key === "Escape") {
    event.stopImmediatePropagation();
    closeAppearancePopup(popup);
    return;
  }
  if (event.key !== "Tab") return;
  const focusable = [...popup.querySelectorAll("button:not(:disabled), input:not(:disabled), select:not(:disabled)")];
  if (!focusable.length) return;
  const first = focusable[0], last = focusable.at(-1);
  if (event.shiftKey && document.activeElement === first) {
    event.preventDefault();
    last.focus();
  } else if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault();
    first.focus();
  }
});
refreshAppearancePreviews();
const COLOR_PALETTE = [
  "#ffffff", "#f3f4f6", "#d1d5db", "#9ca3af", "#6b7280", "#4b5563", "#374151", "#1f2937", "#111827", "#000000",
  "#f43f5e", "#f97316", "#fde047", "#4caf50", "#16a34a", "#06b6d4", "#2563eb", "#7c3aed", "#9333ea", "#e91e63",
  "#fecdd3", "#fed7aa", "#fef3c7", "#dcfce7", "#ccfbf1", "#cffafe", "#dbeafe", "#e9d5ff", "#e9d5ff", "#fce7f3",
  "#fda4af", "#fdba74", "#fde68a", "#bbf7d0", "#99f6e4", "#a5f3fc", "#bfdbfe", "#ddd6fe", "#d8b4fe", "#fbcfe8",
  "#fb7185", "#fb923c", "#fcd34d", "#86efac", "#5eead4", "#67e8f9", "#93c5fd", "#c4b5fd", "#c084fc", "#f9a8d4",
  "#f0525d", "#f97316", "#facc15", "#4ade80", "#2dd4bf", "#22d3ee", "#60a5fa", "#a78bfa", "#a855f7", "#f472b6",
  "#ef4444", "#f97316", "#fbbf24", "#22c55e", "#14b8a6", "#06b6d4", "#3b82f6", "#8b5cf6", "#9333ea", "#ec4899",
  "#b91c1c", "#ea580c", "#f59e0b", "#15803d", "#0f766e", "#0891b2", "#1d4ed8", "#6d28d9", "#7e22ce", "#be185d",
  "#7f1d1d", "#c2410c", "#d97706", "#166534", "#115e59", "#0e7490", "#1e3a8a", "#4c1d95", "#581c87", "#9d174d",
];
const COLOR_OPACITY_TARGETS = {
  strokeColor: "fillOpacity",
  fillColor: "fillOpacity",
  bullFill: "bullOpacity",
  bearFill: "bearOpacity",
  stopAllFill: "stopAllOpacity",
  orderFill: "orderOpacity",
  blueColor: "blueOpacity",
};
function colorControlTrigger(input) {
  return input?.parentElement?.querySelector(`[data-color-input="${input.id}"]`) || null;
}
function syncColorControl(input) {
  const trigger = colorControlTrigger(input);
  if (trigger) trigger.style.setProperty("--swatch", input.value);
}
function replaceNativeColorControls() {
  $$("input[type='color']:not([data-native-color])").forEach((input) => {
    if (!input.id || colorControlTrigger(input)) return;
    const trigger = document.createElement("button");
    trigger.type = "button";
    trigger.className = "color-swatch-trigger";
    trigger.dataset.colorInput = input.id;
    trigger.style.setProperty("--swatch", input.value);
    trigger.setAttribute("aria-label", input.getAttribute("aria-label") || input.title || "Choose color");
    trigger.addEventListener("click", (event) => {
      event.preventDefault();
      event.stopPropagation();
      openUniversalColorPicker(input);
    });
    input.classList.add("color-value-input");
    input.tabIndex = -1;
    input.setAttribute("aria-hidden", "true");
    input.insertAdjacentElement("afterend", trigger);
    const label = input.closest("label");
    label?.addEventListener("click", (event) => {
      if (!event.target.closest(`[data-color-input="${input.id}"]`)) event.preventDefault();
    }, true);
    input.addEventListener("input", () => trigger.style.setProperty("--swatch", input.value));
  });
}
document.body.insertAdjacentHTML(
  "beforeend",
  `<section id="qgColorPicker" class="qg-color-picker hidden" role="dialog" aria-modal="false" aria-label="Color and opacity">
    <div class="qg-palette">${COLOR_PALETTE.map((color) => `<button type="button" data-qg-color="${color}" style="--swatch:${color}" aria-label="Use ${color}"></button>`).join("")}</div>
    <label class="qg-custom-color">Custom color<input id="qgNativeColor" data-native-color type="color" value="#2962ff" aria-label="Choose custom color"></label>
    <label class="qg-opacity-row"><span>Opacity</span><input id="qgOpacity" type="range" min="0" max="100" step="1" value="100"><b id="qgOpacityValue">100%</b></label>
  </section>`,
);
let activeColorTarget = null;
let activeOpacityTarget = null;
let colorDrawingSnapshot = null;
let colorDrawingChanged = false;
function beginColorDrawingHistory() {
  if (!colorDrawingSnapshot || colorDrawingChanged) return;
  state.history.push(colorDrawingSnapshot);
  if (state.history.length > 80) state.history.shift();
  state.redo = [];
  colorDrawingChanged = true;
}
function closeUniversalColorPicker(restoreFocus = true) {
  const picker = $("#qgColorPicker");
  if (picker.classList.contains("hidden")) return;
  picker.classList.add("hidden");
  colorControlTrigger(activeColorTarget)?.setAttribute("aria-expanded", "false");
  if (colorDrawingChanged) saveDrawings();
  const trigger = activeColorTarget;
  activeColorTarget = null;
  activeOpacityTarget = null;
  colorDrawingSnapshot = null;
  colorDrawingChanged = false;
  if (restoreFocus) colorControlTrigger(trigger)?.focus();
}
function openUniversalColorPicker(target) {
  activeColorTarget = target;
  const opacityTargetId = COLOR_OPACITY_TARGETS[target.id];
  activeOpacityTarget = opacityTargetId ? $("#" + opacityTargetId) : null;
  colorDrawingSnapshot = selected() || selectedIndicatorObject() ? historySnapshot() : null;
  colorDrawingChanged = false;
  $("#qgNativeColor").value = target.value;
  const opacityValue = activeOpacityTarget
    ? Math.round(Number(activeOpacityTarget.value) * (activeOpacityTarget.max === "1" ? 100 : 1))
    : 100;
  $("#qgOpacity").value = String(opacityValue);
  $("#qgOpacityValue").textContent = `${opacityValue}%`;
  $(".qg-opacity-row").classList.toggle("is-disabled", !activeOpacityTarget);
  $("#qgOpacity").disabled = !activeOpacityTarget;
  $$("[data-qg-color]").forEach((swatch) =>
    swatch.classList.toggle("selected", swatch.dataset.qgColor.toLowerCase() === target.value.toLowerCase()),
  );
  const picker = $("#qgColorPicker"), rect = (colorControlTrigger(target) || target).getBoundingClientRect();
  picker.classList.remove("hidden");
  const width = picker.offsetWidth, height = picker.offsetHeight;
  picker.style.left = `${Math.max(8, Math.min(innerWidth - width - 8, rect.left))}px`;
  picker.style.top = `${Math.max(8, Math.min(innerHeight - height - 8, rect.bottom + 6))}px`;
  colorControlTrigger(target)?.setAttribute("aria-expanded", "true");
  picker.querySelector("[data-qg-color]")?.focus();
}
function previewColor(value) {
  if (!activeColorTarget) return;
  beginColorDrawingHistory();
  activeColorTarget.value = value;
  $("#qgNativeColor").value = value;
  activeColorTarget.dispatchEvent(new Event("input", { bubbles: true }));
  refreshAppearancePreviews();
}
function syncRangeProgress(input) {
  const min = Number(input.min || 0), max = Number(input.max || 100), value = Number(input.value);
  const progress = max > min ? ((value - min) / (max - min)) * 100 : 0;
  input.style.setProperty("--range-progress", `${Math.max(0, Math.min(100, progress))}%`);
}
function initializeRangeProgress() {
  $$("input[type='range']").forEach((input) => {
    syncRangeProgress(input);
    input.addEventListener("input", () => syncRangeProgress(input));
  });
}
function isUniversalColorTarget(target) {
  return target instanceof Element
    ? target.closest('input[type="color"]:not([data-native-color])')
    : null;
}
// A native color input opens before its click handler runs in some browsers.
// Capture pointer input first so every Appearance swatch consistently opens
// the shared picker instead of a platform-specific dialog.
document.addEventListener("pointerdown", (event) => {
  const colorInput = isUniversalColorTarget(event.target);
  if (!colorInput) return;
  event.preventDefault();
  event.stopPropagation();
  openUniversalColorPicker(colorInput);
}, true);
document.addEventListener("keydown", (event) => {
  const colorInput = isUniversalColorTarget(event.target);
  if (!colorInput || !["Enter", " "].includes(event.key)) return;
  event.preventDefault();
  openUniversalColorPicker(colorInput);
});
document.addEventListener("click", (event) => {
  if (isUniversalColorTarget(event.target)) return;
  const swatch = event.target.closest("[data-qg-color]");
  if (swatch) previewColor(swatch.dataset.qgColor);
  else if (!event.target.closest("#qgColorPicker") && !event.target.closest('input[type="color"]'))
    closeUniversalColorPicker(false);
});
replaceNativeColorControls();
initializeRangeProgress();
$("#qgNativeColor").addEventListener("input", (event) => previewColor(event.target.value));
$("#qgOpacity").addEventListener("input", (event) => {
  if (!activeOpacityTarget) return;
  beginColorDrawingHistory();
  const percent = Number(event.target.value);
  $("#qgOpacityValue").textContent = `${percent}%`;
  activeOpacityTarget.value = String(activeOpacityTarget.max === "1" ? percent / 100 : percent);
  activeOpacityTarget.dispatchEvent(new Event("input", { bubbles: true }));
});
$("#qgOpacity").addEventListener("change", () => {
  activeOpacityTarget?.dispatchEvent(new Event("change", { bubbles: true }));
});
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && !$("#qgColorPicker").classList.contains("hidden")) {
    event.stopImmediatePropagation();
    closeUniversalColorPicker();
  }
});
// Keep the compact panel focused on controls; range timezone and module detail
// remain available in the picker / tooltips, not as permanent visual noise.
$$('.range-dates > label > span').forEach((label, index) => {
  label.textContent = index ? 'To' : 'From';
});
$$('.section-help, .module-row small').forEach((node) => node.remove());
$('#indicatorStatus span').textContent = '';
$('#applyIndicator').textContent = 'Apply';
function activateIndicatorTab(target, moveFocus = false) {
  $$('[data-indicator-tab]').forEach((tab) => {
    const active = tab.dataset.indicatorTab === target;
    tab.classList.toggle('active', active);
    tab.setAttribute('aria-selected', String(active));
    tab.tabIndex = active ? 0 : -1;
    if (active && moveFocus) tab.focus();
  });
  $$('[data-indicator-page]').forEach((page) => {
    const active = page.dataset.indicatorPage === target;
    page.classList.toggle('active', active);
    page.hidden = !active;
  });
}
$('.indicator-tabs').setAttribute('role', 'tablist');
$('.indicator-tabs').setAttribute('aria-label', 'Indicator settings');
$$('[data-indicator-tab]').forEach((tab) => {
  const name = tab.dataset.indicatorTab;
  tab.setAttribute('role', 'tab');
  tab.id = `indicator-tab-${name}`;
  tab.setAttribute('aria-controls', `indicator-page-${name}`);
  tab.addEventListener('keydown', (event) => {
    const tabs = $$('[data-indicator-tab]');
    const index = tabs.indexOf(tab);
    let next = index;
    if (event.key === 'ArrowRight') next = (index + 1) % tabs.length;
    else if (event.key === 'ArrowLeft') next = (index - 1 + tabs.length) % tabs.length;
    else if (event.key === 'Home') next = 0;
    else if (event.key === 'End') next = tabs.length - 1;
    else return;
    event.preventDefault();
    activateIndicatorTab(tabs[next].dataset.indicatorTab, true);
  });
});
$$('[data-indicator-page]').forEach((page) => {
  const name = page.dataset.indicatorPage;
  page.setAttribute('role', 'tabpanel');
  page.id = `indicator-page-${name}`;
  page.setAttribute('aria-labelledby', `indicator-tab-${name}`);
});
activateIndicatorTab('inputs');
$$("[data-jump-tab]").forEach((button) => {
  button.addEventListener("click", () => {
    activateIndicatorTab(button.dataset.jumpTab);
  });
});
$$("[data-style-reset]").forEach((button) => {
  button.addEventListener("click", (event) => {
    event.stopPropagation();
    const ids = button.dataset.styleReset.split(",");
    for (const id of ids) {
      const element = $("#" + id);
      if (!element || !(id in indicatorDefaults.controls)) continue;
      const value = indicatorDefaults.controls[id];
      if (element.type === "checkbox") element.checked = Boolean(value);
      else element.value = value;
      element.dispatchEvent(new Event("input", { bubbles: true }));
      element.dispatchEvent(new Event("change", { bubbles: true }));
    }
  });
});
$(".indicator-panel > footer").insertAdjacentHTML("afterbegin", `<div class="template-wrap"><button id="templateBtn" type="button">Templates</button><div id="templateMenu" class="template-menu hidden"><button data-template-action="save">Save as…</button><button data-template-action="default">Reset to default</button><div id="savedTemplates"></div></div></div>`);
const objectTreeBtn = $("#objectTreeBtn");
chart.applyOptions({
  localization: {
    locale: "en-US",
    timeFormatter: (time) => formatTehran(time, false),
  },
  timeScale: { tickMarkFormatter: (time) => formatChartAxisTime(time) },
});

function aggregate(rows, seconds) {
  if (seconds === 1) return rows;
  const out = [];
  let bar = null;
  for (const r of rows) {
    const time = Math.floor(Number(r.time) / seconds) * seconds;
    if (!bar || bar.time !== time) {
      if (bar) out.push(bar);
      bar = {
        time,
        open: +r.open,
        high: +r.high,
        low: +r.low,
        close: +r.close,
      };
    } else {
      bar.high = Math.max(bar.high, +r.high);
      bar.low = Math.min(bar.low, +r.low);
      bar.close = +r.close;
    }
  }
  if (bar) out.push(bar);
  return out;
}
const CHART_LOD_TARGET_CANDLES = 4_000;
const CHART_LOD_BARS_PER_PIXEL = 2;
function viewportIndexRange(range) {
  const first = state.data[0], last = state.data.at(-1);
  if (!first || !last) return null;
  const from = Number(range?.from ?? first.time);
  const to = Number(range?.to ?? last.time);
  const start = Math.max(0, lowerBoundTime(state.data, Math.min(from, to)) - 1);
  const end = Math.min(state.data.length, lowerBoundTime(state.data, Math.max(from, to)) + 1);
  return { start, end: Math.max(start + 1, end) };
}
function renderChartViewport(range, { preserveRange = false, force = false } = {}) {
  const visible = viewportIndexRange(range);
  if (!visible) return;
  const visibleCount = Math.max(1, visible.end - visible.start);
  const stride = chooseLodStride(
    visibleCount,
    Math.max(1, chartElement.clientWidth),
    CHART_LOD_BARS_PER_PIXEL,
  );
  const buffer = Math.max(
    visibleCount,
    Math.ceil((CHART_LOD_TARGET_CANDLES * stride) / 2),
  );
  const start = Math.max(0, visible.start - buffer);
  const end = Math.min(state.data.length, visible.end + buffer);
  const previous = state.chartRender;
  const margin = previous ? Math.floor((previous.end - previous.start) * 0.15) : 0;
  const coverage = previous &&
    visible.start >= previous.start && visible.end <= previous.end &&
    (previous.start === 0 || visible.start >= previous.start + margin) &&
    (previous.end === state.data.length || visible.end <= previous.end - margin);
  if (!force && previous?.stride === stride && coverage) return;
  const display = buildCandleLod(state.data, start, end, stride);
  series.setData(display);
  state.chartRender = { start, end, stride, displayCount: display.length };
  if (preserveRange && range?.from != null && range?.to != null)
    chart.timeScale().setVisibleRange({ from: range.from, to: range.to });
}
let chartViewportFrame = 0,
  chartViewportTimer = 0;
function scheduleChartViewport(delay = 140) {
  if (!state.data.length) return;
  clearTimeout(chartViewportTimer);
  chartViewportTimer = setTimeout(() => {
    if (chartViewportFrame) return;
    chartViewportFrame = requestAnimationFrame(() => {
      chartViewportFrame = 0;
      // Never replace series data while the pointer is still dragging the
      // chart. A stale range would make the viewport jump under the cursor.
      if (state.pointerIsPanning) return;
      renderChartViewport(chart.timeScale().getVisibleRange(), { preserveRange: true });
    });
  }, delay);
}
function sourceCandleAt(time) {
  if (!state.data.length || time == null) return null;
  const index = lowerBoundTime(state.data, Number(time));
  const candidate = state.data[index];
  if (candidate && Number(candidate.time) === Number(time)) return candidate;
  return state.data[Math.max(0, Math.min(state.data.length - 1, index - 1))];
}
function fmt(v) {
  return Number.isFinite(v) ? v.toFixed(3) : "—";
}
function compactCount(value) {
  return new Intl.NumberFormat("en-US", {
    notation: value >= 1000 ? "compact" : "standard",
    maximumFractionDigits: 1,
  }).format(value);
}
function setOHLC(d) {
  if (!d) return;
  const color = Number(d.close) >= Number(d.open) ? "var(--chart-bullish)" : "var(--chart-bearish)";
  [["#o", d.open], ["#h", d.high], ["#l", d.low], ["#c", d.close]].forEach(([selector, value]) => {
    const node = $(selector);
    node.textContent = fmt(value);
    node.style.color = color;
  });
}
function renderTf(fit = true) {
  const started = performance.now();
  // The selected source timeframe already has canonical OHLC candles. Reusing
  // it avoids allocating a second multi-million-candle array on large files.
  state.data = state.tf === sourceTimeframeSeconds()
    ? state.raw
    : aggregate(state.raw, state.tf);
  state.chartRender = null;
  renderChartViewport(null, { force: true });
  $("#chartTf").textContent = TF.find((x) => x.s === state.tf)?.l;
  $("#candleCount").textContent = `${new Intl.NumberFormat("en-US").format(state.data.length)} candles`;
  const firstCandle = state.data.at(0), lastCandle = state.data.at(-1);
  $("#chartFrom").textContent = firstCandle ? formatSystemDateTime(firstCandle.time * 1000) : "—";
  $("#chartTo").textContent = lastCandle ? formatSystemDateTime(lastCandle.time * 1000) : "—";
  chart.applyOptions({
    timeScale: { secondsVisible: state.tf < 60, timeVisible: state.tf < 86400 },
  });
  setOHLC(state.data.at(-1));
  if (fit) chart.timeScale().fitContent();
  drawAll();
  const renderTiming = {
    symbol: state.file?.symbol,
    timeframeSeconds: state.tf,
    sourceCandles: state.raw.length,
    renderedCandles: state.data.length,
    displayCandles: state.chartRender?.displayCount || 0,
    displayStride: state.chartRender?.stride || 1,
    durationMs: Math.round((performance.now() - started) * 100) / 100,
    fitContent: fit,
  };
  window.__QG_PERF__ = { ...(window.__QG_PERF__ || {}), chart: renderTiming };
  log.chart.info("TIMEFRAME_RENDERED", renderTiming);
}
function parseName(item) {
  return item.symbol.replace("_", ":");
}
function sourceTimeframeSeconds(item = state.file) {
  const match = String(item?.timeframe || "").match(/^(\d+)([SMHD])$/i);
  if (!match) return 1;
  const unit = { S: 1, M: 60, H: 3600, D: 86400 }[match[2].toUpperCase()];
  return Number(match[1]) * unit;
}
function timeframeLongLabel(item) {
  const value = Number.parseInt(item.l, 10);
  const unit = item.l.endsWith("s") ? "second" : item.l.endsWith("m") ? "minute" : item.l.endsWith("H") ? "hour" : "day";
  return `${value} ${unit}${value === 1 ? "" : "s"}`;
}
function timeframeGroups() {
  return [
    ["Seconds", TF.filter((item) => item.s < 60)],
    ["Minutes", TF.filter((item) => item.s >= 60 && item.s < 3600)],
    ["Hours", TF.filter((item) => item.s >= 3600 && item.s < 86400)],
    ["Days", TF.filter((item) => item.s >= 86400)],
  ].filter(([, items]) => items.length);
}
function renderTimeframeControls(keepMenuOpen = false) {
  const container = $(".timeframes");
  if (!container) return;
  const minimum = sourceTimeframeSeconds();
  const pinned = [...pinnedTimeframes]
    .sort((left, right) => left - right)
    .map((seconds) => TF.find((item) => item.s === seconds))
    .filter(Boolean);
  container.innerHTML = `${pinned.map((item) => `<button class="tf ${state.tf === item.s ? "active" : ""}" type="button" data-tf="${item.s}" ${item.s < minimum ? "disabled" : ""} aria-pressed="${state.tf === item.s}">${item.l}</button>`).join("")}<button id="timeframeMenuButton" class="timeframe-menu-button ${pinnedTimeframes.includes(state.tf) ? "" : "active"}" type="button" aria-label="Open timeframe menu" aria-haspopup="menu" aria-expanded="${keepMenuOpen}">${materialIcon("expand_more")}</button><div id="timeframeMenu" class="timeframe-menu ${keepMenuOpen ? "" : "hidden"}" role="menu">${timeframeGroups().map(([title, items]) => `<section class="timeframe-group"><h3>${title}</h3>${items.map((item) => `<div class="timeframe-menu-row ${state.tf === item.s ? "selected" : ""}"><button type="button" data-timeframe-select="${item.s}" role="menuitem" ${item.s < minimum ? "disabled" : ""}><span>${timeframeLongLabel(item)}</span><small>${item.l}</small></button><button type="button" class="timeframe-star ${pinnedTimeframes.includes(item.s) ? "active" : ""}" data-timeframe-pin="${item.s}" aria-label="${pinnedTimeframes.includes(item.s) ? "Unpin" : "Pin"} ${timeframeLongLabel(item)}" aria-pressed="${pinnedTimeframes.includes(item.s)}">${materialIcon("star")}</button></div>`).join("")}</section>`).join("")}</div>`;
}
function updateTimeframeAvailability() {
  const minimum = sourceTimeframeSeconds();
  if (state.tf < minimum) state.tf = minimum;
  renderTimeframeControls(!$("#timeframeMenu")?.classList.contains("hidden"));
}
async function loadInventory() {
  log.chart.info("SYMBOL_INVENTORY_REQUESTED");
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 12000);
  let r;
  try {
    r = await fetch("/api/symbols", { signal: controller.signal, cache: "no-store" });
  } finally {
    clearTimeout(timeout);
  }
  if (!r.ok) {
    const error = new Error(`Symbol inventory request failed with HTTP ${r.status}`);
    log.chart.error("SYMBOL_INVENTORY_FAILED", error, { status: r.status });
    throw error;
  }
  state.inventory = await r.json();
  if (!state.inventory.length)
    throw new Error("No valid candle-history JSON files found in input.");
  renderSymbolList();
  log.chart.info("SYMBOL_INVENTORY_LOADED", { symbols: state.inventory.length });
  const remembered = localStorage.getItem("qg:last-symbol");
  await loadFile(
    state.inventory.find((item) => item.id === remembered) || state.inventory[0],
  );
}
async function loadFile(item) {
  const started = performance.now();
  log.chart.info("SYMBOL_LOAD_STARTED", { id: item.id, symbol: item.symbol });
  $("#loading").classList.remove("hidden");
  $("#progress").textContent = `Loading ${item.symbol}…`;
  state.file = item;
  localStorage.setItem("qg:last-symbol", item.id);
  const r = await fetch(`/api/candles?id=${encodeURIComponent(item.id)}`);
  if (!r.ok) throw new Error(await r.text());
  const rows = await r.json();
  if (!Array.isArray(rows) || !rows.length)
    throw new Error("The candle file is empty or invalid.");
  state.raw = rows
    .map((x) => ({
      time: +x.time,
      open: +x.open,
      high: +x.high,
      low: +x.low,
      close: +x.close,
    }))
    .sort((a, b) => a.time - b.time);
  if ($("#rangePreset")) $("#rangePreset").value = "all";
  if ($("#indicatorFrom"))
    setDateTimeValue("#indicatorFrom", inputFromTehran(state.raw[0].time));
  if ($("#indicatorTo"))
    setDateTimeValue("#indicatorTo", inputFromTehran(state.raw.at(-1).time));
  state.history = [];
  state.redo = [];
  state.drawings = [];
  state.indicator.objects = [];
  state.indicator.objectMap = new Map();
  state.indicator.selectedObjectId = null;
  loadDrawings();
  updateTimeframeAvailability();
  $("#symbolBtn").innerHTML = `${parseName(item)} ${materialIcon("expand_more")}`;
  renderSymbolList($("#symbolSearch")?.value || "");
  $("#chartSymbol").textContent = parseName(item);
  renderTf();
  $("#loading").classList.add("hidden");
  log.chart.info("SYMBOL_LOAD_COMPLETED", {
    id: item.id,
    symbol: item.symbol,
    rawCandles: state.raw.length,
    durationMs: Math.round((performance.now() - started) * 100) / 100,
  });
  toast(`${parseName(item)} loaded • ${state.raw.length.toLocaleString()} candles`, "success");
}
function renderSymbolList(filter = "") {
  const q = filter.toLowerCase();
  const matching = state.inventory.filter((item) =>
    [item.symbol, item.id, item.timeframe].some((value) => String(value || "").toLowerCase().includes(q)),
  );
  const groups = new Map();
  for (const item of matching) {
    const key = parseName(item);
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(item);
  }
  const itemRow = (item) => {
    const selected = state.file?.id === item.id;
    const displayName = parseName(item);
    return `<button class="symbol-row ${selected ? "selected" : ""}" type="button" data-id="${encodeURIComponent(item.id)}" aria-pressed="${selected}"><span class="symbol-avatar" aria-hidden="true">${escapeHtml(displayName.split(":").at(-1).slice(0, 2))}</span><span class="symbol-meta"><span class="symbol-title"><strong>${escapeHtml(displayName)}</strong><em>${escapeHtml(item.timeframe)}</em></span><span class="symbol-range"><small><b>FROM</b>${escapeHtml(item.from)}</small><i>→</i><small><b>TO</b>${escapeHtml(item.to)}</small></span><span class="symbol-stats"><span>${Number(item.count || 0).toLocaleString()} candles</span><span>${(item.bytes / 1048576).toFixed(1)} MB</span></span></span>${selected ? `<span class="symbol-selected" aria-label="Selected">${materialIcon("check")}</span>` : ""}</button>`;
  };
  $("#symbolList").innerHTML = [...groups.entries()].map(([symbol, items]) =>
    `<section class="symbol-group"><h3>${escapeHtml(symbol)}<small>${items.length} file${items.length === 1 ? "" : "s"}</small></h3>${items.map(itemRow).join("")}</section>`,
  ).join("") || '<div class="symbol-empty">No matching symbols</div>';
}
function toast(msg, type = "auto") {
  const el = $("#toast");
  const resolvedType = type === "auto"
    ? (/error|failed|invalid|outside|unable/i.test(msg)
        ? "error"
        : /loaded|updated|restored|saved|moved|enabled|recalculated|plotted|completed/i.test(msg)
          ? "success"
          : "info")
    : type;
  $("#toastMessage").textContent = msg;
  el.className = `toast toast-${resolvedType}`;
  el.setAttribute("role", resolvedType === "error" ? "alert" : "status");
  el.classList.remove("hidden");
  toast.remaining = 3000;
  toast.deadline = Date.now() + toast.remaining;
  clearTimeout(toast.t);
  toast.t = setTimeout(() => el.classList.add("hidden"), toast.remaining);
}
$("#toast").addEventListener("mouseenter", () => {
  if ($("#toast").classList.contains("hidden")) return;
  toast.remaining = Math.max(0, (toast.deadline || Date.now()) - Date.now());
  clearTimeout(toast.t);
});
$("#toast").addEventListener("mouseleave", () => {
  if ($("#toast").classList.contains("hidden")) return;
  toast.remaining = Math.max(750, toast.remaining || 3000);
  toast.deadline = Date.now() + toast.remaining;
  clearTimeout(toast.t);
  toast.t = setTimeout(() => $("#toast").classList.add("hidden"), toast.remaining);
});
$("#toastClose").onclick = () => {
  clearTimeout(toast.t);
  $("#toast").classList.add("hidden");
};

chart.subscribeCrosshairMove((p) => {
  if (!p.time) {
    setOHLC(state.data.at(-1));
    return;
  }
  const d = sourceCandleAt(p.time) || p.seriesData.get(series);
  if (d) setOHLC(d);
});
function selectTimeframe(seconds, label) {
  if (seconds < sourceTimeframeSeconds()) {
    toast(`The selected dataset cannot display below ${state.file.timeframe}`, "error");
    return;
  }
  state.tf = seconds;
  try { localStorage.setItem(CHART_TIMEFRAME_KEY, String(seconds)); }
  catch (error) { log.chart.warn("TIMEFRAME_PERSIST_FAILED", { message: error.message }); }
  renderTimeframeControls(false);
  renderTf();
  toast(`Chart timeframe changed to ${label}`, "info");
  if (state.indicator.enabled && $("#indicatorTf").value === "follow") calculateIndicator();
}
renderTimeframeControls();
$(".timeframes").onclick = (event) => {
  event.stopPropagation();
  const pinnedButton = event.target.closest("[data-tf]");
  if (pinnedButton) {
    selectTimeframe(Number(pinnedButton.dataset.tf), pinnedButton.textContent.trim());
    return;
  }
  if (event.target.closest("#timeframeMenuButton")) {
    const menu = $("#timeframeMenu");
    const open = menu.classList.contains("hidden");
    menu.classList.toggle("hidden", !open);
    $("#timeframeMenuButton").setAttribute("aria-expanded", String(open));
    return;
  }
  const star = event.target.closest("[data-timeframe-pin]");
  if (star) {
    const seconds = Number(star.dataset.timeframePin);
    const index = pinnedTimeframes.indexOf(seconds);
    if (index >= 0) pinnedTimeframes.splice(index, 1);
    else pinnedTimeframes.push(seconds);
    pinnedTimeframes.sort((left, right) => left - right);
    localStorage.setItem(TIMEFRAME_PIN_KEY, JSON.stringify(pinnedTimeframes));
    renderTimeframeControls(true);
    return;
  }
  const menuItem = event.target.closest("[data-timeframe-select]");
  if (menuItem)
    selectTimeframe(
      Number(menuItem.dataset.timeframeSelect),
      menuItem.querySelector("span")?.textContent || menuItem.textContent.trim(),
    );
};
$("#symbolBtn").onclick = () => $("#symbolMenu").classList.toggle("hidden");
document.addEventListener("click", (e) => {
  if (!e.target.closest(".timeframes")) {
    $("#timeframeMenu")?.classList.add("hidden");
    $("#timeframeMenuButton")?.setAttribute("aria-expanded", "false");
  }
  if (e.target.closest("#symbolBtn,#symbolMenu")) return;
  $("#symbolMenu").classList.add("hidden");
});
$("#symbolSearch").oninput = (e) => renderSymbolList(e.target.value);
$("#symbolList").onclick = async (e) => {
  const row = e.target.closest("[data-id]");
  if (!row) return;
  $("#symbolMenu").classList.add("hidden");
  await loadFile(
    state.inventory.find((i) => encodeURIComponent(i.id) === row.dataset.id),
  );
};
$("#fullscreenBtn").onclick = async () => {
  try {
    if (!document.fullscreenElement)
      await document.documentElement.requestFullscreen();
    else await document.exitFullscreen();
    toast(document.fullscreenElement ? "Fullscreen enabled" : "Fullscreen closed", "success");
    log.chart.info("FULLSCREEN_CHANGED", { enabled: Boolean(document.fullscreenElement) });
  } catch (error) {
    log.chart.error("FULLSCREEN_CHANGE_FAILED", error);
    toast("Full screen is not available in this browser context");
  }
};
document.addEventListener("fullscreenchange", () => {
  $("#fullscreenBtn").classList.toggle("active", !!document.fullscreenElement);
  $("#fullscreenBtn").title = document.fullscreenElement
    ? "Exit full screen"
    : "Full screen";
});
async function exportChartData() {
  if (!state.indicator.results) {
    toast("No calculated indicator results are available to export", "error");
    return;
  }
  try {
    const context = state.indicator.resultContext || {};
    const calculationRangeCandles = state.raw.filter((candle) =>
      Number.isFinite(context.from) && Number.isFinite(context.to)
        ? candle.time >= context.from && candle.time <= context.to
        : true,
    );
    const outcome = await saveManualReview(state.indicator.results, {
      exportedAt: new Date().toISOString(),
      timezone: "Asia/Tehran",
      calculation: context,
      currentChart: {
        source: state.file,
        timeframe: state.tf,
        // Export both existing candle caches as-is; never fetch or aggregate here.
        sourceCandles: state.raw,
        candles: state.data,
        calculationRangeCandles,
      },
      settings: state.indicator.settings,
      chartSettings,
      ...historySnapshot(),
    }, window, (message) => toast(message, "info"));
    if (outcome === "cancelled") return;
    log.chart.info("INDICATOR_REVIEW_EXPORTED", { outcome });
    if (outcome === "saved") toast("Indicator review HTML saved", "success");
  } catch (error) {
    log.chart.error("INDICATOR_REVIEW_EXPORT_FAILED", error);
    toast(`Could not export indicator review: ${error.message}`, "error");
  }
}
$("#exportDataBtn").onclick = exportChartData;
$("#gotoBtn").onclick = () => {
  setDateTimeValue(
    "#gotoInput",
    inputFromTehran(state.data.at(-1)?.time || Date.now() / 1000),
  );
  openDateTimePicker("#gotoInput", true);
};
$("#gotoPickerButton").onclick = () => openDateTimePicker("#gotoInput");
$$(".modal-close").forEach(
  (x) => (x.onclick = () => $("#gotoModal").classList.add("hidden")),
);
$("#gotoApply").onclick = () => {
  const t = parseTehranInput($("#gotoInput").value);
  if (!Number.isFinite(t)) {
    toast("Enter a valid Tehran date and time");
    return;
  }
  const first = state.data[0]?.time,
    last = state.data.at(-1)?.time;
  if (t < first || t > last) {
    toast("That time is outside the available data range");
    return;
  }
  let lo = 0,
    hi = state.data.length - 1;
  while (lo < hi) {
    const m = (lo + hi) >> 1;
    if (state.data[m].time < t) lo = m + 1;
    else hi = m;
  }
  chart
    .timeScale()
    .setVisibleLogicalRange({
      from: Math.max(0, lo - 80),
      to: Math.min(state.data.length - 1, lo + 80),
    });
  $("#gotoModal").classList.add("hidden");
  toast("Moved to the nearest candle (Tehran)");
};
if ($("#shotBtn")) $("#shotBtn").onclick = () => {
  const a = document.createElement("a");
  a.download = `${state.file?.symbol || "chart"}-${TF.find((x) => x.s === state.tf)?.l}.png`;
  a.href = chart.takeScreenshot().toDataURL();
  a.click();
};
$("#settingsNavBtn").onclick = () =>
  $("#chartSettings").classList.remove("hidden");
$("#navLogs").onclick = () =>
  toast("Global application logs are reserved for a future panel", "info");
$("#closeSettings").onclick = () =>
  $("#chartSettings").classList.add("hidden");
$("#chartSettings").onclick = (event) => {
  if (event.target === $("#chartSettings"))
    $("#chartSettings").classList.add("hidden");
};
function syncChartSettingsForm() {
  $("#backgroundColor").value = chartSettings.backgroundColor;
  $("#axisTextColor").value = chartSettings.axisTextColor;
  $("#upColor").value = chartSettings.upColor;
  $("#downColor").value = chartSettings.downColor;
  $("#wickUpColor").value = chartSettings.wickUpColor;
  $("#wickDownColor").value = chartSettings.wickDownColor;
  $("#crosshairEnabled").checked = chartSettings.crosshair;
  $("#priceBorderEnabled").checked = chartSettings.priceBorder;
  $("#timeBorderEnabled").checked = chartSettings.timeBorder;
  $("#unlimitedZoom").checked = chartSettings.unlimitedZoom;
  $("#timeFormat").value = chartSettings.timeFormat;
}
const chartSettingInputs = {
  backgroundColor: "backgroundColor",
  axisTextColor: "axisTextColor",
  upColor: "upColor",
  downColor: "downColor",
  wickUpColor: "wickUpColor",
  wickDownColor: "wickDownColor",
  crosshairEnabled: "crosshair",
  priceBorderEnabled: "priceBorder",
  timeBorderEnabled: "timeBorder",
  unlimitedZoom: "unlimitedZoom",
  timeFormat: "timeFormat",
};
Object.entries(chartSettingInputs).forEach(([id, key]) => {
  const control = $("#" + id);
  if (!control) return;
  control.addEventListener("input", (event) => {
    chartSettings[key] =
      event.target.type === "checkbox" ? event.target.checked : event.target.value;
    applyChartSettings();
  });
});
$("#timeFormat").addEventListener("change", () =>
  toast("Chart time format updated", "success"),
);
$("#resetChartSettings").onclick = () => {
  chartSettings = { ...chartSettingsDefaults };
  syncChartSettingsForm();
  applyChartSettings();
  toast("Chart settings restored");
};
syncChartSettingsForm();
applyChartSettings(false);

const chartElement = $("#chart"),
  canvas = $("#draw"),
  ctx = canvas.getContext("2d"),
  shell = $(".chart-shell");
Object.assign(state, {
  selected: null,
  selectedIds: [],
  redo: [],
  interaction: null,
  defaults: {
    stroke: "#2962ff",
    fill: "#2962ff",
    width: 0.5,
    style: "solid",
    opacity: 0.1,
  },
});
$("#chart").insertAdjacentHTML(
  "afterend",
  '<div id="chartWatermark" class="chart-watermark hidden"></div>',
);
applyChartSettings(false);
const clone = (v) => JSON.parse(JSON.stringify(v));
function storageKey() {
  return `market-canvas:${state.file?.id || "none"}:drawings`;
}
let drawingSaveQueue = Promise.resolve();
function saveDrawings() {
  state.drawings = drawingArray(state.drawings);
  if (state.file) {
    try { localStorage.setItem(storageKey(), JSON.stringify(state.drawings)); }
    catch (error) { log.chart.warn("DRAWING_BROWSER_STORAGE_FAILED", { message: error.message }); }
    const snapshot = clone(state.drawings);
    const fileId = state.file.id;
    // A single queue prevents a slow, older PUT from overwriting a later
    // interaction when the user edits a drawing several times in quick order.
    drawingSaveQueue = drawingSaveQueue
      .catch(() => {})
      .then(async () => {
        const response = await fetch('/api/drawings', {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ id: fileId, drawings: snapshot }),
        });
        if (!response.ok) throw new Error(await response.text());
      })
      .catch((error) => log.chart.error('DRAWING_FILE_SAVE_FAILED', error, { id: fileId }));
  }
  renderObjectTree();
}
function validDrawingPoint(point) {
  return Boolean(
    point &&
      Number.isFinite(Number(point.time)) &&
      Number(point.time) > 0 &&
      Number.isFinite(Number(point.price)),
  );
}
function validStoredDrawing(drawing) {
  if (!drawing || typeof drawing !== "object" || !validDrawingPoint(drawing.a))
    return false;
  if (drawing.b != null && !validDrawingPoint(drawing.b)) return false;
  if (
    ["brush", "path"].includes(drawing.type) &&
    (!Array.isArray(drawing.points) ||
      !drawing.points.length ||
      drawing.points.some((point) => !validDrawingPoint(point)))
  )
    return false;
  return true;
}
async function loadDrawings() {
  const fileId = state.file?.id || "";
  const key = storageKey();
  try {
    let stored;
    try {
      const response = await fetch(
        `/api/drawings?id=${encodeURIComponent(fileId)}`,
      );
      if (!response.ok) throw new Error(await response.text());
      stored = await response.json();
    } catch (fileError) {
      log.chart.warn('DRAWING_FILE_READ_FALLBACK', {
        id: state.file?.id,
        message: fileError.message,
      });
      stored = JSON.parse(localStorage.getItem(key) || "[]");
    }
    if (state.file?.id !== fileId) return;
    const candidates = drawingArray(stored, null);
    // Do not overwrite unknown storage formats with an empty array.
    if (!candidates) throw new Error("Unrecognized drawing storage format");
    const invalid = candidates.filter((drawing) => !validStoredDrawing(drawing));
    state.drawings = candidates.filter(validStoredDrawing);
    // Storage quota/access errors must never erase drawings already recovered.
    try {
      if (invalid.length) {
        const quarantineKey = `${key}:invalid:${Date.now()}`;
        localStorage.setItem(quarantineKey, JSON.stringify(invalid));
        log.chart.warn("INVALID_DRAWINGS_QUARANTINED", {
          symbol: state.file?.symbol,
          invalidCount: invalid.length,
          validCount: state.drawings.length,
          quarantineKey,
        });
      }
      localStorage.setItem(key, JSON.stringify(state.drawings));
    } catch (error) { log.chart.warn("DRAWING_BROWSER_STORAGE_FAILED", { message: error.message }); }
  } catch (error) {
    if (state.file?.id !== fileId) return;
    state.drawings = drawingArray(state.drawings);
    log.chart.error("DRAWING_STORAGE_READ_FAILED", error, {
      key: storageKey(),
    });
  }
  state.selected = null;
  updateToolbar();
  renderObjectTree();
  drawAll();
}
function checkpoint() {
  state.history.push(historySnapshot());
  if (state.history.length > 80) state.history.shift();
  state.redo = [];
}
function historySnapshot() {
  return normalizeHistorySnapshot({ drawings: state.drawings, indicatorObjects: state.indicator.objects }, {});
}
function restoreHistorySnapshot(snapshot) {
  const normalized = normalizeHistorySnapshot(snapshot, historySnapshot());
  state.drawings = normalized.drawings;
  state.indicator.objects = normalized.indicatorObjects;
  state.indicator.objectMap = new Map(state.indicator.objects.map((item) => [item.id, item]));
  state.indicator.selectedObjectId = null;
  state.selected = null;
  state.selectedIds = [];
  state.treeSelectedIds = [];
  state.draft = null;
  state.interaction = null;
  saveDrawings();
  updateToolbar();
  renderObjectTree();
  drawAll();
}
function resize() {
  const r = chartElement.getBoundingClientRect();
  chart.resize(r.width, r.height);
  canvas.width = r.width * devicePixelRatio;
  canvas.height = r.height * devicePixelRatio;
  canvas.style.width = r.width + "px";
  canvas.style.height = r.height + "px";
  ctx.setTransform(devicePixelRatio, 0, 0, devicePixelRatio, 0, 0);
  drawAll();
}
new ResizeObserver(resize).observe(chartElement);
function point(e) {
  // Coordinate conversion must use the actual Lightweight Charts surface.
  // The shell may have additional chrome or change its geometry when panels
  // are pinned, while drawings are anchored exclusively to the chart canvas.
  const r = chartElement.getBoundingClientRect(),
    x = e.clientX - r.left,
    y = e.clientY - r.top;
  const result = {
    x,
    y,
    logical: chart.timeScale().coordinateToLogical(x),
    time: chart.timeScale().coordinateToTime(x),
    price: series.coordinateToPrice(y),
  };
  // The chart library returns null to the right of the last bar. Drawings are
  // intentionally allowed there, so synthesize a stable future time instead
  // of clamping the point to the final candle.
  if (state.data.length && (result.time == null || result.price == null)) {
    const range = chart.timeScale().getVisibleLogicalRange();
    const from = range?.from ?? 0;
    const to = range?.to ?? Math.max(0, state.data.length - 1);
    const logical = from + (Math.max(0, Math.min(x, canvas.clientWidth)) / Math.max(1, canvas.clientWidth)) * (to - from);
    const candle = state.data[Math.max(0, Math.min(state.data.length - 1, Math.round(logical)))];
    if (result.time == null) {
      const first = state.data[0];
      const last = state.data.at(-1);
      const firstX = chart.timeScale().timeToCoordinate(Number(first.time));
      const lastX = chart.timeScale().timeToCoordinate(Number(last.time));
      const spacing = Math.max(1, Number(chart.timeScale().options().barSpacing) || 6);
      if (Number.isFinite(lastX) && x > lastX)
        result.time = Number(last.time) + Math.round((x - lastX) / spacing) * state.tf;
      else if (Number.isFinite(firstX) && x < firstX)
        result.time = Math.max(1, Number(first.time) + Math.round((x - firstX) / spacing) * state.tf);
      else result.time = candle?.time ?? null;
    }
    if (result.price == null) {
      let high = -Infinity, low = Infinity;
      for (const item of state.data) {
        high = Math.max(high, Number(item.high));
        low = Math.min(low, Number(item.low));
      }
      if (Number.isFinite(high) && Number.isFinite(low)) {
        result.price = high - (Math.max(0, Math.min(y, canvas.clientHeight)) / Math.max(1, canvas.clientHeight)) * (high - low || 1);
      }
    }
  }
  if (state.magnet && result.time != null && state.data.length) {
    let lo = 0, hi = state.data.length - 1;
    while (lo < hi) {
      const mid = (lo + hi) >> 1;
      if (state.data[mid].time < result.time) lo = mid + 1;
      else hi = mid;
    }
    const candle = state.data[lo];
    const prices = [candle.open, candle.high, candle.low, candle.close];
    result.time = candle.time;
    result.price = prices.reduce((best, value) =>
      Math.abs(value - result.price) < Math.abs(best - result.price) ? value : best,
    );
  }
  return result;
}
const DRAWING_PRICE_SCALE_GUTTER = 64;
const DRAWING_TIME_SCALE_GUTTER = 34;
function isDrawingSurface(p) {
  return p && p.x >= 0 && p.y >= 0 &&
    p.x < canvas.clientWidth - DRAWING_PRICE_SCALE_GUTTER &&
    p.y < canvas.clientHeight - DRAWING_TIME_SCALE_GUTTER;
}
function xy(p) {
  if (!validDrawingPoint(p)) {
    log.chart.warn("INVALID_DRAWING_POINT_SKIPPED", {
      point: p ?? null,
    });
    return null;
  }
  const time = Number(p.time);
  let x = Number.isFinite(Number(p.logical))
    ? chart.timeScale().logicalToCoordinate(Number(p.logical))
    : chart.timeScale().timeToCoordinate(time);
  if (x == null && Number.isFinite(Number(p.logical)))
    x = chart.timeScale().timeToCoordinate(time);
  if (x == null && state.data.length) {
    const first = state.data[0];
    const last = state.data.at(-1);
    const firstX = chart.timeScale().timeToCoordinate(Number(first.time));
    const lastX = chart.timeScale().timeToCoordinate(Number(last.time));
    const spacing = Math.max(1, Number(chart.timeScale().options().barSpacing) || 6);
    if (Number.isFinite(lastX) && time > Number(last.time))
      x = lastX + ((time - Number(last.time)) / state.tf) * spacing;
    else if (Number.isFinite(firstX) && time < Number(first.time))
      x = firstX + ((time - Number(first.time)) / state.tf) * spacing;
  }
  return {
    x,
    y: series.priceToCoordinate(Number(p.price)),
  };
}
function rgba(hex, a) {
  const n = parseInt(hex.slice(1), 16);
  return `rgba(${n >> 16},${(n >> 8) & 255},${n & 255},${a})`;
}
function styleOf(d) {
  return d.style || state.defaults;
}
function dash(s) {
  return s === "dash" ? [9, 6] : s === "dot" ? [1, 4] : [];
}
function valid(q) {
  return q && q.x != null && q.y != null;
}
function handle(q) {
  ctx.beginPath();
  ctx.arc(q.x, q.y, 5, 0, Math.PI * 2);
  ctx.fillStyle = "#fff";
  ctx.fill();
  ctx.strokeStyle = "#2962ff";
  ctx.lineWidth = 2;
  ctx.setLineDash([]);
  ctx.stroke();
}
function drawOne(d, selected = false) {
  const s = styleOf(d);
  // Freehand drawings can straddle the visible range.  Their legacy a/b
  // endpoints are metadata only; rejecting either endpoint used to hide the
  // entire stroke while it was being moved.
  if (["brush", "path"].includes(d.type)) {
    const pts = (d.points || []).map(xy).filter(valid);
    if (d.type === "path" && d.preview) {
      const preview = xy(d.preview);
      if (valid(preview)) pts.push(preview);
    }
    if (!pts.length) return;
    ctx.save();
    ctx.strokeStyle = s.stroke;
    ctx.lineWidth = s.width;
    ctx.setLineDash(dash(s.style));
    ctx.beginPath();
    ctx.moveTo(pts[0].x, pts[0].y);
    pts.slice(1).forEach((q) => ctx.lineTo(q.x, q.y));
    ctx.stroke();
    ctx.restore();
    if (selected && !d.locked && d.type === "path") pts.forEach(handle);
    return;
  }
  const a = xy(d.a),
    b = xy(d.b || d.a);
  if (!valid(a) || !valid(b)) return;
  ctx.save();
  ctx.strokeStyle = s.stroke;
  ctx.fillStyle = rgba(s.fill, s.opacity);
  ctx.lineWidth = s.width;
  ctx.setLineDash(dash(s.style));
  ctx.beginPath();
  if (d.type === "hline") {
    ctx.moveTo(0, a.y);
    ctx.lineTo(canvas.clientWidth, a.y);
  } else if (d.type === "hray") {
    ctx.moveTo(a.x, a.y);
    ctx.lineTo(canvas.clientWidth, a.y);
  } else if (d.type === "vline") {
    ctx.moveTo(a.x, 0);
    ctx.lineTo(a.x, canvas.clientHeight);
  } else if (["long", "short"].includes(d.type)) {
    const left = Math.min(a.x, b.x);
    const right = Math.max(a.x + 48, b.x);
    const entry = a.y;
    const distance = Math.max(12, Math.abs(b.y - a.y));
    const target = d.type === "long" ? entry - distance : entry + distance;
    const stop = d.type === "long" ? entry + distance : entry - distance;
    const targetTop = Math.min(entry, target);
    const stopTop = Math.min(entry, stop);
    ctx.fillStyle = d.type === "long" ? "rgba(8, 153, 129, .18)" : "rgba(242, 54, 69, .18)";
    ctx.fillRect(left, targetTop, right - left, Math.abs(target - entry));
    ctx.fillStyle = d.type === "long" ? "rgba(242, 54, 69, .16)" : "rgba(8, 153, 129, .16)";
    ctx.fillRect(left, stopTop, right - left, Math.abs(stop - entry));
    ctx.strokeStyle = s.stroke;
    ctx.setLineDash([4, 3]);
    ctx.moveTo(left, entry);
    ctx.lineTo(right, entry);
    ctx.setLineDash([]);
    ctx.rect(left, targetTop, right - left, Math.abs(target - entry));
    ctx.rect(left, stopTop, right - left, Math.abs(stop - entry));
  } else if (d.type === "rect") {
    ctx.rect(a.x, a.y, b.x - a.x, b.y - a.y);
    ctx.fill();
  } else if (d.type === "circle") {
    ctx.ellipse(
      (a.x + b.x) / 2,
      (a.y + b.y) / 2,
      Math.abs(b.x - a.x) / 2,
      Math.abs(b.y - a.y) / 2,
      0,
      0,
      Math.PI * 2,
    );
    ctx.fill();
  } else if (d.type === "fib") {
    const left = Math.min(a.x, b.x),
      right = Math.max(a.x, b.x),
      levels = [0, 0.618, 1];
    ctx.textAlign = "left";
    ctx.textBaseline = "middle";
    for (const level of levels) {
      const y = b.y + (a.y - b.y) * level,
        price =
          Number(d.b.price) +
          (Number(d.a.price) - Number(d.b.price)) * level,
        highlight = level === 0.618;
      ctx.beginPath();
      ctx.moveTo(left, y);
      ctx.lineTo(right, y);
      ctx.strokeStyle = highlight ? "#ff8a4c" : "#cbd0d7";
      ctx.lineWidth = highlight ? 1.5 : 1;
      ctx.setLineDash([]);
      ctx.stroke();
      ctx.fillStyle = highlight ? "#ff7a3d" : "#b6bcc6";
      ctx.font = `${highlight ? 700 : 500} 11px Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`;
      ctx.fillText(
        `${level} (${price.toLocaleString("en-US", { minimumFractionDigits: 4, maximumFractionDigits: 4 })})`,
        right + 7,
        y,
      );
    }
    ctx.beginPath();
  } else if (d.type === "channel") {
    const offset = 34;
    ctx.moveTo(a.x, a.y);
    ctx.lineTo(b.x, b.y);
    ctx.lineTo(b.x, b.y + offset);
    ctx.lineTo(a.x, a.y + offset);
    ctx.closePath();
    ctx.fill();
    ctx.moveTo(a.x, a.y);
    ctx.lineTo(b.x, b.y);
    ctx.moveTo(a.x, a.y + offset);
    ctx.lineTo(b.x, b.y + offset);
  } else if (d.type === "measure") {
    const left=Math.min(a.x,b.x), top=Math.min(a.y,b.y), width=Math.abs(b.x-a.x), height=Math.abs(b.y-a.y);
    ctx.fillStyle="rgba(41,98,255,.08)"; ctx.strokeStyle="rgba(41,98,255,.45)";
    ctx.rect(left,top,width,height); ctx.fill();
    ctx.moveTo(left,(a.y+b.y)/2); ctx.lineTo(left+width,(a.y+b.y)/2);
    ctx.moveTo((a.x+b.x)/2,top); ctx.lineTo((a.x+b.x)/2,top+height);
    const bars = Math.round(Math.abs(Number(d.b.time)-Number(d.a.time))/state.tf);
    const change = Number(d.b.price)-Number(d.a.price);
    const pct = Number(d.a.price) ? change/Number(d.a.price)*100 : 0;
    const label=`${change>=0?'+':''}${change.toFixed(3)} (${pct.toFixed(2)}%) • ${bars} bars`;
    ctx.font='650 12px Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif';
    const labelWidth=ctx.measureText(label).width+18, labelX=left+(width-labelWidth)/2, labelY=top+height+9;
    ctx.fillStyle="#eaf1ff"; ctx.fillRect(labelX,labelY,labelWidth,30);
    ctx.fillStyle="#334155"; ctx.textAlign="center"; ctx.textBaseline="middle";
    ctx.fillText(label,labelX+labelWidth/2,labelY+15);
  } else if (d.type === "text") {
    ctx.font = `600 ${d.textSize || 12 + s.width * 2}px Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`;
    ctx.fillStyle = s.stroke;
    ctx.fillText(d.text, a.x, a.y);
  } else {
    ctx.moveTo(a.x, a.y);
    const ex = d.type === "ray" ? canvas.clientWidth : b.x,
      ey =
        d.type === "ray"
          ? a.y + ((canvas.clientWidth - a.x) * (b.y - a.y)) / (b.x - a.x || 1)
          : b.y;
    ctx.lineTo(ex, ey);
    if (d.type === "arrow") {
      const angle=Math.atan2(ey-a.y,ex-a.x),size=9;
      ctx.lineTo(ex-size*Math.cos(angle-.55),ey-size*Math.sin(angle-.55));
      ctx.moveTo(ex,ey);ctx.lineTo(ex-size*Math.cos(angle+.55),ey-size*Math.sin(angle+.55));
    }
  }
  ctx.stroke();
  ctx.restore();
  if (d.type === "vline") {
    const label = formatTehran(d.a.time, false),
      labelY = canvas.clientHeight - 21;
    ctx.save();
    ctx.font =
      '500 10px "SF Mono", Consolas, ui-monospace, monospace';
    const labelWidth = ctx.measureText(label).width + 12,
      labelX = Math.max(
        2,
        Math.min(canvas.clientWidth - labelWidth - 2, a.x - labelWidth / 2),
      );
    ctx.fillStyle = s.stroke;
    ctx.fillRect(labelX, labelY, labelWidth, 19);
    ctx.fillStyle = "#ffffff";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(label, labelX + labelWidth / 2, labelY + 9.5);
    ctx.restore();
  }
  if (selected && !d.locked && d.type === "path") {
    (d.points || []).map(xy).filter(valid).forEach(handle);
  } else if (selected && !d.locked) {
    handle(a);
    if (!["hline", "hray", "vline", "text"].includes(d.type)) handle(b);
  }
}
function indicatorObject(id) {
  return state.indicator.objectMap.get(id);
}
function indicatorObjectVisible(id) {
  const item = indicatorObject(id);
  return !item || !item.hidden;
}
const INDICATOR_LABEL_MEDIUM_SIZE = 12,
  INDICATOR_LABEL_SMALL_SIZE = 12,
  INDICATOR_LABEL_LARGE_SIZE = 15,
  STOPALL_LABEL_GAP = 16;
function rebuildIndicatorObjects() {
  const output = [];
  if (!state.indicator.results) {
    state.indicator.objects = output;
    state.indicator.objectMap = new Map();
    renderObjectTree();
    return;
  }
  const add = (item) => output.push({ locked: true, hidden: false, ...item });
  for (const [direction, group] of Object.entries(state.indicator.results.directions)) {
    (group.reactions || []).forEach((item, index) => add({ id: `indicator:${direction}:reaction:${index}`, type: "indicator-reaction", name: `${direction} Reaction ${index + 1}`, time: item.firstTime, price: item.boxTop, color: direction === "bullish" ? state.indicator.settings.bullBorder : state.indicator.settings.bearBorder }));
    (group.blueLines || []).forEach((item, index) => add({ id: `indicator:${direction}:blue:${index}`, type: "indicator-blue", name: `Blue Line ${index + 1}`, time: item.sourceTime, price: item.linePrice, color: state.indicator.settings.blueColor }));
    (group.aZones || []).forEach((item, index) => add({ id: `indicator:${direction}:a:${index}`, type: "indicator-label", name: `A ${index + 1}`, text: "A", size: INDICATOR_LABEL_SMALL_SIZE, weight: 500, time: item.sourceTime, price: item.price, color: "#7c3aed" }));
    (group.sZones || []).forEach((item, index) => {
      add({ id: `indicator:${direction}:s:${index}`, type: "indicator-label", name: `S ${index + 1}`, text: "S", size: INDICATOR_LABEL_MEDIUM_SIZE, weight: 500, time: item.sourceTime, price: item.price, color: item.color === "red" ? "#f23645" : "#2563eb" });
      if (item.orderFirstTime != null)
        add({ id: `indicator:${direction}:s-order:${index}`, type: "indicator-order", name: `S order ${index + 1}`, time: item.orderFirstTime, price: item.orderStopLevel, color: state.indicator.settings.orderColor });
    });
    (group.eZones || []).forEach((item, index) => {
      const family = item.family === "red" ? "red" : "blue";
      const eName = `E${item.number}`;
      const eColor = family === "red" ? "#7f1d1d" : "#1e3a8a";
      add({ id: `indicator:${direction}:e:${index}`, type: "indicator-label", name: eName, text: eName, size: INDICATOR_LABEL_MEDIUM_SIZE, weight: 600, time: item.sourceTime, price: item.price, color: eColor });
      add({ id: `indicator:${direction}:e-order:${index}`, type: "indicator-order", name: `${eName} order`, time: item.orderFirstTime, price: item.orderStopLevel, color: state.indicator.settings.orderColor });
      if (
        String(item.parentType).toUpperCase() === "E" &&
        Number(item.parentStopIndex) - Number(item.parentSourceIndex) > 350
      )
        add({ id: `indicator:${direction}:e-stop:${index}`, type: "indicator-stop", name: `E${Math.max(1, Number(item.number) - 1)} stop`, time: item.parentSourceTime, price: item.parentPrice, color: state.indicator.settings.eStopColor });
    });
    (group.stopAlls || []).forEach((item, index) => {
      const name = `StopAll${item.number}`;
      add({ id: `indicator:${direction}:stopall:${index}`, type: "indicator-label", name, text: String(item.number), size: INDICATOR_LABEL_LARGE_SIZE, weight: 600, time: item.sourceTime, price: item.price, color: "#ff9800" });
      add({ id: `indicator:${direction}:stopall-order:${index}`, type: "indicator-order", name: `${name} order`, time: item.orderFirstTime, price: item.orderStopLevel, color: state.indicator.settings.orderColor });
    });
    const seenStops = new Set();
    [...(group.sZones || []), ...(group.eZones || []), ...(group.stopAlls || [])].forEach((item) => {
      if (item.orderStopSourceIndex == null || item.orderStopLevel == null) return;
      const key = [item.orderDirection, item.orderFirstIndex, item.orderStopSourceIndex].join(":");
      if (seenStops.has(key)) return;
      seenStops.add(key);
      add({ id: `indicator:${direction}:stop:${key}`, type: "indicator-stop", name: `Order stop ${seenStops.size}`, time: item.orderStopSourceTime, price: item.orderStopLevel, color: state.indicator.settings.orderStopColor });
    });
  }
  state.indicator.objects = output;
  state.indicator.objectMap = new Map(output.map((item) => [item.id, item]));
  state.indicator.selectedObjectId = null;
  renderObjectTree();
}
function indicatorOffset(item) {
  return {
    x: Number.isFinite(Number(item?.offsetX)) ? Number(item.offsetX) : 0,
    y: Number.isFinite(Number(item?.offsetY)) ? Number(item.offsetY) : 0,
  };
}
function offsetIndicatorPoint(item, x, y) {
  const offset = indicatorOffset(item);
  return { x: x + offset.x, y: y + offset.y };
}
function offsetIndicatorRect(item, x1, y1, x2, y2) {
  const offset = indicatorOffset(item);
  return { x1: x1 + offset.x, y1: y1 + offset.y, x2: x2 + offset.x, y2: y2 + offset.y };
}
function drawIndicator() {
  state.indicator.hitBoxes = [];
  if (!state.indicator.enabled || !state.indicator.results) return;
  const settings = state.indicator.settings,
    visibleRange = chart.timeScale().getVisibleRange(),
    timeframe = Number(state.indicator.results.timeframe || state.tf),
    visiblePadding = Number.isFinite(timeframe) ? timeframe * 30 : 0,
    visibleFrom = visibleRange ? Number(visibleRange.from) - visiblePadding : -Infinity,
    visibleTo = visibleRange ? Number(visibleRange.to) + visiblePadding : Infinity,
    isTimeVisible = (time) => {
      const value = Number(time);
      return !Number.isFinite(value) || (value >= visibleFrom && value <= visibleTo);
    },
    isTimeRangeVisible = (from, to = from) => {
      const start = Number(from), end = Number(to);
      return !Number.isFinite(start) || !Number.isFinite(end) ||
        Math.max(start, end) >= visibleFrom && Math.min(start, end) <= visibleTo;
    };
  for (const direction of Object.keys(state.indicator.results.directions)) {
    const group = state.indicator.results.directions[direction],
      bullish = direction === "bullish",
      eSourceIndices = group.__eSourceIndices ||= new Set(
        (group.eZones || []).map((zone) => Number(zone.sourceIndex)),
      ),
      stopAllSourceIndices = group.__stopAllSourceIndices ||= new Set(
        (group.stopAlls || []).map((zone) => Number(zone.sourceIndex)),
      ),
      sSourceIndices = group.__sSourceIndices ||= new Set(
        (group.sZones || []).map((zone) => Number(zone.sourceIndex)),
      ),
      fill = bullish ? settings.bullFill : settings.bearFill,
      border = bullish ? settings.bullBorder : settings.bearBorder,
      opacity = (bullish ? settings.bullOpacity : settings.bearOpacity) / 100,
      width = bullish ? settings.bullWidth : settings.bearWidth;
    let count = 0,
      lastFirst = -1,
      resetCursor = 0,
      aCursor = 0;
    const resets = settings.numberEnabled && settings.numberMode === "reset"
        ? (group.__sortedResets ||= [...group.resets].sort((a, b) => a.index - b.index))
        : [],
      aZones = settings.numberEnabled && settings.numberMode === "a"
        ? (group.__sortedAZones ||= [...(group.aZones || [])].sort((a, b) => Number(a.sourceIndex) - Number(b.sourceIndex)))
        : [];
    for (const [reactionIndex, reaction] of group.reactions.entries()) {
      if (settings.numberMode === "reset") {
        let reset = false;
        while (
          resetCursor < resets.length &&
          resets[resetCursor].index <= reaction.firstIndex
        ) {
          if (resets[resetCursor].index > lastFirst) reset = true;
          resetCursor++;
        }
        count = reset ? 1 : count + 1;
      } else if (settings.numberMode === "a") {
        let restart = false;
        while (
          aCursor < aZones.length &&
          Number(aZones[aCursor].sourceIndex) <= reaction.firstIndex
        ) {
          if (Number(aZones[aCursor].sourceIndex) > lastFirst) restart = true;
          aCursor++;
        }
        count = restart ? 1 : count + 1;
      } else count++;
      lastFirst = reaction.firstIndex;
      if (!isTimeRangeVisible(reaction.firstTime, reaction.breakTime)) continue;
      const reactionObjectId = `indicator:${direction}:reaction:${reactionIndex}`;
      if (!settings.reactionVisible || !indicatorObjectVisible(reactionObjectId)) continue;
      const reactionObject = indicatorObject(reactionObjectId);
      const startTime = bullish
          ? reaction.boxTopSourceTime
          : reaction.boxBottomSourceTime,
        x1 = chart.timeScale().timeToCoordinate(startTime),
        x2 = chart.timeScale().timeToCoordinate(reaction.breakTime),
        yTop = series.priceToCoordinate(+reaction.boxTop),
        yBottom = series.priceToCoordinate(+reaction.boxBottom);
      if ([x1, x2, yTop, yBottom].some((v) => v == null)) continue;
      const shifted = offsetIndicatorRect(reactionObject, x1, yTop, x2, yBottom),
        left = Math.min(shifted.x1, shifted.x2),
        right = Math.max(shifted.x1, shifted.x2),
        top = Math.min(shifted.y1, shifted.y2),
        bottom = Math.max(shifted.y1, shifted.y2);
      state.indicator.hitBoxes.push({
        objectId: reactionObjectId,
        shape: "rect",
        left,
        right,
        top,
        bottom,
        direction,
        reaction,
      });
      ctx.save();
      ctx.fillStyle = rgba(
        reactionObject?.customized ? reactionObject.fill : fill,
        reactionObject?.customized ? reactionObject.opacity : opacity,
      );
      ctx.strokeStyle = reactionObject?.customized ? reactionObject.color : border;
      ctx.lineWidth = reactionObject?.customized ? reactionObject.width : width;
      ctx.setLineDash(
        reactionObject?.customized
          ? dash(reactionObject.lineStyle)
          : dash(bullish ? settings.bullLineStyle : settings.bearLineStyle),
      );
      ctx.beginPath();
      ctx.rect(left, top, Math.max(1, right - left), Math.max(1, bottom - top));
      ctx.fill();
      if (width > 0) ctx.stroke();
      if (settings.numberEnabled) {
        ctx.font = `${settings.numberWeight} ${settings.numberSize}px Inter`;
        ctx.textAlign = "center";
        ctx.textBaseline = bullish ? "top" : "bottom";
        ctx.fillStyle = settings.numberColor;
        ctx.fillText(
          String(count),
          (left + right) / 2,
          bullish ? bottom + settings.numberGap : top - settings.numberGap,
        );
      }
      ctx.restore();
    }
    if (settings.blueLineEnabled) {
      for (const [blueIndex, blueLine] of (group.blueLines || []).entries()) {
        if (!isTimeVisible(blueLine.sourceTime)) continue;
        const blueObjectId = `indicator:${direction}:blue:${blueIndex}`,
          blueObject = indicatorObject(blueObjectId);
        if (blueObject?.hidden) continue;
        const x1 = chart.timeScale().timeToCoordinate(blueLine.startTime),
          x2 = chart.timeScale().timeToCoordinate(blueLine.endTime),
          y = series.priceToCoordinate(+blueLine.linePrice);
        if ([x1, x2, y].some((value) => value == null)) continue;
        const shifted = offsetIndicatorRect(blueObject, x1, y, x2, y);
        state.indicator.hitBoxes.push({ objectId: blueObjectId, shape: "line", x1: shifted.x1, y1: shifted.y1, x2: shifted.x2, y2: shifted.y2 });
        ctx.save();
        ctx.strokeStyle = blueObject?.customized ? rgba(blueObject.color, blueObject.opacity ?? 1) : rgba(settings.blueColor, settings.blueOpacity / 100);
        ctx.lineWidth = blueObject?.customized ? blueObject.width : settings.blueWidth;
        ctx.lineCap = "round";
        ctx.setLineDash(
          blueObject?.customized
            ? dash(blueObject.lineStyle)
            : dash(settings.blueLineStyle),
        );
        ctx.beginPath();
        ctx.moveTo(shifted.x1, shifted.y1);
        ctx.lineTo(shifted.x2, shifted.y2);
        ctx.stroke();
        ctx.restore();
      }
    }
    for (const [zoneIndex, zone] of (group.aZones || []).entries()) {
      const labelObject = indicatorObject(`indicator:${direction}:a:${zoneIndex}`);
      if (!settings.aVisible) continue;
      if (labelObject?.hidden) continue;
      if (
        eSourceIndices.has(Number(zone.sourceIndex)) ||
        stopAllSourceIndices.has(Number(zone.sourceIndex)) ||
        sSourceIndices.has(Number(zone.sourceIndex))
      )
        continue;
      const x = chart.timeScale().timeToCoordinate(zone.sourceTime),
        y = series.priceToCoordinate(+zone.price);
      if (x == null || y == null) continue;
      const shifted = offsetIndicatorPoint(labelObject, x, bullish ? y + settings.aGap : y - settings.aGap);
      state.indicator.hitBoxes.push({ objectId: `indicator:${direction}:a:${zoneIndex}`, shape: "point", x: shifted.x, y: shifted.y, radius: 14 });
      ctx.save();
      ctx.fillStyle = labelObject?.customized
        ? labelObject.color
        : settings.aColor || "#7c3aed";
      ctx.font = `${labelObject?.weight || 500} ${
        labelObject?.customized ? labelObject.size : settings.aSize || INDICATOR_LABEL_SMALL_SIZE
      }px Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`;
      ctx.textAlign = "center";
      ctx.textBaseline = bullish ? "top" : "bottom";
      ctx.fillText(labelObject?.text ?? "A", shifted.x, shifted.y);
      ctx.restore();
    }
    for (const [zoneIndex, zone] of (group.sZones || []).entries()) {
      const hasOrder = zone.orderFirstTime != null;
      const orderObject = indicatorObject(`indicator:${direction}:s-order:${zoneIndex}`),
        labelObject = indicatorObject(`indicator:${direction}:s:${zoneIndex}`);
      const orderBullish = zone.orderDirection === "bullish",
        orderStartTime = orderBullish
          ? zone.orderBoxTopSourceTime
          : zone.orderBoxBottomSourceTime,
        boxX1 = hasOrder ? chart.timeScale().timeToCoordinate(orderStartTime) : null,
        boxX2 = hasOrder ? chart.timeScale().timeToCoordinate(zone.orderBreakTime) : null,
        boxYTop = hasOrder ? series.priceToCoordinate(+zone.orderBoxTop) : null,
        boxYBottom = hasOrder ? series.priceToCoordinate(+zone.orderBoxBottom) : null;
      if (hasOrder && settings.orderVisible && !orderObject?.hidden && ![boxX1, boxX2, boxYTop, boxYBottom].some((v) => v == null)) {
        const shifted = offsetIndicatorRect(orderObject, boxX1, boxYTop, boxX2, boxYBottom),
          left = Math.min(shifted.x1, shifted.x2),
          right = Math.max(shifted.x1, shifted.x2),
          top = Math.min(shifted.y1, shifted.y2),
          bottom = Math.max(shifted.y1, shifted.y2);
        state.indicator.hitBoxes.push({ objectId: `indicator:${direction}:s-order:${zoneIndex}`, shape: "rect", left, right, top, bottom });
        ctx.save();
        ctx.fillStyle = rgba(orderObject?.customized ? orderObject.fill : settings.orderFill, orderObject?.customized ? orderObject.opacity : settings.orderOpacity / 100);
        ctx.strokeStyle = orderObject?.customized ? orderObject.color : settings.orderColor;
        ctx.lineWidth = orderObject?.customized ? orderObject.width : settings.orderWidth;
        ctx.setLineDash(
          orderObject?.customized
            ? dash(orderObject.lineStyle)
            : dash(settings.orderLineStyle),
        );
        ctx.beginPath();
        ctx.rect(left, top, Math.max(1, right - left), Math.max(1, bottom - top));
        ctx.fill();
        ctx.stroke();
        ctx.restore();
      }
      const x = chart.timeScale().timeToCoordinate(zone.sourceTime),
        y = series.priceToCoordinate(+zone.price);
      if (x == null || y == null) continue;
      const shiftedLabel = offsetIndicatorPoint(labelObject, x, bullish ? y + settings.sGap : y - settings.sGap);
      state.indicator.hitBoxes.push({ objectId: `indicator:${direction}:s:${zoneIndex}`, shape: "point", x: shiftedLabel.x, y: shiftedLabel.y, radius: 14 });
      if (eSourceIndices.has(Number(zone.sourceIndex)) || stopAllSourceIndices.has(Number(zone.sourceIndex))) continue;
      if (!settings.sVisible) continue;
      if (labelObject?.hidden) continue;
      ctx.save();
      ctx.fillStyle = labelObject?.customized
        ? labelObject.color
        : zone.color === "red"
          ? settings.sBearColor || "#f23645"
          : settings.sBullColor || "#2563eb";
      ctx.font = `${labelObject?.weight || 500} ${
        labelObject?.customized ? labelObject.size : settings.sSize || INDICATOR_LABEL_MEDIUM_SIZE
      }px Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`;
      ctx.textAlign = "center";
      ctx.textBaseline = bullish ? "top" : "bottom";
      ctx.fillText(labelObject?.text ?? "S", shiftedLabel.x, shiftedLabel.y);
      ctx.restore();
    }
    for (const [zoneIndex, zone] of (group.eZones || []).entries()) {
      const orderObject = indicatorObject(`indicator:${direction}:e-order:${zoneIndex}`),
        labelObject = indicatorObject(`indicator:${direction}:e:${zoneIndex}`);
      const orderBullish = zone.orderDirection === "bullish",
        orderStartTime = orderBullish
          ? zone.orderBoxTopSourceTime
          : zone.orderBoxBottomSourceTime,
        boxX1 = chart.timeScale().timeToCoordinate(orderStartTime),
        boxX2 = chart.timeScale().timeToCoordinate(zone.orderBreakTime),
        boxYTop = series.priceToCoordinate(+zone.orderBoxTop),
        boxYBottom = series.priceToCoordinate(+zone.orderBoxBottom);
      if (settings.orderVisible && !orderObject?.hidden && ![boxX1, boxX2, boxYTop, boxYBottom].some((v) => v == null)) {
        const shifted = offsetIndicatorRect(orderObject, boxX1, boxYTop, boxX2, boxYBottom),
          left = Math.min(shifted.x1, shifted.x2),
          right = Math.max(shifted.x1, shifted.x2),
          top = Math.min(shifted.y1, shifted.y2),
          bottom = Math.max(shifted.y1, shifted.y2);
        state.indicator.hitBoxes.push({ objectId: `indicator:${direction}:e-order:${zoneIndex}`, shape: "rect", left, right, top, bottom });
        ctx.save();
        ctx.fillStyle = rgba(orderObject?.customized ? orderObject.fill : settings.orderFill, orderObject?.customized ? orderObject.opacity : settings.orderOpacity / 100);
        ctx.strokeStyle = orderObject?.customized ? orderObject.color : settings.orderColor;
        ctx.lineWidth = orderObject?.customized ? orderObject.width : settings.orderWidth;
        ctx.setLineDash(
          orderObject?.customized
            ? dash(orderObject.lineStyle)
            : dash(settings.orderLineStyle),
        );
        ctx.beginPath();
        ctx.rect(left, top, Math.max(1, right - left), Math.max(1, bottom - top));
        ctx.fill();
        ctx.stroke();
        ctx.restore();
      }
      const x = chart.timeScale().timeToCoordinate(zone.sourceTime),
        y = series.priceToCoordinate(+zone.price);
      if (x == null || y == null) continue;
      const shiftedLabel = offsetIndicatorPoint(labelObject, x, bullish ? y + settings.eGap : y - settings.eGap);
      state.indicator.hitBoxes.push({ objectId: `indicator:${direction}:e:${zoneIndex}`, shape: "point", x: shiftedLabel.x, y: shiftedLabel.y, radius: 14 });
      if (!settings.eVisible) continue;
      if (labelObject?.hidden) continue;
      ctx.save();
      ctx.fillStyle = labelObject?.customized
        ? labelObject.color
        : zone.family === "red"
          ? settings.eRedColor || "#7f1d1d"
          : settings.eBlueColor || "#1e3a8a";
      ctx.font = `${labelObject?.weight || 500} ${
        labelObject?.customized ? labelObject.size : settings.eSize || INDICATOR_LABEL_MEDIUM_SIZE
      }px Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`;
      ctx.textAlign = "center";
      ctx.textBaseline = bullish ? "top" : "bottom";
      ctx.fillText(labelObject?.text ?? `E${zone.number}`, shiftedLabel.x, shiftedLabel.y);
      ctx.restore();
    }
    for (const [zoneIndex, zone] of (group.stopAlls || []).entries()) {
      const objectId = `indicator:${direction}:stopall:${zoneIndex}`,
        object = indicatorObject(objectId),
        orderObject = indicatorObject(`indicator:${direction}:stopall-order:${zoneIndex}`),
        orderBullish = zone.orderDirection === "bullish",
        orderStartTime = orderBullish
          ? zone.orderBoxTopSourceTime
          : zone.orderBoxBottomSourceTime,
        boxX1 = chart.timeScale().timeToCoordinate(orderStartTime),
        boxX2 = chart.timeScale().timeToCoordinate(zone.orderBreakTime),
        boxYTop = series.priceToCoordinate(+zone.orderBoxTop),
        boxYBottom = series.priceToCoordinate(+zone.orderBoxBottom),
        x = chart.timeScale().timeToCoordinate(zone.sourceTime),
        y = series.priceToCoordinate(+zone.price);
      if (settings.orderVisible && !orderObject?.hidden && ![boxX1, boxX2, boxYTop, boxYBottom].some((value) => value == null)) {
        const shifted = offsetIndicatorRect(orderObject, boxX1, boxYTop, boxX2, boxYBottom),
          left = Math.min(shifted.x1, shifted.x2),
          right = Math.max(shifted.x1, shifted.x2),
          top = Math.min(shifted.y1, shifted.y2),
          bottom = Math.max(shifted.y1, shifted.y2);
        state.indicator.hitBoxes.push({ objectId: `indicator:${direction}:stopall-order:${zoneIndex}`, shape: "rect", left, right, top, bottom });
        ctx.save();
        ctx.fillStyle = rgba(orderObject?.customized ? orderObject.fill : settings.orderFill, orderObject?.customized ? orderObject.opacity : settings.orderOpacity / 100);
        ctx.strokeStyle = orderObject?.customized ? orderObject.color : settings.orderColor;
        ctx.lineWidth = orderObject?.customized ? orderObject.width : settings.orderWidth;
        ctx.setLineDash(
          orderObject?.customized
            ? dash(orderObject.lineStyle)
            : dash(settings.orderLineStyle),
        );
        ctx.beginPath();
        ctx.rect(left, top, Math.max(1, right - left), Math.max(1, bottom - top));
        ctx.fill();
        ctx.stroke();
        ctx.restore();
      }
      if (!settings.stopAllVisible || object?.hidden || x == null || y == null) continue;
      const radius = settings.stopAllRadius,
        shifted = offsetIndicatorPoint(object, x, y);
      state.indicator.hitBoxes.push({ objectId, shape: "point", x: shifted.x, y: shifted.y, radius: radius + 2 });
      ctx.save();
      ctx.fillStyle = rgba(settings.stopAllFill, settings.stopAllOpacity / 100);
      ctx.strokeStyle = object?.customized ? object.color : settings.stopAllBorder;
      ctx.lineWidth = object?.customized ? object.width : settings.stopAllWidth;
      ctx.beginPath();
      ctx.arc(shifted.x, shifted.y, radius, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();
      ctx.fillStyle = object?.customized ? object.color : settings.stopAllBorder;
      ctx.font = `${object?.weight || 600} ${object?.customized ? object.size : settings.stopAllSize || INDICATOR_LABEL_LARGE_SIZE}px Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`;
      ctx.textAlign = "center";
      ctx.textBaseline = bullish ? "top" : "bottom";
      ctx.fillText(object?.text ?? String(zone.number), shifted.x,
        shifted.y + (bullish ? 1 : -1) * (radius + settings.stopAllGap));
      ctx.restore();
    }
    if (settings.orderStopVisible) {
      const seen = new Set();
      for (const zone of [...(group.sZones || []), ...(group.eZones || []), ...(group.stopAlls || [])]) {
        if (zone.orderStopSourceIndex == null || zone.orderStopLevel == null) continue;
        const key = [zone.orderDirection, zone.orderFirstIndex, zone.orderStopSourceIndex].join(":");
        if (seen.has(key)) continue;
        seen.add(key);
        const stopObject = indicatorObject(`indicator:${direction}:stop:${key}`);
        if (stopObject?.hidden) continue;
        const stopIndex = Number(zone.orderStopSourceIndex),
          endIndex = Math.min(
            Number.isFinite(+zone.decisionIndex) ? +zone.decisionIndex : stopIndex + settings.orderStopCap,
            stopIndex + settings.orderStopCap,
          );
        const
          startTime = zone.orderStopSourceTime,
          endTime = Number(startTime) +
            Math.max(1, endIndex - stopIndex) *
              timeframe,
          visibleEndTime = Number.isFinite(+zone.decisionTime)
            ? Math.min(+zone.decisionTime, endTime)
            : endTime;
        const
          x1 = chart.timeScale().timeToCoordinate(startTime),
          x2 = chart.timeScale().timeToCoordinate(visibleEndTime),
          y = series.priceToCoordinate(+zone.orderStopLevel);
        if ([x1, x2, y].some((value) => value == null)) continue;
        const shifted = offsetIndicatorRect(stopObject, x1, y, x2, y);
        state.indicator.hitBoxes.push({ objectId: `indicator:${direction}:stop:${key}`, shape: "line", x1: shifted.x1, y1: shifted.y1, x2: shifted.x2, y2: shifted.y2 });
        ctx.save();
        ctx.strokeStyle = stopObject?.customized ? stopObject.color : settings.orderStopColor;
        ctx.lineWidth = stopObject?.customized ? stopObject.width : settings.orderStopWidth;
        ctx.lineCap = (stopObject?.customized ? stopObject.lineStyle : settings.orderStopLineStyle) === "dot"
          ? "round"
          : "butt";
        ctx.setLineDash(
          stopObject?.customized
            ? dash(stopObject.lineStyle)
            : dash(settings.orderStopLineStyle || "dot"),
        );
        ctx.beginPath();
        ctx.moveTo(shifted.x1, shifted.y1);
        ctx.lineTo(shifted.x2, shifted.y2);
        ctx.stroke();
        ctx.restore();
      }
    }
    if (settings.eStopVisible) {
      for (const [zoneIndex, zone] of (group.eZones || []).entries()) {
        const parentStopIndex = Number(zone.parentStopIndex),
          parentSourceIndex = Number(zone.parentSourceIndex);
        if (
          String(zone.parentType).toUpperCase() !== "E" ||
          !Number.isFinite(parentStopIndex) ||
          !Number.isFinite(parentSourceIndex) ||
          parentStopIndex - parentSourceIndex <= 350
        )
          continue;
        const objectId = `indicator:${direction}:e-stop:${zoneIndex}`,
          stopObject = indicatorObject(objectId);
        if (stopObject?.hidden) continue;
        const x1 = chart.timeScale().timeToCoordinate(zone.parentSourceTime),
          x2 = chart.timeScale().timeToCoordinate(zone.parentStopTime),
          y = series.priceToCoordinate(+zone.parentPrice);
        if ([x1, x2, y].some((value) => value == null)) continue;
        const shifted = offsetIndicatorRect(stopObject, x1, y, x2, y);
        state.indicator.hitBoxes.push({
          objectId,
          shape: "line",
          x1: shifted.x1,
          y1: shifted.y1,
          x2: shifted.x2,
          y2: shifted.y2,
        });
        ctx.save();
        ctx.strokeStyle = stopObject?.customized
          ? stopObject.color
          : settings.eStopColor;
        ctx.lineWidth = stopObject?.customized
          ? stopObject.width
          : settings.eStopWidth;
        ctx.lineCap = (stopObject?.customized ? stopObject.lineStyle : settings.eStopLineStyle) === "dot"
          ? "round"
          : "butt";
        ctx.setLineDash(
          stopObject?.customized
            ? dash(stopObject.lineStyle)
            : dash(settings.eStopLineStyle || "dot"),
        );
        ctx.beginPath();
        ctx.moveTo(shifted.x1, shifted.y1);
        ctx.lineTo(shifted.x2, shifted.y2);
        ctx.stroke();
        ctx.restore();
      }
    }
  }
}
function drawIndicatorSelection() {
  if (!state.indicator.selectedObjectId) return;
  const hit = state.indicator.hitBoxes.find(
    (item) => item.objectId === state.indicator.selectedObjectId,
  );
  if (!hit) return;
  ctx.save();
  ctx.strokeStyle = "#3157d5";
  ctx.lineWidth = 1;
  ctx.setLineDash([3, 3]);
  if (hit.shape === "rect")
    ctx.strokeRect(hit.left - 3, hit.top - 3, hit.right - hit.left + 6, hit.bottom - hit.top + 6);
  else if (hit.shape === "line") {
    ctx.beginPath();
    ctx.moveTo(hit.x1, hit.y1);
    ctx.lineTo(hit.x2, hit.y2);
    ctx.stroke();
  } else {
    ctx.beginPath();
    ctx.arc(hit.x, hit.y, (hit.radius || 12) + 3, 0, Math.PI * 2);
    ctx.stroke();
  }
  ctx.restore();
}
function drawAll() {
  ctx.clearRect(0, 0, canvas.clientWidth, canvas.clientHeight);
  drawIndicator();
  drawIndicatorSelection();
  state.drawings
    .filter((d) => !d.hidden)
    .forEach((d) =>
      drawOne(d, d.id === state.selected || state.selectedIds.includes(d.id)),
    );
  if (state.draft) drawOne(state.draft);
  if (state.selectionBox) {
    const { a, b } = state.selectionBox;
    ctx.save();
    ctx.fillStyle = "rgba(41,98,255,.08)";
    ctx.strokeStyle = "#2962ff";
    ctx.lineWidth = 1;
    ctx.setLineDash([4, 4]);
    ctx.fillRect(a.x, a.y, b.x - a.x, b.y - a.y);
    ctx.strokeRect(a.x, a.y, b.x - a.x, b.y - a.y);
    ctx.restore();
  }
  if (state.selected || state.indicator.selectedObjectId)
    scheduleDrawingToolbarPosition();
}
let drawFrame = 0;
function scheduleDraw() {
  if (drawFrame) return;
  drawFrame = requestAnimationFrame(() => {
    drawFrame = 0;
    drawAll();
  });
}
chart
  .timeScale()
  .subscribeVisibleLogicalRangeChange(() => {
    scheduleDraw();
    scheduleChartViewport();
  });
chart.timeScale().subscribeVisibleTimeRangeChange(() => {
  scheduleDraw();
  scheduleChartViewport();
});
chart.timeScale().subscribeSizeChange(() => {
  scheduleDraw();
  scheduleChartViewport(0);
});
shell.addEventListener("pointermove", (event) => {
  if (event.buttons) scheduleDraw();
}, { passive: true });
shell.addEventListener("pointerdown", (event) => {
  if (event.button === 0) state.pointerIsPanning = true;
}, { passive: true });
shell.addEventListener("pointerup", () => {
  state.pointerIsPanning = false;
  scheduleDraw();
  scheduleChartViewport(90);
}, { passive: true });
shell.addEventListener("pointercancel", () => {
  state.pointerIsPanning = false;
  scheduleChartViewport(90);
}, { passive: true });
function distSeg(p, a, b) {
  const dx = b.x - a.x,
    dy = b.y - a.y,
    t = Math.max(
      0,
      Math.min(
        1,
        ((p.x - a.x) * dx + (p.y - a.y) * dy) / (dx * dx + dy * dy || 1),
      ),
    );
  return Math.hypot(p.x - a.x - t * dx, p.y - a.y - t * dy);
}
function hitTest(p) {
  for (let i = state.drawings.length - 1; i >= 0; i--) {
    const d = state.drawings[i];
    if (d.hidden) continue;
    const a = xy(d.a),
      b = xy(d.b || d.a);
    if (!valid(a) || !valid(b)) continue;
    let hit = false;
    if (d.type === "hline") hit = Math.abs(p.y - a.y) < 8;
    else if (d.type === "hray") hit = p.x >= a.x - 8 && Math.abs(p.y - a.y) < 8;
    else if (d.type === "vline") hit = Math.abs(p.x - a.x) < 8;
    else if (d.type === "rect")
      hit =
        p.x >= Math.min(a.x, b.x) - 7 &&
        p.x <= Math.max(a.x, b.x) + 7 &&
        p.y >= Math.min(a.y, b.y) - 7 &&
        p.y <= Math.max(a.y, b.y) + 7;
    else if (d.type === "circle") {
      const rx = Math.abs(b.x - a.x) / 2 || 1,
        ry = Math.abs(b.y - a.y) / 2 || 1,
        cx = (a.x + b.x) / 2,
        cy = (a.y + b.y) / 2;
      hit =
        Math.abs(((p.x - cx) / rx) ** 2 + ((p.y - cy) / ry) ** 2 - 1) < 0.25;
    } else if (d.type === "text") hit = Math.hypot(p.x - a.x, p.y - a.y) < 30;
    else if (["brush", "path"].includes(d.type)) {
      const pts = (d.points || []).map(xy).filter(valid);
      hit = pts.some((q, j) =>
        Math.hypot(p.x - q.x, p.y - q.y) < 9 ||
        (j && distSeg(p, pts[j - 1], q) < 8),
      );
    } else if (["rect", "measure", "long", "short"].includes(d.type))
      hit =
        p.x >= Math.min(a.x, b.x) - 7 &&
        p.x <= Math.max(a.x, b.x) + 7 &&
        p.y >= Math.min(a.y, b.y) - 7 &&
        p.y <= Math.max(a.y, b.y) + 7;
    else if (d.type === "channel") {
      const offset = 34;
      hit =
        distSeg(p, a, b) < 8 ||
        distSeg(p, { x: a.x, y: a.y + offset }, { x: b.x, y: b.y + offset }) < 8;
    } else
      hit =
        distSeg(
          p,
          a,
          d.type === "ray"
            ? {
                x: canvas.clientWidth,
                y:
                  a.y +
                  ((canvas.clientWidth - a.x) * (b.y - a.y)) / (b.x - a.x || 1),
              }
            : b,
        ) < 8;
    if (hit) return d;
  }
  return null;
}
function indicatorHitTest(p) {
  for (let index = state.indicator.hitBoxes.length - 1; index >= 0; index--) {
    const hit = state.indicator.hitBoxes[index],
      item = indicatorObject(hit.objectId);
    if (!item || item.hidden) continue;
    if (hit.shape === "point" && Math.hypot(p.x - hit.x, p.y - hit.y) <= (hit.radius || 12))
      return item;
    if (
      hit.shape === "line" &&
      distSeg(p, { x: hit.x1, y: hit.y1 }, { x: hit.x2, y: hit.y2 }) <= 7
    )
      return item;
    if (hit.shape === "rect") {
      const withinX = p.x >= hit.left - 7 && p.x <= hit.right + 7,
        withinY = p.y >= hit.top - 7 && p.y <= hit.bottom + 7,
        onBorder =
          Math.abs(p.x - hit.left) <= 7 || Math.abs(p.x - hit.right) <= 7 ||
          Math.abs(p.y - hit.top) <= 7 || Math.abs(p.y - hit.bottom) <= 7;
      if (withinX && withinY && onBorder) return item;
    }
  }
  return null;
}
function selected() {
  return state.drawings.find((d) => d.id === state.selected);
}
function selectedIndicatorObject() {
  return indicatorObject(state.indicator.selectedObjectId);
}
let toolbarPositionFrame = 0;
let manualToolbarPosition = null;
function clampToolbarPosition(left, top, chartRect, width, height) {
  return {
    left: Math.max(chartRect.left + 8, Math.min(chartRect.right - width - 8, left)),
    top: Math.max(chartRect.top + 8, Math.min(chartRect.bottom - height - 8, top)),
  };
}
function scheduleDrawingToolbarPosition() {
  if (toolbarPositionFrame) return;
  toolbarPositionFrame = requestAnimationFrame(() => {
    toolbarPositionFrame = 0;
    const bar = $("#drawingToolbar");
    if (!bar || bar.classList.contains("hidden")) return;
    const chartRect = chartElement.getBoundingClientRect();
    const width = bar.offsetWidth, height = bar.offsetHeight;
    const automaticPosition = clampToolbarPosition(
      chartRect.left + (chartRect.width - width) / 2,
      chartRect.top + 12,
      chartRect,
      width,
      height,
    );
    const position = manualToolbarPosition
      ? clampToolbarPosition(manualToolbarPosition.left, manualToolbarPosition.top, chartRect, width, height)
      : automaticPosition;
    bar.style.left = `${Math.round(position.left)}px`;
    bar.style.top = `${Math.round(position.top)}px`;
  });
}
const toolbarGrip = $(".toolbar-grip");
let toolbarDrag = null;
toolbarGrip.addEventListener("pointerdown", (event) => {
  const bar = $("#drawingToolbar");
  if (bar.classList.contains("hidden")) return;
  const rect = bar.getBoundingClientRect();
  event.preventDefault();
  event.stopPropagation();
  manualToolbarPosition = { left: rect.left, top: rect.top };
  toolbarDrag = { offsetX: event.clientX - rect.left, offsetY: event.clientY - rect.top };
  toolbarGrip.classList.add("is-dragging");
  toolbarGrip.setPointerCapture(event.pointerId);
});
toolbarGrip.addEventListener("pointermove", (event) => {
  if (!toolbarDrag) return;
  const rect = chartElement.getBoundingClientRect();
  const bar = $("#drawingToolbar");
  manualToolbarPosition = clampToolbarPosition(
    event.clientX - toolbarDrag.offsetX,
    event.clientY - toolbarDrag.offsetY,
    rect,
    bar.offsetWidth,
    bar.offsetHeight,
  );
  bar.style.left = `${Math.round(manualToolbarPosition.left)}px`;
  bar.style.top = `${Math.round(manualToolbarPosition.top)}px`;
});
function finishToolbarDrag(event) {
  if (!toolbarDrag) return;
  toolbarDrag = null;
  toolbarGrip.classList.remove("is-dragging");
  if (toolbarGrip.hasPointerCapture(event.pointerId)) toolbarGrip.releasePointerCapture(event.pointerId);
}
toolbarGrip.addEventListener("pointerup", finishToolbarDrag);
toolbarGrip.addEventListener("pointercancel", finishToolbarDrag);
function updateToolbar() {
  const d = selected(),
    indicatorItem = selectedIndicatorObject(),
    target = d || indicatorItem,
    bar = $("#drawingToolbar");
  bar.classList.toggle("hidden", !target);
  if (!target) return;
  const s = d ? styleOf(d) : null;
  $("#strokeColor").value = s?.stroke || indicatorItem.color || "#2962ff";
  $("#fillColor").value = s?.fill || indicatorItem.fill || indicatorItem.color || "#2962ff";
  syncColorControl($("#strokeColor"));
  syncColorControl($("#fillColor"));
  $("#lineWidth").value = String(s?.width || indicatorItem.width || 0.5);
  $("#lineStyle").value = s?.style || indicatorItem.lineStyle || "solid";
  $("#fillOpacity").value = s?.opacity ?? indicatorItem.opacity ?? 0.1;
  const isLabel = indicatorItem?.type === "indicator-label",
    isLine = ["indicator-blue", "indicator-stop"].includes(indicatorItem?.type),
    isBox = ["indicator-reaction", "indicator-order"].includes(indicatorItem?.type);
  const drawingText = d?.type === "text";
  const drawingHasFill = ["rect", "circle", "long", "short", "channel", "measure"].includes(d?.type);
  $("#objectText").classList.toggle("hidden", !isLabel && !drawingText);
  $("#objectText").value = indicatorItem?.text || d?.text || "";
  $("#objectSize").classList.toggle("hidden", !isLabel && !drawingText);
  $("#objectSize").value = String(indicatorItem?.size || d?.textSize || 13);
  $("#copyDrawing").classList.toggle("hidden", Boolean(indicatorItem));
  $("#fillColor").classList.toggle("hidden", indicatorItem ? !isBox : !drawingHasFill);
  $("#fillOpacity").closest(".opacity-control").classList.add("hidden");
  $("#lineWidth").classList.toggle("hidden", isLabel || drawingText);
  $("#lineStyle").classList.toggle("hidden", isLabel || drawingText);
  for (const id of ["strokeColor", "fillColor", "lineWidth", "lineStyle", "fillOpacity", "objectText", "objectSize"])
    $("#" + id).disabled = Boolean(indicatorItem?.locked);
  $("#lockDrawing").classList.toggle("active", !!target.locked);
  $("#lockDrawing").innerHTML = icon(target.locked ? "lock" : "unlock", 18);
  scheduleDrawingToolbarPosition();
}
function renderObjectTree() {
  if (!$("#objectList")) return;
  const names = {
    line: "Line",
    trend: "Trend Line",
    ray: "Ray",
    hline: "Horizontal Line",
    hray: "Horizontal Ray",
    vline: "Vertical Line",
    brush: "Brush",
    rect: "Rectangle",
    circle: "Circle",
    fib: "Fibonacci",
    text: "Text",
    arrow: "Arrow",
    channel: "Parallel Channel",
    path: "Path",
    measure: "Measure",
    long: "Long Position",
    short: "Short Position",
  };
  const total = state.drawings.length + state.indicator.objects.length;
  $("#objectCount").textContent = `${total} object${total === 1 ? "" : "s"}`;
  if ($("#objectTree").classList.contains("hidden")) {
    $("#objectList").replaceChildren();
    return;
  }
  const query = ($("#objectSearch")?.value || "").trim().toLowerCase();
  const treeSelected = (id) => state.treeSelectedIds.includes(id);
  const folderCollapsed = (id) => !query && state.collapsedObjectFolders.includes(id);
  const folderHeader = (id, label, count, locked = false, nested = false, removable = false) =>
    `<div class="tree-folder-heading"><button class="tree-folder-row ${nested ? "nested" : ""}" type="button" data-folder-toggle="${id}" aria-expanded="${!folderCollapsed(id)}"><span class="tree-chevron">${icon("chevron", 14)}</span>${icon("folder", 16)}<strong>${label}</strong><small>${count}</small>${locked ? icon("lock", 13) : ""}</button>${removable ? `<button class="tree-folder-delete" type="button" data-folder-delete="${id}" title="Delete folder" aria-label="Delete folder">${icon("trash", 14)}</button>` : ""}</div>`;
  const drawingRow = (drawing, index) =>
    `<div class="object-row ${treeSelected(drawing.id) ? "selected" : ""} ${drawing.hidden ? "muted" : ""}" draggable="true" data-object="${drawing.id}"><span class="object-color" style="background:${styleOf(drawing).stroke}"></span><div class="object-name"><strong>${names[drawing.type] || drawing.type} ${index + 1}</strong><small>${formatTehran(drawing.a.time, false)} • ${Number(drawing.a.price).toFixed(3)}</small></div><button data-action="focus" title="Focus on chart">${icon("target", 15)}</button><button data-action="visibility" title="${drawing.hidden ? "Show" : "Hide"}">${icon("eye", 15)}</button><button data-action="lock" title="${drawing.locked ? "Unlock" : "Lock"}">${icon(drawing.locked ? "lock" : "unlock", 15)}</button><button data-action="delete" class="danger" title="Delete">${icon("trash", 15)}</button></div>`;
  const indicatorRow = (item) =>
    `<div class="object-row indicator-object ${treeSelected(item.id) ? "selected" : ""} ${item.hidden ? "muted" : ""}" data-indicator-object="${item.id}"><span class="object-color" style="background:${item.color}"></span><div class="object-name"><strong>${item.name}</strong><small>Indicator • ${formatTehran(item.time, false)} • ${Number(item.price).toFixed(3)}</small></div><button data-action="focus" title="Focus on chart">${icon("target", 15)}</button><button data-action="visibility" title="${item.hidden ? "Show" : "Hide"}">${icon("eye", 15)}</button><button data-action="lock" title="${item.locked ? "Unlock" : "Lock"}">${icon(item.locked ? "lock" : "unlock", 15)}</button><button data-action="delete" class="danger" title="Hide indicator object">${icon("trash", 15)}</button></div>`;
  const manualFolders = [{ id: "manual-unfiled", name: "Drawings" }, ...state.objectFolders];
  const manualTree = manualFolders.map((folder) => {
    const items = state.drawings.filter((drawing) =>
      (drawing.folderId || "manual-unfiled") === folder.id &&
      (!query || `${names[drawing.type] || drawing.type}`.toLowerCase().includes(query)),
    );
    if (!items.length && query) return "";
    return `<section class="tree-folder" data-folder-drop="${folder.id}">${folderHeader(folder.id, folder.name, items.length, false, false, folder.id !== "manual-unfiled")}${folderCollapsed(folder.id) ? "" : `<div class="tree-folder-items">${items.map(drawingRow).join("") || '<div class="folder-empty">Drop drawings here</div>'}</div>`}</section>`;
  }).join("");
  const visibleIndicators = state.indicator.objects.filter((item) =>
    !query || `${item.name} ${item.type}`.toLowerCase().includes(query),
  );
  const indicatorTree = visibleIndicators.length ? ["bullish", "bearish"].map((direction) => {
    const id = `indicator-${direction}`;
    const items = visibleIndicators.filter((item) => item.id.includes(`:${direction}:`));
    if (!items.length) return "";
    return `${folderHeader(id, direction[0].toUpperCase() + direction.slice(1), items.length, true, true)}${folderCollapsed(id) ? "" : `<div class="tree-folder-items nested-items">${items.map(indicatorRow).join("")}</div>`}`;
  }).join("") : "";
  $("#objectList").innerHTML = `${manualTree}${indicatorTree ? `<section class="tree-folder indicator-folder">${folderHeader("indicator-output", "Indicator output", visibleIndicators.length, true)}${folderCollapsed("indicator-output") ? "" : `<div class="tree-folder-items">${indicatorTree}</div>`}</section>` : ""}` || '<div class="object-empty">Drawings and indicator output will appear here.</div>';
  const lockButton = $("#lockAllObjects");
  if (lockButton) {
    const targets = selectedTreeObjects();
    const allLocked = targets.length > 0 && targets.every((item) => item.locked);
    lockButton.innerHTML = `${icon(allLocked ? "unlock" : "lock", 15)}<span>${allLocked ? "Unlock all" : "Lock all"}</span>`;
    lockButton.title = allLocked ? "Unlock selected, or all when no objects are selected" : "Lock selected, or all when no objects are selected";
  }
  return;
  const visibleIndicatorObjects = state.indicator.objects.filter((item) =>
    !query || `${item.name} ${item.type}`.toLowerCase().includes(query),
  );
  const visibleDrawings = state.drawings.filter((item) =>
    !query || `${names[item.type] || item.type}`.toLowerCase().includes(query),
  );
  const rowLimit = 240;
  const limitedIndicatorObjects = visibleIndicatorObjects.slice(0, rowLimit);
  const remainingLimit = Math.max(0, rowLimit - limitedIndicatorObjects.length);
  const limitedDrawings = visibleDrawings.slice(0, remainingLimit);
  const drawingRows = limitedDrawings
      .map(
        (d, i) =>
          `<div class="object-row ${d.id === state.selected ? "selected" : ""} ${d.hidden ? "muted" : ""}" data-object="${d.id}"><span class="object-color" style="background:${styleOf(d).stroke}"></span><div class="object-name"><strong>${names[d.type] || d.type} ${i + 1}</strong><small>${formatTehran(d.a.time, false)} • ${Number(d.a.price).toFixed(3)}</small></div><button data-action="visibility" title="${d.hidden ? "Show" : "Hide"}">${d.hidden ? "Hidden" : "Visible"}</button><button data-action="lock" title="${d.locked ? "Unlock" : "Lock"}">${icon(d.locked ? "lock" : "unlock", 15)}</button><button data-action="delete" class="danger" title="Delete">${icon("trash", 15)}</button></div>`,
      )
      .join("");
  const indicatorRows = limitedIndicatorObjects.map((item) =>
    `<div class="object-row indicator-object ${item.id === state.indicator.selectedObjectId ? "selected" : ""} ${item.hidden ? "muted" : ""}" data-indicator-object="${item.id}"><span class="object-color" style="background:${item.color}"></span><div class="object-name"><strong>${item.name}</strong><small>Indicator • ${formatTehran(item.time, false)} • ${Number(item.price).toFixed(3)}</small></div><button data-action="visibility" title="${item.hidden ? "Show" : "Hide"}">${item.hidden ? "Hidden" : "Visible"}</button><button data-action="lock" title="${item.locked ? "Unlock" : "Lock"}">${icon(item.locked ? "lock" : "unlock", 15)}</button><button data-action="delete" class="danger" title="Remove until reload">${icon("trash", 15)}</button></div>`
  ).join("");
  const matchedTotal = visibleIndicatorObjects.length + visibleDrawings.length;
  const limitNotice = matchedTotal > rowLimit
    ? `<div class="object-limit">Showing ${rowLimit} of ${matchedTotal}. Search to reach any object.</div>`
    : "";
  $("#objectList").innerHTML = `${visibleIndicatorObjects.length ? '<div class="object-group-title">Indicator objects • temporary</div>' : ""}${indicatorRows}${limitedDrawings.length ? '<div class="object-group-title">Manual drawings • saved</div>' : ""}${drawingRows}${limitNotice}` ||
    '<div class="object-empty">Indicator objects and drawings will appear here.</div>';
}
function selectDrawing(id) {
  if (state.selected !== id || state.indicator.selectedObjectId) manualToolbarPosition = null;
  state.indicator.selectedObjectId = null;
  state.selected = id;
  state.selectedIds = id ? [id] : [];
  state.treeSelectedIds = id ? [id] : [];
  updateToolbar();
  renderObjectTree();
  drawAll();
}
function selectIndicatorObject(id) {
  if (state.indicator.selectedObjectId !== id || state.selected) manualToolbarPosition = null;
  state.selected = null;
  state.selectedIds = [];
  state.indicator.selectedObjectId = id;
  state.treeSelectedIds = id ? [id] : [];
  updateToolbar();
  renderObjectTree();
  drawAll();
}
function newDrawing(type, p) {
  return {
    id: crypto.randomUUID(),
    type,
    a: p,
    b: p,
    points: [p],
    style: clone(state.defaults),
    locked: false,
  };
}
const twoClickTools = new Set([
  "line",
  "arrow",
  "rect",
  "circle",
  "fib",
  "measure",
  "long",
  "short",
]);
function constrainLinePoint(anchor, next, shiftKey) {
  if (!shiftKey || state.tool !== "line") return next;
  const start = xy(anchor);
  if (!valid(start)) return next;
  const dx = next.x - start.x,
    dy = next.y - start.y,
    length = Math.hypot(dx, dy),
    angle = Math.round(Math.atan2(dy, dx) / (Math.PI / 4)) * (Math.PI / 4),
    x = start.x + Math.cos(angle) * length,
    y = start.y + Math.sin(angle) * length,
    time = chart.timeScale().coordinateToTime(x),
    price = series.coordinateToPrice(y);
  return time == null || price == null ? next : { x, y, time, price };
}
function finishDraft() {
  if (!state.draft) return;
  checkpoint();
  const completed = state.draft;
  delete completed.preview;
  state.drawings.push(completed);
  const id = completed.id;
  state.draft = null;
  // Brush remains armed for consecutive strokes; all other tools return to Cursor.
  state.tool = completed.type === "brush" ? "brush" : "cursor";
  $$("[data-tool]").forEach((item) =>
    item.classList.toggle("active", item.dataset.tool === state.tool),
  );
  canvas.classList.toggle("draw-mode", state.tool !== "cursor");
  selectDrawing(id);
  saveDrawings();
  log.chart.info("DRAWING_CREATED", {
    id,
    type: state.drawings.at(-1)?.type,
    totalDrawings: state.drawings.length,
  });
}
function shiftPoint(p, dt, dp, logicalDelta = 0) {
  const time = Number(p.time) + Number(dt);
  const price = Number(p.price) + Number(dp);
  if (!Number.isFinite(time) || time <= 0 || !Number.isFinite(price)) return false;
  p.time = time;
  p.price = price;
  if (Number.isFinite(Number(p.logical)) && Number.isFinite(Number(logicalDelta)))
    p.logical = Number(p.logical) + Number(logicalDelta);
  return true;
}
function moveDrawing(d, dt, dp, logicalDelta = 0) {
  if (!Number.isFinite(Number(dt)) || !Number.isFinite(Number(dp))) return false;
  const candidate = clone(d);
  if (["brush", "path"].includes(candidate.type)) {
    if (!(candidate.points || []).every((p) => shiftPoint(p, dt, dp, logicalDelta))) return false;
    if (candidate.points?.length) {
      candidate.a = clone(candidate.points[0]);
      candidate.b = clone(candidate.points.at(-1));
    }
  } else {
    if (!shiftPoint(candidate.a, dt, dp, logicalDelta)) return false;
    if (candidate.b && candidate.b !== candidate.a && !shiftPoint(candidate.b, dt, dp, logicalDelta)) return false;
  }
  Object.assign(d, candidate);
  return true;
}
function selectDrawingTool(tool) {
  if (tool !== "cursor" && !chartWorkspaceActive()) return;
  state.tool = tool;
  $$("[data-tool]").forEach((item) =>
    item.classList.toggle("active", item.dataset.tool === tool),
  );
  canvas.classList.toggle("draw-mode", state.tool !== "cursor");
  if (state.tool !== "cursor") selectDrawing(null);
  log.chart.info("DRAWING_TOOL_SELECTED", { tool: state.tool });
}
function setDrawingToolsActive(active) {
  const toolbar = $(".top-drawing-tools");
  if (!toolbar) return;
  toolbar.classList.toggle("hidden", !active);
  toolbar.setAttribute("aria-hidden", String(!active));
  ["#undoBtn", "#redoBtn", "#hideAllBtn"].forEach((selector) => {
    const control = $(selector);
    if (control) control.disabled = !active;
  });
  if (!active && (state.tool !== "cursor" || state.draft)) {
    state.draft = null;
    state.interaction = null;
    selectDrawingTool("cursor");
    drawAll();
  }
}
function cancelDrawingTool(reason, { preservePath = false } = {}) {
  if (preservePath && state.draft?.type === "path" && state.draft.points.length > 1) {
    const id = state.draft.id;
    finishDraft();
    toast("Path kept and drawing tool deselected");
    log.chart.info("PATH_DRAFT_PRESERVED", { id, reason });
    return;
  }
  const wasActive = state.tool !== "cursor" || state.draft;
  state.draft = null;
  state.interaction = null;
  selectDrawingTool("cursor");
  drawAll();
  if (wasActive) {
    toast("Drawing tool cancelled");
    log.chart.info("DRAWING_TOOL_CANCELLED", { reason });
  }
}
$(".top-drawing-tools").onclick = (event) => {
  if (!chartWorkspaceActive()) return;
  const button = event.target.closest("[data-drawing-tool]");
  if (button) selectDrawingTool(button.dataset.drawingTool);
};
function moveDrawingTool(id, direction) {
  const from = drawingTools.indexOf(id);
  const to = from + direction;
  if (from < 0 || to < 0 || to >= drawingTools.length) return;
  [drawingTools[from], drawingTools[to]] = [drawingTools[to], drawingTools[from]];
  localStorage.setItem(DRAWING_TOOL_ORDER_KEY, JSON.stringify(drawingTools));
  renderDrawingToolbar(id);
  toast(`${drawingToolById.get(id)} moved ${direction < 0 ? "left" : "right"}`);
}
const drawingToolbar = $(".top-drawing-tools");
// Let the browser pan the outer mobile header, including gestures starting on
// a tool. A completed drag must never activate the tool underneath the finger.
let toolbarTouch = null;
let suppressToolbarClick = false;
drawingToolbar.addEventListener("pointerdown", (event) => {
  suppressToolbarClick = false;
  toolbarTouch = event.pointerType !== "mouse" && window.matchMedia("(max-width: 760px)").matches
    ? { id: event.pointerId, x: event.clientX, y: event.clientY } : null;
}, { passive: true });
drawingToolbar.addEventListener("pointermove", (event) => {
  if (toolbarTouch?.id === event.pointerId &&
      Math.hypot(event.clientX - toolbarTouch.x, event.clientY - toolbarTouch.y) > 8)
    suppressToolbarClick = true;
}, { passive: true });
drawingToolbar.addEventListener("pointercancel", () => {
  if (toolbarTouch) suppressToolbarClick = true;
  toolbarTouch = null;
}, { passive: true });
drawingToolbar.addEventListener("pointerup", () => { toolbarTouch = null; }, { passive: true });
drawingToolbar.addEventListener("click", (event) => {
  if (suppressToolbarClick && event.detail !== 0) {
    event.preventDefault();
    event.stopImmediatePropagation();
  }
  suppressToolbarClick = false;
}, true);
window.matchMedia("(max-width: 760px)").addEventListener("change", () => renderDrawingToolbar());
let draggedDrawingTool = null;
drawingToolbar.addEventListener("dragstart", (event) => {
  if (window.matchMedia("(max-width: 760px)").matches) return;
  const button = event.target.closest("[data-drawing-tool]");
  if (!button) return;
  draggedDrawingTool = button.dataset.drawingTool;
  event.dataTransfer.effectAllowed = "move";
  event.dataTransfer.setData("text/plain", draggedDrawingTool);
  button.classList.add("is-dragging");
});
drawingToolbar.addEventListener("dragend", (event) => {
  event.target.closest("[data-drawing-tool]")?.classList.remove("is-dragging");
  draggedDrawingTool = null;
});
drawingToolbar.addEventListener("dragover", (event) => {
  if (!window.matchMedia("(max-width: 760px)").matches) event.preventDefault();
});
drawingToolbar.addEventListener("drop", (event) => {
  if (window.matchMedia("(max-width: 760px)").matches) return;
  event.preventDefault();
  const target = event.target.closest("[data-drawing-tool]");
  const source = draggedDrawingTool || event.dataTransfer.getData("text/plain");
  if (!target || !source || target.dataset.drawingTool === source) return;
  const from = drawingTools.indexOf(source);
  const to = drawingTools.indexOf(target.dataset.drawingTool);
  drawingTools.splice(from, 1);
  drawingTools.splice(to, 0, source);
  localStorage.setItem(DRAWING_TOOL_ORDER_KEY, JSON.stringify(drawingTools));
  renderDrawingToolbar(source);
  toast(`${drawingToolById.get(source)} order saved`);
});
drawingToolbar.addEventListener("keydown", (event) => {
  const button = event.target.closest("[data-drawing-tool]");
  if (window.matchMedia("(max-width: 760px)").matches || !button || !event.altKey || !["ArrowLeft", "ArrowRight"].includes(event.key)) return;
  event.preventDefault();
  moveDrawingTool(button.dataset.drawingTool, event.key === "ArrowLeft" ? -1 : 1);
});
function startGroupSelection(event) {
  const p = point(event);
  if (p.time == null || p.price == null) return false;
  event.preventDefault();
  event.stopPropagation();
  state.selected = null;
  state.selectedIds = [];
  state.selectionBox = { a: p, b: p };
  state.interaction = { mode: "select" };
  shell.setPointerCapture(event.pointerId);
  drawAll();
  return true;
}
canvas.onpointerdown = (e) => {
  if (!chartWorkspaceActive()) return;
  if (e.button === 2) {
    return;
  }
  if (!isDrawingSurface(point(e))) return;
  if (state.tool === "cursor") {
    if (e.ctrlKey || e.metaKey) startGroupSelection(e);
    return;
  }
  let p = point(e);
  if (p.time == null || p.price == null) {
    toast("Load candle data before drawing");
    return;
  }
  if (state.tool === "zoom") {
    const scale = chart.timeScale();
    const current = scale.options().barSpacing || 8;
    scale.applyOptions({ barSpacing: Math.min(80, current * 1.55) });
    state.tool = "cursor";
    $$('[data-tool]').forEach((x) =>
      x.classList.toggle("active", x.dataset.tool === "cursor"),
    );
    canvas.classList.remove("draw-mode");
    return;
  }
  if (state.tool === "erase") {
    const d = hitTest(p);
    if (d) {
      checkpoint();
      state.drawings = state.drawings.filter((x) => x.id !== d.id);
      saveDrawings();
      drawAll();
    }
    return;
  }
  if (state.tool === "text") {
    const text = prompt("Text note");
    if (text) {
      const d = newDrawing("text", p);
      d.text = text;
      state.draft = d;
      finishDraft();
    }
    return;
  }
  if (state.tool === "path") {
    if (!state.draft) {
      state.draft = newDrawing("path", p);
      state.draft.preview = p;
      toast("Click to add points • Enter or double-click to finish");
    } else {
      state.draft.points.push(p);
      state.draft.b = clone(p);
      state.draft.preview = p;
    }
    drawAll();
    return;
  }
  if (state.draft && twoClickTools.has(state.tool)) {
    p = constrainLinePoint(state.draft.a, p, e.shiftKey);
    state.draft.b = p;
    finishDraft();
    return;
  }
  state.draft = newDrawing(state.tool, p);
  if (!twoClickTools.has(state.tool)) canvas.setPointerCapture(e.pointerId);
};
canvas.onpointermove = (e) => {
  if (!state.draft) return;
  const p = constrainLinePoint(state.draft.a, point(e), e.shiftKey);
  if (state.draft.type === "path") {
    state.draft.preview = p;
    drawAll();
    return;
  }
  state.draft.b = p;
  if (state.tool === "brush") state.draft.points.push(p);
  drawAll();
};
canvas.onpointerup = () => {
  if (!state.draft) return;
  if (twoClickTools.has(state.tool) || state.draft.type === "path") return;
  finishDraft();
};
// Capture active drawing gestures before Lightweight Charts can consume them.
// The canvas remains the rendering surface, while the shell is the reliable input surface.
shell.addEventListener(
  "pointerdown",
  (event) => {
    if (!chartWorkspaceActive()) return;
    if (state.tool === "cursor") return;
    if (event.button === 2) {
      event.preventDefault();
      event.stopImmediatePropagation();
      return;
    }
    event.preventDefault();
    event.stopImmediatePropagation();
    canvas.onpointerdown(event);
  },
  true,
);
shell.addEventListener(
  "pointermove",
  (event) => {
    if (!state.draft || state.tool === "cursor") return;
    event.preventDefault();
    event.stopImmediatePropagation();
    canvas.onpointermove(event);
  },
  true,
);
shell.addEventListener(
  "pointerup",
  (event) => {
    if (!state.draft || state.tool === "cursor") return;
    event.preventDefault();
    event.stopImmediatePropagation();
    canvas.onpointerup(event);
  },
  true,
);
shell.addEventListener(
  "dblclick",
  (event) => {
    if (state.draft?.type !== "path" || state.draft.points.length < 2) return;
    event.preventDefault();
    event.stopImmediatePropagation();
    finishDraft();
  },
  true,
);
shell.addEventListener(
  "pointerdown",
  (e) => {
    if (state.tool !== "cursor" || e.target === canvas) return;
    // The floating editor lives above the chart but is still inside the shell.
    // Do not treat a click on one of its controls (including the drag grip) as
    // an empty-chart click that clears the selected drawing.
    if (e.target.closest("#drawingToolbar")) return;
    const p = point(e);
    if (!isDrawingSurface(p)) return;
    if ((e.ctrlKey || e.metaKey) && startGroupSelection(e)) return;
    const d = hitTest(p),
      indicatorItem = d ? null : indicatorHitTest(p);
    if (indicatorItem) {
      e.preventDefault();
      e.stopPropagation();
      selectIndicatorObject(indicatorItem.id);
      if (!indicatorItem.locked) {
        checkpoint();
        state.interaction = { indicatorId: indicatorItem.id, mode: "indicator-move", last: p };
        canvas.classList.add("selection-active");
        shell.setPointerCapture(e.pointerId);
      }
      return;
    }
    if (!d) {
      selectDrawing(null);
      return;
    }
    e.preventDefault();
    e.stopPropagation();
    selectDrawing(d.id);
    if (d.locked) return;
    checkpoint();
    const a = xy(d.a),
      b = xy(d.b || d.a);
    let mode = "move";
    const isFreeform = ["brush", "path"].includes(d.type);
    let vertexIndex = -1;
    if (d.type === "path") {
      const vertices = (d.points || []).map(xy);
      vertexIndex = vertices.findIndex(
        (vertex) => valid(vertex) && Math.hypot(p.x - vertex.x, p.y - vertex.y) <= 12,
      );
      if (vertexIndex >= 0) mode = "path-vertex";
    }
    if (!isFreeform && Math.hypot(p.x - a.x, p.y - a.y) < 7) mode = "a";
    else if (
      !isFreeform &&
      Math.hypot(p.x - b.x, p.y - b.y) < 9 &&
      !["hline", "vline", "text"].includes(d.type)
    )
      mode = "b";
    state.interaction = { id: d.id, mode, last: p, vertexIndex };
    canvas.classList.add("selection-active");
    shell.setPointerCapture(e.pointerId);
  },
  true,
);
shell.addEventListener(
  "pointermove",
  (e) => {
    if (!state.interaction) return;
    e.preventDefault();
    e.stopPropagation();
    const p = point(e);
    if (!isDrawingSurface(p)) return;
    if (state.interaction.mode === "select") {
      state.selectionBox.b = p;
      drawAll();
      return;
    }
    if (state.interaction.mode === "indicator-move") {
      const indicatorItem = indicatorObject(state.interaction.indicatorId);
      if (!indicatorItem || indicatorItem.locked) return;
      indicatorItem.offsetX = (Number(indicatorItem.offsetX) || 0) + p.x - state.interaction.last.x;
      indicatorItem.offsetY = (Number(indicatorItem.offsetY) || 0) + p.y - state.interaction.last.y;
      indicatorItem.customized = true;
      state.interaction.last = p;
      drawAll();
      return;
    }
    const
      d = selected();
    if (!d || p.time == null || p.price == null) return;
    if (state.interaction.mode === "path-vertex") {
      const index = state.interaction.vertexIndex;
      if (!Array.isArray(d.points) || index < 0 || index >= d.points.length) return;
      d.points[index] = clone(p);
      d.a = clone(d.points[0]);
      d.b = clone(d.points.at(-1));
    } else if (state.interaction.mode === "move") {
      moveDrawing(
        d,
        Number(p.time) - Number(state.interaction.last.time),
        Number(p.price) - Number(state.interaction.last.price),
        Number.isFinite(Number(p.logical)) && Number.isFinite(Number(state.interaction.last.logical))
          ? Number(p.logical) - Number(state.interaction.last.logical)
          : 0,
      );
    } else d[state.interaction.mode] = p;
    state.interaction.last = p;
    drawAll();
  },
  true,
);
shell.addEventListener(
  "pointerup",
  (e) => {
    if (!state.interaction) return;
    e.preventDefault();
    e.stopPropagation();
    if (state.interaction.mode === "select" && state.selectionBox) {
      const { a, b } = state.selectionBox,
        left = Math.min(a.x, b.x),
        right = Math.max(a.x, b.x),
        top = Math.min(a.y, b.y),
        bottom = Math.max(a.y, b.y);
      state.selectedIds = state.drawings
        .filter((drawing) => {
          if (drawing.hidden) return false;
          const points = (drawing.points?.length ? drawing.points : [drawing.a, drawing.b || drawing.a])
            .map(xy)
            .filter(valid);
          if (!points.length) return false;
          const xs = points.map((point) => point.x);
          const ys = points.map((point) => point.y);
          return Math.max(...xs) >= left && Math.min(...xs) <= right &&
            Math.max(...ys) >= top && Math.min(...ys) <= bottom;
        })
        .map((drawing) => drawing.id);
      state.selected = state.selectedIds[0] || null;
      state.selectionBox = null;
      toast(`${state.selectedIds.length} drawings selected`);
      log.chart.info("DRAWING_MULTI_SELECTION_COMPLETED", {
        selectedCount: state.selectedIds.length,
        ids: state.selectedIds,
      });
      updateToolbar();
      renderObjectTree();
    }
    state.interaction = null;
    canvas.classList.remove("selection-active");
    saveDrawings();
    drawAll();
  },
  true,
);
function changeStyle(persist = true) {
  const indicatorItem = selectedIndicatorObject();
  if (indicatorItem) {
    if (indicatorItem.locked) return;
    indicatorItem.color = $("#strokeColor").value;
    indicatorItem.fill = $("#fillColor").value;
    indicatorItem.width = +$("#lineWidth").value;
    indicatorItem.lineStyle = $("#lineStyle").value;
    indicatorItem.opacity = +$("#fillOpacity").value;
    indicatorItem.customized = true;
    if (indicatorItem.type === "indicator-label") indicatorItem.text = $("#objectText").value;
    if (indicatorItem.type === "indicator-label") indicatorItem.size = +$("#objectSize").value;
    if (persist) renderObjectTree();
    drawAll();
    return;
  }
  const targets = state.drawings.filter((drawing) =>
    state.selectedIds.includes(drawing.id),
  );
  if (!targets.length) return;
  targets.forEach((d) => {
    d.style = {
      stroke: $("#strokeColor").value,
      fill: $("#fillColor").value,
      width: +$("#lineWidth").value,
      style: $("#lineStyle").value,
      opacity: +$("#fillOpacity").value,
    };
    if (d.type === "text") {
      d.text = $("#objectText").value || d.text;
      d.textSize = +$("#objectSize").value || d.textSize || 13;
    }
  });
  if (persist) saveDrawings();
  drawAll();
}
["strokeColor", "fillColor", "lineWidth", "lineStyle", "fillOpacity", "objectText", "objectSize"].forEach(
  (id) => {
    $("#" + id).addEventListener("input", () => changeStyle(false));
    $("#" + id).addEventListener("change", () => changeStyle(true));
  },
);
$("#lockDrawing").onclick = () => {
  const indicatorItem = selectedIndicatorObject();
  if (indicatorItem) {
    indicatorItem.locked = !indicatorItem.locked;
    updateToolbar();
    renderObjectTree();
    return;
  }
  const d = selected();
  if (!d) return;
  d.locked = !d.locked;
  saveDrawings();
  updateToolbar();
  drawAll();
};
$("#copyDrawing").onclick = () => {
  const d = selected();
  if (!d) return;
  checkpoint();
  const copy = clone(d);
  copy.id = crypto.randomUUID();
  moveDrawing(copy, state.tf * 3, (state.data.at(-1)?.close || 1) * 0.001);
  state.drawings.push(copy);
  selectDrawing(copy.id);
  saveDrawings();
};
$("#deleteDrawing").onclick = () => {
  const indicatorItem = selectedIndicatorObject();
  if (indicatorItem) {
    indicatorItem.hidden = true;
    state.indicator.selectedObjectId = null;
    updateToolbar();
    renderObjectTree();
    drawAll();
    return;
  }
  if (!state.selectedIds.length) return;
  const removedIds = [...state.selectedIds];
  checkpoint();
  state.drawings = state.drawings.filter(
    (x) => !state.selectedIds.includes(x.id),
  );
  selectDrawing(null);
  saveDrawings();
  log.chart.info("DRAWINGS_DELETED", {
    removedCount: removedIds.length,
    ids: removedIds,
    remaining: state.drawings.length,
  });
};
let latestRightClickAt = 0;
shell.addEventListener("contextmenu", (event) => {
  if (shell.classList.contains("candle-export-active")) return;
  event.preventDefault();
  const now = performance.now();
  const isDoubleRightClick = now - latestRightClickAt <= 360;
  latestRightClickAt = now;
  if (!isDoubleRightClick || (state.tool === "cursor" && !state.draft)) return;
  cancelDrawingTool("contextmenu", { preservePath: true });
});
$("#undoBtn").onclick = () => {
  const prev = state.history.pop();
  if (!prev) return;
  state.redo.push(historySnapshot());
  restoreHistorySnapshot(prev);
};
$("#redoBtn").onclick = () => {
  const next = state.redo.pop();
  if (!next) return;
  state.history.push(historySnapshot());
  if (state.history.length > 80) state.history.shift();
  restoreHistorySnapshot(next);
};
if ($("#lockAllBtn")) $("#lockAllBtn").onclick = () => {
  const lock = state.drawings.some((drawing) => !drawing.locked);
  state.drawings.forEach((drawing) => (drawing.locked = lock));
  state.drawingsLocked = lock;
  $("#lockAllBtn").classList.toggle("active", lock);
  saveDrawings();
  updateToolbar();
  drawAll();
};
$("#hideAllBtn").onclick = () => {
  const hide = state.drawings.some((drawing) => !drawing.hidden);
  state.drawings.forEach((drawing) => (drawing.hidden = hide));
  state.drawingsVisible = !hide;
  state.selected = null;
  const hideButton = $("#hideAllBtn");
  const hideLabel = hide ? "Show drawings" : "Hide drawings";
  hideButton.classList.toggle("active", hide);
  hideButton.classList.toggle("is-hidden-active", hide);
  hideButton.innerHTML = materialIcon(hide ? "visibility_off" : "visibility");
  hideButton.setAttribute("aria-pressed", String(hide));
  hideButton.setAttribute("aria-label", hideLabel);
  hideButton.title = hideLabel;
  if ($("#hideAllObjects")) $("#hideAllObjects").textContent = hide ? "Show all" : "Hide all";
  saveDrawings();
  updateToolbar();
  drawAll();
};
if ($("#clearBtn")) $("#clearBtn").onclick = () => {
  if (!state.drawings.length) return;
  checkpoint();
  state.drawings = [];
  selectDrawing(null);
  saveDrawings();
};
const PANEL_MIN_WIDTH = 270;
const PANEL_MAX_WIDTH = 560;
const PANEL_DEFAULT_WIDTH = 300;
const PANEL_WIDTH_KEYS = {
  objectTree: "qg:object-tree-width:v2",
  indicatorModal: "qg:indicator-panel-width:v2",
};
let pinnedPanel = null;
const panelWidths = Object.fromEntries(
  Object.entries(PANEL_WIDTH_KEYS).map(([id, key]) => {
    const value = Number(localStorage.getItem(key));
    return [id, Number.isFinite(value) && value > 0 ? value : PANEL_DEFAULT_WIDTH];
  }),
);
function panelWidthLimit() {
  const workspaceWidth = $(".workspace").clientWidth;
  return Math.max(
    PANEL_MIN_WIDTH,
    Math.min(PANEL_MAX_WIDTH, Math.floor(workspaceWidth * 0.45), workspaceWidth - 360),
  );
}
function applyPinnedPanelWidth(panel, width, persist = false, notify = true) {
  if (!panel) return;
  const next = Math.min(panelWidthLimit(), Math.max(PANEL_MIN_WIDTH, Math.round(width)));
  panelWidths[panel.id] = next;
  if (panel === pinnedPanel)
    $(".workspace").style.setProperty("--qg-panel-width", `${next}px`);
  const handle = panel.querySelector(".panel-resize-handle");
  handle?.setAttribute("aria-valuenow", String(next));
  handle?.setAttribute("aria-valuemax", String(panelWidthLimit()));
  if (persist) localStorage.setItem(PANEL_WIDTH_KEYS[panel.id], String(next));
  if (notify) requestAnimationFrame(() => window.dispatchEvent(new Event("resize")));
}
function ensurePanelResizeHandle(panel) {
  if (panel.querySelector(".panel-resize-handle")) return;
  const handle = document.createElement("div");
  handle.className = "panel-resize-handle";
  handle.tabIndex = 0;
  handle.setAttribute("role", "separator");
  handle.setAttribute("aria-orientation", "vertical");
  handle.setAttribute("aria-label", "Resize pinned side panel");
  handle.setAttribute("aria-valuemin", String(PANEL_MIN_WIDTH));
  handle.setAttribute("aria-valuemax", String(PANEL_MAX_WIDTH));
  panel.prepend(handle);
  const resizeBy = (delta, persist = false) =>
    applyPinnedPanelWidth(panel, panelWidths[panel.id] + delta, persist);
  handle.addEventListener("keydown", (event) => {
    if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
    event.preventDefault();
    if (event.key === "Home") applyPinnedPanelWidth(panel, PANEL_MIN_WIDTH, true);
    else if (event.key === "End") applyPinnedPanelWidth(panel, panelWidthLimit(), true);
    else resizeBy((event.key === "ArrowLeft" ? 1 : -1) * (event.shiftKey ? 32 : 12), true);
  });
  handle.addEventListener("pointerdown", (event) => {
    if (!panel.classList.contains("is-pinned") || event.button !== 0) return;
    event.preventDefault();
    handle.setPointerCapture(event.pointerId);
    let previousClientX = event.clientX;
    let pendingWidth = panelWidths[panel.id];
    let resizeFrame = 0;
    const move = (moveEvent) => {
      if (moveEvent.pointerId !== event.pointerId) return;
      pendingWidth += previousClientX - moveEvent.clientX;
      previousClientX = moveEvent.clientX;
      if (!resizeFrame)
        resizeFrame = requestAnimationFrame(() => {
          resizeFrame = 0;
          applyPinnedPanelWidth(panel, pendingWidth);
        });
    };
    const stop = (stopEvent) => {
      if (stopEvent.type !== "blur" && stopEvent.pointerId !== event.pointerId) return;
      if (resizeFrame) cancelAnimationFrame(resizeFrame);
      applyPinnedPanelWidth(panel, pendingWidth, true);
      if (handle.hasPointerCapture(event.pointerId)) handle.releasePointerCapture(event.pointerId);
      window.removeEventListener("pointermove", move);
      window.removeEventListener("pointerup", stop);
      window.removeEventListener("pointercancel", stop);
      window.removeEventListener("blur", stop);
    };
    // Window listeners also retain drag continuity if capture is unavailable
    // or the cursor leaves the thin handle before the next event.
    window.addEventListener("pointermove", move);
    window.addEventListener("pointerup", stop);
    window.addEventListener("pointercancel", stop);
    window.addEventListener("blur", stop);
  });
}
function setPanelPinned(panel, pinned) {
  if (pinned && pinnedPanel && pinnedPanel !== panel) {
    pinnedPanel.classList.remove("is-pinned");
    const previousPin = pinnedPanel.querySelector(".panel-pin");
    if (previousPin) {
      previousPin.classList.remove("active");
      previousPin.setAttribute("aria-pressed", "false");
      previousPin.title = "Pin panel";
    }
  }
  pinnedPanel = pinned ? panel : (pinnedPanel === panel ? null : pinnedPanel);
  panel.classList.toggle("is-pinned", pinned);
  $(".workspace").classList.toggle("has-pinned-panel", Boolean(pinnedPanel));
  ensurePanelResizeHandle(panel);
  if (pinned) applyPinnedPanelWidth(panel, panelWidths[panel.id]);
  const dialog = panel.matches("#indicatorModal") ? panel.querySelector(".indicator-panel") : panel;
  dialog?.setAttribute("aria-modal", String(!pinned));
  const pin = panel.querySelector(".panel-pin");
  if (pin) {
    pin.classList.toggle("active", pinned);
    pin.setAttribute("aria-pressed", String(pinned));
    pin.title = pinned ? "Unpin panel" : "Pin panel";
  }
  requestAnimationFrame(() => window.dispatchEvent(new Event("resize")));
}
function closeSidePanel(panel) {
  setPanelPinned(panel, false);
  panel.classList.add("hidden");
}
function closeTransientPanels(event) {
  if (event?.target?.closest("#objectTree,#indicatorModal,#objectTreeBtn,#indicatorBtn")) return;
  const visiblePinnedPanel = [$("#objectTree"), $("#indicatorModal")].find(
    (panel) => panel.classList.contains("is-pinned") && !panel.classList.contains("hidden"),
  );
  if (visiblePinnedPanel) return;
  if (pinnedPanel && !pinnedPanel.classList.contains("hidden")) return;
  if (pinnedPanel?.classList.contains("hidden")) pinnedPanel = null;
  $("#objectTree").classList.add("hidden");
  $("#indicatorModal").classList.add("hidden");
}
$("#pinIndicatorPanel").onclick = () =>
  setPanelPinned($("#indicatorModal"), !$("#indicatorModal").classList.contains("is-pinned"));
$("#pinObjectTree").onclick = () =>
  setPanelPinned($("#objectTree"), !$("#objectTree").classList.contains("is-pinned"));
objectTreeBtn.onclick = () => {
  if (!chartWorkspaceActive()) return;
  if (!$("#objectTree").classList.contains("hidden")) {
    closeSidePanel($("#objectTree"));
    return;
  }
  setPanelPinned($("#indicatorModal"), false);
  $("#indicatorModal").classList.add("hidden");
  $("#objectTree").classList.remove("hidden");
  renderObjectTree();
};
$("#closeObjectTree").onclick = () => closeSidePanel($("#objectTree"));
window.addEventListener("resize", () => {
  if (pinnedPanel)
    applyPinnedPanelWidth(pinnedPanel, panelWidths[pinnedPanel.id], false, false);
});
$("#chart").addEventListener("pointerdown", closeTransientPanels);
$("#objectSearch").oninput = renderObjectTree;
function objectByTreeId(id) {
  return state.drawings.find((drawing) => drawing.id === id) || indicatorObject(id);
}
function focusObjectOnChart(item) {
  const time = item?.a?.time ?? item?.time;
  if (!Number.isFinite(Number(time)) || !state.data.length) return;
  const target = Number(time);
  const first = Number(state.data[0].time);
  const last = Number(state.data.at(-1).time);
  let index;
  if (target < first) index = (target - first) / state.tf;
  else if (target > last) index = (state.data.length - 1) + (target - last) / state.tf;
  else index = state.data.findIndex((candle) => Number(candle.time) >= target);
  chart.timeScale().setVisibleLogicalRange({
    from: index - 35,
    to: index + 35,
  });
  toast("Focused object on chart");
}
function selectTreeObject(id, append = false) {
  const item = objectByTreeId(id);
  if (!item) return;
  const current = append ? [...state.treeSelectedIds] : [];
  const exists = current.includes(id);
  state.treeSelectedIds = append
    ? (exists ? current.filter((selectedId) => selectedId !== id) : [...current, id])
    : [id];
  const manualIds = state.treeSelectedIds.filter((selectedId) => state.drawings.some((drawing) => drawing.id === selectedId));
  const indicatorIds = state.treeSelectedIds.filter((selectedId) => state.indicator.objectMap.has(selectedId));
  state.selectedIds = manualIds;
  state.selected = manualIds[0] || null;
  state.indicator.selectedObjectId = indicatorIds[0] || null;
  updateToolbar();
  renderObjectTree();
  drawAll();
}
function selectedTreeObjects({ fallbackToAll = true } = {}) {
  const selected = state.treeSelectedIds.map(objectByTreeId).filter(Boolean);
  return selected.length || !fallbackToAll
    ? selected
    : [...state.drawings, ...state.indicator.objects];
}
$("#newObjectFolder").onclick = () => {
  const name = prompt("Folder name");
  if (!name?.trim()) return;
  state.objectFolders.push({ id: crypto.randomUUID(), name: name.trim().slice(0, 36) });
  saveObjectTreePreferences();
  renderObjectTree();
};
$("#objectList").addEventListener("click", (event) => {
  const folderDelete = event.target.closest("[data-folder-delete]");
  if (folderDelete) {
    event.preventDefault();
    event.stopImmediatePropagation();
    const id = folderDelete.dataset.folderDelete;
    state.drawings.forEach((drawing) => {
      if (drawing.folderId === id) delete drawing.folderId;
    });
    state.objectFolders = state.objectFolders.filter((folder) => folder.id !== id);
    state.collapsedObjectFolders = state.collapsedObjectFolders.filter((folderId) => folderId !== id);
    saveObjectTreePreferences();
    saveDrawings();
    renderObjectTree();
    return;
  }
  const folderToggle = event.target.closest("[data-folder-toggle]");
  if (folderToggle) {
    event.preventDefault();
    event.stopImmediatePropagation();
    const id = folderToggle.dataset.folderToggle;
    state.collapsedObjectFolders = state.collapsedObjectFolders.includes(id)
      ? state.collapsedObjectFolders.filter((folderId) => folderId !== id)
      : [...state.collapsedObjectFolders, id];
    saveObjectTreePreferences();
    renderObjectTree();
    return;
  }
  const row = event.target.closest("[data-object],[data-indicator-object]");
  if (!row) return;
  event.preventDefault();
  event.stopImmediatePropagation();
  const id = row.dataset.object || row.dataset.indicatorObject;
  const item = objectByTreeId(id);
  const action = event.target.closest("[data-action]")?.dataset.action;
  if (!item) return;
  if (action === "focus") return focusObjectOnChart(item);
  if (action === "visibility") item.hidden = !item.hidden;
  else if (action === "lock") item.locked = !item.locked;
  else if (action === "delete") {
    if (state.drawings.includes(item)) {
      checkpoint();
      state.drawings = state.drawings.filter((drawing) => drawing !== item);
      state.treeSelectedIds = state.treeSelectedIds.filter((selectedId) => selectedId !== item.id);
    } else item.hidden = true;
  } else {
    selectTreeObject(id, event.shiftKey);
    return;
  }
  saveDrawings();
  updateToolbar();
  renderObjectTree();
  drawAll();
}, true);
$("#objectList").addEventListener("dragstart", (event) => {
  const row = event.target.closest("[data-object]");
  if (!row) return;
  event.dataTransfer.effectAllowed = "move";
  event.dataTransfer.setData("text/plain", row.dataset.object);
  row.classList.add("is-dragging");
});
$("#objectList").addEventListener("dragend", (event) => event.target.closest("[data-object]")?.classList.remove("is-dragging"));
$("#objectList").addEventListener("dragover", (event) => {
  if (event.target.closest("[data-folder-drop]")) event.preventDefault();
});
$("#objectList").addEventListener("drop", (event) => {
  const folder = event.target.closest("[data-folder-drop]");
  const id = event.dataTransfer.getData("text/plain");
  const drawing = state.drawings.find((item) => item.id === id);
  if (!folder || !drawing) return;
  event.preventDefault();
  drawing.folderId = folder.dataset.folderDrop === "manual-unfiled" ? undefined : folder.dataset.folderDrop;
  saveDrawings();
  renderObjectTree();
});
$("#lockAllObjects").onclick = () => {
  const targets = selectedTreeObjects();
  if (!targets.length) return;
  const lock = targets.some((item) => !item.locked);
  targets.forEach((item) => { item.locked = lock; });
  saveDrawings();
  updateToolbar();
  renderObjectTree();
  drawAll();
};
$("#deleteAllObjects").addEventListener("click", (event) => {
  event.preventDefault();
  event.stopImmediatePropagation();
  const targets = selectedTreeObjects();
  if (!targets.length) return;
  const manualIds = new Set(targets.filter((item) => state.drawings.includes(item)).map((item) => item.id));
  if (manualIds.size) {
    checkpoint();
    state.drawings = state.drawings.filter((item) => !manualIds.has(item.id));
  }
  targets.filter((item) => !state.drawings.includes(item) && state.indicator.objectMap.has(item.id)).forEach((item) => { item.hidden = true; });
  state.treeSelectedIds = [];
  state.selectedIds = [];
  state.selected = null;
  state.indicator.selectedObjectId = null;
  saveDrawings();
  updateToolbar();
  renderObjectTree();
  drawAll();
}, true);
$("#objectList").onclick = (e) => {
  const indicatorRow = e.target.closest("[data-indicator-object]");
  if (indicatorRow) {
    const item = indicatorObject(indicatorRow.dataset.indicatorObject);
    if (!item) return;
    const action = e.target.closest("[data-action]")?.dataset.action;
    if (action === "visibility") item.hidden = !item.hidden;
    else if (action === "lock") item.locked = !item.locked;
    else if (action === "delete") item.hidden = true;
    else {
      state.selected = null;
      state.selectedIds = [];
      state.indicator.selectedObjectId = item.id;
    }
    updateToolbar();
    renderObjectTree();
    drawAll();
    return;
  }
  const row = e.target.closest("[data-object]");
  if (!row) return;
  const d = state.drawings.find((x) => x.id === row.dataset.object);
  if (!d) return;
  const action = e.target.closest("[data-action]")?.dataset.action;
  if (action === "visibility") {
    d.hidden = !d.hidden;
    if (d.hidden && state.selected === d.id) state.selected = null;
    saveDrawings();
    updateToolbar();
    drawAll();
    return;
  }
  if (action === "lock") {
    d.locked = !d.locked;
    saveDrawings();
    selectDrawing(d.id);
    return;
  }
  if (action === "delete") {
    checkpoint();
    state.drawings = state.drawings.filter((x) => x.id !== d.id);
    if (state.selected === d.id) state.selected = null;
    saveDrawings();
    updateToolbar();
    drawAll();
    return;
  }
  selectDrawing(d.id);
};
if ($("#hideAllObjects")) $("#hideAllObjects").onclick = () => {
  const hide = state.drawings.some((d) => !d.hidden);
  state.drawings.forEach((d) => (d.hidden = hide));
  state.selected = null;
  saveDrawings();
  updateToolbar();
  drawAll();
  $("#hideAllObjects").textContent = hide ? "Show all" : "Hide all";
};
$("#deleteAllObjects").onclick = () => {
  if (!state.drawings.length) return;
  checkpoint();
  state.drawings = [];
  state.selected = null;
  saveDrawings();
  updateToolbar();
  drawAll();
};
function indicatorSettings() {
  const selectedDirection = $("[data-direction].active")?.dataset.direction || null;
  return {
    direction: selectedDirection,
    timeframe: $("#indicatorTf").value,
    bullFill: $("#bullFill").value,
    bullBorder: $("#bullBorder").value,
    bullOpacity: +$("#bullOpacity").value,
    bullWidth: +$("#bullWidth").value,
    bullLineStyle: $("#bullLineStyle").value,
    bearFill: $("#bearFill").value,
    bearBorder: $("#bearBorder").value,
    bearOpacity: +$("#bearOpacity").value,
    bearWidth: +$("#bearWidth").value,
    bearLineStyle: $("#bearLineStyle").value,
    reactionVisible: $("#reactionVisible").checked,
    blueLineEnabled: $("#blueLineEnabled").checked,
    aVisible: $("#aVisible").checked,
    sVisible: $("#sVisible").checked,
    eVisible: $("#eVisible").checked,
    stopAllVisible: $("#stopAllVisible").checked,
    eStopVisible: $("#eStopVisible").checked,
    orderVisible: $("#orderVisible").checked,
    orderStopVisible: $("#orderStopVisible").checked,
    blueColor: $("#blueColor").value,
    blueOpacity: +$("#blueOpacity").value,
    blueWidth: +$("#blueWidth").value,
    blueLineStyle: $("#blueLineStyle").value,
    aColor: $("#aColor").value,
    aSize: +$("#aSize").value,
    aGap: +$("#aGap").value,
    sBullColor: $("#sBullColor").value,
    sBearColor: $("#sBearColor").value,
    sSize: +$("#sSize").value,
    sGap: +$("#sGap").value,
    eBlueColor: $("#eBlueColor").value,
    eRedColor: $("#eRedColor").value,
    eSize: +$("#eSize").value,
    eGap: +$("#eGap").value,
    stopAllFill: $("#stopAllFill").value,
    stopAllBorder: $("#stopAllBorder").value,
    stopAllOpacity: +$("#stopAllOpacity").value,
    stopAllWidth: +$("#stopAllWidth").value,
    stopAllSize: +$("#stopAllSize").value,
    stopAllRadius: +$("#stopAllRadius").value,
    stopAllGap: +$("#stopAllGap").value,
    orderFill: $("#orderFill").value,
    orderOpacity: +$("#orderOpacity").value,
    orderColor: $("#orderColor").value,
    orderWidth: +$("#orderWidth").value,
    orderLineStyle: $("#orderLineStyle").value,
    orderStopColor: $("#orderStopColor").value,
    orderStopWidth: +$("#orderStopWidth").value,
    orderStopLineStyle: $("#orderStopLineStyle").value,
    orderStopCap: Math.min(200, Math.max(1, +$("#orderStopCap").value || 200)),
    eStopColor: $("#eStopColor").value,
    eStopWidth: +$("#eStopWidth").value,
    eStopLineStyle: $("#eStopLineStyle").value,
    numberEnabled: false,
    numberMode: "off",
  };
}
function indicatorStatus(text, type = "idle") {
  const root = $("#indicatorStatus");
  root.className = type;
  root.querySelector("span").textContent = text;
}
function calculationKey(settings, from, to, timeframe) {
  return JSON.stringify({
    id: state.file?.id,
    direction: settings.direction,
    timeframe,
    from,
    to,
  });
}
function applyVisualSettings(settings = indicatorSettings()) {
  state.indicator.settings = settings;
  if (state.indicator.results) {
    localStorage.setItem(
      "market-canvas:reaction-indicator",
      JSON.stringify({
        settings,
        from: $("#indicatorFrom").value,
        to: $("#indicatorTo").value,
        enabled: state.indicator.enabled,
      }),
    );
    drawAll();
  }
}
function setCalculationProgress(value, stage) {
  const progress = Math.max(0, Math.min(100, Math.round(value)));
  $("#calculationPercent").textContent = `${progress}%`;
  $("#calculationBar").style.width = `${progress}%`;
  $("#calculationStage").textContent = stage;
}
const calculationStageDescriptions = Object.freeze({
  "Validate request": "Checks the calculation request, range, direction, and required settings.",
  "Read source file": "Reads the selected raw candle file from local storage.",
  "Parse source JSON": "Converts the raw JSON text into candle records.",
  "Filter raw range": "Keeps only raw records inside the requested time range.",
  "Load Reaction engine": "Loads the maintained Reaction calculation module.",
  "Load Blue Line engine": "Loads the maintained Blue Line calculation module.",
  "Load A engine": "Loads the maintained A calculation module.",
  "Load S engine": "Loads the maintained S calculation module.",
  "Load E engine": "Loads the maintained E calculation module.",
  "Load StopAll engine": "Loads the maintained StopAll calculation module.",
  "Normalize raw candles": "Converts OHLC values to exact Decimal values and builds time buckets.",
  "Build lower candle views": "Creates chronological lower-timeframe candle objects for rule evaluation.",
  "Build timeframe candle views": "Creates the selected-timeframe candle objects for chart calculations.",
  "Select candle range": "Finds the inclusive candle indexes used for the requested range.",
  "Reaction": "Detects reaction and reset events for the specified direction.",
  "Reaction geometry": "Builds full-history reaction geometry required by downstream E logic.",
  "Blue Line": "Derives Blue Line structures from detected reactions and resets.",
  "A": "Derives A structures from the applicable Blue Line structures.",
  "S": "Derives S structures and their eligible order evidence.",
  "E": "Builds E structures and reconciles their lifecycle evidence.",
  "StopAll": "Detects StopAll events and reconciles their reset boundaries with E.",
  "Apply visibility filters": "Applies deterministic ownership and reset visibility rules to output objects.",
  "Serialize Reaction": "Converts reaction and reset objects to the stable response schema.",
  "Serialize output": "Converts all calculated objects to the stable response schema.",
  "Encode response JSON": "Encodes the completed calculation payload for transport to the browser.",
  "Calculation pipeline": "Marks completion of the deterministic Python calculation pipeline.",
  "Start Python calculation": "Starts the isolated Python calculation process.",
  "Response ready": "The local server has prepared the calculation response.",
  "Cached result": "Returns an unchanged calculation payload from the validated cache.",
  "HTTP request and server": "Sends the calculation request and waits for the local server response.",
  "Server cache read": "Reads a validated result from memory or the local cache file.",
  "Response parsing": "Reads and parses the returned calculation response in the browser.",
  "Prepare chart objects": "Builds browser drawing objects from the returned calculation payload.",
  "Canvas render": "Draws the chart and indicator objects on the canvas.",
});
function calculationStageDescription(label) {
  const normalized = String(label || "").replace(/^(Python|Browser)\s•\s/, "");
  const match = Object.keys(calculationStageDescriptions)
    .sort((a, b) => b.length - a.length)
    .find((stage) => normalized === stage || normalized.startsWith(`${stage} •`) || normalized.startsWith(`${stage} -`));
  return calculationStageDescriptions[match] || "Reports a calculation, transport, cache, or rendering event.";
}
function calculationStageTitle(label) {
  return ` title="${escapeHtml(calculationStageDescription(label))}"`;
}
function plannedCalculationStages(direction) {
  const selectedDirections = direction === "both" ? ["Bullish", "Bearish"] : [String(direction || "bullish").replace(/^./, (letter) => letter.toUpperCase())];
  const common = [
    "Validate request", "Read source file", "Parse source JSON", "Filter raw range",
    "Load Reaction engine", "Load Blue Line engine", "Load A engine", "Load S engine",
    "Load E engine", "Load StopAll engine", "Normalize raw candles", "Build lower candle views",
    "Build timeframe candle views", "Select candle range", "Reaction geometry • Bullish",
    "Reaction geometry • Bearish", "Start Python calculation", "Cached result",
  ];
  const directional = selectedDirections.flatMap((name) => [
    `Blue Line • ${name}`, `A • ${name}`, `S • ${name}`,
    `E • ${name} • initial`, `E • ${name} • S reconciliation`, `E • ${name} • final audit`,
    `Serialize Reaction - ${name}`, `Reconcile S visibility - ${name}`,
    `StopAll - ${name}`, `E - ${name} - StopAll reconciliation`,
    `Apply visibility filters - ${name}`, `Serialize output - ${name}`,
  ]);
  return [...common, ...directional,
    "Calculation pipeline", "Encode response JSON", "Response ready",
    "HTTP request and server", "Server cache read", "Response parsing",
    "Prepare chart objects", "Canvas render", "Pipeline error", "Unexpected pipeline event",
  ];
}
function calculationStageKey(label, status, planned) {
  if (status === "failed") return "Pipeline error";
  const text = String(label || "Pipeline event");
  const visibility = text.match(/^Reconcile S visibility - (Bullish|Bearish) - pass \d+$/);
  if (visibility) return `Reconcile S visibility - ${visibility[1]}`;
  const stopAll = text.match(/^StopAll - (Bullish|Bearish) - pass \d+$/);
  if (stopAll) return `StopAll - ${stopAll[1]}`;
  const eReconciliation = text.match(/^E - (Bullish|Bearish) - StopAll reconciliation \d+$/);
  if (eReconciliation) return `E - ${eReconciliation[1]} - StopAll reconciliation`;
  if (text.startsWith("Cached result")) return "Cached result";
  return planned.has(text) ? text : "Unexpected pipeline event";
}
function startCalculationProgress(requestId, direction) {
  $("#indicatorLoading").classList.remove("hidden");
  const plannedStages = plannedCalculationStages(direction);
  const planned = new Set(plannedStages);
  const stageAggregates = new Map(plannedStages.map((key) => [key, {
    key, label: key, runs: 0, totalDurationMs: 0, active: false, status: "pending",
  }]));
  $("#calculationSteps").innerHTML = plannedStages.map((stage, index) =>
    `<li data-stage="${escapeHtml(stage)}"><i aria-hidden="true">${index + 1}</i><span class="calculation-stage-copy"${calculationStageTitle(stage)}><b>${escapeHtml(stage)}</b><small></small></span><time>Pending</time></li>`,
  ).join("");
  $("#calculationStageCount").textContent = `${plannedStages.length} planned`;
  const started = performance.now();
  const completed = new Set();
  const startedStages = new Map();
  const events = [];
  let progressState = null;
  const source = new EventSource(`/api/reactions/progress?requestId=${encodeURIComponent(requestId)}`);
  const updateStage = (key, event) => {
    const { aggregate } = updateStageAggregate(stageAggregates, key, key, event);
    const stage = $(`#calculationSteps [data-stage="${CSS.escape(key)}"]`);
    return { stage, aggregate };
  };
  const update = () => {
    const active = [...startedStages.keys()].at(-1) || "Waiting for Python";
    const percent = Math.min(96, Math.round((completed.size / plannedStages.length) * 100));
    setCalculationProgress(percent, active);
    $("#calculationRemaining").textContent = `${completed.size} completed • ${plannedStages.length - completed.size - startedStages.size} remaining`;
    $("#calculationElapsed").textContent = `Elapsed ${formatDuration(performance.now() - started)}`;
  };
  const refreshActiveTimers = () => {
    const now = performance.now();
    startedStages.forEach((stageStarted, key) => {
      const stage = $(`#calculationSteps [data-stage="${CSS.escape(key)}"]`);
      const aggregate = stageAggregates.get(key);
      if (stage && aggregate)
        stage.querySelector("time").textContent = formatDuration(aggregate.totalDurationMs + now - stageStarted);
    });
  };
  const recordEvent = (event) => {
    events.push({
      status: event.status || "info",
      label: event.label || "Pipeline event",
      durationMs: Number.isFinite(Number(event.durationMs)) ? Number(event.durationMs) : null,
      elapsedMs: Math.round((performance.now() - started) * 100) / 100,
    });
    const stageKey = calculationStageKey(event.label, event.status, planned);
    const { stage, aggregate } = updateStage(stageKey, event);
    if (event.status === "started") {
      startedStages.delete(stageKey);
      startedStages.set(stageKey, performance.now());
    }
    if (["completed", "finished"].includes(event.status)) { completed.add(stageKey); startedStages.delete(stageKey); }
    if (stage && ["started", "completed", "finished", "failed"].includes(event.status)) {
      stage.className = event.status === "started" ? "active" : event.status === "failed" ? "failed" : "done";
      stage.classList.toggle("bottleneck", aggregate.totalDurationMs >= 60_000);
      stage.querySelector("small").textContent = aggregate.runs > 1 ? `${aggregate.runs}×` : "";
      stage.querySelector("small").title = aggregate.runs > 1 ? `${aggregate.runs} executions; time is the total.` : "";
      stage.querySelector("time").textContent = event.status === "started"
        ? formatDuration(aggregate.totalDurationMs)
        : event.status === "failed"
          ? "Failed"
          : aggregate.runs && aggregate.totalDurationMs >= 0
            ? formatDuration(aggregate.totalDurationMs)
            : "Completed";
    }
    update();
  };
  source.onmessage = (message) => {
    try { recordEvent(JSON.parse(message.data)); } catch { /* Ignore malformed progress events. */ }
  };
  source.onerror = () => {
    if (!progressState?.stopped)
      pushIndicatorActivity("WARNING", "Progress stream disconnected; the calculation request is still being verified.");
  };
  setCalculationProgress(0, "Connecting to local Python pipeline");
  $("#calculationRemaining").textContent = `${plannedStages.length} planned stages`;
  const timer = setInterval(() => {
    $("#calculationElapsed").textContent = `Elapsed ${formatDuration(performance.now() - started)}`;
    refreshActiveTimers();
  }, 250);
  progressState = { timer, started, source, completed, events, update, recordEvent, stopped: false, plannedStages, startedStages, stageAggregates };
  return progressState;
}
function stopCalculationProgress(progressState, success = true) {
  clearInterval(progressState.timer);
  progressState.stopped = true;
  progressState.source.close();
  if (success) {
    setCalculationProgress(100, "Calculation complete");
    let skipped = 0;
    $$("#calculationSteps li").forEach((stage) => {
      if (stage.className) return;
      stage.className = "skipped";
      stage.querySelector("time").textContent = "Not needed";
      skipped++;
    });
    $("#calculationRemaining").textContent = `${progressState.completed.size} completed • ${skipped} not needed`;
    $("#calculationElapsed").textContent = `Completed in ${formatDuration(performance.now() - progressState.started)}`;
    setTimeout(() => $("#indicatorLoading").classList.add("hidden"), 350);
  } else {
    $("#indicatorLoading").classList.add("hidden");
  }
}
function eventDetails(direction, group, type) {
  const events =
    type === "reactions"
      ? group.reactions
      : type === "blueLines"
        ? group.blueLines || []
        : type === "aZones"
          ? group.aZones || []
          : type === "sZones"
          ? group.sZones || []
          : type === "eZones"
            ? group.eZones || []
            : type === "stopAlls"
              ? group.stopAlls || []
            : group.resets;
  return events
    .map((event, index) => {
      if (type === "blueLines") {
        const detail = event.kind === "reset"
          ? `Reset after reaction ${event.reactionNumber} • broken ${event.brokenLevel} • one-fifth line ${event.linePrice}`
          : `Reaction ${event.reactionNumber} • strikes ${event.previousStrikeCount} → ${event.strikeCount} • Fib 0.618 ${event.fibonacciLevel} • one-third line ${event.linePrice}`;
        return `<li><b>${index + 1}. ${formatTehran(event.sourceTime, false)}</b><span>${detail}</span></li>`;
      }
      if (type === "aZones")
        return `<li><b>${index + 1}. A ${formatTehran(event.sourceTime, false)} • ${event.price}</b><span>Blue ${event.blue1Ordinal} → ${event.blue2Ordinal} • trigger ${formatTehran(event.triggerEventTime, false)} • reaction ${event.reactionNumber} at ${formatTehran(event.reactionFirstTime, false)}</span></li>`;
      if (type === "sZones") {
        const detail = event.formationType === "type3"
          ? `Type 3 • A ${event.aOrdinal} stopped ${formatTehran(event.aStopEventTime, false)} • reset reaction ${event.resetReactionNumber} at ${formatTehran(event.resetTime, false)} • decision ${formatTehran(event.decisionEventTime, false)}`
          : `${event.formationType || "simple"} • A ${event.aOrdinal} stopped ${formatTehran(event.aStopEventTime, false)} • ${event.orderDirection} order reaction ${event.orderReactionNumber} • stop ${event.orderStopLevel} • decision ${formatTehran(event.decisionEventTime, false)}`;
        return `<li><b>${index + 1}. S ${formatTehran(event.sourceTime, false)} • ${event.price}</b><span>${detail}</span></li>`;
      }
      if (type === "eZones")
        return `<li><b>${index + 1}. E${event.number} ${formatTehran(event.sourceTime, false)} • ${event.price}</b><span>${event.parentType} stopped ${formatTehran(event.parentStopEventTime, false)} • ${event.orderDirection} order reaction ${event.orderReactionNumber} • cause ${(event.orderCauses || ["legacy-unknown"]).join(" + ")} • stop ${event.orderStopLevel}</span></li>`;
      if (type === "stopAlls")
        return `<li><b>${index + 1}. StopAll${event.number} ${formatTehran(event.sourceTime, false)} • ${event.price}</b><span>${event.stoppedBehaviorType} group ${event.stoppedBehaviorKey} × ${event.stoppedBehaviorCount} • gate ${formatTehran(event.gateEventTime, false)} • ${event.orderDirection} order reaction ${event.orderReactionNumber} • stop ${event.orderStopLevel}</span></li>`;
      if (type === "resets")
        return `<li><b>${index + 1}. ${formatTehran(event.time, false)}</b><span>Index ${event.index} • broken ${event.brokenLevel}${event.secondTime ? ` • exact ${event.secondTime}` : ""}</span></li>`;
      return `<li><b>${index + 1}. ${direction === "bullish" ? "FirstRed" : "FirstGreen"} ${formatTehran(event.firstTime, false)}</b><span>${direction === "bullish" ? "Breakout" : "Breakdown"} ${formatTehran(event.breakTime, false)} • Top ${event.boxTop} • Bottom ${event.boxBottom} • ${event.mode === "A" ? "Leg-Start" : "Normal Search"}</span></li>`;
    })
    .join("");
}
function setIndicatorVisibility(enabled) {
  state.indicator.enabled = Boolean(enabled && state.indicator.results);
  $("#indicatorBtn").classList.toggle("active", state.indicator.enabled);
  const footer = $("#indicatorStatusFooter");
  if (footer) {
    footer.dataset.state = state.indicator.enabled ? "active" : "inactive";
    footer.title = state.indicator.enabled ? "Indicator is active" : "Indicator is inactive";
  }
  if (!state.indicator.enabled) {
    state.indicator.hitBoxes = [];
    state.indicator.selectedObjectId = null;
    updateToolbar();
  }
  // This switch changes presentation only. Keep payload, request identity,
  // per-object overrides and manual drawings intact for an immediate restore.
  try {
    const saved = localStorage.getItem("market-canvas:reaction-indicator");
    if (saved) {
      localStorage.setItem("market-canvas:reaction-indicator",
        JSON.stringify({ ...JSON.parse(saved), enabled: Boolean(enabled) }));
    }
  } catch { /* A storage failure must not block render-only visibility. */ }
  drawAll();
}
function setFooterCacheStatus(cache) {
  const source = String(cache || "").toLowerCase();
  const footer = $("#cacheStatusFooter");
  if (!footer) return;
  const fromCache = source === "file" || source === "memory" || source === "hit";
  const cold = source === "miss" || source === "cold";
  footer.dataset.state = fromCache ? "cache" : cold ? "cold" : "idle";
  footer.title = fromCache ? "Indicator result loaded from cache" : cold ? "Indicator result calculated without a cache hit" : "Calculation source is not available";
}
function formatDuration(durationMs) {
  const milliseconds = Math.max(0, Number(durationMs) || 0);
  if (milliseconds < 1000) return `${milliseconds.toFixed(2)}ms`;
  const seconds = milliseconds / 1000;
  if (seconds < 60) return `${seconds.toFixed(3)}s`;
  const minutes = Math.floor(seconds / 60);
  return `${minutes}m ${(seconds % 60).toFixed(3).padStart(6, "0")}s`;
}
function calculationTraceAggregates(events, direction) {
  const planned = new Set(plannedCalculationStages(direction));
  const aggregates = new Map();
  for (const event of events || []) {
    const key = calculationStageKey(event.label, event.status, planned);
    updateStageAggregate(aggregates, key, key, event);
  }
  return [...aggregates.values()];
}
function indicatorLogTime(timestamp) {
  const date = new Date(timestamp);
  const base = new Intl.DateTimeFormat("en-GB", {
    timeZone: TEHRAN,
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hourCycle: "h23",
  }).format(date);
  return `${base}.${String(date.getMilliseconds()).padStart(3, "0")}`;
}
function renderIndicatorActivity() {
  const root = $("#indicatorInfo");
  if (!root) return;
  const last = state.indicator.lastCalculation;
  const logs = state.indicator.activity
    .slice()
    .reverse()
    .map((entry) => `<li data-level="${entry.level.toLowerCase()}"><time>${indicatorLogTime(entry.time)}</time><b>${entry.level}</b><span>${entry.message}${entry.durationMs != null ? ` • ${formatDuration(entry.durationMs)}` : ""}</span></li>`)
    .join("");
  root.innerHTML = `<section class="info-last-calculation"><span>Last calculation</span><strong>${last ? formatDuration(last.durationMs) : "—"}</strong><small>${last?.status || "No completed calculation"}</small></section><section class="indicator-activity"><h4>Activity, warnings & errors</h4><ol>${logs || '<li class="activity-empty"><span>Calculation events, warnings, and errors will appear here.</span></li>'}</ol></section>${state.indicator.infoDetails || ""}`;
  if ($("#infoBadge")) $("#infoBadge").textContent = String(state.indicator.activity.length);
}
function pushIndicatorActivity(level, message, details = {}) {
  state.indicator.activity.push({
    time: Date.now(),
    level: level.toUpperCase(),
    message,
    durationMs: details.durationMs,
  });
  if (state.indicator.activity.length > 150)
    state.indicator.activity.splice(0, state.indicator.activity.length - 150);
  renderIndicatorActivity();
}
function renderIndicatorInfo() {
  const payload = state.indicator.results;
  if (!payload) {
    state.indicator.infoDetails = "";
    renderIndicatorActivity();
    return;
  }
  let reactionTotal = 0,
    resetTotal = 0,
    blueLineTotal = 0,
    aTotal = 0,
    sTotal = 0,
    eTotal = 0,
    stopAllTotal = 0;
  const groups = Object.entries(payload.directions)
    .map(([direction, group]) => {
      reactionTotal += group.reactions.length;
      resetTotal += group.resets.length;
      blueLineTotal += (group.blueLines || []).length;
      aTotal += (group.aZones || []).length;
      sTotal += (group.sZones || []).length;
      eTotal += (group.eZones || []).length;
      stopAllTotal += (group.stopAlls || []).length;
      return `<section class="info-direction ${direction}"><header><i></i><strong>${direction === "bullish" ? "Bullish" : "Bearish"}</strong><span>${group.reactions.length} reactions • ${(group.blueLines || []).length} Blue Lines • ${(group.aZones || []).length} A • ${(group.sZones || []).length} S • ${(group.eZones || []).length} E • ${(group.stopAlls || []).length} StopAll</span></header><details><summary>Reactions <b>${group.reactions.length}</b></summary><ol>${eventDetails(direction, group, "reactions")}</ol></details><details><summary>Blue Lines <b>${(group.blueLines || []).length}</b></summary><ol>${eventDetails(direction, group, "blueLines")}</ol></details><details><summary>A <b>${(group.aZones || []).length}</b></summary><ol>${eventDetails(direction, group, "aZones")}</ol></details><details><summary>S <b>${(group.sZones || []).length}</b></summary><ol>${eventDetails(direction, group, "sZones")}</ol></details><details><summary>E <b>${(group.eZones || []).length}</b></summary><ol>${eventDetails(direction, group, "eZones")}</ol></details><details><summary>StopAll <b>${(group.stopAlls || []).length}</b></summary><ol>${eventDetails(direction, group, "stopAlls")}</ol></details><details><summary>Resets <b>${group.resets.length}</b></summary><ol>${eventDetails(direction, group, "resets")}</ol></details></section>`;
    })
    .join("");
  if (!$("#infoBadge") || !$("#indicatorInfo")) {
    log.indicator.debug("INFO_PANEL_DISABLED", { reactionTotal });
    return;
  }
  const calculationTiming = state.indicator.lastCalculation?.timing || {};
  const backendPhases = Object.entries(payload.timings?.phasesMs || {});
  const frontendPhases = [
    ["HTTP request and server", calculationTiming.requestAndComputeMs],
    ["Server cache read", calculationTiming.cacheReadMs],
    ["Response parsing", calculationTiming.responseParseMs],
    ["Prepare chart objects", calculationTiming.objectPreparationMs],
    ["Canvas render", calculationTiming.canvasRenderMs],
  ].filter(([, duration]) => Number.isFinite(Number(duration)));
  const timingRows = [
    ...backendPhases.map(([label, duration]) => ["Python • " + label, duration]),
    ...frontendPhases.map(([label, duration]) => ["Browser • " + label, duration]),
  ].map(([label, duration]) => `<div><span${calculationStageTitle(label)}>${escapeHtml(label)}</span><strong class="${Number(duration) >= 60_000 ? "bottleneck" : ""}">${formatDuration(duration)}</strong></div>`).join("") || '<p class="info-empty">Timing data will appear after the next calculation.</p>';
  const progressTrace = calculationTiming.progressEvents || [];
  const stageTotals = calculationTraceAggregates(progressTrace, state.indicator.lastCalculation?.direction || state.indicator.settings?.direction);
  const stageRows = stageTotals
    .map((stage, index) => `<li data-status="${escapeHtml(stage.status)}"><i>${index + 1}</i><span${calculationStageTitle(stage.label)}>${escapeHtml(stage.label)}</span>${stage.runs > 1 ? `<small title="${stage.runs} executions; time is the total.">${stage.runs}×</small>` : ""}<b class="${stage.totalDurationMs >= 60_000 ? "bottleneck" : ""}">${stage.runs ? formatDuration(stage.totalDurationMs) : stage.status === "failed" ? "Failed" : "Pending"}</b></li>`)
    .join("") || '<li class="timeline-empty"><span>No execution stages were recorded.</span></li>';
  const progressRows = progressTrace
    .map((event) => `<li data-status="${escapeHtml(event.status)}"><time>${formatDuration(event.elapsedMs)}</time><span${calculationStageTitle(event.label)}>${escapeHtml(event.label)}</span><b>${event.durationMs != null ? formatDuration(event.durationMs) : escapeHtml(event.status)}</b></li>`)
    .join("") || '<li><span>No popup trace was captured for this calculation.</span></li>';
  const timingSource = state.indicator.lastCalculation?.cache || "unknown";
  const bridgeTotal = payload.timings?.bridgeTotalMs;
  state.indicator.infoDetails = `<details class="info-analysis-details" open><summary>Calculation details <b>${reactionTotal} reactions</b></summary><div class="info-metrics"><div><span>Reactions</span><strong>${reactionTotal}</strong></div><div><span>Blue Lines</span><strong>${blueLineTotal}</strong></div><div><span>A</span><strong>${aTotal}</strong></div><div><span>S</span><strong>${sTotal}</strong></div><div><span>E</span><strong>${eTotal}</strong></div><div><span>StopAll</span><strong>${stopAllTotal}</strong></div><div><span>Resets</span><strong>${resetTotal}</strong></div><div><span>Timeframe</span><strong>${payload.timeframe || "—"}s</strong></div></div><section class="info-timing info-stage-summary"><header><span>Execution timing</span><strong>${formatDuration(state.indicator.lastCalculation?.durationMs)}</strong></header><p>Cache: ${escapeHtml(timingSource)}${Number.isFinite(Number(bridgeTotal)) ? ` • Python bridge total: ${formatDuration(bridgeTotal)}` : ""}</p><ol>${stageRows}</ol></section><section class="info-timing info-engine-timing"><header><span>Engine timing details</span><strong>${backendPhases.length} measurements</strong></header><div class="info-timing-grid">${timingRows}</div></section><section class="info-timing info-progress-trace"><header><span>Complete execution log</span><strong>${progressTrace.length} events</strong></header><ol>${progressRows}</ol></section><div class="info-meta"><span>Engines</span><b>Reaction ${payload.version || "9.2.1"} • Blue Line ${payload.blueLineVersion || "3.0.0"} • A ${payload.aVersion || "2.0.0"} • S ${payload.sVersion || "4.0.0"} • E ${payload.eVersion || "—"} • StopAll ${payload.stopAllVersion || "—"}</b><span>Range</span><b>${formatTehran(payload.actualFrom, false)} → ${formatTehran(payload.actualTo, false)}</b></div>${groups}</details>`;
  renderIndicatorActivity();
}
const pickerState = { target: null, trigger: null, year: 0, month: 0, day: 1, applyAfterSave: false };
const monthNames = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];
function displayPickerValue(value) {
  return value ? value.replace("T", "  ") : "Select date & time";
}
function setDateTimeValue(target, value) {
  const field = $(target),
    display = $(`${target}Display`);
  if (!field) {
    log.chart.error("DATE_FIELD_NOT_FOUND", new Error("Date input is missing"), { target, value });
    return false;
  }
  field.value = value || "";
  if (display) display.textContent = displayPickerValue(value);
  else log.chart.debug("DATE_DISPLAY_NOT_PRESENT", { target });
  return true;
}
function pickerValueParts(value) {
  const match = value?.match(
    /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})$/,
  );
  if (!match) return null;
  return match.slice(1).map(Number);
}
function renderPickerCalendar() {
  $("#pickerMonth").textContent =
    `${pickerState.month + 1}.${monthNames[pickerState.month]} ${pickerState.year}`;
  $("#pickerDateValue").textContent = `${String(pickerState.day).padStart(2, "0")} ${monthNames[pickerState.month]} ${pickerState.year}`;
  const firstWeekday = new Date(
      Date.UTC(pickerState.year, pickerState.month, 1),
    ).getUTCDay();
  const mondayFirstWeekday = (firstWeekday + 6) % 7,
    daysInMonth = new Date(
      Date.UTC(pickerState.year, pickerState.month + 1, 0),
    ).getUTCDate(),
    previousDays = new Date(
      Date.UTC(pickerState.year, pickerState.month, 0),
    ).getUTCDate();
  const cells = [];
  for (let slot = 0; slot < 42; slot++) {
    const relative = slot - mondayFirstWeekday + 1;
    let day = relative,
      offset = 0;
    if (relative < 1) {
      day = previousDays + relative;
      offset = -1;
    } else if (relative > daysInMonth) {
      day = relative - daysInMonth;
      offset = 1;
    }
    const selected = offset === 0 && day === pickerState.day;
    cells.push(
      `<button type="button" data-picker-day="${day}" data-month-offset="${offset}" class="${offset ? "outside" : ""} ${selected ? "selected" : ""}">${day}</button>`,
    );
  }
  $("#pickerDays").innerHTML = cells.join("");
}
function openDateTimePicker(target, applyAfterSave = false) {
  pickerState.target = target;
  pickerState.trigger = $(
    target === "#gotoInput" ? "#gotoPickerButton" : `${target}Button`,
  );
  pickerState.applyAfterSave = applyAfterSave;
  const targetField = $(target);
  if (!targetField) {
    log.chart.error("DATE_PICKER_TARGET_NOT_FOUND", new Error("Picker target is missing"), { target });
    return;
  }
  const fallback = inputFromTehran(state.raw.at(-1)?.time || Date.now() / 1000),
    parts = pickerValueParts(targetField.value || fallback) || pickerValueParts(fallback);
  if (!parts) {
    log.chart.error("DATE_PICKER_VALUE_INVALID", new Error("Unable to parse picker value"), { target, value: targetField.value, fallback });
    return;
  }
  [pickerState.year, pickerState.month, pickerState.day] = [
    parts[0],
    parts[1] - 1,
    parts[2],
  ];
  $("#pickerHour").value = String(parts[3]).padStart(2, "0");
  $("#pickerMinute").value = String(parts[4]).padStart(2, "0");
  $("#pickerSecond").value = String(parts[5]).padStart(2, "0");
  $("#pickerTitle").textContent =
    target === "#indicatorFrom" || target === "#candleRangeFrom"
      ? "Select start date & time"
      : target === "#gotoInput"
        ? "Go to date & time"
        : "Select end date & time";
  $("#pickerSave").textContent = applyAfterSave ? "Go to" : "Apply";
  renderPickerCalendar();
  const picker = $("#dateTimePicker");
  picker.classList.remove("hidden");
  requestAnimationFrame(positionDateTimePicker);
}
function positionDateTimePicker() {
  const picker = $("#dateTimePicker");
  picker.style.left = "";
  picker.style.top = "";
}
function closeDateTimePicker() {
  $("#dateTimePicker").classList.add("hidden");
  pickerState.trigger = null;
}
function movePickerMonth(delta) {
  pickerState.month += delta;
  if (pickerState.month < 0) {
    pickerState.month = 11;
    pickerState.year--;
  } else if (pickerState.month > 11) {
    pickerState.month = 0;
    pickerState.year++;
  }
  pickerState.day = Math.min(
    pickerState.day,
    new Date(Date.UTC(pickerState.year, pickerState.month + 1, 0)).getUTCDate(),
  );
  renderPickerCalendar();
}
function openIndicator() {
  if (!chartWorkspaceActive()) return;
  setPanelPinned($("#objectTree"), false);
  $("#objectTree").classList.add("hidden");
  $("#indicatorModal").classList.add("side-panel");
  log.indicator.info("SETTINGS_OPENED", {
    symbol: state.file?.symbol,
    chartTimeframeSeconds: state.tf,
    hasResults: Boolean(state.indicator.results),
  });
  if (!openIndicator.restored) {
    try {
      const saved = JSON.parse(
        localStorage.getItem("market-canvas:reaction-indicator") || "null",
      );
      if (saved?.settings) {
        const savedDirection = ["bullish", "bearish"].includes(
          saved.settings.direction,
        )
          ? saved.settings.direction
          : null;
        for (const [id, value] of Object.entries(saved.settings)) {
          const element = $("#" + indicatorControlId(id));
          if (!element) continue;
          let normalizedValue = id === "orderColor" && value === "#f59e0b"
            ? "#8a8f98"
            : value;
          if (
            saved.settings.stopAllSize == null &&
            (id === "sSize" || id === "eSize")
          )
            normalizedValue = 12;
          if (element.type === "checkbox") element.checked = Boolean(normalizedValue);
          else element.value = normalizedValue;
        }
        $$("[data-direction]").forEach((button) =>
          button.classList.toggle(
            "active",
            button.dataset.direction === savedDirection,
          ),
        );
        $$("[data-direction]").forEach((button) =>
          button.setAttribute(
            "aria-pressed",
            String(button.dataset.direction === savedDirection),
          ),
        );
        if (savedDirection)
          $(".trend-segment")?.setAttribute("data-trend", savedDirection);
        else $(".trend-segment")?.removeAttribute("data-trend");
        if (saved.from) setDateTimeValue("#indicatorFrom", saved.from);
        if (saved.to) setDateTimeValue("#indicatorTo", saved.to);
        $("#indicatorEnabled").checked = Boolean(saved.enabled);
      }
    } catch {
      localStorage.removeItem("market-canvas:reaction-indicator");
    }
    openIndicator.restored = true;
    updateStyleAvailability();
  }
  if (state.raw.length) {
    if (!$("#indicatorFrom").value)
      setDateTimeValue("#indicatorFrom", inputFromTehran(state.raw[0].time));
    if (!$("#indicatorTo").value)
      setDateTimeValue("#indicatorTo", inputFromTehran(state.raw.at(-1).time));
  }
  renderIndicatorActivity();
  $("#indicatorModal").classList.remove("hidden");
}
async function calculateIndicator() {
  if (state.indicator.loading || !state.file) return;
  const calculationStarted = performance.now();
  const direction = $("[data-direction].active")?.dataset.direction;
  if (!["bullish", "bearish"].includes(direction)) {
    indicatorStatus("Select Bullish or Bearish before calculating", "error");
    toast("Select a trend direction", "error");
    $("[data-direction]")?.focus();
    return;
  }
  const enabled = $("#indicatorEnabled").checked;
  if (!enabled) {
    setIndicatorVisibility(false);
    indicatorStatus("");
    log.indicator.info("DISABLED");
    return;
  }
  const from = parseTehranInput($("#indicatorFrom").value),
    to = parseTehranInput($("#indicatorTo").value);
  if (!Number.isFinite(from) || !Number.isFinite(to) || from > to) {
    indicatorStatus("Choose a valid Tehran time range", "error");
    toast("Invalid indicator time range");
    log.indicator.warn("INVALID_RANGE", { from, to });
    return;
  }
  if (from < state.raw[0].time || to > state.raw.at(-1).time) {
    indicatorStatus("Range is outside available candles", "error");
    toast("Indicator range is outside available data");
    log.indicator.warn("RANGE_OUTSIDE_SOURCE", {
      from,
      to,
      sourceFrom: state.raw[0].time,
      sourceTo: state.raw.at(-1).time,
    });
    return;
  }
  const settings = indicatorSettings(),
    timeframe = settings.timeframe === "follow" ? state.tf : +settings.timeframe,
    nextKey = calculationKey(settings, from, to, timeframe);
  if (state.indicator.results && state.indicator.calculationKey === nextKey) {
    setIndicatorVisibility(true);
    applyVisualSettings(settings);
    indicatorStatus("Appearance updated without recalculation", "success");
    toast("Indicator appearance updated");
    pushIndicatorActivity("INFO", "Appearance updated from the existing calculation");
    log.indicator.info("VISUAL_SETTINGS_APPLIED_FROM_CLIENT_CACHE", {
      timeframe,
      direction: settings.direction,
    });
    return;
  }
  state.indicator.loading = true;
  indicatorStatus("Calculation progress is open", "loading");
  $("#applyIndicator").disabled = true;
  const progressRequestId = crypto.randomUUID();
  const progressTimer = startCalculationProgress(progressRequestId, settings.direction);
  pushIndicatorActivity("INFO", "Calculation started");
  pushIndicatorActivity("DATA", `Validated ${formatTehran(from, false)} → ${formatTehran(to, false)}`);
  log.indicator.info("CALCULATION_STARTED", {
    symbol: state.file.symbol,
    timeframe,
    direction: settings.direction,
    from,
    to,
    visibility: {
      reaction: settings.reactionVisible,
      blueLine: settings.blueLineEnabled,
      a: settings.aVisible,
      s: settings.sVisible,
      e: settings.eVisible,
      stopAll: settings.stopAllVisible,
      eStops: settings.eStopVisible,
      orders: settings.orderVisible,
      orderStops: settings.orderStopVisible,
    },
  });
  let succeeded = false;
  try {
    const calculationSource = clone(state.file),
      requestStarted = performance.now();
    progressTimer.recordEvent({ status: "started", label: "HTTP request and server" });
    const r = await fetch("/api/reactions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          id: state.file.id,
          timeframe,
          from,
          to,
          direction: settings.direction,
          blueLines: true,
          requestId: progressRequestId,
        }),
      }),
      responseReceived = performance.now();
    progressTimer.recordEvent({
      status: "completed",
      label: "HTTP request and server",
      durationMs: responseReceived - requestStarted,
    });
    progressTimer.recordEvent({
      status: "completed",
      label: "Server cache read",
      durationMs: Number(r.headers.get("X-QG-Cache-Read-Ms") || 0),
    });
    pushIndicatorActivity("STEP", "Python pipeline response received");
    const payload = await r.json(),
      responseParsed = performance.now();
    progressTimer.recordEvent({
      status: "completed",
      label: "Response parsing",
      durationMs: responseParsed - responseReceived,
    });
    if (!r.ok) throw new Error(payload.error || "Calculation failed");
    state.indicator.enabled = $("#indicatorEnabled").checked;
    state.indicator.settings = settings;
    state.indicator.results = payload;
    state.indicator.resultContext = { source: calculationSource, timeframe, from, to, direction, calculationKey: nextKey, sourceFingerprint: r.headers.get("X-QG-Source-Fingerprint") };
    state.indicator.calculationKey = nextKey;
    const objectPreparationStarted = performance.now();
    rebuildIndicatorObjects();
    const objectPreparationCompleted = performance.now();
    progressTimer.recordEvent({
      status: "completed",
      label: "Prepare chart objects",
      durationMs: objectPreparationCompleted - objectPreparationStarted,
    });
    pushIndicatorActivity("STEP", "Chart layers prepared");
    const total = Object.values(payload.directions).reduce(
      (sum, x) => sum + x.reactions.length,
      0,
    ), elapsedSeconds = (performance.now() - calculationStarted) / 1000;
    indicatorStatus("", "success");
    $("#indicatorBtn").classList.toggle("active", state.indicator.enabled);
    $("#indicatorStatusFooter").dataset.state = state.indicator.enabled ? "active" : "inactive";
    localStorage.setItem(
      "market-canvas:reaction-indicator",
      JSON.stringify({
        settings,
        from: $("#indicatorFrom").value,
        to: $("#indicatorTo").value,
        enabled: state.indicator.enabled,
      }),
    );
    const renderStarted = performance.now();
    drawAll();
    const renderCompleted = performance.now();
    progressTimer.recordEvent({
      status: "completed",
      label: "Canvas render",
      durationMs: renderCompleted - renderStarted,
    });
    succeeded = true;
    toast(`${total} reactions plotted in ${elapsedSeconds.toFixed(1)} seconds`, "success");
    const counts = Object.fromEntries(
      Object.entries(payload.directions).map(([direction, group]) => [
        direction,
        {
          reactions: group.reactions?.length || 0,
          blueLines: group.blueLines?.length || 0,
          a: group.aZones?.length || 0,
          s: group.sZones?.length || 0,
          e: group.eZones?.length || 0,
        },
      ]),
    );
    const completedTiming = {
      durationMs: Math.round((performance.now() - calculationStarted) * 100) / 100,
      serverCache: r.headers.get("X-QG-Cache") || "unknown",
      timing: {
        requestAndComputeMs: Math.round((responseReceived - requestStarted) * 100) / 100,
        detectorMs: Number(r.headers.get("X-QG-Detector-Ms") || 0),
        serverMs: Number(r.headers.get("X-QG-Server-Ms") || 0),
        cacheReadMs: Number(r.headers.get("X-QG-Cache-Read-Ms") || 0),
        responseParseMs: Math.round((responseParsed - responseReceived) * 100) / 100,
        objectPreparationMs: Math.round((objectPreparationCompleted - objectPreparationStarted) * 100) / 100,
        canvasRenderMs: Math.round((renderCompleted - renderStarted) * 100) / 100,
        progressEvents: progressTimer.events,
      },
      timeframe,
      counts,
    };
    state.indicator.lastCalculation = {
      durationMs: completedTiming.durationMs,
      status: "Completed successfully",
      cache: completedTiming.serverCache,
      timeframe,
      direction: settings.direction,
      timing: completedTiming.timing,
    };
    pushIndicatorActivity("SUCCESS", "Indicator calculation completed", {
      durationMs: completedTiming.durationMs,
    });
    renderIndicatorInfo();
    window.__QG_PERF__ = {
      ...(window.__QG_PERF__ || {}),
      indicator: completedTiming,
    };
    setFooterCacheStatus(completedTiming.serverCache);
    $("#indicatorStatusFooter").title = state.indicator.enabled ? "Indicator is active" : "Indicator is inactive";
    log.indicator.info("CALCULATION_COMPLETED", completedTiming);
  } catch (error) {
    const failedDurationMs = Math.round((performance.now() - calculationStarted) * 100) / 100;
    state.indicator.lastCalculation = {
      durationMs: failedDurationMs,
      status: "Failed",
      timeframe: null,
    };
    pushIndicatorActivity("ERROR", error.message || "Indicator calculation failed", {
      durationMs: failedDurationMs,
    });
    indicatorStatus(error.message, "error");
    toast(error.message);
    log.indicator.error("CALCULATION_FAILED", error, {
      durationMs: failedDurationMs,
      symbol: state.file?.symbol,
    });
    $("#indicatorStatusFooter").dataset.state = "inactive";
    $("#indicatorStatusFooter").title = "Indicator is inactive after calculation error";
  } finally {
    stopCalculationProgress(progressTimer, succeeded);
    if (succeeded) renderIndicatorInfo();
    state.indicator.loading = false;
    $("#applyIndicator").disabled = false;
  }
}
$("#indicatorBtn").onclick = openIndicator;
$("#indicatorStatusFooter").onclick = openIndicator;
$("#reloadIndicatorBtn").onclick = async () => {
  if (state.indicator.loading || !state.file) return;
  $("#reloadIndicatorBtn").classList.add("is-loading");
  try {
    const response = await fetch("/api/reactions/cache", { method: "DELETE" });
    if (!response.ok) throw new Error("Unable to clear the indicator cache");
    const result = await response.json();
    state.indicator.results = null;
    state.indicator.calculationKey = null;
    state.indicator.objects = [];
    state.indicator.objectMap = new Map();
    state.indicator.selectedObjectId = null;
    $("#indicatorEnabled").checked = true;
    setFooterCacheStatus();
    setIndicatorVisibility(false);
    indicatorStatus("Cache cleared. Use Apply & calculate to run the indicator.");
    drawAll();
    log.indicator.info("CACHE_CLEARED", result);
    toast("Indicator cache cleared. Calculation has not started.");
  } catch (error) {
    log.indicator.error("RELOAD_FAILED", error);
    toast(error.message);
  } finally {
    $("#reloadIndicatorBtn").classList.remove("is-loading");
  }
};
$("#closeIndicator").onclick = $("#cancelIndicator").onclick = () =>
  closeSidePanel($("#indicatorModal"));
$("#indicatorModal").onclick = (e) => {
  if (e.target === $("#indicatorModal") && !$("#indicatorModal").classList.contains("is-pinned"))
    closeSidePanel($("#indicatorModal"));
};
$$("[data-indicator-tab]").forEach(
  (button) =>
    (button.onclick = () => {
      activateIndicatorTab(button.dataset.indicatorTab);
    }),
);
$$("[data-direction]").forEach(
  (button) =>
    (button.onclick = () => {
      $$("[data-direction]").forEach((x) =>
        x.classList.toggle("active", x === button),
      );
      $$("[data-direction]").forEach((x) =>
        x.setAttribute("aria-pressed", String(x === button)),
      );
      $(".trend-segment")?.setAttribute(
        "data-trend",
        button.dataset.direction,
      );
      toast(
        `${button.dataset.direction === "bullish" ? "Bullish" : "Bearish"} trend selected`,
        "info",
      );
    }),
);
$("#indicatorEnabled").onchange = () => {
  const enabled = $("#indicatorEnabled").checked;
  setIndicatorVisibility(enabled);
  indicatorStatus(enabled
    ? state.indicator.results ? "Cached indicator restored" : "Ready to calculate"
    : "");
};
$("#applyIndicator").onclick = async () => {
  await calculateIndicator();
  if (state.indicator.enabled && !$("#indicatorModal").classList.contains("is-pinned"))
    closeSidePanel($("#indicatorModal"));
};
document.addEventListener("click", (event) => {
  if (event.target.closest("#indicatorFromButton")) openDateTimePicker("#indicatorFrom");
  if (event.target.closest("#indicatorToButton")) openDateTimePicker("#indicatorTo");
});
$("#pickerClose").onclick = $("#pickerCancel").onclick = closeDateTimePicker;
$("#dateTimePicker").onclick = (event) => {
  if (event.target === $("#dateTimePicker")) closeDateTimePicker();
};
document.addEventListener("pointerdown", (event) => {
  const picker = $("#dateTimePicker");
  if (picker.classList.contains("hidden") || picker.contains(event.target) || pickerState.trigger?.contains(event.target)) return;
  closeDateTimePicker();
});
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && !$("#dateTimePicker").classList.contains("hidden")) {
    closeDateTimePicker();
  }
});
window.addEventListener("resize", positionDateTimePicker);
$("#pickerPrev").onclick = () => movePickerMonth(-1);
$("#pickerNext").onclick = () => movePickerMonth(1);
$("#pickerDays").onclick = (event) => {
  const button = event.target.closest("[data-picker-day]");
  if (!button) return;
  const offset = +button.dataset.monthOffset;
  if (offset) movePickerMonth(offset);
  pickerState.day = +button.dataset.pickerDay;
  renderPickerCalendar();
};
$("#pickerToday").onclick = () => {
  const parts = pickerValueParts(inputFromTehran(Date.now() / 1000));
  [pickerState.year, pickerState.month, pickerState.day] = [
    parts[0],
    parts[1] - 1,
    parts[2],
  ];
  $("#pickerHour").value = String(parts[3]).padStart(2, "0");
  $("#pickerMinute").value = String(parts[4]).padStart(2, "0");
  $("#pickerSecond").value = String(parts[5]).padStart(2, "0");
  renderPickerCalendar();
};
$("#pickerSave").onclick = () => {
  const value = `${pickerState.year}-${String(pickerState.month + 1).padStart(2, "0")}-${String(pickerState.day).padStart(2, "0")}T${$("#pickerHour").value}:${$("#pickerMinute").value}:${$("#pickerSecond").value}`;
  setDateTimeValue(pickerState.target, value);
  const applyAfterSave = pickerState.applyAfterSave;
  closeDateTimePicker();
  if (applyAfterSave) $("#gotoApply").click();
};
const visualSettingIds = [
  "bullFill",
  "bullBorder",
  "bullOpacity",
  "bullWidth",
  "bullLineStyle",
  "bearFill",
  "bearBorder",
  "bearOpacity",
  "bearWidth",
  "bearLineStyle",
  "reactionVisible",
  "blueLineEnabled",
  "aVisible",
  "sVisible",
  "eVisible",
  "stopAllVisible",
  "eStopVisible",
  "orderVisible",
  "orderStopVisible",
  "blueColor",
  "blueOpacity",
  "blueWidth",
  "blueLineStyle",
  "aColor",
  "aSize",
  "aGap",
  "sBullColor",
  "sBearColor",
  "sSize",
  "sGap",
  "eBlueColor",
  "eRedColor",
  "eSize",
  "eGap",
  "stopAllFill",
  "stopAllBorder",
  "stopAllOpacity",
  "stopAllWidth",
  "stopAllSize",
  "stopAllRadius",
  "stopAllGap",
  "orderFill",
  "orderColor",
  "orderOpacity",
  "orderWidth",
  "orderLineStyle",
  "orderStopColor",
  "orderStopWidth",
  "orderStopLineStyle",
  "orderStopCap",
  "eStopColor",
  "eStopWidth",
  "eStopLineStyle",
];
for (const id of visualSettingIds) {
  $("#" + id).oninput = () => {
    const valueLabel = $("#" + id + "Value");
    if (valueLabel)
      valueLabel.textContent =
        $("#" + id).value + (id.includes("Opacity") ? "%" : id.includes("Width") ? "" : "px");
    refreshAppearancePreviews();
    if (state.indicator.results) applyVisualSettings();
  };
  $("#" + id).onchange = $("#" + id).oninput;
}
const TEMPLATE_KEY = "qg:indicator-templates:v1";
const indicatorControlIds = [
  "indicatorTf", ...visualSettingIds,
];
function captureIndicatorForm() {
  const controls = Object.fromEntries(indicatorControlIds.map((id) => {
    const element = $("#" + id);
    return [id, element.type === "checkbox" ? element.checked : element.value];
  }));
  return {
    controls,
    direction: $("[data-direction].active")?.dataset.direction || null,
  };
}
const indicatorDefaults = captureIndicatorForm();
function applyIndicatorForm(snapshot) {
  if (!snapshot?.controls) return;
  for (const [id, value] of Object.entries(snapshot.controls)) {
    const element = $("#" + id);
    if (!element) continue;
    if (element.type === "checkbox") element.checked = Boolean(value);
    else element.value = value;
    const valueLabel = $("#" + id + "Value");
    if (valueLabel)
      valueLabel.textContent =
        element.value + (id.includes("Opacity") ? "%" : "px");
  }
  const direction = ["bullish", "bearish"].includes(snapshot.direction)
    ? snapshot.direction
    : null;
  $$("[data-direction]").forEach((button) =>
    button.classList.toggle("active", button.dataset.direction === direction),
  );
  $$("[data-direction]").forEach((button) =>
    button.setAttribute(
      "aria-pressed",
      String(button.dataset.direction === direction),
    ),
  );
  if (direction) $(".trend-segment")?.setAttribute("data-trend", direction);
  else $(".trend-segment")?.removeAttribute("data-trend");
  refreshAppearancePreviews();
  updateStyleAvailability();
  if (state.indicator.results) applyVisualSettings();
}
function readTemplates() {
  try { return JSON.parse(localStorage.getItem(TEMPLATE_KEY) || "{}"); }
  catch { return {}; }
}
function renderTemplates() {
  $("#savedTemplates").innerHTML = Object.keys(readTemplates())
    .map((name) => `<button data-template-name="${name.replaceAll('"', "&quot;")}">${name}</button>`)
    .join("") || "<small>No saved templates</small>";
}
function updateStyleAvailability() {
  const map = [
    ["reactionVisible", ["bullFill", "bullBorder", "bullOpacity", "bullWidth", "bullLineStyle", "bearFill", "bearBorder", "bearOpacity", "bearWidth", "bearLineStyle"]],
    ["blueLineEnabled", ["blueColor", "blueWidth", "blueLineStyle"]],
    ["aVisible", ["aColor", "aSize", "aGap"]],
    ["sVisible", ["sBullColor", "sBearColor", "sSize", "sGap"]],
    ["eVisible", ["eBlueColor", "eRedColor", "eSize", "eGap"]],
    ["stopAllVisible", ["stopAllFill", "stopAllBorder", "stopAllOpacity", "stopAllWidth", "stopAllSize", "stopAllRadius", "stopAllGap"]],
    ["orderVisible", ["orderFill", "orderColor", "orderOpacity", "orderWidth", "orderLineStyle"]],
    ["orderStopVisible", ["orderStopColor", "orderStopWidth", "orderStopLineStyle", "orderStopCap"]],
    ["eStopVisible", ["eStopColor", "eStopWidth", "eStopLineStyle"]],
  ];
  for (const [toggle, ids] of map)
    ids.forEach((id) => $("#" + id).disabled = !$("#" + toggle).checked);
}
$("#templateBtn").onclick = () => {
  renderTemplates();
  $("#templateMenu").classList.toggle("hidden");
};
$("#templateMenu").onclick = (event) => {
  const action = event.target.closest("[data-template-action]")?.dataset.templateAction;
  const name = event.target.closest("[data-template-name]")?.dataset.templateName;
  if (action === "save") {
    const nextName = prompt("Template name");
    if (nextName?.trim()) {
      const templates = readTemplates();
      templates[nextName.trim()] = captureIndicatorForm();
      localStorage.setItem(TEMPLATE_KEY, JSON.stringify(templates));
      renderTemplates();
      toast("Template saved");
    }
  } else if (action === "default") {
    applyIndicatorForm(indicatorDefaults);
    toast("Default settings restored");
  } else if (name) {
    applyIndicatorForm(readTemplates()[name]);
    $("#templateMenu").classList.add("hidden");
    toast(`Template "${name}" applied`);
  }
};
for (const id of ["reactionVisible", "blueLineEnabled", "aVisible", "sVisible", "eVisible", "stopAllVisible", "orderVisible", "orderStopVisible", "eStopVisible"])
  $("#" + id).addEventListener("change", updateStyleAvailability);
updateStyleAvailability();
$$('[data-range="all"]').forEach(
  (button) =>
    (button.onclick = () => {
      setDateTimeValue("#indicatorFrom", inputFromTehran(state.raw[0].time));
      setDateTimeValue("#indicatorTo", inputFromTehran(state.raw.at(-1).time));
    }),
);
$$('[data-range="visible"]').forEach(
  (button) =>
    (button.onclick = () => {
      const range = chart.timeScale().getVisibleLogicalRange();
      if (!range || !state.data.length) return;
      const fromIndex = Math.max(0, Math.floor(range.from));
      const toIndex = Math.min(state.data.length - 1, Math.ceil(range.to));
      setDateTimeValue(
        "#indicatorFrom",
        inputFromTehran(state.data[fromIndex].time),
      );
      setDateTimeValue(
        "#indicatorTo",
        inputFromTehran(state.data[toIndex].time),
      );
    }),
);
shell.addEventListener(
  "dblclick",
  (event) => {
    if (!state.indicator.enabled || !state.indicator.hitBoxes.length) return;
    const bounds = shell.getBoundingClientRect(),
      x = event.clientX - bounds.left,
      y = event.clientY - bounds.top,
      tolerance = 7;
    const hit = state.indicator.hitBoxes.find((box) => {
      const withinX = x >= box.left - tolerance && x <= box.right + tolerance,
        withinY = y >= box.top - tolerance && y <= box.bottom + tolerance,
        onVertical =
          Math.abs(x - box.left) <= tolerance ||
          Math.abs(x - box.right) <= tolerance,
        onHorizontal =
          Math.abs(y - box.top) <= tolerance ||
          Math.abs(y - box.bottom) <= tolerance;
      return withinX && withinY && (onVertical || onHorizontal);
    });
    if (!hit) return;
    event.preventDefault();
    event.stopPropagation();
    openIndicator();
  },
  true,
);
document.addEventListener("keydown", (e) => {
  if (
    (e.key === "Delete" || e.key === "Backspace") &&
    state.selected &&
    !["INPUT", "TEXTAREA"].includes(document.activeElement.tagName)
  )
    $("#deleteDrawing").click();
  if (e.key === "Escape") {
    cancelDrawingTool("escape");
  }
  if (
    e.key === "Enter" &&
    state.draft?.type === "path" &&
    state.draft.points.length > 1 &&
    !["INPUT", "TEXTAREA"].includes(document.activeElement.tagName)
  ) {
    e.preventDefault();
    finishDraft();
  }
  const editingText = document.activeElement?.matches("input, textarea, select, [contenteditable]:not([contenteditable='false'])") || document.activeElement?.isContentEditable;
  if (!editingText && (e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "z") {
    e.preventDefault();
    (e.shiftKey ? $("#redoBtn") : $("#undoBtn")).click();
  }
  if (!editingText && (e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "y") {
    e.preventDefault();
    $("#redoBtn").click();
  }
}, true);
setInterval(
  () => ($("#clock").textContent = formatSystemDateTime(new Date())),
  1000,
);
$("#clock").textContent = formatSystemDateTime(new Date());
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && !$("#errorLogModal").classList.contains("hidden")) closeErrorLog();
});
loadInventory().catch((err) => {
  const message = err?.name === "AbortError"
    ? "Market data service timed out. Restart the dev server from the repository root."
    : (err?.message || "Unable to load local market data.");
  $("#loading").classList.remove("hidden");
  $("#progress").textContent = message;
  log.chart.error("SYMBOL_INVENTORY_STARTUP_FAILED", err, { message });
  console.error(err);
});
