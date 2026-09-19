import test from "node:test";
import assert from "node:assert/strict";

import { buildReviewBody, visibleReviewTimeGroupIds } from "../src/features/manual-review/render.js";

test("time-group bulk selection is limited to visible records in that Tehran day", () => {
  const ids = visibleReviewTimeGroupIds([
    { id: "bullish:reactions:0", timeGroup: "2026-09-15", hidden: false },
    { id: "bullish:sZones:0", timeGroup: "2026-09-15", hidden: true },
    { id: "bearish:reactions:0", timeGroup: "2026-09-16", hidden: false },
  ], "2026-09-15");

  assert.deepEqual(ids, ["bullish:reactions:0"]);
});

test("review body exposes only day-scoped bulk review controls", async () => {
  const payload = {
    timeframe: 5,
    directions: {
      bullish: { reactions: [{ firstTime: 1_789_430_400, breakTime: 1_789_430_405, mode: "A" }] },
    },
  };
  const cryptoApi = { subtle: { async digest() { return new Uint8Array(32).buffer; } } };
  const { body } = await buildReviewBody(payload, {}, cryptoApi);

  assert.match(body, /data-time-group-status="true"/);
  assert.match(body, /data-time-group-status="false"/);
  assert.match(body, /data-time-group="2026-09-15"/);
  assert.doesNotMatch(body, /data-collection-status/);
});
