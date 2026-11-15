export function recordVerifiedRows(ranges, first, candles, reference) {
  const byTime = new Map(reference.map(row => [row.time, row]));
  const corrections = [];
  let checkedCount = 0;
  let run = null;
  candles.forEach((candle, offset) => {
    const row = byTime.get(candle.time);
    if (!row) { run = null; return; }
    checkedCount++;
    const index = first + offset;
    if (run) run[1] = index;
    else { run = [index, index]; ranges.push(run); }
    if (ohlcDiffers(row, candle)) corrections.push(row);
  });
  return { checkedCount, corrections };
}

export function summarizeVerifiedRows(ranges, count) {
  const merged = [];
  for (const range of ranges.toSorted((a, b) => a[0] - b[0])) {
    const last = merged.at(-1);
    if (last && range[0] <= last[1] + 1) last[1] = Math.max(last[1], range[1]);
    else merged.push([...range]);
  }
  const verifiedCount = merged.reduce((total, [from, to]) => total + to - from + 1, 0);
  return { ranges: merged, verifiedCount, totalCount: count, status: verifiedCount === count ? "verified" : "pending" };
}

export function firstUnverifiedRow(ranges, index) {
  for (const [from, to] of ranges) {
    if (from > index) break;
    if (index <= to) index = to + 1;
  }
  return index;
}

function ohlcDiffers(left, right) {
  return left.open !== right.open || left.high !== right.high || left.low !== right.low || left.close !== right.close;
}

export function recordVerifiedGapBatch(ranges, first, candles, reference) {
  const corrections = [], recovered = [];
  let index = 0, checkedCount = 0, run = null;
  for (const row of reference) {
    while (index < candles.length && candles[index].time < row.time) index++;
    const position = first + index + recovered.length;
    if (run?.[1] === position - 1) run[1] = position;
    else { run = [position, position]; ranges.push(run); }
    if (candles[index]?.time !== row.time) recovered.push(row);
    else {
      checkedCount++;
      if (ohlcDiffers(candles[index], row)) corrections.push(row);
    }
  }
  return { checkedCount, corrections, recovered };
}
