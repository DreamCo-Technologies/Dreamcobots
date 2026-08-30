import { test } from 'node:test';
import assert from 'node:assert/strict';
import { prepareBuild, approveRequirements, verifyInSandbox } from '../framework/buddy-platform/build-orchestrator.js';
test('orchestrator connects planning and artifacts',()=>{const s=prepareBuild('o1','Build a multiplayer educational game');assert.equal(s.session.plan.kind,'game');assert.equal(s.generation.tasks[0].status,'ready');assert.equal(s.artifacts.projectId,'o1');});
test('orchestrator requires approval before sandbox verification',async()=>{const s=prepareBuild('o2','Build an app');await assert.rejects(()=>verifyInSandbox(s,['npm','test']));const approved=approveRequirements(s);const checked=await verifyInSandbox(approved,['npm','test']);assert.equal(checked.sandbox?.status,'blocked');});
