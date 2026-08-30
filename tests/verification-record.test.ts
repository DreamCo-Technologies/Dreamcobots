import { test } from 'node:test';
import assert from 'node:assert/strict';
import { summarizeVerification, toEvidenceRecord } from '../framework/buddy-platform/verification-record.js';
test('verification records normalize into evidence',()=>{const r=toEvidenceRecord({id:'t1',kind:'test',status:'pass',summary:'tests passed',source:'runner'},'2026-08-30T00:00:00Z');assert.equal(r.timestamp,'2026-08-30T00:00:00Z');assert.equal(r.status,'pass');});
test('verification summary fails closed',()=>{assert.equal(summarizeVerification([{id:'1',kind:'test',status:'blocked',summary:'waiting',source:'runner'}]).overall,'blocked');assert.equal(summarizeVerification([{id:'1',kind:'test',status:'fail',summary:'failed',source:'runner'}]).overall,'failed');assert.equal(summarizeVerification([{id:'1',kind:'test',status:'pass',summary:'passed',source:'runner'}]).overall,'verified');});
