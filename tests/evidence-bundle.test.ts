import { test } from 'node:test';
import assert from 'node:assert/strict';
import { addEvidence, assertPublishable, createEvidenceBundle } from '../framework/buddy-platform/evidence-bundle.js';
test('evidence bundle fails closed until all gates pass',()=>{let b=createEvidenceBundle('p1');assert.equal(b.overall,'blocked');assert.throws(()=>assertPublishable(b));for(const kind of ['build','test','security','performance','review'] as const)b=addEvidence(b,{id:`${kind}-1`,kind,status:'pass',summary:'verified',timestamp:'2026-08-30T00:00:00Z',source:'test'});assert.equal(b.overall,'verified');assert.doesNotThrow(()=>assertPublishable(b));});
test('failed evidence prevents publication',()=>{let b=createEvidenceBundle('p2');b=addEvidence(b,{id:'security-1',kind:'security',status:'fail',summary:'finding',timestamp:'2026-08-30T00:00:00Z',source:'test'});assert.equal(b.overall,'failed');assert.throws(()=>assertPublishable(b));});
