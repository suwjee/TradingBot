import test from "node:test";
import assert from "node:assert/strict";

import { MIN_SAFE_BAR_SPACING, zoomOutCapacityGain } from "../../src/chart/zoom-config.js";

test("minimum bar spacing adds 50% to 100% to the previous 0.10px viewport span", () => {
  assert.ok(Number.isFinite(MIN_SAFE_BAR_SPACING) && MIN_SAFE_BAR_SPACING > 0);
  const gain = zoomOutCapacityGain(0.10, MIN_SAFE_BAR_SPACING);
  assert.ok(gain >= 1.5 && gain <= 2);
});
