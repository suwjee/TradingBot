import test from "node:test";
import assert from "node:assert/strict";

import {
  buildRawFilename,
  formatTehranFileTime,
  parseRawFilename,
} from "../src/features/raw-file-contract.js";

test("RAW filenames use broker, symbol, source timeframe, and readable Tehran bounds", () => {
  assert.equal(formatTehranFileTime(1788449740), "2026-09-03 19-05-40");
  assert.equal(buildRawFilename({
    broker: "FOREXCOM",
    symbol: "XAUUSD",
    timeframe: "1s",
    firstTime: 1788449740,
    lastTime: 1788824908,
  }), "RAW FOREXCOM_XAUUSD 1S FROM 2026-09-03 19-05-40 TO 2026-09-08 03-18-28.json");
});

test("RAW filename parser rejects legacy FARAZ and numeric-bound names", () => {
  assert.deepEqual(parseRawFilename("RAW FXCM_USOIL 5S FROM 2026-09-11 02-53-30 TO 2026-09-15 11-03-45.json"), {
    broker: "FXCM",
    symbol: "USOIL",
    timeframe: "5S",
    fromTehran: "2026-09-11 02-53-30",
    toTehran: "2026-09-15 11-03-45",
  });
  assert.equal(parseRawFilename("RAW FARAZ_FXCM_USOIL 5S FROM 1789082610 TO 1789457625.json"), null);
});
