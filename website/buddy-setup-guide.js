/* Fixed choices only. Service setup and evidence review happen outside this guide. */
((root) => {
  'use strict';
  const KEY = 'dreamco.buddy.setup-guide.v1';
  const STEPS = ['Your goal', 'Your device', 'Free budget', 'Learning sources', 'Model test', 'Readiness plan'];
  const OPTIONS = {
    goal: [['code', 'Build with code', 'Start with a small working app and an acceptance test.'], ['study', 'Learn and research', 'Collect cited sources and check understanding.'], ['bots', 'Operate my bots', 'Prepare one bounded workflow with visible results.'], ['creative', 'Make useful content', 'Prepare, review and export a finished artifact.']],
    audience: [['personal', 'Just me', 'Local choices use this browser profile.'], ['clients', 'Me and my clients', 'Separate accounts, permissions and storage need a tested backend.']],
    device: [['mobile', 'Phone or tablet', 'Begin with planning and small tasks; model downloads may be too large.'], ['computer', 'Everyday computer', 'Try a small model and watch available memory.'], ['local-server', 'Computer with a local server', 'Server features still need configuration and health checks.']],
    privacy: [['local-only', 'Keep setup local', 'No service requests from this guide. Use existing local tools first.'], ['public-sources', 'Use selected public sources', 'Open provider pages yourself; check source rights before importing.'], ['private-backend', 'Plan private account access', 'Configure credentials in a protected backend, never in these pages.']],
    budget: [['zero', 'No paid provider calls', 'Start with browser features and free public resources. Device, electricity and internet costs still exist.'], ['review-later', 'Review paid options later', 'This remains a zero-paid-call plan. Enable nothing until its cost and limits are reviewed.']]
  };
  const SOURCES = [
    {id:'github', name:'GitHub repositories and Actions', page:'repositories.html', setup:'https://github.com/settings/apps', boundary:'Public files can be browsed. Private reads, writes and workflow dispatch need scoped authentication outside public Pages.', steps:['Choose a repository and record its revision.', 'Read one file or test artifact and keep its source link.', 'Before any write, configure a scoped connector and verify the review and rollback path.'], proof:'Recorded repository revision plus a successful read or authorized action result.'},
    {id:'huggingface', name:'Hugging Face models and datasets', page:'hf-hub.html', setup:'https://huggingface.co', boundary:'A model card or catalog entry is not downloaded weights, training or verified model quality.', steps:['Choose one model or dataset and review its license and resource needs.', 'For a small local model, open the model lab and run a short prompt.', 'Keep the model revision and evaluate separate held-out tasks before claiming improvement.'], proof:'Model revision, actual inference record and reviewed task scores; a training claim also needs training artifacts.'},
    {id:'web', name:'Web resources and documentation', page:'resource-connection-center.html', setup:'https://developer.mozilla.org/', boundary:'Opening a resource does not give Buddy persistent browsing or permission to copy everything on that site.', steps:['Select a public or authorized source relevant to your goal.', 'Record the source URL, date and the claim it supports.', 'Test whether the answer cites the right passage and can distinguish uncertainty.'], proof:'Source citation and a checked retrieval result; not evidence of changed model weights.'},
    {id:'courses', name:'Courses and study materials', page:'study-path.html', setup:'https://ocw.mit.edu/', boundary:'Course discovery is not enrollment, course completion, a credential or permission to reuse every asset.', steps:['Choose a lesson and check its access and reuse rules.', 'Set one learning objective and complete an exercise.', 'Keep the result and score a fresh exercise before marking the objective learned.'], proof:'Reviewed exercise, rubric and a separate test of the same skill.'},
    {id:'video', name:'Authorized videos and transcripts', page:'studio.html', setup:'https://github.com/openai/whisper', boundary:'Media processing needs a configured local or server tool. A video link alone is not a watched, transcribed or learned source.', steps:['Choose a video or transcript you own or may use.', 'Use a configured media tool; record timestamps and transcription errors.', 'Check a summary against the source and test the resulting study task.'], proof:'Authorized source, timestamped transcript or observations and reviewed output.'},
    {id:'database', name:'Databases and structured data', page:'connections.html', setup:'https://www.postgresql.org/docs/', boundary:'Database access requires a protected backend or local connector. Never put database passwords or connection strings in public Pages.', steps:['Start with a sample export or a least-privilege read-only role.', 'Store credentials in the backend secret store and allow only the selected data.', 'Test one bounded query, access denial and data deletion before enabling client use.'], proof:'Scoped query result plus permission tests; data access is not model training.'}
  ];
  const CHECKS = [['rights','I reviewed which sources I am allowed to use.'], ['limits','I understand that a saved plan does not connect services or enable autonomous actions.'], ['evidence','I will check real output and failures before calling a feature production ready.']];
  function sanitize(raw) {
    raw = raw && typeof raw === 'object' ? raw : {};
    const state = {schema:'dreamco.buddy_setup_choices.v1'};
    for (const [key, choices] of Object.entries(OPTIONS)) state[key] = choices.some(x => x[0] === raw[key]) ? raw[key] : choices[0][0];
    state.sources = SOURCES.filter(x => Array.isArray(raw.sources) && raw.sources.includes(x.id)).map(x => x.id);
    state.checks = Object.fromEntries(CHECKS.map(([id]) => [id, raw.checks?.[id] === true]));
    state.step = Number.isInteger(raw.step) && raw.step >= 0 && raw.step < STEPS.length ? raw.step : 0;
    state.modelRecord = sanitizeRecordMetadata(raw.modelRecord);
    return state;
  }
  function sanitizeRecordMetadata(record) {
    if (!record || record.model !== 'HuggingFaceTB/SmolLM2-135M-Instruct' || !/^[a-f0-9]{40}$/.test(record.revision || '') || !Number.isFinite(record.elapsed_ms) || record.elapsed_ms < 0 || !Number.isFinite(Date.parse(record.created_at))) return null;
    return {model:record.model, revision:record.revision, elapsed_ms:record.elapsed_ms, created_at:new Date(record.created_at).toISOString(), status:'imported_record_not_independently_verified'};
  }
  function readModelRecord(raw) {
    if (!raw || raw.execution !== 'local_model_inference' || raw.external_actions_executed !== false || typeof raw.output !== 'string' || !raw.output.trim()) throw new Error('Use the JSON test record downloaded by the Buddy local model lab.');
    const record = sanitizeRecordMetadata(raw);
    if (!record) throw new Error('The model test record is missing a supported model, revision, date or duration.');
    return record;
  }
  function label(key, value) { return OPTIONS[key].find(x => x[0] === value)?.[1] || value; }
  function buildPlan(raw, now = new Date().toISOString()) {
    const state = sanitize(raw);
    const next = ['Choose one small task and write the expected result.', 'Run the task, retain its output and test at least one failure path.'];
    if (state.audience === 'clients') next.push('Configure and test separate user accounts, server-side authorization, isolated storage and sign-out before onboarding clients.');
    if (state.privacy === 'private-backend' || state.sources.includes('database')) next.push('Set up a protected backend connector and verify a least-privilege read before allowing private data access.');
    if (state.goal === 'bots') next.push('Select one bot, compare its original specification with its actual runner and test stop, retry and duplicate-action handling.');
    if (state.goal === 'code') next.push('Open a small project in the coding workspace; edit, test, save and review its changes before publishing.');
    if (!state.modelRecord) next.push('If your device supports it, run the local model lab and download a test record; otherwise retain the model step as not tested.');
    next.push('Verify the deployed revision, required checks and the intended user journey before making a production claim.');
    return {schema:'dreamco.buddy_setup_plan.v1', created_at:now, storage:'browser_local_choices_only', choices:state,
      setup_status:'plan_prepared_not_production_verified', production_ready:false, authenticated_user_created:false, paid_calls_enabled:false,
      local_capabilities:['Prepare and download this setup plan', 'Browse available public catalogs', 'Use local model inference on a compatible device after explicit download'],
      server_required:['Private account connections and secret storage', 'Per-user accounts, permissions and shared durable storage', 'Real bot execution, workflow dispatch and external writes'],
      sources:state.sources.map(id => {const source=SOURCES.find(x=>x.id===id);return {id, name:source.name, status:'setup_required_not_verified_connected', connected:false, setup_url:source.setup, buddy_page:source.page, steps:source.steps, evidence_required:source.proof};}),
      model_test:state.modelRecord || {status:'not_tested'}, training_status:'no_training_performed', acknowledgements_are_not_evidence:true,
      next_steps:next};
  }
  const api = {KEY, STEPS, OPTIONS, SOURCES, CHECKS, sanitize, readModelRecord, buildPlan};
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  root.BuddySetupGuide = api;
  if (typeof document === 'undefined') return;
  const $ = id => document.getElementById(id);
  const node = (tag, text) => { const n=document.createElement(tag); if (text !== undefined) n.textContent=text; return n; };
  let state, storageAvailable=true;
  try { state=sanitize(JSON.parse(localStorage.getItem(KEY) || '{}')); } catch (_) { state=sanitize({}); storageAvailable=false; }
  function save() { try { localStorage.setItem(KEY,JSON.stringify(state)); storageAvailable=true; } catch (_) { storageAvailable=false; } storageNotice(); }
  function storageNotice() { $('sg-storage').textContent=storageAvailable?'Choices are saved only in this browser.':'Browser storage is unavailable. You can still use the guide and download your plan.'; }
  function link(text, href) { const a=node('a',text); a.href=href; if (href.startsWith('https://')) { a.target='_blank'; a.rel='noopener noreferrer'; } return a; }
  function options(key, title) { const field=node('fieldset'); field.append(node('legend',title)); for (const [id,title,detail] of OPTIONS[key]) { const item=node('label');item.className='sg-choice';const input=node('input');input.type='radio';input.name=key;input.value=id;input.checked=state[key]===id;input.addEventListener('change',()=>{state[key]=id;save();});const text=node('span');text.append(node('strong',title),node('small',detail));item.append(input,text);field.append(item); } return field; }
  function list(items) { const ol=node('ol');items.forEach(text=>ol.append(node('li',text)));return ol; }
  function render(focus=false) {
    $('sg-step-nav').replaceChildren(); STEPS.forEach((title,i)=>{const button=node('button',`${i+1}. ${title}`);button.type='button';if(i===state.step)button.setAttribute('aria-current','step');button.onclick=()=>{state.step=i;save();render(true);};$('sg-step-nav').append(button);});
    $('sg-title').textContent=STEPS[state.step];$('sg-position').textContent=`Step ${state.step+1} of ${STEPS.length}`;
    const content=$('sg-content');content.replaceChildren();
    if(state.step===0) content.append(options('goal','What do you want Buddy to help with first?'),options('audience','Who will use this setup?'));
    if(state.step===1) content.append(options('device','Which device will you start on?'),options('privacy','How should you start using information?'),link('Review data controls','data-control.html'));
    if(state.step===2) {content.append(options('budget','How should this plan handle paid services?'),node('p','This guide never calls a paid model, starts a subscription or changes a provider account. Free access and device capacity vary; check a provider’s current limits before using it.'),node('p','Browser tools can prepare plans and run a supported small model. Production accounts, private connectors, scheduled jobs and isolated client workspaces need separately configured infrastructure.'));}
    if(state.step===3) {content.append(node('p','Select the sources you want to set up. Every selected source stays “setup required” until a real connection is tested outside this guide.'));for(const source of SOURCES){const section=node('section');section.className='sg-source';const choice=node('label');choice.className='sg-choice';const input=node('input');input.type='checkbox';input.value=source.id;input.checked=state.sources.includes(source.id);input.onchange=()=>{state.sources=input.checked?[...state.sources,source.id]:state.sources.filter(x=>x!==source.id);state=sanitize(state);save();};choice.append(input,node('strong',source.name));section.append(choice,node('p',source.boundary),list(source.steps),node('p','Evidence needed: '+source.proof));const links=node('p');links.className='sg-links';links.append(link('Open official setup or source',source.setup),link('Open Buddy workspace',source.page));section.append(links);content.append(section);}}
    if(state.step===4) {content.append(node('p','Run a short prompt in the local model lab, then download its JSON test record. This tests inference on your device. It does not train a model or prove answer quality.'),link('Open local model lab','buddy-model-lab.html'));const labelNode=node('label','Optionally select the downloaded JSON test record');labelNode.htmlFor='sg-model-record';const input=node('input');input.type='file';input.id='sg-model-record';input.accept='.json,application/json';const status=node('p',state.modelRecord?'Test record retained as unverified metadata. No prompt or answer is saved here.':'Model not tested in this guide.');status.id='sg-model-status';status.setAttribute('role','status');input.onchange=async()=>{try{const file=input.files?.[0];if(!file)return;if(file.size>100000)throw Error('Select a JSON test record smaller than 100 KB.');state.modelRecord=readModelRecord(JSON.parse(await file.text()));save();status.textContent='Imported model, revision, date and duration only. Prompts and answers were discarded. This editable record is not independent proof of quality or readiness.';}catch(error){status.textContent=error.message;}};const clear=node('button','Remove model-test metadata');clear.type='button';clear.className='btn btn-outline';clear.onclick=()=>{state.modelRecord=null;input.value='';save();status.textContent='Model-test metadata removed. Model remains unverified.';};content.append(labelNode,input,status,clear,node('p','An imported file can be edited, so it is treated as a reported test. Keep the original result and have its behavior reviewed. If your device cannot run the model, leave this step untested and continue planning.'));}
    if(state.step===5) {const plan=buildPlan(state);const status=node('p','Plan prepared — production not verified');status.className='sg-status';content.append(status);const summary=node('dl');summary.className='sg-summary';for(const key of ['goal','audience','device','privacy','budget'])summary.append(node('dt',key.charAt(0).toUpperCase()+key.slice(1)),node('dd',label(key,state[key])));summary.append(node('dt','Sources'),node('dd',plan.sources.length?plan.sources.map(x=>x.name).join(', '):'None selected'),node('dt','Connections'),node('dd','No live connection verified by this guide'));content.append(summary,node('h3','Your next actions'),list(plan.next_steps),node('h3','Before calling this production ready'));for(const [id,text] of CHECKS){const labelNode=node('label');labelNode.className='sg-choice';const input=node('input');input.type='checkbox';input.checked=state.checks[id];input.onchange=()=>{state.checks[id]=input.checked;save();};labelNode.append(input,node('span',text));content.append(labelNode);}content.append(node('p','These acknowledgements record your review only. They cannot mark a service connected, a model trained, a bot running or a deployment verified.'),link('Open test and benchmark center','test-center.html'));}
    $('sg-back').disabled=state.step===0;$('sg-next').disabled=state.step===STEPS.length-1;storageNotice();if(focus)$('sg-title').focus();
  }
  $('sg-back').onclick=()=>{if(state.step>0){state.step--;save();render(true);}};
  $('sg-next').onclick=()=>{if(state.step<STEPS.length-1){state.step++;save();render(true);}};
  $('sg-export').onclick=()=>{const url=URL.createObjectURL(new Blob([JSON.stringify(buildPlan(state),null,2)],{type:'application/json'}));const a=node('a');a.href=url;a.download='buddy-setup-plan.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);$('sg-feedback').textContent='Setup plan prepared for download. It contains choices and setup steps, never credentials. No service was connected.';};
  $('sg-reset').onclick=()=>{state=sanitize({});try{localStorage.removeItem(KEY);storageAvailable=true;}catch(_){storageAvailable=false;}$('sg-feedback').textContent='Setup choices cleared for this guide. Other Buddy data is unchanged.';render(true);};
  render();
})(typeof globalThis !== 'undefined' ? globalThis : this);
