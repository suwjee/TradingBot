export function findActionableGaps(candles, resolutionSeconds, isMarketClosed = () => false) {
  const step = Number(resolutionSeconds);
  if (!Array.isArray(candles) || candles.length < 2 || !Number.isSafeInteger(step) || step < 1) return [];
  const gaps = [];
  for (let index = 1; index < candles.length; index += 1) {
    const previous = Number(candles[index - 1]?.time);
    const next = Number(candles[index]?.time);
    if (!Number.isSafeInteger(previous) || !Number.isSafeInteger(next) || next <= previous + step) continue;
    let start = null;
    let count = 0;
    for (let time = previous + step; time < next; time += step) {
      if (isMarketClosed(time, step)) {
        if (start !== null) {
          gaps.push({ from: start, to: start + (count - 1) * step, missingCandles: count });
          start = null;
          count = 0;
        }
        continue;
      }
      if (start === null) start = time;
      count += 1;
    }
    if (start !== null) gaps.push({ from: start, to: start + (count - 1) * step, missingCandles: count });
  }
  return gaps;
}
