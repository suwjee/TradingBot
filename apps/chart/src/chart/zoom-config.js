// 0.25px keeps the scale finite while exposing twice as many candles as the
// previous 0.5px floor. Dense views are handled by the display-only LOD path;
// raw timestamps remain the authority for drawings and hit testing.
export const MIN_SAFE_BAR_SPACING = 0.25;

export function zoomOutCapacityGain(previousSpacing, nextSpacing) {
  const previous = Number(previousSpacing);
  const next = Number(nextSpacing);
  if (!(previous > 0) || !(next > 0)) return 0;
  return previous / next;
}
