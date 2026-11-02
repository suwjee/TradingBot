import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import http from "node:http";
import os from "node:os";
import path from "node:path";

import { createFarazCandleApi } from "../../server/faraz-candle-api.js";

const HISTORY_URL = "https://ir3.faraz.io/api/customer/trading-view/history?symbolName=FXCM%3AUSOIL&resolution=5S&countback=120&adjustType=2";

function fakeLoginBrowser() {
  let pageUrl = "about:blank";
  let closed = false;
  let closeCount = 0;
  const listeners = new Map();
  const cookie = { name: "farazSession", value: "unit-cookie", domain: ".faraz.io", path: "/", expires: -1 };
  const page = {
    url: () => pageUrl,
    isClosed: () => false,
    on(event, callback) {
      if (!listeners.has(event)) listeners.set(event, []);
      listeners.get(event).push(callback);
    },
    async goto(url) { pageUrl = url; },
    async bringToFront() {},
    async evaluate() { return ""; },
  };
  const context = {
    pages: () => [page],
    newPage: async () => page,
    on() {},
    async setExtraHTTPHeaders() {},
    async cookies() { return [cookie]; },
    async storageState() { return { cookies: [cookie], origins: [] }; },
  };
  const browser = {
    on() {},
    isConnected: () => !closed,
    async close() { closed = true; closeCount++; },
  };
  return {
    browser,
    context,
    emit(event, value) {
      for (const callback of listeners.get(event) || []) callback(value);
    },
    listenerCount(event) { return (listeners.get(event) || []).length; },
    isClosed: () => closed,
    closeCount: () => closeCount,
  };
}

async function startFixture(t) {
  const workspaceRoot = fs.mkdtempSync(path.join(os.tmpdir(), "tradingbot-faraz-response-"));
  const managed = fakeLoginBrowser();
  const api = createFarazCandleApi({
    workspaceRoot,
    localStateRoot: path.join(workspaceRoot, "apps", "chart", "state"),
    launchBrowser: async () => ({ browser: managed.browser, context: managed.context }),
  });
  const routes = new Map();
  api.configureServer({ middlewares: { use(route, handler) { routes.set(route, handler); } } });
  const server = http.createServer((req, res) => {
    const handler = routes.get(new URL(req.url, "http://localhost").pathname);
    if (handler) return handler(req, res);
    res.statusCode = 404;
    res.end();
  });
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  t.after(async () => {
    await api.shutdown();
    await new Promise((resolve) => server.close(resolve));
    fs.rmSync(workspaceRoot, { recursive: true, force: true });
  });
  const url = `http://127.0.0.1:${server.address().port}/api/faraz/auth/open`;
  const opened = await fetch(url, { method: "POST" });
  assert.equal(opened.status, 200);
  assert.equal(managed.listenerCount("request"), 1);
  assert.equal(managed.listenerCount("response"), 1);
  return {
    managed,
    secretPath: path.join(workspaceRoot, "apps", "chart", "state", "secret", "faraz-session.dpapi.json"),
  };
}

async function waitFor(predicate, description) {
  const deadline = Date.now() + 3000;
  while (!predicate()) {
    if (Date.now() > deadline) throw new Error(`Timed out waiting for ${description}`);
    await new Promise((resolve) => setTimeout(resolve, 5));
  }
}

test("successful allowed FARAZ browser history response captures session without status polling", async (t) => {
  const { managed, secretPath } = await startFixture(t);
  assert.equal(fs.existsSync(secretPath), false);
  managed.emit("request", {
    url: () => HISTORY_URL,
    headers: () => ({ "x-access-token": "unit-token", cookie: "farazSession=unit-cookie" }),
  });
  managed.emit("response", { url: () => HISTORY_URL, ok: true });
  await waitFor(() => managed.isClosed(), "browser to close after response");
  assert.equal(fs.existsSync(secretPath), true);
  const session = JSON.parse(fs.readFileSync(secretPath, "utf8"));
  assert.equal(session.format, "clear-text");
  assert.equal(session["x-access-token"], "unit-token");
  assert.equal(session.farazSession, "unit-cookie");
  assert.equal(session.historyAuth.host, "ir3.faraz.io");
  assert.equal(session.historyAuth.resolution, "5S");
  assert.equal(session.historyAuth.countback, 120);
  assert.equal(managed.closeCount(), 1);
});

test("untrusted or unsuccessful browser history responses never capture a session", async (t) => {
  const { managed, secretPath } = await startFixture(t);
  const responses = [
    { url: () => "https://attacker.example/api/customer/trading-view/history", ok: true },
    { url: () => "https://faraz.io/api/public/authentication/me", ok: true },
    { url: () => HISTORY_URL, ok: false },
  ];
  for (const response of responses) managed.emit("response", response);
  await new Promise((resolve) => setImmediate(resolve));
  assert.equal(fs.existsSync(secretPath), false);
  assert.equal(managed.isClosed(), false);
});

test("concurrent successful browser response callbacks finalize one session only", async (t) => {
  const { managed, secretPath } = await startFixture(t);
  const response = { url: () => HISTORY_URL, ok: true };
  managed.emit("response", response);
  managed.emit("response", response);
  await waitFor(() => managed.isClosed(), "single browser finalization");
  assert.equal(fs.existsSync(secretPath), true);
  assert.equal(managed.closeCount(), 1);
});
