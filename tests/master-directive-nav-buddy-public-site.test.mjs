import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';

const data=JSON.parse(readFileSync(new URL('../website/data/master-directive-status.json',import.meta.url),'utf8'));
const html=readFileSync(new URL('../website/master-build.html',import.meta.url),'utf8');
const js=readFileSync(new URL('../website/master-build.js',import.meta.url),'utf8');
const nav=readFileSync(new URL('../website/nav.js',import.meta.url),'utf8');
const worker=readFileSync(new URL('../website/service-worker.js',import.meta.url),'utf8');

test('master directive tracks every numbered section with honest evidence states',()=>{
  assert.equal(data.schema,'dreamco.master_directive_status.v1');
  assert.equal(data.summary.directive_sections,311);
  assert.equal(data.items.length,311);
  assert.deepEqual(data.items.map(item=>item.section),Array.from({length:311},(_,index)=>index+1));
  assert.deepEqual(data.evidence_taxonomy,['catalogued','implemented','sandbox_verified','benchmark_verified','regression_verified','production_verified']);
  for(const item of data.items){assert.ok(data.evidence_taxonomy.includes(item.status));if(item.status!=='catalogued')assert.ok(item.evidence_refs.length>0)}
  assert.equal(data.summary.status_counts.production_verified,0);
  assert.ok(data.unified_plan.source_count>100);
  assert.equal(data.unified_plan.sources.length,data.unified_plan.source_count);
  assert.equal(data.unified_plan.lanes.length,8);
  assert.equal(data.unified_plan.coordination.dependency_aware,true);
  assert.equal(data.unified_plan.coordination.shared_file_locking_required,true);
});

test('master build page renders searchable audit data and is linked in navigation',()=>{
  assert.match(html,/DreamCo Master Build/);
  assert.match(html,/id="directive-list"/);
  assert.match(html,/id="audit-grid"/);
  assert.match(html,/id="lane-grid"/);
  assert.match(html,/id="plan-source-list"/);
  assert.match(js,/master-directive-status\.json/);
  assert.match(js,/evidence_refs/);
  assert.match(nav,/master-build\.html/);
  assert.match(worker,/master-build\.html/);
  assert.match(worker,/master-directive-status\.json/);
});
