const test=require('node:test');
const assert=require('node:assert/strict');
const {estimate,rank}=require('../website/resource-efficiency-core.js');
test('free quota is applied before paid usage',()=>assert.deepEqual(estimate({free:100,workload:125,rate:2,reliability:99}),{cost:50,freeUsed:100,reliability:99}));
test('zero-cost free-tier job',()=>assert.equal(estimate({free:100,workload:20,rate:3,reliability:90}).cost,0));
test('rejects missing, invalid, negative, infinite, and impossible inputs',()=>{
for(const p of [{free:'',workload:10,rate:1,reliability:99},{free:10,workload:-1,rate:1,reliability:99},{free:10,workload:1,rate:Infinity,reliability:99},{free:10,workload:1,rate:1,reliability:101}])assert.equal(estimate(p),null);
});
test('ranks cheaper first, then higher reliability',()=>{const p=(provider,free,reliability)=>({provider,free,workload:10,rate:1,reliability});assert.deepEqual(rank([p('expensive',0,100),p('cheap-low',10,90),p('cheap-high',10,99)]).map(x=>x.p.provider),['cheap-high','cheap-low','expensive']);});
