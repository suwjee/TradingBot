import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { calculationInfoPath, openManualReviewTab } from "../src/manual-test.js";

const entrySource = readFileSync(new URL("../src/manual-test-entry.js", import.meta.url), "utf8");
const viteSource = readFileSync(new URL("../vite.config.js", import.meta.url), "utf8");

const calculation = { calculationId: "FOREXCOM-XAUUSD/30s/bullish/1788320800-1788449367--230da30e6e9508b3.json" };

test("calculation report URL is stable, cache-specific and popup-safe", () => {
  const opened = [], host = { open: (...args) => { opened.push(args); return {}; } };
  assert.equal(calculationInfoPath(calculation), "/info/FOREXCOM-XAUUSD/30s/bullish/1788320800-1788449367--230da30e6e9508b3.json");
  openManualReviewTab(calculation, host);
  assert.deepEqual(opened, [[calculationInfoPath(calculation), "_blank"]]);
  assert.throws(() => calculationInfoPath({}), /no persisted report identity/);
});

test("the served review route accepts the cache identity and exposes a cache-only API", () => {
  assert.match(viteSource, /middlewares\.use\('\/info'/);
  assert.match(viteSource, /middlewares\.use\('\/api\/info'/);
  assert.doesNotMatch(viteSource, /middlewares\.use\('\/manual-test'/);
});

test("the page entry fetches only the calculation identified in its URL", () => {
  assert.match(entrySource, /fetch\(`\/api\/info\/\$\{identity\}`/);
  assert.match(entrySource, /location\.pathname/);
  assert.doesNotMatch(entrySource, /BroadcastChannel/);
  assert.match(entrySource, /buildReviewBody/);
});
