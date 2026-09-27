import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import test from 'node:test';

const context = {module:{exports:{}}};
vm.runInNewContext(fs.readFileSync('website/buddy-setup-guide.js','utf8'), context);
const {sanitize,readModelRecord,buildPlan,SOURCES} = context.module.exports;
const plain = value => JSON.parse(JSON.stringify(value));
const record = {model:'HuggingFaceTB/SmolLM2-135M-Instruct',revision:'a'.repeat(40),
  elapsed_ms:234,created_at:'2026-09-27T10:00:00Z',execution:'local_model_inference',
  external_actions_executed:false,output:'A variable stores a value.',prompt:'Private prompt should be discarded.'};

test('malicious or stale saved choices cannot add arbitrary configuration or connection claims',()=>{
  const state = sanitize({goal:'<script>alert(1)</script>',sources:['github','github','unknown'],
    password:'not retained',connected:true,step:999,checks:{rights:'true'},modelRecord:{status:'verified'}});
  assert.equal(state.goal,'code');assert.deepEqual(plain(state.sources),['github']);
  assert.equal(state.step,0);assert.equal(state.checks.rights,false);assert.equal(state.modelRecord,null);
  assert.equal('password' in state,false);assert.equal('connected' in state,false);
});
test('acknowledgements and imported records never certify production, connectivity or training',()=>{
  const plan=buildPlan({sources:SOURCES.map(x=>x.id),checks:{rights:true,limits:true,evidence:true},modelRecord:readModelRecord(record)});
  assert.equal(plan.production_ready,false);assert.equal(plan.paid_calls_enabled,false);
  assert.equal(plan.training_status,'no_training_performed');
  assert.ok(plan.sources.every(x=>x.connected===false && x.status==='setup_required_not_verified_connected'));
  assert.equal(plan.model_test.status,'imported_record_not_independently_verified');
});
test('model import retains metadata and rejects simulations or incomplete evidence',()=>{
  const result=readModelRecord(record);
  assert.equal('prompt' in result,false);assert.equal('output' in result,false);
  assert.throws(()=>readModelRecord({...record,execution:'simulation'}));
  assert.throws(()=>readModelRecord({...record,external_actions_executed:true}));
  assert.throws(()=>readModelRecord({...record,revision:'main'}));
  assert.throws(()=>readModelRecord({...record,output:''}));
});
test('client and database setup require private backend and authorization tests',()=>{
  const plan=buildPlan({audience:'clients',sources:['database'],privacy:'private-backend'});
  assert.ok(plan.next_steps.some(x=>x.includes('separate user accounts')));
  assert.ok(plan.next_steps.some(x=>x.includes('least-privilege read')));
  assert.equal(plan.authenticated_user_created,false);
});
test('all requested learning routes have actionable steps, evidence and existing Buddy pages',()=>{
  assert.deepEqual(SOURCES.map(x=>x.id).sort().join(','),'courses,database,github,huggingface,video,web');
  for(const source of SOURCES){assert.ok(fs.existsSync('website/'+source.page));assert.ok(source.steps.length>=3);assert.ok(source.proof);assert.match(source.setup,/^https:\/\//);}
  const html=fs.readFileSync('website/setup-center.html','utf8');assert.match(html,/href="buddy-setup-guide.html"/);
});
test('saved progress survives sanitization without importing unrecognized data',()=>{
  const state=sanitize({goal:'bots',audience:'clients',device:'local-server',privacy:'public-sources',budget:'review-later',step:5,sources:['web'],checks:{rights:true}});
  assert.deepEqual(plain(sanitize(JSON.parse(JSON.stringify(state)))),plain(state));
  assert.ok(buildPlan(state).next_steps.some(x=>x.includes('stop, retry')));
});
