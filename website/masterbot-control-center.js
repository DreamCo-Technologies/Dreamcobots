(function(){
"use strict";
const DATA="data/masterbot-fleet.json";
const $=id=>document.getElementById(id);
const esc=s=>String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const params=new URLSearchParams(location.search);
let fleet=[];
function card(bot){
 const encoded=encodeURIComponent(bot.name);
 return `<article class="bot-card"><span class="pill">${esc(bot.type)}</span><span class="pill">#${bot.id}</span><h3>${esc(bot.name)}</h3><p>${esc(bot.mission)}</p><p class="muted">Lane: ${esc(bot.lane_id)} · Status: ${esc(bot.status)}</p><div class="links"><a href="masterbot-control-center.html?id=${encoded}">Dashboard</a><a href="buddy-command-center.html?masterbot=${encoded}">Command center</a><a href="masterbot-control-center.html?id=${encoded}#prospectus">Prospectus</a><a href="masterbot-control-center.html?id=${encoded}#training-queue">Training queue</a><a href="https://github.com/DreamCo-Technologies/Dreamcobots/actions/workflows/buddy-65-masterbot-training.yml">Training controls</a><a href="test-center.html">Sandbox / benchmarks</a></div></article>`;
}
function render(){
 const q=$("search").value.toLowerCase(),kind=$("kind").value;
 const chosen=params.get("id");
 let rows=fleet.filter(b=>(kind==="all"||b.type===kind)&&(!q||[b.name,b.mission,b.lane_id].join(" ").toLowerCase().includes(q)));
 if(chosen) rows=rows.filter(b=>b.name.toLowerCase()===chosen.toLowerCase());
 $("selected-title").textContent=chosen?(rows[0]?.name||"MasterBot not found"):"MasterBot fleet";
 $("selected-summary").textContent=chosen?(rows[0]?"Individual dashboard and command handoff for this registered MasterBot.":"No matching canonical MasterBot was found."):`Showing ${rows.length} of ${fleet.length} canonical MasterBots.`;
 $("fleet-grid").innerHTML=rows.length?rows.map(card).join(""):'<div class="empty">No MasterBots match this filter.</div>';
}
fetch(DATA).then(r=>{if(!r.ok)throw Error("Fleet manifest unavailable");return r.json();}).then(data=>{
 fleet=data.masterbots||[];
 $("fleet-metrics").innerHTML=[["MasterBots",data.summary.total],["Domain",data.summary.domain],["Platform",data.summary.platform],["Max parallel",data.summary.maxParallel]].map(([k,v])=>`<div class="metric"><span class="muted">${esc(k)}</span><strong>${esc(v)}</strong></div>`).join("");
 $("selected-summary").textContent=data.policy.training;
 render();
 $("search").addEventListener("input",render);$("kind").addEventListener("change",render);
}).catch(e=>{$("selected-summary").textContent=e.message;$("fleet-grid").innerHTML='<div class="empty">Could not load the canonical fleet manifest. Check the Actions build.</div>';});
})();