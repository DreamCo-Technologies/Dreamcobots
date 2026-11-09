(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const esc = value => String(value ?? '').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  let data = {documents:[],gap_status_counts:{}};
  function render() {
    const q = $('gap-search').value.trim().toLowerCase();
    const status = $('gap-filter').value;
    const rows = data.documents.filter(row => {
      if (status !== 'all' && row.gap_status !== status) return false;
      return !q || [row.path,row.title,row.next_action,...row.referenced_paths,...row.missing_paths].join(' ').toLowerCase().includes(q);
    });
    $('gap-status').textContent = 'Showing ' + rows.length.toLocaleString() + ' of ' + data.documents.length.toLocaleString() + ' tracked Markdown documents. All totals are recomputed from the current repository.';
    $('gap-results').innerHTML = rows.map(row => '<article class="gap-card">' +
      '<h3>' + esc(row.path) + '</h3><p>' + esc(row.title) + '</p><span class="gap-pill">' + esc(row.gap_status) + '</span><span class="gap-pill">' + Number(row.actionable_claim_lines || 0).toLocaleString() + ' actionable lines</span>' +
      '<p><strong>Implementation references</strong></p><div class="gap-paths">' + (row.implementation_paths || []).map(p=>'<a href="https://github.com/DreamCo-Technologies/Dreamcobots/blob/main/' + encodeURI(p) + '">' + esc(p) + '</a>').join('<br>') + (row.implementation_paths?.length ? '' : 'None detected') + '</div>' +
      '<p><strong>Test references</strong></p><div class="gap-paths">' + (row.test_paths || []).map(p=>'<a href="https://github.com/DreamCo-Technologies/Dreamcobots/blob/main/' + encodeURI(p) + '">' + esc(p) + '</a>').join('<br>') + (row.test_paths?.length ? '' : 'None detected') + '</div>' +
      '<p><strong>Missing paths</strong></p><div class="gap-paths">' + ((row.missing_paths || []).map(esc).join('<br>') || 'None detected') + '</div>' +
      '<p>' + esc(row.next_action) + '</p><p class="gap-muted">Execution verified: no. This report does not claim implementation or production readiness.</p></article>').join('') || '<p class="gap-muted">No matching documents.</p>';
  }
  async function init() {
    try {
      const response = await fetch('data/markdown-implementation-gap-audit.json',{cache:'no-store'});
      if(!response.ok) throw new Error('Audit data unavailable: HTTP ' + response.status);
      data = await response.json();
      const metrics = [
        ['Markdown files',data.document_count],
        ['Actionable claim lines',data.actionable_claim_lines],
        ['Missing path references',data.documents_with_missing_paths],
        ['No implementation links',data.documents_without_implementation_references],
        ['Code links without tests',data.documents_without_test_references]
      ];
      $('gap-metrics').innerHTML = metrics.map(([label,value])=>'<article class="gap-metric"><strong>'+Number(value||0).toLocaleString()+'</strong><span>'+esc(label)+'</span></article>').join('');
      const statuses = Object.keys(data.gap_status_counts || {}).sort();
      $('gap-filter').innerHTML = '<option value="all">All gap statuses</option>' + statuses.map(s=>'<option value="'+esc(s)+'">'+esc(s.replaceAll('_',' '))+' ('+Number(data.gap_status_counts[s]).toLocaleString()+')</option>').join('');
      $('gap-search').addEventListener('input',render);
      $('gap-filter').addEventListener('change',render);
      render();
    } catch(error) {
      $('gap-status').textContent = error.message;
    }
  }
  init();
})();