import { test } from 'node:test';
import assert from 'node:assert/strict';
import { startVibeBuildSession, approveStage, requireGenerationApproval } from '../framework/buddy-platform/vibe-build-session.js';

test('session requires requirements approval before generation',()=>{const s=startVibeBuildSession('s1',{prompt:'build a website'});assert.throws(()=>requireGenerationApproval(s));const approved=approveStage(s,'requirements');assert.equal(approved.stage,'ready_for_generation');assert.doesNotThrow(()=>requireGenerationApproval(approved));});
test('duplicate approval is idempotent',()=>{const s=startVibeBuildSession('s2',{prompt:'build an app'});const a=approveStage(s,'requirements');const b=approveStage(a,'requirements');assert.deepEqual(b.approvals,['requirements']);});
