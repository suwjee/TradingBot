const QUALIFIED_FARAZ_SYMBOL = /^[A-Z0-9][A-Z0-9._-]*:[A-Z0-9][A-Z0-9._-]*$/;
const BARE_FARAZ_SYMBOL = /^[A-Z0-9][A-Z0-9._-]*$/;

export function isQualifiedFarazSymbol(value) {
  return QUALIFIED_FARAZ_SYMBOL.test(String(value || "").trim().toUpperCase());
}

export function normalizeFarazSymbol(value, fallback = "") {
  const requested = String(value || "").trim().toUpperCase();
  const defaultSymbol = String(fallback || "").trim().toUpperCase();
  if (isQualifiedFarazSymbol(requested)) return requested;
  if (BARE_FARAZ_SYMBOL.test(requested)) {
    if (isQualifiedFarazSymbol(defaultSymbol) && defaultSymbol.split(":").at(-1) === requested) return defaultSymbol;
    return requested;
  }
  return isQualifiedFarazSymbol(defaultSymbol) ? defaultSymbol : "";
}
