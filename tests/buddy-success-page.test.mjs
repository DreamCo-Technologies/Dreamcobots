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

test('Success Center exposes profile, tracker, ontology, division, model, and resource controls', () => {
  for (const id of [
    'success-profile-form', 'success-questionnaire', 'profile-share', 'growth-record-form', 'growth-title',
    'tracker-export', 'ontology-form', 'ontology-presets', 'division-program-select', 'division-improvement-list',
    'model-source-list', 'resource-search', 'resource-list',
  ]) {
    assert.match(html, new RegExp(`id=["']${id}["']`), `missing #${id}`);
    assert.match(script, new RegExp(`byId\\(["']${id}["']\\)`), `unbound #${id}`);
  }
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
  assert.equal(program.summary.model_benchmark_targets, 200);
  assert.equal(program.truth_contract.millionaire_outcome_guaranteed, false);
  assert.equal(program.truth_contract.external_resource_reference_means_connected, false);
  assert.equal(program.summary.verified_live_resource_hosts, 0);
});

test('Success Center uses stable responsive layouts', () => {
  assert.match(css, /grid-template-columns:/);
  assert.match(css, /@media \(max-width: 800px\)/);
  assert.doesNotMatch(css, /font-size:\s*[^;]*vw/);
  assert.doesNotMatch(css, /letter-spacing:\s*-/);
});
