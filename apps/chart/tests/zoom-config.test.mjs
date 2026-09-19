import test from "node:test";
import assert from "node:assert/strict";

import { MIN_SAFE_BAR_SPACING, zoomOutCapacityGain } from "../src/chart/zoom-config.js";

test("minimum bar spacing provides at least twice the previous zoom-out capacity", () => {
  assert.ok(MIN_SAFE_BAR_SPACING > 0, "spacing must remain finite and positive");
  assert.ok(MIN_SAFE_BAR_SPACING <= 0.25);
  assert.ok(zoomOutCapacityGain(0.5, MIN_SAFE_BAR_SPACING) >= 2);
});
