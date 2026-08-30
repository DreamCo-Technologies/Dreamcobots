import { test } from 'node:test';
import assert from 'node:assert/strict';
import { startVibeBuildSession } from '../framework/buddy-platform/vibe-build-session.js';
import { createGenerationPlan, advanceGenerationPlan } from '../framework/buddy-platform/generation-plan.js';
test('generation plan gates work by dependency',()=>{const s=startVibeBuildSession('g1',{prompt:'build a game'});let p=createGenerationPlan(s);assert.equal(p.tasks[0].status,'ready');assert.equal(p.tasks[1].status,'blocked');p=advanceGenerationPlan(p,'requirements');assert.equal(p.tasks[1].status,'ready');assert.equal(p.tasks[2].status,'blocked');});
test('generation plan rejects unknown tasks and unmet dependencies',()=>{const p=createGenerationPlan(startVibeBuildSession('g2',{prompt:'build an app'}));assert.throws(()=>advanceGenerationPlan(p,'missing'));assert.throws(()=>advanceGenerationPlan(p,'implementation'));});
