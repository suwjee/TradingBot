import { buildReviewBody, mountReview } from "./render.js";
import { isLiveReportId, liveReportLocation } from "./tab.js";
import { reviewView } from "./view.js";
import { createErrorJournalClient } from "../error-journal.js";
import { errorDetails } from "../diagnostic-details.js";

const loading = document.getElementById("review-loading");
const app = document.getElementById("app");
const diagnostics = createErrorJournalClient({ storage: localStorage, changed: () => {} });
function recordReportError(event, error) {
  const id = `report-${globalThis.crypto.getRandomValues(new Uint32Array(4)).join("-")}`;
  void diagnostics.record({ id, event, scope: "CALCULATION REPORT", level: "ERROR",
    recordedAt: Date.now(), path: location.pathname, ...errorDetails(error) })
    .catch(failure => console.error("Could not persist report diagnostic", failure));
}
window.addEventListener("error", event => recordReportError("UNCAUGHT_REPORT_ERROR", event.error || event.message));
window.addEventListener("unhandledrejection", event => recordReportError("UNHANDLED_REPORT_REJECTION", event.reason));

function fail(message) {
  const paragraph = document.createElement("p");
  paragraph.textContent = message;
  loading.replaceChildren(paragraph);
}

let renderedId;
let listeners;
let archivePending = false;
let archiveMessage = "";

function updateArchiveControls() {
  app.querySelector("#export-zip").disabled = archivePending;
  app.querySelector("#export-status").textContent = archiveMessage;
}

function stylesheetText(sheet) {
  return Array.from(sheet.cssRules, rule => rule instanceof CSSImportRule
    ? stylesheetText(rule.styleSheet) : rule.cssText).join("\n");
}

function wireArchive(payload, snapshot, review, reopen) {
  const trigger = app.querySelector("#export-zip");
  const dialog = app.querySelector("#export-dialog");
  const form = app.querySelector("#export-form");
  const bridge = app.querySelector("#include-bridge");
  const submit = app.querySelector("#download-zip");
  const selectionStatus = app.querySelector("#export-selection-status");
  const selectedFormats = () => new FormData(form).getAll("format");
  function updateSelection() {
    const formats = selectedFormats();
    bridge.disabled = !formats.some(format => format !== "html");
    submit.disabled = formats.length === 0;
    selectionStatus.textContent = submit.disabled ? "Select at least one format." : "";
  }
  function openDialog() {
    updateSelection();
    dialog.showModal();
  }

  updateArchiveControls();
  trigger.addEventListener("click", openDialog);
  app.querySelector("#cancel-export").addEventListener("click", () => dialog.close());
  dialog.addEventListener("close", () => trigger.focus({ preventScroll: true }));
  form.addEventListener("change", updateSelection);
  form.addEventListener("submit", async event => {
    event.preventDefault();
    const formats = selectedFormats();
    if (archivePending || !formats.length) return;
    const exportedAt = new Date();
    dialog.close();
    const view = reviewView(app);
    archivePending = true;
    archiveMessage = "Preparing ZIP…";
    updateArchiveControls();
    try {
      const { createCalculationArchive } = await import("./archive.js");
      const css = formats.includes("html") ? Array.from(document.styleSheets, stylesheetText).join("\n") : "";
      const { name, bytes } = await createCalculationArchive({
        payload, snapshot, review, css, view, formats, exportedAt, includeBridgeOutput: view.includeBridge,
      });
      const url = URL.createObjectURL(new Blob([bytes], { type: "application/zip" }));
      const link = document.createElement("a");
      link.href = url;
      link.download = name;
      document.body.append(link);
      link.click();
      link.remove();
      setTimeout(() => URL.revokeObjectURL(url), 30_000);
      archiveMessage = "ZIP download started.";
    } catch (error) {
      recordReportError("REPORT_EXPORT_FAILED", error);
      archiveMessage = `Could not create ZIP. ${error.message}`;
    } finally {
      archivePending = false;
      updateArchiveControls();
      if (document.activeElement === document.body) app.querySelector("#export-zip").focus({ preventScroll: true });
    }
  });
  if (reopen && !archivePending) openDialog();
}

async function renderReview({ payload, snapshot }) {
  const calculationId = snapshot?.calculation?.calculationId;
  if (calculationId && calculationId === renderedId) return;
  const review = await buildReviewBody(payload, snapshot);
  const { hash, reviewId, body, bridgeData } = review;
  const view = reviewView(app);
  const active = document.activeElement;
  const focusId = app.contains(active) && active.id;
  const { scrollX, scrollY } = window;

  listeners?.abort();
  listeners = new AbortController();
  app.innerHTML = body;
  reviewView(app, view);
  mountReview(bridgeData, { signal: listeners.signal });
  wireArchive(payload, snapshot, review, view.exportOpen);
  if (focusId) document.getElementById(focusId)?.focus({ preventScroll: true });
  window.scrollTo(scrollX, scrollY);
  document.title = `Indicator Info · ${reviewId}`;
  document.body.dataset.payloadHash = hash;
  document.body.dataset.reviewId = reviewId;
  loading.remove();
  renderedId = calculationId;
}

async function fetchReport(url, options) {
  const response = await fetch(url, { cache: "no-store", signal: AbortSignal.timeout(12_000), ...options });
  if (response.status === 304) return response;
  const result = await response.json();
  if (!response.ok) {
    const error = new Error(`Calculation Report request failed with HTTP ${response.status}.`);
    error.displayMessage = typeof result?.error === "string" && result.error ? result.error : error.message;
    throw error;
  }
  await renderReview(result);
  return response;
}

async function loadCalculationReport() {
  const identity = location.pathname.replace(/^\/info\/?/, "");
  if (!identity) { fail("This report has no calculation identity."); return; }
  const url = `/api/info/${identity}`;
  const follow = liveReportLocation(identity) && new URLSearchParams(location.search).get("follow") === "1";
  try {
    await fetchReport(url, { method: isLiveReportId(identity) ? "POST" : "GET" });
  } catch (error) {
    if (!follow) {
      recordReportError("REPORT_LOAD_FAILED", error);
      fail(`Could not load this calculation report: ${error.displayMessage ?? error.message}`);
    }
  }
  if (!follow) return;

  let tag;
  let inFlight = false;
  let timer;
  async function refresh() {
    if (inFlight) return;
    clearTimeout(timer);
    if (document.hidden) return;
    inFlight = true;
    try {
      const response = await fetchReport(`${url}?latest=1`, {
        headers: tag ? { "If-None-Match": tag } : undefined,
      });
      tag = response.headers.get("ETag") || tag;
    } catch (error) {
      if (!renderedId) fail(`Waiting for the chart calculation. ${error.displayMessage ?? error.message}`);
    } finally {
      inFlight = false;
      if (!document.hidden) timer = setTimeout(refresh, 3_000);
    }
  }
  document.addEventListener("visibilitychange", refresh);
  void refresh();
}

loadCalculationReport();
