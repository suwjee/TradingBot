import { defineConfig } from 'vite';
import fs from 'node:fs';
import path from 'node:path';
import { spawn } from 'node:child_process';
import { performance } from 'node:perf_hooks';
import { createHash, randomUUID } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { createFarazCandleApi } from './server/faraz-candle-api.js';
import { createChartTransferBundle, importChartTransferBundle } from './server/chart-transfer.js';
import { runIndicatorRangeCalculation, withIndicatorInputPipe } from './server/indicator-range-input.js';
import { migrateFlatRawFiles } from './server/migrate-raw-resources.js';
import { createRawResourceStore } from './server/raw-resource-store.js';
import { sendCandleFile } from './server/candle-file-response.js';
import { resolveLocalStatePaths } from './server/local-state-paths.js';
import { createCalculationCoordinator, parseEngineConcurrency } from './server/calculation-coordinator.js';
import { readBoundedBody } from './server/request-body.js';
import { createProgressChannels } from './server/progress-channels.js';
import { assertRawInputUnchanged, captureRawInputIdentity } from './server/raw-input-identity.js';
import { cachePathForRaw, readCalculationCache, writeCalculationCache } from './server/calculation-cache.js';
import { createLiveEngineSessions, LiveEngineError, startLiveEngineWorker } from './server/live-engine-sessions.js';
import { indicatorDigest, restoreRawSnapshot } from './server/live-engine-recovery.js';
import { chartWatchOptions, preserveOpenChart } from './server/ui-live-update.js';

// Anchor source paths to this config and local state to the chart-owned subtree.
// Vite may be launched from either the repository root or apps/chart.
const chartRoot = path.dirname(fileURLToPath(import.meta.url));
const workspaceRoot = path.resolve(chartRoot, '..', '..');
const localState = resolveLocalStatePaths(workspaceRoot);
const inputDir = localState.raw;
const rawStore = createRawResourceStore({ rootDir: inputDir });
const bridgePath = path.join(workspaceRoot, 'engine', 'bridge', 'trading_pipeline.py');
const liveBridgePath = path.join(workspaceRoot, 'engine', 'bridge', 'live_pipeline.py');
const pipelineRoot = path.join(workspaceRoot, 'engine', 'pipeline');
const enginePath = path.join(pipelineRoot, 'reaction_engine.py');
const blueEnginePath = path.join(pipelineRoot, 'blue_line_detector.py');
const aEnginePath = path.join(pipelineRoot, 'a_zone_detector.py');
const sEnginePath = path.join(pipelineRoot, 's_zone_detector.py');
const eEnginePath = path.join(pipelineRoot, 'e_zone_detector.py');
const stopAllEnginePath = path.join(pipelineRoot, 'lifecycle_engine.py');
const orderEnginePath = path.join(pipelineRoot, 'order_audit_engine.py');
const directionPolicyPath = path.join(pipelineRoot, 'direction_policy.py');
const coreUtilsPath = path.join(pipelineRoot, 'core_utils.py');
const primaryEnginePath = path.join(pipelineRoot, 'PL_PH_detector.py');
const trueFalseEnginePath = path.join(pipelineRoot, 'true_false.py');
const indicatorRangeInputPath = path.join(chartRoot, 'server', 'indicator-range-input.js');
const calculationSources = [bridgePath, enginePath, blueEnginePath, aEnginePath, sEnginePath, eEnginePath, stopAllEnginePath, orderEnginePath, directionPolicyPath, coreUtilsPath, primaryEnginePath, trueFalseEnginePath, indicatorRangeInputPath];
const pythonCommand = process.env.TRADINGBOT_PYTHON || 'python';
const engineArgs = ['--engine', enginePath, '--blue-engine', blueEnginePath, '--a-engine', aEnginePath,
  '--s-engine', sEnginePath, '--e-engine', eEnginePath, '--stopall-engine', stopAllEnginePath];
// Limit polling to UI and Engine sources on VMware shared folders. RAW, cache and server
// sources stay outside the watcher so an edit cannot restart the workstation.
const useVitePolling = process.env.TRADINGBOT_VITE_POLLING !== 'false';
const vitePollingInterval = Math.max(500, Number(process.env.TRADINGBOT_VITE_POLL_INTERVAL_MS) || 1_500);
const engineStyles = path.join(workspaceRoot, 'engine', 'styles');
const liveUpdateEngineSources = [liveBridgePath, ...calculationSources.filter(file => file.endsWith('.py'))];
const viteWatchOptions = chartWatchOptions({
  chartRoot, engineStyles, engineSources: liveUpdateEngineSources,
  enabled: useVitePolling, interval: vitePollingInterval,
});

function calculationSourceFingerprint() {
  const hash = createHash('sha256');
  for (const file of calculationSources) {
    // Content, not mtimes or version labels: same-size edits and preserved file
    // timestamps must invalidate both memory and disk entries. Basenames keep
    // the identity portable between real checkouts of these maintained files.
    hash.update(path.basename(file));
    hash.update('\0');
    hash.update(createHash('sha256').update(fs.readFileSync(file)).digest());
  }
  return hash.digest('hex');
}

function liveSourceFingerprint(sourceFingerprint) {
  try {
    return createHash('sha256').update(sourceFingerprint).update(fs.readFileSync(liveBridgePath)).digest('hex');
  } catch (error) {
    if (error?.code === 'ENOENT') return null;
    throw error;
  }
}
const inventoryMeta = new Map();
// Durable, human-navigable cache root.  Calculation results must never rely on
// Vite's process memory: restarting the dev server must preserve the exact
// serialized payload and each chart source gets an independent drawing file.
const primaryCacheRoot = localState.cache;
const drawingsDir = path.join(primaryCacheRoot, 'drawings');
const calculationsDir = path.join(primaryCacheRoot, 'indicator-calculations');
const templatesDir = path.join(primaryCacheRoot, 'indicator-templates');
const templatesPath = path.join(templatesDir, 'templates.json');
const progressChannels = createProgressChannels();
const calculationCoordinator = createCalculationCoordinator({
  maxActive: parseEngineConcurrency(process.env.TRADINGBOT_MAX_ENGINE_CONCURRENCY),
});
const activeDetectorChildren = new Set();
const liveEngineSessions = createLiveEngineSessions();
const liveReports = new Map();

function shutdownCalculations() {
  calculationCoordinator.close();
  liveEngineSessions.close();
  liveReports.clear();
  for (const child of activeDetectorChildren) child.kill();
  progressChannels.close();
}

function publishProgress(requestId, event) {
  progressChannels.publish(requestId, event);
}

function cacheSegment(value, fallback) {
  const cleaned = String(value ?? '')
    .normalize('NFKD')
    .replace(/[^a-zA-Z0-9._-]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 72);
  return cleaned || fallback;
}

function identityDigest(identity) {
  return createHash('sha256').update(String(identity)).digest('hex').slice(0, 16);
}

function drawingPath(item) {
  const symbol = cacheSegment(item.symbol, 'unnamed-symbol');
  const identity = item.chartId || item.id;
  return path.join(drawingsDir, symbol, `chart-${identityDigest(identity)}.json`);
}

function legacyDrawingPath(item) {
  const symbol = cacheSegment(item.symbol, 'unnamed-symbol');
  const source = cacheSegment(path.basename(item.id, '.json'), 'source');
  return path.join(drawingsDir, symbol, `${source}--${identityDigest(item.id)}.json`);
}

function resolveDrawingPath(item) {
  const target = drawingPath(item);
  if (fs.existsSync(target)) return target;
  const legacy = legacyDrawingPath(item);
  if (!fs.existsSync(legacy)) return target;
  fs.mkdirSync(path.dirname(target), { recursive: true });
  fs.copyFileSync(legacy, target);
  return target;
}

function calculationPath(item, request, cacheKey) {
  const symbol = cacheSegment(item.symbol, 'unnamed-symbol');
  const timeframe = `${request.timeframe}s`;
  const direction = cacheSegment(request.direction, 'direction');
  // Request options remain in the immutable cache key/digest; the file name
  // stays readable because symbol, timeframe, direction, and range are already
  // represented by the directory tree and prefix.
  const filename = `${request.from}-${request.to}--${identityDigest(cacheKey)}.json`;
  return path.join(calculationsDir, symbol, timeframe, direction, filename);
}

function calculationMetadataPath(calculationFile) {
  return `${calculationFile}.info.json`;
}

function calculationId(calculationFile) {
  return path.relative(calculationsDir, calculationFile).split(path.sep).join('/');
}

function calculationMetadata(item, request, reportId) {
  return {
    calculationId: reportId,
    chartId: item.chartId || null,
    symbol: item.symbol,
    sourceFile: item.id,
    timeframe: request.timeframe,
    chartTimeframe: request.chartTimeframe,
    direction: request.direction,
    from: request.from,
    to: request.to,
  };
}

function resolveCalculationReport(id) {
  const parts = typeof id === 'string' ? id.split('/') : [];
  if (parts.length !== 4) return null;
  const [symbol, timeframe, direction, filename] = parts;
  if (!/^[a-zA-Z0-9._-]{1,72}$/.test(symbol) || !/^\d+s$/.test(timeframe)
    || !/^(bullish|bearish)$/.test(direction) || !/^\d+-\d+--[a-f0-9]{16}\.json$/.test(filename)) return null;
  const file = path.resolve(calculationsDir, symbol, timeframe, direction, filename);
  return file.startsWith(`${path.resolve(calculationsDir)}${path.sep}`) && fs.existsSync(file) ? file : null;
}

function livePublication(item, request, to, payload, workerFingerprint, tabId) {
  const reportId = `live/${randomUUID().replaceAll('-', '')}`;
  liveReports.set(reportId, { payload, calculation: calculationMetadata(item, { ...request, to }, reportId) });
  if (liveReports.size > 16) liveReports.delete(liveReports.keys().next().value);
  return { calculationId: reportId, output: JSON.stringify(payload), proof: {
    chartId: item.chartId, tabId, request, to, workerFingerprint,
    rawBytes: item.metadata.dataBytes, rawSha256: item.metadata.dataSha256, resultDigest: indicatorDigest(payload),
  } };
}

function engineCalculationArgs(dataPath, request, bounds) {
  return ['--data', dataPath, '--timeframe', String(request.timeframe),
    '--from-time', String(bounds.fromTime), '--to-time', String(bounds.toTime),
    '--direction', request.direction, '--blue-lines', request.blueLines ? 'enabled' : 'disabled',
    '--a-zones', 'enabled', '--s-zones', 'enabled', '--bridge-output'];
}

function seedLiveEngine({ chartId, tabId, workerFingerprint, request, sourcePath, args, onProgress }) {
  return liveEngineSessions.seed({ chartId, tabId, sourceFingerprint: workerFingerprint, request },
    () => startLiveEngineWorker({
      command: pythonCommand, args: [liveBridgePath, ...engineArgs, ...args],
      env: { ...process.env, PYTHONDONTWRITEBYTECODE: '1', PYTHONUTF8: '1',
        TRADINGBOT_LIVE_RAW_SOURCE: sourcePath, TRADINGBOT_LIVE_CHART_TIMEFRAME: String(request.chartTimeframe) },
      onProgress,
    }));
}

function validLiveProof(proof, selected, tabId) {
  const request = proof?.request;
  return proof?.chartId === selected.chartId && proof.tabId === tabId
    && Number.isSafeInteger(proof.to) && request
    && Number.isSafeInteger(request.from) && Number.isSafeInteger(request.to)
    && request.from <= request.to && request.from <= proof.to
    && Number.isSafeInteger(request.timeframe) && request.timeframe > 0
    && Number.isSafeInteger(request.chartTimeframe) && request.chartTimeframe > 0
    && ['bullish', 'bearish'].includes(request.direction) && typeof request.blueLines === 'boolean';
}

async function recoverLiveEngine({ selected, proof, tabId, workerFingerprint }) {
  if (!validLiveProof(proof, selected, tabId)) {
    throw new LiveEngineError(404, 'Run an indicator calculation with Apply in this tab before enabling automatic continuation.', 'NO_INDICATOR_CALCULATION');
  }
  const current = await captureRawInputIdentity(selected.dataPath, { includeBytes: true }).catch(() => null);
  if (!current || current.sha256 !== selected.metadata.dataSha256) {
    throw new LiveEngineError(503, 'RAW changed during recovery. Retrying at the next check.', 'RAW_RETRY');
  }
  const request = proof.request;
  const runSeed = (rows, sourcePath, applied, to) => runIndicatorRangeCalculation({
    rows, sourcePath, from: applied.from, to, chartTimeframeSeconds: applied.chartTimeframe,
    run: (input, bounds) => seedLiveEngine({
      chartId: selected.chartId, tabId, workerFingerprint, request: applied, sourcePath,
      args: engineCalculationArgs(input, applied, bounds),
    }),
  });
  const decode = bytes => JSON.parse(bytes.toString('utf8').replace(/^\uFEFF/, ''));
  const snapshot = proof.workerFingerprint === workerFingerprint && restoreRawSnapshot(current.bytes, proof);
  if (snapshot) {
    const seed = await withIndicatorInputPipe(snapshot, sourcePath => runSeed(decode(snapshot), sourcePath, request, proof.to))
      .catch(error => {
        if (error.status === 429 || error.status === 503) throw error;
        return null;
      });
    if (seed?.sessionId) {
      if (indicatorDigest(seed.payload) === proof.resultDigest) return seed.sessionId;
      liveEngineSessions.discard(seed.sessionId);
    }
  }

  // Only this tab's applied range can initialize a replacement worker.
  // If its exact RAW prefix no longer exists, run it once on current RAW.
  const rows = decode(current.bytes);
  const first = rows.find(row => row.time >= request.from);
  if (!first) {
    throw new LiveEngineError(503, 'Waiting for RAW candles at the previously applied starting time.', 'RAW_RETRY');
  }
  const from = Math.floor(first.time / request.chartTimeframe) * request.chartTimeframe;
  const to = Math.floor(rows.at(-1).time / request.chartTimeframe) * request.chartTimeframe;
  const seed = await runSeed(rows, selected.dataPath, { ...request, from }, to);
  if (!seed.sessionId) throw new LiveEngineError(503, 'The indicator worker is unavailable. Retrying at the next check.');
  return seed.sessionId;
}

function ensureStateDirectories() {
  fs.mkdirSync(drawingsDir, { recursive: true });
  fs.mkdirSync(calculationsDir, { recursive: true });
  fs.mkdirSync(templatesDir, { recursive: true });
}

function readTemplates() {
  if (!fs.existsSync(templatesPath)) return {};
  try {
    const value = JSON.parse(fs.readFileSync(templatesPath, 'utf8'));
    return value && typeof value === 'object' && !Array.isArray(value) ? value : {};
  } catch { return {}; }
}

function cacheFileCount(directory) {
  if (!fs.existsSync(directory)) return 0;
  let count = 0;
  for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
    const child = path.join(directory, entry.name);
    if (entry.isDirectory()) count += cacheFileCount(child);
    else if (entry.isFile() && entry.name.endsWith('.json') && !entry.name.endsWith('.info.json')) count++;
  }
  return count;
}

function storedFileCount(directory) {
  if (!fs.existsSync(directory)) return 0;
  let count = 0;
  for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
    const child = path.join(directory, entry.name);
    if (entry.isDirectory()) count += storedFileCount(child);
    else if (entry.isFile() && entry.name !== '.gitkeep') count++;
  }
  return count;
}

function removeChartArtifacts(item) {
  let drawingsCleared = 0;
  for (const target of new Set([drawingPath(item), legacyDrawingPath(item)])) {
    if (!fs.existsSync(target) || !fs.statSync(target).isFile()) continue;
    fs.unlinkSync(target);
    drawingsCleared += 1;
  }

  let calculationFilesCleared = 0;
  const calculationRoot = path.join(calculationsDir, cacheSegment(item.symbol, 'unnamed-symbol'));
  const walk = (directory) => {
    if (!fs.existsSync(directory)) return;
    for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
      const target = path.join(directory, entry.name);
      if (entry.isDirectory()) {
        walk(target);
        try { if (!fs.readdirSync(target).length) fs.rmdirSync(target); } catch {}
        continue;
      }
      if (!entry.isFile() || !entry.name.endsWith('.info.json')) continue;
      let metadata = null;
      try { metadata = JSON.parse(fs.readFileSync(target, 'utf8')); } catch {}
      if (metadata?.sourceFile !== item.id && (!item.chartId || metadata?.chartId !== item.chartId)) continue;
      const calculationFile = target.slice(0, -'.info.json'.length);
      if (fs.existsSync(calculationFile)) fs.unlinkSync(calculationFile);
      const digestFile = `${calculationFile}.raw-sha256`;
      if (fs.existsSync(digestFile)) fs.unlinkSync(digestFile);
      fs.unlinkSync(target);
      calculationFilesCleared += 1;
    }
  };
  walk(calculationRoot);
  return { drawingsCleared, calculationFilesCleared };
}

function readBody(req, maxBytes = 100_000) {
  return readBoundedBody(req, maxBytes);
}

async function readJson(req, maxBytes = 100_000) {
  let body;
  try { body = JSON.parse(await readBody(req, maxBytes)); }
  catch { throw new Error('Request body must be valid JSON.'); }
  if (!body || typeof body !== 'object' || Array.isArray(body)) throw new Error('Request body must be a JSON object.');
  return body;
}

function runDetector(args, onProgress = () => {}, signal) {
  return new Promise((resolve, reject) => {
    if (signal?.aborted) { reject(new Error('Server is shutting down.')); return; }
    const child = spawn(pythonCommand, [bridgePath, ...engineArgs, ...args], {
      windowsHide: true,
      env: { ...process.env, PYTHONDONTWRITEBYTECODE: '1' },
    });
    activeDetectorChildren.add(child);
    const stopChild = () => child.kill();
    const releaseChild = () => {
      activeDetectorChildren.delete(child);
      signal?.removeEventListener('abort', stopChild);
    };
    signal?.addEventListener('abort', stopChild, { once: true });
    let stdout = '', stderr = '', stderrBuffer = '';
    child.stdout.on('data', (part) => { stdout += part; });
    child.stderr.on('data', (part) => {
      stderrBuffer += part;
      const lines = stderrBuffer.split(/\r?\n/);
      stderrBuffer = lines.pop();
      for (const line of lines) {
        if (!line.startsWith('QG_PROGRESS:')) { stderr += `${line}\n`; continue; }
        try { onProgress(JSON.parse(line.slice('QG_PROGRESS:'.length))); }
        catch { stderr += `${line}\n`; }
      }
    });
    child.on('error', (error) => { releaseChild(); reject(error); });
    child.on('close', (code) => {
      releaseChild();
      if (stderrBuffer) stderr += stderrBuffer;
      code === 0 ? resolve(stdout) : reject(new Error(stderr || stdout || `Detector exited with ${code}`));
    });
  });
}

function candleRows(filename) {
  const source = fs.readFileSync(path.join(inputDir, filename), "utf8");
  const rows = JSON.parse(source);
  if (!Array.isArray(rows) || !rows.length) return null;
  const keys = ["time", "open", "high", "low", "close"];
  const valid = rows.every((row, index) => {
    if (!row || Object.keys(row).length !== keys.length || !keys.every((key) => Object.hasOwn(row, key))) return false;
    const candle = Object.fromEntries(keys.map((key) => [key, Number(row[key])]));
    return Number.isSafeInteger(candle.time) && candle.time > 0
      && [candle.open, candle.high, candle.low, candle.close].every(Number.isFinite)
      && candle.high >= Math.max(candle.open, candle.close, candle.low)
      && candle.low <= Math.min(candle.open, candle.close, candle.high)
      && (!index || candle.time > Number(rows[index - 1].time));
  });
  return valid ? rows : null;
}

function inventory() {
  return rawStore.list().map((item) => {
    return {
      id: item.id,
      chartId: item.chartId || item.metadata?.chartId || null,
      symbol: item.symbol,
      broker: item.broker,
      timeframe: item.timeframe,
      from: item.from,
      to: item.to,
      createdAt: item.metadata.createdAt || null,
      updatedAt: item.metadata.updatedAt || item.savedAt,
      metadata: item.metadata,
      bytes: item.bytes, count: item.count, savedAt: item.savedAt,
    };
  });
}

function localDataApi() {
  return {
    name: 'local-candle-data-api',
    configureServer(server) {
      ensureStateDirectories();
      server.watcher.once('close', shutdownCalculations);
      server.httpServer?.once('close', shutdownCalculations);
      server.middlewares.use('/api/reactions/progress', (req, res) => {
        const requestId = new URL(req.url ?? '', 'http://localhost').searchParams.get('requestId');
        if (!requestId || !/^[a-zA-Z0-9-]{8,80}$/.test(requestId)) { res.statusCode = 400; res.end('Invalid progress request'); return; }
        res.writeHead(200, { 'Content-Type': 'text/event-stream', 'Cache-Control': 'no-cache, no-transform', Connection: 'keep-alive' });
        res.write(': connected\n\n');
        const detach = progressChannels.attach(requestId, res);
        req.once('close', detach);
      });
      server.middlewares.use('/api/symbols', (_req, res) => {
        res.setHeader('Content-Type', 'application/json; charset=utf-8');
        res.setHeader('Cache-Control', 'no-store');
        res.end(JSON.stringify(inventory()));
      });
      server.middlewares.use('/api/info', (req, res) => {
        res.setHeader('Content-Type', 'application/json; charset=utf-8');
        res.setHeader('Cache-Control', 'no-store');
        try {
          const route = decodeURIComponent(new URL(req.url ?? '/', 'http://localhost').pathname).replace(/^\/+/, '');
          if (/^live\/[a-f0-9]{32}$/.test(route) && ['GET', 'POST'].includes(req.method)) {
            const file = path.join(calculationsDir, `${route}.json`);
            if (fs.existsSync(file)) { res.end(fs.readFileSync(file)); return; }
            const report = liveReports.get(route);
            if (!report) throw new Error('The live report is unavailable. Update the indicator in its chart tab.');
            const output = JSON.stringify({ payload: report.payload, snapshot: { timezone: 'Asia/Tehran', calculation: report.calculation } });
            if (req.method === 'POST') {
              const temporary = `${file}.${randomUUID()}.tmp`;
              fs.mkdirSync(path.dirname(file), { recursive: true });
              try {
                fs.writeFileSync(temporary, output, { encoding: 'utf8', flag: 'wx' });
                fs.renameSync(temporary, file);
              } finally {
                fs.rmSync(temporary, { force: true });
              }
            }
            res.end(output);
            return;
          }
          if (req.method !== 'GET') throw new Error('GET is required');
          const calculationFile = resolveCalculationReport(route);
          if (!calculationFile) throw new Error('Calculation report was not found');
          const [symbol, timeframe, direction, filename] = route.split('/');
          const payload = JSON.parse(fs.readFileSync(calculationFile, 'utf8'));
          const metadataFile = calculationMetadataPath(calculationFile);
          const metadata = fs.existsSync(metadataFile)
            ? JSON.parse(fs.readFileSync(metadataFile, 'utf8'))
            : { calculationId: route, symbol, sourceFile: 'Legacy cache file', timeframe: Number(timeframe.slice(0, -1)), direction, from: Number(filename.split('--')[0].split('-')[0]), to: Number(filename.split('--')[0].split('-')[1]) };
          const { recovery: _recovery, ...calculation } = metadata;
          res.end(JSON.stringify({ payload, snapshot: { timezone: 'Asia/Tehran', calculation } }));
        } catch (error) {
          res.statusCode = 404;
          res.end(JSON.stringify({ error: error.message }));
        }
      });
      server.middlewares.use('/api/candle-files/delete', async (req, res) => {
        if (req.method !== 'POST') { res.statusCode = 405; res.end(JSON.stringify({ error: 'POST is required.' })); return; }
        try {
          const { id } = await readJson(req);
          const valid = inventory().find((item) => item.id === id);
          if (!valid) { res.statusCode = 404; res.end(JSON.stringify({ error: 'Candle file was not found.' })); return; }
          if (!rawStore.remove(valid.id)) { res.statusCode = 404; res.end(JSON.stringify({ error: 'Candle file was not found.' })); return; }
          const artifacts = removeChartArtifacts(valid);
          inventoryMeta.delete(valid.id);
          res.setHeader('Content-Type', 'application/json; charset=utf-8');
          res.setHeader('Cache-Control', 'no-store');
          res.end(JSON.stringify({ ok: true, deleted: valid.id, ...artifacts }));
        } catch (error) {
          res.statusCode = 400;
          res.setHeader('Content-Type', 'application/json; charset=utf-8');
          res.end(JSON.stringify({ error: error.message }));
        }
      });
      server.middlewares.use('/api/candle-files/cut', async (req, res) => {
        res.setHeader('Content-Type', 'application/json; charset=utf-8');
        res.setHeader('Cache-Control', 'no-store');
        try {
          if (req.method !== 'POST') throw new Error('POST is required.');
          const body = await readJson(req);
          const id = typeof body.id === 'string' ? body.id : '';
          const from = Number(body.from), to = Number(body.to);
          const mode = body.mode === 'new' ? 'new' : body.mode === 'replace' ? 'replace' : '';
          if (!id || !mode || !Number.isSafeInteger(from) || !Number.isSafeInteger(to)) throw new Error('A valid file and inclusive candle range are required.');
          const result = rawStore.cut(id, { from, to, mode });
          inventoryMeta.clear();
          res.end(JSON.stringify({ ok: true, ...result }));
        } catch (error) {
          res.statusCode = 400;
          res.end(JSON.stringify({ error: error.message }));
        }
      });
      server.middlewares.use('/api/candle-files/migrate', async (req, res) => {
        res.setHeader('Content-Type', 'application/json; charset=utf-8');
        res.setHeader('Cache-Control', 'no-store');
        try {
          if (req.method !== 'POST') throw new Error('POST is required.');
          const body = await readJson(req);
          const report = migrateFlatRawFiles({ rootDir: inputDir, apply: body.apply === true });
          inventoryMeta.clear();
          res.end(JSON.stringify({ ok: true, applied: body.apply === true, report }));
        } catch (error) {
          res.statusCode = 400;
          res.end(JSON.stringify({ error: error.message }));
        }
      });
      server.middlewares.use('/api/candles', async (req, res) => {
        try {
          const url = new URL(req.url ?? '', 'http://localhost');
          const id = url.searchParams.get('id');
          const resource = rawStore.resolve(id);
          if (!resource) { res.statusCode = 404; res.end('Candle file not found'); return; }
          await sendCandleFile(req, res, resource.dataPath);
        } catch (error) {
          if (!res.headersSent) res.statusCode = 500;
          if (!res.writableEnded) res.end('Unable to read candle file');
        }
      });
      server.middlewares.use('/api/reactions/cache', (req, res) => {
        res.setHeader('Content-Type', 'application/json; charset=utf-8');
        res.setHeader('Cache-Control', 'no-store');
        if (req.method !== 'DELETE') {
          res.statusCode = 405;
          res.end(JSON.stringify({ error: 'DELETE is required' }));
          return;
        }
        const url = new URL(req.url ?? '', 'http://localhost');
        const scope = url.searchParams.get('scope') || 'all';
        const availableLayers = new Set(['calculations', 'drawings', 'secret']);
        const suppliedLayers = url.searchParams.get('layers');
        const layers = suppliedLayers
          ? [...new Set(suppliedLayers.split(',').map((value) => value.trim()).filter((value) => availableLayers.has(value)))]
          : ['calculations'];
        if (!layers.length) {
          res.statusCode = 400;
          res.end(JSON.stringify({ error: 'Select at least one server cache layer.' }));
          return;
        }
        let calculationTarget = calculationsDir;
        let drawingsTarget = drawingsDir;
        let symbol;
        if (scope === 'symbol') {
          symbol = url.searchParams.get('symbol') || '';
          const segment = cacheSegment(symbol, '');
          if (!symbol || !segment) {
            res.statusCode = 400;
            res.end(JSON.stringify({ error: 'A valid chart symbol is required.' }));
            return;
          }
          calculationTarget = path.resolve(calculationsDir, segment);
          const cacheRoot = `${path.resolve(calculationsDir)}${path.sep}`;
          drawingsTarget = path.resolve(drawingsDir, segment);
          const drawingsRoot = `${path.resolve(drawingsDir)}${path.sep}`;
          if (!calculationTarget.startsWith(cacheRoot) || !drawingsTarget.startsWith(drawingsRoot)) {
            res.statusCode = 400;
            res.end(JSON.stringify({ error: 'Invalid cache target.' }));
            return;
          }
        } else if (scope !== 'all') {
          res.statusCode = 400;
          res.end(JSON.stringify({ error: 'Unknown cache clear scope.' }));
          return;
        }
        if (layers.includes('secret') && scope !== 'all') {
          res.statusCode = 400;
          res.end(JSON.stringify({ error: 'The local FARAZ session can only be cleared for all charts.' }));
          return;
        }
        const filesCleared = layers.includes('calculations') ? cacheFileCount(calculationTarget) : 0;
        const drawingsCleared = layers.includes('drawings') ? storedFileCount(drawingsTarget) : 0;
        if (layers.includes('calculations')) fs.rmSync(calculationTarget, { recursive: true, force: true });
        if (layers.includes('drawings')) fs.rmSync(drawingsTarget, { recursive: true, force: true });
        fs.mkdirSync(calculationsDir, { recursive: true });
        fs.mkdirSync(drawingsDir, { recursive: true });
        const farazSessionPath = path.join(localState.secret, 'faraz-session.dpapi.json');
        const localSessionCleared = layers.includes('secret') && fs.existsSync(farazSessionPath);
        if (localSessionCleared) fs.unlinkSync(farazSessionPath);
        res.end(JSON.stringify({ filesCleared, drawingsCleared, localSessionCleared, layers, scope, symbol: scope === 'symbol' ? symbol : undefined }));
      });
      server.middlewares.use('/api/drawings', async (req, res) => {
        res.setHeader('Content-Type', 'application/json; charset=utf-8');
        res.setHeader('Cache-Control', 'no-store');
        try {
          if (req.method === 'GET') {
            const query = new URL(req.url ?? '', 'http://localhost').searchParams;
            const id = query.get('id');
            const chartId = query.get('chartId');
            if (!id && !chartId) throw new Error('Drawing file identity is required');
            const item = inventory().find((candidate) => (chartId ? candidate.chartId === chartId : candidate.id === id));
            if (!item) throw new Error('Candle file not found');
            const target = resolveDrawingPath(item);
            res.end(fs.existsSync(target) ? fs.readFileSync(target, 'utf8') : '[]');
            return;
          }
          if (req.method === 'PUT') {
            const body = JSON.parse(await readBody(req));
            if ((!body.id && !body.chartId) || !Array.isArray(body.drawings)) throw new Error('Invalid drawings payload');
            const item = inventory().find((candidate) => body.chartId ? candidate.chartId === body.chartId : candidate.id === body.id);
            if (!item) throw new Error('Candle file not found');
            const target = drawingPath(item);
            fs.mkdirSync(path.dirname(target), { recursive: true });
            fs.writeFileSync(target, JSON.stringify(body.drawings, null, 2), 'utf8');
            res.end(JSON.stringify({ saved: body.drawings.length }));
            return;
          }
          res.statusCode = 405;
          res.end(JSON.stringify({ error: 'GET or PUT is required' }));
        } catch (error) {
          res.statusCode = 400;
          res.end(JSON.stringify({ error: error.message }));
        }
      });
      server.middlewares.use('/api/chart-transfer/export', async (req, res) => {
        res.setHeader('Content-Type', 'application/json; charset=utf-8');
        res.setHeader('Cache-Control', 'no-store');
        try {
          if (req.method !== 'GET') throw new Error('GET is required');
          const id = new URL(req.url ?? '', 'http://localhost').searchParams.get('id');
          const item = inventory().find((candidate) => candidate.id === id);
          if (!item) throw new Error('Candle file not found');
          const target = drawingPath(item);
          let drawings = [];
          if (fs.existsSync(target)) {
            const stored = JSON.parse(fs.readFileSync(target, 'utf8'));
            if (Array.isArray(stored)) drawings = stored;
          }
          res.end(JSON.stringify(createChartTransferBundle({ item, candles: rawStore.read(item.id), drawings, drawingFilename: path.basename(target) })));
        } catch (error) {
          res.statusCode = 400;
          res.end(JSON.stringify({ error: error.message }));
        }
      });
      server.middlewares.use('/api/chart-transfer/import', async (req, res) => {
        res.setHeader('Content-Type', 'application/json; charset=utf-8');
        res.setHeader('Cache-Control', 'no-store');
        try {
          if (req.method !== 'POST') throw new Error('POST is required');
          const { item, drawings } = importChartTransferBundle({
            bundle: await readJson(req, 50_000_000),
            rawStore,
            saveDrawings: (importedItem, importedDrawings) => {
              const target = drawingPath(importedItem);
              fs.mkdirSync(path.dirname(target), { recursive: true });
              fs.writeFileSync(target, JSON.stringify(importedDrawings, null, 2), 'utf8');
            },
          });
          inventoryMeta.clear();
          res.end(JSON.stringify({ ok: true, id: item.id, symbol: item.symbol, broker: item.broker, timeframe: item.timeframe, drawings }));
        } catch (error) {
          res.statusCode = 400;
          res.end(JSON.stringify({ error: error.message }));
        }
      });
      server.middlewares.use('/api/indicator-templates', async (req, res) => {
        res.setHeader('Content-Type', 'application/json; charset=utf-8');
        res.setHeader('Cache-Control', 'no-store');
        try {
          if (req.method === 'GET') { res.end(JSON.stringify(readTemplates())); return; }
          if (req.method !== 'PUT') { res.statusCode = 405; res.end(JSON.stringify({ error: 'GET or PUT is required' })); return; }
          const { templates } = await readJson(req);
          if (!templates || typeof templates !== 'object' || Array.isArray(templates)) throw new Error('Templates must be an object');
          const names = Object.keys(templates);
          if (names.length > 100 || names.some((name) => !name.trim() || name.length > 80)) throw new Error('Invalid template name');
          fs.mkdirSync(templatesDir, { recursive: true });
          fs.writeFileSync(templatesPath, JSON.stringify(templates, null, 2), 'utf8');
          res.end(JSON.stringify({ saved: names.length }));
        } catch (error) {
          res.statusCode = 400;
          res.end(JSON.stringify({ error: error.message }));
        }
      });
      server.middlewares.use('/api/reactions/source', (req, res) => {
        res.setHeader('Content-Type', 'application/json; charset=utf-8');
        res.setHeader('Cache-Control', 'no-store');
        if (req.method !== 'GET') {
          res.statusCode = 405;
          res.end(JSON.stringify({ error: 'GET is required' }));
          return;
        }
        try {
          res.end(JSON.stringify({ sourceFingerprint: calculationSourceFingerprint() }));
        } catch {
          res.statusCode = 500;
          res.end(JSON.stringify({ error: 'Calculation source identity is unavailable' }));
        }
      });
      server.middlewares.use('/api/reactions/continue', async (req, res) => {
        res.setHeader('Content-Type', 'application/json; charset=utf-8');
        res.setHeader('Cache-Control', 'no-store');
        try {
          if (req.method !== 'POST') throw new LiveEngineError(405, 'POST is required.');
          const { id, chartId, tabId = null, sessionId, keepAlive, proof } = await readJson(req).catch(error => { throw new LiveEngineError(400, error.message); });
          if (typeof id !== 'string' || typeof chartId !== 'string' || !chartId ||
              (tabId !== null && (typeof tabId !== 'string' || !/^[a-zA-Z0-9-]{8,80}$/.test(tabId))) ||
              (sessionId != null && (typeof sessionId !== 'string' || !/^[a-f0-9]{32}$/.test(sessionId)))) {
            throw new LiveEngineError(400, 'A valid live indicator session and RAW identity are required.');
          }
          const sourceFingerprint = calculationSourceFingerprint();
          const workerFingerprint = liveSourceFingerprint(sourceFingerprint);
          if (!workerFingerprint) throw new LiveEngineError(503, 'The live Engine is unavailable. Retrying at the next check.');
          const selected = rawStore.get(id);
          if (!selected || selected.chartId !== chartId) {
            throw new LiveEngineError(503, 'The selected RAW changed before the indicator update. The next poll will retry.');
          }
          const { dataPath, metadata } = selected;
          let rawIdentity;
          let currentSessionId = sessionId;
          async function validate(includeBytes = false) {
            if (liveSourceFingerprint(calculationSourceFingerprint()) !== workerFingerprint) {
              liveEngineSessions.discard(currentSessionId);
              throw new LiveEngineError(409, 'Calculation sources changed. Use Apply again.', 'ENGINE_CHANGED');
            }
            try {
              if (rawIdentity) {
                await assertRawInputUnchanged(dataPath, rawIdentity);
                return;
              }
              const { bytes, ...identity } = await captureRawInputIdentity(dataPath, { includeBytes });
              if (identity.sha256 !== metadata.dataSha256) throw new Error('The selected RAW changed.');
              rawIdentity = identity;
              return bytes;
            } catch {
              throw new LiveEngineError(503, 'The selected RAW changed during the indicator update. The next poll will retry.');
            }
          }
          const session = { chartId, tabId, sourceFingerprint: workerFingerprint };
          function advance(token) {
            return liveEngineSessions.advance({
              ...session, sessionId: token, rawSha256: metadata.dataSha256, data: dataPath,
            }, { validate, publish(payload, request) {
              const to = Math.floor(selected.to / request.chartTimeframe) * request.chartTimeframe;
              return livePublication(selected, request, to, payload, workerFingerprint, tabId);
            } });
          }
          let result;
          try {
            if (keepAlive === true) {
              liveEngineSessions.keepAlive({ ...session, sessionId });
              res.statusCode = 204;
              res.end();
              return;
            }
            result = await advance(sessionId);
          } catch (error) {
            const lostSession = ['LIVE_SESSION_EXPIRED', 'LIVE_SESSION_CLOSED', 'LIVE_ENGINE_TIMEOUT',
              'LIVE_ENGINE_FAILED', 'LIVE_ENGINE_PROTOCOL'].includes(error.code);
            const staleHistory = ['ENGINE_CHANGED', 'RAW_CHANGED'].includes(error.code);
            if (!lostSession && !(proof && staleHistory)) throw error;
            const key = JSON.stringify(['live-recovery', chartId, tabId, sessionId, proof, metadata.dataSha256, workerFingerprint]);
            const recovered = await calculationCoordinator.run(key, async () => {
              const token = await recoverLiveEngine({ selected, proof, tabId, workerFingerprint });
              currentSessionId = token;
              rawIdentity = undefined;
              try { return { result: await advance(token), token }; }
              catch (recoveryError) { liveEngineSessions.discard(token); throw recoveryError; }
            });
            result = recovered.result;
            res.setHeader('X-QG-Live-Session', recovered.token);
          }
          res.setHeader('X-QG-Source-Fingerprint', sourceFingerprint);
          res.setHeader('X-QG-Calculation-Id', result.calculationId);
          res.setHeader('X-QG-Live-Proof', JSON.stringify(result.proof));
          res.end(result.output);
        } catch (error) {
          res.statusCode = error.status || 500;
          res.end(JSON.stringify({ error: error.message, code: error.code }));
        }
      });
      server.middlewares.use('/api/reactions', async (req, res) => {
        const requestStarted = performance.now();
        let requestId = null;
        res.setHeader('Content-Type', 'application/json; charset=utf-8');
        res.setHeader('Cache-Control', 'no-store');
        try {
          if (req.method !== 'POST') throw new Error('POST is required');
          const body = JSON.parse(await readBody(req));
          requestId = typeof body.requestId === 'string' && /^[a-zA-Z0-9-]{8,80}$/.test(body.requestId) ? body.requestId : null;
          const valid = inventory().find((item) => item.id === body.id);
          if (!valid) throw new Error('Candle file not found');
          if (body.chartId && body.chartId !== valid.chartId) throw new Error('Chart identity does not match the selected RAW file');
          const timeframe = Number(body.timeframe), chartTimeframe = Number(body.chartTimeframe), from = Number(body.from), to = Number(body.to);
          if (!Number.isInteger(timeframe) || timeframe < 1 || !Number.isInteger(chartTimeframe) || chartTimeframe < 1
            || !Number.isSafeInteger(from) || !Number.isSafeInteger(to) || from > to) throw new Error('Invalid indicator range or timeframe');
          const sourceFromBucket = Math.floor(Number(valid.from) / chartTimeframe) * chartTimeframe;
          const sourceToBucket = Math.floor(Number(valid.to) / chartTimeframe) * chartTimeframe;
          if (from % chartTimeframe !== 0 || to % chartTimeframe !== 0 || from < sourceFromBucket || to > sourceToBucket) {
            throw new Error('Indicator range must use available chart-candle boundaries');
          }
          if (!['bullish', 'bearish'].includes(body.direction)) throw new Error('Invalid reaction direction');
          if (typeof body.blueLines !== 'boolean') throw new Error('Invalid Blue Line setting');
          const sourcePath = path.join(inputDir, valid.id);
          const rawIdentity = await captureRawInputIdentity(sourcePath);
          if (rawIdentity.sha256 !== valid.metadata?.dataSha256) {
            throw new Error('The selected RAW file changed while calculating. Apply again with the current file.');
          }
          const dataStat = rawIdentity.stat;
          const sourceFingerprint = calculationSourceFingerprint();
          const inputScope = from === sourceFromBucket && to === sourceToBucket ? 'complete-source' : 'selected-range';
          const bridgeOutput = true;
          const calculationRequest = { timeframe, chartTimeframe, from, to, direction: body.direction, blueLines: body.blueLines, bridgeOutput };
          const cacheKey = JSON.stringify(['engine-content-v3-range-input', sourceFingerprint, valid.chartId || valid.id, valid.id, dataStat.mtimeMs, timeframe, chartTimeframe, from, to, body.direction, body.blueLines, bridgeOutput, inputScope]);
          const liveRequested = body.liveSession === true;
          const tabId = body.tabId ?? null;
          if (tabId !== null && (typeof tabId !== 'string' || !/^[a-zA-Z0-9-]{8,80}$/.test(tabId))) {
            throw new Error('Invalid indicator tab identity');
          }
          const workerFingerprint = liveRequested && valid.chartId ? liveSourceFingerprint(sourceFingerprint) : null;
          const executionKey = JSON.stringify([cacheKey, rawIdentity.sha256, liveRequested, workerFingerprint, tabId]);
          let persistedCalculationPath = null;
          if (!liveRequested) {
            const base = calculationPath(valid, calculationRequest, cacheKey);
            const changed = calculationPath(valid, calculationRequest, JSON.stringify([cacheKey, rawIdentity.sha256]));
            persistedCalculationPath = cachePathForRaw(base, rawIdentity.sha256, changed);
          }
          let output = null;
          let cacheSource = null;
          const cacheReadStarted = performance.now();
          if (persistedCalculationPath) output = readCalculationCache(persistedCalculationPath, rawIdentity.sha256);
          if (output) {
            cacheSource = 'file';
          }
          const cacheHit = Boolean(output);
          const cacheReadMs = performance.now() - cacheReadStarted;
          let detectorMs = 0;
          let liveSessionId = null;
          if (!output || workerFingerprint) {
            const calculated = await calculationCoordinator.run(executionKey, async (publish, signal) => {
              await assertRawInputUnchanged(sourcePath, rawIdentity);
              let jobDetectorMs = 0;
              let jobLiveSessionId = null;
              const cachedOutput = persistedCalculationPath ? readCalculationCache(persistedCalculationPath, rawIdentity.sha256) : null;
              const runCalculation = async (calculationInputPath, bounds) => {
                const detectorStarted = performance.now();
                publish({ status: 'started', label: 'Start Python calculation' });
                try {
                  const args = engineCalculationArgs(calculationInputPath, calculationRequest, bounds);
                  let result = cachedOutput;
                  if (workerFingerprint) {
                    try {
                      const seed = await seedLiveEngine({ chartId: valid.chartId, tabId, workerFingerprint,
                        request: calculationRequest, sourcePath, args, onProgress: publish });
                      jobLiveSessionId = seed.sessionId;
                      if (!result) result = JSON.stringify(seed.payload);
                    } catch {
                      // The tab can still perform its manual calculation using the Engine.
                    }
                  }
                  if (!result) result = await runDetector(args, publish, signal);
                  jobDetectorMs = performance.now() - detectorStarted;
                  publish({ status: 'completed', label: 'Start Python calculation', durationMs: jobDetectorMs });
                  return result;
                } catch (error) {
                  jobDetectorMs = performance.now() - detectorStarted;
                  throw error;
                }
              };
              try {
                let result;
                if (inputScope === 'complete-source') {
                  result = await runCalculation(sourcePath, { fromTime: from, toTime: Number(valid.to) });
                } else {
                  const inputPreparationStarted = performance.now();
                  publish({ status: 'started', label: 'Filter raw range' });
                  const rows = rawStore.read(valid.id);
                  if (!rows) throw new Error('Candle file not found');
                  result = await runIndicatorRangeCalculation({
                    rows, sourcePath, from, to, chartTimeframeSeconds: chartTimeframe,
                    onPrepared: () => publish({
                      status: 'completed', label: 'Filter raw range',
                      durationMs: performance.now() - inputPreparationStarted,
                    }),
                    run: runCalculation,
                  });
                }
                if (calculationSourceFingerprint() !== sourceFingerprint) {
                  throw new Error('Calculation sources changed while running. Apply again with the current engines.');
                }
                if (jobLiveSessionId && liveSourceFingerprint(sourceFingerprint) !== workerFingerprint) {
                  liveEngineSessions.discard(jobLiveSessionId);
                  jobLiveSessionId = null;
                }
                await assertRawInputUnchanged(sourcePath, rawIdentity);
                if (liveRequested) return { output: result, detectorMs: jobDetectorMs, liveSessionId: jobLiveSessionId };
                const published = readCalculationCache(persistedCalculationPath, rawIdentity.sha256);
                if (!published) writeCalculationCache(persistedCalculationPath, rawIdentity.sha256, result);
                return { output: published || result, detectorMs: jobDetectorMs, liveSessionId: jobLiveSessionId };
              } catch (error) {
                if (jobLiveSessionId) liveEngineSessions.discard(jobLiveSessionId);
                throw error;
              }
            }, (event) => publishProgress(requestId, event));
            output = calculated.output;
            detectorMs = calculated.detectorMs;
            liveSessionId = calculated.liveSessionId;
          }
           else {
             await assertRawInputUnchanged(sourcePath, rawIdentity);
             if (calculationSourceFingerprint() !== sourceFingerprint) {
               throw new Error('Calculation sources changed while running. Apply again with the current engines.');
             }
             publishProgress(requestId, { status: 'completed', label: `Cached result (${cacheSource})` });
           }
           if (liveRequested) {
             const live = livePublication(valid, calculationRequest, to, JSON.parse(output), workerFingerprint, tabId);
             res.setHeader('X-QG-Live-Proof', JSON.stringify(live.proof));
             res.setHeader('X-QG-Calculation-Id', live.calculationId);
           } else {
             const reportId = calculationId(persistedCalculationPath);
             const metadataFile = calculationMetadataPath(persistedCalculationPath);
             if (!fs.existsSync(metadataFile)) fs.writeFileSync(metadataFile, JSON.stringify(
               calculationMetadata(valid, calculationRequest, reportId),
             ), 'utf8');
             res.setHeader('X-QG-Calculation-Id', reportId);
           }
           res.setHeader('X-QG-Cache', liveRequested ? 'bypass' : cacheHit ? cacheSource : 'miss');
           res.setHeader('X-QG-Input-Scope', inputScope);
          res.setHeader('X-QG-Source-Fingerprint', sourceFingerprint);
          if (liveSessionId) res.setHeader('X-QG-Live-Session', liveSessionId);
          res.setHeader('X-QG-Detector-Ms', detectorMs.toFixed(2));
          res.setHeader('X-QG-Cache-Read-Ms', cacheReadMs.toFixed(2));
          res.setHeader('X-QG-Server-Ms', (performance.now() - requestStarted).toFixed(2));
          res.setHeader('Server-Timing', `detector;dur=${detectorMs.toFixed(2)}, total;dur=${(performance.now() - requestStarted).toFixed(2)}`);
          publishProgress(requestId, { status: 'finished', label: 'Response ready', durationMs: performance.now() - requestStarted });
          res.end(output);
        } catch (error) {
          publishProgress(requestId, { status: 'failed', label: error.message });
          res.statusCode = 400;
          res.end(JSON.stringify({ error: error.message }));
        }
      });
    },
  };
}

function infoPage() {
  // Serve the runtime review shell without requiring an .html extension.
  const pagePath = path.join(chartRoot, 'review.html');
  return {
    name: 'info-page',
    configureServer(server) {
      server.middlewares.use('/info', (req, res, next) => {
        const route = req.url ?? '';
        const calculationRoute = /^\/[a-zA-Z0-9._-]+\/\d+s\/(bullish|bearish)\/\d+-\d+--[a-f0-9]{16}\.json(?:\?.*)?$/.test(route);
        if (req.method !== 'GET' || (route.includes('.') && !calculationRoute)) { next(); return; }
        res.setHeader('Content-Type', 'text/html; charset=utf-8');
        res.setHeader('Cache-Control', 'no-store');
        res.end(fs.readFileSync(pagePath, 'utf8'));
      });
    },
  };
}

export default defineConfig({
  plugins: [localDataApi(), createFarazCandleApi({ workspaceRoot, localStateRoot: localState.root, rawStore }),
    infoPage(), preserveOpenChart({ workspaceRoot, engineStyles, engineSources: liveUpdateEngineSources })],
  server: {
    port: 5173,
    strictPort: false,
    fs: {
      deny: ['**/.env', '**/.env.*', '**/*.{crt,pem}', '**/.git/**', '**/state/**', '**/tests/**', '**/engineering/archive/**', '**/engineering/verification/**'],
    },
    watch: viteWatchOptions,
    hmr: { overlay: false },
  },
  build: { target: 'chrome89' },
});
