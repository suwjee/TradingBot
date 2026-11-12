import test from "node:test";
import assert from "node:assert/strict";
import * as annotations from "../../src/chart/setup-annotations.js";
import { editPositionLevel, editPositionTime } from "../../src/drawings/drawing-math.js";

const setup = { id: "bullish:setup:PL:source:confirmation", anchorKind: "PL", anchorNumber: 2,
  entryTime: 1060, entryPrice: "110", targetPrice: "150", stopPrice: "100", widthBars: 50 };
const candles = Array.from({ length: 80 }, (_, i) => ({ time: 1000+i*30+(i>=10?3600:0) }));

test("indicator setup objects reuse Engine prices and 50 actual chart intervals", () => {
  const original=structuredClone(setup);
  const [object]=annotations.setupVisualObjects({ positionSetups: [setup] }, "bullish");
  assert.equal(object.type,"indicator-position");
  assert.equal(object.locked,false);
  const drawing=annotations.setupPositionDrawing(object,candles,30);
  assert.deepEqual(drawing.a,{time:1060,price:110});
  assert.deepEqual(drawing.b,{time:candles[52].time,price:150});
  assert.equal(drawing.stopPrice,100);
  assert.deepEqual(setup,original);
});

test("saved automatic-position edits keep TP SL and horizontal boundaries independent", () => {
  const [object]=annotations.setupVisualObjects({positionSetups:[setup]},"bullish");
  const drawing=annotations.setupPositionDrawing(object,candles,30);
  object.position=editPositionLevel(drawing,"target",130);
  object.position=editPositionTime(object.position,"end",candles[62].time);
  const restored=annotations.setupPositionDrawing(JSON.parse(JSON.stringify(object)),candles,60);
  assert.equal(restored.b.price,130);
  assert.equal(restored.stopPrice,100);
  assert.equal(restored.b.time,candles[62].time);
  assert.equal(setup.targetPrice,"150");
});

test("status labels are projections of Engine T F and match existing physical objects", () => {
  const group={stopAlls:[{sourceIndex:2,sourceTime:1060,price:"100"}],
    sZones:[{sourceIndex:3,sourceTime:1090,price:"103"}],
    stopAllAssessments:[{sourceIndex:2,sourceTime:1060,status:"F",scopeId:"fresh"},
      {sourceIndex:4,sourceTime:1120,status:null}],
    behaviorAssessments:[{kind:"S",sourceIndex:3,sourceTime:1090,status:"F",anchorSourceIndex:2}]};
  const labels=annotations.setupVisualObjects(group,"bullish");
  assert.deepEqual(labels.map(r=>[r.text,r.price,r.color]),[["F","100","#f23645"],["F","103","#f23645"]]);
  const calls=[];
  const ctx={save(){},restore(){},fillText(...args){calls.push(args);}};
  annotations.drawSetupStatusLabels(ctx,labels,{timeToX:t=>t,priceToY:p=>p,
    objectFor:id=>labels.find(r=>r.id===id),offsetPoint:(_,x,y)=>({x,y}),
    settings:{stopAllSize:15,stopAllRadius:8,stopAllGap:16,sSize:12,sGap:8},onHit(){}});
  assert.equal(calls.length,2);
  assert.ok(calls[0][2]>100+8+16+15);
  assert.ok(calls[1][2]>103+8+12);
});

test("hidden annotations and pending states do not draw and rendering has no state decisions", () => {
  const group={positionSetups:[setup],stopAlls:[{sourceIndex:2,sourceTime:1060,price:"100"}],
    stopAllAssessments:[{sourceIndex:2,sourceTime:1060,status:"T"}]};
  const objects=annotations.setupVisualObjects(group,"bullish");
  const label=objects.find(r=>r.type==="indicator-label");label.hidden=true;
  const ctx={save(){throw new Error("Hidden label rendered");}};
  annotations.drawSetupStatusLabels(ctx,objects,{objectFor:id=>objects.find(r=>r.id===id)});
  assert.equal(label.color,"#089981");
  assert.deepEqual(annotations.setupVisualObjects({},"bearish"),[]);
});

test("setup status labels follow the owning module visibility", () => {
  const group={stopAlls:[{sourceIndex:2,sourceTime:1060,price:"100"}],
    stopAllAssessments:[{sourceIndex:2,sourceTime:1060,status:"F"}]};
  const objects=annotations.setupVisualObjects(group,"bullish");
  const ctx={save(){assert.fail("A disabled module must not leave a status label");}};
  annotations.drawSetupStatusLabels(ctx,objects,{objectFor:()=>null,timeToX:t=>t,
    priceToY:p=>p,offsetPoint:(_,x,y)=>({x,y}),settings:{stopAllVisible:false}});
});

function renderStatuses(settings, customize = () => {}) {
  const group = { stopAlls: [{ sourceIndex: 2, sourceTime: 1060, price: "100" },
    { sourceIndex: 3, sourceTime: 1090, price: "105" }],
    stopAllAssessments: [{ sourceIndex: 2, sourceTime: 1060, status: "T" },
      { sourceIndex: 3, sourceTime: 1090, status: "F" }] };
  const objects = annotations.setupVisualObjects(group, "bullish");
  customize(objects);
  const calls = [], hits = [];
  const ctx = { save() {}, restore() {}, measureText: () => ({ width: 24 }),
    fillText(text, x, y) { calls.push({ text, x, y, color: this.fillStyle, font: this.font }); } };
  annotations.drawSetupStatusLabels(ctx, objects, { settings, objectFor: () => null,
    timeToX: t => t, priceToY: p => p, offsetPoint: (_, x, y) => ({ x, y }),
    onHit: hit => hits.push(hit) });
  return { calls, hits, objects };
}

test("T and F appearance settings are independent and zero distance is respected", () => {
  const { calls, hits } = renderStatuses({ setupTSize: 28, setupTColor: "#123456", setupTGap: 0,
    setupFSize: 18, setupFColor: "#abcdef", setupFGap: 64 });
  assert.deepEqual(calls, [
    { text: "T", x: 1060, y: 139, color: "#123456", font: "600 28px Inter, sans-serif" },
    { text: "F", x: 1090, y: 208, color: "#abcdef", font: "600 18px Inter, sans-serif" },
  ]);
  assert.equal(hits[0].bottom - hits[0].top, 28);
  assert.equal(hits[0].right - hits[0].left, 24);
});

test("T and F toggles suppress only their own rendering and hit boxes", () => {
  for (const status of ["T", "F"]) {
    const { calls, hits } = renderStatuses({ [`setup${status}Visible`]: false });
    assert.deepEqual(calls.map(row => row.text), [status === "T" ? "F" : "T"]);
    assert.equal(hits.length, 1);
  }
  assert.deepEqual(renderStatuses({ setupTVisible: false, setupFVisible: false }).hits, []);
});

test("global appearance respects individual customizations and hidden objects", () => {
  const { calls } = renderStatuses({ setupTSize: 28, setupTColor: "#123456" }, objects => {
    Object.assign(objects[0], { customized: true, size: 14, color: "#ffffff", text: "Edited" });
    objects[1].hidden = true;
  });
  assert.equal(calls.length, 1);
  assert.equal(calls[0].font, "600 14px Inter, sans-serif");
  assert.equal(calls[0].color, "#ffffff");
  assert.equal(renderStatuses({ setupTVisible: false }, objects => {
    objects[0].text = "Edited";
  }).calls.length, 1);
});

test("position visibility does not affect manual drawings, labels or Engine setup data", () => {
  const group = { positionSetups: [setup] }, before = structuredClone(group);
  const [object] = annotations.setupVisualObjects(group, "bullish");
  assert.equal(annotations.setupObjectVisible(object, {}), true);
  assert.equal(annotations.setupObjectVisible(object, { setupPositionsVisible: false }), false);
  assert.equal(annotations.setupObjectVisible({ type: "long" }, { setupPositionsVisible: false }), true);
  assert.equal(annotations.setupObjectVisible({ ...object, hidden: true }, { setupPositionsVisible: true }), false);
  assert.equal(renderStatuses({ setupPositionsVisible: false }).calls.length, 2);
  assert.deepEqual(group, before);
});
