// /manual-test page runtime. The opener tab posts the cached indicator
// payload over the BroadcastChannel; this page renders the review body from
// src/manual-review.js into the document. It makes no other requests and
// persists only review verdicts in localStorage.
import { buildReviewBody, reviewRuntime } from "./manual-review.js";

// The opener is not needed for the handoff (BroadcastChannel is same-origin),
// so sever it as soon as this controlled page starts.
try { window.opener = null; } catch {}

const channel = new BroadcastChannel("qg-manual-test");
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
    .then(({ hash, reviewId, styles, runtime, body }) => {
      document.title = `Indicator Timeline Review · ${reviewId}`;
      const style = document.createElement("style");
      style.textContent = styles;
      document.head.append(style);
      document.body.dataset.payloadHash = hash;
      document.body.dataset.reviewId = reviewId;
      app.innerHTML = body;
      loading.remove();
      (0, eval)(`(${runtime})()`);
    })
    .catch((error) => fail(`Could not render the review page: ${error.message}`));
}

channel.onmessage = (event) => {
  if (event.data?.type !== "review-payload") return;
  channel.close();
  renderReview(event.data.payload, event.data.snapshot);
};
channel.postMessage({ type: "review-ready" });
