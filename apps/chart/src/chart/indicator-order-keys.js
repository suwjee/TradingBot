// Presentation-only suppression index for order-audit rectangles.
// The canonical Engine results remain authoritative and untouched.
const ORDER_ZONE_FIELDS = Object.freeze(["sZones", "eZones", "stopAlls"]);

export function representedOrderKeys(group) {
  const keys = new Set();
  for (const field of ORDER_ZONE_FIELDS) {
    for (const item of group[field] || []) {
      if (item.calculationValid === false ||
          item.orderFirstIndex == null || item.orderBreakIndex == null) continue;
      keys.add(`${item.orderFirstIndex}:${item.orderBreakIndex}`);
    }
  }
  return keys;
}
