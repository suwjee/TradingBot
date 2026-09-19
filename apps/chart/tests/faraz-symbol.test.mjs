import assert from "node:assert/strict";
import test from "node:test";
import { isQualifiedFarazSymbol, normalizeFarazSymbol } from "../src/features/faraz-symbol.js";

test("FARAZ symbols reject persisted placeholders and use the selected RAW identity", () => {
  assert.equal(isQualifiedFarazSymbol("—"), false);
  assert.equal(normalizeFarazSymbol("—", "FXCM:USOIL"), "FXCM:USOIL");
  assert.equal(normalizeFarazSymbol("USOIL", "FXCM:USOIL"), "FXCM:USOIL");
});

test("FARAZ symbols preserve valid qualified custom identities", () => {
  assert.equal(isQualifiedFarazSymbol("forexcom:xauusd"), true);
  assert.equal(normalizeFarazSymbol("forexcom:xauusd", "FXCM:USOIL"), "FOREXCOM:XAUUSD");
});
