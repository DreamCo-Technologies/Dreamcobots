(() => {
  'use strict';
  const $ = (id) => document.getElementById(id);
  const esc = (value) => String(value ?? '').replace(/[&<>"']/g, (c) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[c]));
  const labels = {
    registry: 'Resource registry categories',
    study: 'Study-resource categories',
    model: 'AI model categories',
    division: 'Division systems'
  };
  const order = ['registry', 'study', 'model', 'division'];
  let systems = [];

  function list(items) {
    if (!Array.isArray(items) || !items.length) return '<p class="cs-muted">Not yet specified.</p>';
    return '<ul>' + items.map(value => '<li>' + esc(value) + '</li>').join('') + '</ul>';
  }

  function card(item) {
    const contract = item.contract || {};
    const sourceFiles = (item.source_files || (item.source ? [item.source] : []))
      .map(path => '<li class="cs-source"><a href="https://github.com/DreamCo-Technologies/Dreamcobots/blob/main/' + encodeURI(path).replace(/#/g, '%23') + '" target="_blank" rel="noopener noreferrer">' + esc(path) + '</a></li>').join('');
    return '<details class="cs-card">' +
      '<summary><strong>' + esc(item.category) + '</strong><span class="cs-id">' + esc(item.id) + '</span>' +
      '<div class="cs-pills"><span class="cs-pill">' + esc(item.lifecycle_status) + '</span><span class="cs-pill">' + esc(item.implementation_status) + '</span><span class="cs-pill">' + esc(item.verification_status) + '</span>' +
      (item.reconciliation_status ? '<span class="cs-pill">' + esc(item.reconciliation_status) + '</span>' : '') +
      '<span class="cs-pill">' + Number(item.source_item_count || 0).toLocaleString() + ' source records</span></div></summary>' +
      '<div class="cs-detail"><h3>Mission</h3><p>' + esc(contract.mission || 'Mission not yet specified.') + '</p>' +
      '<h3>Inputs</h3>' + list(contract.inputs) + '<h3>Outputs</h3>' + list(contract.outputs) +
      '<h3>Permissions and safety</h3>' + list([...(contract.permissions || []), ...(contract.safety_controls || [])]) +
      '<h3>Metrics</h3>' + list(contract.metrics) + '<h3>Acceptance criteria</h3>' + list(contract.acceptance_criteria) +
      '<h3>Dependencies</h3>' + list(contract.dependencies) +
      '<h3>Source files</h3><ul>' + (sourceFiles || '<li>No source files recorded.</li>') + '</ul>' +
      '<h3>Known limitations</h3>' + list(contract.known_limitations) + '</div></details>';
  }

  function render() {
    const query = $('cs-search').value.trim().toLowerCase();
    const group = $('cs-group-filter').value;
    const filtered = systems.filter(item => {
      if (group !== 'all' && item.group !== group) return false;
      if (!query) return true;
      return [item.category, item.id, item.group, item.reconciliation_status,
        item.contract?.mission, ...(item.source_files || []), ...(item.source_resource_ids || [])]
        .join(' ').toLowerCase().includes(query);
    });
    const counts = Object.fromEntries(order.map(key => [key, filtered.filter(item => item.group === key).length]));
    $('cs-groups').innerHTML = order.filter(key => group === 'all' || group === key).map(key => {
      const rows = filtered.filter(item => item.group === key);
      return '<section class="cs-group" id="cs-' + key + '"><div class="cs-group-head"><div><h2>' + labels[key] + '</h2><p class="cs-muted">' + counts[key].toLocaleString() + ' systems shown</p></div></div>' +
        '<div class="cs-grid">' + (rows.length ? rows.map(card).join('') : '<p class="cs-muted">No matching systems.</p>') + '</div></section>';
    }).join('');
    $('cs-status').textContent = 'Showing ' + filtered.length.toLocaleString() + ' of ' + systems.length.toLocaleString() + ' separately catalogued category systems.';
  }

  async function init() {
    try {
      const response = await fetch('data/category-system-registry.json', { cache: 'no-store' });
      if (!response.ok) throw new Error('Registry request failed: HTTP ' + response.status);
      const data = await response.json();
      systems = Array.isArray(data.systems) ? data.systems : [];
      const counts = data.counts || {};
      $('cs-metrics').innerHTML = [
        ['Total systems', counts.total_category_systems],
        ['Study categories', counts.study_categories],
        ['Registry categories', counts.registry_categories],
        ['Model categories', counts.model_categories],
        ['Division systems', counts.division_systems]
      ].map(([label, value]) => '<article class="cs-metric"><strong>' + Number(value || 0).toLocaleString() + '</strong><span>' + label + '</span></article>').join('');
      $('cs-search').addEventListener('input', render);
      $('cs-group-filter').addEventListener('change', render);
      render();
    } catch (error) {
      $('cs-status').textContent = 'Could not load category registry: ' + error.message;
      $('cs-status').classList.add('error');
    }
  }
  init();
})();
