import fs from "node:fs";
import path from "node:path";
import { createRawResourceStore } from "./raw-resource-store.js";

function legacyIdentity(filename) {
  const match = String(filename).match(/^RAW\s+(.+?)\s+(\d+[SMHD])\s+FROM\s+/i);
  if (!match) return null;
  const [brokerPart, ...symbolParts] = match[1].split("_");
  const broker = brokerPart?.trim();
  const symbol = symbolParts.join("_").trim();
  if (!broker || !symbol) return null;
  return { broker, symbol, timeframe: match[2].toUpperCase() };
}

export function migrateFlatRawFiles({ rootDir, apply = false }) {
  const report = { candidates: [], moved: [], skipped: [], errors: [] };
  if (!fs.existsSync(rootDir)) return report;
  const store = createRawResourceStore({ rootDir });
  for (const item of store.list()) {
    if (item.broker !== "FARAZ" || !String(item.symbol).includes(":")) continue;
    const [broker, symbol] = String(item.symbol).split(":", 2);
    const candidate = { filename: item.id, broker, symbol, timeframe: item.timeframe, candleCount: item.count, repair: true };
    report.candidates.push(candidate);
    if (!apply) continue;
    try {
      const candles = store.read(item.id);
      store.write({ broker, symbol, timeframe: item.timeframe, candles, filename: path.basename(item.dataPath),
        requestedRange: item.metadata.requestedRange || null, effectiveRange: item.metadata.effectiveRange || null, source: "migration-repair" });
      fs.renameSync(item.dataPath, `${item.dataPath}.migrated`);
      if (fs.existsSync(item.metaPath)) fs.renameSync(item.metaPath, `${item.metaPath}.migrated`);
      report.moved.push({ ...candidate, id: `${broker}/${symbol}/${path.basename(item.dataPath)}` });
    } catch (error) { report.errors.push({ filename: item.id, reason: error.message }); }
  }
  for (const entry of fs.readdirSync(rootDir, { withFileTypes: true })) {
    if (!entry.isFile() || !entry.name.endsWith(".json") || entry.name.endsWith(".meta.json")) continue;
    const legacy = legacyIdentity(entry.name);
    if (!legacy) { report.skipped.push({ filename: entry.name, reason: "Unsupported legacy filename" }); continue; }
    const legacyPath = path.join(rootDir, entry.name);
    let candles;
    try { candles = JSON.parse(fs.readFileSync(legacyPath, "utf8")); }
    catch { report.errors.push({ filename: entry.name, reason: "Invalid JSON" }); continue; }
    const candidate = { filename: entry.name, ...legacy, candleCount: Array.isArray(candles) ? candles.length : 0 };
    report.candidates.push(candidate);
    if (!apply) continue;
    try {
      const item = store.write({ ...legacy, candles, source: "legacy-migration" });
      fs.renameSync(legacyPath, `${legacyPath}.migrated`);
      report.moved.push({ ...candidate, id: item.id });
    } catch (error) { report.errors.push({ filename: entry.name, reason: error.message }); }
  }
  return report;
}
