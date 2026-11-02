// Runtime browser smoke for the Chart entry point after non-Engine refactors.
// Uses the disposable CI workspace, never real market data or credentials.
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { spawn } from "node:child_process";
import { fileURLToPath } from "node:url";
import { setTimeout as sleep } from "node:timers/promises";
import { chromium } from "playwright-core";

const chartRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
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
], { cwd: chartRoot, env: { ...process.env, TRADINGBOT_VITE_POLLING: "" }, stdio: ["ignore", "pipe", "pipe"] });
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
  assert.deepEqual(pageErrors, [], "Chart startup should have no uncaught page errors");
  console.log("PASS Chart browser initialization and visibility-aware UI clock.");
} finally {
  await browser?.close();
  if (server.exitCode === null && !server.killed) server.kill();
  // Do not let a stuck child keep CI alive; the process is owned by this smoke.
  await Promise.race([
    new Promise((resolve) => server.once("exit", resolve)),
    sleep(3_000),
  ]);
}
