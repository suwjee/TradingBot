import { parseTehranMetadataTime } from "./raw-file-contract.js";

function creationTime(item) {
  try {
    const createdAt = parseTehranMetadataTime(item.createdAt ?? item.metadata?.createdAt);
    if (Number.isFinite(createdAt)) return createdAt * 1000;
  } catch { /* Legacy metadata can omit a valid creation time. */ }
  const savedAt = Number(item.savedAt);
  return Number.isFinite(savedAt) ? savedAt : 0;
}

export function orderSymbolFiles(files, isBookmarked = () => false) {
  return files.map((item) => ({ item, createdAt: creationTime(item), bookmarked: isBookmarked(item) }))
    .sort((left, right) => Number(right.bookmarked) - Number(left.bookmarked)
      || right.createdAt - left.createdAt || left.item.id.localeCompare(right.item.id))
    .map(({ item }) => item);
}
