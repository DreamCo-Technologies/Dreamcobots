import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import vm from 'node:vm';

const html = readFileSync('website/models.html', 'utf8');
const script = readFileSync('website/models.js', 'utf8');
const dataSource = readFileSync('website/data/ai-organization-intelligence.js', 'utf8');
const modelDataSource = readFileSync('website/data/buddy-model-benchmarks.js', 'utf8');
const context = { window: {} };
vm.runInNewContext(dataSource, context);
vm.runInNewContext(modelDataSource, context);
const registry = context.window.BUDDY_AI_ORGANIZATIONS;
const modelCatalog = context.window.BUDDY_MODEL_BENCHMARKS;

test('Model Lab exposes task routing, catalog exports, and per-target test preparation', () => {
  for (const id of [
    'model-route-form', 'model-route-objective', 'model-route-capabilities', 'model-route-tier',
    'model-priority-quality', 'model-priority-cost', 'model-priority-latency', 'model-priority-privacy',
    'model-route-discovery', 'model-route-status', 'model-route-results', 'export-model-json', 'export-model-csv',
  ]) {
    assert.match(html, new RegExp(`id=["']${id}["']`), `missing #${id}`);
    assert.match(script, new RegExp(`byId\\(["']${id}["']\\)`), `unbound #${id}`);
  }
  assert.equal(modelCatalog.summary.targets, 500);
  assert.ok(modelCatalog.targets.every((target) => target.promptLibrary.length >= 4));
  assert.match(script, /quality contributed 0 points/i);
});

test('Model Lab exposes organization discovery and benchmark controls', () => {
  assert.match(html, /id=["']organization-intelligence["']/);
  for (const id of [
    'organization-search', 'organization-source', 'organization-type',
    'organization-rows', 'organization-needs', 'organization-audit', 'organization-plan',
    'organization-status', 'organization-result', 'organization-detail',
  ]) {
    assert.match(html, new RegExp(`id=["']${id}["']`), `missing #${id}`);
    assert.match(script, new RegExp(`byId\\(["']${id}["']\\)`), `unbound #${id}`);
  }
});

test('organization registry keeps membership, capabilities, and connections separate', () => {
  assert.equal(registry.summary.existingBenchmarkTargets, 500);
  assert.ok(registry.summary.allianceMembers >= 190);
  assert.equal(registry.summary.organizationRecords, registry.existingProviders.length + registry.allianceMembers.length);
  assert.equal(registry.truthContract.allianceMembershipMeansProviderConnection, false);
  assert.equal(registry.truthContract.directoryMembershipMeansCapabilityVerified, false);
  assert.equal(registry.truthContract.liveBenchmarksCompleted, 0);
  assert.ok(registry.allianceMembers.every((item) => item.connectedAdapter === false));
});

test('browser organization plans never execute or accept credentials', () => {
  assert.match(script, /rawCredentialsAccepted:\s*false/);
  assert.match(script, /executionPerformed:\s*false/);
  assert.match(script, /permanentBestClaimed:\s*false/);
});
