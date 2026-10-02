/* Owner workbench: repository metadata, source previews and browser-local change drafts. */
(() => {
  'use strict';
  if (window.DreamcoRepositoryWorkbench) return;
  window.DreamcoRepositoryWorkbench = true;
  const script = document.currentScript;
  const base = new URL('.', script.src);
  const site = path => new URL(path, base).href;
  const repo = 'https://github.com/DreamCo-Technologies/Dreamcobots';
  const encodePath = path => path.split('/').map(encodeURIComponent).join('/');
  const gh = (path, mode = 'blob') => `${repo}/${mode}/main/${encodePath(path)}`;
  const mount = document.getElementById('repository-workbench');
  if (!mount) return;
  const key = 'dreamco.repository.workbench.v1';
  let saved = {};
  let storageProblem = '';
  try { const parsed = JSON.parse(localStorage.getItem(key) || '{}'); if (parsed && !Array.isArray(parsed) && typeof parsed === 'object') saved = parsed; }
  catch (_) { storageProblem = 'Saved notes could not be loaded. You can still browse and download new drafts.'; }
  const state = {tab:'files', query:'', area:'all', page:1, data:null, bots:[], legacy:[], canonicalCount:0, coverage:null, divisions:[], fileSet:new Set(), botCache:new Map()};
  const SIZE = 40;
  function el(tag, value, cls) { const node = document.createElement(tag); if (value !== undefined) node.textContent = value; if (cls) node.className = cls; return node; }
  function button(label, fn) { const b = el('button', label, 'rw-button'); b.type = 'button'; b.addEventListener('click', fn); return b; }
  function link(label, href) { const a = el('a', label, 'rw-button'); a.href = href; return a; }
  function group(...nodes) { const g = el('div', undefined, 'rw-controls'); g.append(...nodes); return g; }
  function download(name, content, type='application/json') { const url = URL.createObjectURL(new Blob([content], {type})); const a=link(name,url);a.download=name;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000); }
  function remember(id, value) { saved[id] = {...value, updated_at:new Date().toISOString()}; try {localStorage.setItem(key,JSON.stringify(saved));return true;} catch (_) {return false;} }
  function promptLink(prompt) { return site(`buddy.html?prompt=${encodeURIComponent(prompt)}`); }
  function openDialog(title) {
    const d=el('dialog',undefined,'rw-dialog'); const header=group(el('h2',title),button('Close',()=>d.close()));
    d.append(header); document.body.append(d); d.addEventListener('close',()=>d.remove()); d.showModal(); return d;
  }
  function notice(d, text) { d.append(el('p',text,'rw-muted')); }
  function sourceLinks(d, refs) {
    const g=group(); let found=0;
    [...new Set(refs)].filter(Boolean).forEach(ref=>{const path=ref.split('#')[0]; if (state.fileSet.has(path)) {g.append(link(path,gh(path)));found++;}});
    if (found) d.append(g); else notice(d,'No matching source reference was found in this deployed file index.');
  }
  function notesEditor(d, id, label, context) {
    const box=el('section',undefined,'rw-note-editor');box.append(el('h3','Your work plan'));
    const taskId=`rw-notes-${Math.random().toString(36).slice(2)}`;
    const l=el('label','Notes, desired change, or work samples');l.htmlFor=taskId;
    const notes=el('textarea');notes.id=taskId;notes.rows=5;notes.value=saved[id]?.notes || '';notes.placeholder='Describe what you want in normal words. Add links to work samples or test results.';
    const statusId=taskId+'-status';const statusLabel=el('label','Your tracking status');statusLabel.htmlFor=statusId;
    const select=el('select');select.id=statusId;
    ['Not started','Planning','In progress','Needs review','Done locally'].forEach(value=>{const o=el('option',value);o.value=value;select.append(o);});select.value=saved[id]?.status||'Not started';
    const msg=el('p','Saved on this browser only. This does not change GitHub or certify production readiness.','rw-muted');msg.setAttribute('role','status');
    box.append(l,notes,statusLabel,select,group(button('Save my plan',()=>{const ok=remember(id,{label,notes:notes.value,status:select.value,context});msg.textContent=ok?'Saved in this browser. GitHub has not changed.':'Browser storage is unavailable. Download your plan to keep it.';render();}),button('Download plan',()=>download('buddy-change-plan.json',JSON.stringify({item:id,label,notes:notes.value,status:select.value,context,execution:'not_run'},null,2)))),msg);
    d.append(box);
  }
  function describe(row) {
    return state.data.areas.find(a=>a.id===row.area)?.description || 'Supporting repository file';
  }
  function fileDialog(row) {
    const d=openDialog(row.path);notice(d,describe(row));notice(d,'You are viewing a file record from the deployed index. GitHub links and previews use current main, which may be newer.');
    const controls=group(link('View on GitHub',gh(row.path)),link('Edit with GitHub',gh(row.path,'edit')),link('Explain with Buddy',promptLink(`Explain ${row.path} for a beginner. Show its purpose, what depends on it, and one safe small change. Read the actual source before making code claims.`)));
    if(row.path.startsWith('.github/workflows/')) controls.append(link('Workflow runs',`${repo}/actions/workflows/${encodeURIComponent(row.path.split('/').pop())}`));
    if(row.path.startsWith('website/') && row.path.endsWith('.html'))controls.append(link('Open page',site(row.path.slice(8))));
    d.append(controls);notesEditor(d,'file:'+row.path,row.path,{path:row.path});
    const textFile=/\.(?:md|txt|json|jsonc|js|mjs|cjs|ts|tsx|jsx|py|html|css|yml|yaml|toml|sh|svg|xml|sql|csv|nix)$/.test(row.path);
    if(row.protected){notice(d,'Credential-related path: browser preview is disabled. Manage this file through GitHub and your normal secret controls.');return;}
    if(!textFile){notice(d,'Use View on GitHub for this file type.');return;}
    const status=el('p','Load the current public source to read or prepare a local draft.','rw-muted');status.setAttribute('role','status');
    const editor=el('textarea');editor.className='rw-source';editor.setAttribute('aria-label','Source draft');editor.rows=14;editor.hidden=true;
    const save=button('Download edited file',()=>download(row.path.split('/').pop(),editor.value,'text/plain'));save.disabled=true;
    const load=button('Load source preview',async()=>{
      load.disabled=true;status.textContent='Loading public source…';
      const abort=new AbortController();d.addEventListener('close',()=>abort.abort(),{once:true});
      try {const response=await fetch(`https://raw.githubusercontent.com/DreamCo-Technologies/Dreamcobots/main/${encodePath(row.path)}`,{signal:abort.signal});if(!response.ok)throw Error(`HTTP ${response.status}`);
        if(Number(response.headers.get('content-length'))>262144)throw Error('Large file: open it on GitHub');
        const text=await response.text();if(text.length>262144)throw Error('Large file: open it on GitHub');
        editor.value=text;editor.hidden=false;save.disabled=false;status.textContent='Editable local draft. Download it or use GitHub’s editor to submit a reviewed change. Nothing runs here.';
      } catch(error){status.textContent=`Preview unavailable: ${error.message}. View on GitHub remains available.`;}finally{load.disabled=false;}
    });d.append(group(load,save),status,editor);
  }
  async function botDialog(row) {
    const d=openDialog(`${row.name} — portfolio & prospectus`);const slot=el('section');d.append(slot);slot.append(el('p','Loading the existing bot prospectus…'));
    const division=state.divisions.find(x=>x.id===row.division_id);
    try {
      if(!division)throw Error('Division not found');
      if(!row.legacy && !state.botCache.has(division.name)){const response=await fetch(site(`data/bot-fleet/${encodeURIComponent(division.name)}.json`));if(!response.ok)throw Error(`HTTP ${response.status}`);state.botCache.set(division.name,await response.json());}
      const shard=row.legacy?{bots:state.legacy}:state.botCache.get(division.name);const bot=(shard.bots||shard.items||[]).find(b=>b.identity.slug===row.id);if(!bot)throw Error('Bot not found in source catalog');
      slot.replaceChildren();const p=bot.prospectus||{};
      slot.append(el('p',p.mission||'Mission not recorded.'),el('p',`Division: ${division.name} · Registry status: ${row.status}. This is not independent verification of live operation.`,'rw-muted'));
      slot.append(group(link(row.legacy?'Historical source document':'Existing full prospectus',row.legacy?gh(row.source_refs[0]):site(`bots.html?prospectus=${encodeURIComponent(row.id)}`)),link('Ask Buddy about this bot',site(`buddy.html?${row.legacy?'':`bot=${encodeURIComponent(row.id)}&`}prompt=${encodeURIComponent(`Explain ${row.name} using ${row.source_refs.join(', ')} and help me build one useful feature. This ${row.legacy?'historical concept':'bot profile'} needs source evidence and required setup.`)}`)),button('Download portfolio',()=>download(`${row.id}-portfolio.json`,JSON.stringify({identity:bot.identity,prospectus:p,capabilities:bot.capabilities,readiness:bot.readiness,evidence:bot.evidence,historical_specification:bot.historical_specification||null,owner_plan:saved['bot:'+row.id]||null,truth:'Catalog and owner notes; not a verified customer-results portfolio.'},null,2)))));
      if(row.legacy){notice(slot,`Historical record · source category: ${row.source_division} · ${row.accounting_state.replaceAll('_',' ')}. ${row.same_name_source_records} historical records share this normalized name. These are not extra verified runtimes.`);if(bot.historical_specification){const archive=el('details');archive.append(el('summary','Preserved historical specification'),el('pre',bot.historical_specification));slot.append(archive);}}
      const sections=[['Who it helps',p.target_users],['Offer and pricing plan',`${p.catalog_business_model||'Not recorded'} · ${p.catalog_price_range||'Not recorded'} (catalog plan; not earnings evidence)`],['Inputs',p.inputs],['Outputs',p.outputs],['Limitations',p.limitations]];
      for(const [title,value] of sections){const details=el('details');details.append(el('summary',title),el('p',Array.isArray(value)?value.join(' · '):String(value||'Not recorded')));slot.append(details);}
      const cap=el('details');cap.open=true;cap.append(el('summary','Capabilities and source evidence'));for(const c of bot.capabilities||[]){const section=el('div',undefined,'rw-cap');section.append(el('strong',c.name),group(link('Explain this capability',promptLink(`Explain ${row.name}: ${c.name}. Use ${c.source||'the bot registry'} as evidence. Give a beginner example and label unverified features.`))));sourceLinks(section,[c.source,c.test_evidence]);cap.append(section);}slot.append(cap);
      const readiness=el('details');readiness.append(el('summary','Readiness and configuration'),el('pre',JSON.stringify(bot.readiness||{},null,2)));slot.append(readiness);
      const works=el('details');works.open=true;works.append(el('summary','Portfolio evidence and work samples'),el('p','Source references show implementation provenance. Add your own completed work links and results below; no customer results are invented.'));sourceLinks(works,[...row.source_refs,...row.evidence_refs]);slot.append(works);
    }catch(error){slot.replaceChildren(el('p',`Portfolio data could not load: ${error.message}`),link('Open bot catalog',site(`bots.html?prospectus=${encodeURIComponent(row.id)}`)));}
    notesEditor(d,'bot:'+row.id,row.name,{bot:row.id,division:row.division_id});
  }
  function pageDialog(path) {
    const d=openDialog(path.replace(/\.html$/,'').replaceAll('-',' '));
    d.append(group(link('Open this page',site(path)),link('View page source',gh('website/'+path)),button('Inspect page file',()=>{d.close();fileDialog(state.data.items.find(x=>x.path==='website/'+path));})),el('p','Use Explore info on the page to turn a section or selected text into a learning or change plan.'));
    notesEditor(d,'page:'+path,path,{page:path});
  }
  mount.classList.add('rw-shell');
  const heading=el('header');heading.append(el('p','BUDDY · YOUR REPOSITORY','rw-kicker'),el('h2','Find it. Understand it. Change it.'),el('p','Browse all tracked files, pages, and registered bots. Use small change plans to learn as you build.'));
  const summary=el('p','Loading repository index…','rw-muted');summary.setAttribute('role','status');
  const tabs=group();tabs.setAttribute('aria-label','Repository views');const tabButtons={};
  for(const [id,label] of [['files','All files'],['pages','All pages'],['bots','Bot portfolios'],['plans','My work plans'],['coverage','Project coverage']]){const b=button(label,()=>{state.tab=id;state.page=1;state.area='all';area.value='all';render();});b.dataset.view=id;tabButtons[id]=b;tabs.append(b);}
  const searchLabel=el('label','Find a file, page, or bot');const search=el('input');search.type='search';search.id='rw-search';search.placeholder='Try payments, memory, website, or a bot name';searchLabel.htmlFor=search.id;
  search.addEventListener('input',()=>{state.query=search.value;state.page=1;render();});
  const areaLabel=el('label','Folder');const area=el('select');area.id='rw-area';areaLabel.htmlFor=area.id;const all=el('option','All folders');all.value='all';area.append(all);area.addEventListener('change',()=>{state.area=area.value;state.page=1;render();});
  const results=el('div',undefined,'rw-results');results.id='rw-results';const count=el('p','','rw-muted');count.setAttribute('role','status');const pager=group();
  const prev=button('Previous',()=>{state.page--;render();});const next=button('Next',()=>{state.page++;render();});const pageLabel=el('span');pager.append(prev,pageLabel,next);
  const exportButton=button('Download my work plans',()=>download('buddy-work-plans.json',JSON.stringify({scope:'browser-local drafts; no GitHub changes applied',plans:saved},null,2)));
  const help=el('details');help.append(el('summary','New to coding? Start with one small change'),el('p','1. Find a page or file. 2. Open its details and ask Buddy to explain it. 3. Write the change you want and what success looks like. 4. Read or edit a local draft. 5. Use Edit with GitHub to propose the change. 6. Review checks before merging and deploying. GitHub sign-in and repository permission are required to save there.'));
  mount.append(heading,summary,tabs,searchLabel,search,areaLabel,area,count,results,pager,group(exportButton,link('GitHub changes and reviews',repo+'/pulls'),link('Deployment checks',repo+'/actions')),help);
  if(storageProblem)mount.append(el('p',storageProblem,'rw-muted'));
  function rows() {
    const q=state.query.toLowerCase().trim();
    if(state.tab==='coverage')return state.coverage.items.filter(x=>`${x.name} ${x.scope}`.toLowerCase().includes(q));
    if(state.tab==='files')return state.data.items.filter(x=>(state.area==='all'||x.area===state.area)&&`${x.path} ${x.kind}`.toLowerCase().includes(q));
    if(state.tab==='pages')return state.data.pages.filter(x=>x.toLowerCase().includes(q));
    if(state.tab==='bots')return state.bots.filter(x=>`${x.name} ${x.id} ${x.division_id} ${x.category}`.toLowerCase().includes(q));
    return Object.entries(saved).filter(([id,x])=>`${id} ${x.label} ${x.notes}`.toLowerCase().includes(q));
  }
  function render() {
    if(!state.data)return;
    Object.entries(tabButtons).forEach(([id,b])=>b.setAttribute('aria-pressed',String(id===state.tab)));
    area.hidden=areaLabel.hidden=state.tab!=='files';const filtered=rows();const total=Math.max(1,Math.ceil(filtered.length/SIZE));state.page=Math.max(1,Math.min(state.page,total));
    const start=(state.page-1)*SIZE;count.textContent=`${filtered.length.toLocaleString()} matching ${state.tab} · showing ${filtered.length?start+1:0}–${Math.min(start+SIZE,filtered.length)}`;
    results.replaceChildren();
    filtered.slice(start,start+SIZE).forEach(row=>{
      const card=el('article',undefined,'rw-card');
      if(state.tab==='files'){card.append(button(row.path,()=>fileDialog(row)),el('small',`${row.kind.replaceAll('_',' ')}${row.protected?' · protected preview':''}`));}
      if(state.tab==='pages'){card.append(button(row,()=>pageDialog(row)),link('Open page',site(row)));}
      if(state.tab==='bots'){card.append(button(row.name,()=>botDialog(row)),el('small',`${row.division_id} · ${row.legacy?'historical record':'canonical profile'} · ${row.status}`));}
      if(state.tab==='coverage'){card.append(el('strong',row.name),el('p',row.scope),el('small',row.coverage_status.replaceAll('_',' ')),button('Inspect coverage',()=>{const d=openDialog(row.name);notice(d,row.scope);notice(d,state.coverage.truth);sourceLinks(d,row.source_refs);notesEditor(d,'coverage:'+row.id,row.name,{feature:row.id});}));}
      if(state.tab==='plans'){const[id,plan]=row;card.append(el('strong',plan.label||id),el('p',plan.status||'Planning'),el('p',plan.notes||'No notes'),button('Open plan',()=>{const d=openDialog(plan.label||id);notesEditor(d,id,plan.label||id,plan.context||{});}));}
      results.append(card);
    });
    if(!filtered.length)results.append(el('p',state.tab==='plans'?'No work plans saved yet. Open any file, page, or bot to create one.':'No matches. Try a shorter name or clear the folder filter.'));
    prev.disabled=state.page===1;next.disabled=state.page===total;pageLabel.textContent=`Page ${state.page} of ${total}`;
  }
  async function start() {
    try {
      const loaded=await Promise.all(['repository-browser.json','bots.json','divisions.json','legacy-bots.json','project-coverage.json'].map(async name=>{const r=await fetch(site('data/command-center/'+name),{cache:'no-store'});if(!r.ok)throw Error(`${name}: HTTP ${r.status}`);return r.json();}));
      [state.data]=loaded;state.coverage=loaded[4];const markdownSources=new Map(loaded[3].canonical_markdown_links.map(x=>[x.canonical_id,x.path]));state.canonicalCount=loaded[1].items.length;state.bots=[...loaded[1].items.map(x=>({...x,source_refs:[...x.source_refs,...(markdownSources.has(x.id)?[markdownSources.get(x.id)]:[])]})),...loaded[3].items];state.legacy=loaded[3].bots;state.divisions=loaded[2].items;state.fileSet=new Set(state.data.items.map(x=>x.path));
      state.data.areas.forEach(x=>{const o=el('option',x.id);o.value=x.id;area.append(o);});
      summary.textContent=`${state.data.items.length.toLocaleString()} tracked files · ${state.data.pages.length} pages · ${state.canonicalCount.toLocaleString()} canonical bot portfolios + ${state.legacy.length} historical records. Includes generated files and legacy sources. Work plans stay on this browser; GitHub edits use GitHub’s signed-in editor.`;
      const params=new URLSearchParams(location.search);const view=params.get('view');if(tabButtons[view])state.tab=view;state.query=params.get('q')||'';search.value=state.query;render();
      const file=params.get('file');if(file){const row=state.data.items.find(x=>x.path===file);if(row)fileDialog(row);else summary.textContent+=' Requested file was not found.';}
      const bot=params.get('bot');if(bot){const row=state.bots.find(x=>x.id===bot);if(row)botDialog(row);else summary.textContent+=' Requested bot was not found.';}
    }catch(error){summary.textContent=`Repository index unavailable: ${error.message}. Retry or open GitHub directly.`;results.replaceChildren(button('Retry loading',start),link('Open repository',repo));}
  }
  start();
})();
