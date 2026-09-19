import test from "node:test";
import assert from "node:assert/strict";

import { formatInventoryDateTime, formatSymbolWithBroker } from "../src/ui/symbol-format.js";

test("symbol inventory times use colon separators without changing the date", () => {
  assert.equal(
    formatInventoryDateTime("2026-09-03 19-05-48"),
    "2026-09-03 19:05:48",
  );
  assert.equal(
    formatInventoryDateTime("2026-09-03 19:05:48"),
    "2026-09-03 19:05:48",
  );
});

test("numeric RAW bounds display complete Tehran dates in symbol selection", () => {
  const epochSeconds = Date.UTC(2026, 9, 9, 19, 2, 6) / 1000;
  assert.equal(formatInventoryDateTime(epochSeconds), "2026-10-09 22:32:06");
});

test("symbol inventory formatting leaves unknown values intact", () => {
  assert.equal(formatInventoryDateTime("unknown"), "unknown");
  assert.equal(formatInventoryDateTime(""), "");
});

test("symbol labels include their broker exactly once", () => {
  assert.equal(formatSymbolWithBroker({ broker: "FXCM", symbol: "USOIL" }), "FXCM:USOIL");
  assert.equal(formatSymbolWithBroker({ broker: "FOREXCOM", symbol: "FOREXCOM:XAUUSD" }), "FOREXCOM:XAUUSD");
});
