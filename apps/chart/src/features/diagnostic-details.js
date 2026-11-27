const secretKey = /authorization|cookie|password|secret|token|api[-_ ]?key|session[-_ ]?(?:id|value)/i;

export function scrubDiagnostic(value, depth = 0) {
  if (depth > 15) return "[nested diagnostic]";
  if (typeof value === "string") {
    return value.replace(/(https?:\/\/[^\s?#]+)[?#][^\s"'<>]+/gi, "$1?[redacted]")
      .replace(/(\bBearer\s+)[^\s"',]+/gi, "$1[redacted]")
      .replace(/((?:cookie|authorization|password|secret|access[_-]?token|refresh[_-]?token|api[_-]?key)["']?\s*[:=]\s*)[^\r\n,}]+/gi, "$1[redacted]");
  }
  if (Array.isArray(value)) return value.map(item => scrubDiagnostic(item, depth + 1));
  if (value && typeof value === "object") {
    return Object.fromEntries(Object.entries(value).map(([key, item]) => [key,
      secretKey.test(key) ? "[redacted]" : scrubDiagnostic(item, depth + 1)]));
  }
  return value;
}

export function errorDetails(error, depth = 0) {
  if (!(error instanceof Error) || depth >= 6) return { error: String(error) };
  return {
    error: error.message, errorType: error.name, stack: error.stack, code: error.code,
    cause: error.cause === undefined ? undefined : errorDetails(error.cause, depth + 1),
    errors: error instanceof AggregateError ? error.errors.map(item => errorDetails(item, depth + 1)) : undefined,
  };
}
