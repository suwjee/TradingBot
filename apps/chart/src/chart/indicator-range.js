import { lowerBoundTime } from "./lod.js";

function nearestIndex(value, candles) {
  if (!Array.isArray(candles) || !candles.length) return -1;
  const target = Number(value);
  if (!Number.isFinite(target)) return 0;
  // Chart candles are strictly ordered by time. Keep the earlier bar on ties.
  const right = lowerBoundTime(candles, target);
  if (right === 0) return 0;
  if (right === candles.length) return right - 1;
  return target - Number(candles[right - 1].time) <= Number(candles[right].time) - target
    ? right - 1 : right;
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
