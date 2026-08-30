import { test } from 'node:test';
import assert from 'node:assert/strict';
import { startVibeBuildSession, approveStage } from '../framework/buddy-platform/vibe-build-session.js';
import { createGenerationPlan } from '../framework/buddy-platform/generation-plan.js';
import { createArtifactManifest, assertArtifactEvidence } from '../framework/buddy-platform/generation-artifacts.js';
test('artifact manifest records evidence requirements',()=>{const s=approveStage(startVibeBuildSession('a1',{prompt:'build a website'}),'requirements');const m=createArtifactManifest('a1',s.plan.kind,createGenerationPlan(s));assert.equal(m.artifacts.length,1);assert.equal(m.artifacts[0].kind,'docs');});
test('evidence gate rejects unverified required artifacts',()=>{const s=approveStage(startVibeBuildSession('a2',{prompt:'build software'}),'requirements');const p=createGenerationPlan(s);const m=createArtifactManifest('a2',s.plan.kind,p);assert.throws(()=>assertArtifactEvidence({...m,artifacts:[...m.artifacts,{id:'a2-source',kind:'source',path:'generated/a2/source',purpose:'source',generatedBy:'buddy',requiresEvidence:true}]},[]));});
