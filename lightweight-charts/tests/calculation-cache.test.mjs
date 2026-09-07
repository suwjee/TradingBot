import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import { createHash } from "node:crypto";
import { EventEmitter } from "node:events";
import vm from "node:vm";

const config = readFileSync(new URL("../vite.config.js", import.meta.url), "utf8")
  .replace(/^import .*;\r?\n/gm, "")
  .replace(/const chartRoot = .*\r?\nconst workspaceRoot = .*\r?\n/, 'const chartRoot = "C:\\\\test-workspace\\\\lightweight-charts";\nconst workspaceRoot = path.resolve(chartRoot, "..");\n')
  .replace("export default defineConfig(", "const config = defineConfig(");
const id = "candle-history TEST 5S from 2026-01-01 00-00-00 to 2026-01-01 00-01-00 .json";
const request = { id, timeframe: 30, from: 1, to: 30, direction: "bullish", blueLines: true };
const files = ["reaction_bridge.py", "Reaction-detection-new.py", "blue_line.py", "a_detector.py", "s_detector.py", "e_detector.py", "stopall_detector.py"];

test("detector uses the Python executable selected by the launcher", () => {
  assert.match(config, /const pythonCommand = process\.env\.TRADINGBOT_PYTHON \|\| 'python'/);
  assert.match(config, /spawn\(pythonCommand,/);
});

test("local runtime paths are anchored to the Vite config, not the shell working directory", () => {
  const source = readFileSync(new URL("../vite.config.js", import.meta.url), "utf8");
  assert.match(source, /const chartRoot = path\.dirname\(fileURLToPath\(import\.meta\.url\)\)/);
  assert.match(source, /const inputDir = path\.join\(workspaceRoot, 'market-data', 'raw'\)/);
  assert.doesNotMatch(source, /path\.resolve\(process\.cwd\(\), '\.\.', 'market-data', 'raw'\)/);
});

function server(disk = new Map(), sources = new Map(files.map((name) => [name, "version-1"])), entries = [id], rawSources = new Map()) {
  const routes = new Map(); let runs = 0, unlinkCalls = 0;
  const directoryEntries = (directory) => {
    const prefix = `${path.resolve(directory)}${path.sep}`;
    const children = new Map();
    for (const file of disk.keys()) {
      if (!file.startsWith(prefix)) continue;
      const [name, ...rest] = file.slice(prefix.length).split(path.sep);
      if (!name) continue;
      children.set(name, rest.length ? "directory" : "file");
    }
    return [...children].map(([name, type]) => ({
      name,
      isFile: () => type === "file",
      isDirectory: () => type === "directory",
    }));
  };
  const fs = {
    mkdirSync() {}, existsSync: (file) => {
      const prefix = `${path.resolve(file)}${path.sep}`;
      return disk.has(file) || [...disk.keys()].some((key) => key.startsWith(prefix)) || /raw$/.test(file);
    },
    statSync: () => ({ mtimeMs: 123, size: 500 }),
    readdirSync(file) { return String(file).includes("indicator-calculations") ? directoryEntries(file) : entries.map((name) => ({ name, isFile: () => true, isDirectory: () => false })); },
    readFileSync(file, encoding) {
      const value = rawSources.get(path.basename(file)) ?? sources.get(path.basename(file)) ?? disk.get(file) ?? '[{"time":1,"open":1,"high":1,"low":1,"close":1}]';
      return encoding ? String(value) : Buffer.from(value);
    },
    writeFileSync(file, value) { disk.set(file, value); },
    rmSync(directory) { const prefix = `${path.resolve(directory)}${path.sep}`; for (const file of [...disk.keys()]) if (file.startsWith(prefix)) disk.delete(file); },
    unlinkSync(file) { unlinkCalls++; rawSources.delete(path.basename(file)); },
  };
  const context = vm.createContext({ fs, path, createHash, performance, process, URL, Buffer,
    defineConfig: (value) => value,
    createFarazCandleApi: () => ({ name: "faraz-candle-export-api-test-stub" }),
    spawn() { assert.fail("tests must not calculate trades"); } });
  vm.runInContext(config, context);
  context.runDetector = async () => { runs++; return JSON.stringify({ calculation: runs, sources: [...sources] }); };
  context.localDataApi().configureServer({ middlewares: { use: (url, handler) => routes.set(url, handler) } });
  async function post() {
    const req = new EventEmitter(); req.method = "POST"; req.setEncoding = () => {};
    const headers = {}, result = { statusCode: 200, headers, setHeader(key, value) { headers[key] = value; }, end(body) { this.body = body; } };
    const done = routes.get("/api/reactions")(req, result);
    req.emit("data", JSON.stringify(request)); req.emit("end"); await done;
    return result;
  }
  async function clearCache() {
    const req = new EventEmitter(); req.method = "DELETE";
    const headers = {}, result = { statusCode: 200, headers, setHeader(key, value) { headers[key] = value; }, end(body) { this.body = body; } };
    await routes.get("/api/reactions/cache")(req, result);
    return result;
  }
  async function info(calculationId) {
    const req = new EventEmitter(); req.method = "GET"; req.url = `/${calculationId}`;
    const headers = {}, result = { statusCode: 200, headers, setHeader(key, value) { headers[key] = value; }, end(body) { this.body = body; } };
    await routes.get("/api/info")(req, result);
    return result;
  }
  async function deleteCandle(candleId) {
    const req = new EventEmitter(); req.method = "POST"; req.setEncoding = () => {};
    const headers = {}, result = { statusCode: 200, headers, setHeader(key, value) { headers[key] = value; }, end(body) { this.body = body; } };
    const done = routes.get("/api/candle-files/delete")(req, result);
    req.emit("data", JSON.stringify({ id: candleId })); req.emit("end"); await done;
    return result;
  }
  return { context, disk, sources, post, clearCache, deleteCandle, info, runs: () => runs, unlinkCalls: () => unlinkCalls };
}

test("candle deletion parses its JSON request and removes only the validated raw inventory item", async () => {
  const raw = "RAW FXCM_USOIL 1S FROM 2026-09-02 20-10-14 TO 2026-09-02 20-36-30.json";
  const s = server(new Map(), new Map(files.map((name) => [name, "version-1"])), [raw]);
  const response = await s.deleteCandle(raw);
  assert.equal(response.statusCode, 200);
  assert.deepEqual(JSON.parse(response.body), { ok: true, deleted: raw });
  assert.equal(s.unlinkCalls(), 1);
});

test("inventory accepts every valid raw JSON filename and infers metadata when its name is nonstandard", () => {
  const arbitrary = "broker-export XAUUSD range A.json";
  const invalid = "notes.json";
  const rows = '[{"time":60,"open":1,"high":2,"low":1,"close":2},{"time":65,"open":2,"high":3,"low":2,"close":2.5}]';
  const s = server(new Map(), new Map(files.map((name) => [name, "version-1"])), [arbitrary, invalid], new Map([[arbitrary, rows], [invalid, "{}"]]));
  const items = s.context.inventory();
  assert.equal(items.length, 1);
  assert.equal(items[0].id, arbitrary);
  assert.equal(items[0].symbol, "XAUUSD");
  assert.equal(items[0].timeframe, "5S");
  assert.equal(items[0].count, 2);
});

test("inventory recognizes the FARAZ RAW export filename", () => {
  const raw = "RAW FOREXCOM_XAUUSD 1S FROM 2026-08-18 04-05-01 TO 2026-09-01 00-29-31.json";
  const s = server(new Map(), new Map(files.map((name) => [name, "version-1"])), [raw]);
  const [item] = s.context.inventory();
  assert.equal(item.symbol, "FOREXCOM:XAUUSD");
  assert.equal(item.timeframe, "1S");
  assert.equal(item.from, "2026-08-18 04-05-01");
  assert.equal(item.to, "2026-09-01 00-29-31");
});

test("inventory recognizes underscore RAW filenames and rejects unsafe candle chronology", () => {
  const raw = "RAW_FOREXCOM_XAUUSD_30S_FROM_2026_08_25_12_04_30_TO_2026_09_01_22.json";
  const reversed = "reversed.json";
  const rawRows = '[{"time":60,"open":1,"high":2,"low":1,"close":2},{"time":90,"open":2,"high":3,"low":2,"close":2.5}]';
  const reversedRows = '[{"time":90,"open":2,"high":3,"low":2,"close":2.5},{"time":60,"open":1,"high":2,"low":1,"close":2}]';
  const s = server(new Map(), new Map(files.map((name) => [name, "version-1"])), [raw, reversed], new Map([[raw, rawRows], [reversed, reversedRows]]));
  const [item] = s.context.inventory();
  assert.equal(item.id, raw);
  assert.equal(item.symbol, "FOREXCOM:XAUUSD");
  assert.equal(item.timeframe, "30S");
});

test("same-source requests reuse only the persisted primary-cache JSON", async () => {
  const s = server();
  const first = await s.post(); assert.equal(first.headers["X-QG-Cache"], "miss");
  const second = await s.post(); assert.equal(second.headers["X-QG-Cache"], "file");
  assert.equal(first.body, second.body); assert.equal(s.runs(), 1);
  const restarted = server(s.disk, s.sources);
  const third = await restarted.post(); assert.equal(third.headers["X-QG-Cache"], "file");
  assert.equal(third.body, first.body); assert.equal(restarted.runs(), 0);
  assert.match(third.headers["X-QG-Source-Fingerprint"], /^[a-f0-9]{64}$/);
  assert.match(third.headers["X-QG-Calculation-Id"], /^TEST\/30s\/bullish\/1-30--[a-f0-9]{16}\.json$/);
});

test("calculation report reads one exact persisted cache entry with its source metadata", async () => {
  const s = server(); const response = await s.post();
  const report = await s.info(response.headers["X-QG-Calculation-Id"]);
  assert.equal(report.statusCode, 200);
  const value = JSON.parse(report.body);
  assert.deepEqual(value.payload, JSON.parse(response.body));
  assert.equal(value.snapshot.calculation.sourceFile, id);
  assert.equal(value.snapshot.calculation.symbol, "TEST");
  assert.equal(value.snapshot.calculation.timeframe, 30);
  assert.equal(value.snapshot.calculation.direction, "bullish");
});

test("each maintained source invalidates cache even for same-size content edits and unchanged mtimes", async () => {
  const s = server(); const original = await s.post();
  let previous = original.headers["X-QG-Source-Fingerprint"];
  for (const file of files) {
    s.sources.set(file, "version-2");
    const changed = await s.post();
    assert.equal(changed.headers["X-QG-Cache"], "miss", file);
    assert.notEqual(changed.headers["X-QG-Source-Fingerprint"], previous, file);
    previous = changed.headers["X-QG-Source-Fingerprint"];
  }
  assert.equal([...s.disk.keys()].filter((file) => !file.endsWith('.info.json')).length, 8); // all superseded calculation files remain intact
  assert.equal(s.runs(), 8);
});

test("pre-fingerprint legacy files are preserved but never served", async () => {
  const s = server();
  const oldPath = path.resolve("..", "Results", "chart-state", "indicator-calculations", "legacy.json");
  s.disk.set(oldPath, '{"legacy":true}');
  const result = await s.post();
  assert.equal(result.headers["X-QG-Cache"], "miss"); assert.doesNotMatch(result.body, /legacy/);
  assert.equal(s.disk.get(oldPath), '{"legacy":true}');
});

test("primary cache paths are grouped by symbol and calculation parameters", () => {
  const s = server();
  const item = s.context.inventory()[0];
  const key = "request-key";
  const drawing = s.context.drawingPath(item);
  const calculation = s.context.calculationPath(item, request, key);
  assert.match(drawing, /primary-cache[\\/]drawings[\\/]TEST[\\/]/);
  assert.match(calculation, /primary-cache[\\/]indicator-calculations[\\/]TEST[\\/]30s[\\/]bullish[\\/]/);
  assert.match(calculation, /1-30--[a-f0-9]{16}\.json$/);
  assert.doesNotMatch(calculation, /blue-lines/);
});

test("Reload clears every persisted indicator result but never touches drawing files", async () => {
  const s = server();
  await s.post();
  const drawing = path.resolve("..", "primary-cache", "drawings", "TEST", "chart.json");
  s.disk.set(drawing, "[]");
  const cleared = await s.clearCache();
  assert.equal(cleared.statusCode, 200);
  assert.equal(JSON.parse(cleared.body).filesCleared, 1);
  assert.equal(s.disk.get(drawing), "[]");
  const recalculated = await s.post();
  assert.equal(recalculated.headers["X-QG-Cache"], "miss");
  assert.equal(s.runs(), 2);
});

test("changing an engine during calculation rejects the result without persisting it", async () => {
  const s = server();
  s.context.runDetector = async () => { s.sources.set("e_detector.py", "version-2"); return '{"mixed":true}'; };
  const result = await s.post();
  assert.equal(result.statusCode, 400); assert.match(result.body, /sources changed while running/);
  assert.equal(s.disk.size, 0);
});
