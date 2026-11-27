import {
  positionEndTime, positionLevels, positionRightTime, positionWidthBars,
} from "../drawings/drawing-math.js";

const POSITION_WIDTH_BARS = 50;
const POSITION_TYPES = ["1.1", "1.2", "2.1", "2.2", "3.1", "3.2", "3.3"];
export const POSITION_VISIBILITY_GROUPS = [
  ["Buy", POSITION_TYPES.map(type => `${type}B`)],
  ["Sell", POSITION_TYPES.map(type => `${type}S`)],
];
const typesBySide = { buy: POSITION_VISIBILITY_GROUPS[0][1], sell: POSITION_VISIBILITY_GROUPS[1][1] };
const validTypes = new Set(POSITION_VISIBILITY_GROUPS.flatMap(([, types]) => types));
const POSITION_FONT = '500 10px Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif';

export function positionVisibilityKey(type) {
  return `position${type.replace(".", "_")}Visible`;
}

export function isIndicatorPosition(item) {
  return item?.type === "indicator-position" && validTypes.has(item.positionType);
}

export function isPositionOverrideId(id) {
  return /^indicator:(bullish|bearish):position:/.test(id);
}

function positionObject(row, direction) {
  const side = row?.side;
  if ((side !== "buy" && side !== "sell") || !typesBySide[side].includes(row.type) || typeof row.id !== "string" || !row.id
    || [row.entryTime, row.entryPrice, row.targetPrice, row.stopPrice].some(value =>
      value == null || value === "" || !Number.isFinite(Number(value)))) return null;
  return {
    id: `indicator:${direction}:position:${encodeURIComponent(row.id)}`,
    type: "indicator-position",
    positionType: row.type,
    side,
    name: row.type,
    time: Number(row.entryTime),
    price: Number(row.entryPrice),
    targetPrice: Number(row.targetPrice),
    stopPrice: Number(row.stopPrice),
    color: "#2962ff",
  };
}

export function indicatorPositionObjects(group, direction) {
  const rows = [...(group.positions || []),
    ...(group.calculationSegments || []).flatMap(segment => segment.positions || [])];
  const unique = new Map();
  for (const row of rows) {
    const item = positionObject(row, direction);
    if (item && !unique.has(item.id)) unique.set(item.id, item);
  }
  return [...unique.values()];
}

export function indicatorPositionDrawing(item, candles, timeframe) {
  const edit = item.positionEdit;
  const time = edit?.time ?? item.time;
  return {
    type: item.side === "buy" ? "long" : "short",
    finalizedPosition: true,
    locked: item.locked,
    a: { time, price: edit?.entry ?? item.price },
    b: {
      time: positionEndTime(candles, time, timeframe, edit?.bars ?? POSITION_WIDTH_BARS),
      price: edit?.target ?? item.targetPrice,
    },
    stopPrice: edit?.stop ?? item.stopPrice,
  };
}

export function saveIndicatorPositionEdit(item, previous, edited, candles, timeframe) {
  const edit = { ...item.positionEdit };
  if (previous.a.time !== edited.a.time) edit.time = edited.a.time;
  if (previous.a.price !== edited.a.price) edit.entry = edited.a.price;
  if (previous.b.price !== edited.b.price) edit.target = edited.b.price;
  if (previous.stopPrice !== edited.stopPrice) edit.stop = edited.stopPrice;
  if (previous.a.time !== edited.a.time || previous.b.time !== edited.b.time) {
    edit.bars = positionWidthBars(candles, edited.a.time, edited.b.time, timeframe);
  }
  item.positionEdit = edit;
}

export function positionGeometry(drawing, { candles, timeframe, timeToX, priceToY }) {
  const levels = positionLevels(drawing);
  if (!levels) return null;
  const left = timeToX(drawing.a.time);
  const right = timeToX(positionRightTime(drawing, candles, timeframe));
  const entry = priceToY(levels.entry), target = priceToY(levels.target), stop = priceToY(levels.stop);
  if (![left, right, entry, target, stop].every(Number.isFinite)) return null;
  const handles = [
    { x: left, y: target, level: "target" },
    { x: right, y: target, level: "target" },
    { x: left, y: stop, level: "stop" },
    { x: right, y: stop, level: "stop" },
    { x: left, y: entry, level: "start" },
    { x: right, y: entry, level: "end" },
  ];
  return { left, right, entry, target, stop, levels, handles };
}

export function paintPositionBoxes(ctx, { left, right, entry, target, stop }, { stroke, width, entryDash = [4, 3] }) {
  const reward = [left, Math.min(entry, target), right - left, Math.abs(entry - target)];
  const risk = [left, Math.min(entry, stop), right - left, Math.abs(entry - stop)];
  ctx.fillStyle = "rgba(8, 153, 129, 0.10)";
  ctx.fillRect(...reward);
  ctx.fillStyle = "rgba(242, 54, 69, 0.10)";
  ctx.fillRect(...risk);
  ctx.lineWidth = width;
  ctx.strokeStyle = "#089981";
  ctx.strokeRect(...reward);
  ctx.strokeStyle = "#f23645";
  ctx.strokeRect(...risk);
  ctx.strokeStyle = stroke;
  ctx.setLineDash(entryDash);
  ctx.beginPath();
  ctx.moveTo(left, entry);
  ctx.lineTo(right, entry);
  ctx.stroke();
}

export function drawIndicatorPositions(ctx, rows, {
  direction, candles, timeframe, timeToX, priceToY, rightBoundary, settings, objectFor, hits, dash,
}) {
  for (const row of rows) {
    const base = positionObject(row, direction);
    if (!base || settings[positionVisibilityKey(base.positionType)] === false) continue;
    const item = objectFor(base.id) ?? base;
    if (item.hidden) continue;
    const drawing = indicatorPositionDrawing(item, candles, timeframe);
    const geometry = positionGeometry(drawing, { candles, timeframe, timeToX, priceToY });
    if (!geometry) continue;
    const { left, right, entry, target, stop, handles } = geometry;
    const visibleLeft = Math.max(left, 0), visibleRight = Math.min(right, rightBoundary);
    if (visibleRight <= visibleLeft) continue;
    const buy = base.side === "buy";
    const labelY = buy ? Math.max(entry, stop) + 3 : Math.min(entry, stop) - 3;
    const labelX = (visibleLeft + visibleRight) / 2;
    hits.push({
      objectId: base.id, shape: "rect", area: true, left, right: visibleRight,
      top: Math.min(entry, target, stop), bottom: Math.max(entry, target, stop),
      clipRight: rightBoundary, handles: handles.filter(handle => handle.x >= 0 && handle.x <= rightBoundary),
    });
    ctx.save();
    paintPositionBoxes(ctx, geometry, {
      stroke: item.color ?? base.color,
      width: item.width ?? 0.5,
      entryDash: item.lineStyle ? dash(item.lineStyle) : undefined,
    });
    ctx.fillStyle = "#171a21";
    ctx.font = POSITION_FONT;
    ctx.textAlign = "center";
    ctx.textBaseline = buy ? "top" : "bottom";
    ctx.fillText(base.positionType, labelX, labelY);
    ctx.restore();
  }
}
