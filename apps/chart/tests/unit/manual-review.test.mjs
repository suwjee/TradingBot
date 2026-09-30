import test from "node:test";
import assert from "node:assert/strict";

import {
  buildReviewBody,
  manualInfoObject,
  reportCategoryColor,
  reportDisplayLabel,
  visibleReviewTimeGroupIds,
} from "../../src/features/manual-review/render.js";

test("report labels use family names while retaining semantic color variants", () => {
  assert.equal(reportDisplayLabel({ direction: "Bullish", category: { family: "Blue Line" }, label: "Blue Line / Reset" }), "Blue Line");
  assert.equal(reportDisplayLabel({ direction: "Bullish", category: { family: "S Blue" }, label: "S Blue / Simple" }), "S");
  assert.equal(reportDisplayLabel({ direction: "Bullish", category: { family: "Order Audit", label: "Order_A | Order_B" }, label: "Order_A | Order_B" }), "Order_A | Order_B");
  assert.equal(reportDisplayLabel({ direction: "Bearish", category: { family: "Reaction" }, label: "Bearish Reaction" }), "Bearish Reaction");
  assert.equal(reportCategoryColor("reactions:bullish", "Reaction"), "var(--report-reaction-bullish)");
  assert.equal(reportCategoryColor("reactions:bearish", "Reaction"), "var(--report-reaction-bearish)");
});

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

test("report records render from the bridge report payload inside a collapsed bridge disclosure", async () => {
  const payload = {
    timeframe: 5,
    directions: {},
    report: [
      {
        id: "bullish:a:0",
        time: "2026-09-15 10:00:01",
        direction: "Bullish",
        label: "A / Normal",
        category: { key: "a:normal", family: "A", label: "A / Normal", count: 1 },
        details: { type: "A", direction: "Bullish", formation: "Normal" },
      },
    ],
  };
  const cryptoApi = { subtle: { async digest() { return new Uint8Array(32).buffer; } } };
  const { body } = await buildReviewBody(payload, {}, cryptoApi);

  assert.match(body, /class="filter-sidebar"/);
  assert.match(body, /class="chip"[^>]*>A<\/span>/);
  assert.match(body, />Normal<\/span>/);
  assert.doesNotMatch(body, /A \/ Normal/);
  assert.match(body, /class="bridge-output"/);
  assert.doesNotMatch(body, /<details[^>]+class="bridge-output"[^>]*open/);
  assert.doesNotMatch(body, /Events are grouped by Tehran calendar day/);
  assert.doesNotMatch(body, /Source SHA-256/);
});

test("Bridge output uses the finalized projection at the matching legacy collection index", () => {
  const projected = {
    type: "Reaction",
    direction: "Bullish",
    mode: "Leg Start",
    firstCandle: { color: "Green", time: "2026-09-15 10:00:00" },
  };
  const record = {
    group: "reactions",
    index: 1,
    direction: "bullish",
    row: { firstTime: 1_789_430_400, mode: "B" },
    groups: {
      reactions: [{ firstTime: 1 }, { firstTime: 1_789_430_400, mode: "B" }],
      bridgeOutput: { reactions: [{ type: "wrong row" }, projected] },
    },
  };

  assert.deepEqual(manualInfoObject(record), projected);
});

test("sidebar filters subdivide Reaction and S rows by finalized formation", async () => {
  const payload = {
    timeframe: 5,
    directions: {
      bearish: {
        reactions: [
          { firstTime: 1_789_430_400, mode: "B" },
          { firstTime: 1_789_430_405, mode: "A" },
        ],
        sZones: [
          { sourceTime: 1_789_430_410, color: "blue" },
          { sourceTime: 1_789_430_415, color: "blue" },
          { sourceTime: 1_789_430_420, color: "blue" },
          { sourceTime: 1_789_430_425, color: "blue" },
          { sourceTime: 1_789_430_430, color: "red" },
        ],
        bridgeOutput: {
          reactions: [
            { type: "Reaction", direction: "Bearish", mode: "Normal" },
            { type: "Reaction", direction: "Bearish", mode: "Leg Start" },
          ],
          sZones: [
            { type: "S", direction: "Bearish", color: "Blue", formation: "Type-1" },
            { type: "S", direction: "Bearish", color: "Blue", formation: "Type-2" },
            { type: "S", direction: "Bearish", color: "Blue", formation: "Type-3" },
            { type: "S", direction: "Bearish", color: "Blue", formation: "Type-4" },
            { type: "S", direction: "Bearish", color: "Red" },
          ],
        },
      },
    },
  };
  const cryptoApi = { subtle: { async digest() { return new Uint8Array(32).buffer; } } };
  const { body } = await buildReviewBody(payload, {}, cryptoApi);

  for (const filterKey of [
    "reactions:bearish:normal", "reactions:bearish:reset-leg",
    "sZones:blue:type-1", "sZones:blue:type-2", "sZones:blue:type-3",
    "sZones:blue:type-4", "sZones:red:simple",
  ]) assert.match(body, new RegExp(`data-filter-key="${filterKey}"`));
  assert.match(body, /data-filter-family="Reaction"/);
  assert.match(body, /data-filter-family="S Blue"/);
  assert.match(body, /data-filter-family="S Red"/);
  assert.match(body, />Reset leg<\/span>/);
  assert.match(body, />Simple<\/span>/);
});

test("sidebar filters use the other finalized Bridge formations without changing legacy rows", async () => {
  const payload = {
    timeframe: 5,
    directions: {
      bullish: {
        blueLines: [{ sourceTime: 1_789_430_400 }],
        aZones: [{ sourceTime: 1_789_430_405 }],
        eZones: [{ sourceTime: 1_789_430_410, family: "blue" }],
        stopAlls: [{ sourceTime: 1_789_430_415 }],
        bridgeOutput: {
          blueLines: [{ type: "Blue Line", direction: "Bullish", formation: "Scale" }],
          aZones: [{ type: "A", direction: "Bullish", formation: "Type-1" }],
          eZones: [{ type: "E", direction: "Bullish", color: "Blue", number: 1 }],
          stopAlls: [{ type: "StopAll", direction: "Bullish", formation: "Type-2" }],
        },
      },
    },
  };
  const cryptoApi = { subtle: { async digest() { return new Uint8Array(32).buffer; } } };
  const { body } = await buildReviewBody(payload, {}, cryptoApi);

  for (const filterKey of [
    "blueLines:scale", "aZones:type-1", "eZones:blue:e1", "stopAlls:type-2",
  ]) assert.match(body, new RegExp(`data-filter-key="${filterKey}"`));
  assert.match(body, />Scale<\/span>/);
  assert.match(body, />Type-1<\/span>/);
  assert.match(body, />E1<\/span>/);
  assert.match(body, />Type-2<\/span>/);
});

test("Order Audit filters use finalized Order_A and Order_B cause formations", async () => {
  const payload = {
    timeframe: 5,
    directions: {
      bullish: {
        orderAudit: [
          { firstTime: 1_789_430_400 },
          { firstTime: 1_789_430_405 },
          { firstTime: 1_789_430_410 },
        ],
        bridgeOutput: {
          orderAudit: [
            { type: "Order Audit", causes: [{ kind: "parent-stop" }] },
            { type: "Order Audit", causes: [{ kind: "reset-leg" }] },
            { type: "Order Audit", causes: [{ kind: "parent-stop" }, { kind: "reset-leg" }] },
          ],
        },
      },
    },
  };
  const cryptoApi = { subtle: { async digest() { return new Uint8Array(32).buffer; } } };
  const { body } = await buildReviewBody(payload, {}, cryptoApi);

  for (const filterKey of ["orderAudit:order-a", "orderAudit:order-b", "orderAudit:order-a-order-b"]) {
    assert.match(body, new RegExp(`data-filter-key="${filterKey}"`));
  }
  assert.match(body, />Order_A<\/span>/);
  assert.match(body, />Order_B<\/span>/);
  assert.match(body, />Order_A \| Order_B<\/span>/);
});

test("report filters expose grouped families and subtype keys", async () => {
  const payload = {
    timeframe: 5,
    directions: {},
    report: [
      { id: "bullish:a:0", time: "2026-09-15 10:00:01", direction: "Bullish", label: "A / Normal", category: { key: "a:normal", family: "A", label: "A / Normal", count: 1 }, details: {} },
      { id: "bullish:a:1", time: "2026-09-15 10:00:02", direction: "Bullish", label: "A / Double Stop", category: { key: "a:double-stop", family: "A", label: "A / Double Stop", count: 1 }, details: {} },
    ],
  };
  const cryptoApi = { subtle: { async digest() { return new Uint8Array(32).buffer; } } };
  const { body } = await buildReviewBody(payload, {}, cryptoApi);

  assert.match(body, /data-filter-family="A"/);
  assert.match(body, /data-filter-key="a:normal"/);
  assert.match(body, /data-filter-key="a:double-stop"/);
  assert.match(body, /class="filter-tree"/);
  assert.match(body, /id="all-filters"/);
  assert.match(body, /class="filter-all-toggle"/);
  assert.match(body, /class="filter-group-checkbox"/);
  assert.match(body, /class="filter-options"/);
  assert.match(body, /class="filter-total-count">2</);
});

test("order audit filters preserve combined Order_A and Order_B labels", async () => {
  const payload = {
    timeframe: 5,
    directions: {},
    report: [
      {
        id: "bullish:orderAudit:0",
        time: "2026-09-15 10:00:01",
        direction: "Bullish",
        label: "Order_A | Order_B",
        category: {
          key: "order:order_a|order_b",
          family: "Order Audit",
          label: "Order_A | Order_B",
        },
        details: { type: "Order Audit", formation: "Order_A | Order_B" },
      },
    ],
  };
  const cryptoApi = { subtle: { async digest() { return new Uint8Array(32).buffer; } } };
  const { body } = await buildReviewBody(payload, {}, cryptoApi);

  assert.match(body, />Order_A \| Order_B<\/span>/);
});

test("filter children retain their canonical subtype labels", async () => {
  const payload = {
    timeframe: 5,
    directions: {},
    report: [
      { id: "bullish:blue:0", time: "2026-09-15 10:00:01", direction: "Bullish", label: "Scale", category: { key: "blue:scale", family: "Blue Line", label: "Blue Line / Scale" }, details: {} },
      { id: "bullish:s:0", time: "2026-09-15 10:00:02", direction: "Bullish", label: "Simple", category: { key: "s:blue:simple", family: "S Blue", label: "S Blue / Simple" }, details: {} },
      { id: "bullish:e:0", time: "2026-09-15 10:00:03", direction: "Bullish", label: "E1", category: { key: "e:blue:1", family: "E Blue", label: "E Blue / E1" }, details: {} },
    ],
  };
  const cryptoApi = { subtle: { async digest() { return new Uint8Array(32).buffer; } } };
  const { body } = await buildReviewBody(payload, {}, cryptoApi);

  assert.match(body, />Scale<\/span>/);
  assert.match(body, />Simple<\/span>/);
  assert.match(body, />E1<\/span>/);
  assert.doesNotMatch(body, /<span>Blue Line<\/span>/);
  assert.doesNotMatch(body, /<span>S<\/span>/);
  assert.doesNotMatch(body, /<span>E<\/span>/);
});
