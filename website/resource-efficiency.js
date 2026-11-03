(() => {
'use strict';
const KEY='dreamco.resource-efficiency.v1';
const $=id=>document.getElementById(id);
const finite=v=>Number.isFinite(Number(v)) && Number(v)>=0 ? Number(v):null;
const escape=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let profiles=[];
try { const saved=JSON.parse(localStorage.getItem(KEY)||'[]'); if(Array.isArray(saved)) profiles=saved.filter(p=>p&&typeof p.provider==='string').slice(0,100); } catch {}
const estimate=p=>{const quota=finite(p.free),work=finite(p.workload),rate=finite(p.rate),rel=finite(p.reliability);if([quota,work,rate,rel].some(v=>v===null)||rel>100)return null;return {cost:Math.max(0,work-quota)*rate,freeUsed:Math.min(work,quota),reliability:rel};};
function render(){
const rows=profiles.map((p,i)=>({p,i,e:estimate(p)})).filter(x=>x.e).sort((a,b)=>a.e.cost-b.e.cost||b.e.reliability-a.e.reliability);
$('summary').textContent=profiles.length+' local profiles; '+rows.filter(x=>x.e.cost===0).length+' estimated at $0 for their specified workload. Estimates depend on your inputs.';
$('results').innerHTML='<table><thead><tr><th>Provider</th><th>Type</th><th>Free units used</th><th>Estimated monthly cost</th><th>Reliability</th><th>Eligibility</th><th>Action</th></tr></thead><tbody>'+rows.map(({p,i,e})=>'<tr><td>'+escape(p.provider)+'</td><td>'+escape(p.kind)+'</td><td>'+e.freeUsed.toLocaleString()+'</td><td>$'+e.cost.toFixed(2)+'</td><td>'+e.reliability+'%</td><td>'+escape(p.data==='review'?'Approval required':p.data==='local'?'Local-only':'Cloud non-sensitive only')+'</td><td><button data-remove="'+i+'" type="button">Remove</button></td></tr>').join('')+'</tbody></table>';
}
function save(){localStorage.setItem(KEY,JSON.stringify(profiles));render();}
$('profile-form').addEventListener('submit',e=>{e.preventDefault();if(profiles.length>=100){alert('Maximum 100 local profiles.');return;}const p={provider:$('provider').value.trim(),kind:$('kind').value,free:$('free').value,workload:$('workload').value,rate:$('rate').value,reliability:$('reliability').value,data:$('data').value};if(!p.provider||!estimate(p)){alert('Enter valid nonnegative numbers and reliability from 0 to 100.');return;}profiles.push(p);save();e.target.reset();});
$('results').addEventListener('click',e=>{const index=e.target.getAttribute('data-remove');if(index===null)return;profiles.splice(Number(index),1);save();});
$('clear').addEventListener('click',()=>{if(confirm('Delete all local resource profiles?')){profiles=[];save();}});
$('export').addEventListener('click',()=>{const blob=new Blob([JSON.stringify({generated_at:new Date().toISOString(),verified_live:false,profiles},null,2)],{type:'application/json'});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download='dreamco-resource-plan.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
render();
})();