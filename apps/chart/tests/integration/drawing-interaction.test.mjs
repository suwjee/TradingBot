import assert from "node:assert/strict";
import { existsSync } from "node:fs";
import fs from "node:fs/promises";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright-core";
import { createServer } from "vite";
import { createRawResourceStore } from "../../server/raw-resource-store.js";

const chart = fileURLToPath(new URL("../../", import.meta.url));
const browserPaths = [
  process.env.TRADINGBOT_TEST_CHROMIUM,
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
];
const executablePath = browserPaths.find(candidate => candidate && existsSync(candidate));

test("Ctrl-drag copies an unlocked drawing on drop with one undo step", {
  skip: !executablePath && "Chromium or Edge is required for browser drawing tests",
  timeout: 45_000,
}, async () => {
  const tempRoot = path.join(chart, "state", "tmp");
  await fs.mkdir(tempRoot, { recursive: true });
  const stateRoot = await fs.mkdtemp(path.join(tempRoot, "drawing-interaction-"));
  const previous = process.env.TRADINGBOT_LOCAL_STATE_ROOT;
  process.env.TRADINGBOT_LOCAL_STATE_ROOT = stateRoot;
  let server, browser;
  try {
    const candles = Array.from({ length: 240 }, (_, index) => {
      const close = 100 + (index * 13 % 41);
      return { time: 1_795_000_020 + index * 5, open: close, high: close + 1, low: close - 1, close };
    });
    const store = createRawResourceStore({ rootDir: path.join(stateRoot, "data", "raw") });
    const raw = store.write({ broker: "TEST", symbol: "DRAWINGS", timeframe: "5S", candles });
    server = await createServer({ root: chart, configFile: path.join(chart, "vite.config.js"), configLoader: "native",
      // Other browser fixtures can optimize the same dependencies in parallel.
      cacheDir: path.join(stateRoot, "vite-cache"),
      server: { port: 0, host: "127.0.0.1", ws: false } });
    await server.listen();
    const origin = `http://127.0.0.1:${server.httpServer.address().port}`;
    browser = await chromium.launch({ executablePath, headless: true });
    const page = await browser.newPage({ viewport: { width: 1280, height: 820 } });
    const startupErrors = [];
    page.on("pageerror", error => startupErrors.push(error.message));
    page.on("response", response => {
      const url = new URL(response.url());
      if (url.origin === origin && response.status() >= 500) startupErrors.push(`${response.status()} ${url.pathname}`);
    });
    const waitForSave = () => page.waitForResponse(response =>
      new URL(response.url()).pathname === "/api/drawings" && response.request().method() === "PUT");
    const readDrawings = async () => {
      const params = new URLSearchParams({ id: raw.id, chartId: raw.chartId });
      return (await fetch(`${origin}/api/drawings?${params}`)).json();
    };
    try {
      await page.goto(`${origin}/?chartId=${raw.chartId}&tf=5`, { waitUntil: "domcontentloaded" });
      await page.waitForFunction(chartId =>
        document.querySelector("#chartIdFooter")?.title.toLowerCase() === chartId
        && document.querySelector("#loading")?.classList.contains("hidden"),
      raw.chartId.toLowerCase(), { timeout: 15_000 });
    } catch (error) {
      throw new Error(`The drawing fixture did not load its RAW chart.\n${startupErrors.join("\n")}`, { cause: error });
    }
    const bounds = await page.locator("#chart").boundingBox({ timeout: 5_000 });
    assert.ok(bounds, "The loaded fixture must have a visible drawing surface.");
    const x = bounds.x + bounds.width * 0.42, y = bounds.y + bounds.height * 0.44;
    const x2 = x + 90, y2 = y + 100;
    await page.locator('[data-drawing-tool="hline"]').click();
    await page.mouse.move(x, y);
    await page.locator(".drawing-crosshair").waitFor({ state: "visible" });
    await Promise.all([waitForSave(), page.mouse.click(x, y)]);
    const [original] = await readDrawings();
    assert.equal(original.type, "hline");

    await page.keyboard.down("Control");
    await page.mouse.move(x, y);
    await page.mouse.down();
    await page.mouse.move(x2, y2, { steps: 5 });
    await page.locator(".drawing-crosshair").waitFor({ state: "visible" });
    await Promise.all([waitForSave(), page.mouse.up()]);
    await page.keyboard.up("Control");
    const duplicated = await readDrawings();
    assert.equal(duplicated.length, 2);
    assert.deepEqual(duplicated[0], original);
    assert.notEqual(duplicated[1].id, original.id);
    assert.notEqual(duplicated[1].a.price, original.a.price);
    assert.deepEqual(duplicated[1].style, original.style);

    await Promise.all([waitForSave(), page.locator("#undoBtn").click()]);
    assert.deepEqual(await readDrawings(), [original]);
    await Promise.all([waitForSave(), page.locator("#redoBtn").click()]);
    assert.deepEqual(await readDrawings(), duplicated);

    await page.keyboard.down("Control");
    await page.mouse.move(x, y);
    await page.mouse.down();
    await page.mouse.move(x2, y2 + 45, { steps: 4 });
    await page.keyboard.press("Escape");
    await page.mouse.up();
    await page.keyboard.up("Control");
    assert.deepEqual(await readDrawings(), duplicated);

    await page.keyboard.down("Control");
    await page.mouse.click(x, y);
    await page.keyboard.up("Control");
    assert.deepEqual(await readDrawings(), duplicated);

    await Promise.all([waitForSave(), page.locator("#lockDrawing").click()]);
    const locked = await readDrawings();
    assert.deepEqual(locked, [{ ...original, locked: true }, duplicated[1]]);
    await page.keyboard.down("Control");
    await page.mouse.move(x, y);
    await page.mouse.down();
    await page.mouse.move(x2, y2 - 45, { steps: 4 });
    await page.mouse.up();
    await page.keyboard.up("Control");
    assert.deepEqual(await readDrawings(), locked);

    const closeToast = page.locator("#toastClose");
    if (await closeToast.isVisible()) await closeToast.click();
    const measure = page.locator('[data-drawing-tool="measure"]');
    assert.equal(await measure.locator("svg rect").count(), 1);
    await measure.click();
    await page.keyboard.press("Escape");
    assert.ok(await page.locator(".drawing-crosshair").isHidden());
    assert.ok(await page.locator("#toast").isHidden());

    const start = { x: bounds.x + bounds.width * 0.56, y: bounds.y + bounds.height * 0.30 };
    const end = { x: start.x + 102, y: start.y + 75 };
    await page.locator('[data-drawing-tool="line"]').click();
    await page.mouse.click(start.x, start.y);
    await page.keyboard.down("Shift");
    await Promise.all([waitForSave(), page.mouse.click(end.x, end.y)]);
    await page.keyboard.up("Shift");
    const line = (await readDrawings()).find(item => item.type === "line");
    assert.equal(line.a.price, line.b.price);
    await page.keyboard.down("Shift");
    await page.mouse.move(end.x, start.y);
    await page.mouse.down();
    await page.mouse.move(end.x + 38, start.y + 35, { steps: 5 });
    await Promise.all([waitForSave(), page.mouse.up()]);
    await page.keyboard.up("Shift");
    const resized = (await readDrawings()).find(item => item.id === line.id);
    assert.notEqual(resized.b.time, line.b.time);
    assert.equal(resized.a.price, resized.b.price);

    await page.evaluate(() => { void Promise.reject(new Error("Journal fixture error", { cause: new Error("Fixture cause") })); });
    await page.locator("#healthStatus").click();
    await page.locator("#errorLogList").getByText("Journal fixture error", { exact: true }).waitFor();
    await page.waitForFunction(async () => (await (await fetch("/api/error-journal")).json()).entries
      .some(entry => entry.error === "Journal fixture error" && entry.cause?.error === "Fixture cause"));
    await page.reload();
    await page.locator("#healthStatus").click();
    await page.locator("#errorLogList").getByText("Journal fixture error", { exact: true }).waitFor();
    await page.locator("#clearErrorLogs").click();
    await page.locator("#errorLogList").getByText("Journal fixture error", { exact: true }).waitFor({ state: "hidden" });
  } finally {
    await browser?.close();
    await server?.close();
    if (previous === undefined) delete process.env.TRADINGBOT_LOCAL_STATE_ROOT;
    else process.env.TRADINGBOT_LOCAL_STATE_ROOT = previous;
    assert.equal(path.dirname(stateRoot), tempRoot);
    await fs.rm(stateRoot, { recursive: true, force: true });
  }
});
test("indicator position edits survive Apply, Live, undo, visibility changes, and reload", {
  skip: !executablePath && "Chromium or Edge is required for browser drawing tests",
  timeout: 45_000,
}, async () => {
  const tempRoot = path.join(chart, "state", "tmp");
  await fs.mkdir(tempRoot, { recursive: true });
  const stateRoot = await fs.mkdtemp(path.join(tempRoot, "indicator-positions-"));
  const previous = process.env.TRADINGBOT_LOCAL_STATE_ROOT;
  process.env.TRADINGBOT_LOCAL_STATE_ROOT = stateRoot;
  let server, browser;
  try {
    const candles = Array.from({ length: 240 }, (_, index) => {
      const close = 100 + (index * 13 % 41);
      return { time: 1_795_000_020 + index * 5, open: close, high: close + 1, low: close - 1, close };
    });
    const store = createRawResourceStore({ rootDir: path.join(stateRoot, "data", "raw") });
    const raw = store.write({ broker: "TEST", symbol: "POSITIONS", timeframe: "5S", candles });
    server = await createServer({ root: chart, configFile: path.join(chart, "vite.config.js"), configLoader: "native",
      cacheDir: path.join(stateRoot, "vite-cache"),
      server: { port: 0, host: "127.0.0.1", ws: false } });
    await server.listen();
    const origin = `http://127.0.0.1:${server.httpServer.address().port}`;
    browser = await chromium.launch({ executablePath, headless: true });
    const page = await browser.newPage({ viewport: { width: 1280, height: 820 } });
    page.setDefaultTimeout(7_000);
    const pageErrors = [];
    page.on("pageerror", error => pageErrors.push(error.message));
    const position = { id: "stable:buy", type: "1.1B", side: "buy", entryTime: candles[170].time,
      entryPrice: "119", stopPrice: "115", targetPrice: "135" };
    const group = { reactions: [], positions: [position],
      liquidity: [
        { sourceTime: candles[160].time, visibleFrom: candles[175].time,
          lineEndTime: candles[235].time, price: "105" },
        { sourceTime: candles[175].time, visibleFrom: candles[185].time,
          lineEndTime: candles[230].time, price: "136", collectedTime: candles[230].time,
          repeatGroupSourceTime: candles[160].time },
      ],
      eZones: [{ number: 5, family: "red", sourceIndex: 198, sourceTime: candles[198].time, price: "130",
        parentType: "E", parentStopEventTime: candles[199].time,
        trueFalse: "F", trueFalseRepeated: true, trueFalseRepeatCount: 2, trueFalseRepeatF: true }],
      stopAlls: [{ number: 1, sourceIndex: 210, sourceTime: candles[210].time, price: "125",
        gateEventTime: candles[214].time,
        trueFalse: "T", trueFalseRepeated: true }],
      trendTransitions: [{ id: "bullish:trend:fixture", direction: "bullish", sourceTime: candles[170].time,
        level: "130", iconCandleTime: candles[219].time, iconCandleHigh: "136" }],
    };
    const payload = { timeframe: 5, actualFrom: candles[0].time, actualTo: candles.at(-1).time,
      directions: { bullish: { ...group, calculationSegments: [group] } } };
    const calculation = { calculationId: "test", chartId: raw.chartId, direction: "bullish",
      timeframe: 5, from: candles[0].time, to: candles.at(-1).time };
    await page.route("**/api/reactions/cached?*", route =>
      route.fulfill({ json: { payload, snapshot: { calculation } } }));
    let applies = 0;
    const releaseCancelledApply = Promise.withResolvers();
    const releaseApply = Promise.withResolvers();
    await page.route(url => url.pathname === "/api/reactions", async route => {
      if (route.request().postDataJSON().direction === "bearish") {
        return route.fulfill({ status: 422, json: { error: "Fixture rejected direction" } });
      }
      if (++applies === 1) {
        await releaseCancelledApply.promise;
        return route.abort();
      }
      await releaseApply.promise;
      return route.fulfill({ json: payload });
    });
    const liveRequests = [];
    let readinessChecks = 0;
    await page.route("**/api/reactions/source", route => {
      if (liveRequests.length >= 3 && ++readinessChecks === 1) return route.abort("connectionreset");
      return route.continue();
    });
    await page.route("**/api/reactions/continue", route => {
      const request = route.request().postDataJSON();
      liveRequests.push(request);
      if (liveRequests.length <= 3) return route.abort("connectionreset");
      const { tabId } = request;
      const livePosition = { ...position, entryTime: candles[171].time, entryPrice: "120",
        stopPrice: "114", targetPrice: "144" };
      const addedPosition = { ...position, id: "another", type: "1.2B", entryTime: candles[175].time };
      const advanced = { reactions: [], positions: [livePosition, addedPosition] };
      const result = { ...payload, directions: { bullish: { ...advanced, calculationSegments: [advanced] } } };
      return route.fulfill({
        headers: {
          "X-QG-Calculation-Id": "test-live",
          "X-QG-Source-Fingerprint": "test-source",
          "X-QG-Live-Proof": JSON.stringify({ chartId: raw.chartId, tabId, to: calculation.to,
            request: { ...calculation, chartTimeframe: 5 } }),
        },
        json: result,
      });
    });
    await page.addInitScript(() => {
      const EventSourceImpl = window.EventSource;
      window.EventSource = class extends EventSourceImpl {
        constructor(url, ...args) {
          super(url, ...args);
          if (String(url).startsWith("/api/reactions/progress?")) window.calculationProgress = this;
        }
      };
      const { fillText, arc, beginPath, fill, clearRect } = CanvasRenderingContext2D.prototype;
      const lastCircle = new WeakMap();
      window.positionPaint = { label: null, handles: [], marks: {}, liquidity: [] };
      CanvasRenderingContext2D.prototype.clearRect = function (...args) {
        if (this.canvas.id === "draw") window.positionPaint = { label: null, handles: [], marks: {}, liquidity: [] };
        return clearRect.apply(this, args);
      };
      CanvasRenderingContext2D.prototype.fillText = function (label, x, y, ...args) {
        if (this.canvas.id === "draw") {
          if (label === "1.1B") window.positionPaint.label = { x, y };
          if (label === "$$$") window.positionPaint.liquidity.push({
            color: this.fillStyle, font: this.font, width: this.lineWidth, x, y,
          });
          if (["F", "T", "**", "X", "N/A", "edited"].includes(label)) {
            window.positionPaint.marks[label] = { x, y, color: this.fillStyle };
          }
        }
        return fillText.call(this, label, x, y, ...args);
      };
      CanvasRenderingContext2D.prototype.arc = function (x, y, radius, ...args) {
        if (this.canvas.id === "draw" && radius === 5) lastCircle.set(this, { x, y });
        return arc.call(this, x, y, radius, ...args);
      };
      CanvasRenderingContext2D.prototype.beginPath = function () {
        lastCircle.delete(this);
        return beginPath.call(this);
      };
      CanvasRenderingContext2D.prototype.fill = function (...args) {
        const circle = lastCircle.get(this);
        if (circle && this.fillStyle === "#ffffff") window.positionPaint.handles.push(circle);
        return fill.apply(this, args);
      };
    });
    const key = `market-canvas:${raw.id}:indicator-overrides:v1`;
    const id = "indicator:bullish:position:stable%3Abuy";
    const row = page.locator(`[data-indicator-object="${id}"]`);
    const readOverride = () => page.evaluate(([key, id]) => JSON.parse(localStorage.getItem(key) || "{}")[id] ?? null, [key, id]);
    const waitForLabel = async (shown) => {
      await page.waitForFunction(expected => Boolean(window.positionPaint.label) === expected, shown, { timeout: 6_000 });
    };
    const openIndicator = () => page.locator("#indicatorBtn").click();
    const closeIndicator = () => page.locator("#closeIndicator").click();
    const openPositions = async () => {
      await page.locator('[data-indicator-tab="inputs"]').click();
      const header = page.locator('[data-style-group="positions"] .style-group-header');
      if (await header.getAttribute("aria-expanded") !== "true") await header.click();
    };
    await page.goto(`${origin}/?chartId=${raw.chartId}&tf=5`, { waitUntil: "domcontentloaded" });
    await waitForLabel(true);
    assert.equal(await page.locator('#cacheStatusFooter').getAttribute('data-state'), 'cache');
    const waitForLiquidity = count => page.waitForFunction(expected =>
      window.positionPaint.liquidity.length === expected
      && window.positionPaint.liquidity.every(({ color, font, width }) =>
        color === "#b8b8b8" && font.includes("10px") && width === 0.5), count);
    await waitForLiquidity(2);
    await openIndicator();
    await page.locator('[data-indicator-tab="inputs"]').click();
    const collectedLiquidity = page.locator("label:has(#liquidityCollectedVisible)");
    await collectedLiquidity.click();
    await waitForLiquidity(1);
    await collectedLiquidity.click();
    await waitForLiquidity(2);
    assert.equal(applies, 0);
    await closeIndicator();
    await page.locator("#objectTreeBtn").click();
    await row.waitFor();
    for (const objectId of ["indicator:bullish:e:0:verdict", "indicator:bullish:e:0:stars",
      "indicator:bullish:e:0:x", "indicator:bullish:stopall:0:na", "indicator:market:bullish:trend:fixture:line",
      "indicator:market:bullish:trend:fixture:time", `indicator:bullish:liquidity:${candles[160].time}`]) {
      await page.locator(`[data-indicator-object="${objectId}"]`).waitFor();
    }
    assert.equal(await page.locator('[data-indicator-object="indicator:market:bullish:trend:fixture:icon"]').count(), 0);
    assert.equal(await row.locator(".object-name strong").textContent(), "1.1B");
    await row.locator(".object-name").click();
    assert.equal(await page.locator("#positionTarget").inputValue(), "135");
    assert.equal(await page.locator("#positionStop").inputValue(), "115");
    assert.equal(await page.locator("#positionBars").inputValue(), "50");
    await page.locator("#lockDrawing").click();
    await page.locator("#positionTarget").fill("133");
    await page.locator("#positionTarget").press("Tab");
    assert.equal((await readOverride()).positionEdit.target, 133);
    await page.locator("#positionStop").fill("114");
    await page.locator("#positionStop").press("Tab");
    assert.equal((await readOverride()).positionEdit.stop, 114);
    await page.locator("#objectTreeBtn").click();

    const bounds = await page.locator("#chart").boundingBox();
    const drag = async ({ x, y }, dx, dy) => {
      await page.mouse.move(bounds.x + x, bounds.y + y);
      await page.mouse.down();
      await page.mouse.move(bounds.x + x + dx, bounds.y + y + dy, { steps: 5 });
      await page.mouse.up();
    };
    const paint = () => page.evaluate(() => window.positionPaint);
    const marks = (await paint()).marks;
    assert.ok(marks.F.y < marks["**"].y && marks["**"].y < marks.X.y);
    assert.ok(marks.T.y < marks["N/A"].y);
    assert.equal(marks.X.color, "#808080");
    assert.equal(marks["N/A"].color, "#808080");
    await page.context().grantPermissions(["clipboard-read", "clipboard-write"], { origin });
    await page.mouse.dblclick(bounds.x + marks.F.x, bounds.y + marks.F.y + 4);
    await page.waitForFunction(async () => (await navigator.clipboard.readText()).endsWith("|  bullish | E5 Red (F)"));
    assert.ok(await page.locator("#indicatorModal").isHidden());
    const liquidity = (await paint()).liquidity[0];
    await page.mouse.click(bounds.x + liquidity.x, bounds.y + liquidity.y);
    await page.locator("#lockDrawing").click();
    await page.keyboard.down("Shift");
    await drag(liquidity, 35, 12);
    await page.keyboard.up("Shift");
    const liquidityId = `indicator:bullish:liquidity:${candles[160].time}`;
    const liquidityEdit = await page.evaluate(([storeKey, objectId]) => JSON.parse(localStorage.getItem(storeKey))[objectId].liquidityEdit,
      [key, liquidityId]);
    assert.equal(liquidityEdit.a.price, liquidityEdit.b.price);
    assert.notEqual(liquidityEdit.a.time, candles[160].time);
    await page.locator("#deleteDrawing").click();
    await waitForLiquidity(1);
    await page.keyboard.press("Control+z");
    await waitForLiquidity(2);
    await page.mouse.click(bounds.x + marks.X.x, bounds.y + marks.X.y + 4);
    assert.equal(await page.locator("#objectText").inputValue(), "X");
    await page.locator("#lockDrawing").click();
    await page.locator("#objectText").fill("edited");
    await page.waitForFunction(() => Boolean(window.positionPaint.marks.edited));
    const edited = (await paint()).marks.edited;
    await drag({ ...edited, y: edited.y + 4 }, 32, 14);
    const movedMarker = (await paint()).marks.edited;
    assert.ok(movedMarker.x > edited.x && movedMarker.y > edited.y);
    await page.locator("#deleteDrawing").click();
    await page.waitForFunction(() => !window.positionPaint.marks.edited);
    assert.ok((await paint()).marks["**"]);
    const { label } = await paint();
    await drag({ x: label.x, y: label.y - 10 }, 24, 12);
    const moved = (await readOverride()).positionEdit;
    assert.ok(moved.time > position.entryTime, JSON.stringify({ moved, label }));
    assert.ok(moved.entry < Number(position.entryPrice));
    assert.equal(moved.bars, 50);

    const handles = (await paint()).handles;
    assert.equal(handles.length, 6);
    const rightEntry = handles.at(-1);
    await drag(rightEntry, 34, 0);
    const resized = (await readOverride()).positionEdit;
    assert.ok(resized.bars > moved.bars);
    assert.equal(resized.entry, moved.entry);
    await page.locator("#undoBtn").click();
    assert.deepEqual((await readOverride()).positionEdit, moved);
    await page.locator("#redoBtn").click();
    assert.deepEqual((await readOverride()).positionEdit, resized);

    await openIndicator();
    await openPositions();
    assert.deepEqual(await page.locator('[data-indicator-page="inputs"] .style-group-header')
      .evaluateAll(headers => headers.map(header => header.getAttribute("aria-expanded"))),
    ["true", "true", "true", "true", "true"]);
    await page.locator('[data-direction="bearish"]').click();
    await waitForLabel(true);
    assert.ok((await paint()).marks["N/A"]);
    assert.equal(applies, 0);
    await Promise.all([
      page.waitForResponse(response => new URL(response.url()).pathname === "/api/reactions" && response.status() === 422),
      page.locator("#applyIndicator").click(),
    ]);
    await page.waitForFunction(() => !document.querySelector("#applyIndicator").disabled);
    await waitForLabel(true);
    assert.ok((await paint()).marks["N/A"]);
    if (await page.locator("#toastClose").isVisible()) await page.locator("#toastClose").click();
    if (await page.locator("#indicatorModal").isHidden()) await openIndicator();
    await page.locator('[data-direction="bullish"]').click();
    for (const [control, mark] of [["foundationStarsVisible", "**"], ["foundationXVisible", "X"], ["secondaryNaVisible", "N/A"]]) {
      await page.locator(`label:has(#${control})`).click();
      await page.waitForFunction(label => !window.positionPaint.marks[label], mark);
      await page.locator(`label:has(#${control})`).click();
      if (mark !== "X") await page.waitForFunction(label => Boolean(window.positionPaint.marks[label]), mark);
    }
    const groups = page.locator("#indicator-configure-positions fieldset");
    assert.deepEqual(await groups.locator("legend").allTextContents(), ["Buy", "Sell"]);
    assert.deepEqual(await groups.locator("label > span > b").allTextContents(), [
      "1.1B", "1.2B", "2.1B", "2.2B", "3.1B", "3.2B", "3.3B",
      "1.1S", "1.2S", "2.1S", "2.2S", "3.1S", "3.2S", "3.3S",
    ]);
    const buyToggle = groups.getByRole("checkbox", { name: "Toggle 1.1B" });
    const clickBuyToggle = () => groups.locator("label").filter({ has: page.locator("#position1_1BVisible") }).click();
    await clickBuyToggle();
    await waitForLabel(false);
    await clickBuyToggle();
    await waitForLabel(true);
    const apply = page.locator("#applyIndicator");
    const isApply = request => new URL(request.url()).pathname === "/api/reactions";
    await Promise.all([page.waitForRequest(isApply), apply.click()]);
    const cancel = page.getByRole("button", { name: "Cancel calculation" });
    await cancel.click();
    await page.locator("#indicatorLoading").waitFor({ state: "hidden" });
    assert.match(await page.locator("#indicatorStatus").textContent(), /Calculation cancelled/);
    assert.equal(await apply.isEnabled(), true);
    assert.equal(await apply.evaluate(button => button === document.activeElement), true);
    await waitForLabel(true);
    assert.deepEqual((await readOverride()).positionEdit, resized);
    releaseCancelledApply.resolve();
    await apply.click();
    const steps = page.locator("#calculationSteps");
    const positionsStage = steps.locator('[data-stage="Evaluate positions - Bullish"]');
    const progress = page.locator(".calculation-track");
    await positionsStage.waitFor();
    assert.equal(await progress.getAttribute("aria-valuenow"), "0");
    assert.match(await positionsStage.innerText(), /Pending/);
    assert.ok(await steps.locator("li").count() > 25);
    const publish = event => page.evaluate(value => window.calculationProgress.dispatchEvent(
      new MessageEvent("message", { data: JSON.stringify(value) }),), event);
    await publish({ status: "started", label: "Evaluate positions - Bullish" });
    assert.match(await positionsStage.innerText(), /Running/);
    await publish({ status: "completed", label: "Evaluate positions - Bullish", durationMs: 25 });
    assert.match(await positionsStage.innerText(), /Done.*25\.00ms/s);
    const interim = Number(await progress.getAttribute("aria-valuenow"));
    assert.ok(interim > 0 && interim < 100);
    await publish({ status: "started", label: "Evaluate positions - Bullish" });
    assert.equal(Number(await progress.getAttribute("aria-valuenow")), interim, "Another pass cannot move completion backward");
    await publish({ status: "completed", label: "Evaluate positions - Bullish", durationMs: 5 });
    assert.match(await positionsStage.innerText(), /2×.*Done.*30\.00ms/s);
    await publish({ status: "completed", label: "Start Python calculation", durationMs: 30 });
    assert.match(await steps.locator('[data-stage="Evaluate positions - Bearish"]').innerText(), /Not needed/);
    releaseApply.resolve();
    await page.waitForFunction(() => document.querySelector("#indicatorModal").classList.contains("hidden"));
    assert.equal(applies, 2);
    const progressLabels = await page.locator("#calculationSteps .calculation-stage-copy b").allTextContents();
    for (const label of ["HTTP request and server", "Response parsing", "Prepare chart objects", "Canvas render"]) {
      assert.ok(progressLabels.includes(label), progressLabels.join(", "));
    }
    assert.equal(await page.locator("#calculationPercent").textContent(), "100%");
    assert.deepEqual((await readOverride()).positionEdit, resized);
    await openIndicator();
    await page.locator('[data-indicator-tab="info"]').click();
    const positionsActivity = page.locator(".info-positions");
    await positionsActivity.locator("summary").click();
    assert.match(await positionsActivity.innerText(), /1\.1B.*\n.*Entry 119.*Stop 115.*Target 135/);
    await closeIndicator();
    await page.locator("#realtimeChartBtn").click();
    const realtime = page.locator("#realtimeChartPopup");
    if (!(await realtime.locator("#realtimeChartIndicator").isEnabled())) {
      await realtime.locator("[data-enable]").click();
    }
    await realtime.locator('label[for="realtimeChartIndicator"]').click();
    await page.keyboard.press("Escape");
    await page.locator("#objectTreeBtn").click();
    await page.locator('[data-indicator-object="indicator:bullish:position:another"]').waitFor({ timeout: 18_000 });
    const { requestId: originalRequestId, ...original } = liveRequests[0];
    const { requestId: retryRequestId, ...retry } = liveRequests[3];
    assert.ok(originalRequestId && retryRequestId && originalRequestId !== retryRequestId);
    assert.deepEqual(retry, original);
    assert.ok(readinessChecks >= 2);
    assert.equal(applies, 2);
    const { entries } = await (await fetch(`${origin}/api/error-journal`)).json();
    assert.ok(!entries.some(entry => ["REALTIME_INDICATOR_CONTINUATION_DEFERRED", "REALTIME_INDICATOR_CONNECTION_UNAVAILABLE"].includes(entry.event)));
    assert.deepEqual((await readOverride()).positionEdit, resized);
    await row.locator(".object-name").click();
    await page.locator("#deleteDrawing").click();
    assert.equal((await readOverride()).hidden, true);
    await waitForLabel(false);
    await row.locator('.object-quick-action[data-action="visibility"]').click();
    await waitForLabel(true);

    await openIndicator();
    await openPositions();
    await clickBuyToggle();
    await closeIndicator();
    await waitForLabel(false);
    await page.reload();
    await openIndicator();
    await openPositions();
    assert.equal(await buyToggle.isChecked(), false);
    await clickBuyToggle();
    await waitForLabel(true);
    assert.deepEqual((await readOverride()).positionEdit, resized);
    assert.equal(position.targetPrice, "135");
    const master = page.locator('.master-switch[title="Enable indicator"]');
    await Promise.all([
      page.waitForResponse(response => new URL(response.url()).pathname === "/api/workspace-preferences"
        && response.request().method() === "PATCH" && response.request().postDataJSON().value?.enabled === false),
      master.click(),
    ]);
    await page.reload();
    await page.locator('#cacheStatusFooter[data-state="cache"]').waitFor();
    await openIndicator();
    assert.equal(await page.locator("#indicatorEnabled").isChecked(), false);
    await waitForLabel(false);
    await master.click();
    await waitForLabel(true);
    assert.deepEqual(pageErrors, []);
  } finally {
    await browser?.close();
    await server?.close();
    if (previous === undefined) delete process.env.TRADINGBOT_LOCAL_STATE_ROOT;
    else process.env.TRADINGBOT_LOCAL_STATE_ROOT = previous;
    assert.equal(path.dirname(stateRoot), tempRoot);
    await fs.rm(stateRoot, { recursive: true, force: true });
  }
});
