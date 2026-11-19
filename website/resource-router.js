/* User-scoped resource selection. No credentials, network requests, or autonomous writes. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;root.DreamCoResourceRouter=api;})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
function plan({userId,resources,job,policy,math}){
 if(typeof userId!=='string'||!userId.trim()||!Array.isArray(resources)||!job||typeof job!=='object'||!policy||!math)return {status:'blocked',reason:'invalid_request',candidates:[]};
 if(typeof job.capability!=='string'||!job.capability.trim())return {status:'blocked',reason:'missing_capability',candidates:[]};
 const candidates=[];
 for(const resource of resources){
  if(!resource||resource.ownerId!==userId)continue;
  if(!Array.isArray(resource.capabilities)||!resource.capabilities.includes(job.capability))continue;
  const decision=policy.evaluate(resource,job);
  const estimate=math.estimate(resource);
  candidates.push({id:String(resource.id||''),eligible:decision.eligible&&!!estimate,reasons:estimate?decision.reasons:[...decision.reasons,'invalid_cost_estimate'],estimatedMonthlyCost:estimate?estimate.cost:null,reliability:estimate?estimate.reliability:null});
 }
 candidates.sort((a,b)=>Number(b.eligible)-Number(a.eligible)||(a.estimatedMonthlyCost??Infinity)-(b.estimatedMonthlyCost??Infinity)||(b.reliability??0)-(a.reliability??0));
 const winner=candidates.find(c=>c.eligible);
 return {status:winner?'candidate_only':'blocked',reason:winner?'requires_runtime_verification_and_approval':'no_eligible_resource',selectedResourceId:winner?.id||null,candidates};
}
return Object.freeze({plan});
});
