import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";

const source = readFileSync(new URL("../src/browser-compat.js", import.meta.url), "utf8");

test("Chrome 89 compatibility fallbacks provide Array.at and structuredClone", () => {
  const context = vm.createContext({});
  vm.runInContext("Array.prototype.at = undefined; globalThis.structuredClone = undefined;", context);
  vm.runInContext(source, context);
  const result = vm.runInContext(`(() => {
    const original = { nested: { value: 1 }, items: ["first", "last"] };
    const copy = structuredClone(original);
    copy.nested.value = 2;
    return { first: original.items.at(0), last: original.items.at(-1), originalValue: original.nested.value };
  })()`, context);
  assert.equal(result.first, "first");
  assert.equal(result.last, "last");
  assert.equal(result.originalValue, 1);
});
