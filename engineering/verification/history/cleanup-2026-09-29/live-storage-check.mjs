import fs from 'node:fs';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';

const workspace = 'D:/My-Projects/TradingBot';
const chart = path.join(workspace, 'apps/chart');
const state = 'D:/My-Projects/TradingBot-Local';
const audit = path.join(state, 'cleanup-2026-09-29');
const require = createRequire(path.join(chart, 'package.json'));
const { createServer } = await import(pathToFileURL(require.resolve('vite')).href);
const { createRawResourceStore } = await import(pathToFileURL(path.join(chart, 'server/raw-resource-store.js')).href);
process.env.PYTHONDONTWRITEBYTECODE = '1';
process.env.TRADINGBOT_LOCAL_STATE_ROOT = state;
const rows = JSON.parse(fs.readFileSync(path.join(audit, 'baseline-inventory.json'), 'utf8'));
const rawRows = rows.filter(row => row.classification === 'MARKET_DATA' && row.path.endsWith('.json') && !row.path.endsWith('.meta.json'));
const selected = [...rawRows].sort((a,b) => a.size-b.size)[0];
const raw = fs.readFileSync(path.join(state, selected.path));
const sourceHash = createHash('sha256').update(raw).digest('hex');
const id = selected.path.slice('data/raw/'.length);
const server = await createServer({ root:chart, configFile:path.join(chart,'vite.config.js'), configLoader:'native', logLevel:'error', server:{host:'127.0.0.1',port:0,strictPort:false,watch:null} });
try {
  await server.listen();
  const port = server.httpServer.address().port;
  const response = await fetch(`http://127.0.0.1:${port}/api/candles?id=${encodeURIComponent(id)}`);
  if (!response.ok) throw new Error(`Candle API status ${response.status}`);
  const returned = await response.json();
  const source = JSON.parse(raw);
  if (JSON.stringify(returned) !== JSON.stringify(source)) throw new Error('External candle API payload differs from original RAW.');
  const store = createRawResourceStore({ rootDir:path.join(state,'data/raw') });
  if (!store.resolve(id)) throw new Error('Migrated RAW resource is unavailable.');
  const info = await fetch(`http://127.0.0.1:${port}/info`);
  if (!info.ok || !(await info.text()).includes('review')) throw new Error('Review entry point is unavailable.');
  const result = {status:'PASS',port,rows:source.length,rawSha256:sourceHash,rawContentUnchanged:sourceHash===createHash('sha256').update(fs.readFileSync(path.join(state, selected.path))).digest('hex'),reviewShell:'PASS'};
  fs.writeFileSync(path.join(audit,'live-storage-check.json'),JSON.stringify(result,null,2));
  console.log(JSON.stringify(result));
} finally {
  await server.close();
}
