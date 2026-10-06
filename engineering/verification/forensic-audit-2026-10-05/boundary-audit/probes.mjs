import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { createHash } from 'node:crypto';
import { fileURLToPath, pathToFileURL } from 'node:url';

// Isolated diagnostics. No production store inventory, pipe, HTTP server,
// detector process, or RAW write is invoked.
const directory = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(directory, '../../../..');
const moduleUrl = (name) => pathToFileURL(path.join(root, 'apps/chart/server', name));
const { prepareIndicatorRangeInput, runIndicatorRangeCalculation } = await import(moduleUrl('indicator-range-input.js'));
const { createCalculationCoordinator, parseEngineConcurrency } = await import(moduleUrl('calculation-coordinator.js'));
const { cachePathForRaw, readCalculationCache, writeCalculationCache } = await import(moduleUrl('calculation-cache.js'));
const { captureRawInputIdentity, assertRawInputUnchanged } = await import(moduleUrl('raw-input-identity.js'));
const evidence = { seed: 530105, safety: 'Only this boundary-audit directory is written. No pipe, server, browser, Python child, store inventory, or production RAW mutation.', checks: {} };
const scratch = fs.mkdtempSync(path.join(directory, 'scratch-'));
const row = (time) => ({ time, open: '1.000000000000000001', high: '2.000000000000000001', low: '0.999999999999999999', close: '1.000000000000000002' });
const bucket = (time, timeframe) => Math.floor(time / timeframe) * timeframe;
let seed = evidence.seed;
const random = () => { seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0; return seed / 4294967296; };
let assertions = 0;
for (let run = 0; run < 500; run++) {
  const timeframe = [5, 15, 30, 60, 90, 300][Math.floor(random() * 6)];
  const rows = [];
  for (let index = 0; index < 240; index++) if (random() > 0.22) rows.push(row(6000 + index * 5));
  const occupied = [...new Set(rows.map((item) => bucket(item.time, timeframe)))];
  const first = Math.floor(random() * occupied.length);
  const last = first + Math.floor(random() * (occupied.length - first));
  const from = occupied[first];
  const to = occupied[last];
  const oracle = rows.filter((item) => bucket(item.time, timeframe) >= from && bucket(item.time, timeframe) <= to);
  const prepared = prepareIndicatorRangeInput(rows, { from, to, chartTimeframeSeconds: timeframe });
  assert.deepEqual(prepared.rows, oracle); assertions++;
  assert.equal(prepared.usesCompleteSource, first === 0 && last === occupied.length - 1); assertions++;
  assert(prepared.rows.every((item) => rows.includes(item))); assertions++;
  assert.equal(prepared.rows[0].open, '1.000000000000000001'); assertions++;
  const whole = prepareIndicatorRangeInput(rows, { from: occupied[0], to: occupied.at(-1), chartTimeframeSeconds: timeframe });
  assert.equal(whole.rows, rows); assertions++;
}
const sparse = [60,65,70,75,80,85,120,125,130,135,140,145,150,155].map(row);
const sparseSelected = prepareIndicatorRangeInput(sparse, { from: 60, to: 120, chartTimeframeSeconds: 30 });
assert.deepEqual([...new Set(sparseSelected.rows.map((item) => bucket(item.time, 30)))], [60,120]);
assert.equal(sparseSelected.usesCompleteSource, false);
assert.throws(() => prepareIndicatorRangeInput(sparse, { from: 90, to: 120, chartTimeframeSeconds: 30 }), /endpoints/);
assert.throws(() => prepareIndicatorRangeInput(sparse, { from: 61, to: 120, chartTimeframeSeconds: 30 }), /boundaries/);
let invocation;
const fullResult = await runIndicatorRangeCalculation({ rows: sparse, sourcePath: 'isolated-original.json', from: 60, to: 150, chartTimeframeSeconds: 30, run: (sourcePath, bounds) => { invocation = { sourcePath, bounds }; return 'result'; } });
assert.equal(fullResult, 'result');
assert.deepEqual(invocation, { sourcePath: 'isolated-original.json', bounds: { fromTime: 60, toTime: 155, usesCompleteSource: true, rowCount: 14 } });
evidence.checks.range = { status: 'PASS', histories: 500, differentialAssertions: assertions, sparsePrefixPreserved: [60,120], missingEndpointRejected: true, fullSourceArrayIdentity: true, fullSourceRunner: invocation, stringPricesPreserved: true };

for (let concurrency = 1; concurrency <= 8; concurrency++) assert.equal(parseEngineConcurrency(String(concurrency)), concurrency);
for (const invalid of ['0','9','1.0',' 1',1,null]) assert.throws(() => parseEngineConcurrency(invalid));
assert.equal(parseEngineConcurrency(undefined), 1);
const coordinator = createCalculationCoordinator({ maxActive: 2 });
const starts = [];
const releases = new Map();
const results = [];
let executions = 0;
const execute = (key) => (publish) => { executions++; starts.push(key); for (let index = 0; index < 200; index++) publish({ index }); return new Promise((resolve) => releases.set(key, resolve)); };
results.push(coordinator.run('same', execute('same'), () => { throw new Error('Disconnected progress subscriber'); }));
const replayed = [];
const joined = coordinator.run('same', () => { throw new Error('Duplicate execution'); }, (event) => replayed.push(event.index));
assert.equal(joined, results[0]);
assert.deepEqual(replayed, Array.from({ length: 120 }, (_, index) => index + 80));
for (let index = 0; index < 9; index++) results.push(coordinator.run(`job-${index}`, execute(`job-${index}`)));
assert.deepEqual(starts, ['same', 'job-0']);
assert.deepEqual(coordinator.stats(), { active: 2, pending: 8, inFlight: 10 });
for (const key of ['same', ...Array.from({ length: 9 }, (_, index) => `job-${index}`)]) {
  assert(releases.has(key));
  releases.get(key)(key);
  await Promise.resolve();
}
assert.deepEqual(await Promise.all(results), ['same', ...Array.from({ length: 9 }, (_, index) => `job-${index}`)]);
assert.equal(executions, 10);
assert.deepEqual(starts, ['same', ...Array.from({ length: 9 }, (_, index) => `job-${index}`)]);
assert.deepEqual(coordinator.stats(), { active: 0, pending: 0, inFlight: 0 });
const shuttingDown = createCalculationCoordinator();
const active = shuttingDown.run('active', (_, signal) => new Promise((_, reject) => signal.addEventListener('abort', () => reject(new Error('Observed abort')), { once: true })));
const pending = shuttingDown.run('pending', () => { throw new Error('Queued executor must not start'); });
const observed = Promise.allSettled([active, pending]);
shuttingDown.close();
const stopped = await observed;
assert(stopped.every((item) => item.status === 'rejected'));
assert.deepEqual(shuttingDown.stats(), { active: 0, pending: 0, inFlight: 0 });
await assert.rejects(shuttingDown.run('late', () => 1), /shutting down/);
evidence.checks.coordinator = { status: 'PASS', distinctExecutions: executions, duplicatePromiseIdentity: true, boundedActive: 2, fifoStarts: starts, replayedProgress: replayed.length, subscriberExceptionIsolated: true, shutdownRejectsQueuedAndAbortsActive: true };

const resultPath = path.join(scratch, 'base.json');
const changedPath = path.join(scratch, 'changed.json');
const oldHash = createHash('sha256').update('old').digest('hex');
const newHash = createHash('sha256').update('new').digest('hex');
assert.equal(readCalculationCache(resultPath, oldHash), null);
assert.equal(cachePathForRaw(resultPath, oldHash, changedPath), resultPath);
writeCalculationCache(resultPath, oldHash, '{"result":"old"}');
assert.equal(readCalculationCache(resultPath, oldHash), '{"result":"old"}');
assert.equal(readCalculationCache(resultPath, newHash), null);
assert.equal(cachePathForRaw(resultPath, newHash, changedPath), changedPath);
writeCalculationCache(changedPath, newHash, '{"result":"new"}');
assert.equal(readCalculationCache(resultPath, oldHash), '{"result":"old"}');
assert.equal(readCalculationCache(changedPath, newHash), '{"result":"new"}');
evidence.checks.cache = { status: 'PASS', unstampedOrMissingIsMiss: true, rawDigestMismatchIsMiss: true, changedRawPathPreservesExistingSnapshot: true, exactSerializedPayload: true };

const isolatedRaw = path.join(scratch, 'isolated-input.json');
fs.writeFileSync(isolatedRaw, '{"same-size":"aaa"}');
const selected = await captureRawInputIdentity(isolatedRaw);
await assertRawInputUnchanged(isolatedRaw, selected);
fs.writeFileSync(isolatedRaw, '{"same-size":"bbb"}');
fs.utimesSync(isolatedRaw, selected.stat.atime, selected.stat.mtime);
const changed = await captureRawInputIdentity(isolatedRaw);
assert.notEqual(changed.sha256, selected.sha256);
assert.equal(changed.stat.size, selected.stat.size);
await assert.rejects(assertRawInputUnchanged(isolatedRaw, selected), /changed while calculating/);
evidence.checks.rawIdentity = { status: 'PASS', sameSizeMutationRejected: true, requestedMtimePreservation: true, actualMtimeDeltaMs: changed.stat.mtimeMs - selected.stat.mtimeMs, contentDigestChanged: true };

// Execute the exact current Source fingerprint function with scratch paths.
// It has no module initialization or runtime server effects.
const configText = fs.readFileSync(path.join(root, 'apps/chart/vite.config.js'), 'utf8');
const fingerprintSource = configText.slice(configText.indexOf('function calculationSourceFingerprint()'), configText.indexOf('\nconst inventoryMeta'));
const fingerprintFile = path.join(scratch, 'fingerprint-source.py');
fs.writeFileSync(fingerprintFile, 'value = 1\n');
const fingerprintStat = fs.statSync(fingerprintFile);
const fingerprint = vm.runInNewContext(`(${fingerprintSource})`, { createHash, fs, path, calculationSources: [fingerprintFile] });
const beforeFingerprint = fingerprint();
fs.writeFileSync(fingerprintFile, 'value = 2\n');
fs.utimesSync(fingerprintFile, fingerprintStat.atime, fingerprintStat.mtime);
const afterFingerprint = fingerprint();
assert.notEqual(afterFingerprint, beforeFingerprint);
evidence.checks.sourceFingerprint = { status: 'PASS', currentSourceFunctionExecuted: true, sameSizeContentEditChangesFingerprint: true, before: beforeFingerprint, after: afterFingerprint };

fs.writeFileSync(path.join(directory, 'probe-evidence.json'), JSON.stringify(evidence, null, 2));
console.log(JSON.stringify({ status: 'PASS', checks: Object.keys(evidence.checks), rangeAssertions: assertions, artifact: path.join(directory, 'probe-evidence.json') }));
