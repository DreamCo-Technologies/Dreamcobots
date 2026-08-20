(function () {
  'use strict';
  const REPOSITORY = 'DreamCo-Technologies/Dreamcobots';
  const REPORT_URL = 'data/actions-health-report.json';
  const PROSPECTUS_URL = 'data/actions-prospectus.json';
  const benchmarkIndex = window.BUDDY_BENCHMARK_INDEX || { programs: [], summary: {} };
  const state = { report: null, prospectus: null, runs: new Map() };
  const byId = (id) => document.getElementById(id);
  const readable = (value) => String(value || '').replaceAll('_', ' ');
  const make = (tag, text, className) => { const node = document.createElement(tag); if (text !== undefined) node.textContent = text; if (className) node.className = className; return node; };
  function ensureShell() {
    const main = document.querySelector('main') || document.body;
    if (!byId('actions-control-cards')) {
      const section = make('section', undefined, 'actions-workspace actions-command-center');
      section.innerHTML = `<div class="actions-workspace-heading"><div><p class="actions-kicker">Command center</p><h2>Find, understand and improve anything</h2></div><p id="prospectus-status">Loading control registry...</p></div><div class="actions-filter-bar"><input id="actions-search" type="search" placeholder="Search workflows, goals, benchmarks or capabilities" aria-label="Search actions"><select id="actions-status-filter" aria-label="Filter by status"><option value="all">All statuses</option><option value="attention">Needs attention</option><option value="running">Running</option><option value="unknown">Unknown</option><option value="passing">Passing</option></select><select id="actions-trigger-filter" aria-label="Filter by trigger"><option value="all">All triggers</option></select></div><div id="actions-control-cards" class="actions-control-grid"></div></section>`;
      const evidence = document.querySelector('.actions-evidence');
      main.insertBefore(section, evidence || main.firstChild);
    }
    if (!byId('workflow-detail')) {
      const dialog = document.createElement('dialog');
      dialog.id = 'workflow-detail'; dialog.className = 'workflow-detail-dialog';
      dialog.innerHTML = `<div class="workflow-detail-head"><div><p class="actions-kicker">Action prospectus</p><h2 id="detail-title">Workflow</h2><code id="detail-path"></code></div><button id="close-workflow-detail" class="btn btn-outline" type="button">Close</button></div><div id="workflow-detail-body"></div><div class="workflow-detail-actions"><a id="detail-github-link" class="btn btn-outline" target="_blank" rel="noopener">Open GitHub evidence</a><a id="detail-buddy-link" class="btn btn-primary">Plan with Buddy</a></div>`;
      document.body.appendChild(dialog);
    }
    for (const [id, text] of [['metric-workflows','0'],['metric-static','0'],['metric-passing','0'],['metric-attention','0'],['metric-upgrades','0'],['metric-benchmarks','0']]) {
      if (!byId(id)) { const el = make('span', text); el.id = id; el.hidden = true; document.body.appendChild(el); }
    }
    for (const id of ['actions-search','actions-status-filter','actions-trigger-filter','refresh-actions','close-workflow-detail']) {
      if (!byId(id)) console.warn(`Actions page missing expected control: ${id}`);
    }
  }
  function latestEvidence(workflow) {
    const run = state.runs.get(workflow.workflow) || state.runs.get(workflow.path);
    if (!run) return { key: 'unknown', label: 'Not loaded', run: null };
    if (run.status === 'in_progress' || run.status === 'queued') return { key: 'running', label: readable(run.status), run };
    if (run.conclusion === 'success') return { key: 'passing', label: 'Passing', run };
    if (['failure','cancelled','timed_out','action_required','startup_failure','stale'].includes(run.conclusion)) return { key: 'attention', label: readable(run.conclusion), run };
    return { key: 'unknown', label: readable(run.conclusion || run.status || 'unknown'), run };
  }
  function prospectusFor(id) { return state.prospectus?.controls?.find(item => item.id === id) || null; }
  function benchmarkPrograms(workflow) { return (benchmarkIndex.programs || []).filter(program => (workflow.npm_scripts || []).some(script => program.check_command?.includes(`npm run ${script}`))); }
  function buddyUpgradeUrl(workflow, evidence) {
    const p = prospectusFor('repair');
    const upgrades = (workflow.upgrades || []).map((item, index) => `${index + 1}. ${item}`).join('\n');
    const runState = evidence.run ? `${evidence.label}; run ${evidence.run.id}; commit ${String(evidence.run.head_sha || '').slice(0,12) || 'unknown'}` : 'No public live run was loaded.';
    const prompt = `Debug and upgrade ${workflow.workflow}. Purpose: ${workflow.purpose}. Evidence: ${runState}. Static findings: ${(workflow.errors || []).length} errors, ${(workflow.warnings || []).length} warnings. Repository upgrades:\n${upgrades}\nRepair policy: ${p?.truth_boundary || 'reproduce first; smallest safe repair; targeted test; dependent regression; never fabricate evidence.'}`;
    return `buddy.html?prompt=${encodeURIComponent(prompt)}`;
  }
  function renderProspectusCards() {
    const host = byId('actions-control-cards'); if (!host) return;
    host.replaceChildren();
    const controls = state.prospectus?.controls || [];
    controls.forEach(control => {
      const card = make('article', undefined, 'actions-control-card');
      card.append(make('p', control.category || 'control', 'actions-kicker'), make('h3', control.name), make('p', control.purpose));
      const grid = make('div', undefined, 'prospectus-meta');
      [['Progress', control.progress || 'configured'], ['Planning horizon', control.planning_horizon || 'Re-estimate from evidence'], ['Investor value', control.investor_value || 'Operational value']].forEach(([k,v]) => { const item=make('div'); item.append(make('span',k),make('strong',v)); grid.append(item); });
      card.append(grid);
      const details = make('details'); details.append(make('summary','View upgrade plan + evidence rules'));
      const plan = make('ol'); (control.upgrade_plan || []).forEach(step => { const li=make('li'); li.append(make('strong',step.step),make('span',` — ${step.estimate}`)); plan.append(li); });
      details.append(make('h4','Upgrade plan'),plan,make('h4','Evidence'));
      const evidenceList=make('ul'); (control.evidence || []).forEach(item => evidenceList.append(make('li',item))); details.append(evidenceList,make('h4','Success'),make('p',control.success||''),make('h4','Fallback'),make('p',control.fallback||''));
      card.append(details); host.append(card);
    });
    const status=byId('prospectus-status'); if(status) status.textContent=`${controls.length} controls documented with evidence and upgrade plans.`;
  }
  function showDetail(workflow) {
    const evidence=latestEvidence(workflow), programs=benchmarkPrograms(workflow), repair=prospectusFor('repair');
    byId('detail-path').textContent=workflow.workflow; byId('detail-title').textContent=workflow.display_name; byId('detail-github-link').href=evidence.run?.html_url||workflow.github_url; byId('detail-buddy-link').href=buddyUpgradeUrl(workflow,evidence);
    const body=byId('workflow-detail-body'); body.replaceChildren();
    const summary=make('div',undefined,'detail-summary');
    [['Static status',readable(workflow.static_status)],['Latest run',evidence.label],['Runner jobs',String(workflow.controls?.runner_jobs ?? 'unknown')],['Timeouts',String(workflow.controls?.job_timeouts_declared ?? 'unknown')],['Artifacts',workflow.controls?.artifacts_declared?'Declared':'Not declared'],['Concurrency',workflow.controls?.concurrency_declared?'Declared':'Not declared']].forEach(([label,value])=>{const item=make('div');item.append(make('span',label),make('strong',value));summary.append(item);});
    body.append(summary,make('h3','What this action protects'),make('p',workflow.purpose));
    const upgrades=make('ol');(workflow.upgrades||[]).forEach(item=>upgrades.append(make('li',item)));body.append(make('h3','Repository upgrade plan'),upgrades);
    if(repair){body.append(make('h3','Repair planning timeframe'),make('p',repair.planning_horizon||'Re-estimated after reproduction'));const plan=make('ol');(repair.upgrade_plan||[]).forEach(item=>{const li=make('li');li.append(make('strong',item.step),make('span',` — ${item.estimate}`));plan.append(li);});body.append(plan);}
    body.append(make('h3','Repository evidence'));const evidenceList=make('div',undefined,'detail-code-list');[...(workflow.npm_scripts||[]).map(s=>`npm run ${s}`),...(workflow.referenced_files||[]),...(workflow.actions||[])].forEach(item=>evidenceList.append(make('code',item)));body.append(evidenceList);
    body.append(make('h3','Connected benchmark programs'));const list=make('ul',undefined,'detail-benchmark-list');if(programs.length)programs.forEach(program=>{const item=make('li');const link=make('a',program.name);link.href=program.public_page;item.append(link,document.createTextNode(`: ${readable(program.status)}`));list.append(item);});else list.append(make('li','Tracked by Actions health; no dedicated benchmark program mapped yet.'));body.append(list);byId('workflow-detail').showModal();
  }
  function render() {
    if(!state.report) return;
    const search=byId('actions-search')?.value.trim().toLowerCase()||'', status=byId('actions-status-filter')?.value||'all', trigger=byId('actions-trigger-filter')?.value||'all';
    const workflows=state.report.findings.map(workflow=>({workflow,evidence:latestEvidence(workflow)})).filter(({workflow,evidence})=>{const text=`${workflow.display_name} ${workflow.purpose} ${workflow.workflow} ${(workflow.npm_scripts||[]).join(' ')} ${(workflow.upgrades||[]).join(' ')}`.toLowerCase();return(!search||text.includes(search))&&(status==='all'||evidence.key===status)&&(trigger==='all'||(workflow.triggers||[]).includes(trigger));}).sort((a,b)=>({attention:0,running:1,unknown:2,passing:3}[a.evidence.key]-({attention:0,running:1,unknown:2,passing:3}[b.evidence.key])||a.workflow.display_name.localeCompare(b.workflow.display_name));
    const list=byId('workflow-list'); if(!list)return; list.replaceChildren();
    workflows.forEach(({workflow,evidence})=>{const item=make('article',undefined,'workflow-item');const row=make('div',undefined,'workflow-row');const identity=make('div',undefined,'workflow-name');identity.append(make('strong',workflow.display_name),make('p',workflow.purpose));row.append(identity);const addCell=(label,value,statusClass)=>{const cell=make('div',undefined,'workflow-cell');cell.append(make('span',label),make('strong',value,statusClass?`workflow-status ${statusClass}`:undefined));row.append(cell);};addCell('Static evidence',readable(workflow.static_status),workflow.static_status==='static_checks_passed'?'passing':'attention');addCell('Latest run',evidence.label,evidence.key);addCell('Controls',`${workflow.controls?.job_timeouts_declared ?? 0} timeout · ${workflow.controls?.artifacts_declared?'artifacts':'no artifact'}`);const commands=make('div',undefined,'workflow-commands');const inspect=make('button','Prospectus','btn btn-outline');inspect.type='button';inspect.addEventListener('click',()=>showDetail(workflow));const github=make('a',evidence.run?'Open run':'Open workflow','btn btn-outline');github.href=evidence.run?.html_url||workflow.github_url;github.target='_blank';github.rel='noopener';const buddy=make('a','Plan with Buddy','btn btn-primary');buddy.href=buddyUpgradeUrl(workflow,evidence);commands.append(inspect,github,buddy);row.append(commands);item.append(row);const upgrades=make('details',undefined,'workflow-upgrades');upgrades.append(make('summary',`${(workflow.upgrades||[]).length} repository upgrade steps`));const plan=make('ol');(workflow.upgrades||[]).forEach(upgrade=>plan.append(make('li',upgrade)));upgrades.append(plan);item.append(upgrades);list.append(item);});
    if(!workflows.length)list.append(make('p','No workflows match these filters.','actions-empty'));
    const allEvidence=state.report.findings.map(latestEvidence); const set=(id,value)=>{const el=byId(id);if(el)el.textContent=String(value);};set('metric-workflows',state.report.workflow_count);set('metric-static',`${state.report.workflow_count-state.report.critical_error_count}/${state.report.workflow_count}`);set('metric-passing',allEvidence.filter(i=>i.key==='passing').length);set('metric-attention',allEvidence.filter(i=>i.key==='attention').length+state.report.critical_error_count);set('metric-upgrades',state.report.findings.reduce((sum,w)=>sum+(w.upgrades||[]).length,0));set('metric-benchmarks',benchmarkIndex.summary?.trackedBenchmarkSurfaces||0);const count=byId('workflow-result-count');if(count)count.textContent=`${workflows.length} of ${state.report.workflow_count} workflows shown`;
  }
  async function refreshRuns(){const button=byId('refresh-actions');if(!button)return;button.disabled=true;button.textContent='Refreshing...';const status=byId('actions-refresh-status');if(status)status.textContent='Reading public GitHub run evidence...';try{const response=await fetch(`https://api.github.com/repos/${REPOSITORY}/actions/runs?per_page=100`,{headers:{Accept:'application/vnd.github+json'}});if(!response.ok)throw new Error(`GitHub returned ${response.status}`);const payload=await response.json();state.runs.clear();(payload.workflow_runs||[]).forEach(run=>{const key=run.path||run.workflow_id;if(key&&!state.runs.has(key))state.runs.set(key,run);});const seen=state.report.findings.filter(w=>latestEvidence(w).run).length;if(status)status.textContent=`Public run evidence loaded for ${seen} workflows. Observed evidence is not a guarantee of future success.`;}catch(error){if(status)status.textContent=`Static evidence is available. Public run refresh unavailable: ${error.message}`;}finally{button.disabled=false;button.textContent='Refresh GitHub Runs';render();}}
  const LOCAL_COMMANDS={doctor:['Doctor','Check repository structure, runtime bindings, dependencies, and common configuration problems.'],test:['Tests','Run repository tests and preserve the first failing test.'],lint:['Lint','Run formatting, lint, imports, and types without modifying source.'],security:['Security','Run dependency and secret-boundary checks without exposing credentials.'],benchmark:['Local benchmark','Measure quality, latency, throughput, efficiency, and reliability on the current device.'],repair:['Repair planner','Turn observed failures into a smallest-safe repair plan with rollback and regression tests.'],pages:['Pages verification','Verify repository evidence and generated data are present in the public dashboard.'],bundle:['Device bundle','Validate downloadable launcher/package and local build artifacts.']};
  function setupLocalCommands(){document.querySelectorAll('[data-local-command]').forEach(button=>button.addEventListener('click',()=>{const [label,description]=LOCAL_COMMANDS[button.dataset.localCommand]||['Action','No description available.'];const output=byId('actions-command-output');if(output)output.textContent=`${label}\n\n${description}\n\nSafe boundary: browser actions do not execute arbitrary shell commands. Use the downloadable Buddy launcher for approved local execution or open the GitHub workflow for remote execution.\n\nNext: evidence → root cause → smallest repair → targeted test → dependent regression.`;}));}
  async function initialize(){ensureShell();try{const [reportResponse,prospectusResponse]=await Promise.all([fetch(REPORT_URL),fetch(PROSPECTUS_URL)]);if(!reportResponse.ok)throw new Error(`Actions catalog returned ${reportResponse.status}`);state.report=await reportResponse.json();if(prospectusResponse.ok)state.prospectus=await prospectusResponse.json();renderProspectusCards();const triggerFilter=byId('actions-trigger-filter');if(triggerFilter){[...new Set(state.report.findings.flatMap(w=>w.triggers||[]))].sort().forEach(trigger=>{const option=document.createElement('option');option.value=trigger;option.textContent=trigger;triggerFilter.append(option);});}render();setupLocalCommands();await refreshRuns();}catch(error){const status=byId('actions-refresh-status');if(status)status.textContent=`Actions catalog could not load: ${error.message}`;const list=byId('workflow-list');if(list)list.append(make('p','Run the repository Actions health generator before opening this page.','actions-empty'));setupLocalCommands();}}
  ensureShell();
  byId('actions-search')?.addEventListener('input',render);byId('actions-status-filter')?.addEventListener('change',render);byId('actions-trigger-filter')?.addEventListener('change',render);byId('refresh-actions')?.addEventListener('click',refreshRuns);byId('close-workflow-detail')?.addEventListener('click',()=>byId('workflow-detail')?.close());byId('workflow-detail')?.addEventListener('click',event=>{if(event.target===byId('workflow-detail'))byId('workflow-detail').close();});
  initialize();
})();