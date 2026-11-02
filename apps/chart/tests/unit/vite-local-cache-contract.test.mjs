import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import { randomUUID } from "node:crypto";
import { fileURLToPath } from "node:url";
import path from "node:path";

const chartRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const stateRoot = path.join(chartRoot, "state", `refactor-phase3-${randomUUID()}`);
process.env.TRADINGBOT_LOCAL_STATE_ROOT = stateRoot;
const { default: viteConfig } = await import("../../vite.config.js");

function registerLocalRoutes() {
  const routes = new Map();
  const server = {
    watcher: { once() {} },
    httpServer: { once() {} },
    middlewares: { use(route, handler) { routes.set(route, handler); } },
  };
  const plugin = viteConfig.plugins.find((item) => item.name === "local-candle-data-api");
  assert.ok(plugin);
  plugin.configureServer(server);
  return routes;
}

function invoke(handler, { method = "GET", url = "/" } = {}) {
  let body = null;
  const headers = new Map();
  const request = { method, url };
  const response = {
    statusCode: 200,
    setHeader(key, value) { headers.set(key.toLowerCase(), value); },
    end(value) { body = value; },
  };
  handler(request, response);
  return { response, headers, json: JSON.parse(body) };
}

test("Vite calculation fingerprint API produces stable content-based identity without changing engine", () => {
  const routes = registerLocalRoutes();
  const handler = routes.get("/api/reactions/source");
  assert.ok(handler);
  const first = invoke(handler, { url: "/api/reactions/source" });
  const second = invoke(handler, { url: "/api/reactions/source" });
  assert.equal(first.response.statusCode, 200);
  assert.equal(second.response.statusCode, 200);
  assert.match(first.json.sourceFingerprint, /^[a-f0-9]{64}$/);
  assert.deepEqual(first.json, second.json);
  assert.equal(first.headers.get("cache-control"), "no-store");
  const rejected = invoke(handler, { method: "POST", url: "/api/reactions/source" });
  assert.equal(rejected.response.statusCode, 405);
});

test("Vite cache deletion counts only calculation JSON and drawing data, not metadata", () => {
  const routes = registerLocalRoutes();
  const cache = path.join(stateRoot, "cache");
  const calc = path.join(cache, "indicator-calculations", "PAIR", "5s", "bullish");
  const draw = path.join(cache, "drawings", "PAIR");
  fs.mkdirSync(calc, { recursive: true });
  fs.mkdirSync(draw, { recursive: true });
  fs.writeFileSync(path.join(calc, "a.json"), "{}");
  fs.writeFileSync(path.join(calc, "a.json.info.json"), "{}");
  fs.writeFileSync(path.join(calc, "a.json.raw-sha256"), "abc");
  fs.writeFileSync(path.join(draw, "b.json"), "[]");
  fs.writeFileSync(path.join(draw, ".gitkeep"), "");
  const handler = routes.get("/api/reactions/cache");
  const result = invoke(handler, { method: "DELETE", url: "/api/reactions/cache?scope=all&layers=calculations,drawings" });
  assert.equal(result.response.statusCode, 200);
  assert.deepEqual(result.json, { filesCleared: 1, drawingsCleared: 1, localSessionCleared: false, layers: ["calculations", "drawings"], scope: "all" });
  assert.equal(fs.existsSync(calc), false);
  assert.equal(fs.existsSync(draw), false);
});

test("Vite cache API rejects invalid methods without clearing cache", () => {
  const routes = registerLocalRoutes();
  const handler = routes.get("/api/reactions/cache");
  const result = invoke(handler, { method: "GET", url: "/api/reactions/cache" });
  assert.equal(result.response.statusCode, 405);
  assert.equal(result.json.error, "DELETE is required");
});

test.after(() => fs.rmSync(stateRoot, { recursive: true, force: true }));
