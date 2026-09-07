import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

const source = await readFile(new URL("../src/main.js", import.meta.url), "utf8");

test("Type 3 S renders its label without inventing order geometry or stop", () => {
  assert.match(source, /if \(item\.calculationValid !== false && item\.orderFirstTime != null\)/);
  assert.match(source, /hasOrder = zone\.calculationValid !== false && zone\.orderFirstTime != null/);
  assert.match(
    source,
    /if \(zone\.orderStopSourceIndex == null \|\| zone\.orderStopLevel == null\) continue/,
  );
  assert.doesNotMatch(source, /audit \? zone\.stopSourceIndex : zone\.orderStopSourceIndex/);
  assert.match(source, /event\.formationType === "type3"/);
  assert.match(source, /reset reaction \$\{event\.resetReactionNumber\}/);
});

test("label-only invalid behavior cannot own chart calculations or order geometry", () => {
  assert.match(source, /function removeInvalidIndicatorCalculations\(payload\)/);
  assert.match(source, /group\[key\] = group\[key\]\.filter\(\(item\) => item\.calculationValid !== false\)/);
  assert.match(source, /state\.indicator\.results = removeInvalidIndicatorCalculations\(payload\)/);
  assert.match(source, /filter\(\(zone\) => zone\.calculationValid !== false\)/);
  assert.match(source, /if \(zone\.calculationValid === false\) continue/);
  assert.match(source, /item\.calculationValid !== false && item\.orderFirstIndex != null/);
});
