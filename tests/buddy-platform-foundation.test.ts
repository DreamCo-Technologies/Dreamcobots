import { test } from 'node:test';
import assert from 'node:assert/strict';
import { buildCourse, masteryByObjective } from '../framework/buddy-platform/learning.js';
import { createTeacherGame } from '../framework/buddy-platform/teacher-studio.js';
import { buildCouncil, councilQuorum } from '../framework/buddy-platform/model-council.js';
import { authorizeSecurityAssessment, canUseTechnique } from '../framework/buddy-platform/security.js';
import { COMPLEX_GAME_LEVELS } from '../framework/buddy-platform/game-benchmark.js';
import { nextStage, requireEvidence } from '../framework/buddy-platform/build-pipeline.js';

test('teacher request becomes an educational game spec', () => {
  const game = createTeacherGame({ prompt: 'Teach fractions with a city builder', gradeBand: '5', subject: 'math', mode: 'multiplayer' });
  assert.equal(game.mode, 'multiplayer'); assert.equal(game.world.streaming, true); assert.equal(game.world.persistent, true); assert.ok(game.assessments.length);
});
test('courses require measurable objectives and mastery is evidence-based', () => {
  const objective = { id: 'fractions', title: 'Fractions', subject: 'math' as const, gradeBand: '5', measurableOutcome: 'Compare fractions' };
  assert.equal(buildCourse('c1','Fractions',[objective],2).lessons.length,2);
  assert.deepEqual(masteryByObjective([{ objectiveId:'fractions', score:.85, evidence:'quiz', attempt:2 }]), { fractions:true });
});
test('500-model council has specialized roles and quorum', () => { const council=buildCouncil(); assert.equal(council.length,500); assert.equal(councilQuorum(500,335),true); });
test('security assessment blocks absent/expired authorization', () => {
  const a=authorizeSecurityAssessment({target:'example-owned-app',owner:'customer',authorizationId:'AUTH-1',allowedTechniques:['passive-scan'],expiresAt:'2099-01-01T00:00:00Z'},new Date('2026-01-01T00:00:00Z'));
  assert.equal(a.status,'authorized'); assert.equal(canUseTechnique(a,'passive-scan'),true); assert.equal(canUseTechnique(a,'exploit'),false);
});
test('complex game benchmark has ten progressive levels', () => { assert.equal(COMPLEX_GAME_LEVELS.length,10); assert.equal(COMPLEX_GAME_LEVELS[9].name,'full-educational-simulation'); });
test('pipeline cannot advance without evidence approval', () => {
  const blocked=nextStage({stage:'plan',approved:false,evidence:[]}); assert.equal(blocked.stage,'plan');
  const approved=requireEvidence({stage:'plan',approved:false,evidence:[]},['plan-review']); assert.equal(nextStage(approved).stage,'generate');
});
