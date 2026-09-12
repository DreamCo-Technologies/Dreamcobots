import assert from 'node:assert/strict';
import fs from 'node:fs';
import test from 'node:test';

const page=fs.readFileSync('website/buddy-learning-lab.html','utf8');
const script=fs.readFileSync('website/buddy-learning-lab.js','utf8');
const nav=fs.readFileSync('website/nav.js','utf8');
const worker=fs.readFileSync('website/service-worker.js','utf8');
const routes=fs.readFileSync('server/routes.ts','utf8');

test('Buddy learning lab requires proof without modifying or releasing weights',()=>{
  assert.match(page,/Buddy Proof-Carrying Learning/);
  assert.match(page,/separate hidden holdout/);
  assert.match(page,/does not train, alter, or publish model weights/);
  assert.match(script,/hidden_holdout_improved/);
  assert.match(script,/research_references/);
  assert.match(script,/safety_not_regressed/);
  assert.match(script,/improvement_proven_owner_approval_required/);
  assert.match(script,/promoted_to_users: false/);
  assert.match(script,/global_weights_modified: false/);
  assert.match(nav,/buddy-learning-lab\.html/);
  assert.match(worker,/buddy-learning-lab\.html/);
  assert.match(routes,/app\.post\("\/api\/buddy\/open-core\/learning-evidence"/);
  assert.match(routes,/evaluateBuddyLearningEvidence\(request\)/);
});
