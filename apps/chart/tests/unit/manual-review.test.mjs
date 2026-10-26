import test from "node:test";
import assert from "node:assert/strict";

import {
  buildReviewBody,
  manualInfoObject,
  reportCategoryColor,
  reportDisplayLabel,
  reviewRecords,
  reviewColor,
  visibleReviewTimeGroupIds,
} from "../../src/features/manual-review/render.js";

test("counted report labels retain finalized behavior numbers", () => {
  for (const [family, number, expected] of [
    ["E Red", 3, "E-3"], ["E Blue", 12, "E-12"], ["StopAll", 9, "StopAll-9"],
    ["PH", 5, "PH-5"], ["PL", 2, "PL-2"], ["A", 4, "A-4"],
  ]) assert.equal(reportDisplayLabel({ category: { family }, row: { number } }), expected);
  assert.equal(reportDisplayLabel({ category: { family: "E Red" }, row: {} }), "E");
  assert.equal(reportDisplayLabel({ category: { family: "MBL" }, row: { number: 9 } }), "MBL");
});

test("raw primary collections become PH PL MBL events and exclude cycle metadata", () => {
  const payload = { directions: { bearish: {
    primaryHighs: [{ id: "high", number: 5, sourceTime: 100, price: "12" }],
    primaryLows: [{ id: "low", number: 2, sourceTime: 200, price: "8" }],
    matchingBehaviorLegs: [{ id: "leg", sourceTime: 50, price: "9" }],
    primaryCycles: [{ id: "internal-cycle", triggerTime: 90 }],
  } } };
  const original = JSON.stringify(payload);
  const records = reviewRecords(payload);
  assert.deepEqual(records.map(record => [record.category.family, reportDisplayLabel(record)]),
    [["MBL", "MBL"], ["PH", "PH-5"], ["PL", "PL-2"]]);
  assert.equal(JSON.stringify(payload), original);
});

test("structured report numbers and primary family names are preserved", () => {
  const records = reviewRecords({ directions: {}, report: [
    { id: "e", time: "2026-01-01 10:00:00", category: { key: "e:red:3", family: "E Red", label: "E3" }, details: { number: 3 } },
    { id: "high", time: "2026-01-01 10:01:00", category: { key: "primaryHighs", family: "primaryHighs" }, details: { number: 5 } },
    { id: "cycles", category: { key: "primaryCycles", family: "primaryCycles" }, details: {} },
  ] });
  assert.deepEqual(records.map(record => reportDisplayLabel(record)), ["E-3", "PH-5"]);
  assert.deepEqual(records.map(record => record.category.family), ["E Red", "PH"]);
});

test("structured reports keep an explicit numbered label when details omit number", () => {
  for (const [family, label, expected] of [
    ["E Blue", "E7", "E-7"], ["StopAll", "StopAll9", "StopAll-9"],
    ["PH", "PH-5", "PH-5"], ["PL", "PL-2", "PL-2"],
  ]) assert.equal(reportDisplayLabel({ category: { family }, label, row: {} }), expected);
  assert.equal(reportDisplayLabel({ category: { family: "E Blue", label: "E Blue / E7" }, row: {} }), "E-7");
});

test("primary collection aliases retain explicit category-only numbers", () => {
  const records = reviewRecords({ directions: {}, report: [
    { id: "high", category: { key: "primaryHighs", family: "primaryHighs", label: "PH-5" }, details: {} },
    { id: "low", category: { key: "primaryLows", family: "primaryLows", label: "PL-2" }, details: {} },
  ] });
  assert.deepEqual(records.map(record => reportDisplayLabel(record)), ["PH-5", "PL-2"]);
});

test("primary report colors follow chart defaults direction appearance and object overrides", () => {
  const record = (group, kind, direction = "bearish") => ({
    group, direction, row: { id: "point", sourceTime: 1 },
    category: { key: group, family: kind },
  });
  const ph = record("primaryHighs", "PH"), pl = record("primaryLows", "PL");
  const mbl = record("matchingBehaviorLegs", "MBL");
  assert.equal(reviewColor(ph), "#056656");
  assert.equal(reviewColor(pl), "#ec407a");
  assert.equal(reviewColor(mbl), "#b22833");
  assert.equal(reviewColor(record("primaryHighs", "PH", "bullish")), "#ec407a");
  assert.equal(reviewColor(record("primaryLows", "PL", "bullish")), "#056656");
  assert.equal(reviewColor(ph, { settings: { primaryArrowColor: "#123456" } }), "#123456");
  assert.equal(reviewColor(ph, { indicatorObjects: [
    { id: "indicator:bearish:primary:PH:point", customized: true, color: "#abcdef" },
  ] }), "#abcdef");
});

test("default report controls and rows hide Reaction Reset and Blue Line only", async () => {
  const payload = { directions: { bearish: {
    reactions: [{ firstTime: 100 }], resets: [{ time: 110 }], blueLines: [{ sourceTime: 120 }],
    eZones: [{ sourceTime: 130, family: "red", number: 3 }],
    stopAlls: [{ sourceTime: 140, number: 9 }],
  } } };
  const { body } = await buildReviewBody(payload);
  for (const family of ["Reaction", "Reset", "Blue Line"]) {
    const controls = body.match(new RegExp(`<input[^>]+data-filter-family="${family}"[^>]*>`, "g"));
    assert.ok(controls?.length);
    for (const input of controls) assert.doesNotMatch(input, /\bchecked\b/);
    const article = body.match(new RegExp(`<article[^>]+data-report-family="${family}"[^>]*>`))?.[0];
    assert.match(article, /\bhidden\b/);
  }
  for (const label of ["E-3", "StopAll-9"]) assert.match(body, new RegExp(`class="chip"[^>]*>${label}</span>`));
});

test("Reaction filter family color follows the calculation direction", async () => {
  for (const direction of ["bearish", "bullish"]) {
    const { body } = await buildReviewBody({ directions: { [direction]: {
      reactions: [{ firstTime: 100 }],
    } } });
    assert.match(body, new RegExp(`data-filter-group="Reaction" style="--family-color:var\\(--report-reaction-${direction}\\)"`));
  }
});

test("live report offers all visible events in addition to reviewed statuses", async () => {
  const { body } = await buildReviewBody({ directions: { bearish: { eZones: [{ sourceTime: 100, number: 3, family: "red" }] } } });
  assert.match(body, /<option value="visible">All visible<\/option>/);
  for (const value of ["all", "true", "false"]) assert.match(body, new RegExp(`<option value="${value}">`));
});

test("primary report chips and filters use chart colors and omit primaryCycles", async () => {
  const payload = { directions: { bearish: {
    primaryHighs: [{ id: "high", number: 5, sourceTime: 100, price: "12" }],
    primaryLows: [{ id: "low", number: 2, sourceTime: 200, price: "8" }],
    matchingBehaviorLegs: [{ id: "leg", sourceTime: 50, price: "9" }],
    primaryCycles: [{ id: "internal-cycle" }],
  } } };
  const { body } = await buildReviewBody(payload, { settings: { primaryArrowColor: "#123456" } });
  for (const [label, color] of [["PH-5", "#123456"], ["PL-2", "#ec407a"], ["MBL", "#b22833"]]) {
    assert.match(body, new RegExp(`class="chip"[^>]*--chip-color:${color}[^>]*>${label}</span>`));
  }
  for (const family of ["PH", "PL", "MBL"]) assert.match(body, new RegExp(`data-filter-group="${family}"`));
  assert.doesNotMatch(body, /primaryCycles|internal-cycle|primaryHighs<|primaryLows<|matchingBehaviorLegs</);
});

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
  assert.match(body, />E-1<\/span>/);
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
  assert.match(body, />E-1<\/span>/);
  assert.doesNotMatch(body, /<span>Blue Line<\/span>/);
  assert.doesNotMatch(body, /<span>S<\/span>/);
  assert.doesNotMatch(body, /<span>E<\/span>/);
});
