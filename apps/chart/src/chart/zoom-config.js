// Keep a positive floor while allowing 2.5 times the visible span of 0.25px.
// Display density may change, but the time axis still uses candle coordinates.
export const MIN_SAFE_BAR_SPACING = 0.10;

export function zoomOutCapacityGain(previousSpacing, nextSpacing) {
  const previous = Number(previousSpacing);
  const next = Number(nextSpacing);
  if (!(previous > 0) || !(next > 0)) return 0;
  return previous / next;
}
