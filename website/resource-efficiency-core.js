/* Shared, dependency-free calculations for browser and Node tests. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;root.DreamCoResourceMath=api;})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
const finite=value=>value!==''&&value!==null&&value!==undefined&&Number.isFinite(Number(value))&&Number(value)>=0?Number(value):null;
function estimate(p){
 if(!p||typeof p!=='object')return null;
 const quota=finite(p.free),work=finite(p.workload),rate=finite(p.rate),rel=finite(p.reliability);
 if([quota,work,rate,rel].some(v=>v===null)||rel>100)return null;
 const cost=Math.max(0,work-quota)*rate;
 if(!Number.isFinite(cost))return null;
 return {cost,freeUsed:Math.min(work,quota),reliability:rel};
}
function rank(profiles){return profiles.map((p,i)=>({p,i,e:estimate(p)})).filter(x=>x.e).sort((a,b)=>a.e.cost-b.e.cost||b.e.reliability-a.e.reliability);}
return Object.freeze({estimate,rank});
});
