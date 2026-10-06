import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import test from 'node:test';
import '../website/buddy-run.js';

const B = globalThis.BuddyRun;
const meta = JSON.parse(readFileSync(new URL('../website/data/run-prospectus.json', import.meta.url), 'utf8'));
const bots = JSON.parse(readFileSync(new URL('../website/data/run-prospectus-bots.json', import.meta.url), 'utf8'));
const fleetHtml = readFileSync(new URL('../website/fleet-runtime.html', import.meta.url), 'utf8');
const filesHtml = readFileSync(new URL('../website/files.html', import.meta.url), 'utf8');
const toCard = (row) => { const o = {}; bots.columns.forEach((c, i) => { o[c] = row[i]; }); o.blocked_reason = o.blocked ? bots.blocked_reasons[o.blocked] : null; return B.resolveBot(o, meta); };

test('every rendered Run button carries a complete prospectus; none without one', () => {
  assert.equal(B.runControls(null), '');
  assert.equal(B.runControls({ id: 'x', kind: 'workflow', title: 'x' }), '');
  for (const card of meta.workflows) {
    const html = B.runControls(card);
    assert.match(html, /data-prospectus="/, card.id);
    assert.equal(/class="btn btn-(primary br-run|outline br-run br-run-pick)"/.test(html), card.trigger.triggerable, card.id);
  }
  let runnable = 0;
  for (const row of bots.rows) {
    const card = toCard(row);
    assert.ok(B.complete(card), row[0]);
    const html = B.runControls(card);
    if (/class="btn btn-primary br-run"/.test(html)) runnable += 1;
  }
  assert.equal(runnable, meta.counts.bot_buttons);
});

test('money and destructive bots never get a Run link or a Customize form', () => {
  for (const row of bots.rows) {
    const card = toCard(row);
    if (card.risk_tier === 'money' || card.risk_tier === 'destructive') {
      assert.doesNotMatch(B.runControls(card), /issues\/new/);
      assert.doesNotMatch(B.botCustomizeForm(card, meta.customize), /<form/);
    }
  }
});

test('Run and Customize only open prefilled issues (no token on Pages)', () => {
  const card = toCard(bots.rows.find((r) => r[7]));
  const html = B.runControls(card);
  assert.match(html, /github\.com\/DreamCo-Technologies\/Dreamcobots\/issues\/new\?labels=buddy-command/);
  assert.match(decodeURIComponent(html.replace(/&amp;/g, '&')), /\/buddy run fleet_bot_run bot=/);
  const body = B.customizeBody(card.id, B.buildPatch({ model: 'dreamco/fast' }));
  assert.match(body, /^\/buddy customize \S+\n\n```yaml\nmodel: "dreamco\/fast"\n```/);
  const src = readFileSync(new URL('../website/buddy-run.js', import.meta.url), 'utf8');
  assert.doesNotMatch(src, /Authorization|ghp_|github_pat_|token=/i);
});

test('pages wire the shared Run/Customize library', () => {
  for (const html of [fleetHtml, filesHtml]) {
    assert.match(html, /buddy-run\.js/);
    assert.match(html, /buddy-run\.css/);
    assert.match(html, /nav\.js/);
  }
  assert.match(fleetHtml, /Run with Buddy/);
  assert.match(fleetHtml, /id="fr-wf-list"/);
  assert.match(filesHtml, /id="fp-search"/);
  assert.match(filesHtml, /id="fp-detail"/);
});

test('workflow prospectus count matches the live .github/workflows directory', () => {
  const live = readdirSync(new URL('../.github/workflows/', import.meta.url)).filter((f) => /\.ya?ml$/.test(f)).length;
  assert.equal(meta.workflows.length, live);
});
