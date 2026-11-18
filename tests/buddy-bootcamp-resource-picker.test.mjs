import assert from 'node:assert/strict';
import fs from 'node:fs';
import test from 'node:test';

const page = fs.readFileSync('website/buddy-bootcamp.html', 'utf8');
const script = fs.readFileSync('website/buddy-bootcamp-resource-picker.js', 'utf8');
const catalog = JSON.parse(fs.readFileSync('website/data/buddy-bootcamp-resource-catalog.json', 'utf8'));
const connectionCatalog = JSON.parse(fs.readFileSync('website/data/buddy-resource-connection-catalog.json', 'utf8'));

test('bootcamp offers categorized resource selection and per-user custom references', () => {
  assert.match(page, /Choose resources for this bootcamp/);
  assert.match(page, /bootcamp-resource-category/);
  assert.match(page, /Add a resource you use/);
  assert.match(page, /Download my resource selection/);
  assert.match(script, /dreamco\.buddy-bootcamp\.resources\.v1/);
  assert.match(script, /connection_status/);
  assert.match(script, /HTTPS URL without credentials/);
  assert.equal(catalog.resources.length, catalog.resource_count);
  assert.ok(catalog.resource_count >= connectionCatalog.resource_count);
  assert.ok(catalog.categories.every((category) => Number.isInteger(category.count)));
});

test('REA remains uninstalled and reconstruction requires permission plus customization', () => {
  const rea = catalog.resources.find((resource) => resource.id === 'project:rea_reverse_engineer_anything');
  assert.ok(rea);
  assert.equal(rea.connection_status, 'not_installed_or_connected');
  assert.match(page, /I own the target or have authorization/);
  assert.match(page, /reviewed REA's current code, license, dependencies, and security/);
  assert.match(page, /at least two/);
  assert.match(page, /at least 30 characters/);
  assert.match(script, /target_owner_authorization_required/);
  assert.match(script, /review_REA_current_code_license_dependencies_and_security/);
  assert.match(script, /clean_room_implementation_required/);
  assert.match(script, /minimum_distinct_changes: 2/);
  assert.match(script, /source_code_copied: false/);
});

test('bootcamp points users to the private, rights-scoped dataset study tool', () => {
  assert.match(page, /Study a dataset with Buddy/);
  assert.match(page, /buddy_discover_hf_dataset\.py/);
  assert.match(page, /private training, shared-fleet training, and publication each require separate permissions/);
  assert.match(page, /buddy_study_dataset.py/);
  assert.match(page, /User-created data remains user-owned/);
});

test('bootcamp links research findings to benchmark diagnosis and learning points', () => {
  const page = fs.readFileSync(new URL('../website/buddy-bootcamp.html', import.meta.url), 'utf8');
  assert.match(page, /BUDDY_RESEARCH_BENCHMARK_TOKEN_INTEGRATION\.md/);
  assert.match(page, /Verified code-tracking failures produce reverse-engineering plans/);
  assert.match(page, /Only verified repeated benchmark mastery can earn non-cash learning points/);
  assert.match(page, /do not start runs, change weights, execute source code, or transfer financial tokens/);
});
