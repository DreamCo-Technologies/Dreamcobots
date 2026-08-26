/* DreamCo Actions — evidence-first code review cockpit. Public-repo safe: read-only GitHub API, heuristic review, no claims of execution. */
(function () {
  'use strict';
  const REPO = 'DreamCo-Technologies/Dreamcobots';
  const state = { prs: [], selected: null, diff: '' };
  const $ = (id) => document.getElementById(id);
  const text = (v) => String(v ?? '');
  const esc = (v) => text(v).replace(/[&<>\"]/g, (c) => ({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;'}[c]));

  function finding(severity, title, evidence, recommendation) {
    return { severity, title, evidence, recommendation };
  }

  function reviewDiff(diff) {
    const lines = diff.split('\n');
    const added = lines.filter(l => l.startsWith('+') && !l.startsWith('+++'));
    const removed = lines.filter(l => l.startsWith('-') && !l.startsWith('---'));
    const files = [...diff.matchAll(/^diff --git a\/(.+?) b\/(.+)$/gm)].map(m => m[2]);
    const findings = [];
    const joined = added.join('\n');
    const lower = joined.toLowerCase();

    if (/api[_-]?key|secret|password|private[_-]?key|authorization:\s*bearer/i.test(joined))
      findings.push(finding('critical','Possible credential or secret exposure','Added lines contain a secret-like token or authorization pattern.','Move credentials to approved secret storage and rotate any exposed credential; never commit real secrets.'));
    if (/eval\s*\(|new Function\s*\(|child_process|exec\(|spawn\(|os\.system\s*\(/i.test(joined))
      findings.push(finding('high','Dynamic or process execution detected','Added code contains dynamic evaluation or process execution.','Require an explicit trust boundary, input validation, least privilege, timeout, and sandboxing.'));
    if (/innerHTML\s*=|dangerouslySetInnerHTML|document\.write\s*\(/i.test(joined))
      findings.push(finding('high','HTML injection surface detected','Added code writes raw HTML.','Prefer textContent/DOM construction or a vetted sanitizer and add an injection regression test.'));
    if (/fetch\(|axios\.|httpx\.|requests\./i.test(joined) && !/timeout/i.test(joined))
      findings.push(finding('medium','Network call without obvious timeout','A new network call appears without a nearby timeout.','Add bounded timeout, cancellation, retry policy, and error classification.'));
    if (/TODO|FIXME|HACK/i.test(joined))
      findings.push(finding('low','Unresolved work marker','Added code contains TODO/FIXME/HACK.','Convert the marker into a tracked issue or finish the implementation before approval.'));
    if (added.length > 250 && !/test|spec/i.test(files.join(' ')))
      findings.push(finding('medium','Large change without obvious test file','A large number of lines were added and no changed test file is visible.','Add focused unit/integration coverage and a regression test for the changed behavior.'));
    if (/\.github\/workflows\//i.test(files.join('\n')) && !/permissions:/i.test(joined))
      findings.push(finding('medium','Workflow permissions should be reviewed','A GitHub Actions workflow changed without an explicit permissions block in added lines.','Use least-privilege workflow permissions and review write-capable actions.'));
    if (!findings.length) findings.push(finding('info','No high-signal heuristic finding','The public diff passed the current static review rules.','Run repository CI, security tooling, and targeted tests before treating the change as verified.'));

    const score = Math.max(0, 100 - findings.reduce((n, f) => n + ({critical:40,high:25,medium:12,low:4,info:0}[f.severity] || 0), 0));
    const risk = findings.some(f=>f.severity==='critical') ? 'critical' : findings.some(f=>f.severity==='high') ? 'high' : findings.some(f=>f.severity==='medium') ? 'medium' : 'low';
    return { files, added: added.length, removed: removed.length, findings, score, risk };
  }

  function renderReview(result) {
    const host = $('actions-review-results');
    if (!host) return;
    host.innerHTML = `<div class="review-score"><strong>${result.score}/100</strong><span>heuristic review score</span><b class="review-risk review-${result.risk}">${esc(result.risk.toUpperCase())} RISK</b></div>` +
      `<p class="review-proof">Evidence: ${result.files.length} changed files, +${result.added}/-${result.removed} diff lines. This review is static evidence only; CI/runtime execution remains a required gate.</p>` +
      result.findings.map(f => `<article class="review-finding review-${esc(f.severity)}"><div><strong>${esc(f.severity.toUpperCase())}</strong><h4>${esc(f.title)}</h4></div><p>${esc(f.evidence)}</p><p><b>Recommended:</b> ${esc(f.recommendation)}</p></article>`).join('');
  }

  async function loadPRs() {
    const status = $('actions-review-status');
    try {
      const r = await fetch(`https://api.github.com/repos/${REPO}/pulls?state=open&per_page=30`, {headers:{Accept:'application/vnd.github+json'}});
      if (!r.ok) throw new Error(`GitHub ${r.status}`);
      state.prs = await r.json();
      const select = $('actions-review-pr');
      select.innerHTML = '<option value="">Choose an open PR…</option>' + state.prs.map(p => `<option value="${p.number}">#${p.number} — ${esc(p.title)}</option>`).join('');
      status.textContent = `${state.prs.length} open pull requests loaded from the public repository.`;
    } catch (e) { status.textContent = `Unable to load PRs: ${e.message}`; }
  }

  async function inspectPR(number) {
    const status = $('actions-review-status');
    const pr = state.prs.find(p => String(p.number) === String(number));
    if (!pr) return;
    state.selected = pr;
    status.textContent = `Loading diff for #${number}…`;
    try {
      const r = await fetch(`https://api.github.com/repos/${REPO}/pulls/${number}`, {headers:{Accept:'application/vnd.github.v3.diff'}});
      if (!r.ok) throw new Error(`GitHub ${r.status}`);
      state.diff = await r.text();
      renderReview(reviewDiff(state.diff));
      $('actions-review-open').href = pr.html_url;
      status.textContent = `Reviewing #${number}: ${pr.title}`;
    } catch (e) { status.textContent = `Diff unavailable: ${e.message}`; }
  }

  function init() {
    if (!$('actions-review-pr')) return;
    $('actions-review-pr').addEventListener('change', (e) => inspectPR(e.target.value));
    $('actions-review-refresh').addEventListener('click', loadPRs);
    loadPRs();
  }
  document.addEventListener('DOMContentLoaded', init);
})();
