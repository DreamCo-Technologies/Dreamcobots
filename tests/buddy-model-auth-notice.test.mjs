import assert from 'node:assert/strict';
import { readdirSync, readFileSync } from 'node:fs';
import test from 'node:test';

const html = readFileSync('website/buddy.html', 'utf8');
const script = readFileSync('website/buddy.js', 'utf8');
const modelsHtml = readFileSync('website/models.html', 'utf8');
const modelsScript = readFileSync('website/models.js', 'utf8');
const nav = readFileSync('website/nav.js', 'utf8');

const GATED_PATHS = [
  '/api/buddy/model-benchmarks/catalog-audit',
  '/api/buddy/models/encyclopedia',
  '/api/buddy/models/connections',
  '/api/buddy/models/progress',
  '/api/buddy/models/council',
  '/api/buddy/models/demand-ontology',
  '/api/buddy/models/demand-match',
  '/api/buddy/models/select',
  '/api/buddy/model-benchmarks/plan',
  '/api/buddy/models/improvement-plan',
  '/api/buddy/open-model-lab/catalog',
  '/api/buddy/open-model-lab/comparison-plan',
  '/api/buddy/open-secure-ai-defense/model-discovery-plan',
  '/api/buddy/route-capability',
];

test('Buddy page shows a sign-in notice on gated 401 and keeps the local route fallback', () => {
  assert.match(html, /id=["']buddy-model-auth-notice["']/);
  assert.match(html, /Sign in to see live model data/);
  assert.match(html, /href=["']sign-in\.html["']/);
  assert.match(script, /response\.status === 401/);
  assert.match(script, /showBuddyModelAuthNotice/);
  assert.match(script, /if \(!response\.ok\) return fallback/);
  assert.doesNotMatch(script, /console\.(error|warn|log).{0,40}401/);
  // Reuse the existing site sign-in entry point (nav already links to sign-in.html).
  assert.match(nav, /href:\s*['"]sign-in\.html['"]/);
});

test('only website/buddy.js and website/models.js call gated model API routes', () => {
  const callers = [];
  for (const name of readdirSync('website').filter((file) => file.endsWith('.js'))) {
    if (name === 'service-worker.js') continue;
    const source = readFileSync(`website/${name}`, 'utf8');
    const hits = GATED_PATHS.filter((path) => source.includes(path));
    if (hits.length) callers.push({ name, hits });
  }
  assert.deepEqual(
    callers.map((row) => row.name).sort(),
    ['buddy.js', 'models.js'],
    `unexpected gated-route callers: ${JSON.stringify(callers)}`,
  );
  assert.ok(modelsScript.includes('/api/buddy/models/connections'));
  assert.ok(script.includes('/api/buddy/route-capability'));
  assert.match(modelsHtml, /id=["']model-live-auth-notice["']/);
  assert.match(modelsScript, /showModelLiveAuthNotice/);
});
