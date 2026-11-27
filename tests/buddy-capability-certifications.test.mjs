import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import vm from 'node:vm';

const certificationPath = new URL('../website/data/buddy-capability-certifications.js', import.meta.url);
const evidencePath = new URL('../website/data/bot-fleet-e2e.json', import.meta.url);

test('published capability certification matches canonical fleet E2E evidence', () => {
  const context = { window: {} };
  vm.runInNewContext(readFileSync(certificationPath, 'utf8'), context);
  const published = context.window.BUDDY_CAPABILITY_CERTIFICATIONS;
  const evidence = JSON.parse(readFileSync(evidencePath, 'utf8'));

  assert.deepEqual(JSON.parse(JSON.stringify(published.summary)), evidence.summary);
  assert.equal(Object.keys(published.bots).length, evidence.profiles.length);
  assert.equal(evidence.summary.profilesTested, evidence.profiles.length);
  assert.equal(evidence.summary.divisionsTested, evidence.divisions.length);
  assert.equal(evidence.summary.liveExternalFlowComplete, false);

  for (const profile of evidence.profiles) {
    const bot = published.bots[profile.slug];
    assert.ok(bot, profile.slug);
    assert.equal(bot.division, profile.division);
    assert.equal(bot.status, profile.status);
    assert.equal(bot.declaredCapabilityCount, profile.declaredCapabilityCount);
    assert.equal(bot.capabilityTestsPassed, profile.capabilityTestsPassed);
    assert.equal(bot.capabilityTestsFailed, profile.capabilityTestsFailed);
  }
});
