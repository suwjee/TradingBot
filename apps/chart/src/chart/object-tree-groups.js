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
