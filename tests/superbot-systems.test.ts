import assert from 'node:assert/strict';
import test from 'node:test';
import { once } from 'node:events';
import express from 'express';
import { SuperbotSystems, createSuperbotRouter, superbotPlanSchema } from '../server/superbot-systems';

test('every complete proposal, manifest bot and preserved legacy record has an honest bounded planning result', () => {
  const systems = SuperbotSystems.fromFile();
  for (const kind of ['proposal','bot','legacy'] as const) {
    for (const row of systems.rows(kind)) {
      const result = systems.plan({kind,id:row.id,objective:'Review the cited requirements and prepare a synthetic implementation test.'});
      assert.equal(result.planningOnly,true);
      assert.equal(result.liveExternalActionTaken,false);
      assert.notEqual(result.status,'not_found');
      if (result.status==='not_found') continue;
      assert.equal(result.capabilityImplementationVerified,false);
      assert.ok(result.taskPackets.length<=3);
      if (['missing','partial'].includes(row.source_status)) {
        assert.equal(result.status,'source_required');
        assert.equal(result.taskPackets.length,0);
      }
      for (const packet of result.taskPackets) {
        assert.equal(packet.status,'sandbox_task_packet_ready');
        assert.equal(packet.liveExternalActionTaken,false);
      }
    }
  }
});

test('legacy planning reaches an existing shared worker without promoting the legacy note', () => {
  const systems = SuperbotSystems.fromFile();
  const row = systems.rows('legacy').find(row=>row.source_refs.includes('original-bots/systems/master-bot-system.md'))!;
  assert.ok(row);
  const result = systems.plan({kind:'legacy',id:row.id,objective:'Prepare a coordinated local plan for these original bot requirements.'});
  assert.equal(result.status,'coordination_plan_ready');
  assert.equal(result.planningOnly,true);
});

test('plan input cannot enable external actions or inject execution commands', () => {
  assert.equal(superbotPlanSchema.safeParse({kind:'proposal',id:'1001',objective:'Prepare a research plan.',liveActionRequested:true}).success,false);
  assert.equal(superbotPlanSchema.safeParse({kind:'proposal',id:'1001',objective:'Prepare a research plan.',command:'run arbitrary code'}).success,false);
});

test('read-only catalog and planning HTTP contract works without a database', async () => {
  const systems = SuperbotSystems.fromFile();
  const app=express();app.use(express.json());app.use('/api/superbots',createSuperbotRouter(()=>systems));
  const server=app.listen(0,'127.0.0.1');
  try {
    await once(server,'listening');
    const address=server.address();assert.ok(address && typeof address!=='string');
    const base=`http://127.0.0.1:${address.port}/api/superbots`;
    const listing=await fetch(base+'?kind=legacy&limit=2');
    assert.equal(listing.status,200);const data=await listing.json();assert.equal(data.rows.length,2);assert.equal(data.total,281);
    assert.equal((await fetch(base+'?limit=10000')).status,400);
    const post=(body: unknown)=>fetch(base+'/plan',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(body)});
    assert.equal((await post({kind:'proposal',id:'999999',objective:'Prepare a valid bounded plan.'})).status,404);
    const missing=systems.rows('proposal').find(row=>row.source_status==='missing')!;
    assert.equal((await post({kind:'proposal',id:missing.id,objective:'Prepare a valid bounded plan.'})).status,409);
    assert.equal((await post({kind:'proposal',id:'1001',objective:'Prepare a valid bounded plan.',liveActionRequested:true})).status,400);
  } finally { server.closeAllConnections();await new Promise<void>(resolve=>server.close(()=>resolve())); }
});

test('stale catalog loader fails closed at the HTTP boundary', async () => {
  const app=express();app.use('/api/superbots',createSuperbotRouter(()=>{throw new Error('stale private server path');}));
  const server=app.listen(0,'127.0.0.1');
  try {
    await once(server,'listening');const address=server.address();assert.ok(address && typeof address!=='string');
    const response=await fetch(`http://127.0.0.1:${address.port}/api/superbots`);
    assert.equal(response.status,503);assert.ok(!(await response.text()).includes('private server path'));
  } finally { server.closeAllConnections();await new Promise<void>(resolve=>server.close(()=>resolve())); }
});
