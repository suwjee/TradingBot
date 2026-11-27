import { strToU8, zip } from "fflate";
import { engineCalculationDuration } from "../indicator-lifecycle.js";
import { reportExportFormats, reportFamilyOrder, reviewEventLabels, reviewRuntimeSource } from "./render.js";
import { reviewView } from "./view.js";

function filenamePart(value, fallback) {
  return String(value || "").replace(/[^a-zA-Z0-9._-]+/g, "-").replace(/^[.-]+|[.-]+$/g, "").slice(0, 64) || fallback;
}

function collectionCounts(group) {
  return Object.fromEntries(Object.entries(group || {}).flatMap(([key, rows]) =>
    Array.isArray(rows) ? [[key, rows.length]] : []));
}

function archiveMetadata(payload, snapshot, events, exportedAt, includesBridgeOutput) {
  const calculation = snapshot.calculation || {};
  const directions = Object.entries(payload.directions);
  const families = new Map(reportFamilyOrder.map(family => [family, 0]));
  const categories = new Map();
  const byDirection = new Map();
  for (const { family, category, direction } of events) {
    families.set(family, (families.get(family) || 0) + 1);
    categories.set(category, (categories.get(category) || 0) + 1);
    const counts = byDirection.get(direction) || new Map();
    counts.set(family, (counts.get(family) || 0) + 1);
    byDirection.set(direction, counts);
  }
  const regimes = directions.flatMap(([direction, group]) =>
    (group.calculationSegments || [group]).map(segment => ({
      direction,
      fromEpoch: segment.calculationStartTime ?? payload.actualFrom ?? null,
      toEpoch: segment.calculationEndTime ?? payload.actualTo ?? null,
    }))).sort((a, b) => a.fromEpoch - b.fromEpoch);
  const sourceId = calculation.sourceFile || calculation.source?.id || null;
  return {
    schemaVersion: 1,
    sourceFile: sourceId?.split(/[\\/]/).at(-1) || null,
    sourceId,
    calculationId: calculation.calculationId ?? null,
    symbol: calculation.symbol ?? calculation.source?.symbol ?? null,
    timeframeSeconds: calculation.timeframe ?? payload.timeframe ?? null,
    chartTimeframeSeconds: calculation.chartTimeframe ?? null,
    rawTimeframeSeconds: calculation.rawTimeframeSeconds ?? null,
    timezone: "Asia/Tehran",
    calculatedAt: calculation.calculatedAt ?? null,
    exportedAt: exportedAt.toISOString(),
    includesBridgeOutput,
    durationMs: engineCalculationDuration(payload),
    phasesMs: payload.timings?.phasesMs ?? null,
    initialDirection: calculation.direction ?? null,
    activeDirection: payload.activeDirection ?? (directions.length === 1 ? directions[0][0] : null),
    publishedDirections: directions.map(([direction]) => direction),
    regimes,
    requestedRange: { fromEpoch: calculation.from ?? null, toEpoch: calculation.to ?? null },
    actualRange: { fromEpoch: payload.actualFrom ?? null, toEpoch: payload.actualTo ?? null },
    counts: {
      events: events.length,
      families: Object.fromEntries(families),
      categories: Object.fromEntries(categories),
      byDirection: Object.fromEntries([...byDirection].map(([key, counts]) => [key, Object.fromEntries(counts)])),
      payloadCollections: Object.fromEntries(directions.map(([key, group]) => [key, collectionCounts(group)])),
      ...(includesBridgeOutput && {
        bridgeCollections: Object.fromEntries(directions.map(([key, group]) => [key, collectionCounts(group.bridgeOutput)])),
      }),
    },
  };
}

function withoutBridgeOutput(payload) {
  function omitGroup({ bridgeOutput, ...group }) {
    if (Array.isArray(group.calculationSegments)) group.calculationSegments = group.calculationSegments.map(omitGroup);
    return group;
  }
  const { bridgeOutput, ...result } = payload;
  result.directions = Object.fromEntries(Object.entries(result.directions).map(([key, group]) => [key, omitGroup(group)]));
  if (Array.isArray(result.report)) {
    result.report = result.report.map(({ details, bridgeOutput, ...event }) => event);
  }
  return result;
}

const pointerKey = key => String(key).replaceAll("~", "~0").replaceAll("/", "~1");

// Keep records intact while addressing them by JSON Pointer through the payload.
function* payloadEntries(value, path = "", splitObject = true) {
  const isObject = value !== null && typeof value === "object";
  const split = Array.isArray(value) || (isObject && splitObject);
  const entries = split ? Object.entries(value) : [];
  if (!entries.length) {
    yield [path, value];
    return;
  }
  yield [path, Array.isArray(value) ? [] : {}];
  for (const [key, child] of entries) {
    const childPath = `${path}/${pointerKey(key)}`;
    const splitChild = !path || path === "/directions" || key === "bridgeOutput" || path.endsWith("/calculationSegments");
    yield* payloadEntries(child, childPath, splitChild);
  }
}

function csvCell(value) {
  let text = String(value ?? "");
  // Spreadsheet controls apply only to display columns. JSON values remain lossless.
  if (/^[\t\r\n]|^\s*[=+@-]/.test(text)) text = `'${text}`;
  return /[",\r\n]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text;
}

function addCsvRows(rows, section, path, data, columns = []) {
  const json = JSON.stringify(data);
  const fragmented = json.length > 30_000;
  const size = fragmented ? 12_000 : json.length;
  const fields = Array.from({ length: 7 }, (_, index) => csvCell(columns[index]));
  let start = 0;
  for (let part = 1; start < json.length; part++) {
    let end = Math.min(start + size, json.length);
    // A UTF-16 surrogate pair must stay in one UTF-8 cell.
    if (end < json.length && /[\uD800-\uDBFF]/.test(json[end - 1])) end--;
    const text = fragmented ? JSON.stringify(json.slice(start, end)) : json;
    const chunk = `"${text.replaceAll('"', '""')}"`;
    rows.push([section, csvCell(path), part, ...fields, fragmented ? "json-string-fragment" : "json", chunk].join(","));
    start = end;
  }
}

function addMachineFiles(files, formats, metadata, payload, events) {
  if (formats.has("json")) files["calculation.json"] = strToU8(`${JSON.stringify({ metadata, payload, events }, null, 2)}\n`);
  const csv = formats.has("csv") ? ["section,path,part,event_id,time,direction,family,category,label,verdict,encoding,data_json"] : null;
  const ndjson = formats.has("ndjson") ? [JSON.stringify({ section: "metadata", data: metadata })] : null;
  if (!csv && !ndjson) return;
  if (csv) {
    for (const [key, value] of Object.entries(metadata)) addCsvRows(csv, "metadata", `/${pointerKey(key)}`, value);
  }
  for (const [index, event] of events.entries()) {
    const path = `/events/${index}`;
    if (csv) {
      const { id, time, direction, family, category, copyLabel, verdict } = event;
      addCsvRows(csv, "event", path, event, [id, time, direction, family, category, copyLabel, verdict]);
    }
    ndjson?.push(JSON.stringify({ section: "event", path, data: event }));
  }
  for (const [path, data] of payloadEntries(payload)) {
    if (csv) addCsvRows(csv, "payload", path, data);
    ndjson?.push(JSON.stringify({ section: "payload", path, data }));
  }
  if (csv) files["calculation.csv"] = strToU8(`\uFEFF${csv.join("\r\n")}\r\n`);
  if (ndjson) files["calculation.ndjson"] = strToU8(`${ndjson.join("\n")}\n`);
}

const scriptJson = value => JSON.stringify(value).replaceAll("<", "\\u003c");

function offlineHtml({ body, bridgeData }, css, view) {
  return `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Indicator Info</title><style>${css}</style></head><body><div id="app">${body}</div><script>
${reviewRuntimeSource()}
(${reviewView.toString()})(document.getElementById("app"), ${scriptJson(view ?? null)});
const exportButton = document.getElementById("export-zip");
exportButton.disabled = true;
exportButton.title = "This report is already part of an exported archive.";
document.getElementById("include-bridge").disabled = true;
mountReview(${scriptJson(bridgeData)});
</script></body></html>`;
}

const supportedFormats = reportExportFormats.map(([id]) => id);

export async function createCalculationArchive({
  payload, snapshot, review, css, view, formats = supportedFormats, includeBridgeOutput = true, exportedAt = new Date(),
}) {
  const selected = new Set(formats);
  if (!selected.size) throw new Error("Select at least one file format.");
  if ([...selected].some(id => !supportedFormats.includes(id))) throw new Error("Unsupported calculation export format.");
  const includeData = [...selected].some(id => id !== "html");
  const events = includeData ? review.records.map(record => ({
    id: record.id,
    time: record.time,
    epoch: typeof record.epoch === "number" ? record.epoch : null,
    direction: String(record.direction || "").toLowerCase(),
    collection: record.group,
    family: record.category.family,
    category: record.category.key,
    ...reviewEventLabels(record),
    ...(includeBridgeOutput && { bridgeOutput: review.bridgeData[record.id] }),
  })) : [];
  const metadata = archiveMetadata(payload, snapshot, events, exportedAt, includeBridgeOutput);
  const slug = filenamePart(metadata.symbol || metadata.sourceFile, "indicator");
  const timeframe = metadata.timeframeSeconds == null ? "unknown-tf" : `${metadata.timeframeSeconds}s`;
  const stamp = metadata.exportedAt.replace(/[:.]/g, "-");
  const files = {};
  if (includeData) {
    const dataPayload = includeBridgeOutput ? payload : withoutBridgeOutput(payload);
    addMachineFiles(files, selected, metadata, dataPayload, events);
  }
  if (selected.has("html")) files["html/index.html"] = strToU8(offlineHtml(review, css, view));
  const bytes = await new Promise((resolve, reject) => {
    zip(files, { level: 9 }, (error, data) => { if (error) reject(error); else resolve(data); });
  });
  return { name: `calculation-report-${slug}-${timeframe}-${stamp}.zip`, bytes };
}
