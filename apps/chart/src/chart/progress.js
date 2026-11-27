export function calculationStageKey(label) {
  const text = String(label || "Pipeline event");
  if (text === "Load StopAll engine") return "Load Lifecycle engine";
  if (text === "Market chronology ready") return "Build live market chronology";
  if (/^Update live (lower|timeframe) candle views$/.test(text)) {
    return text.replace("Update live ", "Build ");
  }
  if (/^(?:(?:Reaction geometry|Reaction) • (?:Bullish|Bearish)|Continue Reaction geometry)$/.test(text)) {
    return "Reaction geometry";
  }
  if (/^(?:Blue Line|A|S) - (?:Bullish|Bearish)$/.test(text)) return text.replace(" - ", " • ");
  return text.replace(/^(Reconcile S visibility|StopAll)( - (?:Bullish|Bearish)) - pass \d+$/, "$1$2")
    .replace(/^(E - (?:Bullish|Bearish) - StopAll reconciliation) \d+$/, "$1");
}

const engineInputs = [
  "Validate request", "Read source file", "Parse source JSON", "Use full RAW calculation context",
  "Normalize raw candles", "Build live market chronology",
  "Build lower candle views", "Build timeframe candle views", "Select candle range",
];
const engineModules = ["Reaction", "Blue Line", "A", "S", "E", "Lifecycle"].map(name => `Load ${name} engine`);

export function plannedCalculationStages(direction) {
  const selected = direction === "bearish" ? "Bearish" : "Bullish";
  const directions = [selected, selected === "Bullish" ? "Bearish" : "Bullish"];
  const rows = [];
  function add(scope, labels, optional = false) {
    rows.push(...labels.map(label => ({ scope, label, optional })));
  }
  add("server", ["HTTP request and server", "Verify RAW input"]);
  add("input-range", ["Filter raw range"], true);
  add("server", ["Start Python calculation"]);
  add("engine", engineModules);
  add("engine", engineInputs, true);
  add("engine", ["Reaction geometry", "Internal Reaction ownership"]);
  for (const name of ["Bullish", "Bearish"]) {
    add("engine", [`Blue Line • ${name}`, `A • ${name}`, `S • ${name}`, `E • ${name} • initial`]);
    add("engine", [`E • ${name} • S reconciliation`], true);
    add("engine", [`E • ${name} • final audit`]);
    add("engine", [`E • ${name} • shared Order-stop reconciliation`, `Reconcile S visibility - ${name}`,
      `StopAll - ${name}`, `E - ${name} - StopAll reconciliation`, `Order_B reset legs - ${name}`], true);
  }
  for (const name of directions) {
    add("engine", [`Apply visibility filters - ${name}`, `PH/PL - ${name}`,
      `Serialize Reaction - ${name}`, `Serialize output - ${name}`], name !== selected);
  }
  for (const name of directions) {
    add("engine", [`Evaluate T/F - ${name}`, `Evaluate positions - ${name}`, `Evaluate liquidity - ${name}`], name !== selected);
  }
  add("engine", ["Calculation pipeline", "Encode response JSON"], true);
  add("server", ["Verify calculation inputs", "Save calculation result", "Response ready"]);
  add("browser", ["Response parsing", "Prepare chart objects", "Canvas render"]);
  return rows;
}

export function calculationStageProgress(stages, complete = false) {
  const planned = [...stages].filter(stage => stage.scope);
  const completed = planned.filter(stage => stage.runs > 0).length;
  const skipped = planned.filter(stage => stage.status === "skipped").length;
  const unreported = planned.filter(stage => stage.status === "unreported").length;
  const total = planned.length - skipped;
  const percent = complete ? 100 : Math.min(99, Math.floor(100 * completed / Math.max(1, total)));
  return { completed, skipped, unreported, total, percent };
}

export function updateStageAggregate(aggregates, key, label, event) {
  const created = !aggregates.has(key);
  const aggregate = aggregates.get(key) || {
    key,
    label,
    runs: 0,
    totalDurationMs: 0,
    timedRuns: 0,
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
    const duration = event?.durationMs;
    if (typeof duration === "number" && Number.isFinite(duration) && duration >= 0) {
      aggregate.totalDurationMs += duration;
      aggregate.timedRuns = (aggregate.timedRuns || 0) + 1;
    }
  } else if (status === "failed") {
    aggregate.active = false;
    aggregate.status = "failed";
  }
  aggregates.set(key, aggregate);
  return { aggregate, created };
}
