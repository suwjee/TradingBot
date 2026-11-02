// Presentation-only selection resolution. Preserve the historical selected-ID
// order, duplicates and fallback to the Indicator map without persisting an index.
export function partitionObjectTreeSelection(selectedIds, drawings, indicatorMap) {
  const drawingIds = new Set(drawings.map((drawing) => drawing.id));
  return {
    manualIds: selectedIds.filter((id) => drawingIds.has(id)),
    indicatorIds: selectedIds.filter((id) => indicatorMap.has(id)),
  };
}
