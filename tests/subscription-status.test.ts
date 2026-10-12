import test from 'node:test';
import assert from 'node:assert/strict';
import {subscriptionStatus} from '../server/subscription-status';

test('missing customer never queries Stripe', async()=>{
 const client={subscriptions:{list:async()=>{throw new Error('must not execute')}}};
 assert.equal((await subscriptionStatus(null,client)).hasActiveSubscription,false);
});
test('queries only mapped customer and rejects foreign subscription', async()=>{
 let called='';
 const client={subscriptions:{list:async(p:{customer:string})=>{called=p.customer;return {data:[{customer:'cus_other',status:'active'}]}}}};
 assert.equal((await subscriptionStatus('cus_mine',client)).hasActiveSubscription,false);
 assert.equal(called,'cus_mine');
});
test('trialing subscription belongs to mapped customer',async()=>{
 const client={subscriptions:{list:async()=>({data:[{customer:'cus_mine',status:'trialing',items:{data:[{price:{product:{metadata:{tier:'pro'}}}}]}}]})}};
 const result=await subscriptionStatus('cus_mine',client);assert.equal(result.hasActiveSubscription,true);assert.equal(result.tier,'pro');
});
test('provider failure is not converted into positive entitlement',async()=>{
 const client={subscriptions:{list:async()=>{throw new Error('offline')}}};
 await assert.rejects(()=>subscriptionStatus('cus_mine',client),/offline/);
});
