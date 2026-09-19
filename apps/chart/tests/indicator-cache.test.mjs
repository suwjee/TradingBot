import test from "node:test";
import assert from "node:assert/strict";

import { cacheClearLayers, clearDrawingStorage, clearIndicatorStorage, selectedCacheLayers } from "../src/features/indicator-cache.js";

function storageWith(keys) {
  const values = new Map(keys.map((key) => [key, "value"]));
  return {
    get length() { return values.size; },
    key(index) { return [...values.keys()][index] ?? null; },
    removeItem(key) { values.delete(key); },
    has(key) { return values.has(key); },
  };
}

test("symbol cache clearing removes every file context for that symbol only", () => {
  const first = "market-canvas:file-a:indicator-settings:v1";
  const second = "market-canvas:file-b:indicator-overrides:v1";
  const other = "market-canvas:file-c:indicator-settings:v1";
  const storage = storageWith([first, second, other]);

  assert.equal(clearIndicatorStorage(storage, {
    scope: "symbol",
    fileIds: ["file-a", "file-b"],
  }), 2);
  assert.equal(storage.has(first), false);
  assert.equal(storage.has(second), false);
  assert.equal(storage.has(other), true);
});

test("cache scopes expose secret only for all charts", () => {
  assert.equal(cacheClearLayers("current").includes("secret"), false);
  assert.equal(cacheClearLayers("all").includes("secret"), true);
  assert.equal(cacheClearLayers("symbol").includes("drawings"), true);
});

test("selected cache layers reject secret for a symbol-scoped clear", () => {
  assert.deepEqual(
    selectedCacheLayers("symbol", ["calculations", "secret", "drawings"]),
    ["calculations", "drawings"],
  );
});

test("drawing cache clearing honors the selected chart scope", () => {
  const first = "market-canvas:file-a:drawings";
  const other = "market-canvas:file-b:drawings";
  const storage = storageWith([first, other]);

  assert.equal(clearDrawingStorage(storage, { scope: "symbol", fileId: "file-a" }), 1);
  assert.equal(storage.has(first), false);
  assert.equal(storage.has(other), true);
});
