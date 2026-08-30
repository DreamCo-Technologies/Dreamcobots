import { test } from 'node:test';
import assert from 'node:assert/strict';
import { inferProjectType, makeVibePlan } from '../framework/buddy-platform/vibe-coding.js';

test('vibe coding classifies common project ideas', () => {
  assert.equal(inferProjectType('build a multiplayer open world game'),'game');
  assert.equal(inferProjectType('build a student website'),'website');
  assert.equal(inferProjectType('build a mobile app'),'app');
  assert.equal(inferProjectType('build business software'),'software');
  assert.equal(inferProjectType('create a science simulation'),'simulation');
});

test('vibe plan includes examples, tests, rights, security and learning', () => {
  const plan=makeVibePlan({prompt:'Build an AI tutoring app',inputMode:'mixed'});
  assert.equal(plan.projectType,'app');
  assert.ok(plan.examples.length>=3);
  assert.ok(plan.gates.includes('tests'));
  assert.ok(plan.gates.includes('rights/provenance'));
  assert.ok(plan.learningTrack.length>=3);
});

test('empty ideas are rejected', () => { assert.throws(()=>makeVibePlan({prompt:'   '})); });
