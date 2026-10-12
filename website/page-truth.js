/* Page truth labels. Loaded by nav.js on every page. Reads data/pages-feature-audit.json
 * (tools/audit_pages_features.py) and marks this page's non-working features as "stub"
 * instead of implying they work: dead controls get a stub chip, server-only (/api) features
 * and missing data are listed in a small notice. Never blocks or changes page behaviour. */
(function () {
  'use strict';
  try {
    const base = new URL('.', (document.currentScript && document.currentScript.src) || location.href);
    const page = decodeURIComponent(location.pathname.replace(/^.*?\/website\//, '').replace(new RegExp('^' + base.pathname.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')), '')) || 'index.html';
    fetch(new URL('data/pages-feature-audit.json', base).href, { cache: 'no-cache' })
      .then((r) => (r.ok ? r.json() : null))
      .then((audit) => {
        if (!audit) return;
        const row = audit.rows.find((r) => r.page === page || r.page === page + 'index.html');
        if (!row || row.verdict === 'working' || !row.issues.length) return;
        const style = document.createElement('style');
        style.textContent = '.pt-stub-chip{display:inline-block;margin-left:.35rem;padding:0 .4rem;border-radius:999px;font-size:.7rem;font-weight:700;background:#7f1d1d;color:#fff;vertical-align:middle}' +
          '.pt-notice{margin:.6rem auto;max-width:1100px;padding:.5rem .8rem;border:1px dashed #b45309;border-radius:8px;font-size:.82rem;background:rgba(180,83,9,.08)}.pt-notice ul{margin:.2rem 0 0;padding-left:1.1rem}';
        document.head.appendChild(style);
        const notes = [];
        row.issues.forEach((i) => {
          if (i.kind === 'control') {
            const el = document.getElementById(i.target.split('#')[1]);
            if (el && !el.querySelector('.pt-stub-chip')) {
              el.setAttribute('data-stub', 'true');
              el.title = 'Stub: this control is not wired to any code yet (pages feature audit).';
              const chip = document.createElement('span');
              chip.className = 'pt-stub-chip';
              chip.textContent = 'stub';
              (el.tagName === 'FORM' ? el : el).appendChild(chip);
            }
            notes.push('Control “' + (i.label || i.target) + '” is a stub (not wired to code).');
          } else if (i.status === 'server-only') {
            notes.push('Feature using ' + i.target + ' needs the DreamCo server; it cannot work on static GitHub Pages (stub here).');
          } else if (i.status === 'missing') {
            notes.push(i.kind + ' ' + i.target + ' is missing, so the feature that uses it does not work.');
          } else if (i.status === 'stub-text') {
            notes.push('Page text says “' + i.target + '”.');
          }
        });
        const box = document.createElement('aside');
        box.className = 'pt-notice';
        box.setAttribute('role', 'note');
        box.innerHTML = '<strong>Page truth: ' + row.verdict + '.</strong> Some features on this page are stubs:<ul>' +
          Array.from(new Set(notes)).slice(0, 8).map((n) => '<li>' + n.replace(/[&<>]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c])) + '</li>').join('') +
          '</ul><a href="' + new URL('files.html#f=' + encodeURIComponent('website/' + page), base).href + '">file prospectus</a> · source: data/pages-feature-audit.json';
        const main = document.querySelector('main') || document.body;
        main.insertBefore(box, main.firstChild);
      })
      .catch(() => {});
  } catch (err) { /* never break the page */ }
})();
