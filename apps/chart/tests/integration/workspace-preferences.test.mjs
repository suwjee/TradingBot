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
const executablePath = [
  process.env.TRADINGBOT_TEST_CHROMIUM,
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
].find((candidate) => candidate && existsSync(candidate));

test("filesystem preferences survive a fresh server and browser context", {
  skip: !executablePath && "Chromium or Edge is required for browser workspace tests",
  timeout: 45_000,
}, async () => {
  const tempRoot = path.join(chart, "state", "tmp");
  await fs.mkdir(tempRoot, { recursive: true });
  const stateRoot = await fs.mkdtemp(path.join(tempRoot, "workspace-preferences-"));
  const priorStateRoot = process.env.TRADINGBOT_LOCAL_STATE_ROOT;
  process.env.TRADINGBOT_LOCAL_STATE_ROOT = stateRoot;
  let server, browser;
  try {
    const rawStore = createRawResourceStore({ rootDir: path.join(stateRoot, "data", "raw") });
    const raw = (offset, createdAt) => rawStore.write({
      broker: "TEST", symbol: "USOIL", timeframe: "5S", createdAt,
      candles: Array.from({ length: 80 }, (_, index) => ({
        time: 1_795_000_020 + offset + index * 5, open: 100, high: 102, low: 98, close: 101,
      })),
    });
    const older = raw(0, "2026-11-24 12:00:00 Asia/Tehran");
    const newer = raw(400, "2026-11-26 12:00:00 Asia/Tehran");
    const gold = rawStore.write({ broker: "FOREXCOM", symbol: "XAUUSD", timeframe: "5S",
      candles: [{ time: 1_795_000_020, open: 100, high: 102, low: 98, close: 101 }] });
    const errors = [];
    let origin;

    async function startServer() {
      server = await createServer({
        root: chart, configFile: path.join(chart, "vite.config.js"), configLoader: "native",
        cacheDir: path.join(stateRoot, "vite-cache"),
        server: { port: 0, host: "127.0.0.1", ws: false },
      });
      await server.listen();
      origin = `http://127.0.0.1:${server.httpServer.address().port}`;
    }
    async function openChart(item = newer) {
      const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
      page.on("pageerror", (error) => errors.push(error.message));
      await page.goto(`${origin}/chart?chartId=${item.chartId}&tf=5`, { waitUntil: "domcontentloaded" });
      await page.waitForFunction((id) => document.querySelector("#chartIdFooter")?.title.toLowerCase() === id
        && document.querySelector("#loading")?.classList.contains("hidden"), item.chartId);
      return page;
    }
    function saved(page, key) {
      return page.waitForResponse((response) => new URL(response.url()).pathname === "/api/workspace-preferences"
        && response.request().method() === "PATCH" && response.request().postDataJSON().key === key)
        .then((response) => assert.equal(response.status(), 200));
    }
    const bookmarks = (page) => page.locator("[data-bookmark-chart-id]").evaluateAll(
      (buttons) => buttons.map((button) => button.dataset.bookmarkChartId),
    );
    const drawingOrder = (page) => page.locator("[data-drawing-tool]").evaluateAll(
      (buttons) => buttons.map((button) => button.dataset.drawingTool),
    );
    async function addLine(page, offset = 0) {
      const bounds = await page.locator("#chart").boundingBox();
      assert.ok(bounds);
      await page.locator('[data-drawing-tool="hline"]').click();
      await Promise.all([
        page.waitForResponse((response) => new URL(response.url()).pathname === "/api/drawings"
          && response.request().method() === "PUT"),
        page.mouse.click(bounds.x + bounds.width / 2, bounds.y + bounds.height / 2 + offset),
      ]);
    }

    await startServer();
    for (const route of ["/api/missing-route", "/api/reactions/missing-route", "/api/faraz/auth/status/missing-route"]) {
      const response = await fetch(origin + route, { headers: { Accept: "text/html" } });
      assert.equal(response.status, 404);
      assert.deepEqual(await response.json(), { error: "API route not found." });
    }
    browser = await chromium.launch({ executablePath, headless: true });
    const page = await openChart();
    await page.locator("#symbolBtn").click();
    assert.deepEqual((await bookmarks(page)).filter(id => id !== gold.chartId), [newer.chartId, older.chartId]);
    await Promise.all([
      saved(page, `bookmark:${older.chartId}`),
      page.locator(`[data-bookmark-chart-id="${older.chartId}"]`).click(),
    ]);
    assert.deepEqual((await bookmarks(page)).filter(id => id !== gold.chartId), [older.chartId, newer.chartId]);
    await page.keyboard.press("Escape");

    await page.locator("#realtimeChartBtn").click();
    await Promise.all([
      saved(page, "realtime-default"),
      page.locator("#realtimeChartInterval").selectOption("300000"),
    ]);
    await Promise.all([
      saved(page, "realtime-default"),
      page.getByRole("button", { name: "Disable", exact: true }).click(),
    ]);
    await page.keyboard.press("Escape");

    await page.locator("#indicatorBtn").click();
    await Promise.all([saved(page, `indicator:${newer.chartId}`), page.locator('.master-switch[title="Enable indicator"]').click()]);
    await Promise.all([
      saved(page, `indicator:${newer.chartId}`),
      page.locator('[data-direction="bearish"]').click(),
    ]);
    const visibleBefore = await page.locator("#foundationTfVisible").isChecked();
    await Promise.all([
      saved(page, "indicator-default"),
      saved(page, `indicator:${newer.chartId}`),
      page.locator("#foundationTfVisible").evaluate((input) => input.click()),
    ]);
    await page.locator("#closeIndicator").click();
    const tool = page.locator('[data-drawing-tool="line"]');
    await tool.focus();
    await Promise.all([saved(page, "drawing-order"), page.keyboard.press("Alt+ArrowLeft")]);
    const order = await drawingOrder(page);
    assert.equal(order.indexOf("line"), 0);
    await addLine(page);
    await Promise.all([saved(page, "drawing-style"), page.locator("#lineWidth").selectOption("2")]);

    const journalEntry = { id: "fixture-error-0001", scope: "TEST", recordedAt: Date.now(),
      event: "DURABLE_ERROR", level: "ERROR", stack: "Fixture stack", accessToken: "redact-this-value" };
    assert.equal((await fetch(`${origin}/api/error-journal`, { method: "POST",
      headers: { "Content-Type": "application/json" }, body: JSON.stringify(journalEntry) })).status, 200);

    await page.close();
    await server.close();
    await startServer();
    const { entries } = await (await fetch(`${origin}/api/error-journal`)).json();
    assert.ok(entries.find(row => row.id === journalEntry.id && row.stack === "Fixture stack" && row.accessToken === "[redacted]"));
    const differentChart = await openChart(older);
    await differentChart.locator("#realtimeChartBtn").click();
    assert.ok(await differentChart.getByRole("button", { name: "Enable", exact: true }).isVisible());
    await differentChart.keyboard.press("Escape");
    await differentChart.locator("#indicatorBtn").click();
    assert.equal(await differentChart.locator('[data-direction="bearish"]').getAttribute("aria-pressed"), "true");
    assert.equal(await differentChart.locator("#foundationTfVisible").isChecked(), !visibleBefore);
    await differentChart.close();
    const market = await browser.newPage({ timezoneId: "UTC" });
    await market.clock.install({ time: new Date("2026-11-22T21:00:00Z") });
    await market.goto(`${origin}/chart?chartId=${gold.chartId}&tf=5`);
    await market.waitForFunction(() => document.querySelector("#clock")?.dataset.marketState === "closed");
    assert.equal(await market.locator("#clock").evaluate(node => getComputedStyle(node).borderTopColor), "rgb(220, 38, 38)");
    await market.clock.setSystemTime(new Date("2026-11-23T00:00:00Z"));
    await market.clock.runFor(1000);
    await market.waitForFunction(() => document.querySelector("#clock")?.dataset.marketState === "open");
    assert.equal(await market.locator("#clock").evaluate(node => getComputedStyle(node).borderTopColor), "rgb(22, 163, 74)");
    await market.locator("#clock").click();
    assert.match(await market.locator("#clock time").textContent(), /^2026-11-23 03:30:/);
    assert.match(await market.locator("[data-market-next]").textContent(), /01:30:00.*GMT\+3:30/);
    await market.clock.setSystemTime(new Date("2026-11-22T22:59:58Z"));
    await market.clock.runFor(1000);
    await market.waitForFunction(() => document.querySelector("#clock")?.dataset.marketState === "closed");
    await market.clock.setSystemTime(new Date("2027-03-14T22:00:00Z"));
    await market.clock.runFor(1000);
    await market.waitForFunction(() => document.querySelector("[data-market-next]")?.textContent.includes("00:30:00"));
    await market.clock.setSystemTime(new Date("2026-12-24T18:44:58Z"));
    await market.clock.runFor(1000);
    await market.waitForFunction(() => document.querySelector("[data-market-next]")?.dateTime === "2026-12-24T18:45:00.000Z");
    assert.match(await market.locator("[data-market-next]").textContent(), /22:15:00.*GMT\+3:30/);
    assert.match(await market.locator("[data-market-instrument]").textContent(), /Holiday hours/);
    await market.clock.runFor(1000);
    await market.waitForFunction(() => document.querySelector("#clock")?.dataset.marketState === "closed");
    assert.equal(await market.locator("[data-market-next]").getAttribute("datetime"), "2026-12-27T23:00:00.000Z");
    await market.close();

    const report = await browser.newPage();
    const entryTime = Date.parse("2026-11-24T08:21:00+03:30") / 1000;
    await report.route("**/api/info/**", route => route.fulfill({ json: { payload: { directions: { bearish: {
      positions: [...Array.from({ length: 40 }, (_, index) => ({ type: "1.1S", entryTime: entryTime - 300 - index * 30 })),
        { type: "2.1S", entryTime, entryPrice: "100.005", anchorSourceTime: entryTime - 60 },
        { type: "2.2S", entryTime, entryPrice: "99.005" }],
      stopAlls: [{ sourceTime: entryTime - 60, number: 1 }],
      aZones: [{ sourceTime: entryTime, number: 1 }],
      bridgeOutput: { stopAlls: [{ formation: "Fixture stop" }] },
    } } }, snapshot: {} } }));
    await report.goto(`${origin}/info/XAUUSD/30s/bearish/1795-1796--0000000000000000.json`);
    await report.locator("#record-search").fill("2026-11-24 08:21:00 |  bearish | 2.1S");
    const visible = report.locator(".event[data-located]");
    assert.equal(await visible.count(), 1);
    assert.ok(await report.locator(".event:not([hidden])").count() > 1);
    assert.ok(await visible.isVisible());
    assert.equal(await visible.getAttribute("data-copy-label"), "2.1S");
    await report.waitForFunction(() => {
      const node = document.querySelector(".event[data-located]");
      if (!node) return false;
      const bounds = node.getBoundingClientRect();
      return scrollY > 0 && bounds.top < innerHeight && bounds.bottom > 0;
    });
    assert.match(await visible.locator(".bridge-yaml").textContent(), /100\.005/);
    assert.match(await visible.locator(".bridge-yaml").textContent(), /Fixture stop/);
    await report.close();
    const restored = await openChart();
    assert.deepEqual(await drawingOrder(restored), order);
    await addLine(restored, 30);
    assert.equal(await restored.locator("#lineWidth").inputValue(), "2");
    await restored.locator("#symbolBtn").click();
    assert.deepEqual((await bookmarks(restored)).filter(id => id !== gold.chartId), [older.chartId, newer.chartId]);
    assert.equal(await restored.locator(`[data-bookmark-chart-id="${older.chartId}"]`).getAttribute("aria-pressed"), "true");
    await restored.keyboard.press("Escape");
    await restored.locator("#realtimeChartBtn").click();
    assert.equal(await restored.locator("#realtimeChartInterval").inputValue(), "300000");
    assert.equal(await restored.getByRole("button", { name: "Enable", exact: true }).isVisible(), true);
    await restored.keyboard.press("Escape");
    await restored.locator("#indicatorBtn").click();
    assert.equal(await restored.locator("#indicatorEnabled").isChecked(), true);
    assert.equal(await restored.locator('[data-direction="bearish"]').getAttribute("aria-pressed"), "true");
    assert.equal(await restored.locator("#foundationTfVisible").isChecked(), !visibleBefore);
    await restored.locator("#closeIndicator").click();
    await restored.locator("#alertBtn").click();
    await restored.waitForURL("**/alert?*");
    await restored.reload();
    await restored.waitForFunction(() => document.querySelector("[data-workspace=alert]"));
    await restored.locator("#candleExportBtn").click();
    await restored.waitForURL("**/faraz?*");
    await restored.locator("#algorithmBtn").click();
    await restored.waitForFunction(() => location.pathname === "/algorithm" && location.hash.startsWith("#algorithm-"));
    const articleUrl = restored.url();
    await restored.locator("#chartNavBtn").click();
    await restored.waitForURL("**/chart?*");
    await restored.goBack();
    await restored.waitForURL(articleUrl);
    await restored.waitForFunction(() => document.querySelector("[data-workspace=algorithm]"));
    await restored.goBack();
    await restored.waitForFunction(() => location.pathname === "/faraz" && document.querySelector("[data-workspace=faraz]"));
    await restored.goBack();
    await restored.waitForFunction(() => location.pathname === "/alert" && document.querySelector("[data-workspace=alert]"));
    await restored.goForward();
    await restored.waitForFunction(() => location.pathname === "/faraz" && document.querySelector("[data-workspace=faraz]"));
    await restored.goForward();
    await restored.waitForURL(articleUrl);
    await restored.waitForFunction(() => document.querySelector("[data-workspace=algorithm]"));
    await restored.goForward();
    await restored.waitForFunction(() => location.pathname === "/chart" && document.querySelector("[data-workspace=chart]"));
    await restored.setViewportSize({ width: 390, height: 844 });
    await restored.locator("#symbolBtn").click();
    const menuBounds = await restored.locator("#symbolMenu").boundingBox();
    const bookmarkBounds = await restored.locator(`[data-bookmark-chart-id="${older.chartId}"]`).boundingBox();
    assert.ok(bookmarkBounds.x >= menuBounds.x);
    assert.ok(bookmarkBounds.x + bookmarkBounds.width <= menuBounds.x + menuBounds.width);
    assert.deepEqual(errors, []);
  } finally {
    await browser?.close();
    await server?.close();
    if (priorStateRoot === undefined) delete process.env.TRADINGBOT_LOCAL_STATE_ROOT;
    else process.env.TRADINGBOT_LOCAL_STATE_ROOT = priorStateRoot;
    assert.equal(path.dirname(stateRoot), tempRoot);
    await fs.rm(stateRoot, { recursive: true, force: true });
  }
});
