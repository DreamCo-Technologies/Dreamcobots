import assert from 'node:assert/strict';
import fs from 'node:fs';
import test from 'node:test';

const page = fs.readFileSync('website/buddy-bootcamp.html', 'utf8');
const script = fs.readFileSync('website/dreamco-investigation-planner.js', 'utf8');
const profiles = JSON.parse(fs.readFileSync('website/data/dreamco-investigation-profiles.json', 'utf8'));

test('DreamCo planner offers modality profiles and keeps plans separate from live execution', () => {
  assert.match(page, /Prepare a DreamCo investigation plan in this browser/);
  assert.match(page, /written permission/);
  assert.match(script, /dreamco.authorized_investigation_plan.v1/);
  assert.match(script, /execution_started: false/);
  assert.match(script, /adapter_required: true/);
  assert.match(script, /No target was connected and no test ran/);
  assert.equal(Object.keys(profiles.profiles).length, 8);
  assert.match(script, /valid_local_reference_or_credential_free_https_url_required/);
  assert.match(script, /immutable_revision_or_content_hash_required/);
});
