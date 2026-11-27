const LIQUIDITY_COLOR = "#b8b8b8";
const LIQUIDITY_LABEL = "$$$";
const LABEL_PADDING = 5;

export function liquidityObjectId(direction, time) {
  return `indicator:${direction}:liquidity:${time}`;
}

export function liquidityEndpoints(item) {
  return item.liquidityEdit ?? {
    a: { time: item.time, price: Number(item.price) },
    b: { time: item.endTime, price: Number(item.price) },
  };
}

export function liquidityVisualObjects(group, direction) {
  return (group.liquidity || []).filter(level => level.visibleFrom != null && level.lineEndTime != null)
    .map(level => ({
      id: liquidityObjectId(direction, level.sourceTime), type: "indicator-liquidity", direction,
      name: level.collectedTime == null ? "Active liquidity" : "Collected liquidity",
      time: level.sourceTime, price: level.price, endTime: level.lineEndTime, color: LIQUIDITY_COLOR,
      text: LIQUIDITY_LABEL, width: 0.5, lineStyle: "solid",
    }));
}

export function drawLiquidityLines(ctx, levels, { settings, timeToX, priceToY, labelSizeAt, width, height, direction, objectFor = () => null, onHit = () => {}, dash = () => [] }) {
  ctx.save();
  ctx.beginPath();
  ctx.rect(0, 0, width, height);
  ctx.clip();
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  const gapsBySize = new Map();

  for (const level of levels) {
    if (level.visibleFrom == null || level.lineEndTime == null) continue;
    const visibility = level.collectedTime == null ? "liquidityActiveVisible" : "liquidityCollectedVisible";
    if (settings[visibility] === false) continue;
    if (level.repeatGroupSourceTime != null && settings.liquidityRepeatedVisible === false) continue;

    const objectId = liquidityObjectId(direction, level.sourceTime);
    const object = objectFor(objectId);
    if (object?.hidden) continue;
    const style = object?.customized ? object : null;
    const { a, b } = liquidityEndpoints(object ?? {
      time: level.sourceTime, endTime: level.lineEndTime, price: level.price,
    });
    const ax = timeToX(a.time), bx = timeToX(b.time);
    const ay = priceToY(a.price), by = priceToY(b.price);
    if (![ax, bx, ay, by].every(Number.isFinite)) continue;
    const [x1, x2, y1, y2] = ax <= bx ? [ax, bx, ay, by] : [bx, ax, by, ay];
    if (x2 <= x1 || x2 < 0 || x1 > width || Math.max(y1, y2) < 0 || Math.min(y1, y2) > height) continue;

    const top = Math.floor(y1) + 0.5, bottom = Math.floor(y2) + 0.5;
    const middle = (x1 + x2) / 2;
    const middleY = (top + bottom) / 2;
    const labelSize = style?.size ?? labelSizeAt(level.sourceTime);
    const label = style?.text ?? LIQUIDITY_LABEL;
    ctx.font = `500 ${labelSize}px system-ui, sans-serif`;
    const metricKey = `${labelSize}:${label}`;
    if (!gapsBySize.has(metricKey)) {
      gapsBySize.set(metricKey, ctx.measureText(label).width / 2 + LABEL_PADDING);
    }
    const labelHalfGap = label ? gapsBySize.get(metricKey) : 0;
    const gapRise = (bottom - top) / (x2 - x1) * labelHalfGap;
    ctx.strokeStyle = ctx.fillStyle = style?.color ?? LIQUIDITY_COLOR;
    ctx.lineWidth = style?.width ?? 0.5;
    ctx.setLineDash(dash(style?.lineStyle ?? "solid"));
    ctx.beginPath();
    ctx.moveTo(x1, top);
    if (label && x2 - x1 > 2 * labelHalfGap + 2) {
      ctx.lineTo(middle - labelHalfGap, middleY - gapRise);
      ctx.moveTo(middle + labelHalfGap, middleY + gapRise);
      if (middle + labelHalfGap > 0 && middle - labelHalfGap < width) {
        ctx.fillText(label, middle, middleY);
      }
    }
    ctx.lineTo(x2, bottom);
    ctx.stroke();
    onHit({ objectId, shape: "line", x1, y1: top, x2, y2: bottom, clipRight: width,
      handles: [{ x: ax, y: ay, level: "a" }, { x: bx, y: by, level: "b" }] });
  }
  ctx.restore();
}
