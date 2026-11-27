import { clipHistoricalHitBoxes, drawPrimaryStructures, drawTrendTransitions, indicatorCalculationSegments } from "./primary-structure.js";
import { drawIndicatorText, drawTrueFalseLabel, trueFalseAppearance, trueFalseVisualObjects, TRUE_FALSE_STOPALL_PRIMARY_WEIGHT } from "./true-false-label.js";
import { drawIndicatorPositions } from "./indicator-positions.js";
import { drawLiquidityLines } from "./indicator-liquidity.js";

export const INDICATOR_MARKER_DEFAULTS = Object.freeze({
  aSize: 10,
  sSize: 10,
  eSize: 10,
  stopAllSize: 14,
  stopAllRadius: 5,
});

const liquiditySourceMarkers = new WeakMap();

function behaviorLabelSize(object, settings, key) {
  return (object?.customized ? object.size : undefined) ?? settings[key] ?? INDICATOR_MARKER_DEFAULTS[key];
}

function reactionNumbers(group, mode) {
  const boundaries = mode === "reset"
    ? (group.__sortedResets ||= [...(group.resets || [])].sort((a, b) => a.index - b.index))
    : mode === "a"
      ? (group.__sortedAZones ||= [...(group.aZones || [])]
        .filter(zone => zone.calculationValid !== false)
        .sort((a, b) => Number(a.sourceIndex) - Number(b.sourceIndex)))
      : [];
  let count = 0, previousFirst = -1, cursor = 0;
  return (group.reactions || []).map(reaction => {
    let restart = false;
    while (cursor < boundaries.length) {
      const index = Number(mode === "reset" ? boundaries[cursor].index : boundaries[cursor].sourceIndex);
      if (index > reaction.firstIndex) break;
      if (index > previousFirst) restart = true;
      cursor++;
    }
    count = restart ? 1 : count + 1;
    previousFirst = reaction.firstIndex;
    return String(count);
  });
}

export function indicatorDecorationObjects(group, direction, settings, offsets) {
  const foundation = trueFalseAppearance(settings, "foundation");
  const secondary = trueFalseAppearance(settings, "secondary");
  const sourceOfE = new Set((group.eZones || []).map(item => Number(item.sourceIndex)));
  const sourceOfStopAll = new Set((group.stopAlls || []).map(item => Number(item.sourceIndex)));
  const numbers = settings.numberEnabled ? reactionNumbers(group, settings.numberMode) : [];
  const objects = numbers.map((number, index) => {
    const item = group.reactions[index];
    const ordinal = index + offsets.reactions;
    return {
      id: `indicator:${direction}:reaction:${ordinal}:number`, type: "indicator-label",
      name: `Reaction ${ordinal + 1} number`, text: number,
      time: item.firstTime, price: direction === "bullish" ? item.boxBottom : item.boxTop,
      size: settings.numberSize, weight: settings.numberWeight, color: settings.numberColor,
    };
  });
  for (const [field, key, appearance, weight] of [
    ["sZones", "s", foundation], ["eZones", "e", foundation],
    ["stopAlls", "stopall", secondary, TRUE_FALSE_STOPALL_PRIMARY_WEIGHT],
  ]) {
    for (const [index, item] of (group[field] || []).entries()) {
      if (key === "s" && (sourceOfE.has(Number(item.sourceIndex)) || sourceOfStopAll.has(Number(item.sourceIndex)))) continue;
      const id = `indicator:${direction}:${key}:${index + offsets[field]}`;
      const sizeKey = key === "stopall" ? "stopAllSize" : `${key}Size`;
      const size = settings[sizeKey] ?? INDICATOR_MARKER_DEFAULTS[sizeKey];
      const label = key === "s" ? "S" : key === "e" ? `E${item.number}` : `StopAll ${item.number}`;
      for (const object of trueFalseVisualObjects(id, item, size, appearance, { weight, repeated: item.trueFalseRepeated === true })) {
        objects.push({ ...object, name: `${label} ${object.text}` });
      }
    }
  }
  return objects;
}

export function drawIndicator(canvasWidth, canvasHeight, {
  ctx, state, indicatorTimeToCoordinate, overlayPriceCoordinate, priceToY,
  indicatorObject, indicatorOffsetPixels, offsetIndicatorPoint, offsetIndicatorRect,
  rgba, dash, plotWidth = canvasWidth, plotHeight = canvasHeight,
  positionTimeToCoordinate = indicatorTimeToCoordinate,
}) {
  state.indicator.hitBoxes = [];
  if (!state.indicator.enabled || !state.indicator.results) return;
  const settings = state.indicator.settings,
    timeframe = Number(state.indicator.results.timeframe || state.tf),
    secondaryVerdict = trueFalseAppearance(settings, "secondary"),
    foundationVerdict = trueFalseAppearance(settings, "foundation");
  const onHit = hit => state.indicator.hitBoxes.push(hit);
  const textObjects = { objectFor: indicatorObject, offsetPoint: offsetIndicatorPoint, onHit };
  const trendTransitions = [];
  for (const { direction, group, objectOffsets } of indicatorCalculationSegments(state.indicator.results)) {
    ctx.save();
    const bullish = direction === "bullish",
      eSourceIndices = group.__eSourceIndices ||= new Set(
        (group.eZones || []).map((zone) => Number(zone.sourceIndex)),
      ),
      stopAllSourceIndices = group.__stopAllSourceIndices ||= new Set(
        (group.stopAlls || []).map((zone) => Number(zone.sourceIndex)),
      ),
      sSourceIndices = group.__sSourceIndices ||= new Set(
        (group.sZones || [])
          .filter((zone) => zone.calculationValid !== false)
          .map((zone) => Number(zone.sourceIndex)),
      ),
      fill = bullish ? settings.bullFill : settings.bearFill,
      border = bullish ? settings.bullBorder : settings.bearBorder,
      opacity = (bullish ? settings.bullOpacity : settings.bearOpacity) / 100,
      width = bullish ? settings.bullWidth : settings.bearWidth;
    if (group.liquidity?.length) {
      let sources = liquiditySourceMarkers.get(group);
      if (!sources) {
        sources = new Map();
        for (const [field, kind] of [["eZones", "e"], ["sZones", "s"]]) {
          for (const [index, zone] of (group[field] || []).entries()) {
            if (zone.calculationValid !== false && !sources.has(zone.sourceTime)) {
              sources.set(zone.sourceTime, { kind, field, index });
            }
          }
        }
        liquiditySourceMarkers.set(group, sources);
      }
      drawLiquidityLines(ctx, group.liquidity, {
        settings, timeToX: positionTimeToCoordinate, priceToY: overlayPriceCoordinate,
        direction, objectFor: indicatorObject, onHit, dash,
        labelSizeAt: time => {
          const marker = sources.get(time);
          const object = marker && indicatorObject?.(
            `indicator:${direction}:${marker.kind}:${marker.index + objectOffsets[marker.field]}`,
          );
          return behaviorLabelSize(object, settings, marker?.kind === "s" ? "sSize" : "eSize");
        },
        width: plotWidth, height: plotHeight,
      });
    }
    if (group.positions?.length) {
      ctx.save();
      if (plotWidth < canvasWidth || plotHeight < canvasHeight) {
        ctx.beginPath();
        ctx.rect(0, 0, plotWidth, plotHeight);
        ctx.clip();
      }
      drawIndicatorPositions(ctx, group.positions, {
        direction, candles: state.data ?? [], timeframe: state.tf, timeToX: positionTimeToCoordinate,
        priceToY: overlayPriceCoordinate, settings, objectFor: indicatorObject ?? (() => undefined),
        hits: state.indicator.hitBoxes, dash,
        rightBoundary: plotWidth,
      });
      ctx.restore();
    }
    const firstHitIndex = state.indicator.hitBoxes.length;
    const historicalEndX = group.calculationEndTime != null
      ? indicatorTimeToCoordinate(group.calculationEndTime) : null;
    if (Number.isFinite(historicalEndX)) {
      ctx.beginPath();
      ctx.rect(0, 0, Math.max(0, historicalEndX), canvasHeight);
      ctx.clip();
    }
    const numbers = settings.numberEnabled ? reactionNumbers(group, settings.numberMode) : [];
    for (const [reactionIndex, reaction] of group.reactions.entries()) {
      const reactionObjectId = `indicator:${direction}:reaction:${reactionIndex + objectOffsets.reactions}`;
      if (!settings.reactionVisible) continue;
      const reactionObject = indicatorObject(reactionObjectId);
      const startTime = bullish
          ? reaction.boxTopSourceTime
          : reaction.boxBottomSourceTime,
        x1 = indicatorTimeToCoordinate(startTime),
        x2 = indicatorTimeToCoordinate(reaction.breakTime);
      if (x1 == null || x2 == null) continue;
      const offset = indicatorOffsetPixels(reactionObject);
      const left = Math.min(x1, x2) + offset.x, right = Math.max(x1, x2) + offset.x;
      const appearance = reactionObject?.customized ? reactionObject : null;
      const strokeWidth = appearance?.width ?? width;
      const label = numbers[reactionIndex] ?? "";
      const padding = Math.max(9, strokeWidth, label.length * settings.numberSize || 0);
      if (right < -padding || left > canvasWidth + padding) continue;
      const yTop = overlayPriceCoordinate(+reaction.boxTop), yBottom = overlayPriceCoordinate(+reaction.boxBottom);
      if (yTop == null || yBottom == null) continue;
      const top = Math.min(yTop, yBottom) + offset.y, bottom = Math.max(yTop, yBottom) + offset.y;
      if (!reactionObject?.hidden) {
        onHit({ objectId: reactionObjectId, shape: "rect", left, right, top, bottom, direction, reaction });
        ctx.save();
        ctx.fillStyle = rgba(appearance?.fill ?? fill, appearance?.opacity ?? opacity);
        ctx.strokeStyle = appearance?.color ?? border;
        ctx.lineWidth = strokeWidth;
        ctx.setLineDash(dash(appearance?.lineStyle ?? (bullish ? settings.bullLineStyle : settings.bearLineStyle)));
        ctx.beginPath();
        ctx.rect(left, top, Math.max(1, right - left), Math.max(1, bottom - top));
        ctx.fill();
        if (strokeWidth > 0) ctx.stroke();
        ctx.restore();
      }
      if (settings.numberEnabled) {
        drawIndicatorText(ctx, label, (left + right) / 2,
          bullish ? bottom + settings.numberGap : top - settings.numberGap, {
            ...textObjects, objectId: `${reactionObjectId}:number`, below: bullish,
            size: settings.numberSize, weight: settings.numberWeight, color: settings.numberColor,
          });
      }
    }
    if (settings.blueLineEnabled) {
      for (const [blueIndex, blueLine] of (group.blueLines || []).entries()) {
        const blueObjectId = `indicator:${direction}:blue:${blueIndex + objectOffsets.blueLines}`,
          blueObject = indicatorObject(blueObjectId);
        if (blueObject?.hidden) continue;
        const x1 = indicatorTimeToCoordinate(blueLine.startTime),
          x2 = indicatorTimeToCoordinate(blueLine.endTime),
          y = priceToY(+blueLine.linePrice);
        if ([x1, x2, y].some((value) => value == null)) continue;
        const shifted = offsetIndicatorRect(blueObject, x1, y, x2, y);
        state.indicator.hitBoxes.push({ objectId: blueObjectId, shape: "line", x1: shifted.x1, y1: shifted.y1, x2: shifted.x2, y2: shifted.y2 });
        const appearance = blueObject?.customized ? blueObject : null;
        ctx.save();
        ctx.strokeStyle = rgba(appearance?.color ?? settings.blueColor, appearance?.opacity ?? settings.blueOpacity / 100);
        ctx.lineWidth = appearance?.width ?? settings.blueWidth;
        ctx.lineCap = "round";
        ctx.setLineDash(dash(appearance?.lineStyle ?? settings.blueLineStyle));
        ctx.beginPath();
        ctx.moveTo(shifted.x1, shifted.y1);
        ctx.lineTo(shifted.x2, shifted.y2);
        ctx.stroke();
        ctx.restore();
      }
    }
    for (const [zoneIndex, zone] of (group.aZones || []).entries()) {
      const objectId = `indicator:${direction}:a:${zoneIndex + objectOffsets.aZones}`;
      if (!settings.aVisible) continue;
      if (
        eSourceIndices.has(Number(zone.sourceIndex)) ||
        stopAllSourceIndices.has(Number(zone.sourceIndex)) ||
        sSourceIndices.has(Number(zone.sourceIndex))
      )
        continue;
      const x = indicatorTimeToCoordinate(zone.sourceTime),
        y = priceToY(+zone.price);
      if (x == null || y == null) continue;
      drawIndicatorText(ctx, "A", x, bullish ? y + settings.aGap : y - settings.aGap, {
        ...textObjects, objectId, below: bullish, size: settings.aSize ?? INDICATOR_MARKER_DEFAULTS.aSize,
        color: settings.aColor || "#7c3aed", weight: 500,
      });
    }
    for (const [zoneIndex, zone] of (group.sZones || []).entries()) {
      const hasOrder = zone.calculationValid !== false && zone.orderFirstTime != null;
      const objectId = `indicator:${direction}:s:${zoneIndex + objectOffsets.sZones}`,
        orderObject = indicatorObject(`indicator:${direction}:s-order:${zoneIndex + objectOffsets.sZones}`),
        labelObject = indicatorObject(objectId);
      const orderBullish = zone.orderDirection === "bullish",
        orderStartTime = orderBullish
          ? zone.orderBoxTopSourceTime
          : zone.orderBoxBottomSourceTime,
        boxX1 = hasOrder ? indicatorTimeToCoordinate(orderStartTime) : null,
        boxX2 = hasOrder ? indicatorTimeToCoordinate(zone.orderBreakTime) : null,
        boxYTop = hasOrder ? priceToY(+zone.orderBoxTop) : null,
        boxYBottom = hasOrder ? priceToY(+zone.orderBoxBottom) : null;
      if (hasOrder && settings.orderVisible && !orderObject?.hidden && ![boxX1, boxX2, boxYTop, boxYBottom].some((v) => v == null)) {
        const shifted = offsetIndicatorRect(orderObject, boxX1, boxYTop, boxX2, boxYBottom),
          left = Math.min(shifted.x1, shifted.x2),
          right = Math.max(shifted.x1, shifted.x2),
          top = Math.min(shifted.y1, shifted.y2),
          bottom = Math.max(shifted.y1, shifted.y2);
        state.indicator.hitBoxes.push({ objectId: `indicator:${direction}:s-order:${zoneIndex + objectOffsets.sZones}`, shape: "rect", left, right, top, bottom });
        const appearance = orderObject?.customized ? orderObject : null;
        ctx.save();
        ctx.fillStyle = rgba(appearance?.fill ?? settings.orderFill, appearance?.opacity ?? settings.orderOpacity / 100);
        ctx.strokeStyle = appearance?.color ?? settings.orderColor;
        ctx.lineWidth = appearance?.width ?? settings.orderWidth;
        ctx.setLineDash(dash(appearance?.lineStyle ?? settings.orderLineStyle));
        ctx.beginPath();
        ctx.rect(left, top, Math.max(1, right - left), Math.max(1, bottom - top));
        ctx.fill();
        ctx.stroke();
        ctx.restore();
      }
      const x = indicatorTimeToCoordinate(zone.sourceTime),
        y = priceToY(+zone.price);
      if (x == null || y == null) continue;
      const shiftedLabel = offsetIndicatorPoint(labelObject, x, bullish ? y + settings.sGap : y - settings.sGap);
      if (eSourceIndices.has(Number(zone.sourceIndex)) || stopAllSourceIndices.has(Number(zone.sourceIndex))) continue;
      if (!settings.sVisible) continue;
      const defaultColor = zone.color === "red"
        ? settings.sBearColor || "#f23645"
        : settings.sBullColor || "#2563eb";
      const labelSize = behaviorLabelSize(labelObject, settings, "sSize");
      drawIndicatorText(ctx, "S", shiftedLabel.x, shiftedLabel.y, {
        objectId, objectFor: () => labelObject, onHit, below: bullish, size: labelSize, color: defaultColor, weight: 500,
      });
      drawTrueFalseLabel(ctx, zone.trueFalse, foundationVerdict.visible, labelSize,
        shiftedLabel.x, shiftedLabel.y + (bullish ? labelSize : -labelSize), bullish,
        undefined, zone.trueFalseRepeated === true, 0, foundationVerdict, zone, { ...textObjects, parentId: objectId });
    }
    for (const [zoneIndex, zone] of (group.eZones || []).entries()) {
      const objectId = `indicator:${direction}:e:${zoneIndex + objectOffsets.eZones}`,
        orderObject = indicatorObject(`indicator:${direction}:e-order:${zoneIndex + objectOffsets.eZones}`),
        labelObject = indicatorObject(objectId);
      const orderBullish = zone.orderDirection === "bullish",
        orderStartTime = orderBullish
          ? zone.orderBoxTopSourceTime
          : zone.orderBoxBottomSourceTime,
        boxX1 = indicatorTimeToCoordinate(orderStartTime),
        boxX2 = indicatorTimeToCoordinate(zone.orderBreakTime),
        boxYTop = priceToY(+zone.orderBoxTop),
        boxYBottom = priceToY(+zone.orderBoxBottom);
      if (settings.orderVisible && !orderObject?.hidden && ![boxX1, boxX2, boxYTop, boxYBottom].some((v) => v == null)) {
        const shifted = offsetIndicatorRect(orderObject, boxX1, boxYTop, boxX2, boxYBottom),
          left = Math.min(shifted.x1, shifted.x2),
          right = Math.max(shifted.x1, shifted.x2),
          top = Math.min(shifted.y1, shifted.y2),
          bottom = Math.max(shifted.y1, shifted.y2);
        state.indicator.hitBoxes.push({ objectId: `indicator:${direction}:e-order:${zoneIndex + objectOffsets.eZones}`, shape: "rect", left, right, top, bottom });
        const appearance = orderObject?.customized ? orderObject : null;
        ctx.save();
        ctx.fillStyle = rgba(appearance?.fill ?? settings.orderFill, appearance?.opacity ?? settings.orderOpacity / 100);
        ctx.strokeStyle = appearance?.color ?? settings.orderColor;
        ctx.lineWidth = appearance?.width ?? settings.orderWidth;
        ctx.setLineDash(dash(appearance?.lineStyle ?? settings.orderLineStyle));
        ctx.beginPath();
        ctx.rect(left, top, Math.max(1, right - left), Math.max(1, bottom - top));
        ctx.fill();
        ctx.stroke();
        ctx.restore();
      }
      const x = indicatorTimeToCoordinate(zone.sourceTime),
        y = priceToY(+zone.price);
      if (x == null || y == null) continue;
      const shiftedLabel = offsetIndicatorPoint(labelObject, x, bullish ? y + settings.eGap : y - settings.eGap);
      if (!settings.eVisible) continue;
      const defaultColor = zone.family === "red"
        ? settings.eRedColor || "#7f1d1d"
        : settings.eBlueColor || "#1e3a8a";
      const labelSize = behaviorLabelSize(labelObject, settings, "eSize");
      drawIndicatorText(ctx, `E${zone.number}`, shiftedLabel.x, shiftedLabel.y, {
        objectId, objectFor: () => labelObject, onHit, below: bullish, size: labelSize, color: defaultColor, weight: 600,
      });
      drawTrueFalseLabel(ctx, zone.trueFalse, foundationVerdict.visible, labelSize,
        shiftedLabel.x, shiftedLabel.y + (bullish ? labelSize : -labelSize), bullish,
        undefined, zone.trueFalseRepeated === true, 0, foundationVerdict, zone, { ...textObjects, parentId: objectId });
    }
    for (const [zoneIndex, zone] of (group.stopAlls || []).entries()) {
      const objectId = `indicator:${direction}:stopall:${zoneIndex + objectOffsets.stopAlls}`,
        object = indicatorObject(objectId),
        orderObject = indicatorObject(`indicator:${direction}:stopall-order:${zoneIndex + objectOffsets.stopAlls}`),
        orderBullish = zone.orderDirection === "bullish",
        orderStartTime = orderBullish
          ? zone.orderBoxTopSourceTime
          : zone.orderBoxBottomSourceTime,
        boxX1 = indicatorTimeToCoordinate(orderStartTime),
        boxX2 = indicatorTimeToCoordinate(zone.orderBreakTime),
        boxYTop = priceToY(+zone.orderBoxTop),
        boxYBottom = priceToY(+zone.orderBoxBottom),
        x = indicatorTimeToCoordinate(zone.sourceTime),
        y = priceToY(+zone.price);
      if (settings.orderVisible && !orderObject?.hidden && ![boxX1, boxX2, boxYTop, boxYBottom].some((value) => value == null)) {
        const shifted = offsetIndicatorRect(orderObject, boxX1, boxYTop, boxX2, boxYBottom),
          left = Math.min(shifted.x1, shifted.x2),
          right = Math.max(shifted.x1, shifted.x2),
          top = Math.min(shifted.y1, shifted.y2),
          bottom = Math.max(shifted.y1, shifted.y2);
        state.indicator.hitBoxes.push({ objectId: `indicator:${direction}:stopall-order:${zoneIndex + objectOffsets.stopAlls}`, shape: "rect", left, right, top, bottom });
        const appearance = orderObject?.customized ? orderObject : null;
        ctx.save();
        ctx.fillStyle = rgba(appearance?.fill ?? settings.orderFill, appearance?.opacity ?? settings.orderOpacity / 100);
        ctx.strokeStyle = appearance?.color ?? settings.orderColor;
        ctx.lineWidth = appearance?.width ?? settings.orderWidth;
        ctx.setLineDash(dash(appearance?.lineStyle ?? settings.orderLineStyle));
        ctx.beginPath();
        ctx.rect(left, top, Math.max(1, right - left), Math.max(1, bottom - top));
        ctx.fill();
        ctx.stroke();
        ctx.restore();
      }
      if (!settings.stopAllVisible || x == null || y == null) continue;
      const radius = settings.stopAllRadius ?? INDICATOR_MARKER_DEFAULTS.stopAllRadius,
        shifted = offsetIndicatorPoint(object, x, y);
      const appearance = object?.customized ? object : null;
      const color = appearance?.color ?? settings.stopAllBorder;
      if (!object?.hidden) {
        onHit({ objectId, shape: "point", x: shifted.x, y: shifted.y, radius: radius + 2 });
        ctx.save();
        ctx.fillStyle = rgba(settings.stopAllFill, settings.stopAllOpacity / 100);
        ctx.strokeStyle = color;
        ctx.lineWidth = appearance?.width ?? settings.stopAllWidth;
        ctx.beginPath();
        ctx.arc(shifted.x, shifted.y, radius, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();
        ctx.restore();
      }
      const labelSize = appearance?.size ?? settings.stopAllSize ?? INDICATOR_MARKER_DEFAULTS.stopAllSize;
      const labelY = shifted.y + (bullish ? 1 : -1) * (radius + settings.stopAllGap);
      drawIndicatorText(ctx, String(zone.number), shifted.x, labelY, {
        objectId, objectFor: () => object, onHit, below: bullish,
        size: labelSize, weight: object?.weight || 600, color,
      });
      drawTrueFalseLabel(ctx, zone.trueFalse, secondaryVerdict.visible, labelSize,
        shifted.x, labelY + (bullish ? labelSize : -labelSize), bullish,
        TRUE_FALSE_STOPALL_PRIMARY_WEIGHT, zone.trueFalseRepeated === true, 0, secondaryVerdict, zone,
        { ...textObjects, parentId: objectId });
    }
    if (settings.orderStopVisible) {
      const seen = new Set();
      for (const zone of [...(group.sZones || []), ...(group.eZones || []), ...(group.stopAlls || [])]) {
        if (zone.calculationValid === false) continue;
        if (zone.orderStopSourceIndex == null || zone.orderStopLevel == null) continue;
        const key = [zone.orderDirection, zone.orderFirstIndex, zone.orderStopSourceIndex].join(":");
        if (seen.has(key)) continue;
        seen.add(key);
        const stopObject = indicatorObject(`indicator:${direction}:stop:${key}`);
        if (stopObject?.hidden) continue;
        const stopIndex = Number(zone.orderStopSourceIndex),
          endIndex = Math.min(
            Number.isFinite(+zone.decisionIndex) ? +zone.decisionIndex : stopIndex + settings.orderStopCap,
            stopIndex + settings.orderStopCap,
          );
        const
          startTime = zone.orderStopSourceTime,
          endTime = Number(startTime) +
            Math.max(1, endIndex - stopIndex) *
              timeframe,
          visibleEndTime = Number.isFinite(+zone.decisionTime)
            ? Math.min(+zone.decisionTime, endTime)
            : endTime;
        const
          x1 = indicatorTimeToCoordinate(startTime),
          x2 = indicatorTimeToCoordinate(visibleEndTime),
          y = priceToY(+zone.orderStopLevel);
        if ([x1, x2, y].some((value) => value == null)) continue;
        const shifted = offsetIndicatorRect(stopObject, x1, y, x2, y);
        state.indicator.hitBoxes.push({ objectId: `indicator:${direction}:stop:${key}`, shape: "line", x1: shifted.x1, y1: shifted.y1, x2: shifted.x2, y2: shifted.y2 });
        const appearance = stopObject?.customized ? stopObject : null;
        ctx.save();
        ctx.strokeStyle = appearance?.color ?? settings.orderStopColor;
        ctx.lineWidth = appearance?.width ?? settings.orderStopWidth;
        ctx.lineCap = (appearance?.lineStyle ?? settings.orderStopLineStyle) === "dot" ? "round" : "butt";
        ctx.setLineDash(dash(appearance?.lineStyle ?? (settings.orderStopLineStyle || "dot")));
        ctx.beginPath();
        ctx.moveTo(shifted.x1, shifted.y1);
        ctx.lineTo(shifted.x2, shifted.y2);
        ctx.stroke();
        ctx.restore();
      }
    }
    const representedOrderKeys = new Set(
      [...(group.sZones || []), ...(group.eZones || []), ...(group.stopAlls || [])]
        .filter((item) => item.calculationValid !== false && item.orderFirstIndex != null && item.orderBreakIndex != null)
        .map((item) => `${item.orderFirstIndex}:${item.orderBreakIndex}`),
    );
    for (const [auditIndex, order] of (group.orderAudit || []).entries()) {
      const key = `${order.firstIndex}:${order.breakIndex}`;
      if (representedOrderKeys.has(key)) continue;
      const objectId = `indicator:${direction}:audit-order:${order.firstIndex}:${order.breakIndex}`,
        object = indicatorObject(objectId),
        orderBullish = order.direction === "bullish",
        startTime = orderBullish ? order.boxTopSourceTime : order.boxBottomSourceTime,
        x1 = indicatorTimeToCoordinate(startTime),
        x2 = indicatorTimeToCoordinate(order.breakTime),
        yTop = priceToY(+order.boxTop),
        yBottom = priceToY(+order.boxBottom);
      if (!settings.orderVisible || object?.hidden || [x1, x2, yTop, yBottom].some((value) => !Number.isFinite(value))) continue;
      const shifted = offsetIndicatorRect(object, x1, yTop, x2, yBottom),
        left = Math.min(shifted.x1, shifted.x2),
        right = Math.max(shifted.x1, shifted.x2),
        top = Math.min(shifted.y1, shifted.y2),
        bottom = Math.max(shifted.y1, shifted.y2);
      state.indicator.hitBoxes.push({ objectId, shape: "rect", left, right, top, bottom });
      const appearance = object?.customized ? object : null;
      ctx.save();
      ctx.fillStyle = rgba(appearance?.fill ?? settings.orderFill, appearance?.opacity ?? settings.orderOpacity / 100);
      ctx.strokeStyle = appearance?.color ?? settings.orderColor;
      ctx.lineWidth = appearance?.width ?? settings.orderWidth;
      ctx.setLineDash(dash(appearance?.lineStyle ?? settings.orderLineStyle));
      ctx.beginPath();
      ctx.rect(left, top, Math.max(1, right - left), Math.max(1, bottom - top));
      ctx.fill();
      ctx.stroke();
      ctx.restore();
    }
    if (settings.eStopVisible) {
      for (const [zoneIndex, zone] of (group.eZones || []).entries()) {
        const parentStopIndex = Number(zone.parentStopIndex),
          parentSourceIndex = Number(zone.parentSourceIndex);
        if (
          String(zone.parentType).toUpperCase() !== "E" ||
          !Number.isFinite(parentStopIndex) ||
          !Number.isFinite(parentSourceIndex) ||
          parentStopIndex - parentSourceIndex <= 350
        )
          continue;
        const objectId = `indicator:${direction}:e-stop:${zoneIndex + objectOffsets.eZones}`,
          stopObject = indicatorObject(objectId);
        if (stopObject?.hidden) continue;
        const x1 = indicatorTimeToCoordinate(zone.parentSourceTime),
          x2 = indicatorTimeToCoordinate(zone.parentStopTime),
          y = priceToY(+zone.parentPrice);
        if ([x1, x2, y].some((value) => value == null)) continue;
        const shifted = offsetIndicatorRect(stopObject, x1, y, x2, y);
        state.indicator.hitBoxes.push({
          objectId,
          shape: "line",
          x1: shifted.x1,
          y1: shifted.y1,
          x2: shifted.x2,
          y2: shifted.y2,
        });
        const appearance = stopObject?.customized ? stopObject : null;
        ctx.save();
        ctx.strokeStyle = appearance?.color ?? settings.eStopColor;
        ctx.lineWidth = appearance?.width ?? settings.eStopWidth;
        ctx.lineCap = (appearance?.lineStyle ?? settings.eStopLineStyle) === "dot" ? "round" : "butt";
        ctx.setLineDash(dash(appearance?.lineStyle ?? (settings.eStopLineStyle || "dot")));
        ctx.beginPath();
        ctx.moveTo(shifted.x1, shifted.y1);
        ctx.lineTo(shifted.x2, shifted.y2);
        ctx.stroke();
        ctx.restore();
      }
    }
    drawPrimaryStructures(ctx, group, {
      direction, settings, timeframe,
      timeToX: indicatorTimeToCoordinate,
      priceToY,
      objectFor: indicatorObject,
      offsetPoint: offsetIndicatorPoint,
      offsetRect: offsetIndicatorRect,
      onHit: (hit) => state.indicator.hitBoxes.push(hit),
    });
    if (Number.isFinite(historicalEndX)) {
      state.indicator.hitBoxes.push(...clipHistoricalHitBoxes(
        state.indicator.hitBoxes.splice(firstHitIndex), historicalEndX));
    }
    ctx.restore();
    for (const transition of group.trendTransitions || []) trendTransitions.push(transition);
  }
  drawTrendTransitions(ctx, { trendTransitions }, {
    timeToX: indicatorTimeToCoordinate,
    priceToY,
    width: plotWidth,
    height: plotHeight,
    settings,
    ...textObjects,
  });
}
