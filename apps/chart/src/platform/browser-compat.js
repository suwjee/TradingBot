// Chrome 89 is the supported baseline across Windows, macOS, Linux, ChromeOS,
// and Android. Keep API fallbacks here so the workstation starts cleanly on
// older managed Chrome installations too.
if (!Array.prototype.at) {
  Object.defineProperty(Array.prototype, "at", {
    configurable: true,
    value(index) {
      const offset = Number(index) || 0;
      const integer = offset < 0 ? Math.ceil(offset) : Math.floor(offset);
      const position = integer < 0 ? this.length + integer : integer;
      return this[position];
    },
    writable: true,
  });
}

if (typeof globalThis.structuredClone !== "function") {
  globalThis.structuredClone = function structuredCloneFallback(value, seen = new Map()) {
    if (value === null || typeof value !== "object") return value;
    if (seen.has(value)) return seen.get(value);
    if (value instanceof Date) return new Date(value.getTime());

    const copy = Array.isArray(value) ? [] : Object.create(Object.getPrototypeOf(value));
    seen.set(value, copy);
    for (const key of Object.keys(value)) {
      copy[key] = structuredCloneFallback(value[key], seen);
    }
    return copy;
  };
}
