(() => {
  const $=id=>document.getElementById(id), el=(tag,text)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;return n;};
  let data;
  function render(){
    const q=$('chat-search').value.toLowerCase();const rows=data.items.filter(x=>(!x.archive_candidate||$('chat-completed').checked)&&JSON.stringify([x.title,x.plans]).toLowerCase().includes(q));
    $('chat-count').textContent=`${rows.length} conversations shown`; $('chat-list').replaceChildren();
    for(const row of rows){const card=el('details');card.className='rw-card';card.id='chat-'+row.id;const summary=el('summary',`${row.title} · ${row.status.replaceAll('_',' ')}`);card.append(summary,el('p',`${row.message_count} retrieved user messages · ${row.candidate_segments} candidate segments to review`));
      for(const field of ['old','new','missing'])card.append(el('h3',field==='old'?'Previously recorded':field==='new'?'Added in this work':'Still needed'),el('p',row[field]));
      const evidence=el('details');evidence.append(el('summary','Candidate code references — not proof of completion'));for(const path of row.candidate_source_refs){const p=el('p'),a=el('a',path);a.href='buddy-command-center.html?file='+encodeURIComponent(path);p.append(a);evidence.append(p);}card.append(evidence);
      for(const plan of row.plans){const section=el('section');section.append(el('h3',plan.goal));const ol=el('ol');plan.steps.forEach(s=>ol.append(el('li',s)));section.append(ol);card.append(section);}
      const a=el('a','Plan the next small change with Buddy');a.href='buddy.html?prompt='+encodeURIComponent(`Help me implement one requirement from ${row.title}. Read project-conversations.html#chat-${row.id} and config/conversation-index.json. Treat candidate code references as unverified. Ask for missing source details and define an acceptance test before coding.`);card.append(a);$('chat-list').append(card);
    }
  }
  fetch('data/conversation-index.json',{cache:'no-store'}).then(r=>{if(!r.ok)throw Error('HTTP '+r.status);return r.json();}).then(d=>{data=d;$('chat-summary').textContent=`${d.summary.visible_conversations} listed conversations · ${d.summary.retrieved_conversations} retrieved · ${d.summary.archive_candidates} verified complete. ${d.scope} ${d.method}`;$('chat-rule').textContent=d.completion_rule;render();const target=document.getElementById(location.hash.slice(1));if(target){target.open=true;target.scrollIntoView();}}).catch(e=>{$('chat-summary').textContent='Index unavailable: '+e.message;});
  $('chat-search').addEventListener('input',()=>data&&render());$('chat-completed').addEventListener('change',()=>data&&render());
})();
