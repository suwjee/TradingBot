// Synthetic presentation records only: not a verified trading example.
export const reviewFixture = {
  engine: "synthetic-presentation-fixture", timeframe: 30,
  actualFrom: 1780000000, actualTo: 1780000900,
  directions: Object.fromEntries(["bullish", "bearish"].map((direction) => [direction, {
    reactions: [{ firstTime: 1780000000, boxTop: "12.340000", boxBottom: "11.0000", mode: "fixture" }],
    resets: [{ time: 1780000030, brokenLevel: "11.0000" }],
    blueLines: [{ sourceTime: 1780000060, linePrice: "12.1234567890123456789" }],
    aZones: [{ sourceTime: 1780000090, price: "11.9000" }],
    sZones: [{ sourceTime: 1780000120, color: "red", price: "11.8000" }],
    eZones: [{ sourceTime: 1780000150, family: "blue", number: 2, orderCauses: ["Order_A", "Order_B"] }],
    stopAlls: [{ sourceTime: 1780000180, number: 1, stopLevel: "11.1000" }],
    orderReactions: [{ firstTime: 1780000210, direction, consumed: false, stopHitEventTime: null }],
    orderAudit: [{ firstTime: 1780000240, causes: [], extra: { untouched: true } }],
  }]))
};
