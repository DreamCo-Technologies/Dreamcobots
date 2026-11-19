(function(){
"use strict";
const $=id=>document.getElementById(id);
const esc=s=>String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
fetch("data/buddy-bootcamp.json").then(r=>{if(!r.ok)throw Error("Curriculum data unavailable");return r.json();}).then(data=>{
 $("bootcamp-status").textContent=`${data.levels.length} levels · ${data.sandbox_modes.length} sandbox modes · ${data.name}`;
 $("bootcamp-levels").innerHTML=data.levels.map(level=>`<article class="level"><span class="pill">Level ${level.id}</span><h3>${esc(level.name)}</h3><p>${esc(level.gate||"")}</p></article>`).join("");
 $("bootcamp-modes").innerHTML=data.sandbox_modes.map(mode=>`<span class="pill">${esc(mode.replaceAll("_"," "))}</span>`).join("");
}).catch(error=>{$("bootcamp-status").textContent=error.message;});
})();