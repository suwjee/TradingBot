const FONT = 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif';
const LABEL_COLORS = { T: "#047857", F: "#be123c", "N/A": "#b8b8b8" };
const LABEL_SETTINGS = { T: "TrueColor", F: "FalseColor", "N/A": "NaColor" };
export const TRUE_FALSE_LABEL_WEIGHT = 300;
export const TRUE_FALSE_STOPALL_PRIMARY_WEIGHT = 700;
export const TRUE_FALSE_VISUAL_DEFAULTS = Object.freeze(Object.fromEntries(
  ["foundation", "secondary", "primary"].flatMap(prefix => [
    [`${prefix}TfVisible`, true],
    [`${prefix}TfSize`, 0],
    ...Object.entries(LABEL_SETTINGS).map(([label, key]) => [`${prefix}Tf${key}`, LABEL_COLORS[label]]),
  ]),
));

export function trueFalseAppearance(settings, group) {
  const prefix = `${group}Tf`;
  return {
    visible: settings[`${prefix}Visible`] ?? settings.trueFalseVisible,
    size: settings[`${prefix}Size`],
    colors: Object.fromEntries(Object.entries(LABEL_SETTINGS).map(([label, key]) => [
      label, settings[`${prefix}${key}`] ?? LABEL_COLORS[label],
    ])),
  };
}

export function drawTrueFalseLabel(ctx, verdict, visible, parentSize, x, edgeY, below,
  weight = TRUE_FALSE_LABEL_WEIGHT, repeated = false, verdictSizeOffset = 0, appearance = {}) {
  const label = verdict === null ? "N/A" : verdict;
  if (visible === false || !Object.hasOwn(LABEL_COLORS, label)) return;
  const customSize = Number(appearance.size);
  const useCustomSize = customSize > 0 && Number.isFinite(customSize);
  const autoSize = Math.max(1, Math.min(9, parentSize - 2));
  const size = useCustomSize ? customSize : autoSize;
  const labelSize = label !== "N/A" && !useCustomSize ? size + verdictSizeOffset : size;
  const labelWeight = label === "N/A" ? 300 : weight;
  const colors = appearance.colors ?? LABEL_COLORS;
  const direction = below ? 1 : -1;
  let y = edgeY + 3 * direction;
  ctx.save();
  ctx.textAlign = "center";
  ctx.textBaseline = below ? "top" : "bottom";
  if (repeated && label !== "N/A") {
    ctx.fillStyle = colors["N/A"];
    ctx.font = `300 ${size}px ${FONT}`;
    ctx.fillText("N/A", x, y);
    y += (size + 2) * direction;
  }
  ctx.fillStyle = colors[label];
  ctx.font = `${labelWeight} ${labelSize}px ${FONT}`;
  ctx.fillText(label, x, y);
  ctx.restore();
}
