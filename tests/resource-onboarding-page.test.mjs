import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import vm from 'node:vm';

const html = readFileSync('website/connections.html', 'utf8');
const script = readFileSync('website/connections.js', 'utf8');
const styles = readFileSync('website/styles.css', 'utf8');
const publicSource = readFileSync('website/data/buddy-model-progress-center.js', 'utf8');
const context = { window: {} };
vm.runInNewContext(publicSource, context);
const catalog = context.window.BUDDY_MODEL_PROGRESS_CENTER;

test('GitHub Pages exposes all provider setups behind one guarded queue', () => {
  for (const id of [
    'resource-target-count', 'resource-provider-count', 'resource-account-count', 'resource-live-count',
    'resource-search', 'resource-task', 'resource-access', 'resource-queue-all',
    'resource-queue-summary', 'resource-provider-rows', 'resource-provider-row-count',
  ]) {
    assert.match(html, new RegExp(`id=["']${id}["']`), `missing #${id}`);
    assert.match(script, new RegExp(`byId\\(["']${id}["']\\)`), `unbound #${id}`);
  }
  assert.match(html, /buddy-model-progress-center\.js\?v=2/);
  assert.match(html, /connections\.js\?v=5/);
  assert.equal(catalog.providerOnboarding.length, 100);
  assert.equal(catalog.providerOnboarding.reduce((total, provider) => total + provider.targetCount, 0), 500);
  assert.equal(catalog.summary.modelTargets, 500);
});

test('the public queue stores metadata only and never automates protected signup actions', () => {
  assert.match(script, /Accounts created: 0\. Forms submitted: 0\. Payments made: 0\./);
  assert.match(script, /prepareProviderHandoff/);
  assert.match(script, /officialUrl\(provider\.officialSource\)/);
  assert.doesNotMatch(script, /document\.querySelector\([^\n]+password/i);
  assert.doesNotMatch(script, /automaticSubmission\s*:\s*true/);
  assert.ok(catalog.providerOnboarding.every((provider) => provider.automaticSubmission === false));
  assert.ok(catalog.providerOnboarding.every((provider) => provider.rawCredentialsAccepted === false));
});

test('the provider table stays horizontally scrollable on narrow screens', () => {
  assert.match(styles, /\.resource-provider-table-wrap\s*\{[^}]*overflow:\s*auto/s);
  assert.match(styles, /\.resource-provider-table\s*\{[^}]*min-width:\s*980px/s);
});
