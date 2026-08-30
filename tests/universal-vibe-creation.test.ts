import { test } from 'node:test';
import assert from 'node:assert/strict';
import { classifyCreation, planCreation } from '../framework/buddy-platform/universal-creation.js';

test('classifies universal creation targets',()=>{assert.equal(classifyCreation('make a multiplayer game'),'game');assert.equal(classifyCreation('build a website'),'website');assert.equal(classifyCreation('make a mobile app'),'app');assert.equal(classifyCreation('build SaaS software'),'software');assert.equal(classifyCreation('create a business plan'),'business');assert.equal(classifyCreation('create a course for students'),'course');});
test('creates evidence-gated learning-aware plans',()=>{const p=planCreation({prompt:'Build an educational simulation',inputMode:'mixed'});assert.equal(p.kind,'simulation');assert.ok(p.examples.length===3);assert.ok(p.gates.includes('automated tests'));assert.ok(p.gates.includes('security/privacy'));assert.ok(p.learningTrack.length===5);});
test('rejects empty intent',()=>assert.throws(()=>planCreation({prompt:'   '})));
