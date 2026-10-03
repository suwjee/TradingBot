import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

import { cachePathForRaw, readCalculationCache, writeCalculationCache } from "../../server/calculation-cache.js";

test("calculation cache accepts only a result stamped for the current RAW bytes", (t) => {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), "tradingbot-cache-identity-"));
  t.after(() => fs.rmSync(directory, { recursive: true, force: true }));
  const file = path.join(directory, "result.json");
  fs.writeFileSync(file, "old result");
  assert.equal(readCalculationCache(file, "old-raw-hash"), null);
  writeCalculationCache(file, "old-raw-hash", "old result");
  assert.equal(readCalculationCache(file, "old-raw-hash"), "old result");
  assert.equal(readCalculationCache(file, "new-raw-hash"), null);
  writeCalculationCache(file, "new-raw-hash", "new result");
  assert.equal(readCalculationCache(file, "new-raw-hash"), "new result");
  assert.equal(readCalculationCache(file, "old-raw-hash"), null);
});

test("a changed RAW digest keeps an existing stamped report at its public path", (t) => {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), "tradingbot-cache-report-"));
  t.after(() => fs.rmSync(directory, { recursive: true, force: true }));
  const publicPath = path.join(directory, "report.json");
  const changedPath = path.join(directory, "new-report.json");
  writeCalculationCache(publicPath, "old-hash", "old report");
  assert.equal(cachePathForRaw(publicPath, "old-hash", changedPath), publicPath);
  assert.equal(cachePathForRaw(publicPath, "new-hash", changedPath), changedPath);
  writeCalculationCache(changedPath, "new-hash", "new report");
  assert.equal(fs.readFileSync(publicPath, "utf8"), "old report");
  assert.equal(readCalculationCache(changedPath, "new-hash"), "new report");
});
