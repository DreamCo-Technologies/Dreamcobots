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

test('resource connection catalog embeds the validated Buddy resource registry', () => {
  const registry = catalog.buddy_resource_registry;
  assert.equal(registry.source, 'config/buddy/resource-registry.json');
  assert.equal(registry.ranked.length, 15);
  assert.ok(registry.blocked.includes('xai_outputs_for_training'));
  assert.ok(registry.secret_names_to_set.every((name) => /^[A-Z][A-Z0-9_]+$/.test(name)));
  assert.ok(fs.existsSync(registry.doc));
});

test('resource connection center offers safe setup choices without collecting secrets', () => {
  assert.match(page, /Choose a connection method/i);
  assert.match(script, /buddy-resource-connection-catalog\.json/);
  assert.match(script, /buddy-connection-catalog\.json/);
  assert.match(script, /pending_backend_review/);
  assert.match(script, /localStorage/);
  assert.match(page, /id="custom-add"/);
  assert.match(page, /Post or publish/);
  assert.match(page, /Research\/current data/);
  assert.match(script, /exact_approval_required_for_write: true/);
  assert.match(script, /live_connections_claimed: 0/);
  assert.match(script, /Open official source/);
  assert.match(script, /Use with Buddy/);
  assert.doesNotMatch(page, /type=["']password["']/i);
  assert.doesNotMatch(page + script, /paste.*secret|enter.*api.*key/i);
  assert.match(nav, /resource-connection-center\.html/);
});
