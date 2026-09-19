import test from "node:test";
import assert from "node:assert/strict";

test("screenshot overlay writes symbol timeframe and Tehran capture time", async () => {
  const { drawScreenshotOverlay } = await import("../src/features/screenshot-overlay.js");
  const text = [];
  drawScreenshotOverlay({
    save() {}, restore() {}, scale() {}, fillRect() {}, fillText(value) { text.push(value); },
    measureText() { return { width: 120 }; },
  }, { symbol: "XAUUSD", timeframe: "5s", capturedAt: new Date("2026-09-15T06:30:00Z") });
  assert.equal(text[0], "XAUUSD · 5s");
  assert.match(text[1], /^Asia\/Tehran · \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/);
});
