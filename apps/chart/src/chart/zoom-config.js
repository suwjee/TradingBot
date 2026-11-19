// A positive floor bounds the visible candle slots at maximum zoom-out.
export const MIN_SAFE_BAR_SPACING = 0.05;

export function zoomOutCapacityGain(previousSpacing, nextSpacing) {
  const previous = Number(previousSpacing);
  const next = Number(nextSpacing);
  if (!(previous > 0) || !(next > 0)) return 0;
  return previous / next;
}
