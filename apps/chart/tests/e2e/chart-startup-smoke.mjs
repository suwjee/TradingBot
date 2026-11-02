// Runtime browser smoke for the Chart entry point after non-Engine refactors.
// Uses the disposable CI workspace, never real market data or credentials.
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { spawn, execFileSync } from "node:child_process";
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
const profileMemory = process.argv.includes("--profile-memory");
const engineOverlay = process.argv.includes("--engine-overlay");
const candleCount = engineOverlay ? 6_000 : profileMemory ? 12_000 : 900;
// The Engine benchmark generator owns synthetic input construction. Its output
// is passed unaltered to the current production bridge via /api/reactions.
const candles = engineOverlay
  ? (() => {
      const repoRoot = path.resolve(chartRoot, "../..");
      execFileSync("python", [
        path.join(repoRoot, "engine", "tests", "benchmarks", "generate_fixture.py"),
        stateRoot, String(candleCount),
      ], { cwd: repoRoot, encoding: "utf8" });
      return JSON.parse(fs.readFileSync(path.join(stateRoot, `synthetic-${candleCount}.json`), "utf8"));
    })()
  : Array.from({ length: candleCount }, (_, index) => {
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
  await page.waitForFunction((expected) => window.__QG_PERF__?.chart?.sourceCandles === expected, candleCount, { timeout: 30_000 });
  if (engineOverlay) {
    const runs = [];
    // This invokes the existing UI Apply action and real, immutable Engine
    // through Vite's production API. No handcrafted trading results are used.
    for (const direction of ["bullish", "bearish"]) {
      await page.locator("#indicatorBtn").click();
      await page.locator(`[data-direction="${direction}"]`).click();
      await page.locator("#indicatorEnabled").check();
      await page.evaluate(() => { window.__phase7LastIndicator = window.__QG_PERF__?.indicator || null; });
      const responsePromise = page.waitForResponse(
        (response) => response.url().endsWith("/api/reactions") && response.request().method() === "POST",
        { timeout: 180_000 },
      );
      await page.locator("#applyIndicator").click();
      const response = await responsePromise;
      const result = await response.json();
      assert.equal(response.status(), 200, JSON.stringify(result).slice(0, 500));
      assert.ok(result.directions && typeof result.directions === "object");
      await page.waitForFunction(() =>
        window.__QG_PERF__?.indicator && window.__QG_PERF__.indicator !== window.__phase7LastIndicator,
        null, { timeout: 60_000 });
      const measurement = await page.evaluate(() => window.__QG_PERF__.indicator);
      const counts = Object.fromEntries(Object.entries(result.directions).map(([side, group]) => [
        side, Object.fromEntries(["reactions", "blueLines", "aZones", "sZones", "eZones", "stopAlls", "orderAudit"].map(
          (field) => [field, Array.isArray(group[field]) ? group[field].length : 0],
        )),
      ]));
      assert.ok(Number.isFinite(measurement.timing.canvasRenderMs));
      assert.ok(Number.isFinite(measurement.timing.objectPreparationMs));
      // Force real overlay redraws on a series of viewport gestures.
      const frameTimes = await page.evaluate(async () => {
        const canvas = document.querySelector("#draw");
        const context = canvas.getContext("2d");
        const previous = context.clearRect;
        let count = 0;
        const timings = [];
        context.clearRect = function(...args) {
          const now = performance.now();
          if (count > 0) timings.push(now - this.__lastOverlayDrawAt);
          this.__lastOverlayDrawAt = now;
          count++;
          return previous.apply(this, args);
        };
        try {
          for (let index = 0; index < 16; index++) {
            const shell = document.querySelector(".chart-shell");
            shell.dispatchEvent(new PointerEvent("pointermove", { bubbles: true, buttons: 1 }));
            await new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve)));
          }
          return { redrawCount: count, intervalsMs: timings };
        } finally {
          context.clearRect = previous;
        }
      });
      runs.push({
        direction, engine: result.engine, pipelineVersion: result.pipelineVersion,
        countByEngineDirection: counts,
        serverCache: response.headers()["x-qg-cache"],
        overlayDrawMs: measurement.timing.canvasRenderMs,
        objectPreparationMs: measurement.timing.objectPreparationMs,
        redrawCount: frameTimes.redrawCount,
        observedDrawIntervalsMs: frameTimes.intervalsMs,
      });
    }
    assert.deepEqual(pageErrors, [], "Genuine Engine-fed overlay render must produce no uncaught JavaScript errors");
    console.log(JSON.stringify({
      type: "chart-engine-output-overlay-profile", candleCount,
      source: "Current read-only production Engine through /api/reactions on Engine-benchmark synthetic candles",
      results: runs,
      caveat: "This validates actual Engine-produced outputs with synthetic prices, not real-market RAW regression or full canvas paint latency.",
    }, null, 2));
  }
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
  // Repeated panel lifecycles must rebuild a bounded, current DOM tree, not
  // append duplicate rows or accumulate obsolete drawing references.
  const repeatedTreeCounts = await page.evaluate(() => {
    const opener = document.querySelector("#objectTreeBtn");
    const closer = document.querySelector("#closeObjectTree");
    const list = document.querySelector("#objectList");
    const counts = [];
    for (let cycle = 0; cycle < 30; cycle++) {
      opener.click();
      counts.push(list.querySelectorAll("[data-object]").length);
      closer.click();
    }
    return counts;
  });
  assert.deepEqual(repeatedTreeCounts, Array(30).fill(drawings.length));
  // Real pointer and resize events must remain safe after handler extraction.
  const chartBox = await page.locator(".chart-shell").boundingBox();
  assert.ok(chartBox, "Chart shell must exist");
  await page.mouse.move(chartBox.x + chartBox.width / 2, chartBox.y + chartBox.height / 2);
  await page.mouse.down();
  await page.mouse.move(chartBox.x + chartBox.width / 2 + 12, chartBox.y + chartBox.height / 2);
  await page.mouse.up();
  await page.evaluate(() => window.dispatchEvent(new Event("resize")));
  await sleep(300);
  if (profileMemory) {
    // CDP measures retained JS heap and DOM/event listener counts after GC,
    // not GPU memory or system RSS. Report all absolute values rather than
    // asserting a universal MB cap across differently provisioned CI runners.
    const cdp = await page.context().newCDPSession(page);
    await cdp.send("Performance.enable");
    async function snapshot() {
      await cdp.send("HeapProfiler.collectGarbage");
      const { metrics } = await cdp.send("Performance.getMetrics");
      const names = ["JSHeapUsedSize", "Nodes", "JSEventListeners"];
      return Object.fromEntries(names.map((name) => [name, metrics.find((item) => item.name === name)?.value ?? null]));
    }
    const previous = await snapshot();
    const cycles = 100;
    const stress = await page.evaluate((count) => {
      const opener = document.querySelector("#objectTreeBtn");
      const closer = document.querySelector("#closeObjectTree");
      const input = document.querySelector("#objectSearch");
      const list = document.querySelector("#objectList");
      const counts = [];
      for (let i = 0; i < count; i++) {
        opener.click();
        input.value = i % 2 ? "brush" : "";
        input.dispatchEvent(new Event("input", { bubbles: true }));
        counts.push(list.querySelectorAll("[data-object]").length);
        closer.click();
      }
      return counts;
    }, cycles);
    assert.deepEqual(stress, Array.from({ length: cycles }, (_, index) => index % 2 ? 1 : drawings.length));
    const current = await snapshot();
    assert.ok(current.Nodes != null && current.JSHeapUsedSize != null);
    assert.ok(current.Nodes <= previous.Nodes + 1000, "Repeated panel ownership must not retain unbounded DOM nodes");
    assert.ok(current.JSEventListeners == null || previous.JSEventListeners == null
      || current.JSEventListeners <= previous.JSEventListeners + 100, "Panel event listeners must not accumulate per cycle");
    console.log(JSON.stringify({
      type: "chart-browser-retained-heap",
      candleCount, drawingCount: drawings.length, cycles, before: previous, after: current,
      jsHeapDeltaBytes: current.JSHeapUsedSize - previous.JSHeapUsedSize,
      caveat: "One CI browser process, forced GC, no workload-wide leak conclusion or OS/GPU RSS measurement.",
    }, null, 2));
    await cdp.detach();
  }
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
