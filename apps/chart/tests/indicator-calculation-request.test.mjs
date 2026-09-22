import test from "node:test";
import assert from "node:assert/strict";

import { buildIndicatorCalculationRequest } from "../src/features/indicator-calculation-request.js";

test("indicator calculation request preserves the selected inclusive range and chart timeframe", () => {
  assert.deepEqual(buildIndicatorCalculationRequest({
    file: { id: "FXCM/USOIL/source.json", chartId: "chart-123" },
    analysisTimeframe: 300,
    chartTimeframe: 60,
    from: 1_800,
    to: 2_400,
    direction: "bullish",
    requestId: "request-12345678",
  }), {
    id: "FXCM/USOIL/source.json",
    chartId: "chart-123",
    timeframe: 300,
    chartTimeframe: 60,
    from: 1_800,
    to: 2_400,
    direction: "bullish",
    blueLines: true,
    requestId: "request-12345678",
  });
});
