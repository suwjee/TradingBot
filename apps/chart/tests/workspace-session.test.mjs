import test from "node:test";
import assert from "node:assert/strict";

import { resolveWorkspaceRefreshState } from "../src/features/workspace-session.js";

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
