// Presentation-only OHLC aggregation for chart timeframes.
// This module must not become a trading-rule or Engine decision source.
export function aggregate(rows, seconds) {
  if (seconds === 1) return rows;
  const out = [];
  let bar = null;
  for (const r of rows) {
    const time = Math.floor(Number(r.time) / seconds) * seconds;
    if (!bar || bar.time !== time) {
      if (bar) out.push(bar);
      bar = {
        time,
        open: +r.open,
        high: +r.high,
        low: +r.low,
        close: +r.close,
      };
    } else {
      bar.high = Math.max(bar.high, +r.high);
      bar.low = Math.min(bar.low, +r.low);
      bar.close = +r.close;
    }
  }
  if (bar) out.push(bar);
  return out;
}
