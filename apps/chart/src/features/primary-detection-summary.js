// Human-readable presentation of finalized Engine counts and status codes.
const PRIMARY_STATUS_LABELS = Object.freeze({
  "waiting-for-matching-behaviors": "Waiting for a qualified matching-behavior leg.",
  "waiting-for-stopall-break": "Waiting for price to cross a qualified StopAll level.",
  "waiting-for-structure-break": "Waiting for price to cross the latest PH or PL level.",
  "waiting-for-ph-order-stop": "Waiting for a valid PH order to stop.",
  "waiting-for-pl-order-stop": "Waiting for a valid PL order to stop.",
  "post-pl3-orders-only": "Evaluating valid orders after PL-3.",
  "ambiguous-raw-boundary-order": "The available RAW candles cannot determine which event happened first.",
});

export function primaryDetectionSummary(group = {}) {
  const count = key => Array.isArray(group[key]) ? group[key].length : 0;
  const status = group.primaryStatus;
  return {
    highs: count("primaryHighs"), lows: count("primaryLows"), legs: count("matchingBehaviorLegs"),
    statusLabel: status == null
      ? "PH/PL was not calculated for this result."
      : PRIMARY_STATUS_LABELS[status] || "PH/PL status is not available.",
  };
}
