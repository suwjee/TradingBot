import test from "node:test";
import assert from "node:assert/strict";
import { Readable } from "node:stream";

import { readBoundedBody } from "../../server/request-body.js";

function request(chunks, headers = {}) {
  const stream = Readable.from(chunks);
  stream.headers = headers;
  return stream;
}

test("body reader accepts exact byte limit and frees listeners", async () => {
  const req = request(["ab", "cd"], { "content-length": "4" });
  assert.equal(await readBoundedBody(req, 4), "abcd");
  assert.equal(req.listenerCount("data"), 0);
  assert.equal(req.listenerCount("end"), 0);
  assert.equal(req.listenerCount("error"), 0);
});

test("body reader accepts empty and chunked bodies below the limit", async () => {
  assert.equal(await readBoundedBody(request([]), 0), "");
  assert.equal(await readBoundedBody(request(["a", "b", "c"], { "transfer-encoding": "chunked" }), 4), "abc");
});

test("body reader counts UTF-8 bytes without relying on Content-Length", async () => {
  await assert.rejects(readBoundedBody(request(["éé"]), 3), /too large/i);
  await assert.rejects(readBoundedBody(request(["abcdef"], { "content-length": "2" }), 4), /too large/i);
  assert.equal(await readBoundedBody(request(["é"], { "content-length": "2" }), 2), "é");
});

test("body reader counts actual wire bytes even for malformed UTF-8", async () => {
  assert.equal(await readBoundedBody(request([Buffer.from([0xff])]), 1), "�");
  assert.equal(await readBoundedBody(request([Buffer.from([0xc3]), Buffer.from([0xa9])]), 2), "é");
});

test("body reader rejects actual bytes above the limit", async () => {
  const req = request(["abcde"], { "content-length": "5" });
  await assert.rejects(readBoundedBody(req, 4), /too large/i);
  assert.equal(req.listenerCount("data"), 0);
});

test("body reader judges a mismatched large Content-Length by received bytes", async () => {
  const req = request(["abc"], { "content-length": "999" });
  assert.equal(await readBoundedBody(req, 4), "abc");
});

test("body reader rejects an aborted request and frees listeners", async () => {
  const req = new Readable({ read() {} });
  req.headers = {};
  const result = readBoundedBody(req, 4);
  req.push("ab");
  req.emit("aborted");
  await assert.rejects(result, /aborted/i);
  req.emit("close");
  assert.equal(req.listenerCount("data"), 0);
  assert.equal(req.listenerCount("aborted"), 0);
  req.destroy();
});

test("an oversized body drains a later stream error without crashing", async () => {
  const req = new Readable({ read() {} });
  req.headers = {};
  const result = readBoundedBody(req, 4);
  req.push("abcde");
  await assert.rejects(result, /too large/i);
  assert.doesNotThrow(() => req.emit("error", new Error("socket reset")));
  assert.doesNotThrow(() => req.emit("error", new Error("socket reset again")));
  req.emit("close");
  assert.equal(req.listenerCount("error"), 0);
  req.destroy();
});

test("a failed body stream absorbs later errors until it closes", async () => {
  const req = new Readable({ read() {} });
  req.headers = {};
  const result = readBoundedBody(req, 4);
  req.emit("error", new Error("first failure"));
  await assert.rejects(result, /first failure/);
  assert.doesNotThrow(() => req.emit("error", new Error("second failure")));
  req.emit("close");
  assert.equal(req.listenerCount("error"), 0);
  req.destroy();
});
