import { ENGINE_CONTRACTS } from "./content/content.js";
import { ALGORITHM_COPY, FAMILY_SUMMARIES_FA, STOP_RULES_FA, TYPE_STEPS_FA } from "./content/i18n.js";
import { MODULE_SUMMARIES } from "./content/module-summaries.js";
import { TYPE_MODULE_SUMMARIES } from "./content/type-module-summaries.js";
import { CALCULATION_GUIDES } from "./content/calculation-guides.js";
import { BRIDGE_OBJECT_CATALOG } from "./content/object-catalog.js";
import {
  BRIDGE_CALCULATION_GUIDE,
  BRIDGE_COPY,
  BRIDGE_ENVELOPE_CATALOG,
  BRIDGE_FAMILY_CONTRACT,
  BRIDGE_MODULE_SUMMARY,
  BRIDGE_TYPE_MODULE_SUMMARIES,
} from "./content/bridge-content.js";
import { GLOSSARY_ENTRIES, REACTION_GEOMETRY_REFERENCE } from "./content/glossary.js";
import { isBearishMirrorFamily, mirrorDirectionalText } from "./mirror.js";
import { mountWorkspaceHeader, restoreWorkspaceHeader } from "../ui/workspace-state.js";
import "./styles.css";

const LANGUAGE_KEY = "qg:algorithm-language";
const SIDEBAR_KEY = "qg:algorithm-sidebar-collapsed";
const DIRECTION_KEY = "qg:algorithm-direction";
const CONTRACTS = Object.freeze({ ...ENGINE_CONTRACTS, bridge: BRIDGE_FAMILY_CONTRACT });
const SUMMARIES = Object.freeze({ ...MODULE_SUMMARIES, bridge: BRIDGE_MODULE_SUMMARY });
const TYPE_SUMMARIES = Object.freeze({ ...TYPE_MODULE_SUMMARIES, bridge: BRIDGE_TYPE_MODULE_SUMMARIES });
const GUIDES = Object.freeze({ ...CALCULATION_GUIDES, bridge: BRIDGE_CALCULATION_GUIDE });
const SUMMARY_FA = Object.freeze({ ...FAMILY_SUMMARIES_FA, bridge: BRIDGE_COPY.summaryFa });
const STOP_FA = Object.freeze({ ...STOP_RULES_FA, bridge: BRIDGE_COPY.stopFa });

const FAMILY_ORDER = Object.freeze([
  { id: "reaction", name: "Reaction", objectId: "reaction", summary: "Builds a confirmed bullish box from First, BoxTop, BoxBottom, and a strict upper break.", required: ["Main Candle[]", "Lower Candle[]", "Decimal OHLC", "GREEN/RED classification", "Candidate state"], creates: ["Reaction", "optional same-candle Reset", "First/Box/Break provenance"] },
  { id: "reset", name: "Reaction Reset", objectId: "reset", summary: "Records the first strict Low below the confirmed bullish Reaction BoxBottom.", required: ["confirmed Reaction", "Reaction.BoxBottom", "Main Candle[]", "Lower Candle[]", "owner First"], creates: ["Reset", "secondTime", "brokenLevel", "fromFirstIndex"] },
  { id: "blue_line", name: "Blue Line", objectId: "blue_line", summary: "Builds Scale Blue and Reset Blue and maintains spacing; A later derives private strict-stop state from valid lines.", required: ["Reaction[]", "Reset[]", "Main Candle[]", "Lower Candle[]", "Decimal('0.618')", "spacing state"], creates: ["public calculation-valid BlueLine", "internal invalid Reset Blue", "BlueState input derived privately by A"] },
  { id: "a", name: "A", objectId: "a", summary: "Pairs eligible Blue states, resolves the first strict trigger, and confirms A with a bullish Reaction.", required: ["calculation-valid BlueLine[]", "internal invalid Reset Blue[]", "bullish Reaction[]", "Main Candle[]", "Lower Candle[]"], creates: ["AZone", "cycle_after_index", "trigger/source/Reaction provenance"] },
  { id: "s_red", name: "S red", objectId: "s", summary: "Creates red S when the opposite Order stop happens before the bullish candidate crossing.", required: ["eligible AZone[]", "bullish Reaction[]", "opposite Order geometry", "opposite Reset[]", "BlueLine[] evidence", "Main/Lower Candle[]"], creates: ["red SZone", "parent-stop Order cause", "red E parent"] },
  { id: "s_blue", name: "S blue", objectId: "s", summary: "Creates blue S when the candidate wins with evidence, or when the protected Type 3 route completes.", required: ["eligible AZone[]", "bullish Reaction[]", "opposite Order geometry", "opposite Reset[]", "Reset Blue evidence", "Main/Lower Candle[]"], creates: ["blue SZone", "nullable Order provenance", "blue E parent"] },
  { id: "e_blue", name: "E blue", objectId: "e", summary: "Extends the accepted blue S/E family after a strict parent stop and an accepted Order stop.", required: ["accepted blue S/E parent", "opposite Order geometry", "accepted Order ledger", "sequence reset map", "Main/Lower Candle[]"], creates: ["blue EZone", "Order audit entry", "recursive parent", "StopAll input"] },
  { id: "e_red", name: "E red", objectId: "e", summary: "Extends the accepted red S/E family and preserves red-family active-state priority.", required: ["accepted red S/E parent", "opposite Order geometry", "accepted Order ledger", "sequence reset map", "Main/Lower Candle[]"], creates: ["red EZone", "Order audit entry", "recursive parent", "StopAll input"] },
  { id: "order_audit", name: "Order Audit", objectId: "order_audit", summary: "Keeps one row per physical opposite Order and merges every accepted formation cause.", required: ["S Order audit", "accepted E Order ledger", "accepted A/S/E/StopAll parents", "First/Break identity"], creates: ["OrderAudit row", "deduplicated causes[]", "complete physical Order geometry"] },
  { id: "stop_all", name: "StopAll", objectId: "stop_all", summary: "Turns a decisive E into StopAll when a sequence-group or continuation gate has strictly stopped.", required: ["visible SZone[]", "accepted EZone[]", "s_key/s_count", "e_key/e_count", "active StopAll[]", "Lower Candle[]"], creates: ["StopAll", "sequence reset", "inherited Order lineage", "strict StopAll stop"] },
]);

const BRIDGE_REFERENCE = Object.freeze({ id: "bridge", name: "Bridge", objectId: null, summary: "Isolates the requested range, runs the bullish dependency chain, reconciles ownership, and serializes the final payload.", required: ["source JSON", "engine paths", "timeframe", "from_time/to_time", "module switches", "direction='bullish'"], creates: ["payload envelope", "directions.bullish", "8 collections", "timings"] });
const ROUTED_FAMILIES = Object.freeze([...FAMILY_ORDER, BRIDGE_REFERENCE]);
const DOCUMENTED_COLLECTION_SLOTS = 185;

const STOP_RULES = Object.freeze({
  reaction: { en: "A confirmed Reaction stays in history. In its Break candle, Reset needs a later lower-second Low strictly below BoxBottom. On later candles, the first main Low below BoxBottom resets it; lower seconds are used only if a Mode-B break competes.", code: "reset = later_second_after_break or first_later_main_low_below_box_bottom" },
  reset: { en: "Reset is an event, not a persistent line. It clears the ordinary candidate and opens direct recovery after secondTime.", code: "ordinary_candidate = None\nrecovery_start = reset.second_time" },
  blue_line: { en: "Blue publishes no stop field. For A only, a private BlueState stops on the first lower-second Low strictly below sourceExtreme; Reset Blue scanning starts at sourceTime + timeframe.", code: "private_blue_state.stop = first_lower_second(after=stop_scan_start, where=low < blue.source_extreme)" },
  a: { en: "A stops on the first lower-second Low strictly below A.price at or after exact confirmation. A next confirmation at or before that stop closes the older S window.", code: "a_stop = first_lower_second(from=a.confirmation_event, where=low < a.price)" },
  s_red: { en: "Red S stops on the first lower-second Low strictly below S.price at or after its decision; the exact event can open the next red E lifecycle.", code: "parent_stop = first_lower_second(from=s.decision_event, where=low < s.price)" },
  s_blue: { en: "Blue S, including Type 3, stops on the first lower-second Low strictly below S.price at or after its decision.", code: "parent_stop = first_lower_second(from=s.decision_event, where=low < s.price)" },
  e_blue: { en: "Blue E stops on the first lower-second Low strictly below E.price at or after its decision. The stopped parent stays available for lineage.", code: "parent_stop = first_lower_second(from=e.decision_event, where=low < e.price)" },
  e_red: { en: "Red E stops on the first lower-second Low strictly below E.price at or after its decision; red remains the dominant active family.", code: "parent_stop = first_lower_second(from=e.decision_event, where=low < e.price)" },
  order_audit: { en: "The opposite Order used by the bullish path stops on the first lower-second High strictly above stopLevel at or after confirmation; equality is not a stop.", code: "order_stop = first_lower_second(from=order.confirmation, where=high > order.stop_level)" },
  stop_all: { en: "StopAll stops on the first lower-second Low strictly below StopAll.price at or after its decision. A later decisive E can create max(stopped number) + 1.", code: "stop = first_lower_second(from=stop_all.decision_event, where=low < stop_all.price)" },
  bridge: { en: "Bridge publishes no new trading behavior. It filters invalid, shadowed, or out-of-range rows before serialization.", code: "public_payload = serialize(accepted_ownership_inside_isolated_range)" },
});

const TYPE_OUTPUT_OVERRIDES = Object.freeze({
  type3: ["sZones (color=blue, formationType=type3)", "Reset provenance", "nullable Order fields"],
  internal_invalid_reset: ["internal BlueLine (calculation_valid=False)", "special A provenance input", "no public blueLines row"],
  same_candle: ["resets row", "exact secondTime after Break event", "direct recovery state"],
  continuation: ["stopAlls row with number >= 2", "stopped prior StopAll history", "new E sequence reset"],
});

const AUDITED_FILES = Object.freeze([
  { path: "engine/pipeline/reaction_engine.py", lines: 2686, version: "9.3.0" },
  { path: "engine/pipeline/blue_line_detector.py", lines: 382, version: "2.0.1 Bridge contract" },
  { path: "engine/pipeline/a_zone_detector.py", lines: 752, version: "1.4.0" },
  { path: "engine/pipeline/s_zone_detector.py", lines: 1238, version: "4.1.3" },
  { path: "engine/pipeline/e_zone_detector.py", lines: 2208, version: "6.1.3" },
  { path: "engine/pipeline/lifecycle_engine.py", lines: 322, version: "1.3.0" },
  { path: "engine/bridge/trading_pipeline.py", lines: 1730, version: "payload authority" },
]);

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (character) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[character]);
}

function persianHtml(value) {
  return String(value ?? "").split(/([A-Za-z][A-Za-z0-9_.\-/]*(?:\([^()\n]*\))?)/g)
    .map((part, index) => index % 2 ? `<bdi dir="ltr">${escapeHtml(part)}</bdi>` : escapeHtml(part)).join("");
}

function localized(en, fa) {
  return `<span class="algorithm-copy algorithm-copy-en" lang="en" dir="ltr">${escapeHtml(en)}</span><span class="algorithm-copy algorithm-copy-fa" lang="fa" dir="rtl">${persianHtml(fa || en)}</span>`;
}

function definitionFor(id) {
  const value = CONTRACTS[id];
  return value && Array.isArray(value.contract) && Array.isArray(value.types) ? value : { contract: [], types: [] };
}

function objectsFor(family) {
  if (family.id === "bridge") return BRIDGE_ENVELOPE_CATALOG;
  const object = BRIDGE_OBJECT_CATALOG.find((item) => item.id === family.objectId);
  return object ? [object] : [];
}

function typeSteps(family, type) {
  const en = (type.steps || []).map((item) => typeof item === "string" ? item : item.en);
  const local = TYPE_STEPS_FA[`${family.id}.${type.id}`];
  const fa = local || (type.steps || []).map((item) => typeof item === "string" ? item : item.fa);
  return { en, fa };
}

function technicalList(items) {
  return `<div class="algorithm-code-list">${items.map((item) => `<code>${escapeHtml(item)}</code>`).join("")}</div>`;
}

function sourceCodes(value) {
  const items = Array.isArray(value) ? value : String(value || "").split(/[;,]/);
  return items.map((item) => String(item).trim()).filter(Boolean).map((item) => `<code>${escapeHtml(item)}</code>`).join("");
}

const PYTHON_KEYWORDS = new Set(["and", "as", "assert", "break", "class", "continue", "def", "elif", "else", "for", "from", "if", "import", "in", "is", "lambda", "None", "not", "or", "pass", "raise", "return", "True", "False", "try", "while", "with", "yield"]);

function highlightCodeLine(line) {
  const tokenPattern = /(#[^\n]*|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|\b\d+(?:\.\d+)?\b|\b[A-Za-z_][A-Za-z0-9_]*\b)/g;
  let html = "";
  let cursor = 0;
  for (const match of line.matchAll(tokenPattern)) {
    const token = match[0];
    const start = match.index ?? cursor;
    html += escapeHtml(line.slice(cursor, start));
    const className = token.startsWith("#") ? "algorithm-token-comment" : (/^[\"']/.test(token) ? "algorithm-token-string" : (/^\d/.test(token) ? "algorithm-token-number" : (PYTHON_KEYWORDS.has(token) ? "algorithm-token-keyword" : "algorithm-token-name")));
    html += `<span class="${className}">${escapeHtml(token)}</span>`;
    cursor = start + token.length;
  }
  return html + escapeHtml(line.slice(cursor));
}

function ideCode(value) {
  return String(value || "").split("\n").map((line) => `<span class="algorithm-code-line"><span class="algorithm-code-content">${highlightCodeLine(line)}</span></span>`).join("\n");
}

function ideCodeBlock(value) {
  return `<pre class="algorithm-ide" aria-readonly="true" tabindex="0"><code>${ideCode(value)}</code></pre>`;
}

function ruleCode(value) {
  return `<pre class="algorithm-rule-code"><code>${escapeHtml(value)}</code></pre>`;
}

function searchable(values) {
  return escapeHtml(values.flat(Infinity).filter(Boolean).map((value) => typeof value === "object" ? JSON.stringify(value) : value).join(" ").toLocaleLowerCase());
}

function tagCategory(tag) {
  const value = String(tag).toLowerCase();
  if (value.includes("reaction")) return "reaction";
  if (value.includes("reset")) return "reset";
  if (value.includes("blue")) return "blue-line";
  if (value === "a" || value.includes("azone")) return "a";
  if (value === "s" || value.includes("szone")) return "s";
  if (value === "e" || value.includes("ezone")) return "e";
  if (value.includes("audit") || value === "order") return "order-audit";
  if (value.includes("stopall") || value.includes("stop-all")) return "stop-all";
  if (value.includes("bridge") || value.includes("payload")) return "bridge";
  if (["time", "decision", "break", "trigger", "gate", "range", "performance"].includes(value)) return "time";
  if (["price", "fibonacci", "strike"].includes(value)) return "value";
  if (["source", "ownership", "parent", "cause", "continuation"].includes(value)) return "provenance";
  return "state";
}

function tagPills(tags) {
  return `<div class="algorithm-tags">${(tags || []).map((tag) => `<span class="algorithm-tag" data-tag-category="${tagCategory(tag)}">${escapeHtml(tag)}</span>`).join("")}</div>`;
}

function contractSequence(definition) {
  return definition.contract.map((item, index) => `<li><span>${index + 1}</span><div><p>${localized(item.en, item.fa)}</p>${ruleCode(item.code)}<div class="algorithm-row-source">${sourceCodes(item.source)}</div></div></li>`).join("");
}

function typeArticle(family, type, typeIndex) {
  const anchor = `algorithm-${family.id}-${type.id}`;
  const nameEn = type.names?.en || type.id;
  const nameFa = type.names?.fa || nameEn;
  const steps = typeSteps(family, type);
  const detection = steps.en.map((text, index) => `<li><span>${index + 1}</span><p>${localized(text, steps.fa[index] || text)}</p></li>`).join("");
  const output = TYPE_OUTPUT_OVERRIDES[type.id] || type.output || family.creates;
  const stop = STOP_RULES[family.id];
  const search = searchable([family.name, type.id, type.names?.en, type.names?.fa, type.entry?.en, type.entry?.fa, type.reject?.en, type.reject?.fa, steps.en, steps.fa, output]);
  return `<article class="algorithm-type" id="${anchor}" data-type-panel="${escapeHtml(type.id)}" data-search="${search}" tabindex="-1">
    <header class="algorithm-type-header"><div><span>${family.index}.${typeIndex + 1}</span><h3>${localized(nameEn, nameFa)}</h3></div><a href="#${anchor}" data-label-en="Link to ${escapeHtml(nameEn)}" data-label-fa="لینک مستقیم به ${escapeHtml(nameFa)}" aria-label="Link to ${escapeHtml(nameEn)}">#</a></header>
    <dl class="algorithm-definitions">
      <div><dt>${localized("Entry rule", "شرط شروع")}</dt><dd>${localized(type.entry?.en || "No separate entry rule.", type.entry?.fa || "شرط شروع جدا ندارد.")}</dd></div>
      <div><dt>${localized("Rejected when", "چه وقت رد می‌شود")}</dt><dd>${localized(type.reject?.en || "A maintained guard rejects it.", type.reject?.fa || "یکی از guardهای اصلی آن را رد کند.")}</dd></div>
    </dl>
    <section class="algorithm-type-section"><h4>${localized("Detection sequence", "ترتیب تشخیص")}</h4><ol class="algorithm-detection-list">${detection}</ol></section>
    <section class="algorithm-type-section algorithm-stop-rule"><h4>${localized("Stop / reset", "قانون stop / reset")}</h4><p>${localized(stop.en, STOP_FA[family.id])}</p>${ruleCode(stop.code)}</section>
    <dl class="algorithm-interface">
      <div><dt>${localized("Required objects", "ورودی‌های لازم")}</dt><dd>${technicalList(family.required)}</dd></div>
      <div><dt>${localized("Created / updated", "خروجی یا تغییر")}</dt><dd>${technicalList(output)}</dd></div>
    </dl>
    <details class="algorithm-disclosure algorithm-sources"><summary>${localized("Verified source", "سورس بررسی‌شده")}</summary><div>${sourceCodes(type.source)}</div></details>
  </article>`;
}

function codeSummary({ family, type = null, item, icon, familyOnly = false }) {
  if (!item) return "";
  const titleEn = type ? `${type.names?.en || type.id} Python-like summary` : `${family.name} Python-like module summary`;
  const titleFa = type ? `خلاصه شبه‌پایتون ${type.names?.fa || type.names?.en || type.id}` : `خلاصه شبه‌پایتون ماژول ${family.name}`;
  const typeAttr = type ? ` data-type-panel="${escapeHtml(type.id)}"` : "";
  const familyAttr = familyOnly ? " data-family-only" : "";
  return `<details class="algorithm-code-summary"${typeAttr}${familyAttr}>
    <summary><span>${icon("terminal", 15)} ${localized(titleEn, titleFa)}</span><em>${localized("Pseudocode", "شبه‌کد")}</em></summary>
    <div class="algorithm-code-summary-body">
      <div class="algorithm-module-code" data-code-block>${ideCodeBlock(item.code)}<button type="button" data-copy-code data-label-en="Copy ${escapeHtml(titleEn)}" data-label-fa="کپی ${escapeHtml(titleFa)}" aria-label="Copy ${escapeHtml(titleEn)}">${icon("copy", 14)}<span data-copy-label>${localized("Copy", "کپی")}</span></button></div>
      <footer><strong>${localized("Source", "منبع")}</strong><div>${sourceCodes(item.sources)}</div></footer>
    </div>
  </details>`;
}

function moduleSummaries(family, icon) {
  const definition = definitionFor(family.id);
  const typeItems = TYPE_SUMMARIES[family.id] || {};
  return `<section class="algorithm-summary-stack">
    ${codeSummary({ family, item: SUMMARIES[family.id], icon, familyOnly: true })}
    ${definition.types.map((type) => codeSummary({ family, type, item: typeItems[type.id], icon })).join("")}
  </section>`;
}

function calculationGuide(family) {
  const guide = GUIDES[family.id];
  if (!guide) return "";
  const definition = definitionFor(family.id);
  const phases = guide.phases.map((phase, index) => `<li><span>${index + 1}</span><div><p>${localized(phase.en, phase.fa)}</p><code class="algorithm-expression">${escapeHtml(phase.code)}</code></div></li>`).join("");
  const typeGuides = definition.types.map((type, typeIndex) => {
    const steps = typeSteps(family, type);
    const output = TYPE_OUTPUT_OVERRIDES[type.id] || type.output || family.creates;
    const ordered = steps.en.map((step, index) => `<li><span>${index + 1}</span><p>${localized(step, steps.fa[index] || step)}</p></li>`).join("");
    return `<article class="algorithm-type-guide" data-type-panel="${escapeHtml(type.id)}">
      <header><span>${family.index}.${typeIndex + 1}</span><h4>${localized(type.names?.en || type.id, type.names?.fa || type.names?.en || type.id)}</h4></header>
      <dl><div><dt>${localized("Start when", "شروع وقتی")}</dt><dd>${localized(type.entry?.en || "The family gate is open.", type.entry?.fa || "gate خانواده باز است.")}</dd></div><div><dt>${localized("Reject when", "رد وقتی")}</dt><dd>${localized(type.reject?.en || "A maintained guard fails.", type.reject?.fa || "یکی از guardهای اصلی برقرار نباشد.")}</dd></div></dl>
      <ol>${ordered}</ol>
      <footer><strong>${localized("Final output", "خروجی نهایی")}</strong>${technicalList(output)}</footer>
    </article>`;
  }).join("");
  return `<section class="algorithm-calculation-guide">
    <div class="algorithm-family-guide" data-family-only>
      <header><span>${localized("CALCULATION GUIDE", "راهنمای محاسبه")}</span><h3>${localized(guide.title, guide.fa)}</h3></header>
      <ol>${phases}</ol>
      <div class="algorithm-guide-columns"><section><h4>${localized("Checks before output", "چک‌های قبل از خروجی")}</h4>${technicalList(guide.checks)}</section><section><h4>${localized("Produced / serialized", "چیزهایی که ساخته یا serialize می‌شوند")}</h4>${technicalList(guide.output)}</section></div>
    </div>
    <section class="algorithm-type-guides"><header><span>${localized("TYPE CHEAT SHEETS", "چیت‌شیت هر نوع")}</span><p>${localized("Read each branch in the exact order in which its gates and calculations are checked.", "هر شاخه را به همان ترتیبی بخوان که gateها و محاسبات آن بررسی می‌شوند.")}</p></header>${typeGuides}</section>
  </section>`;
}

function fieldRows(object, language) {
  return object.fields.map((field) => {
    const meaning = language === "fa" ? persianHtml(field.names.fa) : escapeHtml(field.names.en);
    const cells = language === "fa"
      ? `<th class="algorithm-field-cell"><code>${escapeHtml(field.id)}</code></th><td><code>${escapeHtml(field.type)}</code></td><td>${tagPills(field.tags)}</td><td class="algorithm-meaning-cell" lang="fa" dir="rtl">${meaning}</td>`
      : `<th class="algorithm-field-cell"><code>${escapeHtml(field.id)}</code></th><td><code>${escapeHtml(field.type)}</code></td><td class="algorithm-meaning-cell">${meaning}</td><td>${tagPills(field.tags)}</td>`;
    return `<tr>${cells}</tr>`;
  }).join("");
}

function objectTable(object) {
  return `<section class="algorithm-object-table">
    <header><div><h4>${localized(object.names.en, object.names.fa)}</h4><p>${localized(object.description.en, object.description.fa)}</p></div><code>${escapeHtml(object.collection)}</code></header>
    <div class="algorithm-table-wrap" tabindex="0">
      <table class="algorithm-table-en"><thead><tr><th>Field</th><th>Type</th><th>Meaning</th><th>Tags</th></tr></thead><tbody>${fieldRows(object, "en")}</tbody></table>
      <table class="algorithm-table-fa" lang="fa" dir="rtl"><thead><tr><th>Field</th><th>Type</th><th>Tags</th><th>معنی</th></tr></thead><tbody>${fieldRows(object, "fa")}</tbody></table>
    </div>
  </section>`;
}

function objectContracts(family, icon) {
  const objects = family.id === "bridge" ? BRIDGE_OBJECT_CATALOG : objectsFor(family);
  const count = objects.reduce((total, object) => total + object.fields.length, 0);
  if (!objects.length) return "";
  const envelope = family.id === "bridge" ? `<details class="algorithm-object-contract" data-family-only>
    <summary><span>${icon("data_object", 15)} ${localized("Payload envelope and nested contracts", "قرارداد envelope و فیلدهای nested")}</span><em>${BRIDGE_ENVELOPE_CATALOG.reduce((total, object) => total + object.fields.length, 0)} ${localized("fields", "فیلد")}</em></summary>
    <div>${BRIDGE_ENVELOPE_CATALOG.map(objectTable).join("")}</div>
  </details>` : "";
  return `<details class="algorithm-object-contract" data-family-only>
    <summary><span>${icon("database", 15)} ${localized(family.id === "bridge" ? "Eight collection contracts" : "Bridge object contract", family.id === "bridge" ? "قرارداد هشت collection" : "فیلدهای خروجی Bridge")}</span><em>${count} ${localized("unique fields", "فیلد یکتا")}</em></summary>
    <div>${objects.map(objectTable).join("")}</div>
  </details>${envelope}`;
}

function familySection(family, familyIndex, icon) {
  const definition = definitionFor(family.id);
  const displayIndex = typeof familyIndex === "number" ? familyIndex + 1 : familyIndex;
  const withIndex = { ...family, index: displayIndex };
  const contractSources = definition.contract.map((item, index) => `<li><span>${index + 1}</span>${sourceCodes(item.source)}</li>`).join("");
  const objectSearch = objectsFor(family).flatMap((object) => [object.collection, object.names.en, object.names.fa, object.fields.flatMap((field) => [field.id, field.names.en, field.names.fa, field.tags])]);
  const guide = GUIDES[family.id];
  const search = searchable([family.name, family.summary, SUMMARY_FA[family.id], definition.contract, definition.types, objectSearch, guide?.phases, guide?.checks, guide?.output]);
  return `<section class="algorithm-family" id="algorithm-${family.id}" data-family="${family.id}" data-search="${search}" tabindex="-1" hidden>
    <header class="algorithm-family-header"><span>${typeof displayIndex === "number" ? String(displayIndex).padStart(2, "0") : escapeHtml(displayIndex)}</span><div><p>${localized(family.id === "bridge" ? "SUPPORTING RUNTIME" : "BULLISH PIPELINE", family.id === "bridge" ? "زیرساخت پشتیبان" : "روند صعودی")}</p><h2>${escapeHtml(family.name)}</h2><strong>${localized(family.summary, SUMMARY_FA[family.id])}</strong></div></header>
    <section class="algorithm-contract" data-family-only>
      <header><div><span>${localized("SOURCE CONTRACT", "قرارداد بر اساس سورس")}</span><h3>${localized("Current calculation flow", "روند فعلی محاسبه")}</h3></div><code>${escapeHtml(objectsFor(family)[0]?.collection || "internal")}</code></header>
      <ol class="algorithm-contract-sequence">${contractSequence(definition)}</ol>
      <details class="algorithm-disclosure algorithm-sources"><summary>${localized("Contract sources", "منابع قرارداد")}</summary><ol>${contractSources}</ol></details>
    </section>
    <dl class="algorithm-family-interface" data-family-only><div><dt>${localized("Family inputs", "ورودی‌های خانواده")}</dt><dd>${technicalList(family.required)}</dd></div><div><dt>${localized("Family outputs", "خروجی‌های خانواده")}</dt><dd>${technicalList(family.creates)}</dd></div></dl>
    <div class="algorithm-types">${definition.types.map((item, index) => typeArticle(withIndex, item, index)).join("")}</div>
    ${objectContracts(withIndex, icon)}
    ${moduleSummaries(withIndex, icon)}
    ${calculationGuide(withIndex)}
  </section>`;
}

function reactionGeometryPage(icon) {
  const reference = REACTION_GEOMETRY_REFERENCE;
  const phases = reference.phases.map((phase, index) => `<li><span>${index + 1}</span><div><p>${localized(phase.en, phase.fa)}</p><code class="algorithm-expression">${escapeHtml(phase.code)}</code></div></li>`).join("");
  const search = searchable([reference.title, reference.titleFa, reference.summary, reference.summaryFa, reference.phases, reference.checks, reference.outputs, reference.sources]);
  return `<section class="algorithm-reference-page" id="algorithm-reaction-geometry" data-family="reaction" data-search="${search}" tabindex="-1" hidden>
    <header class="algorithm-family-header"><span>R2</span><div><p>${localized("SUPPORTING REFERENCE", "مرجع پشتیبان")}</p><h2>${localized(reference.title, reference.titleFa)}</h2><strong>${localized(reference.summary, reference.summaryFa)}</strong></div></header>
    ${codeSummary({ family: { name: "Reaction geometry" }, item: { code: reference.code, sources: reference.sources }, icon })}
    <section class="algorithm-calculation-guide"><div class="algorithm-family-guide"><header><span>${localized("GEOMETRY CHEAT SHEET", "چیت‌شیت هندسه")}</span><h3>${localized("How geometry reaches S, E, and Order Audit", "هندسه چگونه به S، E و Order Audit می‌رسد")}</h3></header><ol>${phases}</ol><div class="algorithm-guide-columns"><section><h4>${localized("Required checks", "چک‌های لازم")}</h4>${technicalList(reference.checks)}</section><section><h4>${localized("Produced objects", "آبجکت‌های خروجی")}</h4>${technicalList(reference.outputs)}</section></div></div></section>
  </section>`;
}

function glossaryPage() {
  const rows = GLOSSARY_ENTRIES.map((item) => `<tr><th>${escapeHtml(item.term)}</th><td>${sourceCodes(item.code)}</td><td>${localized(item.en, item.fa)}</td><td>${technicalList(item.usedIn)}</td></tr>`).join("");
  const search = searchable(GLOSSARY_ENTRIES.flatMap((item) => [item.term, item.code, item.en, item.fa, item.usedIn]));
  return `<section class="algorithm-reference-page algorithm-glossary" id="algorithm-glossary" data-family="bridge" data-search="${search}" tabindex="-1" hidden>
    <header class="algorithm-family-header"><span>R3</span><div><p>${localized("TERMS AND EXACT CODE NAMES", "واژه‌ها و نام دقیق در کد")}</p><h2>${localized("Glossary", "واژه‌نامه")}</h2><strong>${localized("Every user-friendly English alias used by the summaries maps back to maintained Python or Bridge names here.", "هر نام انگلیسی ساده‌شده در summaryها در این جدول به نام اصلی Python یا Bridge برمی‌گردد.")}</strong></div></header>
    <div class="algorithm-table-wrap" tabindex="0"><table><thead><tr><th>${localized("Friendly term", "واژه ساده")}</th><th>${localized("Exact code equivalent", "معادل دقیق در کد")}</th><th>${localized("Meaning", "معنی و کاربرد")}</th><th>${localized("Used in", "محل استفاده")}</th></tr></thead><tbody>${rows}</tbody></table></div>
  </section>`;
}

function overview() {
  const typeCount = FAMILY_ORDER.reduce((count, family) => count + definitionFor(family.id).types.length, 0);
  const collectionFieldCount = BRIDGE_OBJECT_CATALOG.reduce((count, object) => count + object.fields.length, 0);
  const envelopeFieldCount = BRIDGE_ENVELOPE_CATALOG.reduce((count, object) => count + object.fields.length, 0);
  const lineCount = AUDITED_FILES.reduce((count, file) => count + file.lines, 0);
  const fileList = AUDITED_FILES.map((file) => `<li><code>${escapeHtml(file.path)}</code><span>${file.lines.toLocaleString("en-US")} lines · ${escapeHtml(file.version)}</span></li>`).join("");
  const pipeline = FAMILY_ORDER.map((family, index) => `<li data-family="${family.id}"><span>${index + 1}</span><strong>${family.name}</strong></li>`).join("");
  return `<section class="algorithm-overview" id="algorithm-overview" data-search="${searchable(["overview", "Decimal", "strict chronology", "ownership", "bullish pipeline", ALGORITHM_COPY.overview.fa])}" tabindex="-1">
    <span class="algorithm-eyebrow">${localized("BULLISH ONLY · PYTHON IS AUTHORITATIVE", "فقط روند صعودی · مرجع اصلی Python است")}</span>
    <h1>${localized("How the bullish indicator pipeline works", "روند صعودی اندیکاتور دقیقاً چطور کار می‌کند")}</h1>
    <p>${localized(ALGORITHM_COPY.overview.en, ALGORITHM_COPY.overview.fa)}</p>
    <dl class="algorithm-overview-stats">
      <div><dt>${FAMILY_ORDER.length}</dt><dd>${localized("algorithm families", "خانواده الگوریتم")}</dd></div><div><dt>${typeCount}</dt><dd>${localized("calculation types", "نوع محاسبه")}</dd></div>
      <div><dt>${DOCUMENTED_COLLECTION_SLOTS}</dt><dd>${localized("audited collection slots", "ردیف ممیزی collection")}</dd></div><div><dt>${collectionFieldCount}</dt><dd>${localized("unique JSON collection fields", "فیلد یکتای JSON")}</dd></div>
      <div><dt>${envelopeFieldCount}</dt><dd>${localized("envelope / nested fields", "فیلد envelope و nested")}</dd></div>
      <div><dt>${AUDITED_FILES.length}</dt><dd>${localized("source files", "فایل سورس")}</dd></div><div><dt>${lineCount.toLocaleString("en-US")}</dt><dd>${localized("source lines reviewed", "خط سورس بررسی‌شده")}</dd></div>
    </dl>
    <section class="algorithm-overview-block"><h2>${localized("Execution order", "ترتیب اجرا")}</h2><ol class="algorithm-overview-pipeline">${pipeline}</ol></section>
    <section class="algorithm-overview-block algorithm-field-audit"><h2>${localized("Why 185 becomes 183 unique JSON fields", "چرا ۱۸۵ به ۱۸۳ فیلد یکتای JSON تبدیل می‌شود")}</h2><p>${localized("The earlier 185-row documentation count contained direction twice: once in A and once in S. The current Python serializers emit 183 unique collection keys. The page keeps the 185-slot audit target visible, but never presents those two repeated rows as extra runtime fields.", "شمارش مستندات قبلی با عدد ۱۸۵، فیلد direction را یک‌بار در A و یک‌بار در S تکراری شمرده بود. serializerهای فعلی Python در عمل ۱۸۳ کلید یکتای collection تولید می‌کنند. صفحه هدف ممیزی ۱۸۵ ردیف را شفاف نشان می‌دهد، اما آن دو ردیف تکراری را فیلد اجرایی اضافه معرفی نمی‌کند.")}</p></section>
    <section class="algorithm-overview-block"><h2>${localized("Important dependency", "وابستگی مهم")}</h2><p>${localized(ALGORITHM_COPY.dependency.en, ALGORITHM_COPY.dependency.fa)}</p></section>
    <details class="algorithm-audit-files"><summary>${localized("Reviewed calculation files", "فایل‌های محاسباتی بررسی‌شده")}</summary><ul>${fileList}</ul></details>
  </section>`;
}

function pageMarkup(icon) {
  const familyNavigation = (family, indexLabel) => {
    const definition = definitionFor(family.id);
    const familySearch = searchable([family.name, family.summary, SUMMARY_FA[family.id], definition.contract]);
    const children = definition.types.map((type, typeIndex) => `<li><a href="#algorithm-${family.id}-${type.id}" data-page-link data-search="${searchable([type.id, type.names?.en, type.names?.fa, type.entry, type.steps])}"><span>${indexLabel}.${typeIndex + 1}</span><strong>${localized(type.names?.en || type.id, type.names?.fa || type.names?.en || type.id)}</strong></a></li>`).join("");
    return `<li data-nav-family="${family.id}" data-family="${family.id}"><a href="#algorithm-${family.id}" data-page-link data-search="${familySearch}" aria-expanded="false"><i aria-hidden="true"></i><span>${indexLabel}</span><strong>${family.name}</strong><em>${definition.types.length}</em></a><ol>${children}</ol></li>`;
  };
  const navigation = FAMILY_ORDER.map((family, index) => familyNavigation(family, index + 1)).join("");
  const bridgeNavigation = familyNavigation(BRIDGE_REFERENCE, "R1");
  return `<section id="algorithmView" class="algorithm-view hidden" data-language="en" aria-labelledby="algorithmPageTitle">
    <a class="algorithm-skip-link" href="#algorithmMain">${localized("Skip navigation", "برو به متن اصلی")}</a>
    <header class="algorithm-page-header">
      <div class="algorithm-identity">
        <button id="algorithmBackToChart" class="algorithm-back" type="button" aria-label="Back to chart">${icon("chart", 15)}<span>${localized("Chart", "چارت")}</span></button>
        <button id="algorithmMenu" type="button" aria-label="Open algorithm navigation" aria-expanded="false">${icon("layers", 17)}</button>
        <span class="algorithm-mark">${icon("account_tree", 18)}</span><strong id="algorithmPageTitle">Algorithm</strong><small id="algorithmDirectionLabel">${localized("Bullish", "صعودی")}</small>
      </div>
      <label class="algorithm-search"><span class="sr-only">${localized("Search the algorithm", "جست‌وجو در الگوریتم")}</span>${icon("search", 15)}<input id="algorithmSearch" type="search" autocomplete="off" placeholder="Search a behavior, rule, or object"><button id="algorithmSearchClear" class="hidden" type="button" aria-label="Clear search">${icon("close", 14)}</button></label>
      <div class="algorithm-actions">
        <button id="algorithmCopyPage" class="algorithm-copy-page" type="button" data-label-en="Copy current page" data-label-fa="کپی کامل صفحه فعلی" aria-label="Copy current page">${icon("copy", 15)}<span class="algorithm-action-label">${localized("Copy page", "کپی صفحه")}</span></button>
        <div class="algorithm-export"><label class="sr-only" for="algorithmExportFormat">Export format</label><select id="algorithmExportFormat"><option value="html">HTML</option><option value="pdf">PDF</option></select><button id="algorithmExport" type="button">${icon("download", 15)}<span>${localized("Save", "ذخیره")}</span></button></div>
        <div class="algorithm-direction" role="group" aria-label="Algorithm direction"><button id="algorithmDirectionBullish" type="button" aria-pressed="true">${localized("Bullish", "صعودی")}</button><button id="algorithmDirectionBearish" type="button" aria-pressed="false" title="Derived directional mirror; not an independent source specification">${localized("Bearish · derived", "نزولی · مشتق‌شده")}</button></div>
        <div class="algorithm-language" role="group" aria-label="Explanation language"><button id="algorithmLanguageEnglish" type="button" aria-pressed="true">EN</button><button id="algorithmLanguagePersian" type="button" aria-pressed="false" lang="fa">فا</button></div>
        <span id="algorithmActionStatus" class="algorithm-export-status" role="status" aria-live="polite"></span>
      </div>
    </header>
    <div class="algorithm-layout">
      <button id="algorithmSidebarScrim" class="algorithm-sidebar-scrim" type="button" aria-label="Close algorithm navigation" tabindex="-1"></button>
      <aside id="algorithmSidebar" class="algorithm-sidebar" aria-label="Algorithm contents">
        <header><div><span>${localized("CONTENTS", "فهرست")}</span><strong id="algorithmPipelineLabel">${localized("Bullish pipeline", "روند صعودی")}</strong></div><button id="algorithmSidebarToggle" type="button" aria-label="Collapse algorithm navigation" aria-expanded="true">${icon("chevron", 15)}</button></header>
        <nav><a class="algorithm-overview-link" href="#algorithm-overview" data-page-link data-search="overview introduction decimal bridge"><i aria-hidden="true"></i>${icon("dashboard", 14)}<strong>${localized("Overview", "نمای کلی")}</strong></a><ol>${navigation}</ol>
          <h3 class="algorithm-nav-heading">${localized("SUPPORTING REFERENCES", "منابع پشتیبان")}</h3>
          <ol class="algorithm-reference-navigation">${bridgeNavigation}
            <li><a class="algorithm-reference-link" href="#algorithm-reaction-geometry" data-page-link data-search="reaction geometry first box break order"><i aria-hidden="true"></i><span>R2</span><strong>${localized("Reaction geometry", "هندسه Reaction")}</strong></a></li>
            <li><a class="algorithm-reference-link" href="#algorithm-glossary" data-page-link data-search="glossary terminology aliases exact code names"><i aria-hidden="true"></i><span>R3</span><strong>${localized("Glossary", "واژه‌نامه")}</strong></a></li>
          </ol><p id="algorithmSearchStatus" class="algorithm-search-status" hidden>No matching page</p></nav>
      </aside>
      <main id="algorithmMain" class="algorithm-main" tabindex="-1">${overview()}${FAMILY_ORDER.map((family, index) => familySection(family, index, icon)).join("")}${familySection(BRIDGE_REFERENCE, "R1", icon)}${reactionGeometryPage(icon)}${glossaryPage()}</main>
    </div>
  </section>`;
}

function storedLanguage() {
  try { return window.localStorage.getItem(LANGUAGE_KEY) === "fa" ? "fa" : "en"; }
  catch { return "en"; }
}

function storedSidebarState() {
  try { return window.localStorage.getItem(SIDEBAR_KEY) === "true"; }
  catch { return false; }
}

function storedDirection() {
  try { return window.localStorage.getItem(DIRECTION_KEY) === "bearish" ? "bearish" : "bullish"; }
  catch { return "bullish"; }
}

function markdownInline(node) {
  if (node.nodeType === 3) return node.nodeValue || "";
  if (node.nodeType !== 1) return "";
  const element = node;
  if (element.matches("svg, button, [aria-hidden='true']")) return "";
  if (element.tagName === "BR") return "\n";
  const children = () => [...element.childNodes].map(markdownInline).join("");
  if (element.children.length > 1 && [...element.children].every((child) => child.tagName === "CODE")) {
    return [...element.children].map((child) => markdownInline(child).trim()).join(", ");
  }
  if (element.matches(".algorithm-tags")) {
    return [...element.children].map((item) => markdownInline(item).trim()).filter(Boolean).join(", ");
  }
  if (element.tagName === "CODE" && element.parentElement?.tagName !== "PRE") {
    const value = element.textContent || "";
    const fence = value.includes("`") ? "``" : "`";
    return `${fence}${value}${fence}`;
  }
  if (element.matches("STRONG, B")) return `**${children().trim()}**`;
  if (element.matches("EM, I")) return `_${children().trim()}_`;
  if (element.tagName === "A") return children();
  return children();
}

function markdownList(list, depth = 0) {
  const ordered = list.tagName === "OL";
  return [...list.children].filter((item) => item.tagName === "LI").map((item, index) => {
    const copy = item.cloneNode(true);
    copy.querySelector(":scope > span:first-child")?.remove();
    const nested = [...copy.querySelectorAll(":scope > ol, :scope > ul")];
    nested.forEach((child) => child.remove());
    const prefix = ordered ? `${index + 1}. ` : "- ";
    const body = markdownBlock(copy, depth + 1).trim().replace(/\n{2,}/g, "\n");
    const continuation = body.split("\n").map((line, lineIndex) => lineIndex ? `${"  ".repeat(depth + 1)}${line}` : line).join("\n");
    const children = nested.map((child) => markdownList(child, depth + 1)).filter(Boolean).join("\n");
    return `${"  ".repeat(depth)}${prefix}${continuation}${children ? `\n${children}` : ""}`;
  }).join("\n");
}

function markdownTable(table) {
  const rows = [...table.rows].map((row) => [...row.cells].map((cell) => markdownInline(cell).replace(/\s+/g, " ").trim().replaceAll("|", "\\|")));
  if (!rows.length) return "";
  const width = Math.max(...rows.map((row) => row.length));
  const normalized = rows.map((row) => [...row, ...Array(Math.max(0, width - row.length)).fill("")]);
  const line = (row) => `| ${row.join(" | ")} |`;
  return [line(normalized[0]), line(Array(width).fill("---")), ...normalized.slice(1).map(line)].join("\n");
}

function markdownBlock(node, depth = 0) {
  if (node.nodeType === 3) return (node.nodeValue || "").trim();
  if (node.nodeType !== 1) return "";
  const element = node;
  if (element.matches("svg, button, [aria-hidden='true']")) return "";
  const tag = element.tagName;
  if (/^H[1-6]$/.test(tag)) return `${"#".repeat(Number(tag[1]))} ${markdownInline(element).trim()}`;
  if (tag === "P") return markdownInline(element).replace(/\s+/g, " ").trim();
  if (tag === "PRE") {
    const value = (element.querySelector("code")?.textContent || element.textContent || "").replace(/\r\n/g, "\n").replace(/\s+$/, "");
    const fence = value.includes("```") ? "````" : "```";
    return `${fence}python\n${value}\n${fence}`;
  }
  if (tag === "OL" || tag === "UL") return markdownList(element, depth);
  if (tag === "TABLE") return markdownTable(element);
  if (element.matches(".algorithm-code-list")) {
    return [...element.children].map((item) => `- ${markdownInline(item).trim()}`).join("\n");
  }
  if (tag === "DL") {
    return [...element.children].map((group) => {
      const term = group.querySelector(":scope > dt");
      const value = group.querySelector(":scope > dd");
      if (!term || !value) return markdownBlock(group, depth);
      const rendered = markdownBlock(value, depth).trim();
      return rendered.startsWith("- ")
        ? `**${markdownInline(term).trim()}:**\n${rendered}`
        : `**${markdownInline(term).trim()}:** ${rendered}`;
    }).filter(Boolean).join("\n\n");
  }
  if (tag === "DETAILS") {
    const summary = element.querySelector(":scope > summary");
    const summaryText = summary
      ? [...summary.childNodes].map(markdownInline).map((value) => value.trim()).filter(Boolean).join(" · ")
      : "";
    const body = [...element.children].filter((child) => child !== summary).map((child) => markdownBlock(child, depth)).filter(Boolean).join("\n\n");
    return `${summaryText ? `**${summaryText}**` : ""}${body ? `\n\n${body}` : ""}`;
  }
  if (tag === "DT") return `**${markdownInline(element).trim()}:**`;
  if (tag === "DD") return markdownInline(element).trim();
  if (tag === "CODE") return markdownInline(element);
  if (element.matches("SPAN, STRONG, B, EM, I, A, BDI")) return markdownInline(element).trim();
  const blocks = [...element.childNodes].map((child) => markdownBlock(child, depth)).filter((value) => value && value.trim());
  return blocks.join("\n\n");
}

function copyablePage(page, language) {
  const clone = page.cloneNode(true);
  clone.removeAttribute("hidden");
  clone.querySelectorAll("[hidden]").forEach((element) => element.remove());
  clone.querySelectorAll(language === "fa" ? ".algorithm-copy-en, .algorithm-table-en" : ".algorithm-copy-fa, .algorithm-table-fa").forEach((element) => element.remove());
  clone.querySelectorAll("button, svg, .algorithm-type-header > a").forEach((element) => element.remove());
  clone.querySelectorAll("details").forEach((details) => { details.open = true; });
  const markdown = markdownBlock(clone).replace(/\n{3,}/g, "\n\n").trim();
  const direction = language === "fa" ? "rtl" : "ltr";
  const html = `<article lang="${language}" dir="${direction}">${clone.innerHTML}</article>`;
  return { markdown, html };
}

async function writePageClipboard(page, language) {
  const content = copyablePage(page, language);
  if (typeof window.ClipboardItem === "function" && navigator.clipboard?.write) {
    try {
      await navigator.clipboard.write([new window.ClipboardItem({
        "text/plain": new Blob([content.markdown], { type: "text/plain;charset=utf-8" }),
        "text/html": new Blob([content.html], { type: "text/html;charset=utf-8" }),
      })]);
      return;
    } catch (error) {
      if (!navigator.clipboard?.writeText) throw error;
    }
  }
  if (!navigator.clipboard?.writeText) throw new Error("Clipboard API is unavailable");
  await navigator.clipboard.writeText(content.markdown);
}

function collectStyleText() {
  return [...document.styleSheets].map((sheet) => {
    try { return [...sheet.cssRules].map((rule) => rule.cssText).join("\n"); }
    catch { return ""; }
  }).join("\n");
}

function exportDocument(main, language, direction = "bullish") {
  const clone = main.cloneNode(true);
  clone.removeAttribute("tabindex");
  clone.querySelectorAll("[hidden]").forEach((element) => element.removeAttribute("hidden"));
  clone.querySelectorAll("details").forEach((details) => { details.open = true; });
  clone.querySelectorAll("button, .algorithm-type-header a").forEach((element) => element.remove());
  clone.querySelectorAll("[tabindex]").forEach((element) => element.removeAttribute("tabindex"));
  const lang = language === "fa" ? "fa" : "en";
  const title = direction === "bearish"
    ? (lang === "fa" ? "مرجع الگوریتم نزولی TradingBot" : "TradingBot Bearish Algorithm Reference")
    : (lang === "fa" ? "مرجع الگوریتم صعودی TradingBot" : "TradingBot Bullish Algorithm Reference");
  const exportCss = `
    html,body{margin:0;background:#fff;color:#171a21}
    body{padding:28px;font-family:Inter,Arial,sans-serif}
    .algorithm-export{position:static;display:block;overflow:visible;background:#fff}
    .algorithm-export .algorithm-main{overflow:visible;padding:0}
    .algorithm-export .algorithm-main>*{width:min(980px,100%);margin-inline:auto}
    .algorithm-export .algorithm-family,.algorithm-export .algorithm-overview{display:block!important;break-before:page;padding-top:28px}
    .algorithm-export .algorithm-overview{break-before:auto}
    .algorithm-export .algorithm-code-summary,.algorithm-export .algorithm-object-contract{break-inside:avoid}
    .algorithm-export .algorithm-copy-fa{display:${lang === "fa" ? "block" : "none"}!important}
    .algorithm-export .algorithm-copy-en{display:${lang === "fa" ? "none" : "block"}!important}
    .algorithm-export .algorithm-table-fa{display:${lang === "fa" ? "table" : "none"}!important}
    .algorithm-export .algorithm-table-en{display:${lang === "fa" ? "none" : "table"}!important}
    @media print{body{padding:0}.algorithm-export .algorithm-family{break-before:page}.algorithm-ide{max-height:none!important;overflow:visible!important}}
  `;
  return `<!doctype html><html lang="${lang}" dir="${lang === "fa" ? "rtl" : "ltr"}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${title}</title><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Vazirmatn:wght@400;500;600;700&display=swap" rel="stylesheet"><style>${collectStyleText()}${exportCss}</style></head><body><section class="algorithm-view algorithm-export" data-language="${lang}"><main class="algorithm-main">${clone.innerHTML}</main></section></body></html>`;
}

export function initAlgorithmPage({ root, headerRoot, icon, showChart }) {
  root.insertAdjacentHTML("beforeend", pageMarkup(icon));
  const view = root.querySelector("#algorithmView");
  const header = view.querySelector(".algorithm-page-header");
  const menuButton = header.querySelector("#algorithmMenu");
  const searchClearButton = header.querySelector("#algorithmSearchClear");
  const main = view.querySelector("#algorithmMain");
  const sidebar = view.querySelector("#algorithmSidebar");
  const searchInput = view.querySelector("#algorithmSearch");
  const englishButton = view.querySelector("#algorithmLanguageEnglish");
  const persianButton = view.querySelector("#algorithmLanguagePersian");
  const searchStatus = view.querySelector("#algorithmSearchStatus");
  const actionStatus = view.querySelector("#algorithmActionStatus");
  const directionBullishButton = view.querySelector("#algorithmDirectionBullish");
  const directionBearishButton = view.querySelector("#algorithmDirectionBearish");
  const overviewPage = view.querySelector("#algorithm-overview");
  const familyPages = [...view.querySelectorAll(".algorithm-family")];
  const referencePages = [...view.querySelectorAll(".algorithm-reference-page")];
  const app = root.closest(".app");
  const isolated = [...root.children].filter((child) => child !== view);
  const previousAria = new Map();
  const pageScroll = new Map();
  const narrowScreen = window.matchMedia("(max-width: 760px)");
  let visible = false;
  let currentRoute = null;
  let lastAlgorithmHash = "#algorithm-overview";
  let previousExternalHash = "";
  let direction = "bullish";
  const originalTextNodes = new Map();
  const originalAttributes = new Map();

  function setDirection(nextDirection, persist = true) {
    direction = nextDirection === "bearish" ? "bearish" : "bullish";
    view.dataset.direction = direction;
    const walker = document.createTreeWalker(view, document.defaultView?.NodeFilter?.SHOW_TEXT || 4);
    while (walker.nextNode()) {
      const node = walker.currentNode;
      if (node.parentElement?.closest(".algorithm-direction")) continue;
      if (!originalTextNodes.has(node)) originalTextNodes.set(node, node.nodeValue || "");
      const owner = node.parentElement?.closest("[data-family], [data-nav-family]");
      const familyId = owner?.dataset.family || owner?.dataset.navFamily || "";
      node.nodeValue = direction === "bearish" && isBearishMirrorFamily(familyId)
        ? mirrorDirectionalText(originalTextNodes.get(node), familyId)
        : originalTextNodes.get(node);
    }
    view.querySelectorAll("[data-search], [aria-label], [title]").forEach((element) => {
      if (element.closest(".algorithm-direction")) return;
      const owner = element.closest("[data-family], [data-nav-family]");
      const familyId = owner?.dataset.family || owner?.dataset.navFamily || "";
      const shouldMirror = direction === "bearish" && isBearishMirrorFamily(familyId);
      ["data-search", "aria-label", "title"].forEach((attribute) => {
        if (!element.hasAttribute(attribute)) return;
        if (!originalAttributes.has(element)) originalAttributes.set(element, {});
        const saved = originalAttributes.get(element);
        if (!(attribute in saved)) saved[attribute] = element.getAttribute(attribute) || "";
        element.setAttribute(attribute, shouldMirror ? mirrorDirectionalText(saved[attribute], familyId) : saved[attribute]);
      });
    });
    const setLocalizedLabel = (selector, english, persian) => {
      const element = view.querySelector(selector) || header.querySelector(selector);
      if (!element) return;
      element.innerHTML = localized(english, persian);
      element.querySelectorAll(".algorithm-copy-en, .algorithm-copy-fa").forEach((copy) => {
        copy.hidden = copy.classList.contains("algorithm-copy-en")
          ? view.dataset.language !== "en"
          : view.dataset.language === "en";
      });
    };
    setLocalizedLabel(
      "#algorithmDirectionLabel",
      direction === "bearish" ? "Bearish · derived" : "Bullish · source",
      direction === "bearish" ? "نزولی · مشتق‌شده" : "صعودی · منبع",
    );
    setLocalizedLabel(
      "#algorithmPipelineLabel",
      direction === "bearish" ? "Bearish selected families" : "Bullish pipeline",
      direction === "bearish" ? "خانواده‌های نزولی منتخب" : "روند صعودی",
    );
    directionBullishButton.setAttribute("aria-pressed", String(direction === "bullish"));
    directionBearishButton.setAttribute("aria-pressed", String(direction === "bearish"));
    if (currentRoute) {
      const familyName = ROUTED_FAMILIES.find((item) => item.id === currentRoute.familyId)?.name;
      const typeName = currentRoute.typeId ? definitionFor(currentRoute.familyId).types.find((item) => item.id === currentRoute.typeId)?.names?.en : null;
      const referenceName = currentRoute.referenceId === "reaction-geometry" ? "Reaction geometry" : currentRoute.referenceId === "glossary" ? "Glossary" : null;
      document.title = `${typeName || familyName || referenceName || (direction === "bearish" ? "Bearish Algorithm" : "Bullish Algorithm")} · TradingBot`;
    }
    filter(searchInput.value);
    if (persist) {
      try { window.localStorage.setItem(DIRECTION_KEY, direction); } catch { /* optional preference */ }
    }
  }

  function setLanguage(language, persist = true) {
    const next = language === "fa" ? "fa" : "en";
    view.dataset.language = next;
    header.dataset.language = next;
    [...view.querySelectorAll(".algorithm-copy-en"), ...header.querySelectorAll(".algorithm-copy-en")].forEach((element) => { element.hidden = next !== "en"; });
    [...view.querySelectorAll(".algorithm-copy-fa"), ...header.querySelectorAll(".algorithm-copy-fa")].forEach((element) => { element.hidden = next !== "fa"; });
    [...view.querySelectorAll("[data-label-en]"), ...header.querySelectorAll("[data-label-en]")].forEach((element) => { element.setAttribute("aria-label", element.dataset[next === "fa" ? "labelFa" : "labelEn"]); });
    englishButton.setAttribute("aria-pressed", String(next === "en"));
    persianButton.setAttribute("aria-pressed", String(next === "fa"));
    searchInput.placeholder = next === "fa" ? "جست‌وجوی رفتار، قانون یا آبجکت" : "Search a behavior, rule, or object";
    searchInput.setAttribute("aria-label", next === "fa" ? "جست‌وجو در الگوریتم" : "Search the algorithm");
    searchStatus.textContent = next === "fa" ? "هیچ صفحه‌ای با این عبارت پیدا نشد" : "No matching page";
    header.querySelector("#algorithmBackToChart").setAttribute("aria-label", next === "fa" ? "برگشت به چارت" : "Back to chart");
    header.querySelector(".algorithm-language").setAttribute("aria-label", next === "fa" ? "زبان توضیحات" : "Explanation language");
    header.querySelector(".algorithm-direction").setAttribute("aria-label", next === "fa" ? "جهت الگوریتم" : "Algorithm direction");
    view.querySelector("#algorithmSidebar").setAttribute("aria-label", next === "fa" ? "فهرست الگوریتم" : "Algorithm contents");
    view.querySelector("#algorithmSidebarScrim").setAttribute("aria-label", next === "fa" ? "بستن فهرست الگوریتم" : "Close algorithm navigation");
    searchClearButton.setAttribute("aria-label", next === "fa" ? "پاک کردن جست‌وجو" : "Clear search");
    header.querySelector("#algorithmExport").setAttribute("aria-label", next === "fa" ? "ذخیره کل مرجع الگوریتم" : "Save the complete algorithm reference");
    header.querySelector("#algorithmExportFormat").setAttribute("aria-label", next === "fa" ? "فرمت ذخیره" : "Export format");
    setSidebarCollapsed(view.classList.contains("sidebar-collapsed"), false);
    actionStatus.textContent = "";
    if (persist) {
      try { window.localStorage.setItem(LANGUAGE_KEY, next); } catch { /* optional preference */ }
    }
  }

  function setIsolation(active) {
    app?.classList.toggle("algorithm-mode", active);
    root.classList.toggle("algorithm-active", active);
    for (const element of isolated) {
      if (active) {
        previousAria.set(element, element.getAttribute("aria-hidden"));
        element.inert = true;
        element.setAttribute("aria-hidden", "true");
      } else {
        element.inert = false;
        const previous = previousAria.get(element);
        if (previous == null) element.removeAttribute("aria-hidden");
        else element.setAttribute("aria-hidden", previous);
      }
    }
    if (!active) previousAria.clear();
  }

  function setSidebarOpen(open) {
    view.classList.toggle("sidebar-open", open);
    const menu = menuButton;
    const persian = view.dataset.language === "fa";
    menu.setAttribute("aria-expanded", String(open));
    menu.setAttribute("aria-label", open
      ? (persian ? "بستن فهرست الگوریتم" : "Close algorithm navigation")
      : (persian ? "باز کردن فهرست الگوریتم" : "Open algorithm navigation"));
    view.querySelector("#algorithmSidebarScrim").tabIndex = open ? 0 : -1;
  }

  function setSidebarCollapsed(collapsed, persist = true) {
    view.classList.toggle("sidebar-collapsed", collapsed);
    const button = view.querySelector("#algorithmSidebarToggle");
    button.setAttribute("aria-expanded", String(!collapsed));
    const persian = view.dataset.language === "fa";
    button.setAttribute("aria-label", narrowScreen.matches
      ? (persian ? "بستن فهرست الگوریتم" : "Close algorithm navigation")
      : (collapsed
        ? (persian ? "باز کردن فهرست الگوریتم" : "Expand algorithm navigation")
        : (persian ? "جمع کردن فهرست الگوریتم" : "Collapse algorithm navigation")));
    if (persist) {
      try { window.localStorage.setItem(SIDEBAR_KEY, String(collapsed)); } catch { /* optional preference */ }
    }
  }

  function routeFromHash(hash) {
    let anchor = String(hash || "").replace(/^#/, "");
    try { anchor = decodeURIComponent(anchor); } catch { anchor = ""; }
    if (anchor === "algorithm-overview") return { anchor, pageId: anchor, familyId: null, typeId: null };
    for (const family of ROUTED_FAMILIES) {
      const pageId = `algorithm-${family.id}`;
      if (anchor === pageId) return { anchor, pageId, familyId: family.id, typeId: null };
      const type = definitionFor(family.id).types.find((item) => anchor === `${pageId}-${item.id}`);
      if (type) return { anchor, pageId, familyId: family.id, typeId: type.id };
    }
    if (anchor === "algorithm-reaction-geometry") return { anchor, pageId: anchor, familyId: null, typeId: null, referenceId: "reaction-geometry" };
    if (anchor === "algorithm-glossary") return { anchor, pageId: anchor, familyId: null, typeId: null, referenceId: "glossary" };
    return { anchor: "algorithm-overview", pageId: "algorithm-overview", familyId: null, typeId: null };
  }

  function isAlgorithmHash(hash) {
    const route = routeFromHash(hash);
    return String(hash || "").replace(/^#/, "") === route.anchor;
  }

  function showPage(hash, { focus = true, restore = false } = {}) {
    const route = routeFromHash(hash);
    if (currentRoute) pageScroll.set(currentRoute.anchor, main.scrollTop);
    overviewPage.hidden = route.pageId !== "algorithm-overview";
    for (const page of familyPages) {
      page.hidden = page.id !== route.pageId;
      if (page.hidden) continue;
      page.classList.toggle("algorithm-type-route", Boolean(route.typeId));
      page.querySelectorAll("[data-family-only]").forEach((element) => { element.hidden = Boolean(route.typeId); });
      page.querySelectorAll("[data-type-panel]").forEach((element) => { element.hidden = Boolean(route.typeId) && element.dataset.typePanel !== route.typeId; });
    }
    for (const page of referencePages) page.hidden = page.id !== route.pageId;
    view.dataset.page = route.familyId || route.referenceId || "overview";
    view.querySelectorAll("[data-nav-family]").forEach((item) => {
      const active = item.dataset.navFamily === route.familyId;
      item.classList.toggle("active", active);
      item.querySelector(":scope > a")?.setAttribute("aria-expanded", String(active));
    });
    view.querySelectorAll(".algorithm-sidebar a[aria-current]").forEach((link) => link.removeAttribute("aria-current"));
    view.querySelector(`.algorithm-sidebar a[href="#${route.anchor}"]`)?.setAttribute("aria-current", "page");
    currentRoute = route;
    lastAlgorithmHash = `#${route.anchor}`;
    const familyName = ROUTED_FAMILIES.find((item) => item.id === route.familyId)?.name;
    const typeName = route.typeId ? definitionFor(route.familyId).types.find((item) => item.id === route.typeId)?.names?.en : null;
    const referenceName = route.referenceId === "reaction-geometry" ? "Reaction geometry" : route.referenceId === "glossary" ? "Glossary" : null;
    document.title = `${typeName || familyName || referenceName || (direction === "bearish" ? "Bearish Algorithm" : "Bullish Algorithm")} · TradingBot`;
    const savedScroll = restore ? pageScroll.get(route.anchor) || 0 : 0;
    main.scrollTop = savedScroll;
    requestAnimationFrame(() => {
      const page = view.querySelector(`#${route.pageId}`);
      const target = route.typeId ? view.querySelector(`#${route.anchor}`) : page;
      main.scrollTop = savedScroll;
      if (focus) target?.focus({ preventScroll: true });
    });
    return route;
  }

  function navigate(hash, { replace = false, restore = false } = {}) {
    const route = routeFromHash(hash);
    const nextHash = `#${route.anchor}`;
    window.history[replace ? "replaceState" : "pushState"](null, "", nextHash);
    showPage(nextHash, { restore });
  }

  function filter(query) {
    const normalized = query.trim().toLocaleLowerCase(view.dataset.language === "fa" ? "fa" : "en");
    let visibleLinks = 0;
    searchClearButton.classList.toggle("hidden", !normalized);
    view.classList.toggle("algorithm-searching", Boolean(normalized));
    const overviewLink = view.querySelector(".algorithm-overview-link");
    const overviewMatch = !normalized || overviewLink.dataset.search.includes(normalized);
    overviewLink.hidden = !overviewMatch;
    if (overviewMatch) visibleLinks += 1;
    view.querySelectorAll("[data-nav-family]").forEach((item) => {
      const familyLink = item.querySelector(":scope > a");
      const familyMatch = !normalized || familyLink.dataset.search.includes(normalized);
      let typeMatches = 0;
      item.querySelectorAll(":scope > ol > li").forEach((typeItem) => {
        const typeLink = typeItem.querySelector("a");
        const match = !normalized || familyMatch || typeLink.dataset.search.includes(normalized);
        typeItem.hidden = !match;
        if (match) typeMatches += 1;
      });
      const show = !normalized || familyMatch || typeMatches > 0;
      item.hidden = !show;
      if (show) visibleLinks += 1 + typeMatches;
    });
    view.querySelectorAll(".algorithm-reference-link").forEach((link) => {
      const match = !normalized || link.dataset.search.includes(normalized);
      link.closest("li").hidden = !match;
      if (match) visibleLinks += 1;
    });
    searchStatus.hidden = !normalized || visibleLinks > 0;
    if (normalized && narrowScreen.matches) setSidebarOpen(true);
  }

  async function saveHtml() {
    const language = view.dataset.language;
    const html = exportDocument(main, language, direction);
    const filename = `tradingbot-${direction}-algorithm-${language}.html`;
    if ("showSaveFilePicker" in window) {
      const handle = await window.showSaveFilePicker({ suggestedName: filename, types: [{ description: "HTML document", accept: { "text/html": [".html"] } }] });
      const writable = await handle.createWritable();
      await writable.write(new Blob([html], { type: "text/html;charset=utf-8" }));
      await writable.close();
      return;
    }
    const href = URL.createObjectURL(new Blob([html], { type: "text/html;charset=utf-8" }));
    const link = document.createElement("a");
    link.href = href;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(href);
  }

  function printPdf() {
    const popup = window.open("", "_blank");
    if (!popup) throw new Error("Print window was blocked");
    popup.document.open();
    popup.document.write(exportDocument(main, view.dataset.language, direction));
    popup.document.close();
    window.setTimeout(() => { popup.focus(); popup.print(); }, 400);
  }

  englishButton.onclick = () => setLanguage("en");
  persianButton.onclick = () => setLanguage("fa");
  directionBullishButton.onclick = () => setDirection("bullish");
  directionBearishButton.onclick = () => setDirection("bearish");
  menuButton.onclick = () => setSidebarOpen(!view.classList.contains("sidebar-open"));
  view.querySelector("#algorithmSidebarToggle").onclick = () => narrowScreen.matches ? setSidebarOpen(false) : setSidebarCollapsed(!view.classList.contains("sidebar-collapsed"));
  view.querySelector("#algorithmSidebarScrim").onclick = () => setSidebarOpen(false);
  narrowScreen.addEventListener?.("change", () => {
    setSidebarOpen(false);
    setSidebarCollapsed(view.classList.contains("sidebar-collapsed"), false);
  });
  header.querySelector("#algorithmBackToChart").onclick = () => showChart();
  searchInput.oninput = (event) => filter(event.target.value);
  searchInput.onkeydown = (event) => {
    if (event.key !== "Enter") return;
    const firstMatch = [...view.querySelectorAll(".algorithm-sidebar a[data-page-link]")].find((link) => !link.hidden && !link.closest("li")?.hidden);
    if (!firstMatch) return;
    event.preventDefault();
    searchInput.value = "";
    filter("");
    navigate(firstMatch.getAttribute("href"));
    setSidebarOpen(false);
  };
  searchClearButton.onclick = () => {
    searchInput.value = "";
    filter("");
    searchInput.focus();
  };
  sidebar.onclick = (event) => {
    const link = event.target.closest("a[data-page-link]");
    if (!link) return;
    event.preventDefault();
    searchInput.value = "";
    filter("");
    navigate(link.getAttribute("href"));
    if (narrowScreen.matches) setSidebarOpen(false);
  };
  sidebar.addEventListener("dragstart", (event) => event.preventDefault());
  header.querySelector("#algorithmCopyPage").onclick = async () => {
    const button = header.querySelector("#algorithmCopyPage");
    const page = view.querySelector(`#${currentRoute?.pageId || "algorithm-overview"}`);
    if (!page) return;
    button.disabled = true;
    actionStatus.textContent = view.dataset.language === "fa" ? "در حال کپی…" : "Copying…";
    try {
      await writePageClipboard(page, view.dataset.language);
      actionStatus.textContent = view.dataset.language === "fa" ? "صفحه کپی شد" : "Page copied";
    } catch {
      actionStatus.textContent = view.dataset.language === "fa" ? "کپی انجام نشد" : "Copy failed";
    } finally {
      button.disabled = false;
    }
  };
  view.onclick = (event) => {
    const copy = event.target.closest("[data-copy-code]");
    if (!copy) return;
    const code = copy.closest("[data-code-block]")?.querySelector("code")?.textContent || "";
    navigator.clipboard.writeText(code).then(() => {
      const label = copy.querySelector("[data-copy-label]");
      label.textContent = view.dataset.language === "fa" ? "کپی شد" : "Copied";
      window.setTimeout(() => { label.innerHTML = localized("Copy", "کپی"); }, 1200);
    }).catch(() => {});
  };
  header.querySelector("#algorithmExport").onclick = async () => {
    const button = header.querySelector("#algorithmExport");
    button.disabled = true;
    actionStatus.textContent = view.dataset.language === "fa" ? "در حال ذخیره…" : "Saving…";
    try {
      if (header.querySelector("#algorithmExportFormat").value === "pdf") printPdf();
      else await saveHtml();
      actionStatus.textContent = view.dataset.language === "fa" ? "آماده شد" : "Ready";
    } catch (error) {
      if (error?.name === "AbortError") actionStatus.textContent = "";
      else actionStatus.textContent = view.dataset.language === "fa" ? "ذخیره انجام نشد" : "Save failed";
    } finally {
      button.disabled = false;
    }
  };
  window.addEventListener("hashchange", () => {
    if (visible && isAlgorithmHash(window.location.hash)) showPage(window.location.hash);
  });
  window.addEventListener("keydown", (event) => {
    if (visible && event.key === "Escape" && view.classList.contains("sidebar-open")) setSidebarOpen(false);
  });

  setLanguage(storedLanguage(), false);
  setSidebarCollapsed(storedSidebarState(), false);
  setDirection(storedDirection(), false);

  function open() {
    if (visible) return;
    visible = true;
    mountWorkspaceHeader(headerRoot, header);
    previousExternalHash = isAlgorithmHash(window.location.hash) ? "" : window.location.hash;
    view.classList.remove("hidden");
    setIsolation(true);
    if (isAlgorithmHash(window.location.hash)) showPage(window.location.hash, { restore: true });
    else navigate(lastAlgorithmHash, { replace: true, restore: true });
  }

  function close() {
    if (!visible) return true;
    if (currentRoute) pageScroll.set(currentRoute.anchor, main.scrollTop);
    visible = false;
    setSidebarOpen(false);
    view.classList.add("hidden");
    restoreWorkspaceHeader(view, header);
    setIsolation(false);
    if (isAlgorithmHash(window.location.hash)) window.history.replaceState(null, "", previousExternalHash || `${window.location.pathname}${window.location.search}`);
    document.title = "TradingBot Chart";
    return true;
  }

  return { open, close, isActive: () => visible };
}
