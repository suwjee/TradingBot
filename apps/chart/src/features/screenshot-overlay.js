function tehranTimestamp(date) {
  const parts = Object.fromEntries(new Intl.DateTimeFormat("en-CA", {
    timeZone: "Asia/Tehran", year: "numeric", month: "2-digit", day: "2-digit",
    hour: "2-digit", minute: "2-digit", second: "2-digit", hourCycle: "h23",
  }).formatToParts(date).map((part) => [part.type, part.value]));
  return `${parts.year}-${parts.month}-${parts.day} ${parts.hour}:${parts.minute}:${parts.second}`;
}

export function drawScreenshotOverlay(context, { symbol, timeframe, capturedAt = new Date() }) {
  const first = `${symbol || "Chart"} · ${timeframe || "—"}`;
  const second = `Asia/Tehran · ${tehranTimestamp(capturedAt)}`;
  context.save();
  context.font = "600 15px system-ui, sans-serif";
  const width = Math.max(context.measureText(first).width, context.measureText(second).width) + 28;
  context.fillStyle = "rgba(255,255,255,.94)";
  context.fillRect(16, 16, width, 58);
  context.fillStyle = "#14213d";
  context.fillText(first, 28, 39);
  context.font = "12px system-ui, sans-serif";
  context.fillStyle = "#475569";
  context.fillText(second, 28, 61);
  context.restore();
}
