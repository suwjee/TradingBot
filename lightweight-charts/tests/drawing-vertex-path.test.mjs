import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

const source = readFileSync(new URL("../src/main.js", import.meta.url), "utf8");

test("visible non-Path endpoint handles resize without requiring Alt", () => {
  assert.match(source, /!isFreeform && Math\.hypot\(p\.x - a\.x, p\.y - a\.y\) < 7/);
  assert.doesNotMatch(source, /!isFreeform && e\.altKey && Math\.hypot\(p\.x - a\.x/);
  assert.match(source, /state\.interaction\.mode === "path-vertex"/);
});

test("right-click preserves a partially drawn Path while deselecting its tool", () => {
  assert.match(source, /preservePath && state\.draft\?\.type === "path" && state\.draft\.points\.length > 1/);
  assert.match(source, /finishDraft\(\);[\s\S]*PATH_DRAFT_PRESERVED/);
  assert.match(source, /cancelDrawingTool\("contextmenu", \{ preservePath: true \}\)/);
});
