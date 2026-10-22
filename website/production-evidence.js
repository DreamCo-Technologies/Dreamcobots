(() => {
  'use strict';
  const esc = (v) => String(v ?? '').replace(/[&<>"']/g, (c) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  let data;
  const renderRows = () => {
    const q = document.getElementById('division-filter').value.toLowerCase().trim();
    const rows = data.divisions.filter((d) => !q || `${d.name} ${d.tier} ${d.blockers.join(' ')}`.toLowerCase().includes(q));
    document.getElementById('division-rows').innerHTML = rows.map((d) => `<tr><td><strong>${esc(d.name)}</strong></td><td>${esc(d.tier)}</td><td>${d.profiles}</td><td><span class="pill ${d.production_ready?'pass':'fail'}">${esc(d.status)}</span></td><td>${d.blockers.map(esc).join(' · ') || 'None'}</td></tr>`).join('');
  };
  fetch('data/production-evidence-ledger.json', {cache:'no-store'}).then((r) => {if(!r.ok) throw new Error(`HTTP ${r.status}`); return r.json();}).then((payload) => {
    data = payload; const s = data.summary;
    const metrics = [['Real divisions',s.real_divisions],['Routable profiles',s.catalog_profiles.toLocaleString()],['Production ready',s.production_ready_divisions],['Trained weights',s.trained_weight_artifacts],['24h soak',s.soak_24h_verified?'Verified':'Not verified'],['Deployments',s.professional_deployments_verified]];
    document.getElementById('evidence-summary').innerHTML = metrics.map(([k,v]) => `<div class="metric"><span>${esc(k)}</span><strong>${esc(v)}</strong></div>`).join('');
    document.getElementById('global-gates').innerHTML = data.global_gates.map((g) => `<article class="gate"><b class="${g.passed?'pass':'fail'}">${g.passed?'PASS':'EVIDENCE REQUIRED'}</b><h3>${esc(g.id.replaceAll('_',' '))}</h3><p>${esc(g.requires)}</p><small>${esc(g.evidence)}</small></article>`).join('');
    document.getElementById('catalogs').innerHTML = data.catalog_reconciliation.map((c) => `<div class="catalog-row"><code>${esc(c.source)}</code><span>${esc(c.scope)} · ${c.divisions ?? c.records} records</span></div>`).join('');
    const status = document.getElementById('reconcile-status'); status.textContent = s.catalogs_reconciled ? '55/55 mapped' : 'Mismatch'; status.className = `pill ${s.catalogs_reconciled?'pass':'fail'}`;
    document.getElementById('buckets').textContent = `Not counted as divisions: ${data.non_division_buckets.map((b) => b.name).join(', ')}.`;
    renderRows();
  }).catch((e) => { document.getElementById('load-error').textContent = `Evidence ledger unavailable: ${e.message}`; });
  document.getElementById('division-filter').addEventListener('input', () => data && renderRows());
})();
