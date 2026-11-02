// Index only for a single Object Tree render. The authoritative drawing order
// stays in the original array; no persistent cache or mutation is introduced.
export function groupDrawingsForTree(drawings, folders, query = "", names = {}) {
  const groups = new Map(folders.map((folder) => [folder.id, []]));
  for (const drawing of drawings) {
    const folderId = drawing.folderId || "manual-unfiled";
    const items = groups.get(folderId);
    if (!items) continue;
    if (query && !`${names[drawing.type] || drawing.type}`.toLowerCase().includes(query)) continue;
    items.push(drawing);
  }
  return groups;
}

/**
 * Build the two display-only Indicator Object Tree buckets in one traversal.
 * A row whose identity contains both direction tokens intentionally appears in
 * both buckets, matching the historical independent per-direction filters.
 */
export function groupIndicatorRowsForTree(objects, query = "") {
  const visible = [];
  const byDirection = { bullish: [], bearish: [] };
  for (const item of objects) {
    if (query && !`${item.name} ${item.type}`.toLowerCase().includes(query)) continue;
    visible.push(item);
    if (item.id.includes(":bullish:")) byDirection.bullish.push(item);
    if (item.id.includes(":bearish:")) byDirection.bearish.push(item);
  }
  return { visible, byDirection };
}
