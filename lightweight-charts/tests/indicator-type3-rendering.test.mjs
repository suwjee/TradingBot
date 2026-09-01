import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

const source = await readFile(new URL("../src/main.js", import.meta.url), "utf8");

test("Type 3 S renders its label without inventing order geometry or stop", () => {
  assert.match(source, /if \(item\.orderFirstTime != null\)/);
  assert.match(source, /hasOrder = zone\.orderFirstTime != null/);
  assert.match(
    source,
    /if \(zone\.orderStopSourceIndex == null \|\| zone\.orderStopLevel == null\) continue/,
  );
  assert.match(source, /event\.formationType === "type3"/);
  assert.match(source, /reset reaction \$\{event\.resetReactionNumber\}/);
});
