import test from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import path from 'node:path';
import { preserveOpenChart } from '../../server/ui-live-update.js';

function watchOptions(polling) {
  const program = `
    const {default: config} = await import('./vite.config.js');
    const path = await import('node:path');
    const options = config.server.watch;
    const sample = (relative) => options.ignored.some(rule =>
      typeof rule === 'function' && rule(path.resolve(relative)));
    process.stdout.write(JSON.stringify({
      options, tests: sample('tests/unit'), raw: sample('state/data/RAW'),
      server: sample('server'), ui: sample('src/chart/true-false-label.js'),
      html: sample('index.html'), stylesheet: sample('../../engine/styles/reaction-detector.css'),
      engine: sample('../../engine/pipeline/true_false.py'),
      engineArchive: sample('../../engine/engine.zip'),
    }));
  `;
  return JSON.parse(execFileSync(process.execPath, ['--input-type=module', '-e', program], {
    encoding: 'utf8',
    env: { ...process.env, TRADINGBOT_LOCAL_STATE_ROOT: '', TRADINGBOT_VITE_POLLING: polling,
      TRADINGBOT_VITE_POLL_INTERVAL_MS: '' },
  }));
}

test('VMware defaults to bounded polling for the Chart UI', () => {
  const { options, tests, raw, server, ui, html, stylesheet, engine, engineArchive } = watchOptions('');
  assert.equal(options.usePolling, true);
  assert.ok(options.interval >= 500);
  assert.equal(tests, true);
  assert.equal(raw, true);
  assert.equal(server, true);
  assert.equal(ui, false);
  assert.equal(html, false);
  assert.equal(stylesheet, false);
  assert.equal(engine, false);
  assert.equal(engineArchive, true);
});

test('filesystem polling can still be disabled explicitly', () => {
  assert.ok(watchOptions('false').options.ignored.includes('**/*'));
});

test('live updates defer navigation and circular imports while passing ordinary HMR', () => {
  const delivered = [];
  const hot = { send: payload => delivered.push(payload) };
  const workspaceRoot = path.resolve('..', '..');
  preserveOpenChart({ workspaceRoot, engineStyles: path.join(workspaceRoot, 'engine', 'styles') })
    .configureServer({ watcher: { add() {} }, environments: { client: { hot } } });
  const regular = { type: 'update', updates: [{ type: 'css-update' }] };
  hot.send(regular);
  hot.send({ type: 'full-reload', triggeredBy: path.join(workspaceRoot, 'apps', 'chart', 'index.html') });
  hot.send({ type: 'update', updates: [{ type: 'js-update', isWithinCircularImport: true }] });

  assert.equal(delivered[0], regular);
  assert.deepEqual(delivered.slice(1).map(({ event }) => event), [
    'tradingbot:ui-update-deferred', 'tradingbot:ui-update-deferred',
  ]);
  assert.equal(delivered[1].data.file, 'apps/chart/index.html');
});
