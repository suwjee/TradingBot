import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from '../../../../apps/chart/node_modules/playwright-core/index.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../../..');
const out = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const origin = 'http://127.0.0.1:5173';
const results = [];
const rawRelative = 'FOREXCOM/XAUUSD/RAW FOREXCOM_XAUUSD 5S FROM 2026-09-16 22-35-00 TO 2026-09-17 19-15-35.json';
const source = JSON.parse(fs.readFileSync(path.join(root, 'apps/chart/state/data/raw', rawRelative), 'utf8'));
for (const route of ['/', '/info', '/src/main.js']) {
  const response = await fetch(origin + route);
  assert.equal(response.status, 200, route);
  await response.body.cancel();
  results.push({ route, status: response.status });
}
const candles = await fetch(`${origin}/api/candles?id=${encodeURIComponent(rawRelative)}`);
assert.equal(candles.status, 200);
assert.deepEqual(await candles.json(), source);
results.push({ route: '/api/candles', status: 200, rows: source.length, source_equal: true });
const stateRelative = '/state/data/raw/' + rawRelative;
const blocked = [
  stateRelative, '/state/secret/faraz-session.dpapi.json',
  '/STATE/secret/faraz-session.dpapi.json',
  '/@fs/' + path.join(root, 'apps/chart/state/secret/faraz-session.dpapi.json').replaceAll('\\', '/'),
  '/@fs/' + path.join(root, 'engineering/verification/single-root-2026-09-29/before-XAUUSD.stable.json').replaceAll('\\', '/'),
];
for (const route of blocked) {
  const response = await fetch(origin + encodeURI(route));
  await response.body?.cancel();
  assert.equal(response.status, 403, 'Private filesystem route must be denied.');
  results.push({ route: route.includes('secret') ? 'private-auth-route' : route, status: response.status });
}
const chromePath = ['C:/Program Files/Google/Chrome/Application/chrome.exe',
  'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe',
  path.join(process.env.LOCALAPPDATA || '', 'Google/Chrome/Application/chrome.exe')].find(fs.existsSync);
assert.ok(chromePath, 'Installed Chrome is required for the browser smoke check.');
const browser = await chromium.launch({ executablePath: chromePath, headless: true });
try {
  const page = await browser.newPage();
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.goto(origin, { waitUntil: 'networkidle' });
  assert.ok(await page.locator('canvas').count() > 0, 'The workstation chart must render.');
  assert.deepEqual(errors, [], 'The main document must initialize without runtime exceptions.');
  await page.goto(origin + '/info', { waitUntil: 'networkidle' });
  assert.ok((await page.title()).length > 0);
  assert.deepEqual(errors, [], 'The review shell must initialize without runtime exceptions.');
  results.push({ browser: 'Chrome headless', chart_canvas: true, review_initialized: true, page_errors: errors });
} finally { await browser.close(); }
fs.writeFileSync(path.join(out, 'runtime-smoke-results.json'), JSON.stringify({ status: 'PASS', results }, null, 2));
console.log(JSON.stringify({ status: 'PASS', http_checks: results.filter(x => x.status).length, raw_rows: source.length, browser: 'PASS' }));
