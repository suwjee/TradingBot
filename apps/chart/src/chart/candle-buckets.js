function aggregateRows(rows, seconds, previousBucket = null) {
  const buckets = [];
  let bucket = previousBucket ? { ...previousBucket } : null;
  for (const row of rows) {
    const time = Math.floor(Number(row.time) / seconds) * seconds;
    if (!bucket || bucket.time !== time) {
      if (bucket) buckets.push(bucket);
      bucket = { time, open: +row.open, high: +row.high, low: +row.low, close: +row.close };
    } else {
      bucket.high = Math.max(bucket.high, +row.high);
      bucket.low = Math.min(bucket.low, +row.low);
      bucket.close = +row.close;
    }
  }
  if (bucket) buckets.push(bucket);
  return buckets;
}

export function aggregateCandles(rows, seconds) {
  return seconds === 1 ? rows : aggregateRows(rows, seconds);
}

export function appendCandleBuckets(existing, rows, seconds) {
  if (!rows.length) return { data: existing, changed: [] };
  const last = existing.at(-1);
  const extendsLastBucket = last && Math.floor(rows[0].time / seconds) * seconds === last.time;
  const changed = aggregateRows(rows, seconds, extendsLastBucket ? last : null);
  const prefix = extendsLastBucket ? existing.slice(0, -1) : existing;
  return { data: prefix.concat(changed), changed };
}
