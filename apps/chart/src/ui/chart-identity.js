const DEFAULT_DISPLAY_LENGTH = 8;

/**
 * Keep the persisted chart identity opaque while presenting a compact,
 * stable eight-character label in dense chart controls.
 */
export function shortChartId(value, maxLength = DEFAULT_DISPLAY_LENGTH) {
  const normalized = String(value || "").replace(/[^a-z0-9]/gi, "").toUpperCase();
  if (!normalized) return "NULL";
  return normalized.slice(0, Math.max(1, Number(maxLength) || DEFAULT_DISPLAY_LENGTH));
}

export function fullChartId(value) {
  const normalized = String(value || "").trim();
  return normalized || "NULL";
}
