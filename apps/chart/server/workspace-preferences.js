import fs from "node:fs";
import path from "node:path";
import { writeAtomicCalculationCache } from "./calculation-cache.js";
import { readBoundedBody } from "./request-body.js";

const CHART_KEY = /^(indicator|realtime|bookmark):[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$/i;
const COLOR = /^#[a-f0-9]{6}$/i;
const MAX_REQUEST_BYTES = 16 * 1024;
const isRecord = (value) => value != null && typeof value === "object" && !Array.isArray(value);

function validForm(value) {
  return isRecord(value) && isRecord(value.controls)
    && [null, "bullish", "bearish"].includes(value.direction)
    && Object.entries(value.controls).every(([id, control]) => (
      /^[a-z][\w-]{0,63}$/i.test(id)
      && (typeof control === "boolean" || Number.isFinite(control)
        || (typeof control === "string" && control.length <= 128))
    ));
}

function validPreference(key, value) {
  if (key === "drawing-order") {
    return Array.isArray(value) && value.length <= 32
      && value.every((item) => typeof item === "string" && /^[a-z]{1,24}$/.test(item));
  }
  if (key === "drawing-style") {
    return isRecord(value) && Object.keys(value).length === 5 && COLOR.test(value.stroke) && COLOR.test(value.fill)
      && Number.isFinite(value.width) && value.width > 0 && value.width <= 20
      && ["solid", "dash", "dot"].includes(value.style)
      && Number.isFinite(value.opacity) && value.opacity >= 0 && value.opacity <= 1;
  }
  if (key === "drawing-toolbar-position") {
    return isRecord(value) && Object.keys(value).length === 2
      && Number.isFinite(value.left) && Number.isFinite(value.top);
  }
  if (key === "drawing-text-size") return [9, 11, 13, 14, 16].includes(value);
  if (key === "indicator-default") return validForm(value);
  if (key === "indicator-enabled") return typeof value === "boolean";
  switch (key === "realtime-default" ? "realtime" : typeof key === "string" && key.match(CHART_KEY)?.[1]) {
    case "bookmark":
      return typeof value === "boolean";
    case "realtime":
      return isRecord(value) && Object.keys(value).length === 3
        && typeof value.enabled === "boolean" && typeof value.indicatorCalculation === "boolean"
        && Number.isSafeInteger(value.intervalMs) && value.intervalMs > 0;
    case "indicator":
      return isRecord(value) && Object.keys(value).every(key => ["form", "from", "to", "enabled"].includes(key))
        && (!Object.hasOwn(value, "enabled") || typeof value.enabled === "boolean") && validForm(value.form)
        && typeof value.from === "string" && value.from.length <= 32
        && typeof value.to === "string" && value.to.length <= 32;
    default:
      return false;
  }
}

export function createWorkspacePreferencesApi(cacheRoot) {
  const file = path.join(cacheRoot, "workspace-preferences.json");

  function readPreferences() {
    try {
      const stored = JSON.parse(fs.readFileSync(file, "utf8"));
      if (!isRecord(stored) || stored.version !== 1 || !isRecord(stored.preferences)
        || !Object.entries(stored.preferences).every(([key, value]) => validPreference(key, value))) {
        throw new Error("Invalid workspace preferences file.");
      }
      return stored.preferences;
    } catch (error) {
      if (error.code === "ENOENT") return {};
      throw error;
    }
  }

  return async function workspacePreferences(req, res, next) {
    if (!["", "/"].includes(req.url?.split("?")[0])) return next();
    const send = (status, body) => {
      res.statusCode = status;
      res.setHeader("Content-Type", "application/json; charset=utf-8");
      res.setHeader("Cache-Control", "no-store");
      res.end(JSON.stringify(body));
    };
    if (!["GET", "PATCH"].includes(req.method)) {
      res.setHeader("Allow", "GET, PATCH");
      return send(405, { error: "Method not allowed." });
    }
    try {
      if (req.method === "GET") return send(200, { preferences: readPreferences() });
      if (req.headers["content-type"]?.split(";")[0].trim() !== "application/json") {
        return send(415, { error: "Workspace preferences require JSON." });
      }
      let update;
      try {
        update = JSON.parse(await readBoundedBody(req, MAX_REQUEST_BYTES));
      } catch {
        return send(400, { error: "Invalid workspace preference request." });
      }
      if (!isRecord(update) || !validPreference(update.key, update.value)) {
        return send(400, { error: "Invalid workspace preference." });
      }
      const preferences = readPreferences();
      preferences[update.key] = update.value;
      writeAtomicCalculationCache(file, JSON.stringify({ version: 1, preferences }));
      return send(200, { saved: true });
    } catch {
      return send(500, { error: "Workspace preferences are unavailable." });
    }
  };
}
