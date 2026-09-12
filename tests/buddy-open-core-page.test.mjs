import assert from 'node:assert/strict';
import fs from 'node:fs';
import test from 'node:test';

const page=fs.readFileSync('website/buddy-open-core.html','utf8');
const script=fs.readFileSync('website/buddy-open-core.js','utf8');
test('Buddy Open Core page builds honest local manifests',()=>{
  assert.match(page,/Buddy Open Core/);
  assert.match(page,/does not pretend untrained weights already exist/);
  assert.match(script,/trained_weights_created:false/);
  assert.match(script,/evidence_gates_remaining/);
  assert.match(script,/Sparse MoE requires active parameters below total/);
});
