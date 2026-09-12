import assert from 'node:assert/strict';
import fs from 'node:fs';
import test from 'node:test';

const expertPage = fs.readFileSync('website/buddy-expert-mode.html', 'utf8');
const expertScript = fs.readFileSync('website/buddy-expert-mode.js', 'utf8');
const inventionPage = fs.readFileSync('website/buddy-invention-lab.html', 'utf8');
const inventionScript = fs.readFileSync('website/buddy-invention-lab.js', 'utf8');
const voiceScript = fs.readFileSync('website/voice-command-center.js', 'utf8');
const voiceCatalog = JSON.parse(fs.readFileSync('website/data/buddy-world-lens-voice-commands.json', 'utf8'));
const nav = fs.readFileSync('website/nav.js', 'utf8');
const worker = fs.readFileSync('website/service-worker.js', 'utf8');
const routes = fs.readFileSync('server/routes.ts', 'utf8');
const catalog = JSON.parse(fs.readFileSync('config/generated/buddy_expert_mode.json', 'utf8'));
const publicCatalogSource = fs.readFileSync('website/data/buddy-expert-mode.js', 'utf8');

test('Expert Mode exposes all resources in one deterministic seven-day assignment', () => {
  const assigned = catalog.days.flatMap((day) => day.resource_ids);
  assert.equal(catalog.days.length, 7);
  assert.equal(assigned.length, catalog.resource_index.length);
  assert.equal(new Set(assigned).size, catalog.resource_index.length);
  assert.equal(catalog.summary.repository_resources, catalog.resource_index.length);
  assert.equal(catalog.summary.runtime_verified_external_connections, 0);
  assert.equal(catalog.truth.universal_mastery_proven, false);
  assert.ok(catalog.learning_sources.sources.some((source) => source.id === 'chatgpt_connected_apps'));
  assert.ok(catalog.learning_sources.sources.some((source) => source.id === 'github'));
  assert.match(expertPage, /route to measurable competency—not instant universal mastery/i);
  assert.match(expertPage, /Resource URLs are indexed, not automatically connected/i);
  assert.match(expertScript, /scheduled_not_executed/);
  assert.match(expertScript, /learningStarted: false/);
  assert.match(expertScript, /externalRequestsStarted: false/);
  assert.match(expertScript, /resource_catalog_url/);
  assert.ok(publicCatalogSource.length < 150_000, 'public Expert payload should not duplicate the full resource catalog');
  assert.match(expertScript, /SpeechRecognition/);
});

test('Idea-to-Store exposes gated stages, resources, approvals, and no fabricated actions', () => {
  const invention = catalog.invention_navigator;
  const used = new Set(invention.stages.flatMap((stage) => stage.resource_ids));
  assert.equal(invention.stages.length, 16);
  assert.ok(invention.resources.length >= 40);
  assert.ok(invention.resources.every((resource) => used.has(resource.id)));
  assert.match(inventionPage, /customer proof, prior-art research, IP decisions/i);
  assert.match(inventionPage, /not legal advice/i);
  assert.match(inventionScript, /ownerApprovalRequiredBeforeExternalAction: true/);
  assert.match(inventionScript, /filingsSubmitted: false/);
  assert.match(inventionScript, /peopleContacted: false/);
  assert.match(inventionScript, /purchasesMade: false/);
  assert.doesNotMatch(inventionScript, /(?:local|session)Storage\.setItem/);
  assert.match(inventionScript, /cleared on reload/);
});

test('Expert and invention experiences are routed, linked, cached, and voice discoverable', () => {
  assert.match(nav, /buddy-expert-mode\.html/);
  assert.match(nav, /buddy-invention-lab\.html/);
  assert.match(worker, /\.\/buddy-expert-mode\.html/);
  assert.match(worker, /\.\/buddy-invention-lab\.html/);
  assert.match(worker, /\.\/data\/buddy-expert-mode\.js/);
  assert.match(routes, /\/api\/buddy\/expert-mode\/catalog/);
  assert.match(routes, /createBuddyExpertSprint\(request\)/);
  assert.match(routes, /evaluateBuddyExpertSprint\(evidence\)/);
  assert.match(routes, /createBuddyInventionProject\(request\)/);
  assert.match(voiceScript, /buddy-expert-mode\.html/);
  assert.match(voiceScript, /buddy-invention-lab\.html/);
  assert.ok(voiceCatalog.groups.some((group) => group.id === 'expert'));
  assert.ok(voiceCatalog.groups.some((group) => group.id === 'invention'));
});
