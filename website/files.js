/* File prospectus browser. Reads data/file-prospectus/index.json + shards (tools/build_file_prospectus.py). */
(function () {
  'use strict';
  const BR = window.BuddyRun;
  const esc = BR.esc;
  const PAGE = 200;
  const byId = (id) => document.getElementById(id);
  const state = { index: null, rows: [], byPath: new Map(), loaded: new Set(), filtered: [], shown: PAGE, meta: null };

  function toObj(cols, row) { const o = {}; cols.forEach((c, i) => { o[c] = row[i]; }); return o; }

  function loadShard(name) {
    if (state.loaded.has(name)) return Promise.resolve();
    const shard = state.index.shards.find((s) => s.name === name);
    if (!shard) return Promise.resolve();
    return fetch(shard.url, { cache: 'no-cache' }).then((r) => r.json()).then((p) => {
      if (state.loaded.has(name)) return;
      state.loaded.add(name);
      p.rows.forEach((row) => { const o = toObj(state.index.columns, row); o.shard = name; state.rows.push(o); state.byPath.set(o.path, o); });
    });
  }

  const loadAll = () => Promise.all(state.index.shards.map((s) => loadShard(s.name)));

  function fileLink(path) { return '<a href="#f=' + encodeURIComponent(path) + '"><code>' + esc(path) + '</code></a>'; }

  function renderTable() {
    const visible = state.filtered.slice(0, state.shown);
    byId('fp-table').tBodies[0].innerHTML = visible.map((f) =>
      '<tr><td>' + fileLink(f.path) + '</td><td>' + esc(f.type) + '</td><td>' + esc(f.purpose) +
      (f.purpose_source === 'auto-summary' ? ' <span class="fr-chip">auto-summary</span>' : '') + '</td><td>' + esc(f.owner) + '</td>' +
      '<td class="num">' + f.used_by_count + '</td><td>' + esc(f.readiness) + '</td></tr>').join('');
    byId('fp-count').textContent = state.filtered.length + ' of ' + state.index.files + ' files' + (state.loaded.size < state.index.shards.length ? ' (loading folders…)' : '');
    byId('fp-more').hidden = state.filtered.length <= state.shown;
  }

  function applyFilters() {
    const q = byId('fp-search').value.trim().toLowerCase();
    const shard = byId('fp-shard').value;
    const src = byId('fp-source').value;
    const need = shard ? loadShard(shard) : (q || src ? loadAll() : loadShard(state.index.shards[0].name));
    need.then(() => {
      state.filtered = state.rows.filter((f) => (!shard || f.shard === shard) && (!src || f.purpose_source === src) &&
        (!q || (f.path + ' ' + f.purpose + ' ' + f.owner + ' ' + f.type).toLowerCase().includes(q)))
        .sort((a, b) => (a.path < b.path ? -1 : 1));
      state.shown = PAGE;
      renderTable();
    });
  }

  function detail(path) {
    const top = path.indexOf('/') > 0 ? path.split('/')[0] : '(root)';
    const shardName = top === '(root)' ? 'root' : top.replace(/^\.+/, '').replace(/[^A-Za-z0-9_-]+/g, '_');
    loadShard(shardName).then(() => {
      const f = state.byPath.get(path);
      const panel = byId('fp-detail');
      panel.hidden = false;
      if (!f) { byId('fp-detail-body').innerHTML = '<p>No prospectus for <code>' + esc(path) + '</code>.</p>'; return; }
      const bot = f.owner.indexOf('bot:') === 0 ? f.owner.slice(4) : null;
      const list = (items) => items.length ? '<ul>' + items.map((p) => '<li>' + fileLink(p) + '</li>').join('') + '</ul>' : '—';
      byId('fp-detail-title').textContent = path;
      byId('fp-detail-body').innerHTML =
        '<dl class="br-grid">' +
        '<div><dt>Type</dt><dd>' + esc(f.type) + '</dd></div>' +
        '<div><dt>Purpose</dt><dd>' + esc(f.purpose) + ' <span class="fr-chip">' + esc(f.purpose_source) + '</span></dd></div>' +
        '<div><dt>Owner</dt><dd>' + esc(f.owner) + ' <span class="fr-chip">' + esc(f.owner_source) + '</span>' + (bot ? ' · <a href="fleet-runtime.html#bot-' + encodeURIComponent(bot) + '">bot card</a>' : '') + '</dd></div>' +
        '<div><dt>Used by (' + f.used_by_count + ')</dt><dd>' + list(f.used_by) + (f.used_by_count > f.used_by.length ? '<p class="br-note">+' + (f.used_by_count - f.used_by.length) + ' more</p>' : '') + '</dd></div>' +
        '<div><dt>Related tests</dt><dd>' + list(f.tests) + '</dd></div>' +
        '<div><dt>Readiness</dt><dd>' + esc(f.readiness) + '</dd></div>' +
        '<div><dt>Links</dt><dd><a href="' + BR.GH + '/blob/main/' + encodeURI(path) + '" rel="noopener">source</a> · <a href="' + BR.GH + '/commits/main/' + encodeURI(path) + '" rel="noopener">history</a></dd></div>' +
        '</dl>' +
        '<div id="fp-run"></div>' +
        '<details class="br-custom-details"><summary>Customize this prospectus</summary>' + (state.meta ? BR.fileCustomizeForm(path, f, state.meta.customize) : 'loading…') + '</details>';
      if (bot && state.meta) {
        BR.loadBots().then((cards) => { const card = BR.resolveBot(cards.get(bot), state.meta); byId('fp-run').innerHTML = card ? '<h3>Owning bot</h3>' + BR.runControls(card) : ''; });
      }
      if (f.type === 'workflow' && state.meta) {
        const card = state.meta.workflows.find((c) => c.links.workflow.endsWith('/' + path.split('/').pop()));
        byId('fp-run').innerHTML = card ? '<h3>Workflow job</h3>' + BR.runControls(card) : '';
      }
      panel.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  }

  function onHash() {
    const m = /^#f=(.+)$/.exec(location.hash || '');
    if (m) detail(decodeURIComponent(m[1]));
  }

  function init(index) {
    state.index = index;
    byId('fp-totals').innerHTML = '<div><span>Files</span><strong>' + index.files + '</strong></div>' +
      Object.entries(index.purpose_sources).map(([k, v]) => '<div><span>purpose: ' + esc(k) + '</span><strong>' + v + '</strong></div>').join('');
    byId('fp-shard').insertAdjacentHTML('beforeend', index.shards.map((s) => '<option value="' + esc(s.name) + '">' + esc(s.name) + ' (' + s.files + ')</option>').join(''));
    byId('fp-source').insertAdjacentHTML('beforeend', Object.keys(index.purpose_sources).map((k) => '<option>' + esc(k) + '</option>').join(''));
    ['fp-search', 'fp-shard', 'fp-source'].forEach((id) => byId(id).addEventListener('input', applyFilters));
    byId('fp-more').addEventListener('click', () => { state.shown += PAGE; renderTable(); });
    BR.wireCustomize(document.body);
    BR.loadMeta().then((m) => { state.meta = m; onHash(); }).catch(() => onHash());
    window.addEventListener('hashchange', onHash);
    applyFilters();
  }

  fetch('data/file-prospectus/index.json', { cache: 'no-cache' })
    .then((r) => { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
    .then(init)
    .catch((err) => { byId('fp-totals').innerHTML = '<div><span>Index unavailable</span><strong>' + esc(err.message) + '</strong></div>'; });
})();
