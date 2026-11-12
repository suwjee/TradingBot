export function resolveCanonicalChartPoint({
  x,
  y,
  timeAtCoordinate,
  priceAtCoordinate,
  fallback,
}) {
  const time = timeAtCoordinate(x);
  const price = priceAtCoordinate(y);
  return time == null || price == null ? fallback : { x, y, time, price };
}

// A future position endpoint must use the chart timeframe, not the duration of
// the final market gap. Neighbour coordinates preserve subpixel/LOD spacing.
export function positionTimeToCoordinate({ candles, time, timeframe, timeToCoordinate, barSpacing }) {
  if (!candles.length) return null;
  const target = Number(time);
  const first = Number(candles[0].time), last = Number(candles.at(-1).time);
  if (target >= first && target <= last) {
    const direct = timeToCoordinate(target);
    if (Number.isFinite(direct)) return direct;
    let lo = 0, hi = candles.length - 1;
    while (lo + 1 < hi) {
      const mid = (lo + hi) >>> 1;
      if (Number(candles[mid].time) <= target) lo = mid;
      else hi = mid;
    }
    const start = Number(candles[lo].time), end = Number(candles[hi].time);
    const left = timeToCoordinate(start), right = timeToCoordinate(end);
    if (!Number.isFinite(left) || !Number.isFinite(right) || end <= start) return null;
    return left + (target - start) / (end - start) * (right - left);
  }
  const after = target > last;
  const edge = after ? last : first;
  const x = timeToCoordinate(edge);
  if (!Number.isFinite(x)) return null;
  const neighbour = candles.length > 1
    ? timeToCoordinate(Number(candles[after ? candles.length - 2 : 1].time)) : null;
  const distance = Number.isFinite(neighbour) ? Math.abs(x - neighbour) : 0;
  const spacing = distance > 0 ? distance : Number(barSpacing);
  if (!(spacing > 0)) return null;
  return x + (target - edge) / Math.max(1, Number(timeframe) || 1) * spacing;
}
