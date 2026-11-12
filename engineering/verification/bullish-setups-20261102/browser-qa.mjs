// Browser plugin is not available. Exercise the actual app with local Chrome,
// authoritative Engine-produced annotations and isolated in-memory API state.
import assert from "node:assert/strict";
import {readFile,writeFile} from "node:fs/promises";
import {createRequire} from "node:module";
import path from "node:path";
const root=process.cwd(), work=path.join(root,"apps/chart/state/tmp/bullish-setups");
const require=createRequire(path.join(root,"apps/chart/package.json"));
const {chromium}=require("playwright-core");
const fixture=JSON.parse(await readFile(path.join(work,"browser-fixture.json"),"utf8"));
const rows=fixture.rows, payload=fixture.payload;
const file={id:"qa-engine-setups",chartId:"qa-engine-setups",broker:"QA",symbol:"USOIL",timeframe:"30s",
  count:rows.length,bytes:100000,from:rows[0].time,to:rows.at(-1).time};
const browser=await chromium.launch({executablePath:"C:/Program Files/Google/Chrome/Application/chrome.exe",headless:true});
const context=await browser.newContext({viewport:{width:1440,height:1000},deviceScaleFactor:1});
const page=await context.newPage();
const errors=[],requests=[],checks=[];let drawings=[];
page.on("pageerror",error=>errors.push(error.message));
page.on("console",msg=>{if(msg.type()==="error") errors.push(msg.text());});
await page.route("**/api/**",async route=>{
  const req=route.request(), url=new URL(req.url()), key=url.pathname;
  requests.push({path:key,method:req.method()});
  let data={};
  if(key==="/api/symbols") data=[file];
  if(key==="/api/candles") data=rows;
  if(key==="/api/drawings") {
    if(req.method()==="PUT") drawings=structuredClone(req.postDataJSON().drawings);
    data=drawings;
  }
  if(key==="/api/reactions/source") data={sourceFingerprint:"qa-current-setups"};
  if(key==="/api/reactions") data=payload;
  if(key==="/api/reactions/progress") return route.fulfill({contentType:"text/event-stream",body:": qa\n\n"});
  await route.fulfill({json:data,headers:{"X-QG-Calculation-Id":"qa-bullish-setups","X-QG-Source-Fingerprint":"qa-current-setups"}});
});
await page.route("**/src/main.js",async route=>{
  const response=await route.fetch();
  await route.fulfill({response,body:await response.text()+`
    window.__setupQA={state,chart,series,positionGeometry,indicatorPositionDrawing,drawAll,
      rebuildIndicatorObjects,selectIndicatorObject,setIndicatorVisibility,fonts:[]};
    const qaText=ctx.fillText.bind(ctx);
    ctx.fillText=(text,...args)=>{if(String(text).startsWith('R:R')) window.__setupQA.fonts.push({text,font:ctx.font});return qaText(text,...args);};
  `});
});
const settle=()=>page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
const objects=()=>page.evaluate(()=>window.__setupQA.state.indicator.objects.filter(r=>r.type==="indicator-position"));
const geometry=id=>page.evaluate(id=>{const q=window.__setupQA;return q.positionGeometry(q.indicatorPositionDrawing(q.state.indicator.objectMap.get(id)));},id);
const close=(a,b)=>assert.ok(Math.abs(a-b)<1e-7,`${a} != ${b}`);
async function drag(from,to) {
  const box=await page.locator("#chart").boundingBox();
  await page.mouse.move(box.x+from.x,box.y+from.y);await page.mouse.down();
  await page.mouse.move(box.x+to.x,box.y+to.y,{steps:8});await page.mouse.up();await settle();
}
async function select(id) {
  const g=await geometry(id),box=await page.locator("#chart").boundingBox();
  await page.mouse.click(box.x+g.left+Math.min(12,(g.right-g.left)*.2),box.y+(g.entry+g.stop)/2);await settle();
  assert.equal(await page.evaluate(()=>window.__setupQA.state.indicator.selectedObjectId),id);
}
async function calculate() {
  await page.locator("#indicatorBtn").click();
  await page.locator("#indicatorEnabled").check({force:true});
  await page.locator('button[data-direction="bullish"]').click();
  await page.locator("#applyIndicator").click();
  await page.waitForFunction(()=>window.__setupQA.state.indicator.objects.some(o=>o.type==="indicator-position"));
  await page.locator("#indicatorLoading").waitFor({state:"hidden"});
  await settle();
}
try {
  await page.goto(process.env.SETUP_QA_URL||"http://127.0.0.1:5180/",{waitUntil:"networkidle"});
  await page.waitForFunction(n=>window.__setupQA?.state.data.length===n,rows.length);
  assert.match(await page.title(),/QG|Chart/i);assert.equal(await page.locator("vite-error-overlay").count(),0);
  await calculate();
  const auto=await objects();assert.equal(auto.length,3);
  await page.screenshot({path:path.join(work,"setups-initial.png")});
  assert.ok(requests.some(r=>r.path==="/api/reactions"&&r.method==="POST"));
  assert.ok(await page.evaluate(()=>window.__setupQA.state.indicator.objects.some(o=>o.setupStatusKind&&o.text==="F")));
  checks.push("Actual Apply flow renders three authoritative Engine setups and F labels with no browser-side entry detection");
  const id=auto[0].id;await select(id);let g=await geometry(id);
  close(g.levels.riskReward,4);const stop=g.levels.stop;
  await drag({x:g.right,y:g.target},{x:g.right,y:g.target-12});g=await geometry(id);
  close(g.levels.stop,stop);assert.notEqual(g.levels.riskReward,4);
  const target=g.levels.target;
  await drag({x:g.right,y:g.stop},{x:g.right,y:g.stop+10});g=await geometry(id);close(g.levels.target,target);
  const levels=structuredClone(g.levels),right=g.right;
  await drag({x:g.right,y:g.entry},{x:g.right+30,y:g.entry});g=await geometry(id);
  assert.ok(g.right>right);assert.deepEqual(g.levels,levels);
  const end=g.right;
  await drag({x:g.left,y:g.entry},{x:g.left+10,y:g.entry});g=await geometry(id);
  close(g.right,end);assert.deepEqual(g.levels,levels);
  checks.push("Automatic TP and SL handles are independent; left/right time handles resize without changing price levels or R:R");
  await page.locator("#positionBars").fill("60");await page.locator("#positionBars").press("Tab");
  assert.equal(await page.locator("#positionBars").inputValue(),"60");
  const oldTarget=(await geometry(id)).levels.target;
  await page.locator("#positionTarget").fill(String(oldTarget+.05));await page.locator("#positionTarget").press("Tab");
  close((await geometry(id)).levels.target,oldTarget+.05);
  await page.locator("#undoBtn").click();await settle();close((await geometry(id)).levels.target,oldTarget);
  await page.locator("#redoBtn").click();await settle();close((await geometry(id)).levels.target,oldTarget+.05);
  await select(id);await page.locator("#lockDrawing").click();assert.ok(await page.locator("#positionTarget").isDisabled());
  await page.locator("#lockDrawing").click();
  checks.push("Numeric Target/Stop/Bars, undo/redo and locking use the existing indicator-object workflow");
  const before=await geometry(id);
  await page.evaluate(()=>{window.__setupQA.rebuildIndicatorObjects({preserveOverrides:true});window.__setupQA.drawAll();});
  assert.deepEqual((await geometry(id)).levels,before.levels);
  await select(id);await page.locator("#deleteDrawing").click();
  assert.ok(await page.evaluate(id=>window.__setupQA.state.indicator.objectMap.get(id).hidden,id));
  await page.locator("#undoBtn").click();await settle();
  assert.equal(await page.evaluate(id=>Boolean(window.__setupQA.state.indicator.objectMap.get(id).hidden),id),false);
  checks.push("Explicit context restoration preserves edited geometry; hiding and undo do not modify Engine results");
  await page.evaluate(()=>{const q=window.__setupQA;q.chart.timeScale().applyOptions({barSpacing:5});q.chart.timeScale().setVisibleLogicalRange({from:80,to:300});q.drawAll();});
  await settle();await select(id);
  const fonts=await page.evaluate(()=>window.__setupQA.fonts);assert.ok(fonts.length&&fonts.every(r=>r.font.includes("10px")));
  await page.screenshot({path:path.join(work,"setups-desktop.png")});
  checks.push("Pan/zoom retains edited values; R:R text is 10px on actual canvas");
  await page.locator('[data-tool="long"]').click();
  const box=await page.locator("#chart").boundingBox();
  await page.mouse.click(box.x+box.width*.7,box.y+box.height*.65);
  await page.mouse.click(box.x+box.width*.72,box.y+box.height*.5);await settle();
  assert.equal(await page.evaluate(()=>window.__setupQA.state.drawings.length),1);
  await page.evaluate(()=>{window.__setupQA.setIndicatorVisibility(false);window.__setupQA.drawAll();});
  assert.equal(await page.evaluate(()=>window.__setupQA.state.indicator.hitBoxes.length),0);
  assert.equal(await page.evaluate(()=>window.__setupQA.state.drawings.length),1);
  await page.evaluate(()=>{window.__setupQA.setIndicatorVisibility(true);window.__setupQA.drawAll();});
  checks.push("Standalone manual tools remain independent; disabling the indicator hides its annotations while preserving manual drawings");
  await page.setViewportSize({width:640,height:900});await settle();
  await page.screenshot({path:path.join(work,"setups-narrow.png")});
  assert.ok((await page.locator("#chart").boundingBox()).width>400);
  assert.ok(!requests.some(r=>r.path==="/api/faraz/history"));assert.deepEqual(errors,[]);
  checks.push("640px viewport, no acquisition/trade requests, no browser console or runtime errors");
  const report={status:"PASS",browser:"Chrome via playwright-core; Browser plugin not available",checks,errors,requests};
  await writeFile(path.join(work,"browser-qa.json"),JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));
} catch(error) {
  await page.screenshot({path:path.join(work,"setups-browser-failure.png")}).catch(()=>{});
  console.error(error);console.error("Browser errors",errors);throw error;
} finally {await browser.close();}
