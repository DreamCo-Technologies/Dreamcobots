/* Safe, deterministic job eligibility; no external actions or credential handling. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;root.DreamCoResourcePolicy=api;})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
const ALLOWED_DATA=new Set(['public','internal','sensitive']);
const ALLOWED_HANDLING=new Set(['local','approved','review']);
function evaluate(profile,job){
 const reasons=[];
 if(!profile||!job||typeof profile!=='object'||typeof job!=='object')return {eligible:false,reasons:['invalid_input']};
 if(!ALLOWED_DATA.has(job.dataClass))reasons.push('unknown_data_class');
 if(!ALLOWED_HANDLING.has(profile.data))reasons.push('unknown_provider_data_policy');
 if(profile.data==='review')reasons.push('data_approval_required');
 if(job.dataClass==='sensitive'&&profile.data!=='local')reasons.push('sensitive_data_requires_local');
 if(job.dataClass==='internal'&&profile.data==='approved'&&job.cloudApproved!==true)reasons.push('internal_cloud_approval_required');
 if(job.externalWrite===true&&!job.exactActionApproved)reasons.push('external_write_requires_exact_approval');
 if(job.requiresLiveConnection===true&&profile.verifiedLive!==true)reasons.push('verified_connection_required');
 if(job.unit&&profile.unit&&job.unit!==profile.unit)reasons.push('incompatible_usage_units');
 if(job.requiresLiveConnection===true&&(!profile.healthCheckedAt||profile.healthStatus!=='healthy'))reasons.push('healthy_connection_required');
 if(typeof job.maxMonthlyCost==='number'&&Number.isFinite(job.maxMonthlyCost)&&job.maxMonthlyCost>=0){
  if(!globalThis.DreamCoResourceMath?.estimate)reasons.push('cost_estimator_unavailable');
  else {const estimate=globalThis.DreamCoResourceMath.estimate(profile);if(!estimate||estimate.cost>job.maxMonthlyCost)reasons.push('budget_exceeded_or_invalid');}
 }
 return {eligible:reasons.length===0,reasons};
}
return Object.freeze({evaluate});
});
