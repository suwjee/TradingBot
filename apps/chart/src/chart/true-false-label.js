const FONT = 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif';
const LABEL_COLORS = { T: "#047857", F: "#be123c", "N/A": "#b8b8b8" };
export const TRUE_FALSE_LABEL_WEIGHT = 300;
export const TRUE_FALSE_STOPALL_PRIMARY_WEIGHT = 700;

export function drawTrueFalseLabel(ctx, verdict, visible, parentSize, x, edgeY, below, weight = TRUE_FALSE_LABEL_WEIGHT) {
  const label = verdict === null ? "N/A" : verdict;
  if (visible === false || !Object.hasOwn(LABEL_COLORS, label)) return;
  const size = Math.max(1, Math.min(9, parentSize - 2));
  const labelWeight = label === "N/A" ? 300 : weight;
  ctx.save();
  ctx.fillStyle = LABEL_COLORS[label];
  ctx.font = `${labelWeight} ${size}px ${FONT}`;
  ctx.textAlign = "center";
  ctx.textBaseline = below ? "top" : "bottom";
  ctx.fillText(label, x, edgeY + (below ? 3 : -3));
  ctx.restore();
}
