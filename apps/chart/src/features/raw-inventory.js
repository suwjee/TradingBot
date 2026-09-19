export function rawInventoryPresentation(item, formatTime) {
  const id = String(item?.id || "");
  const filename = id.split("/").at(-1) || "RAW resource";
  const broker = String(item?.broker || "UNKNOWN");
  const symbol = String(item?.symbol || "Unnamed dataset");
  const timeframe = String(item?.timeframe || "UNKNOWN");
  const count = Number(item?.count || 0);
  const bytes = Number(item?.bytes || 0);
  const normalizedSymbol = symbol.replaceAll("_", ":");
  return {
    id,
    filename,
    symbol: normalizedSymbol.split(":").at(-1) || normalizedSymbol,
    title: normalizedSymbol.includes(":") ? normalizedSymbol : `${broker}:${normalizedSymbol}`,
    detail: `${timeframe} · ${count.toLocaleString("en-US")} candles · ${(bytes / 1048576).toFixed(2)} MB`,
    range: `${formatTime(item?.from)} → ${formatTime(item?.to)}`,
  };
}

function sortableValue(item, key) {
  if (key === "filename") return String(item?.id || "").split("/").at(-1) || "";
  if (["createdAt", "updatedAt", "savedAt"].includes(key)) {
    const tehranSeconds = parseTehranMetadataTime(item?.[key]);
    if (Number.isFinite(tehranSeconds)) return tehranSeconds * 1000;
    const value = Date.parse(item?.[key]);
    return Number.isFinite(value) ? value : Number(item?.[key]) || 0;
  }
  if (["count", "bytes", "from", "to"].includes(key)) return Number(item?.[key]) || 0;
  return String(item?.[key] || "").toLocaleUpperCase();
}

export function sortRawInventory(items, { key = "updatedAt", direction = "desc" } = {}) {
  const order = direction === "asc" ? 1 : -1;
  return [...items].sort((left, right) => {
    const a = sortableValue(left, key), b = sortableValue(right, key);
    const compared = typeof a === "string" ? a.localeCompare(b) : a - b;
    return compared * order || String(left.id).localeCompare(String(right.id));
  });
}
import { parseTehranMetadataTime } from "./raw-file-contract.js";
