import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';

const html = readFileSync('website/system-map.html', 'utf8');
const script = readFileSync('website/system-map.js', 'utf8');
const worker = readFileSync('website/service-worker.js', 'utf8');

test('system map renders searchable canonical ownership without moving files', () => {
  for (const id of ['ownership-map-title', 'ownership-map-status', 'ownership-search', 'ownership-map-grid']) {
    assert.match(html, new RegExp(`id=["']${id}["']`));
  }
  assert.match(script, /data\/command-center\/repository-inventory\.json/);
  assert.match(script, /function renderOwnership\(query\)/);
  assert.match(script, /Preserve in place/);
  assert.match(worker, /system-map\.js\?v=2/);
  assert.match(worker, /data\/command-center\/repository-inventory\.json/);
});

