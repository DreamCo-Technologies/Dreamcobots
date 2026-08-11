import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import vm from 'node:vm';

const html = readFileSync('website/benchmark-tracker.html', 'utf8');
const script = readFileSync('website/benchmark-tracker.js', 'utf8');
const source = readFileSync('website/data/buddy-model-progress-center.js', 'utf8');
const nav = readFileSync('website/nav.js', 'utf8');
const serviceWorker = readFileSync('website/service-worker.js', 'utf8');
const context = { window: {} };
vm.runInNewContext(source, context);
const catalog = context.window.BUDDY_MODEL_PROGRESS_CENTER;

test('benchmark tracker publishes the complete governed model progress catalog', () => {
  assert.equal(catalog.summary.modelTargets, 500);
  assert.equal(catalog.summary.councils, 40);
  assert.equal(catalog.summary.seatsPerCouncil, 20);
  assert.equal(catalog.summary.datasetPackageTemplates, 50);
  assert.equal(catalog.summary.liveBenchmarked, 0);
  assert.equal(catalog.connections.length, 500);
  for (const id of ['readiness-gates', 'council-task', 'council-rows', 'benchmark-roadmaps', 'bootcamp-steps', 'workstream-list', 'dataset-list']) {
    assert.match(html, new RegExp(`id=["']${id}["']`), `missing #${id}`);
    assert.match(script, new RegExp(`byId\\(["']${id}["']\\)`), `unbound #${id}`);
  }
});

test('benchmark tracker is linked and cached for GitHub Pages', () => {
  assert.match(nav, /benchmark-tracker\.html/);
  assert.match(serviceWorker, /buddy-shell-v50/);
  assert.match(serviceWorker, /\.\/benchmark-tracker\.html/);
  assert.match(serviceWorker, /\.\/data\/buddy-model-progress-center\.js\?v=1/);
});

test('public tracker keeps provisional rankings and empty datasets honest', () => {
  assert.match(html, /500 targets are mapped, not 500 live company connections/);
  assert.match(html, /metadata shortlist/);
  assert.equal(catalog.repositoryDatasetInventory.dataFilesDiscovered, 0);
  assert.equal(catalog.summary.datasetRecordsIncluded, 0);
  assert.equal(catalog.summary.verifiedRevenueProduced, 0);
});
