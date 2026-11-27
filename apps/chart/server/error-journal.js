import { errorDetails, scrubDiagnostic } from "../src/features/diagnostic-details.js";
import fs from "node:fs";
import path from "node:path";
import { createHash, randomUUID } from "node:crypto";
import { readBoundedBody } from "./request-body.js";
import { writeAtomicCalculationCache } from "./calculation-cache.js";

const MAX_ENTRY_BYTES = 512 * 1024;
export function createErrorJournal(cacheRoot) {
  const file = path.join(cacheRoot, "error-journal.jsonl");
  function read() {
    try {
      return fs.readFileSync(file, "utf8").split("\n").filter(Boolean).map(line => {
        try { return JSON.parse(line); }
        catch { return { id: `recovery:${createHash("sha256").update(line).digest("hex")}`, scope: "SERVER", level: "ERROR",
          event: "DAMAGED_JOURNAL_RECORD", error: "A journal record could not be decoded." }; }
      });
    } catch (error) {
      if (error.code === "ENOENT") return [];
      throw error;
    }
  }

  const known = new Set();
  let indexed = false;
  let clearedAt = 0;
  function append(input) {
    if (!indexed) {
      for (const row of read()) {
        if (row.clearedAt) clearedAt = row.clearedAt;
        else known.add(row.id);
      }
      indexed = true;
    }
    if (Number.isSafeInteger(input.recordedAt) && input.recordedAt <= clearedAt) return;
    const { clearedAt: _ignored, ...diagnostic } = scrubDiagnostic(input);
    const entry = { ...diagnostic, id: input.id || randomUUID(), recordedAt: input.recordedAt ?? Date.now() };
    if (known.has(entry.id)) return;
    fs.mkdirSync(cacheRoot, { recursive: true });
    fs.appendFileSync(file, JSON.stringify(entry) + "\n", "utf8");
    known.add(entry.id);
  }

  async function api(req, res) {
    const send = (status, body) => {
      res.writeHead(status, { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store" });
      res.end(JSON.stringify(body));
    };
    try {
      if (req.method === "GET") return send(200, { entries: read().filter(row => row.id) });
      if (req.method === "DELETE") {
        const cutoff = Date.now();
        writeAtomicCalculationCache(file, JSON.stringify({ clearedAt: cutoff }) + "\n");
        clearedAt = cutoff;
        indexed = true;
        known.clear();
        return send(200, { cleared: true });
      }
      if (req.method !== "POST") return send(405, { error: "Method not allowed." });
      if (req.headers["content-type"]?.split(";")[0] !== "application/json") return send(415, { error: "JSON required." });
      let entry;
      try { entry = JSON.parse(await readBoundedBody(req, MAX_ENTRY_BYTES)); }
      catch { return send(400, { error: "Invalid diagnostic record." }); }
      if (!entry || !/^[a-zA-Z0-9-]{8,80}$/.test(entry.id || "") || typeof entry.event !== "string"
          || !Number.isSafeInteger(entry.recordedAt) || !["WARN", "ERROR"].includes(entry.level)) {
        return send(400, { error: "Invalid diagnostic fields." });
      }
      append(entry);
      return send(200, { saved: true });
    } catch (error) {
      console.error("Error journal I/O failed", error);
      return send(500, { error: "The local error journal could not be accessed." });
    }
  }

  function observe(req, res, next) {
    const route = (req.url || "").split("?")[0];
    if (!route.startsWith("/api/") || route === "/api/error-journal") return next();
    const end = res.end;
    res.end = function (body, ...args) {
      if (res.statusCode >= 500 && !res.errorJournalCaptured) {
        try {
          let details;
          const text = typeof body === "string" || Buffer.isBuffer(body) ? body.toString() : "";
          try { details = JSON.parse(text); } catch { details = text; }
          append({ scope: "SERVER", level: "ERROR", event: "API_REQUEST_FAILED", method: req.method,
            route, status: res.statusCode, response: details });
        } catch (error) { console.error("Error journal write failed", error); }
      }
      return end.call(this, body, ...args);
    };
    next();
  }

  function capture(res, event, error, context = {}) {
    try {
      append({ scope: "SERVER", level: "ERROR", event, ...context, ...errorDetails(error) });
      res.errorJournalCaptured = true;
    } catch (failure) { console.error("Error journal write failed", failure); }
  }

  return { api, observe, capture };
}
