import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {promotionCheck,trainingHandoff} from '../website/professional-bootcamp.js';

test('professional Bootcamp exposes all governed tracks and truthful zero claims',()=>{
  const data=JSON.parse(readFileSync('website/data/professional-bootcamp.json','utf8'));
  assert.equal(data.tracks.length,10);
  assert.equal(data.task_learning.default,'off');
  assert.equal(data.truth.trained_weight_artifacts,0);
  assert.equal(data.truth.gesture_camera_adapter_connected,false);
  const html=readFileSync('website/professional-bootcamp.html','utf8');
  assert.match(html,/Nothing is recording in the background/);
  assert.match(html,/no weights trained/i);
});

test('promotion calculator enforces repeated improvement, holdout and regression gates',()=>{
  assert.equal(promotionCheck({baseline:60,candidate:82,holdout:80,regression:1,repetitions:3}).promote,true);
  assert.equal(promotionCheck({baseline:80,candidate:82,holdout:80,regression:1,repetitions:3}).promote,false);
  assert.equal(promotionCheck({baseline:60,candidate:82,holdout:74,regression:1,repetitions:3}).promote,false);
});

test('training handoff validates rights, hash and cost and never claims training',()=>{
  const values={baseModel:'owner/base@abc',method:'LoRA',datasetSha256:'a'.repeat(64),hardware:'l4x1',maxCostUsd:10,outputRepo:'owner/private',rightsVerified:true};
  const handoff=trainingHandoff(values);
  assert.equal(handoff.weights_trained,false);
  assert.equal(handoff.status,'manifest_only_no_job_submitted');
  assert.throws(()=>trainingHandoff({...values,rightsVerified:false}));
  assert.throws(()=>trainingHandoff({...values,datasetSha256:'bad'}));
});
