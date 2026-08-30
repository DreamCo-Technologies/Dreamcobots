import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createSandboxJob, assertSandboxPolicy } from '../framework/buddy-platform/sandbox-policy.js';
test('sandbox defaults deny network, processes, secrets and production',()=>{const j=createSandboxJob('job1','p1',['npm','test']);assert.doesNotThrow(()=>assertSandboxPolicy(j));assert.ok(j.policy.permissions.includes('network:none'));assert.ok(j.policy.permissions.includes('production:none'));});
test('sandbox rejects unsafe traversal and invalid limits',()=>{assert.throws(()=>createSandboxJob('job2','p2',['cat','../secret']));const j=createSandboxJob('job3','p3',['npm','test'],{timeoutMs:0});assert.throws(()=>assertSandboxPolicy(j));});
