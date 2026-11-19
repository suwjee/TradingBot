export function startLiveIndicatorProgress({ operationId, signal, report, connect = url => new EventSource(url) }) {
  let percent = 0;
  let closed = false;
  let source;
  report({ operationId, percent, stage: "Preparing calculation", outcome: "started" });

  function finish(outcome) {
    if (closed) return;
    closed = true;
    source?.close();
    signal.removeEventListener("abort", abort);
    report({ operationId, percent: outcome === "applied" ? 100 : percent, outcome });
  }

  function abort() { finish("idle"); }

  signal.addEventListener("abort", abort, { once: true });
  if (signal.aborted) abort();
  else {
    try { source = connect(`/api/reactions/progress?requestId=${encodeURIComponent(operationId)}`); }
    catch { /* Calculation can finish once its result is available. */ }
  }
  if (source) source.onmessage = ({ data }) => {
    if (closed) return;
    let event;
    try { event = JSON.parse(data); } catch { return; }
    if (!event || typeof event.label !== "string") return;
    const { completedStages, totalStages, label, status } = event;
    if (Number.isSafeInteger(completedStages) && completedStages >= 0 && Number.isSafeInteger(totalStages) && totalStages > completedStages) {
      percent = Math.max(percent, Math.min(99, Math.round(100 * completedStages / totalStages)));
    } else if (status !== "started" && status !== "finished") return;
    report({ operationId, percent, stage: status === "finished" ? "Validating result" : label, outcome: "running" });
  };

  return { operationId, finish };
}
