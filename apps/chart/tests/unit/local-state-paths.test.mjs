import test from 'node:test';
import assert from 'node:assert/strict';
import path from 'node:path';
import fs from 'node:fs';
import os from 'node:os';
import { resolveLocalStatePaths } from '../../server/local-state-paths.js';

test('default state belongs to the chart application inside the project', () => {
  const workspace = path.resolve('example', 'TradingBot');
  const paths = resolveLocalStatePaths(workspace, '');
  assert.equal(paths.root, path.join(workspace, 'apps', 'chart', 'state'));
  assert.equal(paths.raw, path.join(paths.root, 'data', 'raw'));
  assert.equal(paths.secret, path.join(paths.root, 'secret'));
  assert.ok(Object.isFrozen(paths));
});

test('custom state root controls every persistent storage path inside app state', () => {
  const workspace = path.resolve('example', 'TradingBot');
  const custom = path.join(workspace, 'apps', 'chart', 'state', 'profile with spaces');
  const paths = resolveLocalStatePaths(workspace, custom);
  assert.equal(paths.root, custom);
  for (const name of ['raw', 'cache', 'secret', 'tmp']) {
    assert.ok(path.relative(custom, paths[name]).length > 0);
    assert.ok(!path.relative(custom, paths[name]).startsWith('..'));
  }
});

test('source directories and external state roots are rejected', () => {
  const workspace = path.resolve('example', 'TradingBot');
  for (const target of [workspace, path.join(workspace, 'engine'), path.join(workspace, 'apps', 'chart', 'src'),
    path.join(workspace, 'engineering'), path.join(workspace, 'apps', 'chart', 'state-other'), `${workspace}-Local`]) {
    assert.throws(() => resolveLocalStatePaths(workspace, target), /dedicated chart state directory/);
  }
});

test('relative state configuration resolves inside the same project', () => {
  const workspace = path.resolve('example', 'TradingBot');
  assert.equal(resolveLocalStatePaths(workspace, 'apps/chart/state/profile').root,
    path.join(workspace, 'apps', 'chart', 'state', 'profile'));
});

test('whitespace configuration uses the internal default', () => {
  const workspace = path.resolve('example', 'TradingBot');
  assert.equal(resolveLocalStatePaths(workspace, '   ').root, path.join(workspace, 'apps', 'chart', 'state'));
});

test('a junction cannot redirect state outside its dedicated subtree', (t) => {
  const workspace = fs.mkdtempSync(path.join(os.tmpdir(), 'tradingbot-state-boundary-'));
  t.after(() => fs.rmSync(workspace, { recursive: true, force: true }));
  const state = path.join(workspace, 'apps', 'chart', 'state');
  const source = path.join(workspace, 'engine');
  fs.mkdirSync(state, { recursive: true });
  fs.mkdirSync(source);
  fs.symlinkSync(source, path.join(state, 'redirect'), process.platform === 'win32' ? 'junction' : 'dir');
  assert.throws(() => resolveLocalStatePaths(workspace, path.join(state, 'redirect', 'profile')), /dedicated chart state directory/);
});
