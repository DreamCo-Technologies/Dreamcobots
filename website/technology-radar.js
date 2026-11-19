(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  let catalog = {records:[],source_runs:[],summary:{}};
  let policy = {priority_lenses:[]};
  const fmt = value => value ? new Date(value).toLocaleString() : 'Date not supplied';

  function renderMetrics() {
    const summary = catalog.summary || {};
    const records = catalog.records || [];
    const active = records.filter(x => x.status === 'active').length;
    const remote = records.filter(x => x.record_kind === 'remote_job').length;
    const matched = records.filter(x => (x.priority_lenses || []).length).length;
    $('radar-metrics').innerHTML = [
      ['Discoveries retained', records.length],
      ['Active in latest scan', active],
      ['Remote-work leads', remote],
      ['Priority matches', matched],
      ['Sources checked', summary.sources_succeeded || 0],
      ['Sources needing attention', summary.sources_failed || 0],
      ['Sources not yet checked', summary.sources_pending || 0]
    ].map(([label,value]) => '<article class="radar-metric"><strong>' + Number(value).toLocaleString() + '</strong><span>' + label + '</span></article>').join('');
  }

  function renderFilters() {
    const lenses = [...new Set((policy.priority_lenses || []).map(x => x.id))];
    $('radar-lens').innerHTML = '<option value="all">All focus areas</option>' + lenses.map(id => {
      const item = policy.priority_lenses.find(x => x.id === id);
      return '<option value="' + esc(id) + '">' + esc(item?.label || id) + '</option>';
    }).join('');
    const kinds = [...new Set((catalog.records || []).map(x => x.record_kind).filter(Boolean))].sort();
    $('radar-kind').innerHTML = '<option value="all">All discovery types</option>' + kinds.map(x => '<option value="' + esc(x) + '">' + esc(x.replaceAll('_',' ')) + '</option>').join('');
  }

  function renderRecords() {
    const query = $('radar-search').value.trim().toLowerCase();
    const lens = $('radar-lens').value;
    const kind = $('radar-kind').value;
    const rows = (catalog.records || []).filter(item => {
      if (lens !== 'all' && !(item.priority_lenses || []).includes(lens)) return false;
      if (kind !== 'all' && item.record_kind !== kind) return false;
      if (!query) return true;
      return [item.title,item.summary,item.source_name,item.source_id,item.record_kind,item.url,...(item.priority_lenses || [])].join(' ').toLowerCase().includes(query);
    });
    $('radar-status').textContent = 'Showing ' + rows.length.toLocaleString() + ' of ' + (catalog.records || []).length.toLocaleString() + ' retained discoveries. The list grows and changes as sources refresh.';
    $('radar-results').innerHTML = rows.map(item => '<article class="radar-card">' +
      '<div class="radar-pills"><span class="radar-pill">' + esc(item.record_kind) + '</span><span class="radar-pill">' + esc(item.source_trust_tier) + '</span><span class="radar-pill">' + esc(item.status) + '</span></div>' +
      '<h3>' + esc(item.title) + '</h3><p>' + esc(item.summary || 'No summary supplied by source.') + '</p>' +
      '<div class="radar-pills">' + (item.priority_lenses || []).map(x => '<span class="radar-pill">' + esc(x.replaceAll('_',' ')) + '</span>').join('') + '</div>' +
      (item.url ? '<a href="' + esc(item.url) + '" target="_blank" rel="noopener noreferrer">Open original source</a>' : '<span class="radar-muted">No direct item URL supplied</span>') +
      '<p class="radar-muted">Source: ' + esc(item.source_name) + ' · Published: ' + esc(fmt(item.published_at)) + ' · First seen: ' + esc(fmt(item.first_seen_at)) + ' · Last seen: ' + esc(fmt(item.last_seen_at)) + '</p>' +
      '<p class="radar-muted">Discovery only. Capability verified: no. Income claim verified: no.</p></article>').join('') || '<p class="radar-muted">No matching discoveries. Try a broader search or wait for the next source refresh.</p>';
  }

  function renderSources() {
    const rows = catalog.source_runs || [];
    $('radar-sources').innerHTML = rows.map(item => '<article class="radar-card">' +
      '<div class="radar-pills"><span class="radar-pill">' + esc(item.status) + '</span><span class="radar-pill">' + Number(item.record_count || 0).toLocaleString() + ' records</span></div>' +
      '<h3>' + esc(item.source_id) + '</h3><p>' + esc(fmt(item.checked_at)) + '</p>' +
      (item.error ? '<p>' + esc(item.error) + '</p>' : '<p class="radar-muted">No source error recorded.</p>') +
      '</article>').join('') || '<p class="radar-muted">No source refresh has completed yet.</p>';
  }

  async function init() {
    try {
      const [catalogResponse, policyResponse] = await Promise.all([
        fetch('data/buddy-technology-radar.json', {cache:'no-store'}),
        fetch('data/technology-discovery-policy.json', {cache:'no-store'}).catch(() => null)
      ]);
      if (!catalogResponse.ok) throw new Error('Technology index unavailable: HTTP ' + catalogResponse.status);
      catalog = await catalogResponse.json();
      if (policyResponse?.ok) policy = await policyResponse.json();
      renderMetrics();
      renderFilters();
      renderRecords();
      renderSources();
      $('radar-updated').textContent = fmt(catalog.generated_at);
      for (const id of ['radar-search','radar-lens','radar-kind']) $(id).addEventListener(id === 'radar-search' ? 'input' : 'change', renderRecords);
    } catch (error) {
      $('radar-status').textContent = error.message;
      $('radar-status').classList.add('error');
    }
  }
  init();
})();
