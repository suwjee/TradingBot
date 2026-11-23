import { buildReviewBody, reviewRuntime } from "./render.js";
import { isLiveReportId, liveReportLocation } from "./tab.js";

const loading = document.getElementById("review-loading");
const app = document.getElementById("app");

function fail(message) {
  const paragraph = document.createElement("p");
  paragraph.textContent = message;
  loading.replaceChildren(paragraph);
}

const viewInputs = ["from", "to", "filter-search"];
let renderedId;
let listeners;

async function renderReview({ payload, snapshot }) {
  const calculationId = snapshot?.calculation?.calculationId;
  if (calculationId && calculationId === renderedId) return;
  const { hash, reviewId, body, bridgeData } = await buildReviewBody(payload, snapshot);
  const values = new Map(viewInputs.map(id => [id, document.getElementById(id)?.value || ""]));
  const openDetails = new Set([...app.querySelectorAll("details[open]")].map(detailKey));
  const oldFilters = new Map([...app.querySelectorAll(".category-filter")].map(input => [input.value, input.checked]));
  const oldFamilies = new Map([...app.querySelectorAll("[data-filter-parent]")].map(input => [
    input.dataset.filterParent, input.indeterminate ? undefined : input.checked,
  ]));
  const collapsed = Boolean(app.querySelector("#filter-groups")?.hidden);
  const active = document.activeElement;
  const focusId = app.contains(active) && active.id;
  const { scrollX, scrollY } = window;

  listeners?.abort();
  listeners = new AbortController();
  app.innerHTML = body;
  for (const [id, value] of values) document.getElementById(id).value = value;
  for (const details of app.querySelectorAll("details")) {
    if (openDetails.has(detailKey(details))) details.open = true;
  }
  for (const input of app.querySelectorAll(".category-filter")) {
    input.checked = oldFilters.get(input.value) ?? oldFamilies.get(input.dataset.filterFamily) ?? input.checked;
  }
  reviewRuntime(bridgeData, { signal: listeners.signal });
  if (collapsed && !values.get("filter-search")) app.querySelector(".filter-all-toggle").click();
  if (focusId) document.getElementById(focusId)?.focus({ preventScroll: true });
  window.scrollTo(scrollX, scrollY);
  document.title = `Indicator Info · ${reviewId}`;
  document.body.dataset.payloadHash = hash;
  document.body.dataset.reviewId = reviewId;
  loading.remove();
  renderedId = calculationId;
}

function detailKey(details) {
  const { timeGroup, filterGroup, bridgeId } = details.dataset;
  if (timeGroup) return `day:${timeGroup}`;
  if (filterGroup) return `filter:${filterGroup}`;
  if (bridgeId) return `bridge:${bridgeId}`;
  return details.querySelector("summary strong")?.textContent;
}

async function fetchReport(url, options) {
  const response = await fetch(url, { cache: "no-store", signal: AbortSignal.timeout(12_000), ...options });
  if (response.status === 304) return response;
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || "Calculation report was not found");
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
    if (!follow) fail(`Could not load this calculation report: ${error.message}`);
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
      if (!renderedId) fail(`Waiting for the chart calculation. ${error.message}`);
    } finally {
      inFlight = false;
      if (!document.hidden) timer = setTimeout(refresh, 3_000);
    }
  }
  document.addEventListener("visibilitychange", refresh);
  void refresh();
}

loadCalculationReport();
