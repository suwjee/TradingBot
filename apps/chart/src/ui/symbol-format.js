const tehranInventoryClock = new Intl.DateTimeFormat("en-US", {
  timeZone: "Asia/Tehran", hourCycle: "h23",
  year: "numeric", month: "2-digit", day: "2-digit",
  hour: "2-digit", minute: "2-digit", second: "2-digit",
});

export function formatInventoryDateTime(value) {
  const text = String(value ?? "");
  if (/^\d{9,12}$/.test(text) && Number.isSafeInteger(Number(text))) {
    const date = new Date(Number(text) * 1000);
    if (Number.isFinite(date.getTime())) {
      const fields = Object.fromEntries(tehranInventoryClock.formatToParts(date)
        .filter((part) => part.type !== "literal").map((part) => [part.type, part.value]));
      return `${fields.year}-${fields.month}-${fields.day} ${fields.hour}:${fields.minute}:${fields.second}`;
    }
  }
  return text.replace(
    /^(\d{4}-\d{2}-\d{2}[ T])(\d{2})-(\d{2})-(\d{2})(.*)$/,
    "$1$2:$3:$4$5",
  );
}

export function formatSymbolWithBroker(item = {}) {
  const broker = String(item.broker || "").trim().replaceAll("_", ":");
  const symbol = String(item.symbol || "").trim().replaceAll("_", ":");
  if (!broker || !symbol || symbol.includes(":")) return symbol || broker || "—";
  return `${broker}:${symbol}`;
}
