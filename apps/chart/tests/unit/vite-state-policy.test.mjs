import test from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';

function watchOptions(polling) {
  const program = "const {default: config} = await import('./vite.config.js'); process.stdout.write(JSON.stringify(config.server.watch));";
  return JSON.parse(execFileSync(process.execPath, ['--input-type=module', '-e', program], {
    encoding: 'utf8',
    env: { ...process.env, TRADINGBOT_LOCAL_STATE_ROOT: '', TRADINGBOT_VITE_POLLING: polling,
      TRADINGBOT_VITE_POLL_INTERVAL_MS: '' },
  }));
}

test('VMware default keeps filesystem watching disabled', () => {
  assert.ok(watchOptions('').ignored.includes('**/*'));
});

test('opt-in polling keeps local state and evidence outside the watcher', () => {
  const options = watchOptions('true');
  assert.equal(options.usePolling, true);
  assert.equal(options.interval, 5000);
  assert.ok(options.ignored.includes('**/state/**'));
  assert.ok(options.ignored.includes('**/engineering/archive/**'));
});
