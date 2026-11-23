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
    await Promise.all([waitForSave(), page.mouse.click(x, y)]);
    const [original] = await readDrawings();
    assert.equal(original.type, "hline");

    await page.keyboard.down("Control");
    await page.mouse.move(x, y);
    await page.mouse.down();
    await page.mouse.move(x2, y2, { steps: 5 });
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
    assert.ok(await page.locator("#toast").isHidden());
  } finally {
    await browser?.close();
    await server?.close();
    if (previous === undefined) delete process.env.TRADINGBOT_LOCAL_STATE_ROOT;
    else process.env.TRADINGBOT_LOCAL_STATE_ROOT = previous;
    assert.equal(path.dirname(stateRoot), tempRoot);
    await fs.rm(stateRoot, { recursive: true, force: true });
  }
});
