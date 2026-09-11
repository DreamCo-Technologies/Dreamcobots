import assert from 'node:assert/strict';
import fs from 'node:fs';
import test from 'node:test';

const read = (path) => fs.readFileSync(path, 'utf8');
const catalog = JSON.parse(read('website/data/buddy-resource-connection-catalog.json'));
const page = read('website/resource-connection-center.html');
const script = read('website/resource-connection-center.js');
const nav = read('website/nav.js');

test('resource connection catalog exposes every discovered machine-readable resource host', () => {
  assert.equal(catalog.schema, 'dreamco.buddy.resource_connection_catalog.v1');
  assert.ok(catalog.resource_count > 0);
  assert.equal(catalog.resources.length, catalog.resource_count);
  assert.ok(catalog.resources.every((resource) => resource.primary_url.startsWith('https://')));
  assert.ok(catalog.resources.every((resource) => resource.source_lists.length > 0));
  assert.ok(catalog.connection_methods.includes('mcp_transport'));
});

test('resource connection center offers safe setup choices without collecting secrets', () => {
  assert.match(page, /Choose a connection method/i);
  assert.match(script, /buddy-resource-connection-catalog\.json/);
  assert.match(script, /buddy-connection-catalog\.json/);
  assert.match(script, /pending_backend_review/);
  assert.match(script, /localStorage/);
  assert.doesNotMatch(page + script, /password|paste.*secret|enter.*api.*key/i);
  assert.match(nav, /resource-connection-center\.html/);
});
