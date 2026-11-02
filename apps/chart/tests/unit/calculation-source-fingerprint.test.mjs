import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { createHash } from "node:crypto";

import { calculateSourceFingerprint } from "../../server/calculation-source-fingerprint.js";

test("source fingerprint retains original basename + NUL + binary per-file SHA-256 contract", (t) => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "tradingbot-source-fp-"));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  const files = ["one.py", "two.js"].map((name, index) => {
    const file = path.join(root, name);
    fs.writeFileSync(file, index === 0 ? "source A" : "source B");
    return file;
  });
  const reference = createHash("sha256");
  for (const filename of files) {
    reference.update(path.basename(filename));
    reference.update("\0");
    reference.update(createHash("sha256").update(fs.readFileSync(filename)).digest());
  }
  assert.equal(calculateSourceFingerprint(files), reference.digest("hex"));
  assert.notEqual(calculateSourceFingerprint([...files].reverse()), calculateSourceFingerprint(files));
});

test("same-size edits with restored timestamps still invalidate the source fingerprint", (t) => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "tradingbot-source-content-"));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  const source = path.join(root, "bridge.py");
  const originalTime = new Date(1700000000000);
  fs.writeFileSync(source, "AAAA");
  fs.utimesSync(source, originalTime, originalTime);
  const baseline = calculateSourceFingerprint([source]);
  fs.writeFileSync(source, "BBBB");
  fs.utimesSync(source, originalTime, originalTime);
  assert.notEqual(calculateSourceFingerprint([source]), baseline);
  assert.equal(calculateSourceFingerprint([source]), calculateSourceFingerprint([source]));
});
