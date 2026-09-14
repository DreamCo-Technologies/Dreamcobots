(()=>{
  const $=id=>document.getElementById(id),key='dreamco.buddy.personal-connections.v1';
  const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  let choices=[];
  const saved=()=>{try{return JSON.parse(localStorage.getItem(key)||'{}')}catch{return {selected:{},custom:[]}}};
  const persist=value=>localStorage.setItem(key,JSON.stringify(value));
  function render(){
    const state=saved(),query=$('my-search').value.toLowerCase(),custom=state.custom||[];
    const visible=[...choices,...custom].filter(item=>!query||JSON.stringify(item).toLowerCase().includes(query));
    $('my-status').textContent=`${Object.keys(state.selected||{}).length} selected choice${Object.keys(state.selected||{}).length===1?'':'s'} · ${custom.length} custom request${custom.length===1?'':'s'} · ${choices.length} repository choices available.`;
    $('my-options').innerHTML=visible.map(item=>`<article class="card"><span class="tag">${esc(item.kind)} · ${esc(item.status)}</span><h2>${esc(item.name)}</h2><p>${esc(item.description)}</p><p>Minimum scope: ${esc(item.scope)}</p><div class="controls">${item.setup?`<a class="btn btn-outline" target="_blank" rel="noopener noreferrer" href="${esc(item.setup)}">Open setup</a>`:''}<button class="btn btn-outline" data-select="${esc(item.id)}">${state.selected?.[item.id]?'Selected for my Buddy':'Choose for my Buddy'}</button>${custom.some(entry=>entry.id===item.id)?`<button class="btn btn-outline" data-remove="${esc(item.id)}">Remove request</button>`:''}</div></article>`).join('')||'<p>No matching choices.</p>';
  }
  Promise.all([
    fetch('data/buddy-universal-connections.json').then(response=>response.json()),
    fetch('data/buddy-world-source-compatibility.json').then(response=>response.json()),
    fetch('data/command-center/capabilities.json').then(response=>response.json())
  ]).then(([connections,world,capabilities])=>{
    choices=[
      ...connections.connections.map(item=>({id:`setup:${item.id}`,kind:'provider',name:item.name,status:item.status,description:`${item.area} connection using ${item.auth}.`,scope:'Choose the smallest provider scope; configure through the official flow.',setup:item.setup_url})),
      ...world.sources.map(item=>({id:`world:${item.id}`,kind:'world source',name:item.name,status:item.mode,description:item.problem,scope:'Source-attributed, terms-compliant use only.',setup:item.setup})),
      ...(capabilities.items||[]).slice(0,500).map(item=>({id:`repo:${item.id||item.name}`,kind:'repository capability',name:item.name||item.id,status:item.status||'cataloged',description:item.description||item.summary||'Repository capability.',scope:'Use the relevant Buddy screen and approve external actions.',setup:null}))
    ];render();
  }).catch(error=>{$('my-status').textContent=`Could not load repository choices: ${error.message}`});
  $('my-search').oninput=render;
  $('my-options').onclick=event=>{const id=event.target.dataset.select||event.target.dataset.remove;if(!id)return;const state=saved();state.selected||={};state.custom||=[];if(event.target.dataset.select){state.selected[id]=!state.selected[id];if(!state.selected[id])delete state.selected[id]}else state.custom=state.custom.filter(item=>item.id!==id);persist(state);render()};
  $('custom-add').onclick=()=>{const name=$('custom-name').value.trim(),url=$('custom-url').value.trim(),scope=$('custom-scope').value.trim();if(!name||!/^https:\/\//i.test(url)||!scope){$('my-status').textContent='Enter a name, an HTTPS URL, and the smallest approved scope.';return}const state=saved();state.custom||=[];state.selected||={};state.custom.push({id:`custom:${Date.now()}`,kind:'custom request',name,status:'pending_backend_review',description:`${$('custom-auth').value} connection request.`,scope,setup:url});persist(state);$('custom-name').value='';$('custom-url').value='';$('custom-scope').value='';render();$('my-status').textContent='Custom request saved locally. Connect it only through a reviewed backend or approved MCP server.'};
  $('my-clear').onclick=()=>{persist({selected:{},custom:[]});render();$('my-status').textContent='All local Buddy choices were disconnected.'};
  $('my-export').onclick=()=>{const packet={schema:'dreamco.buddy.personal_connection_choices.v1',exportedAt:new Date().toISOString(),warning:'Contains preferences and references, never credentials.',...saved()},url=URL.createObjectURL(new Blob([JSON.stringify(packet,null,2)],{type:'application/json'})),anchor=document.createElement('a');anchor.href=url;anchor.download='my-buddy-connection-choices.json';anchor.click();URL.revokeObjectURL(url)};
})();
