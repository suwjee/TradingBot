// Presentation of finalized Engine PH, PL and matching-behavior-leg results.
// Price crossings, structure validity and numbering remain Engine-owned.
import { formatTehranMetadataTime } from "../features/raw-file-contract.js";
import { drawTrueFalseLabel, trueFalseAppearance, trueFalseVisualObjects, TRUE_FALSE_STOPALL_PRIMARY_WEIGHT } from "./true-false-label.js";

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
  primaryCircleRadius: 4,
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
const MBL_UNBROKEN_CANDLES = 400;
export const TREND_VISUAL_DEFAULTS = Object.freeze({
  trendLineVisible: true,
  trendBullColor: "#00a886",
  trendBearColor: "#f23645",
  trendLineWidth: 1,
  trendLineStyle: "dash",
  trendLabelSize: 10,
});

export function clipHistoricalHitBoxes(hits, right) {
  if (right < 0) return [];
  return hits.flatMap(hit => {
    const clipped = { ...hit, clipRight: right };
    if (hit.shape === "rect") {
      if (hit.left >= right) return [];
      clipped.right = Math.min(hit.right, right);
    } else if (hit.shape === "point") {
      if (hit.x - (hit.radius || 12) >= right) return [];
    } else if (hit.shape === "line") {
      if (Math.min(hit.x1, hit.x2) >= right) return [];
      if (Math.max(hit.x1, hit.x2) > right) {
        const y = hit.y1 + (right - hit.x1) * (hit.y2 - hit.y1) / (hit.x2 - hit.x1);
        const end = hit.x1 > right ? "1" : "2";
        clipped[`x${end}`] = right;
        clipped[`y${end}`] = y;
      }
    }
    return [clipped];
  });
}

export function trendTransitionLayout(transition, { timeToX, height }) {
  return { lineX: timeToX(transition.sourceTime), lineBottom: height };
}

function trendObjectId(transition, part) {
  return `indicator:market:${transition.id ?? `${transition.direction}:${transition.sourceTime}`}:${part}`;
}

function trendTimestamp(sourceTime) {
  const epoch = Number(sourceTime);
  return Number.isSafeInteger(epoch) && epoch > 0 ? formatTehranMetadataTime(epoch).slice(0, 19) : null;
}

export function trendVisualObjects(group, settings) {
  const style = settingsWithDefaults(settings, TREND_VISUAL_DEFAULTS);
  const output = [];
  for (const transition of group.trendTransitions || []) {
    const bullish = transition.direction !== "bearish";
    const direction = bullish ? "Bullish" : "Bearish";
    const price = transition.level ?? (bullish ? transition.iconCandleHigh : transition.iconCandleLow);
    const color = bullish ? style.trendBullColor : style.trendBearColor;
    output.push({
      id: trendObjectId(transition, "line"), type: "indicator-stop", name: `${direction} market line`,
      time: transition.sourceTime, direction: transition.direction, price, color, width: style.trendLineWidth, lineStyle: style.trendLineStyle,
    });
    const text = trendTimestamp(transition.sourceTime);
    if (text) {
      output.push({
        id: trendObjectId(transition, "time"), type: "indicator-label", name: `${direction} market timestamp`,
        text, color: "#111827", size: style.trendLabelSize, weight: 600, time: transition.sourceTime,
        direction: transition.direction, price,
      });
    }
  }
  return output;
}

export function drawTrendTransitions(ctx, group, {
  timeToX, width = Infinity, height, settings = {},
  objectFor = () => null, offsetPoint = (_object, x, y) => ({ x, y }), onHit = () => {},
}) {
  const transitions = group.trendTransitions;
  if (!transitions?.length || settings.trendLineVisible === false) return;
  const style = settingsWithDefaults(settings, TREND_VISUAL_DEFAULTS);
  const labels = [];
  for (const transition of transitions) {
    const bullish = transition.direction !== "bearish";
    const color = bullish ? style.trendBullColor : style.trendBearColor;
    const lineId = trendObjectId(transition, "line"), line = objectFor(lineId);
    const labelId = trendObjectId(transition, "time"), timestamp = objectFor(labelId);
    const lineStyle = line?.customized ? line : null;
    const labelStyle = timestamp?.customized ? timestamp : null;
    const marker = trendTransitionLayout(transition, { timeToX, height });
    let label = null;
    if (Number.isFinite(marker.lineX) && marker.lineX >= 0 && marker.lineX <= width) {
      const text = labelStyle?.text ?? trendTimestamp(transition.sourceTime);
      if (!timestamp?.hidden && text) {
        const layout = trendTimestampLayout(ctx, text, marker.lineX, width, height,
          labelStyle?.size ?? style.trendLabelSize, labels);
        if (layout) {
          const position = offsetPoint(timestamp, layout.left, layout.top);
          label = { ...layout, left: position.x, top: position.y, color, textColor: labelStyle?.color, objectId: labelId };
          labels.push(label);
        }
      }
    }
    const lineStart = offsetPoint(line, marker.lineX, 0);
    if (!line?.hidden && Number.isFinite(marker.lineX) && lineStart.x >= 0 && lineStart.x <= width) {
      const thickness = lineStyle?.width ?? style.trendLineWidth;
      const pattern = lineStyle?.lineStyle ?? style.trendLineStyle;
      const baseline = label && lineStart.x >= label.left && lineStart.x <= label.left + label.width
        ? label.top : marker.lineBottom;
      const top = Math.max(0, lineStart.y), bottom = Math.min(height, baseline + lineStart.y);
      ctx.save();
      ctx.strokeStyle = lineStyle?.color ?? color;
      ctx.lineWidth = thickness;
      ctx.lineCap = pattern === "dot" ? "round" : "butt";
      ctx.setLineDash(pattern === "dot" ? [0, thickness * 3] : pattern === "dash" ? [6, 5] : []);
      ctx.beginPath();
      ctx.moveTo(lineStart.x, top);
      ctx.lineTo(lineStart.x, bottom);
      ctx.stroke();
      ctx.restore();
      onHit({ objectId: lineId, shape: "line", x1: lineStart.x, y1: top, x2: lineStart.x, y2: bottom });
    }
  }
  for (const label of labels) {
    drawTrendTimestamp(ctx, label);
    onHit({ objectId: label.objectId, shape: "rect", area: true, left: label.left, top: label.top,
      right: label.left + label.width, bottom: label.top + label.height });
  }
}

function trendTimestampLayout(ctx, text, lineX, width, height, size, labels) {
  if (width < 32 || height < size + 12) return null;
  const font = `600 ${size}px ${FONT}`;
  const margin = 2;
  const padding = 4;
  ctx.save();
  ctx.font = font;
  const badgeWidth = Math.min(ctx.measureText(text).width + padding * 2, width - margin * 2);
  ctx.restore();
  const badgeHeight = size + padding * 2;
  const left = Math.min(Math.max(lineX - badgeWidth / 2, margin), width - margin - badgeWidth);
  let top = height - margin - badgeHeight;
  const spacing = 3;
  while (labels.some(label => label.top === top && left < label.left + label.width + spacing
    && label.left < left + badgeWidth + spacing)) top -= badgeHeight + spacing;
  if (top < margin) return null;
  return { text, font, left, top, width: badgeWidth, height: badgeHeight, padding };
}

function drawTrendTimestamp(ctx, label) {
  const { text, font, left, top, width, height, padding, color, textColor = "#111827" } = label;
  ctx.save();
  ctx.setLineDash([]);
  ctx.lineWidth = 0.75;
  ctx.fillStyle = "rgba(255,255,255,.96)";
  ctx.fillRect(left, top, width, height);
  ctx.strokeStyle = color;
  ctx.strokeRect(left, top, width, height);
  ctx.fillStyle = textColor;
  ctx.font = font;
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillText(text, left + width / 2, top + height / 2, width - padding * 2);
  ctx.restore();
}

function settingsWithDefaults(settings = {}, defaults = PRIMARY_VISUAL_DEFAULTS) {
  const output = { ...defaults };
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
    color: kind === "PH" ? style.primaryArrowColor : style.primaryCircleColor,
    opacity: arrow ? 1 : style.primaryCircleOpacity / 100,
    fontSize: style.primaryLabelSize,
  };
}

export function indicatorCalculationSegments(results) {
  const output = [];
  const fields = ["reactions", "blueLines", "aZones", "sZones", "eZones", "stopAlls"];
  for (const [direction, aggregate] of Object.entries(results.directions || {})) {
    const offsets = Object.fromEntries(fields.map(key => [key, 0]));
    for (const group of aggregate.calculationSegments || [aggregate]) {
      output.push({ direction, group, objectOffsets: { ...offsets } });
      for (const key of fields) offsets[key] += (group[key] || []).length;
    }
  }
  return output;
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
  const verdict = trueFalseAppearance(settings, "primary");
  const output = [];
  for (const [kind, rows] of [["PH", group.primaryHighs], ["PL", group.primaryLows]]) {
    for (const item of rows || []) {
      if (item.calculationValid === false) continue;
      const marker = primaryMarkerLayout(kind, direction, 0, 0, settings);
      const objectId = primaryObjectId(direction, kind, item);
      const name = `${kind}-${item.number}`;
      output.push({
        id: objectId,
        type: "indicator-label", primaryKind: kind,
        name, text: name, copyLabel: item.trueFalse ? `${name} (${item.trueFalse})` : name,
        time: item.sourceTime, price: item.price,
        color: marker.color, fill: marker.color, size: marker.fontSize,
        opacity: marker.opacity, weight: 600,
      });
      for (const object of trueFalseVisualObjects(objectId, item, marker.fontSize, verdict, {
        weight: TRUE_FALSE_STOPALL_PRIMARY_WEIGHT, verdictSizeOffset: 2,
      })) output.push({ ...object, name: `${name} ${object.text}` });
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
  return Math.min(end, cap);
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
  const verdict = trueFalseAppearance(settings, "primary");
  for (const [kind, rows, visible, labelVisible] of [
    ["PH", group.primaryHighs, settings.phGroupVisible ?? style.phVisible,
      settings.phGroupVisible ?? style.phLabelVisible],
    ["PL", group.primaryLows, settings.plGroupVisible ?? style.plVisible,
      settings.plGroupVisible ?? style.plLabelVisible],
  ]) {
    if (!visible && !labelVisible) continue;
    for (const item of rows || []) {
      if (item.calculationValid === false) continue;
      const objectId = primaryObjectId(direction, kind, item);
      const object = objectFor(objectId);
      const x = timeToX(item.sourceTime), y = priceToY(Number(item.price));
      if (x == null || y == null || !Number.isFinite(x) || !Number.isFinite(y)) continue;
      const shifted = offsetPoint(object, x, y);
      const marker = primaryMarkerLayout(kind, direction, shifted.x, shifted.y, settings);
      const appearance = object?.customized ? object : null;
      const color = appearance?.color ?? marker.color;
      ctx.save();
      ctx.strokeStyle = color;
      ctx.fillStyle = color;
      ctx.globalAlpha = appearance?.opacity ?? marker.opacity;
      ctx.setLineDash([]);
      if (visible && !object?.hidden) {
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
        const size = appearance?.size ?? marker.fontSize;
        const text = object?.text ?? `${kind}-${item.number}`;
        ctx.globalAlpha = 1;
        ctx.font = `${object?.weight || 600} ${size}px ${FONT}`;
        ctx.textAlign = "center";
        ctx.textBaseline = "alphabetic";
        const label = primaryLabelLayout({ ...marker, fontSize: size }, ctx.measureText(text));
        const below = marker.textBaseline === "top";
        if (!object?.hidden) {
          ctx.fillText(text, marker.x, label.baselineY);
          onHit({ objectId, shape: "rect", left: label.left, right: label.right,
            top: label.top, bottom: label.bottom });
        }
        drawTrueFalseLabel(ctx, item.trueFalse, verdict.visible, size,
          marker.x, below ? label.bottom : label.top, below, TRUE_FALSE_STOPALL_PRIMARY_WEIGHT, false, 2,
          verdict, item, { parentId: objectId, objectFor, offsetPoint, onHit });
      }
      ctx.restore();
    }
  }
  const mblVisible = settings.mblGroupVisible ?? style.mblVisible;
  const mblLabelVisible = settings.mblGroupVisible ?? style.mblLabelVisible;
  if (!mblVisible && !mblLabelVisible) return;
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
    const appearance = object?.customized ? object : null;
    const color = appearance?.color ?? style.mblColor;
    const lineStyle = appearance?.lineStyle ?? style.mblLineStyle;
    const width = appearance?.width ?? style.mblWidth;
    const fontSize = appearance?.size ?? style.mblSize;
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
    const gap = mblLabelVisible ? ctx.measureText(label).width / 2 + 6 : 0;
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
    if (mblVisible) ctx.stroke();
    if (mblLabelVisible) {
      ctx.fillText(label, middle, line.y1);
      onHit({ objectId, shape: "rect", left: middle - gap, right: middle + gap,
        top: line.y1 - fontSize / 2, bottom: line.y1 + fontSize / 2 });
    }
    ctx.restore();
    if (mblVisible) onHit({ objectId, shape: "line", ...line });
  }
}
