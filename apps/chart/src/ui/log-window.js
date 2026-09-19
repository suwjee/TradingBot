export function boundedLogEntries(logs, limit = 200) {
  const source = Array.isArray(logs) ? logs : [];
  const size = Math.max(1, Math.floor(Number(limit) || 200));
  return {
    entries: source.slice(-size),
    omitted: Math.max(0, source.length - size),
  };
}

export function summarizeUiError(message, limit = 180) {
  const text = String(message || "").trim();
  if (/ProtectedData|Unprotect|Key not valid for use in specified state/i.test(text)) {
    return "Saved FARAZ session could not be read in this Windows profile. Sign in again.";
  }
  const firstLine = text.split(/\r?\n/, 1)[0] || "Unexpected error";
  return firstLine.slice(0, Math.max(1, Number(limit) || 180));
}
