import { test } from 'node:test';
import assert from 'node:assert/strict';
import { assertLegacyRegistryComplete, buildLegacyRegistry, legacyCapabilityTotals } from '../framework/buddy-platform/legacy-capability-registry.js';
import { assertSourcePreservation, mergeLegacyIntoPlan } from '../framework/buddy-platform/legacy-capability-bridge.js';
test('legacy inventory is registered without changing the new-system count',()=>{const r=buildLegacyRegistry();assertLegacyRegistryComplete(r);assert.deepEqual(legacyCapabilityTotals(r),{incomeBots:200,systems:12,declaredSystemFeatures:2400,registeredSources:20});});
test('legacy sources remain addressable by the universal creator',()=>{const p=mergeLegacyIntoPlan('Build an educational course and school platform');assert.equal(p.preserved,true);assert.equal(p.sourceOfTruth,'original-bots/README.md');assert.ok(p.legacySources.length>0);assertSourcePreservation(p.legacySources.map(s=>({id:s.sourceId,kind:'system',name:s.name,path:s.sourcePath,status:'registered'})));});
test('legacy preservation rejects escaped source paths',()=>{assert.throws(()=>assertSourcePreservation([{id:'x',kind:'system',name:'x',path:'outside/x.md',status:'registered'}]));});
