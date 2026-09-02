// Opener side of the served /manual-test review page. The click handler opens
// the tab synchronously (popup-safe); this channel then delivers the cached
// indicator payload once the page announces that it is ready. The handoff is
// in-memory only: nothing is persisted and no candle cache is serialized.
const READY_TIMEOUT_MS = 15000;

export function openManualReviewTab(host = window) {
  // Some Chromium builds return null when `noopener` is passed as a feature,
  // even though they opened the page. Keep the user-gesture popup reference
  // so a real blocker can be distinguished from a successful new tab. The
  // served page immediately severs `window.opener` after it loads.
  return host.open("/manual-test", "_blank");
}

export function startManualReviewHandoff(payload, snapshot, host = window, notify = () => {}) {
  const channel = new host.BroadcastChannel("qg-manual-test");
  let delivered = false;
  const send = () => channel.postMessage({ type: "review-payload", payload, snapshot });
  channel.onmessage = (event) => {
    if (event.data?.type !== "review-ready") return;
    delivered = true;
    send();
  };
  const timer = host.setTimeout(() => {
    if (delivered) return;
    channel.close();
    notify("The review tab did not respond. Allow pop-ups for this page and export again.");
  }, READY_TIMEOUT_MS);
  const finish = () => { host.clearTimeout(timer); channel.close(); };
  return { send, finish };
}
