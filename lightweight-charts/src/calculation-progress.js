export function updateStageAggregate(aggregates, key, label, event) {
  const created = !aggregates.has(key);
  const aggregate = aggregates.get(key) || {
    key,
    label,
    runs: 0,
    totalDurationMs: 0,
    active: false,
    status: "pending",
  };
  const status = String(event?.status || "info");
  if (status === "started") {
    aggregate.active = true;
    aggregate.status = "started";
  } else if (["completed", "finished"].includes(status)) {
    aggregate.active = false;
    aggregate.status = status;
    aggregate.runs += 1;
    const duration = Number(event?.durationMs);
    if (Number.isFinite(duration)) aggregate.totalDurationMs += Math.max(0, duration);
  } else if (status === "failed") {
    aggregate.active = false;
    aggregate.status = "failed";
  }
  aggregates.set(key, aggregate);
  return { aggregate, created };
}
