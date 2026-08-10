import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import vm from 'node:vm';

const html = readFileSync('website/models.html', 'utf8');
const script = readFileSync('website/models.js', 'utf8');
const demandSource = readFileSync('website/data/buddy-demand-ontology.js', 'utf8');
const context = { window: {} };
vm.runInNewContext(demandSource, context);
const ontology = context.window.BUDDY_DEMAND_ONTOLOGY;

test('Models page exposes three demand catalogs and 20-choice routing', () => {
  assert.equal(ontology.summary.catalogs, 3);
  assert.equal(ontology.summary.reasons, 300);
  assert.equal(ontology.summary.modelOptionsPerReason, 20);
  for (const id of ['demand-catalog-tabs', 'demand-search', 'demand-category', 'demand-reason-list']) {
    assert.match(html, new RegExp(`id=["']${id}["']`), `missing #${id}`);
    assert.match(script, new RegExp(`byId\\(["']${id}["']\\)`), `unbound #${id}`);
  }
  assert.match(script, /Compare 20/);
  assert.match(script, /Selection does not call the provider, authorize payment, or prove live availability/);
});

test('static Models page only probes a backend when explicitly configured', () => {
  assert.match(script, /window\.BUDDY_BACKEND_API_BASE/);
  assert.match(script, /get\('backend'\) === '1'/);
  assert.match(script, /if \(!backendBase\) return/);
});
