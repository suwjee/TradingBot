// Present finalized Engine decisions without detecting trades in the browser.
import { calculatePositionLevels, positionEndTime } from "../drawings/drawing-math.js";

export const SETUP_VISUAL_DEFAULTS = Object.freeze({
  setupTVisible: true, setupFVisible: true, setupPositionsVisible: true,
  setupTColor: "#089981", setupFColor: "#f23645",
  setupTSize: 10, setupFSize: 10, setupTGap: 3, setupFGap: 3,
});

export function setupObjectVisible(object, settings = {}) {
  if (object.hidden) return false;
  if (object.type === "indicator-position") return settings.setupPositionsVisible !== false;
  if (!object.setupStatusKind) return true;
  const status = object.setupStatus || object.text;
  const ownerKey = object.setupStatusKind === "StopAll" ? "stopAllVisible"
    : object.setupStatusKind === "S" ? "sVisible" : "eVisible";
  return settings[`setup${status}Visible`] !== false && settings[ownerKey] !== false;
}

export function setupVisualObjects(group, direction) {
  if (direction !== "bullish") return [];
  const objects = (group.positionSetups || []).map(setup => ({
    id: setup.id, type: "indicator-position", name: `Buy ${setup.anchorKind}-${setup.anchorNumber}`,
    time: setup.entryTime, price: setup.entryPrice, targetPrice: setup.targetPrice,
    stopPrice: setup.stopPrice, widthBars: setup.widthBars, color: "#2962ff", width: 0.5,
    locked: false,
  }));
  const sources = Object.fromEntries([["StopAll", "stopAlls"], ["S", "sZones"], ["E", "eZones"]]
    .map(([kind, key]) => [kind, new Map((group[key] || []).map(row => [row.sourceIndex, row]))]));
  for (const [kind, rows] of [["StopAll", group.stopAllAssessments || []],
    [null, group.behaviorAssessments || []]]) {
    for (const row of rows) {
      const ownerKind = kind || row.kind;
      const source = sources[ownerKind]?.get(row.sourceIndex);
      if (!source || !["T", "F"].includes(row.status)) continue;
      objects.push({id:`indicator:bullish:setup-status:${ownerKind}:${row.sourceTime}:${row.sourceIndex}`,
        type:"indicator-label", name:`${ownerKind} ${row.status}`, text:row.status,
        time:row.sourceTime, price:source.price, size:10, weight:600,
        color:SETUP_VISUAL_DEFAULTS[`setup${row.status}Color`],
        setupStatus:row.status, setupStatusKind:ownerKind});
    }
  }
  return objects;
}

export function setupPositionDrawing(object, candles, timeframe) {
  const base = {type:"long",id:object.id,locked:object.locked,
    a:{time:Number(object.time),price:Number(object.price)},
    b:{time:positionEndTime(candles,Number(object.time),timeframe,Number(object.widthBars)||50),
      price:Number(object.targetPrice)},stopPrice:Number(object.stopPrice)};
  const edited = object.position;
  const valid = edited && Number.isFinite(Number(edited.a?.time)) &&
    Number(edited.b?.time) > Number(edited.a.time) &&
    calculatePositionLevels("long", edited.a.price, edited.b.price, edited.stopPrice);
  const position = valid ? {a:{...edited.a},b:{...edited.b},stopPrice:edited.stopPrice} : {};
  return {...base,...position,style:{stroke:object.color||"#2962ff",width:object.width||0.5}};
}

export function drawSetupStatusLabels(ctx, objects, options) {
  for (const original of objects) {
    if (!original.setupStatusKind) continue;
    const object = options.objectFor(original.id) || original;
    const {settings = {}} = options;
    if (!setupObjectVisible(object, settings)) continue;
    const prefix = `setup${original.setupStatus || original.text}`;
    const kind = original.setupStatusKind;
    const x = options.timeToX(object.time), y = options.priceToY(Number(object.price));
    if (!Number.isFinite(x) || !Number.isFinite(y)) continue;
    const ownerGap = kind === "StopAll" ? (settings.stopAllRadius??8)+(settings.stopAllGap??16)+(settings.stopAllSize??15)
      : (kind === "S" ? (settings.sGap??8)+(settings.sSize??12) : (settings.eGap??8)+(settings.eSize??12));
    const gap = ownerGap + (settings[`${prefix}Gap`] ?? SETUP_VISUAL_DEFAULTS[`${prefix}Gap`]);
    const shifted = options.offsetPoint(object,x,y);
    const size = object.customized ? object.size || 10
      : settings[`${prefix}Size`] ?? SETUP_VISUAL_DEFAULTS[`${prefix}Size`];
    ctx.save();
    ctx.font = `${object.weight||600} ${size}px Inter, sans-serif`;
    ctx.textAlign = "center";
    ctx.textBaseline = "top";
    ctx.fillStyle = object.customized ? object.color
      : settings[`${prefix}Color`] ?? SETUP_VISUAL_DEFAULTS[`${prefix}Color`];
    ctx.fillText(object.text,shifted.x,shifted.y+gap);
    const halfWidth = Math.max(7, (ctx.measureText?.(object.text).width ?? size) / 2);
    ctx.restore();
    options.onHit({objectId:object.id,shape:"rect",left:shifted.x-halfWidth,right:shifted.x+halfWidth,
      top:shifted.y+gap,bottom:shifted.y+gap+size});
  }
}
