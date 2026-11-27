import test from "node:test";
import assert from "node:assert/strict";
import { strFromU8, unzipSync } from "fflate";
import { buildReviewBody } from "../../src/features/manual-review/render.js";
import { createCalculationArchive } from "../../src/features/manual-review/archive.js";

test("the calculation ZIP includes the full snapshot, metadata and an offline report", async () => {
  const payload = {
    timeframe: 30, actualFrom: 100, actualTo: 200, activeDirection: "bearish",
    timings: { bridgeTotalMs: 1001.23, phasesMs: { "Run engine": 990.1 } },
    directions: {
      bullish: {
        reactions: [{ firstTime: 100 }],
        sZones: [{ sourceTime: 110, color: "red", trueFalse: "F" }],
        bridgeOutput: { sZones: [{ color: "red", price: "1.00000001", note: "</script>" }] },
      },
      bearish: {
        eZones: [{ sourceTime: 190, number: 1, family: "blue", trueFalse: "T" }],
        calculationSegments: [{ calculationStartTime: 150 }],
        primaryCycles: [{ id: "internal" }],
      },
    },
    futureField: { "a/b~c": [], details: { price: "1.00000001" } },
  };
  const snapshot = { calculation: {
    symbol: "XAUUSD", sourceFile: "folder/XAUUSD_5s.json", timeframe: 30, chartTimeframe: 60,
    rawTimeframeSeconds: 5, calculatedAt: "2026-11-04T13:17:00.000Z", direction: "bullish",
  } };
  const review = await buildReviewBody(payload, snapshot);
  const { name, bytes } = await createCalculationArchive({
    payload, snapshot, review, css: "body{color:red}", view: { open: [] },
    exportedAt: new Date("2026-11-04T13:18:00.123Z"),
  });
  assert.equal(name, "calculation-report-XAUUSD-30s-2026-11-04T13-18-00-123Z.zip");
  const files = unzipSync(bytes);
  const read = path => strFromU8(files[path]);
  const jsonText = read("calculation.json");
  assert.match(jsonText, /^\{\n {2}"metadata": \{\n {4}"schemaVersion": 1,/);
  assert.match(jsonText, /^ {8}"bullish": \{/m);
  const json = JSON.parse(jsonText);
  assert.equal(Object.keys(json)[0], "metadata");
  assert.deepEqual(json.payload, payload);
  assert.equal(json.metadata.sourceFile, "XAUUSD_5s.json");
  assert.equal(json.metadata.calculatedAt, snapshot.calculation.calculatedAt);
  assert.equal(json.metadata.exportedAt, "2026-11-04T13:18:00.123Z");
  assert.equal(json.metadata.durationMs, 1001.23);
  assert.equal(json.metadata.rawTimeframeSeconds, 5);
  assert.equal(json.metadata.initialDirection, "bullish");
  assert.equal(json.metadata.activeDirection, "bearish");
  assert.equal(json.metadata.includesBridgeOutput, true);
  assert.equal(json.metadata.counts.events, 3);
  assert.equal(json.metadata.counts.families.Reaction, 1);
  assert.equal(json.metadata.counts.families["S Red"], 1);
  assert.equal(json.metadata.counts.families["E Blue"], 1);
  assert.equal(json.metadata.counts.families["E Red"], 0);
  assert.equal(json.metadata.counts.payloadCollections.bearish.primaryCycles, 1);
  assert.equal(json.events[1].bridgeOutput.price, "1.00000001");

  const csv = read("calculation.csv");
  assert.match(csv, /\r\nmetadata,\/schemaVersion,/);
  assert.match(csv, /payload,\/directions\/bearish\/primaryCycles\/0,/);
  assert.match(csv, /payload,\/futureField\/a~1b~0c,/);
  const lines = read("calculation.ndjson").trimEnd().split("\n").map(line => JSON.parse(line));
  assert.deepEqual(lines[0], { section: "metadata", data: json.metadata });
  assert.deepEqual(lines.find(row => row.path === "/directions/bullish/bridgeOutput/sZones/0").data,
    payload.directions.bullish.bridgeOutput.sZones[0]);
  const html = read("html/index.html");
  assert.ok(html.includes(review.body));
  assert.ok(html.includes("body{color:red}"));
  assert.ok(html.includes("\\u003c/script>"));
  assert.doesNotMatch(html, /schemaVersion|exportedAt/);
});

test("Bridge Output can be excluded from machine-readable files while remaining available in HTML", async () => {
  const bridge = { important: "private-bridge-marker" };
  const payload = {
    bridgeOutput: bridge,
    directions: { bullish: {
      bridgeOutput: bridge,
      calculationSegments: [{ bridgeOutput: bridge, swings: [{ price: "1.00100" }] }],
      sZones: [{ color: "red", trueFalse: "F" }],
    } },
    report: [{ id: "item", direction: "Bullish", category: { family: "S Red" }, details: bridge }],
  };
  const review = await buildReviewBody(payload);
  const { bytes } = await createCalculationArchive({ payload, snapshot: {}, review, css: "", includeBridgeOutput: false });
  const files = unzipSync(bytes);
  for (const name of ["calculation.json", "calculation.csv", "calculation.ndjson"]) {
    const data = strFromU8(files[name]);
    assert.doesNotMatch(data, /private-bridge-marker/);
    assert.match(data, /1\.00100/);
  }
  const json = JSON.parse(strFromU8(files["calculation.json"]));
  assert.equal(json.metadata.includesBridgeOutput, false);
  assert.deepEqual(json.payload.directions.bullish.sZones, payload.directions.bullish.sZones);
  assert.equal(json.payload.report[0].id, "item");
  assert.ok(!Object.hasOwn(json.payload.report[0], "details"));
  assert.ok(!Object.hasOwn(json.events[0], "bridgeOutput"));
  assert.match(strFromU8(files["html/index.html"]), /private-bridge-marker/);
  assert.equal(payload.directions.bullish.bridgeOutput, bridge);
});

test("the ZIP contains only selected formats and HTML preserves the Bridge detail", async () => {
  const payload = { directions: { bullish: {
    sZones: [{ sourceTime: 110, color: "red" }],
    bridgeOutput: { sZones: [{ color: "red", note: "bridge-marker" }] },
  } } };
  const review = await buildReviewBody(payload);
  const options = { payload, snapshot: {}, review, css: "", includeBridgeOutput: false };
  const cases = [
    [["html"], ["html/index.html"]],
    [["csv"], ["calculation.csv"]],
    [["ndjson"], ["calculation.ndjson"]],
    [["json", "html"], ["calculation.json", "html/index.html"]],
  ];
  for (const [formats, paths] of cases) {
    const { bytes } = await createCalculationArchive({ ...options, formats });
    const files = unzipSync(bytes);
    assert.deepEqual(Object.keys(files).sort(), paths);
    if (files["html/index.html"]) assert.match(strFromU8(files["html/index.html"]), /bridge-marker/);
    if (files["calculation.json"]) assert.doesNotMatch(strFromU8(files["calculation.json"]), /bridge-marker/);
  }
  await assert.rejects(createCalculationArchive({ ...options, formats: [] }), /select at least one/i);
  await assert.rejects(createCalculationArchive({ ...options, formats: ["pdf"] }), /unsupported/i);
});
