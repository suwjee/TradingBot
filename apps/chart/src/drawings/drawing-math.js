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

export function calculatePositionLevels(type, entryPrice, targetPrice, stopPrice) {
  const entry = Number(entryPrice);
  const anchor = Number(targetPrice);
  if (!["long", "short"].includes(type) || !Number.isFinite(entry) || !Number.isFinite(anchor)) return null;
  const distance = Math.abs(anchor - entry) || Math.max(Math.abs(entry) * 0.01, Number.EPSILON);
  const long = type === "long";
  const target = long ? entry + distance : entry - distance;
  const stop = stopPrice === undefined ? (long ? entry - distance : entry + distance) : Number(stopPrice);
  const risk = (entry - stop) * (long ? 1 : -1);
  if (!Number.isFinite(stop) || risk <= 0) return null;
  const reward = Math.abs(target - entry);
  return { entry, target, stop, risk, reward, riskReward: reward / risk };
}

export function initialPositionLevels(type, entryPrice, targetPrice) {
  const levels = calculatePositionLevels(type, entryPrice, targetPrice);
  if (!levels) return null;
  return calculatePositionLevels(type, levels.entry, levels.target,
    levels.entry + (type === "long" ? -1 : 1) * levels.reward / 4);
}

export function editPositionLevel(drawing, level, price) {
  const value = Number(price);
  const levels = calculatePositionLevels(drawing.type, drawing.a?.price, drawing.b?.price, drawing.stopPrice);
  if (!levels || !Number.isFinite(value) || !["target", "stop"].includes(level)) return null;
  const sign = drawing.type === "long" ? 1 : -1;
  if ((value - levels.entry) * sign * (level === "target" ? 1 : -1) <= 0) return null;
  return {
    ...drawing,
    b: { ...drawing.b, price: level === "target" ? value : levels.target },
    stopPrice: level === "stop" ? value : levels.stop,
  };
}

export function editPositionTime(drawing, edge, time, rightTime = drawing.b?.time) {
  const value = Number(time);
  if (!Number.isFinite(value) || value <= 0) return null;
  if (edge === "end" && value > Number(drawing.a.time))
    return { ...drawing, b: { ...drawing.b, time: value } };
  if (edge === "start" && value < Number(rightTime))
    return { ...drawing, a: { ...drawing.a, time: value }, b: { ...drawing.b, time: Number(rightTime) } };
  return null;
}

export function positionRightTime(drawing, candles, timeframe) {
  return Number(drawing.b?.time) > Number(drawing.a.time)
    ? Number(drawing.b.time) : positionEndTime(candles, drawing.a.time, timeframe);
}

export function translatePosition(drawing, candles, timeframe, deltaBars, deltaPrice) {
  if (!drawing.a || !drawing.b || !Number.isFinite(Number(deltaBars)) || !Number.isFinite(Number(deltaPrice))) return null;
  const moved = {
    ...drawing,
    a: { ...drawing.a, time: positionEndTime(candles, drawing.a.time, timeframe, Number(deltaBars)), price: Number(drawing.a.price) + Number(deltaPrice) },
    b: { ...drawing.b, time: positionEndTime(candles, positionRightTime(drawing, candles, timeframe), timeframe, Number(deltaBars)), price: Number(drawing.b.price) + Number(deltaPrice) },
  };
  if (drawing.stopPrice !== undefined) moved.stopPrice = Number(drawing.stopPrice) + Number(deltaPrice);
  if (!(moved.a.time > 0) || !(moved.b.time > moved.a.time) ||
      ![moved.a.time, moved.b.time, moved.a.price, moved.b.price].every(Number.isFinite)) return null;
  return moved;
}

// Count actual chart candles, including across closed-market gaps. Beyond the
// supplied data, extend using the current chart timeframe into future space.
function positionCandleIndex(candles, time, timeframe) {
  const anchor = Number(time);
  const step = Math.max(1, Number(timeframe) || 1);
  if (!candles.length) return anchor / step;
  let lo = 0, hi = candles.length;
  while (lo < hi) {
    const mid = (lo + hi) >>> 1;
    if (Number(candles[mid].time) < anchor) lo = mid + 1;
    else hi = mid;
  }
  const first = Number(candles[0].time), last = Number(candles.at(-1).time);
  return lo === 0 ? (anchor - first) / step
    : lo === candles.length ? candles.length - 1 + (anchor - last) / step
      : lo - 1 + (anchor - Number(candles[lo - 1].time)) /
        (Number(candles[lo].time) - Number(candles[lo - 1].time));
}

export function positionWidthBars(candles, start, end, timeframe) {
  if (!candles.length) return (Number(end) - Number(start)) / Math.max(1, Number(timeframe) || 1);
  return positionCandleIndex(candles, end, timeframe) - positionCandleIndex(candles, start, timeframe);
}

export function positionEndTime(candles, time, timeframe, bars = 20) {
  const step = Math.max(1, Number(timeframe) || 1);
  if (!candles.length) return Number(time) + bars * step;
  const first = Number(candles[0].time), last = Number(candles.at(-1).time);
  const end = positionCandleIndex(candles, time, timeframe) + bars;
  if (end < 0) return first + end * step;
  if (end >= candles.length - 1) return last + (end - candles.length + 1) * step;
  const left = Math.floor(end);
  return Number(candles[left].time) + (end - left) *
    (Number(candles[left + 1].time) - Number(candles[left].time));
}
