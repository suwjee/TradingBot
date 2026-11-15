import { formatTehranMetadataTime, parseTehranMetadataTime } from "../raw-file-contract.js";

export const DEFAULT_ALERT_SECONDS = 3;
export const MAX_ALERT_SECONDS = 300;

export const ALERT_DIRECTIONS = ["bullish", "bearish"];
const LABELS = new Map([
  ["reaction", "Reaction"], ["blue-line", "Blue Line"], ["a", "A"],
  ["s-blue", "S Blue"], ["s-red", "S Red"], ["e-blue", "E Blue family"], ["e-red", "E Red family"],
]);
const NUMBERED_LABELS = { stopall: "StopAll", ph: "PH", pl: "PL" };

function numberedType(kind, number) {
  return Number.isSafeInteger(number) && number > 0 ? `${kind}-${number}` : null;
}

export function alertEventLabel(type) {
  if (typeof type !== "string") return null;
  const [scope, qualified, extra] = type.split(":");
  if (extra !== undefined || (qualified !== undefined && !ALERT_DIRECTIONS.includes(scope))) return null;
  const event = qualified ?? scope;
  const numbered = /^(stopall|ph|pl)-([1-9]\d*)$/.exec(event);
  if (qualified !== undefined && numbered && numbered[1] !== "stopall") return null;
  const label = numbered && Number.isSafeInteger(Number(numbered[2]))
    ? `${NUMBERED_LABELS[numbered[1]]}-${numbered[2]}` : LABELS.get(event);
  return label && qualified !== undefined ? `${scope === "bullish" ? "Bullish" : "Bearish"} ${label}` : label ?? null;
}

export function normalizeAlertRule(rule) {
  const id = typeof rule?.id === "string" && rule.id;
  const name = typeof rule?.name === "string" && rule.name.trim();
  const seconds = Number(rule?.seconds);
  if (!id || !name || !Number.isInteger(seconds) || seconds < 1 || seconds > MAX_ALERT_SECONDS ||
    !Array.isArray(rule.steps) || !rule.steps.length ||
    rule.steps.some(step => !Array.isArray(step) || !step.length ||
      step.some(type => typeof type !== "string" || !alertEventLabel(type)))) return null;
  return {
    id, name, enabled: rule.enabled === true, sound: rule.sound === true, seconds,
    steps: rule.steps.map(step => [...new Set(step)]),
  };
}

function alertEvents(payload, from, through) {
  const events = new Map();
  const firstBridgeTime = formatTehranMetadataTime(from).slice(0, 19);
  const resetKey = (index, time, level) => `${index}:${time}:${level}`;
  function add(direction, type, row, sourceTime = row.sourceTime, time = row.decisionEventTime) {
    if (!type || row.calculationValid === false || !Number.isSafeInteger(time) ||
      time < from || time > through || !Number.isSafeInteger(sourceTime)) return;
    const key = JSON.stringify([direction, type, time, sourceTime, row.number ?? null]);
    events.set(key, { key, direction, type, time });
  }
  function formationTime(value, fallback) {
    if (!value) return fallback;
    return value >= firstBridgeTime ? parseTehranMetadataTime(`${value} Asia/Tehran`) : NaN;
  }
  for (const direction of ALERT_DIRECTIONS) {
    const group = payload?.directions?.[direction];
    if (!group) continue;
    const bridge = group.bridgeOutput;
    const resets = new Map((group.resets || []).map(row => [
      resetKey(row.index, row.time, row.brokenLevel), row.secondTime ?? row.time,
    ]));
    (group.reactions || []).forEach((row, index) => add(direction, "reaction", row, row.firstTime,
      formationTime(bridge?.reactions?.[index]?.structure?.breakoutCandle?.eventTime, row.breakTime)));
    (group.blueLines || []).forEach((row, index) => {
      const formedAt = bridge?.blueLines?.[index]?.formedAt;
      const resetTime = row.kind === "reset" ? resets.get(resetKey(row.sourceIndex, row.sourceTime, row.brokenLevel)) : undefined;
      const time = resetTime ?? formationTime(formedAt?.eventTime ?? formedAt?.time,
        row.kind === "reset" ? row.sourceTime : undefined);
      add(direction, "blue-line", row, row.sourceTime, time);
    });
    (group.aZones || []).forEach((row, index) => add(direction, "a", row, row.sourceTime,
      formationTime(bridge?.aZones?.[index]?.reaction?.confirmedAt?.eventTime, row.reactionBreakTime)));
    for (const row of group.stopAlls || []) add(direction, numberedType("stopall", row.number), row);
    for (const row of group.sZones || []) {
      if (row.color === "blue" || row.color === "red") add(direction, `s-${row.color}`, row);
    }
    for (const row of group.eZones || []) {
      if (row.family === "blue" || row.family === "red") add(direction, `e-${row.family}`, row);
    }
    for (const row of group.primaryHighs || []) add(direction, numberedType("ph", row.number), row);
    for (const row of group.primaryLows || []) add(direction, numberedType("pl", row.number), row);
  }
  return events;
}

export function createAlertMonitor() {
  const partial = new Map();
  let frontier = null;

  return {
    baseline(through) {
      partial.clear();
      // The RAW tail is the boundary between history and subsequent observed events.
      frontier = Number.isSafeInteger(through) ? through : null;
    },
    resetRule(id) { partial.delete(id); },
    progress(id) {
      return Math.max(0, ...Array.from(partial.get(id)?.values() || [], events => events.length));
    },
    advance(rules, payload, through, { revalidateHistory = false } = {}) {
      if (frontier === null || !Number.isSafeInteger(through) || through < frontier) return [];
      if (!rules.some(rule => rule.enabled)) {
        frontier = through;
        return [];
      }
      let firstTime = frontier + 1;
      if (revalidateHistory) {
        for (const lanes of partial.values()) {
          for (const sequence of lanes.values()) firstTime = Math.min(firstTime, sequence[0].time);
        }
      }
      const current = alertEvents(payload, firstTime, through);
      const events = [...current.values()]
        .filter(event => event.time > frontier)
        .sort((left, right) => left.time - right.time);
      frontier = through;
      const matches = [];
      for (const rule of rules) {
        if (!rule.enabled) continue;
        const directionalSteps = rule.steps.some(step => step.some(type => /:|^(ph|pl)-/.test(type)));
        const byDirection = partial.get(rule.id) || new Map();
        partial.set(rule.id, byDirection);
        if (revalidateHistory) {
          for (const [direction, sequence] of byDirection) {
            if (sequence.some(event => !current.has(event.key))) byDirection.delete(direction);
          }
        }
        for (const event of events) {
          const lane = directionalSteps ? "sequence" : event.direction;
          const sequence = byDirection.get(lane) || [];
          const previousTime = sequence.at(-1)?.time ?? -Infinity;
          const alternatives = rule.steps[sequence.length];
          if (event.time <= previousTime ||
            (!alternatives.includes(event.type) && !alternatives.includes(`${event.direction}:${event.type}`))) continue;
          sequence.push(event);
          if (sequence.length === rule.steps.length) {
            matches.push({ rule, events: sequence });
            byDirection.delete(lane);
          } else {
            byDirection.set(lane, sequence);
          }
        }
      }
      return matches.sort((left, right) => left.events.at(-1).time - right.events.at(-1).time);
    },
  };
}
