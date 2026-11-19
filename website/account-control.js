/* Account lifecycle authorization planner. Never handles secrets or executes provider actions. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;root.DreamCoAccountControl=api;})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
const ACTIONS=Object.freeze(['create','connect','configure','read','monitor','rotate_credentials','disconnect','delete']);
const HIGH_RISK=new Set(['create','connect','configure','rotate_credentials','disconnect','delete']);
function plan(input){
 if(!input||typeof input!=='object')return {allowed:false,reasons:['invalid_request']};
 const {userId,account,action,approval,providerCapabilities}=input;
 const reasons=[];
 if(typeof userId!=='string'||!userId.trim()||!account||account.ownerId!==userId)reasons.push('owner_mismatch_or_missing');
 if(!ACTIONS.includes(action))reasons.push('unsupported_action');
 if(!Array.isArray(providerCapabilities)||!providerCapabilities.includes(action))reasons.push('provider_adapter_not_verified_for_action');
 if(!account||account.providerVerified!==true)reasons.push('provider_not_verified');
 if(!account||account.connectionState!=='authenticated')reasons.push('authenticated_connection_required');
 if(!account||!Array.isArray(account.grantedScopes)||!account.grantedScopes.includes(action))reasons.push('scope_not_granted');
 if(HIGH_RISK.has(action)){
  if(!approval||approval.userId!==userId||approval.accountId!==account?.id||approval.action!==action||approval.exactTarget!==account?.providerTarget||approval.approved!==true||!Number.isFinite(approval.expiresAt)||approval.expiresAt<=Date.now())reasons.push('fresh_exact_approval_required');
 }
 if(action==='create')reasons.push('official_signup_and_verification_handoff_required');
 if(action==='delete')reasons.push('provider_specific_deletion_confirmation_required');
 return {allowed:reasons.length===0,reasons,execution:'never_executed_by_planner'};
}
return Object.freeze({ACTIONS,plan});
});
