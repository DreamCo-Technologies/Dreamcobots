import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import vm from 'node:vm';

const html = readFileSync('website/security.html', 'utf8');
const script = readFileSync('website/security.js', 'utf8');
const css = readFileSync('website/security.css', 'utf8');
const dataSource = readFileSync('website/data/buddy-open-secure-ai-defense.js', 'utf8');
const context = { window: {} };
vm.runInNewContext(dataSource, context);
const catalog = context.window.BUDDY_OPEN_SECURE_AI_DEFENSE;

test('Defense Center exposes assessment, GitHub, model, and catalog controls', () => {
  for (const id of [
    'defense-assessment-form', 'defense-source-url', 'defense-revision', 'run-defense-assessment',
    'github-profile-form', 'github-login', 'github-repositories', 'prepare-github-profile',
    'model-discovery-form', 'model-source-options', 'model-task-options', 'prepare-model-discovery',
    'defense-catalog-search', 'defense-catalog-filter', 'defense-catalog-list', 'defense-ask-buddy',
  ]) {
    assert.match(html, new RegExp(`id=["']${id}["']`), `missing #${id}`);
    assert.match(script, new RegExp(`byId\\(["']${id}["']\\)`), `unbound #${id}`);
  }
});

test('Defense Center renders untrusted catalog data without HTML injection', () => {
  assert.doesNotMatch(script, /innerHTML\s*=/);
  assert.match(script, /textContent\s*=/);
  assert.match(script, /noopener noreferrer/);
});

test('Defense Center never accepts raw credentials or claims unverified connections', () => {
  assert.doesNotMatch(html, /type=["']password["']/);
  assert.doesNotMatch(html, /name=["'][^"']*token/i);
  assert.equal(catalog.truth_contract.catalog_entry_means_connected, false);
  assert.equal(catalog.truth_contract.alliance_membership_claimed, false);
  assert.equal(catalog.summary.live_company_connections, 0);
  assert.equal(catalog.model_discovery_sources.some((source) => source.connection_status === 'connected'), false);
});

test('Defense Center covers official projects, threats, and current model discovery', () => {
  assert.ok(catalog.alliance_reference_tools.length >= 6);
  assert.ok(catalog.openssf_projects.length >= 23);
  assert.ok(catalog.threat_domains.length >= 10);
  assert.ok(catalog.model_discovery_sources.length >= 8);
  assert.ok(catalog.priority_open_model_watchlist_2026.length >= 8);
});

test('Defense Center uses stable responsive controls', () => {
  assert.match(css, /grid-template-columns:/);
  assert.match(css, /@media \(max-width: 640px\)/);
  assert.doesNotMatch(css, /font-size:\s*[^;]*vw/);
  assert.doesNotMatch(css, /letter-spacing:\s*-/);
});
