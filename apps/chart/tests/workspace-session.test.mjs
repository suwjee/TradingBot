import test from "node:test";
import assert from "node:assert/strict";

import {
  chartTabUrl,
  resolveChartTabState,
  resolveWorkspaceRefreshState,
} from "../src/features/workspace-session.js";

test("refresh state keeps the prior workspace, selected RAW resource, and supported timeframe", () => {
  assert.deepEqual(resolveWorkspaceRefreshState({
    workspace: "faraz", fileId: "FXCM/USOIL/raw.json", timeframe: 300,
  }, {
    fileIds: ["FXCM/USOIL/raw.json"],
    timeframes: [5, 30, 60, 300],
  }), {
    workspace: "faraz", fileId: "FXCM/USOIL/raw.json", timeframe: 300,
  });
});

test("refresh state rejects stale workspace, resource, and timeframe values", () => {
  assert.deepEqual(resolveWorkspaceRefreshState({
    workspace: "unknown", fileId: "gone.json", timeframe: 17,
  }, {
    fileIds: ["FXCM/USOIL/raw.json"],
    timeframes: [5, 30, 60],
  }), {
    workspace: "chart", fileId: null, timeframe: null,
  });
});

test("a chartId in the tab URL wins over shared browser fallback state", () => {
  const inventory = [
    { id: "FOREXCOM/XAUUSD/a.json", chartId: "11111111-1111-4111-8111-111111111111" },
    { id: "FXCM/USOIL/b.json", chartId: "22222222-2222-4222-8222-222222222222" },
  ];

  assert.deepEqual(resolveChartTabState(
    "?chartId=11111111-1111-4111-8111-111111111111&tf=30",
    { inventory, timeframes: [5, 30, 60] },
  ), {
    chartId: "11111111-1111-4111-8111-111111111111",
    fileId: "FOREXCOM/XAUUSD/a.json",
    timeframe: 30,
  });
});

test("multiple tabs can resolve the same chartId independently", () => {
  const inventory = [
    { id: "FOREXCOM/XAUUSD/a.json", chartId: "11111111-1111-4111-8111-111111111111" },
  ];
  const options = { inventory, timeframes: [5, 30, 60] };

  const firstTab = resolveChartTabState(
    "?chartId=11111111-1111-4111-8111-111111111111&tf=30",
    options,
  );
  const secondTab = resolveChartTabState(
    "?chartId=11111111-1111-4111-8111-111111111111&tf=60",
    options,
  );

  assert.equal(firstTab.fileId, "FOREXCOM/XAUUSD/a.json");
  assert.equal(secondTab.fileId, "FOREXCOM/XAUUSD/a.json");
  assert.equal(firstTab.timeframe, 30);
  assert.equal(secondTab.timeframe, 60);
});

test("chart tab URL preserves unrelated query values and the workspace hash", () => {
  assert.equal(chartTabUrl(
    "http://localhost:5173/?mode=review#algorithm-overview",
    { chartId: "11111111-1111-4111-8111-111111111111", timeframe: 30 },
  ), "/?mode=review&chartId=11111111-1111-4111-8111-111111111111&tf=30#algorithm-overview");
});
