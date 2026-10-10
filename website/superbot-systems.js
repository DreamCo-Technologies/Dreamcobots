(async function () {
  'use strict';
  const $ = id => document.getElementById(id);
  const pageSize = 30;
  let data, offset = 0;
  function element(tag, text) { const node=document.createElement(tag);node.textContent=text;return node; }
  function download(value, name) {
    const url=URL.createObjectURL(new Blob([JSON.stringify(value,null,2)],{type:'application/json'}));
    const link=document.createElement('a');link.href=url;link.download=name;link.click();
    setTimeout(()=>URL.revokeObjectURL(url),1000);
  }
  function request(ids) { return {schema_version:1,request_id:'pages-request',enabled:true,selection:ids.length?'explicit':'all_existing',bot_ids:ids,max_items:2000,batch_size:100,max_parallel:4}; }
  $('download-request').addEventListener('click',()=>download(request([]),'daily-build-request.json'));
  function draw() {
    const catalog=$('catalog').value;
    const query=$('search').value.trim().toLowerCase();
    const rows=data[catalog].filter(row=>(!$('owner').value || row.primary_owner===$('owner').value) &&
      [row.id,row.name,row.purpose,...row.capabilities].join(' ').toLowerCase().includes(query));
    const container=$('results');container.replaceChildren();
    $('results-status').textContent=`${rows.length} matching records. Showing ${rows.length ? offset+1 : 0}–${Math.min(offset+pageSize,rows.length)}.`;
    for(const row of rows.slice(offset,offset+pageSize)) {
      const card=element('article','');card.className='master-card';
      card.appendChild(element('h2',`${row.id} · ${row.name || 'Original source needed'}`));
      card.appendChild(element('p',row.purpose || 'This number is reserved; recover the original description.'));
      card.appendChild(element('p',`Owner: ${row.primary_owner}. State: ${row.state}.`));
      card.appendChild(element('p',`Source: ${row.source_refs.join(', ')}`));
      card.appendChild(element('p',`Planning candidates: ${row.candidate_bots.map(bot=>bot.name).join(', ') || 'No matching shared planner identified'}.`));
      const button=element('button','Download implementation brief');button.type='button';
      button.addEventListener('click',()=>{
        const brief={subject:row,scope:'Implement one bounded capability; do not mark a plan as execution.',
          filesToInspect:[...row.source_refs,'server/fleet-runtime.ts','server/superbot-systems.ts'],
          acceptance:['Preserve source and existing bot identity.','Add input/output contract and meaningful synthetic tests.','Verify failure paths and permissions.','Record evidence before connecting any external provider.']};
        const url=URL.createObjectURL(new Blob([JSON.stringify(brief,null,2)],{type:'application/json'}));
        const link=document.createElement('a');link.href=url;link.download=`dreamco-${catalog}-${row.id}.json`;link.click();
        setTimeout(()=>URL.revokeObjectURL(url),1000);
      });card.appendChild(button);
      if(catalog==='bots') {
        const build=element('button','Download build request');build.type='button';
        build.addEventListener('click',()=>download(request([row.id]),`build-${row.id}.json`));card.appendChild(build);
      }
      container.appendChild(card);
    }
    $('previous').disabled=offset===0;$('next').disabled=offset+pageSize>=rows.length;
  }
  try {
    const response=await fetch('https://raw.githubusercontent.com/DreamCo-Technologies/Dreamcobots/main/config/generated/superbot-crosswalk.json',{cache:'no-store'});
    if(!response.ok) throw new Error('Catalog request failed');
    data=await response.json();
    if(data.schema!=='dreamco.superbot_crosswalk.v1') throw new Error('Unsupported catalog');
    const s=data.summary;
    $('summary').textContent=`${s.proposal_slots} proposals · ${s.shared_planner_profiles} shared planning profiles · ${s.original_bot_records} original records · ${s.missing_source_proposals+s.partial_source_proposals} source gaps. Specialist capabilities still require implementation evidence.`;
    const owners=[...new Set([...data.proposals,...data.bots,...data.legacy].map(row=>row.primary_owner))].sort();
    for(const owner of owners){const option=element('option',owner);option.value=owner;$('owner').appendChild(option);}
    for(const id of ['catalog','owner','search']) $(id).addEventListener(id==='search'?'input':'change',()=>{offset=0;draw();});
    $('previous').addEventListener('click',()=>{offset=Math.max(0,offset-pageSize);draw();});
    $('next').addEventListener('click',()=>{offset+=pageSize;draw();});draw();
  } catch (_) { $('summary').textContent='System catalog is unavailable. No bot has been started.';$('previous').disabled=true;$('next').disabled=true; }
})();
