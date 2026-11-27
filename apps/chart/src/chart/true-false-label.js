const FONT = 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif';
const LABEL_COLORS = { T: "#047857", F: "#be123c", "N/A": "#808080" };
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
    showNA: group !== "secondary" || settings.secondaryNaVisible !== false,
    showStars: settings.foundationStarsVisible !== false,
    showX: settings.foundationXVisible !== false,
    repeatStarColor: group === "foundation" ? settings.secondaryTfNaColor ?? LABEL_COLORS["N/A"] : undefined,
    colors: Object.fromEntries(Object.entries(LABEL_SETTINGS).map(([label, key]) => [
      label, settings[`${prefix}${key}`] ?? LABEL_COLORS[label],
    ])),
  };
}

function verdictMarkers(verdict, parentSize, weight, repeated, verdictSizeOffset, appearance, basic) {
  const label = verdict === null ? "N/A" : verdict;
  if (!Object.hasOwn(LABEL_COLORS, label)) return [];
  const customSize = Number(appearance.size);
  const useCustomSize = customSize > 0 && Number.isFinite(customSize);
  const autoSize = Math.max(1, Math.min(9, parentSize - 2));
  const size = useCustomSize ? customSize : autoSize;
  const labelSize = label !== "N/A" && !useCustomSize ? size + verdictSizeOffset : size;
  const colors = appearance.colors ?? LABEL_COLORS;
  const starColor = appearance.repeatStarColor;
  const repeatCount = basic.trueFalseRepeatCount;
  const ordinal = Number.isSafeInteger(repeatCount) && repeatCount > 0;
  const markers = [];
  if (label !== "N/A") markers.push({ key: "verdict", text: label, size: labelSize, weight, color: colors[label] });
  if ((!starColor && repeated && label !== "N/A") || label === "N/A") {
    markers.push({ key: "na", text: "N/A", size, weight: 300, color: colors["N/A"], visible: appearance.showNA });
  }
  if (label !== "N/A" && starColor && (ordinal || repeated)) {
    markers.push({ key: "stars", text: "*".repeat(ordinal ? repeatCount : 1),
      size: labelSize, weight, color: starColor, visible: appearance.showStars });
    if (ordinal && label === "F" && basic.trueFalseRepeatF === true) {
      markers.push({ key: "x", text: "X", size: labelSize, weight, color: starColor, visible: appearance.showX });
    }
  }
  return markers;
}

export function trueFalseVisualObjects(parentId, item, parentSize, appearance, {
  weight = TRUE_FALSE_LABEL_WEIGHT, repeated = false, verdictSizeOffset = 0,
} = {}) {
  return verdictMarkers(item.trueFalse, parentSize, weight, repeated, verdictSizeOffset, appearance, item)
    .map(({ key, text, size, weight: fontWeight, color }) => ({
      id: `${parentId}:${key}`, type: "indicator-label", name: text, text,
      time: item.sourceTime, price: item.price, size, weight: fontWeight, color,
    }));
}

export function drawIndicatorText(ctx, text, x, y, {
  below, size, weight, color, objectId, objectFor, offsetPoint, onHit,
}) {
  const object = objectId ? objectFor?.(objectId) : null;
  if (object?.hidden) return;
  const style = object?.customized ? object : null;
  const position = offsetPoint?.(object, x, y) ?? { x, y };
  const fontSize = style?.size ?? size;
  const label = style?.text ?? text;
  ctx.save();
  ctx.textAlign = "center";
  ctx.textBaseline = below ? "top" : "bottom";
  ctx.fillStyle = style?.color ?? color;
  ctx.font = `${style?.weight ?? weight} ${fontSize}px ${FONT}`;
  ctx.fillText(label, position.x, position.y);
  if (objectId && onHit) {
    const width = Math.max(8, ctx.measureText?.(label)?.width ?? label.length * fontSize * 0.6);
    const top = below ? position.y : position.y - fontSize;
    onHit({ objectId, shape: "rect", area: true, padding: 1, left: position.x - width / 2,
      right: position.x + width / 2, top, bottom: top + fontSize });
  }
  ctx.restore();
  return fontSize;
}

export function drawTrueFalseLabel(ctx, verdict, visible, parentSize, x, edgeY, below,
  weight = TRUE_FALSE_LABEL_WEIGHT, repeated = false, verdictSizeOffset = 0, appearance = {}, basic = {}, objects = {}) {
  if (visible === false) return;
  const direction = below ? 1 : -1;
  let y = edgeY + 3 * direction;
  for (const marker of verdictMarkers(verdict, parentSize, weight, repeated, verdictSizeOffset, appearance, basic)) {
    if (marker.visible === false) continue;
    const size = drawIndicatorText(ctx, marker.text, x, y, { ...marker, ...objects, below,
      objectId: objects.parentId ? `${objects.parentId}:${marker.key}` : undefined });
    if (size != null) y += (size + 2) * direction;
  }
}
