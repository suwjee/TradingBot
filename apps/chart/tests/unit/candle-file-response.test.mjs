import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { Writable } from "node:stream";

import { sendCandleFile } from "../../server/candle-file-response.js";

function responseCapture() {
  const headers = new Map();
  const chunks = [];
  const response = new Writable({
    write(chunk, _encoding, callback) {
      chunks.push(Buffer.from(chunk));
      callback();
    },
  });
  response.statusCode = 200;
  response.setHeader = (name, value) => headers.set(name.toLowerCase(), String(value));
  return { response, headers, chunks };
}

test("candle responses revalidate an unchanged RAW file across browser tabs", async (t) => {
  const rootDir = fs.mkdtempSync(path.join(os.tmpdir(), "candle-response-"));
  t.after(() => fs.rmSync(rootDir, { recursive: true, force: true }));
  const dataPath = path.join(rootDir, "raw.json");
  const payload = JSON.stringify([{ time: 100, open: 1, high: 1, low: 1, close: 1 }]);
  fs.writeFileSync(dataPath, payload);

  const first = responseCapture();
  await sendCandleFile({ headers: {} }, first.response, dataPath);
  assert.equal(Buffer.concat(first.chunks).toString("utf8"), payload);
  assert.equal(first.headers.get("cache-control"), "private, no-cache");
  assert.ok(first.headers.get("etag"));

  const second = responseCapture();
  await sendCandleFile({ headers: { "if-none-match": first.headers.get("etag") } }, second.response, dataPath);
  assert.equal(second.response.statusCode, 304);
  assert.equal(Buffer.concat(second.chunks).length, 0);
});

test("a same-size edit with the original mtime sends current RAW bytes", async t => {
  const rootDir = fs.mkdtempSync(path.join(os.tmpdir(), "candle-rewrite-"));
  t.after(() => fs.rmSync(rootDir, { recursive: true, force: true }));
  const dataPath = path.join(rootDir, "raw.json");
  const savedTime = new Date("2026-01-02T03:04:05Z");
  fs.writeFileSync(dataPath, "[1]");
  fs.utimesSync(dataPath, savedTime, savedTime);
  const first = responseCapture();
  await sendCandleFile({ headers: {} }, first.response, dataPath);

  const replacement = path.join(rootDir, "replacement.json");
  fs.writeFileSync(replacement, "[2]");
  fs.utimesSync(replacement, savedTime, savedTime);
  fs.renameSync(replacement, dataPath);
  const second = responseCapture();
  await sendCandleFile({ headers: { "if-none-match": first.headers.get("etag") } }, second.response, dataPath);
  assert.equal(second.response.statusCode, 200);
  assert.equal(Buffer.concat(second.chunks).toString(), "[2]");
});

test("a disconnected client settles the file stream", { timeout: 1_000 }, async t => {
  const rootDir = fs.mkdtempSync(path.join(os.tmpdir(), "candle-disconnect-"));
  t.after(() => fs.rmSync(rootDir, { recursive: true, force: true }));
  const dataPath = path.join(rootDir, "raw.json");
  fs.writeFileSync(dataPath, Buffer.alloc(256 * 1024));
  const response = new Writable({ write() { this.destroy(); } });
  response.setHeader = () => {};
  await assert.rejects(sendCandleFile({ headers: {} }, response, dataPath), { code: "ERR_STREAM_PREMATURE_CLOSE" });
});
