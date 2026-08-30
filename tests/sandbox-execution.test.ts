import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createSandboxJob } from '../framework/buddy-platform/sandbox-policy.js';
import { GovernedSandboxExecutor } from '../framework/buddy-platform/sandbox-execution.js';
test('executor validates policy and refuses execution without an isolation host',async()=>{const job=createSandboxJob('e1','p1',['npm','test']);const result=await new GovernedSandboxExecutor().run(job);assert.equal(result.status,'blocked');assert.equal(result.exitCode,null);assert.deepEqual(result.evidence,['policy-validated','execution-not-attempted']);});
test('executor fails closed on insufficient policy',async()=>{const job=createSandboxJob('e2','p2',['npm','test'],{permissions:['filesystem:workspace']});await assert.rejects(()=>new GovernedSandboxExecutor().run(job));});
