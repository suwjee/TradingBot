function nearestIndex(value, candles) {
  if (!Array.isArray(candles) || !candles.length) return -1;
  const target = Number(value);
  if (!Number.isFinite(target)) return 0;
  let best = 0;
  let distance = Math.abs(Number(candles[0].time) - target);
  for (let index = 1; index < candles.length; index++) {
    const nextDistance = Math.abs(Number(candles[index].time) - target);
    if (nextDistance < distance) {
      best = index;
      distance = nextDistance;
    }
  }
  return best;
}

export function normalizeIndicatorRange(from, to, candles) {
  if (!Array.isArray(candles) || !candles.length) return null;
  const first = nearestIndex(from, candles);
  const second = nearestIndex(to, candles);
  const fromIndex = Math.min(first, second);
  const toIndex = Math.max(first, second);
  return {
    from: Number(candles[fromIndex].time),
    to: Number(candles[toIndex].time),
    fromIndex,
    toIndex,
  };
}

export function moveIndicatorRange(current, side, targetIndex, candles) {
  if (!Array.isArray(candles) || !candles.length) return null;
  const max = candles.length - 1;
  const fromIndex = Math.max(0, Math.min(max, Math.trunc(Number(current?.fromIndex) || 0)));
  const toIndex = Math.max(fromIndex, Math.min(max, Math.trunc(Number(current?.toIndex) || fromIndex)));
  const target = Math.max(0, Math.min(max, Math.trunc(Number(targetIndex) || 0)));
  if (side === "from") return { fromIndex: Math.min(target, toIndex), toIndex };
  return { fromIndex, toIndex: Math.max(target, fromIndex) };
}
