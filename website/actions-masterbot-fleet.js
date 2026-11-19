(function(){
"use strict";
const root=document.getElementById("masterbot-fleet-cards");
if(!root)return;
const $=id=>document.getElementById(id);
const esc=s=>String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
let bots=[];
function render(){
 const q=$("masterbot-fleet-search").value.toLowerCase(),kind=$("masterbot-fleet-filter").value;
 const rows=bots.filter(b=>(kind==="all"||b.type===kind)&&(!q||[b.name,b.mission,b.lane_id].join(" ").toLowerCase().includes(q)));
 root.innerHTML=rows.map(b=>{const id=encodeURIComponent(b.name);return `<article class="actions-control-card"><p class="actions-kicker">${esc(b.type)} MasterBot · #${b.id}</p><h3>${esc(b.name)}</h3><p>${esc(b.mission)}</p><p class="review-proof">Dedicated lane: ${esc(b.lane_id)} · ${esc(b.status)}</p><div class="actions-device-grid"><a class="btn btn-outline" href="masterbot-control-center.html?id=${id}">Dashboard</a><a class="btn btn-outline" href="buddy-command-center.html?masterbot=${id}">Command center</a><a class="btn btn-outline" href="masterbot-control-center.html?id=${id}#prospectus">Prospectus</a><a class="btn btn-outline" href="masterbot-control-center.html?id=${id}#training-queue">Training queue</a></div></article>`;}).join("");
 $("masterbot-fleet-search").setAttribute("aria-label",`Search ${bots.length} MasterBots`);
}
fetch("data/masterbot-fleet.json").then(r=>{if(!r.ok)throw Error("Fleet manifest unavailable");return r.json();}).then(data=>{
 bots=data.masterbots||[];
 const summary=data.summary||{};
 $("masterbot-fleet-summary").innerHTML=[["Total MasterBots",summary.total],["Domain MasterBots",summary.domain],["Platform MasterBots",summary.platform],["Matrix max parallel",summary.maxParallel]].map(([k,v])=>`<div><span>${esc(k)}</span><strong>${esc(v)}</strong></div>`).join("");
 $("masterbot-fleet-search").addEventListener("input",render);
 $("masterbot-fleet-filter").addEventListener("change",render);
 render();
}).catch(()=>{root.textContent="MasterBot fleet manifest could not be loaded. Check generated Pages data.";});
})();