import test from "node:test";
import assert from "node:assert/strict";

import { MIN_SAFE_BAR_SPACING, zoomOutCapacityGain } from "../../src/chart/zoom-config.js";

test("minimum bar spacing allows more than double the previous 0.25px viewport span", () => {
  assert.ok(Number.isFinite(MIN_SAFE_BAR_SPACING) && MIN_SAFE_BAR_SPACING > 0);
  assert.ok(zoomOutCapacityGain(0.25, MIN_SAFE_BAR_SPACING) > 2);
});
