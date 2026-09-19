function durationLabel(seconds) {
  const value = Math.max(0, Math.round(Number(seconds) || 0));
  if (value >= 86400) return `${(value / 86400).toFixed(value % 86400 ? 1 : 0)}d`;
  if (value >= 3600) return `${(value / 3600).toFixed(value % 3600 ? 1 : 0)}h`;
  if (value >= 60) return `${(value / 60).toFixed(value % 60 ? 1 : 0)}m`;
  return `${value}s`;
}

export function calculateMeasureStats(a, b, timeframeSeconds = 1) {
  const durationSeconds = Math.abs(Number(b?.time) - Number(a?.time));
  const priceDelta = Number(b?.price) - Number(a?.price);
  const base = Number(a?.price);
  return {
    durationSeconds,
    bars: Math.round(durationSeconds / Math.max(1, Number(timeframeSeconds) || 1)),
    priceDelta,
    percentage: base ? (priceDelta / base) * 100 : 0,
    durationLabel: durationLabel(durationSeconds),
  };
}

export function calculatePositionLevels(type, entryPrice, targetPrice) {
  const entry = Number(entryPrice);
  const anchor = Number(targetPrice);
  if (!Number.isFinite(entry) || !Number.isFinite(anchor)) return null;
  const distance = Math.abs(anchor - entry) || Math.max(Math.abs(entry) * 0.01, Number.EPSILON);
  const long = type === "long";
  const target = long ? entry + distance : entry - distance;
  const stop = long ? entry - distance : entry + distance;
  const reward = Math.abs(target - entry);
  return { entry, target, stop, risk: Math.abs(entry - stop), reward, riskReward: reward / Math.max(Number.EPSILON, Math.abs(entry - stop)) };
}
