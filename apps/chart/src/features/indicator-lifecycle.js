const CONTEXT_KEYS = [
  "fileId",
  "symbol",
  "chartTimeframe",
  "analysisTimeframe",
  "from",
  "to",
  "direction",
];

export function restoreIndicatorLifecycle(saved) {
  return {
    form: saved?.form && typeof saved.form === "object" ? saved.form : null,
    from: typeof saved?.from === "string" ? saved.from : "",
    to: typeof saved?.to === "string" ? saved.to : "",
    active: false,
    resultContext: null,
  };
}

export function appliedContextMatches(applied, next) {
  return Boolean(applied && next)
    && CONTEXT_KEYS.every((key) => applied[key] === next[key]);
}
