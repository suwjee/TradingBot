import fs from "node:fs";
import path from "node:path";
import { createHash, randomUUID } from "node:crypto";
import { summarizeVerifiedRows } from "./candle-verification.js";
import { mergeFarazCoverageRanges } from "../src/features/candle-update.js";
import { buildRawFilename, formatTehranMetadataTime, parseRawFilename, parseTehranMetadataTime } from "../src/features/raw-file-contract.js";

const CANDLE_KEYS = ["time", "open", "high", "low", "close"];
const UNIT_SECONDS = { S: 1, M: 60, H: 3600, D: 86400, W: 604800 };
const MAX_RECENT_APPENDS = 128;
const MAX_APPEND_BYTES = 256 * 1024;

function segment(value, fallback) {
  const result = String(value || "").trim().replace(/[^a-zA-Z0-9._-]+/g, "_").replace(/^_+|_+$/g, "").slice(0, 80);
  return result || fallback;
}

function assertCandles(candles, timeframeSeconds) {
  if (!Array.isArray(candles) || !candles.length) throw new Error("RAW candles must be a non-empty array.");
  let matchesGrid = Number.isSafeInteger(timeframeSeconds) && timeframeSeconds > 0;
  candles.forEach((row, index) => {
    if (!row || Object.keys(row).length !== CANDLE_KEYS.length || !CANDLE_KEYS.every((key) => Object.hasOwn(row, key))) throw new Error(`RAW candle ${index + 1} has an invalid schema.`);
    const time = Number(row.time), open = Number(row.open), high = Number(row.high), low = Number(row.low), close = Number(row.close);
    if (!Number.isSafeInteger(time) || time <= 0 || ![open, high, low, close].every(Number.isFinite)
      || high < Math.max(open, close, low) || low > Math.min(open, close, high)
      || (index && time <= Number(candles[index - 1].time))) throw new Error(`RAW candle ${index + 1} failed chronology or OHLC validation.`);
    matchesGrid = matchesGrid && CANDLE_KEYS.every((key) => typeof row[key] === "number") && (time - candles[0].time) % timeframeSeconds === 0;
  });
  return matchesGrid;
}

function atomicWrite(filePath, text) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  const temporary = path.join(path.dirname(filePath), `.${path.basename(filePath)}.${randomUUID()}.tmp`);
  fs.writeFileSync(temporary, text, "utf8");
  try {
    if (fs.existsSync(filePath)) fs.unlinkSync(filePath);
    fs.renameSync(temporary, filePath);
  } finally {
    if (fs.existsSync(temporary)) fs.unlinkSync(temporary);
  }
}

function safeId(id) {
  const normalized = String(id || "").replaceAll("\\", "/");
  if (!normalized || normalized.startsWith("/") || normalized.split("/").some((part) => !part || part === "." || part === "..")) return null;
  return normalized;
}

function sidecarPath(dataPath) { return `${dataPath}.meta.json`; }

function validChartId(value) {
  const id = String(value || "").trim();
  return /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(id) ? id : null;
}

function readableRange(range) {
  if (!range || !Number.isSafeInteger(Number(range.from)) || !Number.isSafeInteger(Number(range.to))) return null;
  return { from: formatTehranMetadataTime(Number(range.from)), to: formatTehranMetadataTime(Number(range.to)) };
}

function runtimeRange(range) {
  if (!range) return null;
  const from = typeof range.from === "number" ? range.from : parseTehranMetadataTime(range.from);
  const to = typeof range.to === "number" ? range.to : parseTehranMetadataTime(range.to);
  return Number.isSafeInteger(from) && Number.isSafeInteger(to) ? { from, to } : null;
}

function readableCoverage(coverage) {
  if (!coverage) return undefined;
  return {
    ...coverage,
    checkedFrom: Number.isSafeInteger(coverage.checkedFrom) ? formatTehranMetadataTime(coverage.checkedFrom) : null,
    checkedTo: Number.isSafeInteger(coverage.checkedTo) ? formatTehranMetadataTime(coverage.checkedTo) : null,
    checkedThrough: Number.isSafeInteger(coverage.checkedThrough) ? formatTehranMetadataTime(coverage.checkedThrough) : null,
    verifiedAt: typeof coverage.verifiedAt === "string"
      ? coverage.verifiedAt
      : formatTehranMetadataTime(Math.floor(Date.now() / 1000)),
    ranges: (coverage.ranges || []).map((range) => ({ ...range, ...readableRange(range) })),
  };
}

function runtimeCoverage(coverage) {
  if (!coverage) return undefined;
  return {
    ...coverage,
    checkedFrom: typeof coverage.checkedFrom === "number" ? coverage.checkedFrom : parseTehranMetadataTime(coverage.checkedFrom),
    checkedTo: typeof coverage.checkedTo === "number" ? coverage.checkedTo : parseTehranMetadataTime(coverage.checkedTo),
    checkedThrough: typeof coverage.checkedThrough === "number" ? coverage.checkedThrough : parseTehranMetadataTime(coverage.checkedThrough),
    ranges: (coverage.ranges || []).map((range) => ({ ...range, ...runtimeRange(range) })).filter((range) => Number.isSafeInteger(range.from) && Number.isSafeInteger(range.to)),
  };
}

function runtimeMetadata(metadata) {
  const actualRange = runtimeRange(metadata.actualRange || metadata.effectiveRange);
  return { ...metadata, actualRange, effectiveRange: actualRange, requestedRange: runtimeRange(metadata.requestedRange), farazCoverage: runtimeCoverage(metadata.farazCoverage) };
}

function snapshotData(candles, serialized) {
  return {
    from: candles[0].time, to: candles.at(-1).time, count: candles.length,
    dataBytes: Buffer.byteLength(serialized), dataSha256: createHash("sha256").update(serialized).digest("hex"),
  };
}

function amendRawRows(contents, corrections, gapCandles) {
  if (!corrections.length && !gapCandles.length) return contents;
  const text = contents.toString("utf8");
  const replacements = new Map(corrections.map(row => [row.time, row]));
  const parts = [];
  let depth = 0, start = 0, cursor = 0, gapIndex = 0;
  // The validated RAW root is an array of objects. Skip quoted tokens so
  // formatting and numeric lexemes of unaffected rows remain byte-identical.
  for (const token of text.matchAll(/"(?:\\.|[^"\\])*"|[{}\[\]]/gs)) {
    const value = token[0];
    if (value === "{" && depth === 1) start = token.index;
    if (value === "{" || value === "[") depth++;
    if (value === "}" || value === "]") depth--;
    if (value !== "}" || depth !== 1) continue;
    const end = token.index + 1;
    const time = Number(JSON.parse(text.slice(start, end)).time);
    const replacement = replacements.get(time);
    const firstGap = gapIndex;
    while (gapIndex < gapCandles.length && gapCandles[gapIndex].time < time) gapIndex++;
    if (gapCandles[gapIndex]?.time === time) throw new Error("A gap candle already exists in the RAW file.");
    if (replacement || firstGap < gapIndex) {
      parts.push(text.slice(cursor, start));
      for (let index = firstGap; index < gapIndex; index++) parts.push(JSON.stringify(gapCandles[index]), ",");
      parts.push(replacement ? JSON.stringify(replacement) : text.slice(start, end));
      cursor = end;
      replacements.delete(time);
    }
    if (!replacements.size && gapIndex === gapCandles.length) break;
  }
  if (replacements.size || gapIndex !== gapCandles.length) throw new Error("A historical repair references a candle outside this RAW file.");
  return Buffer.from(parts.join("") + text.slice(cursor));
}

function persistedMetadata({ broker, symbol, timeframe, source, filename, snapshot, requestedRange = null, farazCoverage, candleVerification, createdAt, updatedAt, previousSha256, chartId }) {
  const now = formatTehranMetadataTime(Math.floor(Date.now() / 1000));
  const { from, to, count, dataBytes, dataSha256 } = snapshot;
  return {
    schemaVersion: 2,
    chartId: validChartId(chartId) || randomUUID(),
    broker,
    symbol,
    timeframe,
    source,
    filename,
    candleCount: count,
    count,
    dataBytes,
    dataSha256,
    requestedRange: readableRange(requestedRange),
    actualRange: readableRange({ from, to }),
    createdAt: createdAt || now,
    updatedAt: previousSha256 === dataSha256 && typeof updatedAt === "string" ? updatedAt : now,
    ...(farazCoverage ? { farazCoverage: readableCoverage(runtimeCoverage(farazCoverage)) } : {}),
    ...(candleVerification ? { candleVerification } : {}),
  };
}

export function createRawResourceStore({ rootDir }) {
  const root = path.resolve(rootDir);
  const inventoryCache = new Map();
  const recentAppends = new Map();
  const verificationSnapshots = new WeakMap();

  function fileVersion(stat) {
    return `${stat.dev}:${stat.ino}:${stat.size}:${stat.birthtimeNs}:${stat.mtimeNs}:${stat.ctimeNs}`;
  }

  function inventorySignature(dataPath, metaPath) {
    const data = fs.statSync(dataPath, { bigint: true, throwIfNoEntry: false });
    if (!data) return null;
    const metadata = fs.statSync(metaPath, { bigint: true, throwIfNoEntry: false });
    return `${fileVersion(data)}:${metadata ? fileVersion(metadata) : ""}`;
  }

  function resolve(id) {
    const logicalId = safeId(id);
    if (!logicalId || !logicalId.toLowerCase().endsWith(".json") || logicalId.toLowerCase().endsWith(".meta.json")) return null;
    const dataPath = path.resolve(root, ...logicalId.split("/"));
    if (!dataPath.startsWith(`${root}${path.sep}`) || !fs.existsSync(dataPath)) return null;
    return { id: logicalId, dataPath, metaPath: sidecarPath(dataPath) };
  }

  function version(id) {
    const item = resolve(id);
    const stat = item && fs.statSync(item.dataPath, { bigint: true, throwIfNoEntry: false });
    return stat ? fileVersion(stat) : null;
  }

  function write({ broker, symbol, timeframe, candles, requestedRange = null, source = "local", chartId = null, farazCoverage = undefined, createdAt = undefined }) {
    assertCandles(candles);
    const brokerSegment = segment(broker, "UNKNOWN").toUpperCase();
    const symbolSegment = segment(symbol, "UNNAMED").toUpperCase();
    const normalizedTimeframe = String(timeframe || "UNKNOWN").toUpperCase();
    const filename = buildRawFilename({ broker: brokerSegment, symbol: symbolSegment, timeframe: normalizedTimeframe, firstTime: candles[0].time, lastTime: candles.at(-1).time });
    const id = `${brokerSegment}/${symbolSegment}/${filename}`;
    const dataPath = path.join(root, brokerSegment, symbolSegment, filename);
    const serialized = JSON.stringify(candles);
    if (fs.existsSync(dataPath)) {
      if (fs.readFileSync(dataPath, "utf8") !== serialized) throw new Error(`A different RAW file already exists at ${id}.`);
    } else {
      atomicWrite(dataPath, serialized);
    }
    let existing = {};
    const metadataPath = sidecarPath(dataPath);
    if (fs.existsSync(metadataPath)) {
      try { existing = JSON.parse(fs.readFileSync(metadataPath, "utf8")) || {}; } catch { existing = {}; }
    }
    const snapshot = snapshotData(candles, serialized);
    const metadata = persistedMetadata({
      broker: brokerSegment, symbol: symbolSegment, timeframe: normalizedTimeframe, source, filename, snapshot, requestedRange,
      farazCoverage: farazCoverage ?? existing.farazCoverage, chartId: chartId || existing.chartId, createdAt: createdAt || existing.createdAt,
      candleVerification: existing.dataSha256 === snapshot.dataSha256 ? existing.candleVerification : undefined,
      updatedAt: existing.updatedAt, previousSha256: existing.dataSha256,
    });
    atomicWrite(sidecarPath(dataPath), `${JSON.stringify(metadata, null, 2)}\n`);
    inventoryCache.delete(id);
    return { id, dataPath, metaPath: sidecarPath(dataPath), ...runtimeMetadata(metadata), chartId: metadata.chartId, count: candles.length, bytes: Buffer.byteLength(serialized) };
  }

  function cacheItem(resource, metadata, snapshot, timeframeSeconds) {
    const stat = fs.statSync(resource.dataPath);
    const item = { ...resource, broker: metadata.broker, symbol: metadata.symbol, timeframe: metadata.timeframe, chartId: metadata.chartId, from: snapshot.from, to: snapshot.to, count: snapshot.count, bytes: stat.size, savedAt: stat.mtimeMs, metadata: runtimeMetadata(metadata), createdAt: metadata.createdAt, updatedAt: metadata.updatedAt };
    inventoryCache.set(item.id, { signature: inventorySignature(item.dataPath, item.metaPath), item, timeframeSeconds });
    return item;
  }

  function get(id) {
    const resource = resolve(id);
    return resource ? readItem(resource) : null;
  }

  function getListed(id) {
    if (typeof id !== "string" || !id.endsWith(".json")) return null;
    const resource = resolve(id);
    if (resource?.id !== id) return null;
    try {
      const actual = fs.realpathSync.native(resource.dataPath);
      const relative = path.relative(fs.realpathSync.native(root), actual).split(path.sep).join("/");
      // The inventory lists exact filename casing and skips links and junctions.
      if (relative !== id || !fs.lstatSync(resource.dataPath).isFile()) return null;
    } catch {
      return null;
    }
    return readItem(resource);
  }

  function readItem(resource) {
    const { dataPath, metaPath } = resource;
    const filename = path.basename(dataPath);
    const identity = parseRawFilename(filename);
    if (!identity) return null;
    const signature = inventorySignature(dataPath, metaPath);
    const cached = inventoryCache.get(resource.id);
    if (cached?.signature === signature) return cached.item;
    try {
      const serialized = fs.readFileSync(dataPath);
      const candles = JSON.parse(serialized);
      const unit = identity.timeframe.at(-1);
      const timeframeSeconds = Number(identity.timeframe.slice(0, -1)) * UNIT_SECONDS[unit];
      const matchesGrid = assertCandles(candles, timeframeSeconds);
      const snapshot = snapshotData(candles, serialized);
      let previous = {};
      if (fs.existsSync(metaPath)) {
        try { previous = JSON.parse(fs.readFileSync(metaPath, "utf8")) || {}; } catch { previous = {}; }
      }
      const hydratedPrevious = runtimeMetadata(previous);
      const metadata = persistedMetadata({ ...identity, source: previous.source || "import", filename, snapshot, requestedRange: hydratedPrevious.requestedRange, farazCoverage: previous.farazCoverage,
        candleVerification: previous.dataSha256 === snapshot.dataSha256 ? previous.candleVerification : undefined,
        chartId: previous.chartId, createdAt: typeof previous.createdAt === "string" ? previous.createdAt : undefined, updatedAt: previous.updatedAt, previousSha256: previous.dataSha256 });
      if (JSON.stringify(previous) !== JSON.stringify(metadata)) atomicWrite(metaPath, `${JSON.stringify(metadata, null, 2)}\n`);
      return cacheItem(resource, metadata, snapshot, matchesGrid ? timeframeSeconds : null);
    } catch {
      inventoryCache.set(resource.id, { signature, item: null });
      return null;
    }
  }

  function list() {
    if (!fs.existsSync(root)) return [];
    const items = [];
    const seen = new Set();
    const walk = (dir) => fs.readdirSync(dir, { withFileTypes: true }).forEach((entry) => {
      const target = path.join(dir, entry.name);
      if (entry.isDirectory()) return walk(target);
      if (!entry.isFile() || !entry.name.endsWith(".json") || entry.name.endsWith(".meta.json")) return;
      const id = path.relative(root, target).split(path.sep).join("/");
      const item = get(id);
      seen.add(id);
      if (item) items.push(item);
    });
    walk(root);
    for (const id of inventoryCache.keys()) {
      if (!seen.has(id)) inventoryCache.delete(id);
    }
    return items.sort((a, b) => a.symbol.localeCompare(b.symbol) || b.savedAt - a.savedAt || a.id.localeCompare(b.id));
  }

  function read(id) {
    const item = resolve(id);
    if (!item) return null;
    const candles = JSON.parse(fs.readFileSync(item.dataPath, "utf8"));
    assertCandles(candles);
    return candles;
  }

  async function readForVerification(file, expectedVersion, signal) {
    if (inventoryCache.get(file.id)?.item !== file) return null;
    let contents;
    try { contents = await fs.promises.readFile(file.dataPath, { signal }); }
    catch (error) { if (error.code === "ENOENT") return null; throw error; }
    signal.throwIfAborted();
    const digest = createHash("sha256").update(contents).digest("hex");
    if (digest !== file.metadata.dataSha256 || version(file.id) !== expectedVersion) return null;
    // get() already validated the schema and chronology of this exact digest.
    const rows = JSON.parse(contents);
    const snapshot = {};
    verificationSnapshots.set(snapshot, { id: file.id, version: expectedVersion, digest });
    return { rows, snapshot };
  }

  function appendKey(chartId, digest) {
    return `${chartId}:${digest}`;
  }

  function appendChain(chartId, base, target) {
    const edges = [];
    for (let digest = target; digest !== base;) {
      const edge = recentAppends.get(appendKey(chartId, digest));
      if (!edge) return null;
      edges.push(edge);
      digest = edge.base;
    }
    return edges;
  }

  function isCurrent(file) {
    const current = get(file.id);
    return current?.chartId === file.chartId && current.metadata.dataSha256 === file.metadata.dataSha256;
  }

  function readAppendDelta(file, baseSha256) {
    if (!baseSha256 || baseSha256 === file.metadata.dataSha256 || !canServeAppendSnapshot(file)) return null;
    const edges = appendChain(file.chartId, baseSha256, file.metadata.dataSha256);
    return edges && Buffer.concat(edges.reverse().map(edge => edge.bytes));
  }

  function readCommittedCandleAppend(file, { id, lastCandleTime, baseSha256 }) {
    if (!isCurrent(file)) return null;
    const edges = appendChain(file.chartId, baseSha256, file.metadata.dataSha256);
    const oldest = edges?.at(-1);
    if (!oldest || oldest.previousId !== id || oldest.previousTo !== lastCandleTime) return null;
    const bytes = Buffer.concat(edges.reverse().map(edge => edge.bytes));
    return JSON.parse(`[${bytes.subarray(1).toString("utf8")}]`);
  }

  function canServeAppendSnapshot(file) {
    if (isCurrent(file)) return true;
    // A calculation already reading a superseded file may finish when every
    // intervening commit only extended its exact bytes. Repairs break the chain.
    const newest = [...recentAppends.values()].reverse().find(edge => edge.file.chartId === file.chartId);
    return Boolean(newest && appendChain(file.chartId, file.metadata.dataSha256, newest.file.metadata.dataSha256)
      && isCurrent(newest.file));
  }

  async function appendLatest(file, incoming, timeframeSeconds, expectedVersion, signal, {
    corrections = [], gapCandles = [], verification, verificationSnapshot,
  } = {}) {
    const cached = inventoryCache.get(file.id);
    if (cached?.item !== file || (incoming.length && (cached.timeframeSeconds !== timeframeSeconds
      || !assertCandles(incoming, timeframeSeconds) || incoming[0].time <= file.to
      || (incoming[0].time - file.from) % timeframeSeconds !== 0))) {
      throw new Error("The appended candles do not match the RAW chronology and timeframe.");
    }
    if (corrections.length) assertCandles(corrections);
    if (gapCandles.length && (!assertCandles(gapCandles, timeframeSeconds) || gapCandles[0].time <= file.from
      || gapCandles.at(-1).time >= file.to || (gapCandles[0].time - file.from) % timeframeSeconds !== 0)) {
      throw new Error("The gap candles do not match the RAW chronology and timeframe.");
    }
    const signature = inventorySignature(file.dataPath, file.metaPath);
    signal.throwIfAborted();
    if (cached.signature !== signature || version(file.id) !== expectedVersion) return null;
    const previous = file.metadata;
    const dataChanged = Boolean(corrections.length || gapCandles.length || incoming.length);
    const checked = verificationSnapshots.get(verificationSnapshot);
    // A metadata-only change can use the digest already verified while reading
    // the historical comparison input. The filesystem revision must still match.
    const canReuseDigest = !dataChanged && checked?.id === file.id && checked.version === expectedVersion
      && checked.digest === previous.dataSha256;
    let originalContents;
    if (!canReuseDigest) {
      try { originalContents = await fs.promises.readFile(file.dataPath, { signal }); }
      catch (error) { if (error.code === "ENOENT") return null; throw error; }
      signal.throwIfAborted();
      if (version(file.id) !== expectedVersion) return null;
      if (createHash("sha256").update(originalContents).digest("hex") !== previous.dataSha256) {
        inventoryCache.delete(file.id);
        return null;
      }
    }
    const snapshot = {
      from: file.from, to: incoming.at(-1)?.time ?? file.to, count: file.count + incoming.length + gapCandles.length,
      dataBytes: previous.dataBytes, dataSha256: previous.dataSha256,
    };
    let prefix, suffix, trailing;
    if (dataChanged) {
      const contents = amendRawRows(originalContents, corrections, gapCandles);
      // Replace only the closing array bracket and keep surrounding whitespace intact.
      const closingBracket = contents.lastIndexOf(0x5d);
      prefix = contents.subarray(0, closingBracket);
      suffix = incoming.length ? Buffer.from(`,${JSON.stringify(incoming).slice(1)}`) : Buffer.from("]");
      trailing = contents.subarray(closingBracket + 1);
      snapshot.dataBytes = prefix.length + suffix.length + trailing.length;
      snapshot.dataSha256 = createHash("sha256").update(prefix).update(suffix).update(trailing).digest("hex");
    }
    const filename = incoming.length ? buildRawFilename({ ...file, firstTime: snapshot.from, lastTime: snapshot.to }) : path.basename(file.dataPath);
    const directory = path.dirname(file.dataPath);
    const dataPath = path.join(directory, filename);
    const metaPath = sidecarPath(dataPath);
    const renamed = dataPath !== file.dataPath;
    if (renamed && (fs.existsSync(dataPath) || fs.existsSync(metaPath))) throw new Error("A RAW file with the updated name already exists.");
    const id = path.relative(root, dataPath).split(path.sep).join("/");
    const priorVerification = previous.candleVerification;
    const candleVerification = verification ?? (!gapCandles.length && priorVerification && { ...priorVerification,
      ...summarizeVerifiedRows(priorVerification.ranges, snapshot.count) });
    const metadata = persistedMetadata({ ...file, filename, snapshot, source: previous.source, candleVerification,
      requestedRange: previous.requestedRange, farazCoverage: previous.farazCoverage, createdAt: previous.createdAt,
      updatedAt: previous.updatedAt, previousSha256: previous.dataSha256 });
    const temporary = path.join(directory, `.update-${randomUUID()}`);
    const stagedData = `${temporary}.data.tmp`;
    const stagedMeta = `${temporary}.meta.tmp`;
    let publishedMeta = false;
    let publishedData = false;
    try {
      signal.throwIfAborted();
      if (dataChanged) await fs.promises.writeFile(stagedData, [prefix, suffix, trailing], { flag: "wx", signal });
      await fs.promises.writeFile(stagedMeta, `${JSON.stringify(metadata, null, 2)}\n`, { encoding: "utf8", flag: "wx", signal });
      signal.throwIfAborted();
      if (version(file.id) !== expectedVersion || inventorySignature(file.dataPath, file.metaPath) !== signature) return null;
      if (!renamed) {
        // Both files are already staged. Restore the original bytes if the
        // sidecar replacement fails after the RAW replacement succeeds.
        if (dataChanged) fs.renameSync(stagedData, dataPath);
        try { fs.renameSync(stagedMeta, metaPath); }
        catch (error) {
          if (dataChanged) {
            fs.writeFileSync(stagedData, originalContents, { flag: "wx" });
            fs.renameSync(stagedData, dataPath);
          }
          throw error;
        }
        return cacheItem({ id, dataPath, metaPath }, metadata, snapshot, cached.timeframeSeconds);
      }
      if (fs.existsSync(dataPath) || fs.existsSync(metaPath)) throw new Error("A RAW file with the updated name already exists.");
      // Inventory discovers a resource through its data file. Install its sidecar first.
      fs.renameSync(stagedMeta, metaPath);
      publishedMeta = true;
      fs.renameSync(stagedData, dataPath);
      publishedData = true;
      fs.unlinkSync(file.dataPath);
    } catch (error) {
      if (publishedData) fs.unlinkSync(dataPath);
      if (publishedMeta) fs.unlinkSync(metaPath);
      throw error;
    } finally {
      fs.rmSync(stagedData, { force: true });
      fs.rmSync(stagedMeta, { force: true });
    }
    // A sidecar whose old RAW path no longer exists is invisible to inventory.
    try { fs.rmSync(file.metaPath, { force: true }); } catch { /* The new pair is already committed. */ }
    inventoryCache.delete(file.id);
    const committed = cacheItem({ id, dataPath, metaPath }, metadata, snapshot, timeframeSeconds);
    if (!corrections.length && !gapCandles.length && suffix.length <= MAX_APPEND_BYTES) {
      const key = appendKey(committed.chartId, snapshot.dataSha256);
      recentAppends.delete(key);
      recentAppends.set(key, { file: { id, chartId: committed.chartId, metadata: { dataSha256: snapshot.dataSha256 } },
        base: previous.dataSha256, previousId: file.id, previousTo: file.to, bytes: suffix.subarray(0, -1) });
      if (recentAppends.size > MAX_RECENT_APPENDS) recentAppends.delete(recentAppends.keys().next().value);
    }
    return committed;
  }

  function cut(id, { from, to, mode = "replace" } = {}) {
    if (!Number.isSafeInteger(Number(from)) || !Number.isSafeInteger(Number(to)) || Number(from) > Number(to)) {
      throw new Error("The cut range must be ordered and use valid candle times.");
    }
    if (!["replace", "new"].includes(mode)) throw new Error("The cut mode is invalid.");
    const item = resolve(id);
    if (!item) throw new Error("Candle file was not found.");
    const identity = parseRawFilename(path.basename(item.dataPath));
    if (!identity) throw new Error("The existing RAW filename does not follow the required contract.");
    const candles = read(id);
    const selected = candles.filter((candle) => candle.time >= Number(from) && candle.time <= Number(to));
    if (!selected.length) throw new Error("The cut range contains no candles.");
    const filename = buildRawFilename({
      broker: identity.broker,
      symbol: identity.symbol,
      timeframe: identity.timeframe,
      firstTime: selected[0].time,
      lastTime: selected.at(-1).time,
    });
    const directoryId = path.posix.dirname(item.id);
    const newId = directoryId === "." ? filename : `${directoryId}/${filename}`;
    if (mode === "new" && newId === item.id) throw new Error("A new cut file must change the selected range.");
    if (newId !== item.id && resolve(newId)) throw new Error("A candle file with the cut range already exists.");
    let previous = {};
    if (fs.existsSync(item.metaPath)) {
      try { previous = JSON.parse(fs.readFileSync(item.metaPath, "utf8")) || {}; } catch { previous = {}; }
    }
    const written = write({
      broker: identity.broker,
      symbol: identity.symbol,
      timeframe: identity.timeframe,
      candles: selected,
      source: previous.source || "cut",
      chartId: mode === "replace" ? previous.chartId : null,
      createdAt: mode === "replace" ? previous.createdAt : undefined,
    });
    if (mode === "replace" && newId !== item.id) {
      if (fs.existsSync(item.dataPath)) fs.unlinkSync(item.dataPath);
      if (fs.existsSync(item.metaPath)) fs.unlinkSync(item.metaPath);
    }
    const result = list().find((candidate) => candidate.id === written.id) || written;
    return { oldId: item.id, newId: result.id, mode, chartId: result.chartId, count: result.count, metadata: result.metadata };
  }

  function recordFarazCoverage(id, { timeframeSeconds, retryCount = 0, ranges = [], effectiveRange = null, checkedThrough = null, mode = null } = {}) {
    const item = resolve(id);
    const timeframe = Math.trunc(Number(timeframeSeconds));
    if (!item || !Number.isSafeInteger(timeframe) || timeframe < 1) return null;
    const candles = read(id);
    let previous = {};
    if (fs.existsSync(item.metaPath)) {
      try { previous = JSON.parse(fs.readFileSync(item.metaPath, "utf8")) || {}; } catch { previous = {}; }
    }
    const hydrated = runtimeMetadata(previous);
    const priorRanges = hydrated.farazCoverage?.timeframeSeconds === timeframe ? hydrated.farazCoverage.ranges || [] : [];
    const incoming = ranges.map((range) => ({ from: Math.trunc(Number(range?.from)), to: Math.trunc(Number(range?.to)), status: range?.status === "complete" ? "complete" : "source_missing", retryCount: Math.max(0, Math.trunc(Number(retryCount) || 0)) }));
    const mergedRanges = mergeFarazCoverageRanges(priorRanges, incoming, timeframe);
    const checkedFrom = mergedRanges.length ? Math.min(...mergedRanges.map((range) => range.from)) : null;
    const checkedTo = mergedRanges.length ? Math.max(...mergedRanges.map((range) => range.to)) : null;
    const fileRange = runtimeRange(effectiveRange) || { from: candles[0].time, to: candles.at(-1).time };
    let contiguousThrough = fileRange.from;
    for (const range of mergedRanges) {
      if (range.to < contiguousThrough) continue;
      if (range.from > contiguousThrough) break;
      contiguousThrough = Math.max(contiguousThrough, range.to + timeframe);
      if (contiguousThrough > fileRange.to) break;
    }
    const durableCheckpoint = checkedThrough !== null && checkedThrough !== "" && Number.isSafeInteger(Number(checkedThrough))
      ? Number(checkedThrough)
      : Number.isSafeInteger(hydrated.farazCoverage?.checkedThrough) ? hydrated.farazCoverage.checkedThrough : null;
    const chartUpToDate = durableCheckpoint !== null ? durableCheckpoint >= fileRange.to : contiguousThrough > fileRange.to;
    const coverage = { schemaVersion: 2, timeframeSeconds: timeframe, chartUpToDate, status: chartUpToDate ? "faraz_checked" : "unchecked_ranges_remain", checkedFrom, checkedTo, checkedThrough: durableCheckpoint, lastMode: mode || hydrated.farazCoverage?.lastMode || null, retryCount: Math.max(0, Math.trunc(Number(retryCount) || 0)), ranges: mergedRanges };
    const identity = parseRawFilename(path.basename(item.dataPath));
    const serialized = fs.readFileSync(item.dataPath, "utf8");
    const snapshot = snapshotData(candles, serialized);
    const metadata = persistedMetadata({ broker: identity.broker, symbol: identity.symbol, timeframe: identity.timeframe, source: previous.source || "local", filename: path.basename(item.dataPath), snapshot, requestedRange: hydrated.requestedRange, farazCoverage: coverage,
      candleVerification: previous.dataSha256 === snapshot.dataSha256 ? previous.candleVerification : undefined,
      chartId: previous.chartId, createdAt: previous.createdAt });
    atomicWrite(item.metaPath, `${JSON.stringify(metadata, null, 2)}\n`);
    inventoryCache.delete(item.id);
    return runtimeMetadata(metadata);
  }

  function remove(id) {
    const item = resolve(id);
    if (!item) return false;
    fs.unlinkSync(item.dataPath);
    if (fs.existsSync(item.metaPath)) fs.unlinkSync(item.metaPath);
    inventoryCache.delete(item.id);
    return true;
  }
  return { root, resolve, version, get, getListed, write, list, read, readForVerification, appendLatest, readAppendDelta,
    readCommittedCandleAppend, canServeAppendSnapshot, cut, recordFarazCoverage, remove };
}
