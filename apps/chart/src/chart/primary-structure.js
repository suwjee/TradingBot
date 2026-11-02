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
const TREND_COLOR = "#00a886";
const BEARISH_TREND_COLOR = "#f23645";
const TREND_ICON_SIZE = 28;
const TREND_ICON_CLEARANCE = 100;

function clipOneHistoricalHitBox(hit, right) {
  const clipped = { ...hit, clipRight: right };
  if (hit.shape === "rect") {
    if (hit.left >= right) return null;
    clipped.right = Math.min(hit.right, right);
  } else if (hit.shape === "point") {
    if (hit.x - (hit.radius || 12) >= right) return null;
  } else if (hit.shape === "line") {
    if (Math.min(hit.x1, hit.x2) >= right) return null;
    if (Math.max(hit.x1, hit.x2) > right) {
      const y = hit.y1 + (right - hit.x1) * (hit.y2 - hit.y1) / (hit.x2 - hit.x1);
      const end = hit.x1 > right ? "1" : "2";
      clipped[`x${end}`] = right;
      clipped[`y${end}`] = y;
    }
  }
  return clipped;
}

// Keep the original exported, array-producing contract for its existing users.
export function clipHistoricalHitBoxes(hits, right) {
  if (right < 0) return [];
  return hits.flatMap((hit) => {
    const clipped = clipOneHistoricalHitBox(hit, right);
    return clipped === null ? [] : [clipped];
  });
}

/**
 * Replace only the newly rendered segment of a hitbox buffer in place.
 * The stable prefix and source hitbox objects are preserved. The clipped
 * segment consists of the same clones and order as clipHistoricalHitBoxes.
 * No segment array, flatMap arrays, or unbounded push(...items) is needed.
 */
export function clipHistoricalHitBoxesInPlace(hits, startIndex, right) {
  const originalLength = hits.length;
  if (right < 0) {
    hits.length = startIndex;
    return hits;
  }
  let writeIndex = startIndex;
  for (let readIndex = startIndex; readIndex < originalLength; readIndex++) {
    if (!(readIndex in hits)) continue; // Match flatMap's sparse-slot policy.
    const clipped = clipOneHistoricalHitBox(hits[readIndex], right);
    if (clipped !== null) hits[writeIndex++] = clipped;
  }
  hits.length = writeIndex;
  return hits;
}

export function trendTransitionLayout(transition, { timeToX, priceToY, height }) {
  const lineX = timeToX(transition.sourceTime);
  const bullish = transition.direction !== "bearish";
  const targetPrice = bullish ? transition.iconCandleHigh : transition.iconCandleLow;
  let icon = null;
  if (transition.iconCandleTime != null && targetPrice != null) {
    const centerX = timeToX(transition.iconCandleTime);
    const priceY = priceToY(Number(targetPrice));
    if (Number.isFinite(centerX) && Number.isFinite(priceY)) {
      const top = bullish ? priceY - TREND_ICON_CLEARANCE - TREND_ICON_SIZE
        : priceY + TREND_ICON_CLEARANCE;
      icon = { left: centerX - TREND_ICON_SIZE / 2, top,
        right: centerX + TREND_ICON_SIZE / 2, bottom: top + TREND_ICON_SIZE, size: TREND_ICON_SIZE };
    }
  }
  return { lineX, lineBottom: height, icon };
}

export function drawTrendTransitions(ctx, group, { timeToX, priceToY, height }) {
  for (const transition of group.trendTransitions || []) {
    const bullish = transition.direction !== "bearish";
    const color = bullish ? TREND_COLOR : BEARISH_TREND_COLOR;
    const marker = trendTransitionLayout(transition, { timeToX, priceToY, height });
    ctx.save();
    ctx.strokeStyle = color;
    ctx.lineWidth = 1;
    ctx.setLineDash([6, 5]);
    if (Number.isFinite(marker.lineX)) {
      ctx.beginPath();
      ctx.moveTo(marker.lineX, 0);
      ctx.lineTo(marker.lineX, marker.lineBottom);
      ctx.stroke();
    }
    if (marker.icon) {
      const { left, top, size } = marker.icon;
      ctx.translate(left, top + (bullish ? 0 : size));
      ctx.scale(size / 20, (bullish ? 1 : -1) * size / 20);
      ctx.setLineDash([]);
      ctx.lineWidth = 2.4;
      ctx.lineCap = "round";
      ctx.lineJoin = "round";
      ctx.beginPath();
      ctx.moveTo(1.2, 18.8);
      ctx.lineTo(6.1, 12.2);
      ctx.lineTo(9.3, 15.4);
      ctx.lineTo(13.7, 8.4);
      ctx.lineTo(16, 10.5);
      ctx.lineTo(18.8, 1.2);
      ctx.stroke();
      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.moveTo(13.2, 3);
      ctx.lineTo(18.8, 1.2);
      ctx.lineTo(18.1, 7);
      ctx.closePath();
      ctx.fill();
    }
    ctx.restore();
  }
}

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
  const output = [];
  for (const [kind, rows] of [["PH", group.primaryHighs], ["PL", group.primaryLows]]) {
    for (const item of rows || []) {
      if (item.calculationValid === false) continue;
      const marker = primaryMarkerLayout(kind, direction, 0, 0, settings);
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
      const marker = primaryMarkerLayout(kind, direction, shifted.x, shifted.y, settings);
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
