// Recover legacy arrays and snapshots accidentally persisted by old Undo/Redo.
export function drawingArray(value, fallback = []) {
  const seen = new Set();
  while (value && !Array.isArray(value) && typeof value === "object" && !seen.has(value)) {
    seen.add(value);
    value = value.drawings;
  }
  return Array.isArray(value) ? value : fallback;
}

export function normalizeHistorySnapshot(snapshot, current) {
  const drawings = drawingArray(snapshot, drawingArray(current.drawings));
  const indicatorObjects = Array.isArray(snapshot?.indicatorObjects)
    ? snapshot.indicatorObjects
    : Array.isArray(current.indicatorObjects) ? current.indicatorObjects : [];
  return structuredClone({ drawings, indicatorObjects });
}

export const CHART_TIMEFRAME_KEY = "qg:last-chart-timeframe:v1";
export function restoredTimeframe(storage, supported, fallback = 30) {
  try {
    const seconds = Number(storage.getItem(CHART_TIMEFRAME_KEY));
    return supported.some((item) => item.s === seconds) ? seconds : fallback;
  } catch { return fallback; }
}

export function indicatorControlId(key) {
  return key === "timeframe" ? "indicatorTf" : key;
}
