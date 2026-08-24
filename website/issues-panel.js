(function () {
  'use strict';

  const REPOSITORY = 'DreamCo-Technologies/Dreamcobots';
  const API = `https://api.github.com/repos/${REPOSITORY}/issues?state=all&per_page=100&sort=updated&direction=desc`;

  const style = document.createElement('style');
  style.textContent = `
    .issues-panel{margin-top:24px;padding:24px;border:1px solid var(--border);border-radius:18px;background:var(--card)}
    .issues-panel-head{display:flex;justify-content:space-between;gap:18px;align-items:flex-start;flex-wrap:wrap}
    .issues-panel-kicker{font-size:.72rem;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin:0 0 6px}
    .issues-panel h2{margin:0 0 6px}.issues-panel p{color:var(--text2)}
    .issues-panel-metrics{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin:18px 0}
    .issues-panel-metrics div{padding:12px;border:1px solid var(--border);border-radius:12px;background:var(--card2)}
    .issues-panel-metrics span{display:block;font-size:.72rem;color:var(--muted)}.issues-panel-metrics strong{font-size:1.25rem}
    .issues-panel-toolbar{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:14px}.issues-panel-toolbar input,.issues-panel-toolbar select{min-width:180px;padding:9px;border:1px solid var(--border);border-radius:9px;background:var(--card);color:var(--text)}
    .issue-card{padding:15px;border:1px solid var(--border);border-radius:13px;margin:10px 0;background:var(--card2)}
    .issue-card-head{display:flex;justify-content:space-between;gap:12px}.issue-card h3{margin:0;font-size:1rem}.issue-meta{font-size:.78rem;color:var(--muted);margin:6px 0}.issue-stage{display:inline-block;padding:3px 7px;border-radius:999px;border:1px solid var(--border);font-size:.7rem;margin-right:6px}.issue-open{color:#ffb86b}.issue-closed{color:#86efac}.issue-actions{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px}.issue-actions a{font-size:.78rem}.issues-empty{padding:18px;border:1px dashed var(--border);border-radius:12px;color:var(--muted)}
    @media(max-width:760px){.issues-panel-metrics{grid-template-columns:repeat(2,minmax(0,1fr))}}
  `;
  document.head.appendChild(style);

  const shell = document.querySelector('.actions-shell');
  if (!shell) return;

  const panel = document.createElement('section');
  panel.className = 'issues-panel';
  panel.setAttribute('aria-labelledby', 'issues-panel-heading');
  panel.innerHTML = `
    <div class="issues-panel-head">
      <div><p class="issues-panel-kicker">Issue operations</p><h2 id="issues-panel-heading">Repair queue & issue intelligence</h2><p>One view for recurring Actions failures, repair work, verification, and resolved history. Repeated runs are grouped by workflow/root cause instead of creating a new repair item every time.</p></div>
      <div class="issue-actions"><a class="btn btn-primary" target="_blank" rel="noopener" href="https://github.com/DreamCo-Technologies/Dreamcobots/issues">Open GitHub Issues</a><button class="btn btn-outline" id="issues-refresh" type="button">Refresh issues</button></div>
    </div>
    <div class="issues-panel-metrics"><div><span>Open issues</span><strong id="issues-open">—</strong></div><div><span>Failure issues</span><strong id="issues-failures">—</strong></div><div><span>Repair queue</span><strong id="issues-repair">—</strong></div><div><span>Resolved</span><strong id="issues-resolved">—</strong></div></div>
    <div class="issues-panel-toolbar"><input id="issues-search" type="search" placeholder="Search issue, workflow, root cause"/><select id="issues-state"><option value="open">Open</option><option value="closed">Closed</option><option value="all">All</option></select><select id="issues-kind"><option value="all">All issue types</option><option value="actions">Actions failures</option><option value="repair">Repair backlog</option><option value="other">Other</option></select></div>
    <div id="issues-list" class="workflow-list"><div class="issues-empty">Loading issue evidence…</div></div>
  `;

  const evidence = document.querySelector('.actions-evidence');
  shell.insertBefore(panel, evidence || shell.firstElementChild);

  const state = { issues: [], filtered: [] };
  const el = (id) => document.getElementById(id);
  const normalize = (value) => String(value || '').toLowerCase();

  function kind(issue) {
    const text = normalize(`${issue.title} ${issue.body}`);
    if (text.includes('actions run') || text.includes('github actions')) return 'actions';
    if (text.includes('repair') || text.includes('blocker') || text.includes('failed')) return 'repair';
    return 'other';
  }

  function stage(issue) {
    if (issue.state === 'closed') return 'Resolved';
    const text = normalize(issue.body);
    if (text.includes('verification passed') || text.includes('verified')) return 'Verification';
    if (text.includes('repairing') || text.includes('in progress')) return 'Repairing';
    if (text.includes('reproduced') || text.includes('root cause')) return 'Reproduced / triage';
    return 'Detected';
  }

  function rootCause(issue) {
    const title = String(issue.title || '');
    const runMatch = title.match(/^Actions run \d+ failed:\s*/i);
    return (runMatch ? title.replace(runMatch[0], '') : title).trim();
  }

  function render() {
    const query = normalize(el('issues-search').value.trim());
    const stateFilter = el('issues-state').value;
    const kindFilter = el('issues-kind').value;
    const filtered = state.issues.filter((issue) => {
      const haystack = normalize(`${issue.title} ${issue.body} ${rootCause(issue)}`);
      return (!query || haystack.includes(query)) && (stateFilter === 'all' || issue.state === stateFilter) && (kindFilter === 'all' || kind(issue) === kindFilter);
    });
    state.filtered = filtered;

    const list = el('issues-list');
    list.replaceChildren();
    if (!filtered.length) {
      list.append(Object.assign(document.createElement('div'), { className: 'issues-empty', textContent: 'No issues match this queue.' }));
      return;
    }

    filtered.slice(0, 60).forEach((issue) => {
      const card = document.createElement('article');
      card.className = 'issue-card';
      const head = document.createElement('div'); head.className = 'issue-card-head';
      const title = document.createElement('h3'); title.textContent = `#${issue.number} ${rootCause(issue)}`;
      const status = document.createElement('span'); status.className = `issue-stage ${issue.state === 'open' ? 'issue-open' : 'issue-closed'}`; status.textContent = stage(issue);
      head.append(title, status);
      const meta = document.createElement('div'); meta.className = 'issue-meta'; meta.textContent = `${kind(issue)} · updated ${new Date(issue.updated_at).toLocaleString()} · ${issue.comments || 0} comments`;
      const actions = document.createElement('div'); actions.className = 'issue-actions';
      const github = document.createElement('a'); github.className = 'btn btn-outline'; github.target = '_blank'; github.rel = 'noopener'; github.href = issue.html_url; github.textContent = 'Open issue';
      const buddy = document.createElement('a'); buddy.className = 'btn btn-primary'; buddy.href = `buddy.html?prompt=${encodeURIComponent(`Debug GitHub issue #${issue.number} in ${REPOSITORY}. Root cause candidate: ${rootCause(issue)}. Evidence: ${issue.html_url}. Reproduce first, make the smallest safe repair, run the focused test, then run dependent regression checks. Do not claim resolved without evidence.`)}`; buddy.textContent = 'Plan with Buddy';
      actions.append(github, buddy);
      card.append(head, meta, actions);
      list.append(card);
    });
  }

  async function refresh() {
    const button = el('issues-refresh'); button.disabled = true; button.textContent = 'Refreshing…';
    try {
      const response = await fetch(API, { headers: { Accept: 'application/vnd.github+json' } });
      if (!response.ok) throw new Error(`GitHub returned ${response.status}`);
      state.issues = await response.json();
      const open = state.issues.filter((x) => x.state === 'open');
      const actions = state.issues.filter((x) => kind(x) === 'actions' && x.state === 'open');
      const repair = state.issues.filter((x) => kind(x) === 'repair' && x.state === 'open');
      const resolved = state.issues.filter((x) => x.state === 'closed');
      el('issues-open').textContent = String(open.length);
      el('issues-failures').textContent = String(actions.length);
      el('issues-repair').textContent = String(repair.length);
      el('issues-resolved').textContent = String(resolved.length);
      render();
    } catch (error) {
      el('issues-list').replaceChildren(Object.assign(document.createElement('div'), { className: 'issues-empty', textContent: `Issue feed unavailable: ${error.message}. Open GitHub Issues directly to inspect the live queue.` }));
    } finally { button.disabled = false; button.textContent = 'Refresh issues'; }
  }

  ['issues-search','issues-state','issues-kind'].forEach((id) => el(id).addEventListener(id === 'issues-search' ? 'input' : 'change', render));
  el('issues-refresh').addEventListener('click', refresh);
  refresh();
})();
