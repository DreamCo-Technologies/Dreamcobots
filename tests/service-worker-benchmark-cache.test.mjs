import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';

const source = readFileSync('website/service-worker.js', 'utf8');

test('service worker versions and caches benchmark Pages assets together', () => {
  assert.match(source, /buddy-shell-v48/);
  assert.match(source, /buddy-runtime-v48/);
  assert.match(source, /\.\/actions\.html/);
  assert.match(source, /\.\/data\/actions-health-report\.json/);
  assert.match(source, /\.\/data\/buddy-demand-ontology\.js\?v=1/);
  assert.match(source, /\.\/data\/buddy-benchmark-index\.js\?v=1/);
  assert.match(source, /\.\/data\/repository-test-registry\.json\?v=4/);
});
