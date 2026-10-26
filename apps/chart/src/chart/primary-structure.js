// Presentation of finalized Engine PH, PL and matching-behavior-leg results.
// Price crossings, structure validity and numbering remain Engine-owned.
export const PRIMARY_VISUAL_DEFAULTS = Object.freeze({
  phVisible: true,
  phLabelVisible: true,
  plVisible: true,
  plLabelVisible: true,
  mblVisible: true,
  mblLabelVisible: true,
  primaryArrowColor: "#056656",
  primaryArrowSize: 12,
  primaryCircleColor: "#ec407a",
  primaryCircleRadius: 12,
  primaryCircleOpacity: 100,
  primaryLabelSize: 12,
  primaryGap: 12,
  primaryLabelGap: 10,
  mblColor: "#b22833",
  mblWidth: 2,
  mblSize: 9,
  mblLineStyle: "dot",
});

const FONT = 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif';
const MBL_UNBROKEN_CANDLES = 100;

function settingsWithDefaults(settings = {}) {
  const output = { ...PRIMARY_VISUAL_DEFAULTS };
  for (const key of Object.keys(output)) {
    if (settings[key] != null) output[key] = settings[key];
  }
  return output;
}

export function primaryMarkerLayout(kind, direction, x, y, settings = {}) {
  const style = settingsWithDefaults(settings);
  const above = kind === "PH";
  const sign = above ? -1 : 1;
  const arrow = (kind === "PH") === (direction === "bearish");
  const radius = arrow ? style.primaryArrowSize / 2 : style.primaryCircleRadius;
  const centerY = y + sign * (style.primaryGap + radius);
  return {
    shape: arrow ? "chevrons" : "circle",
    pointsDown: above,
    x, y: centerY, radius,
    top: centerY - radius, bottom: centerY + radius,
    labelY: centerY + sign * (radius + style.primaryLabelGap),
    textBaseline: above ? "bottom" : "top",
    color: arrow ? style.primaryArrowColor : style.primaryCircleColor,
    opacity: arrow ? 1 : style.primaryCircleOpacity / 100,
    fontSize: style.primaryLabelSize,
  };
}

export function primaryObjectId(direction, kind, item) {
  const physical = item.id ?? `${item.sourceTime}:${item.sourceIndex ?? ""}:${item.decisionEventTime ?? ""}:${item.number ?? ""}`;
  return `indicator:${direction}:primary:${kind}:${physical}`;
}

export function primaryLabelLayout(marker, metrics) {
  const ascent = metrics.actualBoundingBoxAscent ?? marker.fontSize * 0.8;
  const descent = metrics.actualBoundingBoxDescent ?? marker.fontSize * 0.2;
  const baselineY = marker.textBaseline === "bottom"
    ? marker.labelY - descent : marker.labelY + ascent;
  return { baselineY, left: marker.x - metrics.width / 2, right: marker.x + metrics.width / 2,
    top: baselineY - ascent, bottom: baselineY + descent };
}

export function primaryVisualObjects(group, direction, settings = {}) {
  const style = settingsWithDefaults(settings);
  const output = [];
  for (const [kind, rows] of [["PH", group.primaryHighs], ["PL", group.primaryLows]]) {
    for (const item of rows || []) {
      if (item.calculationValid === false) continue;
      const marker = primaryMarkerLayout(kind, direction, 0, 0, style);
      output.push({
        id: primaryObjectId(direction, kind, item),
        type: "indicator-label", primaryKind: kind,
        name: `${kind}-${item.number}`, text: `${kind}-${item.number}`,
        time: item.sourceTime, price: item.price,
        color: marker.color, fill: marker.color, size: marker.fontSize,
        opacity: marker.opacity, weight: 600,
      });
    }
  }
  for (const item of group.matchingBehaviorLegs || []) {
    if (item.calculationValid === false) continue;
    output.push({
      id: primaryObjectId(direction, "MBL", item),
      type: "indicator-stop", primaryKind: "MBL", name: "MBL", text: "MBL",
      time: item.sourceTime, price: item.price,
      color: style.mblColor, size: style.mblSize, width: style.mblWidth,
      lineStyle: style.mblLineStyle, opacity: 1,
    });
  }
  return output;
}

export function matchingLegEndTime(leg, latest, timeframe) {
  const cap = leg.capTime != null
    ? Number(leg.capTime)
    : Number(leg.sourceTime) + MBL_UNBROKEN_CANDLES * timeframe;
  if (leg.stopIndex == null) return cap;
  const end = leg.stopTime != null
    ? Number(leg.stopTime)
    : Number(leg.sourceTime) + (Number(leg.stopIndex) - Number(leg.sourceIndex)) * timeframe;
  return latest ? end : Math.min(end, cap);
}

function drawChevrons(ctx, marker) {
  const stroke = Math.max(1, marker.radius / 3);
  const left = marker.x - marker.radius + stroke / 2;
  const right = marker.x + marker.radius - stroke / 2;
  const top = marker.top + stroke / 2;
  const height = marker.radius * 2 - stroke;
  ctx.lineWidth = stroke;
  ctx.lineCap = "round";
  ctx.lineJoin = "round";
  ctx.beginPath();
  for (const offset of [0, height * 0.55]) {
    const edge = marker.pointsDown ? top + offset : marker.bottom - stroke / 2 - offset;
    const tip = edge + (marker.pointsDown ? 1 : -1) * height * 0.45;
    ctx.moveTo(left, edge);
    ctx.lineTo(marker.x, tip);
    ctx.lineTo(right, edge);
  }
  ctx.stroke();
}

export function drawPrimaryStructures(ctx, group, {
  direction, settings = {}, timeframe, timeToX, priceToY,
  objectFor = () => null,
  offsetPoint = (_object, x, y) => ({ x, y }),
  offsetRect = (_object, x1, y1, x2, y2) => ({ x1, y1, x2, y2 }),
  onHit = () => {},
}) {
  const style = settingsWithDefaults(settings);
  for (const [kind, rows, visible, labelVisible] of [
    ["PH", group.primaryHighs, style.phVisible, style.phLabelVisible],
    ["PL", group.primaryLows, style.plVisible, style.plLabelVisible],
  ]) {
    if (!visible && !labelVisible) continue;
    for (const item of rows || []) {
      if (item.calculationValid === false) continue;
      const objectId = primaryObjectId(direction, kind, item);
      const object = objectFor(objectId);
      if (object?.hidden) continue;
      const x = timeToX(item.sourceTime), y = priceToY(Number(item.price));
      if (x == null || y == null || !Number.isFinite(x) || !Number.isFinite(y)) continue;
      const shifted = offsetPoint(object, x, y);
      const marker = primaryMarkerLayout(kind, direction, shifted.x, shifted.y, style);
      const color = object?.customized ? object.color : marker.color;
      ctx.save();
      ctx.strokeStyle = color;
      ctx.fillStyle = color;
      ctx.globalAlpha = object?.customized ? (object.opacity ?? marker.opacity) : marker.opacity;
      ctx.setLineDash([]);
      if (visible) {
        if (marker.shape === "circle") {
          ctx.beginPath();
          ctx.arc(marker.x, marker.y, marker.radius, 0, Math.PI * 2);
          ctx.fill();
        } else {
          drawChevrons(ctx, marker);
        }
        onHit({ objectId, shape: "point", x: marker.x, y: marker.y, radius: marker.radius + 2 });
      }
      if (labelVisible) {
        const size = object?.customized ? object.size : marker.fontSize;
        const text = object?.text ?? `${kind}-${item.number}`;
        ctx.globalAlpha = 1;
        ctx.font = `${object?.weight || 600} ${size}px ${FONT}`;
        ctx.textAlign = "center";
        ctx.textBaseline = "alphabetic";
        const label = primaryLabelLayout({ ...marker, fontSize: size }, ctx.measureText(text));
        ctx.fillText(text, marker.x, label.baselineY);
        onHit({ objectId, shape: "rect", left: label.left, right: label.right,
          top: label.top, bottom: label.bottom });
      }
      ctx.restore();
    }
  }
  if (!style.mblVisible && !style.mblLabelVisible) return;
  const legs = (group.matchingBehaviorLegs || []).filter(item => item.calculationValid !== false);
  const latest = legs.reduce((chosen, item) => !chosen ||
    Number(item.triggerEventTime ?? item.triggerTime ?? item.sourceTime) >
      Number(chosen.triggerEventTime ?? chosen.triggerTime ?? chosen.sourceTime) ? item : chosen, null);
  for (const leg of legs) {
    const objectId = primaryObjectId(direction, "MBL", leg);
    const object = objectFor(objectId);
    if (object?.hidden) continue;
    const x1 = timeToX(leg.sourceTime), x2 = timeToX(matchingLegEndTime(leg, leg === latest, timeframe));
    const y = priceToY(Number(leg.price));
    if ([x1, x2, y].some(value => value == null || !Number.isFinite(value))) continue;
    const line = offsetRect(object, x1, y, x2, y);
    const color = object?.customized ? object.color : style.mblColor;
    const lineStyle = object?.customized ? object.lineStyle : style.mblLineStyle;
    const width = object?.customized ? object.width : style.mblWidth;
    const fontSize = object?.customized ? object.size : style.mblSize;
    const label = object?.text ?? "MBL";
    const middle = (line.x1 + line.x2) / 2;
    ctx.save();
    ctx.strokeStyle = color;
    ctx.fillStyle = color;
    ctx.lineWidth = width;
    ctx.lineCap = lineStyle === "dot" ? "round" : "butt";
    ctx.setLineDash(lineStyle === "dot" ? [0, width * 3] : lineStyle === "dash" ? [6, 4] : []);
    ctx.font = `500 ${fontSize}px ${FONT}`;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    const gap = style.mblLabelVisible ? ctx.measureText(label).width / 2 + 6 : 0;
    ctx.beginPath();
    if (!gap) {
      ctx.moveTo(line.x1, line.y1);
      ctx.lineTo(line.x2, line.y2);
    } else {
      if (middle - gap > line.x1) {
        ctx.moveTo(line.x1, line.y1);
        ctx.lineTo(middle - gap, line.y1);
      }
      if (middle + gap < line.x2) {
        ctx.moveTo(middle + gap, line.y2);
        ctx.lineTo(line.x2, line.y2);
      }
    }
    if (style.mblVisible) ctx.stroke();
    if (style.mblLabelVisible) {
      ctx.fillText(label, middle, line.y1);
      onHit({ objectId, shape: "rect", left: middle - gap, right: middle + gap,
        top: line.y1 - fontSize / 2, bottom: line.y1 + fontSize / 2 });
    }
    ctx.restore();
    if (style.mblVisible) onHit({ objectId, shape: "line", ...line });
  }
}
