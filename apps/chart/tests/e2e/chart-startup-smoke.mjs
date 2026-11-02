// Runtime browser smoke for the Chart entry point after non-Engine refactors.
// Uses the disposable CI workspace, never real market data or credentials.
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { spawn } from "node:child_process";
import { fileURLToPath } from "node:url";
import { setTimeout as sleep } from "node:timers/promises";
import { chromium } from "playwright-core";
import { createRawResourceStore } from "../../server/raw-resource-store.js";

const chartRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
// All browser fixtures are generated under a unique, chart-owned state sandbox.
// Production RAW and workspace-local credentials are never read or modified.
const stateParent = path.join(chartRoot, "state");
fs.mkdirSync(stateParent, { recursive: true });
const stateRoot = fs.mkdtempSync(path.join(stateParent, "refactor-phase4-smoke-"));
const candles = Array.from({ length: 900 }, (_, index) => {
  const open = 100 + index / 100;
  return { time: 1700000000 + index * 5, open, high: open + 1, low: open - 1, close: open + 0.2 };
});
const fixture = createRawResourceStore({ rootDir: path.join(stateRoot, "data", "raw") }).write({
  broker: "TEST", symbol: "PHASE4", timeframe: "5S", candles,
});
const drawings = Array.from({ length: 6 }, (_, index) => ({
  id: `drawing-${index}`,
  type: index % 2 ? "rect" : "line",
  a: { time: candles[100 + index * 3].time, price: 101 + index },
  b: { time: candles[130 + index * 3].time, price: 103 + index },
  style: { stroke: "#2962ff", fill: "#2962ff", width: 0.5, style: "solid", opacity: 0.1 },
  locked: false, hidden: false,
}));
for (const type of ["brush", "path"]) {
  const points = Array.from({ length: 100 }, (_, i) => ({
    time: candles[200 + i].time, price: 102 + Math.sin(i / 9) * 0.4,
  }));
  drawings.push({
    id: `drawing-${type}`, type,
    a: points[0], b: points.at(-1), points,
    style: { stroke: "#2962ff", fill: "#2962ff", width: 0.5, style: "solid", opacity: 0.1 },
    locked: false, hidden: false,
  });
}
const port = 5173;
const url = `http://127.0.0.1:${port}`;
const chrome = [
  process.env.CHROME_BIN,
  "/usr/bin/google-chrome",
  "/usr/bin/google-chrome-stable",
  "/usr/bin/chromium",
  "/usr/bin/chromium-browser",
  process.env.ProgramFiles && path.join(process.env.ProgramFiles, "Google", "Chrome", "Application", "chrome.exe"),
  process.env["ProgramFiles(x86)"] && path.join(process.env["ProgramFiles(x86)"], "Google", "Chrome", "Application", "chrome.exe"),
  process.env.LOCALAPPDATA && path.join(process.env.LOCALAPPDATA, "Google", "Chrome", "Application", "chrome.exe"),
].find((candidate) => candidate && fs.existsSync(candidate));

assert.ok(chrome, "This CI smoke requires the runner's installed Chromium/Google Chrome binary.");

const server = spawn(process.execPath, [
  path.join(chartRoot, "node_modules", "vite", "bin", "vite.js"),
  "--configLoader", "native", "--host", "127.0.0.1", "--port", String(port), "--strictPort",
], { cwd: chartRoot, env: { ...process.env, TRADINGBOT_VITE_POLLING: "", TRADINGBOT_LOCAL_STATE_ROOT: stateRoot }, stdio: ["ignore", "pipe", "pipe"] });
let output = "";
server.stdout.on("data", (chunk) => { output += String(chunk); });
server.stderr.on("data", (chunk) => { output += String(chunk); });
let browser;

async function waitForServer() {
  const deadline = Date.now() + 20_000;
  while (Date.now() < deadline) {
    if (server.exitCode !== null) throw new Error(`Vite exited before startup: ${output}`);
    try {
      const response = await fetch(url, { signal: AbortSignal.timeout(1000) });
      if (response.ok) return;
    } catch {}
    await sleep(100);
  }
  throw new Error(`Vite startup timed out: ${output}`);
}

try {
  await waitForServer();
  const stored = await fetch(`${url}/api/drawings`, {
    method: "PUT",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ id: fixture.id, chartId: fixture.chartId, drawings }),
  });
  assert.equal(stored.status, 200, "Synthetic chart drawings must persist before browser load");
  browser = await chromium.launch({ executablePath: chrome, headless: true, args: ["--no-sandbox"] });
  const page = await browser.newPage();
  const pageErrors = [];
  page.on("pageerror", (error) => pageErrors.push(error.message));
  await page.goto(url, { waitUntil: "domcontentloaded", timeout: 20_000 });
  await page.bringToFront();
  await page.waitForFunction(() => /^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/.test(
    document.querySelector("#clock")?.textContent || "",
  ), { timeout: 15_000 });
  const initial = await page.locator("#clock").textContent();
  assert.match(initial, /^\d{4}-\d{2}-\d{2}/);
  await page.evaluate(() => {
    Object.defineProperty(document, "visibilityState", { configurable: true, value: "hidden" });
    document.dispatchEvent(new Event("visibilitychange"));
  });
  const hiddenValue = await page.locator("#clock").textContent();
  await sleep(1400);
  assert.equal(await page.locator("#clock").textContent(), hiddenValue, "Hidden clock should not re-render every second");
  await page.evaluate(() => {
    Object.defineProperty(document, "visibilityState", { configurable: true, value: "visible" });
    document.dispatchEvent(new Event("visibilitychange"));
  });
  const afterResume = await page.locator("#clock").textContent();
  assert.notEqual(afterResume, hiddenValue, "Visible clock must refresh immediately on return");

  // Exercise real Vite RAW inventory, chart viewport and Object Tree presentation.
  await page.waitForFunction(() => window.__QG_PERF__?.chart?.sourceCandles === 900, { timeout: 15_000 });
  await page.locator("#objectTreeBtn").click();
  await page.locator("#objectList [data-object]").first().waitFor({ state: "attached" });
  const objectIds = await page.locator("#objectList [data-object]").evaluateAll((elements) => elements.map((row) => row.dataset.object));
  assert.deepEqual(objectIds, drawings.map((item) => item.id), "Persisted drawing order must remain unchanged");
  await page.locator("#objectSearch").fill("line");
  const filteredIds = await page.locator("#objectList [data-object]").evaluateAll((elements) => elements.map((row) => row.dataset.object));
  assert.deepEqual(filteredIds, ["drawing-0", "drawing-2", "drawing-4"], "Search must preserve folder row order");
  await page.locator("#objectSearch").fill("Brush");
  assert.deepEqual(await page.locator("#objectList [data-object]").evaluateAll((elements) => elements.map((row) => row.dataset.object)), ["drawing-brush"]);
  await page.locator("#objectSearch").fill("Path");
  assert.deepEqual(await page.locator("#objectList [data-object]").evaluateAll((elements) => elements.map((row) => row.dataset.object)), ["drawing-path"]);
  await page.locator("#objectSearch").fill("");
  await page.locator("#closeObjectTree").click();
  // Real pointer and resize events must remain safe after handler extraction.
  const chartBox = await page.locator(".chart-shell").boundingBox();
  assert.ok(chartBox, "Chart shell must exist");
  await page.mouse.move(chartBox.x + chartBox.width / 2, chartBox.y + chartBox.height / 2);
  await page.mouse.down();
  await page.mouse.move(chartBox.x + chartBox.width / 2 + 12, chartBox.y + chartBox.height / 2);
  await page.mouse.up();
  await page.evaluate(() => window.dispatchEvent(new Event("resize")));
  await sleep(300);
  assert.deepEqual(pageErrors, [], "Loaded RAW chart and Drawing Tree interactions should produce no uncaught errors");
  console.log("PASS Chart browser initialization and visibility-aware UI clock.");
} finally {
  await browser?.close();
  if (server.exitCode === null && !server.killed) server.kill();
  // Do not let a stuck child keep CI alive; the process is owned by this smoke.
  await Promise.race([
    new Promise((resolve) => server.once("exit", resolve)),
    sleep(3_000),
  ]);
  fs.rmSync(stateRoot, { recursive: true, force: true });
}
