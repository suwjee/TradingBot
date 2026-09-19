import test from "node:test";
import assert from "node:assert/strict";

import { boundedLogEntries, summarizeUiError } from "../src/ui/log-window.js";

test("FARAZ log rendering keeps the newest bounded window", () => {
  const logs = Array.from({ length: 260 }, (_, index) => ({ message: `event-${index}` }));
  const result = boundedLogEntries(logs, 200);
  assert.equal(result.omitted, 60);
  assert.equal(result.entries.length, 200);
  assert.equal(result.entries[0].message, "event-60");
  assert.equal(result.entries.at(-1).message, "event-259");
});

test("FARAZ credential failures are concise and actionable in the UI", () => {
  const raw = 'Command failed: powershell.exe -Command ProtectedData.Unprotect Key not valid for use in specified state';
  assert.equal(summarizeUiError(raw), "Saved FARAZ session could not be read in this Windows profile. Sign in again.");
});

test("generic UI errors are bounded to one line", () => {
  assert.equal(summarizeUiError("First line\ninternal stack detail"), "First line");
  assert.equal(summarizeUiError("x".repeat(220)).length, 180);
});
