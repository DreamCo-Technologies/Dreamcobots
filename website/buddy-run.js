/* Run with Buddy + prospectus cards + Customize forms, shared by fleet-runtime.html and files.html.
 *
 * Pages is static and public: no token lives here. "Run" and "Customize" only
 * open a prefilled GitHub issue (/buddy run … or /buddy customize … with a
 * fenced YAML patch). The Buddy command router checks the actor allowlist and
 * write permission, validates, then dispatches or opens a PR.
 * Cards come from data/run-prospectus.json (tools/build_actions_prospectus.py);
 * a button is never rendered without a complete card.
 */
(function (global) {
  'use strict';
  const REPO = 'DreamCo-Technologies/Dreamcobots';
  const GH = 'https://github.com/' + REPO;
  const LABEL = 'buddy-command';
  const REQUIRED = ['id', 'kind', 'title', 'does', 'inputs', 'outputs', 'touches', 'risk_tier', 'trigger', 'secrets', 'cost', 'runtime', 'readiness', 'links'];
  const esc = (v) => String(v == null ? '' : v).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const store = { meta: null, bots: null, botsPromise: null };

  function issueUrl(title, body) {
    return GH + '/issues/new?labels=' + encodeURIComponent(LABEL) + '&title=' + encodeURIComponent(title) + '&body=' + encodeURIComponent(body);
  }

  function loadMeta() {
    if (store.meta) return Promise.resolve(store.meta);
    return fetch('data/run-prospectus.json', { cache: 'no-cache' }).then((r) => { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
      .then((m) => { store.meta = m; return m; });
  }

  function loadBots() {
    if (store.bots) return Promise.resolve(store.bots);
    if (!store.botsPromise) {
      store.botsPromise = loadMeta().then((m) => fetch(m.bot_cards_url || 'data/run-prospectus-bots.json', { cache: 'no-cache' }))
        .then((r) => { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
        .then((p) => {
          const map = new Map();
          p.rows.forEach((row) => { const o = {}; p.columns.forEach((c, i) => { o[c] = row[i]; }); o.blocked_reason = o.blocked ? p.blocked_reasons[o.blocked] : null; map.set(o.id, o); });
          store.bots = map; return map;
        });
    }
    return store.botsPromise;
  }

  /* Expand a compact bot row with its engine template: same shape as resolve() in the generator. */
  function resolveBot(row, meta) {
    if (!row) return null;
    const t = (meta.templates || {})['engine:' + row.engine] || {};
    const src = (row.files || [])[0] || '';
    return {
      id: row.id, kind: 'bot', title: row.title, does: row.does,
      inputs: t.inputs || ['none: spec-only bot'], outputs: t.outputs || ['none: spec-only bot'],
      touches: { files: row.files || [], systems: t.systems || ['none (not runnable)'], services: t.services || ['none'] },
      risk_tier: row.risk_tier,
      trigger: { allowlist: meta.operators, requires_write_permission: true, requires_owner_approval: false, triggerable: !!row.triggerable,
        blocked_reason: row.blocked_reason, command: row.triggerable ? '/buddy run fleet_bot_run bot=' + row.id : null },
      secrets: t.secrets || ['none'], cost: t.cost || 'unknown', runtime: t.runtime || 'unknown',
      readiness: { state: row.readiness, detail: 'fixture: ' + (row.fixture || 'none'), source: 'website/data/fleet-runtime-status.json' },
      links: { source: src ? GH + '/blob/main/' + src : 'unknown', workflow: GH + '/actions/workflows/fleet-bot-run.yml',
        latest_run: GH + '/actions/workflows/fleet-bot-run.yml',
        evidence: row.evidence ? GH + '/blob/main/' + row.evidence : 'none yet' },
      division: row.division, engine: row.engine, capabilities: row.capabilities || [], custom: row.custom || null,
    };
  }

  function complete(card) {
    return !!card && REQUIRED.every((k) => card[k] != null && card[k] !== '' && !(Array.isArray(card[k]) && !card[k].length));
  }

  const list = (items) => '<ul>' + (items || []).map((x) => '<li>' + esc(x) + '</li>').join('') + '</ul>';
  const link = (href, text) => /^https?:\/\//.test(href) ? '<a href="' + esc(href) + '" rel="noopener">' + esc(text) + '</a>' : esc(href);

  function prospectusHtml(card) {
    if (!complete(card)) return '<p class="br-missing">No prospectus card: this item has no Run button.</p>';
    const t = card.trigger;
    return '<div class="br-card" data-prospectus="' + esc(card.id) + '">' +
      '<p class="br-does">' + esc(card.does) + '</p>' +
      '<dl class="br-grid">' +
      '<div><dt>Inputs</dt><dd>' + list(card.inputs) + '</dd></div>' +
      '<div><dt>Outputs</dt><dd>' + list(card.outputs) + '</dd></div>' +
      '<div><dt>Files</dt><dd>' + list(card.touches.files.length ? card.touches.files : ['none declared']) + '</dd></div>' +
      '<div><dt>Systems</dt><dd>' + list(card.touches.systems) + '</dd></div>' +
      '<div><dt>Services</dt><dd>' + list(card.touches.services) + '</dd></div>' +
      '<div><dt>Risk tier</dt><dd><span class="br-tier br-tier-' + esc(card.risk_tier) + '">' + esc(card.risk_tier) + '</span>' + (t.requires_owner_approval ? ' · owner approval' : '') + '</dd></div>' +
      '<div><dt>Who can trigger</dt><dd>' + esc((t.allowlist || []).join(', ')) + ' (allowlist, with write permission)' + (t.triggerable ? '' : '<br><strong>Not triggerable:</strong> ' + esc(t.blocked_reason)) + '</dd></div>' +
      '<div><dt>Secrets (names only)</dt><dd>' + list(card.secrets) + '</dd></div>' +
      '<div><dt>Cost</dt><dd>' + esc(card.cost) + '</dd></div>' +
      '<div><dt>Runtime</dt><dd>' + esc(card.runtime) + '</dd></div>' +
      '<div><dt>Readiness</dt><dd><strong>' + esc(card.readiness.state) + '</strong> · ' + esc(card.readiness.detail) + '</dd></div>' +
      '<div><dt>Links</dt><dd>' + link(card.links.source, 'source') + ' · ' + link(card.links.workflow, 'workflow') + ' · ' +
        link(card.links.latest_run, 'latest run') + ' · ' + (/^https?:/.test(card.links.evidence) ? link(card.links.evidence, 'evidence') : 'evidence: ' + esc(card.links.evidence)) + '</dd></div>' +
      '</dl></div>';
  }

  function runControls(card) {
    if (!complete(card)) return '';  // never a button without a prospectus
    const t = card.trigger;
    const runnable = t.triggerable && t.command && card.risk_tier !== 'money' && card.risk_tier !== 'destructive';
    const button = runnable && t.command.indexOf('<') !== -1
      ? '<a class="btn btn-outline br-run br-run-pick" href="fleet-runtime.html#fr-bots-title">Choose a bot to run</a>'
      : runnable
      ? '<a class="btn btn-primary br-run" target="_blank" rel="noopener" href="' + esc(issueUrl(t.command, t.command + '\n\n<!-- Opened from GitHub Pages. Pages holds no token; the Buddy router checks the allowlist before dispatching. -->')) + '">Run with Buddy</a>'
      : '<span class="br-run is-disabled" title="' + esc(t.blocked_reason) + '">Not runnable</span>';
    return '<div class="br-controls">' + button + '<details class="br-details"><summary>Prospectus</summary>' + prospectusHtml(card) + '</details></div>';
  }

  /* ---------------------------------------------------------- customize */
  function yamlString(v) { return JSON.stringify(String(v)); }

  function buildPatch(fields) {
    const lines = [];
    Object.keys(fields).forEach((k) => {
      const v = fields[k];
      if (v && typeof v === 'object') {
        const keys = Object.keys(v);
        if (!keys.length) return;
        lines.push(k + ':');
        keys.forEach((c) => lines.push('  ' + c + ': ' + (v[c] ? 'true' : 'false')));
      } else if (typeof v === 'boolean') {
        lines.push(k + ': ' + (v ? 'true' : 'false'));
      } else if (v !== '' && v != null) {
        lines.push(k + ': ' + yamlString(v));
      }
    });
    return lines.join('\n');
  }

  function customizeBody(target, patch) {
    return '/buddy customize ' + target + '\n\n```yaml\n' + patch + '\n```\n\n<!-- Opened from GitHub Pages. The router validates this patch against the editable-field allowlist and opens a PR; nothing is applied directly. -->';
  }

  function pendingKey(target) { return 'buddy-customize:' + target; }

  function botCustomizeForm(card, spec) {
    if (!card || card.risk_tier === 'money' || card.risk_tier === 'destructive') {
      return '<p class="br-note">Customization is not available for money or destructive bots.</p>';
    }
    const keyRe = new RegExp(spec.toggle_key_pattern);
    const caps = (card.capabilities || []).filter((c) => keyRe.test(c));
    const cur = card.custom || {};
    const opt = (vals, sel, blank) => (blank ? '<option value="">' + esc(blank) + '</option>' : '') + vals.map((v) => '<option' + (v === sel ? ' selected' : '') + '>' + esc(v) + '</option>').join('');
    return '<form class="br-customize" data-target="' + esc(card.id) + '" data-kind="bot"' + (cur.enabled === false ? ' data-was-disabled="1"' : '') + '>' +
      '<label><input type="checkbox" name="enabled"' + (cur.enabled === false ? '' : ' checked') + '> Enabled</label>' +
      '<label>Display name <input name="display_name" maxlength="80" placeholder="' + esc(card.title) + '" value="' + esc(cur.display_name || '') + '"></label>' +
      '<label>Prompt / instructions <textarea name="prompt" maxlength="2000" rows="3">' + esc(cur.prompt || '') + '</textarea></label>' +
      '<label>Model (allowlist) <select name="model">' + opt(spec.model_allowlist, cur.model, 'unchanged') + '</select></label>' +
      '<label>Schedule (UTC cron, fixed minute and hour, or off) <input name="schedule" placeholder="17 9 * * 1" value="' + esc(cur.schedule || '') + '"></label>' +
      '<label>Division <select name="division">' + opt(spec.divisions, cur.division, 'unchanged (' + card.division + ')') + '</select></label>' +
      (caps.length ? '<fieldset><legend>Capabilities</legend>' + caps.map((c) => '<label><input type="checkbox" data-cap="' + esc(c) + '"' + (((cur.capabilities || {})[c] === false) ? '' : ' checked') + '> ' + esc(c) + '</label>').join('') + '</fieldset>' : '') +
      '<button class="btn btn-outline" type="submit">Open customize request</button>' +
      '<p class="br-note">Opens a prefilled <code>/buddy customize</code> issue. Only allowlisted operators with write access are applied, via a PR.</p>' +
      '<div class="br-pending" data-pending="' + esc(card.id) + '"></div></form>';
  }

  function divisionCustomizeForm(card, spec) {
    if (!card || !card.customizable) return '<p class="br-note">Customization is not available for this division (no source, or money-only).</p>';
    const cur = card.custom || {};
    const opt = (vals, sel, blank) => '<option value="">' + esc(blank) + '</option>' + vals.map((v) => '<option' + (v === sel ? ' selected' : '') + '>' + esc(v) + '</option>').join('');
    return '<form class="br-customize" data-target="' + esc(card.id) + '" data-kind="division"' + (cur.enabled === false ? ' data-was-disabled="1"' : '') + '>' +
      '<label><input type="checkbox" name="enabled"' + (cur.enabled === false ? '' : ' checked') + '> Division enabled</label>' +
      '<label>Division-wide prompt <textarea name="prompt" maxlength="2000" rows="3">' + esc(cur.prompt || '') + '</textarea></label>' +
      '<label>Model (allowlist) <select name="model">' + opt(spec.model_allowlist, cur.model, 'unchanged') + '</select></label>' +
      '<label>Schedule (UTC cron, fixed minute and hour, or off) <input name="schedule" placeholder="17 9 * * 1" value="' + esc(cur.schedule || '') + '"></label>' +
      '<button class="btn btn-outline" type="submit">Open customize request</button>' +
      '<p class="br-note">Bot-level customizations override division settings. Money and destructive bots ignore them.</p>' +
      '<div class="br-pending" data-pending="' + esc(card.id) + '"></div></form>';
  }

  function fileCustomizeForm(path, row, spec) {
    return '<form class="br-customize" data-target="file:' + esc(path) + '" data-kind="file">' +
      '<label>Purpose (replaces the auto-summary) <textarea name="purpose" maxlength="300" rows="2" placeholder="' + esc(row.purpose) + '"></textarea></label>' +
      '<label>Owner (bot slug or division) <input name="owner" list="br-owner-options" placeholder="' + esc(row.owner) + '"></label>' +
      '<datalist id="br-owner-options">' + (spec.divisions || []).map((d) => '<option value="' + esc(d) + '">').join('') + '</datalist>' +
      '<button class="btn btn-outline" type="submit">Open customize request</button>' +
      '<p class="br-note">File contents are never edited from Pages; only the prospectus purpose/owner.</p>' +
      '<div class="br-pending" data-pending="file:' + esc(path) + '"></div></form>';
  }

  function collect(form) {
    const fields = {};
    if (form.dataset.kind === 'bot' || form.dataset.kind === 'division') {
      const enabled = form.querySelector('[name=enabled]').checked;
      if (!enabled) fields.enabled = false;
      ['display_name', 'prompt', 'model', 'schedule', 'division'].forEach((n) => { const el = form.querySelector('[name=' + n + ']'); const v = el ? el.value.trim() : ''; if (v) fields[n] = v; });
      const caps = {};
      form.querySelectorAll('[data-cap]').forEach((el) => { if (!el.checked) caps[el.dataset.cap] = false; });
      if (Object.keys(caps).length) fields.capabilities = caps;
      if (enabled && form.dataset.wasDisabled === '1') fields.enabled = true;
    } else {
      ['purpose', 'owner'].forEach((n) => { const v = form.querySelector('[name=' + n + ']').value.trim(); if (v) fields[n] = v; });
    }
    return fields;
  }

  function renderPending(target, container) {
    if (!container) return;
    const local = JSON.parse(localStorage.getItem(pendingKey(target)) || 'null');
    const parts = [];
    if (local) parts.push('<li>Submitted from this browser ' + esc(local.at) + ': <code>' + esc(Object.keys(local.fields).join(', ')) + '</code> (awaiting router)</li>');
    container.innerHTML = parts.length ? '<strong>Pending changes</strong><ul>' + parts.join('') + '</ul>' : '';
    const cacheKey = 'buddy-open-commands';
    const cached = sessionStorage.getItem(cacheKey);
    const fresh = cached && (Date.now() - JSON.parse(cached).t < 300000);
    const get = fresh ? Promise.resolve(JSON.parse(cached).items)
      : fetch('https://api.github.com/repos/' + REPO + '/issues?state=open&labels=' + LABEL + '&per_page=100')
        .then((r) => (r.ok ? r.json() : []))
        .then((items) => { const slim = items.map((i) => ({ n: i.number, t: i.title, u: i.html_url, pr: !!i.pull_request })); sessionStorage.setItem(cacheKey, JSON.stringify({ t: Date.now(), items: slim })); return slim; })
        .catch(() => []);
    get.then((items) => {
      const mine = items.filter((i) => i.t.indexOf('customize ' + target) !== -1 && (i.t.endsWith(target) || i.t.indexOf(target + ' ') !== -1 || i.t.endsWith(target + ')')));
      if (!mine.length) return;
      container.innerHTML = '<strong>Pending changes</strong><ul>' + parts.join('') + mine.map((i) => '<li>' + (i.pr ? 'PR' : 'Issue') + ' <a href="' + esc(i.u) + '">#' + i.n + '</a> ' + esc(i.t) + '</li>').join('') + '</ul>';
    });
  }

  function wireCustomize(root) {
    root.addEventListener('submit', (event) => {
      const form = event.target.closest('form.br-customize');
      if (!form) return;
      event.preventDefault();
      const fields = collect(form);
      if (!Object.keys(fields).length) { alert('Change at least one field first.'); return; }
      const target = form.dataset.target;
      const patch = buildPatch(fields);
      window.open(issueUrl('/buddy customize ' + target, customizeBody(target, patch)), '_blank', 'noopener');
      localStorage.setItem(pendingKey(target), JSON.stringify({ at: new Date().toISOString().slice(0, 16).replace('T', ' ') + ' UTC', fields }));
      renderPending(target, form.querySelector('.br-pending'));
    });
    root.addEventListener('toggle', (event) => {
      const details = event.target;
      if (details.open && details.classList && details.classList.contains('br-custom-details')) {
        const form = details.querySelector('form.br-customize');
        if (form) renderPending(form.dataset.target, form.querySelector('.br-pending'));
      }
    }, true);
  }

  global.BuddyRun = { REPO, GH, issueUrl, loadMeta, loadBots, resolveBot, complete, prospectusHtml, runControls,
    buildPatch, customizeBody, botCustomizeForm, divisionCustomizeForm, fileCustomizeForm, wireCustomize, renderPending, esc };
})(typeof window !== 'undefined' ? window : globalThis);
