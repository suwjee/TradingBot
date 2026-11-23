const liveReportId = /^live\/([a-zA-Z0-9._-]{1,72})\/(\d+s)\/([a-f0-9]{16})\/([a-f0-9]{32})$/;
const legacyLiveReportId = /^live\/[a-f0-9]{32}$/;
const archivedReportId = /^(?!\.{1,2}\/)[a-zA-Z0-9._-]{1,72}\/\d+s\/(?:bullish|bearish)\/\d+-\d+--[a-f0-9]{16}\.json$/;

export function liveReportLocation(id) {
  const fields = liveReportId.exec(id);
  if (!fields || fields[1] === "." || fields[1] === "..") return null;
  const [, symbol, timeframe, chartKey, revision] = fields;
  return { symbol, timeframe, chartKey, revision };
}

export function isLiveReportId(id) {
  return Boolean(liveReportLocation(id)) || legacyLiveReportId.test(id);
}

export function isCalculationReportId(id) {
  return isLiveReportId(id) || archivedReportId.test(id);
}

export function calculationInfoPath(context = {}) {
  const id = String(context.calculationId || "");
  if (!isCalculationReportId(id)) {
    throw new Error("This calculation has no persisted report identity. Calculate again first.");
  }
  return `/info/${id}${liveReportLocation(id) ? "?follow=1" : ""}`;
}

export function openManualReviewTab(context, host = window) {
  return host.open(calculationInfoPath(context), "_blank");
}
