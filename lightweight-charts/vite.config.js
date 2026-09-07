import { defineConfig } from 'vite';
import fs from 'node:fs';
import path from 'node:path';
import { spawn } from 'node:child_process';
import { performance } from 'node:perf_hooks';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { createFarazCandleApi } from './plugins/faraz-candle-api.js';

// Keep local data, caches, and Python engines anchored to this config file.
// Vite may be launched from either TradingBot or lightweight-charts.
const chartRoot = path.dirname(fileURLToPath(import.meta.url));
const workspaceRoot = path.resolve(chartRoot, '..');
const inputDir = path.join(workspaceRoot, 'market-data', 'raw');
const pattern = /^(?:candle-history\s+(.+?)\s+(\d+[SMHD])\s+from\s+(.+?)\s+to\s+(.+?)\s*|RAW\s+(.+?)\s+(\d+[SMHD])\s+FROM\s+(.+?)\s+TO\s+(.+?))\.json$/i;
const rawPrefixPattern = /^RAW(?:\s+|_)(.+?)(?:\s+|_)(\d+[SMHD])(?:\s+|_)FROM(?:\s+|_)/i;
const bridgePath = path.join(workspaceRoot, 'indicator', 'indicator-settings', 'backend', 'reaction_bridge.py');
const moduleRoot = path.join(workspaceRoot, 'indicator', 'Modules');
const enginePath = path.join(moduleRoot, '1_reaction-detector', 'app', 'Reaction-detection-new.py');
const blueEnginePath = path.join(moduleRoot, '2_blue-line', 'app', 'blue_line.py');
const aEnginePath = path.join(moduleRoot, '3_A-zone', 'app', 'a_detector.py');
const sEnginePath = path.join(moduleRoot, '4_S-zones', 'app', 's_detector.py');
const eEnginePath = path.join(moduleRoot, '5_E-zones', 'app', 'e_detector.py');
const stopAllEnginePath = path.join(moduleRoot, '6_StopAll', 'app', 'stopall_detector.py');
const calculationSources = [bridgePath, enginePath, blueEnginePath, aEnginePath, sEnginePath, eEnginePath, stopAllEnginePath];
const pythonCommand = process.env.TRADINGBOT_PYTHON || 'python';

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
const inventoryMeta = new Map();
// Durable, human-navigable cache root.  Calculation results must never rely on
// Vite's process memory: restarting the dev server must preserve the exact
// serialized payload and each chart source gets an independent drawing file.
const primaryCacheRoot = path.join(workspaceRoot, 'primary-cache');
const drawingsDir = path.join(primaryCacheRoot, 'drawings');
const calculationsDir = path.join(primaryCacheRoot, 'indicator-calculations');
const templatesDir = path.join(primaryCacheRoot, 'indicator-templates');
const templatesPath = path.join(templatesDir, 'templates.json');
const progressChannels = new Map();

function publishProgress(requestId, event) {
  if (!requestId) return;
  const channel = progressChannels.get(requestId) || { events: [], clients: new Set() };
  progressChannels.set(requestId, channel);
  channel.events.push(event);
  if (channel.events.length > 120) channel.events.shift();
  const message = `data: ${JSON.stringify(event)}\n\n`;
  for (const client of channel.clients) client.write(message);
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
  const source = cacheSegment(path.basename(item.id, '.json'), 'source');
  return path.join(drawingsDir, symbol, `${source}--${identityDigest(item.id)}.json`);
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

function calculationMetadata(item, request, calculationFile) {
  return {
    calculationId: calculationId(calculationFile),
    symbol: item.symbol,
    sourceFile: item.id,
    timeframe: request.timeframe,
    direction: request.direction,
    from: request.from,
    to: request.to,
  };
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

function readBody(req) {
  return new Promise((resolve, reject) => {
    let body = '';
    req.setEncoding('utf8');
    req.on('data', (chunk) => { body += chunk; if (body.length > 100_000) reject(new Error('Request is too large')); });
    req.on('end', () => resolve(body));
    req.on('error', reject);
  });
}

async function readJson(req) {
  let body;
  try { body = JSON.parse(await readBody(req)); }
  catch { throw new Error('Request body must be valid JSON.'); }
  if (!body || typeof body !== 'object' || Array.isArray(body)) throw new Error('Request body must be a JSON object.');
  return body;
}

function runDetector(args, onProgress = () => {}) {
  return new Promise((resolve, reject) => {
    const child = spawn(pythonCommand, [bridgePath, '--engine', enginePath, '--blue-engine', blueEnginePath, '--a-engine', aEnginePath, '--s-engine', sEnginePath, '--e-engine', eEnginePath, '--stopall-engine', stopAllEnginePath, ...args], { windowsHide: true });
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
    child.on('error', reject);
    child.on('close', (code) => {
      if (stderrBuffer) stderr += stderrBuffer;
      code === 0 ? resolve(stdout) : reject(new Error(stderr || stdout || `Detector exited with ${code}`));
    });
  });
}

function inferredTimeframe(rows) {
  const times = rows.map((row) => Number(row?.time)).filter(Number.isFinite).sort((a, b) => a - b);
  let minimum = Infinity;
  for (let index = 1; index < times.length; index++) {
    const difference = times[index] - times[index - 1];
    if (difference > 0) minimum = Math.min(minimum, difference);
  }
  if (!Number.isFinite(minimum)) return "unknown";
  if (minimum % 86400 === 0) return `${minimum / 86400}D`;
  if (minimum % 3600 === 0) return `${minimum / 3600}H`;
  if (minimum % 60 === 0) return `${minimum / 60}M`;
  return `${minimum}S`;
}

function fallbackSymbol(filename) {
  const stem = path.basename(filename, ".json").replace(/^(?:candle-history|RAW)\s+/i, "").trim();
  const symbol = stem.match(/(?:^|[\s_-])([A-Z]{3,12}(?:[:_][A-Z]{3,12})?)(?:[\s_-]|$)/)?.[1];
  return (symbol || stem || "Unnamed dataset").replace(/_/g, ":");
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
  if (!fs.existsSync(inputDir)) return [];
  return fs.readdirSync(inputDir, { withFileTypes: true })
    .filter((entry) => entry.isFile() && entry.name.toLowerCase().endsWith('.json'))
    .map((entry) => {
      const match = entry.name.match(pattern);
      const rawPrefix = entry.name.match(rawPrefixPattern);
      const stat = fs.statSync(path.join(inputDir, entry.name));
      const cached = inventoryMeta.get(entry.name);
      let meta = cached?.mtimeMs === stat.mtimeMs ? cached : null;
      if (!meta) {
        try {
          const rows = candleRows(entry.name);
          if (!rows) return null;
          const times = rows.map((row) => Number(row.time)).sort((a, b) => a - b);
          meta = {
            mtimeMs: stat.mtimeMs,
            count: rows.length,
            timeframe: inferredTimeframe(rows),
            from: new Date(times[0] * 1000).toISOString(),
            to: new Date(times.at(-1) * 1000).toISOString(),
          };
          inventoryMeta.set(entry.name, meta);
        } catch {
          return null;
        }
      }
      return {
        id: entry.name,
        symbol: (match?.[1] || match?.[5] || rawPrefix?.[1])?.replace(/_/g, ":") || fallbackSymbol(entry.name),
        timeframe: (match?.[2] || match?.[6] || rawPrefix?.[2])?.toUpperCase() || meta.timeframe,
        from: match?.[3] || match?.[7] || meta.from,
        to: match?.[4] || match?.[8] || meta.to,
        bytes: stat.size,
        count: meta.count,
        savedAt: stat.mtimeMs,
      };
    })
    .filter(Boolean)
    .sort((a, b) => a.symbol.localeCompare(b.symbol) || b.savedAt - a.savedAt || a.id.localeCompare(b.id));
}

function localDataApi() {
  return {
    name: 'local-candle-data-api',
    configureServer(server) {
      ensureStateDirectories();
      server.middlewares.use('/api/reactions/progress', (req, res) => {
        const requestId = new URL(req.url ?? '', 'http://localhost').searchParams.get('requestId');
        if (!requestId || !/^[a-zA-Z0-9-]{8,80}$/.test(requestId)) { res.statusCode = 400; res.end('Invalid progress request'); return; }
        const channel = progressChannels.get(requestId) || { events: [], clients: new Set() };
        progressChannels.set(requestId, channel);
        res.writeHead(200, { 'Content-Type': 'text/event-stream', 'Cache-Control': 'no-cache, no-transform', Connection: 'keep-alive' });
        res.write(': connected\n\n');
        channel.clients.add(res);
        for (const event of channel.events) res.write(`data: ${JSON.stringify(event)}\n\n`);
        req.on('close', () => {
          channel.clients.delete(res);
          if (!channel.clients.size && channel.events.at(-1)?.status === 'finished') progressChannels.delete(requestId);
        });
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
          if (req.method !== 'GET') throw new Error('GET is required');
          const route = decodeURIComponent(new URL(req.url ?? '/', 'http://localhost').pathname).replace(/^\/+/, '');
          const parts = route.split('/');
          if (parts.length !== 4) throw new Error('Calculation report was not found');
          const [symbol, timeframe, direction, filename] = parts;
          if (!/^[a-zA-Z0-9._-]{1,72}$/.test(symbol) || !/^\d+s$/.test(timeframe)
            || !/^(bullish|bearish)$/.test(direction) || !/^\d+-\d+--[a-f0-9]{16}\.json$/.test(filename)) {
            throw new Error('Calculation report was not found');
          }
          const calculationFile = path.resolve(calculationsDir, symbol, timeframe, direction, filename);
          const calculationRoot = `${path.resolve(calculationsDir)}${path.sep}`;
          if (!calculationFile.startsWith(calculationRoot) || !fs.existsSync(calculationFile)) throw new Error('Calculation report was not found');
          const payload = JSON.parse(fs.readFileSync(calculationFile, 'utf8'));
          const metadataFile = calculationMetadataPath(calculationFile);
          const metadata = fs.existsSync(metadataFile)
            ? JSON.parse(fs.readFileSync(metadataFile, 'utf8'))
            : { calculationId: route, symbol, sourceFile: 'Legacy cache file', timeframe: Number(timeframe.slice(0, -1)), direction, from: Number(filename.split('--')[0].split('-')[0]), to: Number(filename.split('--')[0].split('-')[1]) };
          res.end(JSON.stringify({ payload, snapshot: { timezone: 'Asia/Tehran', calculation: metadata } }));
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
          fs.unlinkSync(path.join(inputDir, valid.id));
          inventoryMeta.delete(valid.id);
          res.setHeader('Content-Type', 'application/json; charset=utf-8');
          res.setHeader('Cache-Control', 'no-store');
          res.end(JSON.stringify({ ok: true, deleted: valid.id }));
        } catch (error) {
          res.statusCode = 400;
          res.setHeader('Content-Type', 'application/json; charset=utf-8');
          res.end(JSON.stringify({ error: error.message }));
        }
      });
      server.middlewares.use('/api/candles', (req, res) => {
        const url = new URL(req.url ?? '', 'http://localhost');
        const id = url.searchParams.get('id');
        const valid = inventory().find((item) => item.id === id);
        if (!valid) { res.statusCode = 404; res.end('Candle file not found'); return; }
        res.setHeader('Content-Type', 'application/json; charset=utf-8');
        res.setHeader('Cache-Control', 'no-store');
        fs.createReadStream(path.join(inputDir, valid.id)).pipe(res);
      });
      server.middlewares.use('/api/reactions/cache', (req, res) => {
        res.setHeader('Content-Type', 'application/json; charset=utf-8');
        res.setHeader('Cache-Control', 'no-store');
        if (req.method !== 'DELETE') {
          res.statusCode = 405;
          res.end(JSON.stringify({ error: 'DELETE is required' }));
          return;
        }
        const filesCleared = cacheFileCount(calculationsDir);
        // The user explicitly requests a complete indicator-cache reload.
        // This exact, bounded directory never contains drawings or source data.
        fs.rmSync(calculationsDir, { recursive: true, force: true });
        fs.mkdirSync(calculationsDir, { recursive: true });
        // Keep the tracked placeholder; it is not cached indicator data.
        fs.writeFileSync(path.join(calculationsDir, '.gitkeep'), '');
        res.end(JSON.stringify({ filesCleared }));
      });
      server.middlewares.use('/api/drawings', async (req, res) => {
        res.setHeader('Content-Type', 'application/json; charset=utf-8');
        res.setHeader('Cache-Control', 'no-store');
        try {
          if (req.method === 'GET') {
            const id = new URL(req.url ?? '', 'http://localhost').searchParams.get('id');
            if (!id) throw new Error('Drawing file identity is required');
            const item = inventory().find((candidate) => candidate.id === id);
            if (!item) throw new Error('Candle file not found');
            const target = drawingPath(item);
            res.end(fs.existsSync(target) ? fs.readFileSync(target, 'utf8') : '[]');
            return;
          }
          if (req.method === 'PUT') {
            const body = JSON.parse(await readBody(req));
            if (typeof body.id !== 'string' || !Array.isArray(body.drawings)) throw new Error('Invalid drawings payload');
            const item = inventory().find((candidate) => candidate.id === body.id);
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
          const timeframe = Number(body.timeframe), from = Number(body.from), to = Number(body.to);
          if (!Number.isInteger(timeframe) || timeframe < 1 || !Number.isFinite(from) || !Number.isFinite(to) || from > to) throw new Error('Invalid indicator range or timeframe');
          if (!['bullish', 'bearish'].includes(body.direction)) throw new Error('Invalid reaction direction');
          if (typeof body.blueLines !== 'boolean') throw new Error('Invalid Blue Line setting');
          const dataStat = fs.statSync(path.join(inputDir, valid.id));
          const sourceFingerprint = calculationSourceFingerprint();
          const cacheKey = JSON.stringify(['engine-content-v1', sourceFingerprint, valid.id, dataStat.mtimeMs, timeframe, from, to, body.direction, body.blueLines]);
           const persistedCalculationPath = calculationPath(valid, { timeframe, from, to, direction: body.direction, blueLines: body.blueLines }, cacheKey);
          let output = null;
          let cacheSource = null;
          const cacheReadStarted = performance.now();
          if (fs.existsSync(persistedCalculationPath)) {
            output = fs.readFileSync(persistedCalculationPath, 'utf8');
            cacheSource = 'file';
          }
          const cacheHit = Boolean(output);
          const cacheReadMs = performance.now() - cacheReadStarted;
          let detectorMs = 0;
          if (!output) {
            const detectorStarted = performance.now();
            publishProgress(requestId, { status: 'started', label: 'Start Python calculation' });
            output = await runDetector(['--data', path.join(inputDir, valid.id), '--timeframe', String(timeframe), '--from-time', String(from), '--to-time', String(to), '--direction', body.direction, '--blue-lines', body.blueLines ? 'enabled' : 'disabled', '--a-zones', 'enabled', '--s-zones', 'enabled'], (event) => publishProgress(requestId, event));
            detectorMs = performance.now() - detectorStarted;
            publishProgress(requestId, { status: 'completed', label: 'Start Python calculation', durationMs: detectorMs });
            if (calculationSourceFingerprint() !== sourceFingerprint) {
              throw new Error('Calculation sources changed while running. Apply again with the current engines.');
            }
            fs.mkdirSync(path.dirname(persistedCalculationPath), { recursive: true });
            fs.writeFileSync(persistedCalculationPath, output, 'utf8');
          }
           else publishProgress(requestId, { status: 'completed', label: `Cached result (${cacheSource})` });
           const metadataFile = calculationMetadataPath(persistedCalculationPath);
           if (!fs.existsSync(metadataFile)) fs.writeFileSync(metadataFile, JSON.stringify(
             calculationMetadata(valid, { timeframe, from, to, direction: body.direction }, persistedCalculationPath),
           ), 'utf8');
           res.setHeader('X-QG-Cache', cacheHit ? cacheSource : 'miss');
           res.setHeader('X-QG-Calculation-Id', calculationId(persistedCalculationPath));
          res.setHeader('X-QG-Source-Fingerprint', sourceFingerprint);
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
  const pagePath = path.resolve(process.cwd(), 'manual-test.html');
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

export default defineConfig({ plugins: [localDataApi(), createFarazCandleApi(), infoPage()], server: { port: 5173, strictPort: false, watch: { usePolling: true, interval: 500 } }, build: { target: 'chrome89' } });
