import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

import { assertRawInputUnchanged, captureRawInputIdentity } from "../../server/raw-input-identity.js";

test("queued calculations reject a RAW file changed after selection", async () => {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), "tradingbot-raw-identity-"));
  const sourcePath = path.join(directory, "candles.json");
  try {
    fs.writeFileSync(sourcePath, "[]");
    const selected = await captureRawInputIdentity(sourcePath);
    await assert.doesNotReject(assertRawInputUnchanged(sourcePath, selected));
    fs.writeFileSync(sourcePath, "[1]");
    await assert.rejects(assertRawInputUnchanged(sourcePath, selected), /RAW file changed/i);
    fs.rmSync(sourcePath);
    await assert.rejects(assertRawInputUnchanged(sourcePath, selected), /RAW file changed/i);
  } finally {
    fs.rmSync(directory, { recursive: true, force: true });
  }
});

test("RAW identity detects same-size content changes with a preserved mtime", async () => {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), "tradingbot-raw-hash-"));
  const sourcePath = path.join(directory, "candles.json");
  try {
    const fixedTime = new Date(1_700_000_000_000);
    fs.writeFileSync(sourcePath, "[1]");
    fs.utimesSync(sourcePath, fixedTime, fixedTime);
    const selected = await captureRawInputIdentity(sourcePath);
    fs.writeFileSync(sourcePath, "[2]");
    fs.utimesSync(sourcePath, fixedTime, fixedTime);
    const changed = await captureRawInputIdentity(sourcePath);
    assert.notEqual(changed.sha256, selected.sha256);
    await assert.rejects(assertRawInputUnchanged(sourcePath, selected), /RAW file changed/i);
  } finally {
    fs.rmSync(directory, { recursive: true, force: true });
  }
});
