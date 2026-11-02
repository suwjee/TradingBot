import fs from 'node:fs';
import path from 'node:path';

// Preserve existing cache accounting: calculations count result JSON (excluding
// .info.json), while drawings count every stored non-.gitkeep file.
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

export function createLocalCacheClearHandler({ calculationsDir, drawingsDir, localState, cacheSegment }) {
  return (req, res) => {
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
  };
}
