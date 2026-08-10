import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';

const routes = readFileSync('server/routes.ts', 'utf8');

test('model benchmark routes expose connection and demand contracts', () => {
  assert.match(routes, /app\.get\("\/api\/buddy\/models\/connections"/);
  assert.match(routes, /app\.get\("\/api\/buddy\/models\/demand-ontology"/);
  assert.match(routes, /app\.post\("\/api\/buddy\/models\/demand-match"/);
  assert.match(routes, /demandModelMatchRequestSchema\.safeParse\(req\.body\)/);
  assert.match(routes, /Demand matching is locked by the kill switch/);
});
