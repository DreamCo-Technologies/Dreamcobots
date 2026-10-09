/* Public evidence is read-only. Reviews require the separate loopback reviewer session. */
(() => {
  'use strict';
  const byId = id => document.getElementById(id);
  const text = (id, value) => { byId(id).textContent = value; };
  const node = (tag, value) => { const el = document.createElement(tag); el.textContent = value; return el; };
  const empty = 'Untested — no validated runtime evidence submitted.';
  const params = new URLSearchParams(location.hash.slice(1));
  let reviewerToken = params.get('review-token');
  if (reviewerToken) history.replaceState(null, '', location.pathname + location.search);
  const local = location.protocol === 'http:' && ['127.0.0.1', 'localhost'].includes(location.hostname);
  if (!local) reviewerToken = null;
  let evidence;
  let privateReviews = [];
  function cards(id, rows, render, fallback = empty) {
    const target = byId(id); target.replaceChildren();
    if (!rows.length) { target.append(node('p', fallback)); return; }
    rows.forEach(row => { const card = node('article', ''); card.className = 'gi-card'; render(card, row); target.append(card); });
  }
  function renderMatrix() {
    const query = byId('gi-filter').value.toLowerCase();
    const table = byId('gi-matrix'); table.replaceChildren();
    evidence.matrix.filter(c => c.title.toLowerCase().includes(query)).forEach(c => {
      const row = document.createElement('tr');
      const reviewed = c.status === 'verified' && evidence.runs.some(r => r.capability === c.id && r.status === 'verified' && privateReviews.some(review => ['approved','verified'].includes(review.status) && review.parameters.run_id === r.id && review.parameters.run_hash === r.hash));
      [c.title, reviewed ? 'reviewed (local human signoff)' : c.status, reviewed ? 'Scoped evidence reviewed; no AGI claim' : c.gap].forEach(value => row.append(node('td', value)));
      table.append(row);
    });
  }
  async function api(path, payload) {
    if (!local || !reviewerToken) throw new Error('Authenticated local review session required');
    const res = await fetch('/api/local/evaluation/' + path, {
      method: payload ? 'POST' : 'GET', cache: 'no-store', credentials: 'omit',
      headers: { 'Authorization': 'Bearer ' + reviewerToken, ...(payload ? {'Content-Type': 'application/json'} : {}) },
      ...(payload ? {body: JSON.stringify(payload)} : {})
    });
    const result = await res.json();
    if (!res.ok) throw new Error(result.error || 'Review rejected');
    return result;
  }
  async function refresh() {
    byId('gi-refresh').disabled = true;
    try {
      const result = await api('queue');
      privateReviews = result.evidence_reviews || [];
      if (evidence) renderMatrix();
      if (result.horizons?.length) text('gi-horizon', JSON.stringify(result.horizons, null, 2));
      if (result.promotions?.length) cards('gi-promotions', result.promotions, (c,r) => c.append(node('h3', r.action.title + ' · ' + r.status), node('pre', JSON.stringify(r.receipt, null, 2))));
      if (result.interventions) text('gi-interventions', 'Local completed actions: ' + result.interventions.count + '; human-reviewed fraction: ' + (result.interventions.rate ?? 'unknown') + '. This is not a model benchmark score.');
      text('gi-review-status', 'Private local queue · reviewer: ' + result.reviewer + '. Approval authorizes one scoped action; it does not execute it.');
      cards('gi-queue', result.actions, (card, row) => {
        card.append(node('h3', row.action.title), node('p', row.status + ' · ' + row.autonomy + ' · ' + row.action.risk));
        const preview = node('pre', JSON.stringify(row.action, null, 2)); card.append(preview);
        const noteLabel = node('label', 'Review note'); const note = node('textarea', ''); note.rows = 2; noteLabel.append(note); card.append(noteLabel);
        const details = node('details', ''); details.append(node('summary', 'Edit proposal (requires fresh approval)'));
        const edit = node('textarea', JSON.stringify(row.action, null, 2)); edit.setAttribute('aria-label', 'Edited action proposal'); details.append(edit); card.append(details);
        const message = node('p', ''); message.setAttribute('role', 'status');
        const pending = ['pending', 'escalated', 'approved'].includes(row.status);
        for (const decision of ['approve', 'reject', 'edit', 'escalate']) {
          const button = node('button', decision[0].toUpperCase() + decision.slice(1)); button.disabled = !pending;
          button.addEventListener('click', async () => {
            card.querySelectorAll('button').forEach(b => { b.disabled = true; });
            try {
              await api('decide', {id: row.id, revision: row.revision, decision, note: note.value, ...(decision === 'edit' ? {edited: JSON.parse(edit.value)} : {})});
              await refresh();
            } catch (error) { message.textContent = error.message; card.querySelectorAll('button').forEach(b => { b.disabled = !pending; }); }
          }); card.append(button);
        }
        if (row.receipt) card.append(node('pre', 'Post-action verification: ' + JSON.stringify(row.receipt, null, 2)));
        card.append(message);
      }, 'No requests in this local queue.');
      cards('gi-audit', result.audit, (card, row) => card.append(node('p', row.kind + ' · ' + row.action_id), node('pre', JSON.stringify(row.details, null, 2))));
    } catch (error) { text('gi-review-status', error.message + '. Actions remain blocked.'); byId('gi-queue').replaceChildren(); }
    finally { byId('gi-refresh').disabled = !local || !reviewerToken; }
  }
  byId('gi-refresh').addEventListener('click', refresh);
  byId('gi-filter').addEventListener('input', () => { if (evidence) renderMatrix(); });
  fetch('data/general-intelligence.json', {cache:'no-store'}).then(r => { if (!r.ok) throw new Error('Evidence unavailable'); return r.json(); }).then(data => {
    if (data.schema !== 'dreamco.general_intelligence_public.v1' || data.automatic_agi_claim !== false || data.automatic_frontier_claim !== false || !Array.isArray(data.matrix)) throw new Error('Evidence contract invalid');
    evidence = data;
    text('gi-status', data.status + ' · ' + data.matrix.length + ' capability areas · ' + data.runs.length + ' submitted runs');
    for (const section of data.sections) { const link = node('a', section.title); link.href = '#' + section.id; byId('gi-sections').append(link); }
    renderMatrix();
    cards('gi-benchmarks', data.public_benchmarks, (card, b) => {
      card.append(node('h3', b.id), node('p', b.enabled ? 'Configured; results still required' : 'Blocked: ' + b.blocker));
      const a = node('a', 'Official source'); const u = new URL(b.url); if (u.protocol === 'https:') { a.href = u.href; a.rel = 'noopener noreferrer'; card.append(a); }
    });
    text('gi-autonomy', Object.entries(data.autonomy).map(([level, allowed]) => level + ': automatic low-risk, reversible, zero-cost ' + allowed.join(', ')).join('. ') + '. All other actions require fresh approval.');
    text('gi-red-team', data.red_team_categories.join(' · ') + '. Per-model results: ' + (data.runs.length ? 'see evidence ledger' : 'untested'));
    if (data.runs.length) {
      text('gi-transfer', data.runs.map(r => r.id + ': ' + r.transfer.cases + ' transfer attempts · ' + r.transfer.status).join('; '));
      text('gi-red-team', data.runs.map(r => r.id + ': ' + Object.entries(r.red_team).map(([k,v]) => k + '=' + (v === true ? 'reported pass; see evidence status' : v === false ? 'failed' : 'untested')).join(', ')).join('; '));
    }
    cards('gi-calibration', data.runs, (c,r) => c.append(node('p', r.id), node('pre', JSON.stringify(r.calibration, null, 2))));
    cards('gi-interventions', data.runs, (c,r) => c.append(node('p', r.id + ': ' + (r.metrics?.human_intervention_rate ?? 'unknown'))));
    cards('gi-lessons', data.lessons, (c,r) => c.append(node('h3', r.source_run), node('pre', JSON.stringify(r, null, 2))));
    cards('gi-promotions', data.promotions, (c,r) => c.append(node('pre', JSON.stringify(r, null, 2))), 'No published promotions or rejections.');
    cards('gi-ledger', data.runs, (c,r) => c.append(node('h3', r.id + ' · ' + r.status), node('pre', JSON.stringify(r, null, 2))));
  }).catch(error => { text('gi-status', error.message + '. Fail-closed: no readiness claim.'); });
  if (local && reviewerToken) { byId('gi-refresh').disabled = false; refresh(); }
})();
