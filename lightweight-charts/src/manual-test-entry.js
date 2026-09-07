// /info page runtime. The URL identifies one immutable calculation cache entry;
// this page reads only that entry, so reports from different calculations stay
// independent even when several tabs are open.
import { buildReviewBody, reviewRuntime } from "./manual-review.js";
const loading = document.getElementById("review-loading");
const app = document.getElementById("app");

function fail(message) {
  loading.innerHTML = `<p>${message}</p>`;
}

function renderReview(payload, snapshot) {
  try {
    if (!payload || !payload.directions || typeof payload.directions !== "object") throw new Error("Invalid indicator payload");
  } catch (error) {
    fail(`The received payload is not a valid indicator export: ${error.message}`);
    return;
  }
  buildReviewBody(payload, snapshot)
    .then(({ hash, reviewId, styles, body, bridgeData }) => {
      document.title = `Indicator Info · ${reviewId}`;
      const style = document.createElement("style");
      style.textContent = styles;
      document.head.append(style);
      document.body.dataset.payloadHash = hash;
      document.body.dataset.reviewId = reviewId;
      app.innerHTML = body;
      loading.remove();
      reviewRuntime(bridgeData);
    })
    .catch((error) => fail(`Could not render the review page: ${error.message}`));
}

async function loadCalculationReport() {
  const identity = location.pathname.replace(/^\/info\/?/, "");
  if (!identity) { fail("This report has no calculation identity."); return; }
  try {
    const response = await fetch(`/api/info/${identity}`, { cache: "no-store" });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || "Calculation report was not found");
    renderReview(result.payload, result.snapshot);
  } catch (error) {
    fail(`Could not load this calculation report: ${error.message}`);
  }
}
loadCalculationReport();
