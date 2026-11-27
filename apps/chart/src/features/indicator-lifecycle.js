export function restoreIndicatorLifecycle(saved) {
  return {
    form: saved?.form && typeof saved.form === "object" ? saved.form : null,
    from: typeof saved?.from === "string" ? saved.from : "",
    to: typeof saved?.to === "string" ? saved.to : "",
    active: false,
    resultContext: null,
  };
}

export function engineCalculationDuration(payload) {
  const duration = payload?.timings?.bridgeTotalMs;
  return Number.isFinite(duration) && duration >= 0 ? duration : null;
}

export function captureCalculationInputs({ file, chartTimeframe, raw, data, settings,
  from, to, enabled, results, resultContext }) {
  return Object.freeze({
    fileIdentity: JSON.stringify([file?.id, file?.chartId, file?.symbol, file?.timeframe,
      file?.from, file?.to, file?.count, file?.bytes, file?.savedAt]),
    chartTimeframe, raw, data,
    rawLength: raw?.length, rawFirst: raw?.[0]?.time, rawLast: raw?.[raw.length - 1]?.time,
    dataLength: data?.length, dataFirst: data?.[0]?.time, dataLast: data?.[data.length - 1]?.time,
    settingsIdentity: JSON.stringify(settings), from, to, enabled,
    results, resultContext, resultFingerprint: resultContext?.sourceFingerprint,
  });
}

export function calculationInputsMatch(snapshot, current) {
  return Boolean(snapshot && current)
    && Object.keys(snapshot).every(key => snapshot[key] === current[key]);
}

export function migrateIndicatorVisibility(controls) {
  const { trueFalseVisible, ...migrated } = controls;
  for (const prefix of ["foundation", "secondary", "primary"]) {
    const key = `${prefix}TfNaColor`;
    if (migrated[key] === "#b8b8b8") migrated[key] = "#808080";
  }
  if (typeof trueFalseVisible === "boolean") {
    for (const key of ["foundationTfVisible", "secondaryTfVisible", "primaryTfVisible"]) {
      migrated[key] ??= trueFalseVisible;
    }
  }
  for (const prefix of ["ph", "pl", "mbl"]) {
    const group = `${prefix}GroupVisible`;
    const marker = `${prefix}Visible`;
    const label = `${prefix}LabelVisible`;
    if ((marker in controls) || (label in controls)) {
      migrated[group] ??= controls[marker] !== false || controls[label] !== false;
      delete migrated[marker];
      delete migrated[label];
    }
  }
  return migrated;
}
