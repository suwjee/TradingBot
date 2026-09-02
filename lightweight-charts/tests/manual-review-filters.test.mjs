import test from "node:test";
import assert from "node:assert/strict";
import { webcrypto } from "node:crypto";
import vm from "node:vm";
import { buildReviewBody, reviewRecords, reviewColor, reviewColorSurface, reviewLabelColor, manualReviewFilename } from "../src/manual-review.js";
import { reviewFixture } from "./manual-review-fixture.mjs";

// Execute the exact embedded runtime with isolated DOM/storage doubles. No
// trading logic, browser profile, network or production cache is accessed.
async function harness(storage = new Map(), exportedAt = "test-export", denyStorage = false) {
  const payload = structuredClone(reviewFixture);
  payload.directions.bullish.sZones.push({ sourceTime: 1780086600, color: "blue", price: "12.0000" });
  const page = await buildReviewBody(payload, { exportedAt }, webcrypto);
  const records = reviewRecords(payload), nodes = new Map();
  const node = (values = {}) => ({ value: "", checked: false, hidden: false, textContent: "", attributes: {},
    setAttribute(key, value) { this.attributes[key] = value; }, ...values });
  for (const id of ["from", "to", "mode", "range-error", "filter-note", "report-text", "storage-note",
    "reset", "copy", "download", "empty"]) nodes.set(`#${id}`, node());
  nodes.get("#mode").value = "all";
  const events = records.map((record) => {
    const inputs = ["true", "false"].map((value) => node({ value }));
    const copy = node();
    return node({ dataset: { id: record.id, filter: record.category.key, time: record.time, label: record.label }, inputs,
      querySelector(selector) {
        if (selector === "input:checked") return inputs.find((input) => input.checked);
        if (selector === ".copy-line") return copy;
        return inputs.find((input) => selector === `input[value="${input.value}"]`);
      }, querySelectorAll() { return inputs; },
    });
  });
  const filters = [...new Set(records.map((record) => record.category.key))].map((value) => node({ value, checked: true }));
  const references = events.map((event) => node({ dataset: event.dataset }));
  const days = [...new Set(records.map((record) => record.time.slice(0, 10)))].map((date) => {
    const count = node();
    return node({ open: true, querySelectorAll() { return events.filter((event) => !event.hidden && event.dataset.time.startsWith(date)); }, querySelector() { return count; } });
  });
  const collection = node({ querySelector() { return references.find((item) => !item.hidden); } });
  const context = vm.createContext({ console, Set, Date, Blob, URL, setTimeout,
    document: { body: { dataset: { payloadHash: "fixture-hash", reviewId: exportedAt } },
      querySelector(selector) { return nodes.get(selector); },
      querySelectorAll(selector) { return ({ ".event": events, ".reference-row": references, ".category-filter": filters, ".day": days, ".collection": [collection] })[selector]; } },
    localStorage: { getItem(key) { if (denyStorage) throw Error("blocked"); return storage.get(key); },
      setItem(key, value) { if (denyStorage) throw Error("blocked"); storage.set(key, value); },
      removeItem(key) { if (denyStorage) throw Error("blocked"); storage.delete(key); } },
    window: {},
  });
  const script = page.runtime;
  vm.runInContext(`(${script})();`, context);
  return { html: page.body, payload, events, filters, references, days, collection, nodes, storage,
    mark(event, status) { event.inputs.forEach((input) => { input.checked = input.value === status; }); event.inputs[0].onchange(); } };
}

test("A plus S blue filters both timeline and collections without deleting any payload data", async () => {
  const h = await harness();
  h.filters.forEach((filter) => { filter.checked = false; filter.onchange(); });
  assert(h.events.every((event) => event.hidden));
  assert.equal(h.nodes.get("#empty").hidden, false);
  for (const filter of h.filters) if (["aZones", "sZones:blue"].includes(filter.value)) { filter.checked = true; filter.onchange(); }
  assert.deepEqual(h.events.filter((event) => !event.hidden).map((event) => event.dataset.filter), ["aZones", "aZones", "sZones:blue"]);
  assert.equal(h.references.filter((row) => !row.hidden).length, 3);
  assert.equal(h.events.length, 19);
  const encoded = h.html.match(/SHA-256 [0-9a-f]+<\/summary><pre>([\s\S]*?)<\/pre><\/details>/)[1];
  const embedded = JSON.parse(encoded.replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&amp;/g, "&"));
  assert.deepEqual(embedded, h.payload);
});

test("True and False counts include all reviewed records and preserve unrelated storage", async () => {
  const h = await harness(new Map([["unrelated", "preserve"]]));
  h.mark(h.events[0], "true"); h.mark(h.events.at(-1), "false");
  assert.match(h.nodes.get("#filter-note").textContent, /1 True .* 1 False/);
  assert.match(h.nodes.get("#report-text").value, /\| True/);
  assert.match(h.nodes.get("#report-text").value, /\| False/);
  assert.equal(h.storage.get("unrelated"), "preserve");
  const reopened = await harness(h.storage);
  assert.equal(reopened.events[0].inputs[0].checked, true);
  assert.equal(reopened.events.at(-1).inputs[1].checked, true);
});

test("reference day groups, time boundaries and status report compose with filters", async () => {
  const h = await harness();
  assert.equal(h.days.length, 3); // Original records cross Tehran midnight.
  assert.equal((h.html.match(/<details class="day" open>/g) || []).length, 3);
  h.mark(h.events[0], "true"); h.mark(h.events.at(-1), "false");
  h.nodes.get("#from").value = h.events.at(-1).dataset.time;
  h.nodes.get("#from").oninput();
  assert.equal(h.events.filter((event) => !event.hidden).length, 1);
  assert.equal(h.days[0].hidden, true);
  assert.match(h.nodes.get("#report-text").value, /False/);
  assert.doesNotMatch(h.nodes.get("#report-text").value, /True/);
  h.nodes.get("#to").value = "2000-01-01 00:00:00"; h.nodes.get("#to").oninput();
  assert.equal(h.nodes.get("#range-error").hidden, false);
  h.nodes.get("#reset").onclick(); assert(h.events.every((event) => !event.hidden));
});

test("reviews restore for the same export but not another file; unavailable storage is explicit", async () => {
  const h = await harness(); h.mark(h.events[0], "true");
  const restored = await harness(h.storage);
  assert.equal(restored.events[0].inputs[0].checked, true);
  const separate = await harness(h.storage, "another-export");
  assert.equal(separate.events[0].inputs[0].checked, false);
  const blocked = await harness(new Map(), "blocked", true);
  assert.match(blocked.nodes.get("#storage-note").textContent, /storage unavailable/);
});

test("exact chart colors, current settings and customized object colors are respected safely", () => {
  const records = reviewRecords(reviewFixture);
  const a = records.find((record) => record.group === "aZones" && record.direction === "bullish");
  const s = records.find((record) => record.group === "sZones");
  assert.equal(reviewColor(a), "#7c3aed"); assert.equal(reviewColor(s), "#f23645");
  assert.equal(reviewColor(records[0]), "#22c55e");
  assert.equal(reviewColor(a, { settings: { aColor: "#123456" } }), "#123456");
  assert.equal(reviewColor(a, { settings: { aColor: "#123456" }, indicatorObjects: [{ id: "indicator:bullish:a:0", customized: true, color: "#abcdef" }] }), "#abcdef");
  assert.equal(reviewColor(a, { settings: { aColor: 'red; background:url(https://invalid)' } }), "#7c3aed");
  assert.equal(reviewColorSurface("#ffffff"), "#f3f5f7");
  assert.equal(reviewColorSurface("#7c3aed"), "#f3f5f7");
  assert.equal(reviewLabelColor(a, reviewColor(a)), "#7c3aed");
  assert.equal(reviewLabelColor(records.find((record) => record.group === "reactions"), "#22c55e"), "#111827");
  assert.equal(reviewLabelColor(records.find((record) => record.group === "orderAudit"), "#8a8f98"), "#111827");
});

test("filename uses system wall time, zero padding and the requested separator format", () => {
  const date = new Date(2026, 6, 29, 11, 12, 9);
  assert.equal(manualReviewFilename(date), "manualTest-2026_07_29 11_12_09.txt");
  assert.equal(manualReviewFilename(date, "txt"), "manualTest-2026_07_29 11_12_09.txt");
});
