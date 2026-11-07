import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,existsSync} from 'node:fs';
import {incomeScenario} from '../website/capability-workbench.js';
import {runInNewContext} from 'node:vm';

test('income practice includes variable and fixed costs and handles nonprofitable offers',()=>{
  assert.deepEqual(incomeScenario({price:250,cost:25,leads:20,rate:5,fixed:100}),{expectedSales:1,revenue:250,contributionPerSale:225,profit:125,breakEvenSales:1});
  assert.equal(incomeScenario({price:10,cost:20,leads:100,rate:10,fixed:0}).breakEvenSales,null);
  assert.throws(()=>incomeScenario({price:10,cost:0,leads:20,rate:101,fixed:0}));
});

test('all indexed pages exist and every tracked file has a source button target',()=>{
  const index=JSON.parse(readFileSync('website/data/pages-connection-index.json','utf8'));
  assert.ok(index.files.length>1000);
  assert.equal(index.source_base,'https://github.com/DreamCo-Technologies/Dreamcobots/blob/main/');
  for(const row of index.files){
    assert.ok(existsSync(row.path),row.path);
    assert.equal(decodeURIComponent(row.source),row.path);
    assert.ok((index.source_base+row.source).startsWith('https://github.com/DreamCo-Technologies/Dreamcobots/blob/main/'));
    if(row.page)assert.ok(existsSync('website/'+row.page),row.page);
  }
});

test('workbench uses existing authorized bot router and is discoverable on every shared page',()=>{
  const js=readFileSync('website/capability-workbench.js','utf8');
  assert.ok(js.includes('BR.runControls(card)'));
  assert.ok(js.includes('bots=[...b.values()]'));
  for(const file of ['website/nav.js','website/repository-actions.js'])assert.ok(readFileSync(file,'utf8').includes('capability-workbench.html'));
});

test('step model form submission preserves the task instead of navigating away',()=>{
  let submit, prevented=false;
  const status={textContent:''};
  const form={addEventListener(type,handler){if(type==='submit')submit=handler;}};
  runInNewContext(readFileSync('website/step-models.js','utf8'),{
    window:{location:{search:''}}, URLSearchParams,
    document:{getElementById(id){return id==='task-form'?form:status;}},
    fetch:()=>new Promise(()=>{})
  });
  submit({preventDefault(){prevented=true;}});
  assert.equal(prevented,true);
  assert.match(status.textContent,/No model has been called/);
});
