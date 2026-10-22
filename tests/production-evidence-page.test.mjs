import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

test('production evidence page exposes the reconciled ledger', () => {
  const html = readFileSync('website/production-evidence.html','utf8');
  const js = readFileSync('website/production-evidence.js','utf8');
  assert.match(html,/55 REAL DIVISIONS/);
  assert.match(html,/production-evidence\.js/);
  assert.match(js,/production-evidence-ledger\.json/);
  assert.match(js,/blockers/);
});
