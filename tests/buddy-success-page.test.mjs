import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import vm from 'node:vm';

const html = readFileSync('website/success.html', 'utf8');
const script = readFileSync('website/success.js', 'utf8');
const css = readFileSync('website/success.css', 'utf8');
const dataSource = readFileSync('website/data/buddy-success-program.js', 'utf8');
const context = { window: {} };
vm.runInNewContext(dataSource, context);
const program = context.window.BUDDY_SUCCESS_PROGRAM;
const canonical = JSON.parse(readFileSync('config/generated/buddy_success_program.json', 'utf8'));

test('published resource inventory matches canonical evidence without promoting references to live connections', () => {
  assert.deepEqual(JSON.parse(JSON.stringify(program.resource_inventory)), canonical.resource_inventory);
  const resources = program.resource_inventory.resources;
  assert.equal(program.summary.referenced_resource_hosts, resources.length);
  assert.equal(program.summary.referenced_resource_hosts, canonical.summary.referenced_resource_hosts);
  assert.equal(program.summary.source_files_scanned_for_resources, canonical.summary.source_files_scanned_for_resources);
  assert.equal(program.summary.verified_live_resource_hosts, 0);
  assert.equal(new Set(resources.map(resource => resource.host)).size, resources.length);
  assert.ok(resources.length > 0);
  for (const resource of resources) {
    assert.ok(['reference_only', 'configuration_required'].includes(resource.status), resource.host);
    assert.equal(resource.verified_live, false, resource.host);
    assert.equal(resource.health_check_evidence, null, resource.host);
    assert.ok(resource.next_step, resource.host);
  }
  assert.equal(program.truth_contract.external_resource_reference_means_connected, false);
  assert.equal(program.truth_contract.connected_status_requires_credentials_and_health_evidence, true);
});

test('Success Center exposes profile, tracker, production, alliance, trust, model, and resource controls', () => {
  for (const id of [
    'success-profile-form', 'success-questionnaire', 'profile-share', 'growth-record-form', 'growth-title',
    'tracker-export', 'ontology-form', 'ontology-presets', 'division-program-select', 'division-improvement-list',
    'division-purpose', 'division-readiness', 'daily-capabilities', 'daily-worker-roles',
    'alliance-summary', 'alliance-projects', 'alliance-dimensions', 'model-source-list', 'resource-search', 'resource-list',
  ]) {
    assert.match(html, new RegExp(`id=["']${id}["']`), `missing #${id}`);
    assert.match(script, new RegExp(`byId\\(["']${id}["']\\)`), `unbound #${id}`);
  }
});

test('every resource row links to connection setup and a citation-first Buddy research task', () => {
  assert.match(script, /resource-connection-center\.html\?resource=/);
  assert.match(script, /Research with Buddy/);
  assert.match(script, /cite the source and retrieval time/);
  assert.match(script, /do not claim a live connection/);
});

test('benchmark roles and Alliance watch items are clickable', () => {
  assert.match(script, /bots\.html\?q=/);
  assert.match(script, /alliance\.officialSources\.projects/);
  assert.match(script, /models\.html\?dimension=/);
});

test('Success Center renders stored content without HTML injection', () => {
  assert.doesNotMatch(script, /innerHTML\s*=/);
  assert.match(script, /textContent\s*=/);
});

test('generated success program is complete and honest', () => {
  assert.equal(program.questionnaire.length, 30);
  assert.equal(program.divisions.length, 45);
  assert.equal(program.summary.division_must_have_updates, 4500);
  assert.equal(program.summary.division_upgrades, 4500);
  assert.equal(program.summary.division_capabilities, 4500);
  assert.equal(program.summary.daily_logical_benchmark_slots, 360);
  assert.equal(program.summary.production_ready_divisions, 0);
  assert.equal(program.summary.model_benchmark_targets, 500);
  assert.equal(program.summary.ai_organization_records, 296);
  assert.equal(program.summary.alliance_directory_members, 196);
  assert.equal(program.truth_contract.millionaire_outcome_guaranteed, false);
  assert.equal(program.truth_contract.external_resource_reference_means_connected, false);
  assert.equal(program.summary.verified_live_resource_hosts, 0);
  assert.equal(program.open_ai_alliance_watch.memberDirectory.verifiedMemberConnections, 0);
  assert.equal(program.open_ai_alliance_watch.directorySnapshot.records, 196);
  assert.equal(program.open_ai_alliance_watch.endorsementClaimed, false);
  assert.equal(program.organization_intelligence.live_benchmarks_completed, 0);
  assert.equal(program.organization_intelligence.static_site_accepts_raw_keys, false);
  assert.equal(program.trust_and_access.zero_breach_or_fraud_guaranteed, false);
});

test('capability program selector maps to each division capability contract', () => {
  assert.match(script, /kind === 'division_capabilities' \? division\.capabilities : division\[kind\]/);
  for (const division of program.divisions) {
    assert.equal(division.capabilities.count, 100);
    assert.equal(division.capabilities.focuses.length, 10);
  }
});

test('Success Center uses stable responsive layouts', () => {
  assert.match(css, /grid-template-columns:/);
  assert.match(css, /@media \(max-width: 800px\)/);
  assert.doesNotMatch(css, /font-size:\s*[^;]*vw/);
  assert.doesNotMatch(css, /letter-spacing:\s*-/);
});
