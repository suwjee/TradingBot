import assert from "node:assert/strict";
import fs from "node:fs/promises";
import http from "node:http";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { createWorkspacePreferencesApi } from "../../server/workspace-preferences.js";
import { orderSymbolFiles } from "../../src/features/symbol-inventory.js";
import { createWorkspacePreferences } from "../../src/features/workspace-preferences.js";

const chartId = "11111111-1111-4111-8111-111111111111";
const bookmarkKey = `bookmark:${chartId}`;

test("workspace preferences merge independently and reopen from disk", async (t) => {
  const cache = await fs.mkdtemp(path.join(os.tmpdir(), "tradingbot-preferences-"));
  const serve = () => createWorkspacePreferencesApi(cache);
  let handle = serve();
  const server = http.createServer((req, res) => {
    req.url = "/";
    return handle(req, res, () => res.writeHead(404).end());
  });
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  t.after(async () => {
    await new Promise((resolve) => server.close(resolve));
    await fs.rm(cache, { recursive: true, force: true });
  });
  const endpoint = `http://127.0.0.1:${server.address().port}/api/workspace-preferences`;
  const patch = (key, value) => fetch(endpoint, {
    method: "PATCH",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ key, value }),
  });
  const realtime = { enabled: false, intervalMs: 120_000, indicatorCalculation: true };
  const key = `realtime:${chartId}`;
  const responses = await Promise.all([patch(bookmarkKey, true), patch(key, realtime), patch("drawing-order", ["cursor", "line"])]);
  assert.deepEqual(responses.map((response) => response.status), [200, 200, 200]);
  assert.equal((await patch("../secret", true)).status, 400);
  assert.equal((await patch(key, { intervalMs: 0 })).status, 400);
  handle = serve();
  const { preferences } = await (await fetch(endpoint)).json();
  assert.deepEqual(preferences, { [bookmarkKey]: true, [key]: realtime, "drawing-order": ["cursor", "line"] });
});

test("an unsynced browser preference replays after restarting against a stale server value", async () => {
  const data = new Map();
  const storage = {
    get length() { return data.size; },
    getItem: (key) => data.get(key),
    setItem: (key, value) => data.set(key, value),
    key: (index) => [...data.keys()][index],
  };
  const offline = createWorkspacePreferences({ storage, fetcher: async () => ({ ok: false }) });
  offline.set(bookmarkKey, false);
  const requests = [];
  const reconnect = createWorkspacePreferences({
    storage,
    async fetcher(_url, request) {
      if (request.method === "PATCH") requests.push(JSON.parse(request.body));
      return { ok: true, json: async () => ({ preferences: { [bookmarkKey]: true } }) };
    },
  });
  await reconnect.load();
  assert.equal(reconnect.get(bookmarkKey), false);
  assert.deepEqual(requests, [{ key: bookmarkKey, value: false }]);
  assert.equal(JSON.parse([...data.values()][0]).pending, false);
});

test("bookmarked RAW files are listed ahead of newer RAW and creation time beats append time", () => {
  const files = [
    { id: "recently-appended", createdAt: "2026-11-24 08:00:00 Asia/Tehran", savedAt: Infinity },
    { id: "new-import", createdAt: "2026-11-26 08:00:00 Asia/Tehran" },
    { id: "bookmark", createdAt: "2026-11-20 08:00:00 Asia/Tehran" },
  ];
  assert.deepEqual(orderSymbolFiles(files, ({ id }) => id === "bookmark").map(({ id }) => id), [
    "bookmark", "new-import", "recently-appended",
  ]);
  assert.equal(files[0].id, "recently-appended");
});
