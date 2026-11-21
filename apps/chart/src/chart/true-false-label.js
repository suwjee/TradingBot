const FONT = 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif';
const LABEL_COLORS = { T: "#047857", F: "#be123c", "N/A": "#b8b8b8" };
export const TRUE_FALSE_LABEL_WEIGHT = 300;
export const TRUE_FALSE_STOPALL_PRIMARY_WEIGHT = 700;

export function drawTrueFalseLabel(ctx, verdict, visible, parentSize, x, edgeY, below,
  weight = TRUE_FALSE_LABEL_WEIGHT, repeated = false, verdictSizeOffset = 0) {
  const label = verdict === null ? "N/A" : verdict;
  if (visible === false || !Object.hasOwn(LABEL_COLORS, label)) return;
  const size = Math.max(1, Math.min(9, parentSize - 2));
  const labelSize = label === "N/A" ? size : size + verdictSizeOffset;
  const labelWeight = label === "N/A" ? 300 : weight;
  const direction = below ? 1 : -1;
  let y = edgeY + 3 * direction;
  ctx.save();
  ctx.textAlign = "center";
  ctx.textBaseline = below ? "top" : "bottom";
  if (repeated && label !== "N/A") {
    ctx.fillStyle = LABEL_COLORS["N/A"];
    ctx.font = `300 ${size}px ${FONT}`;
    ctx.fillText("N/A", x, y);
    y += (size + 2) * direction;
  }
  ctx.fillStyle = LABEL_COLORS[label];
  ctx.font = `${labelWeight} ${labelSize}px ${FONT}`;
  ctx.fillText(label, x, y);
  ctx.restore();
}
