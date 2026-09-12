import assert from 'node:assert/strict';
import fs from 'node:fs';
import test from 'node:test';

const html = fs.readFileSync('website/buddy-command-center.html', 'utf8');
const script = fs.readFileSync('website/buddy-command-center.js', 'utf8');
const nav = fs.readFileSync('website/nav.js', 'utf8');
const index = JSON.parse(fs.readFileSync('website/data/command-center/index.json', 'utf8'));

test('command center route is navigable and loads generated JSON', () => {
  assert.match(nav, /buddy-command-center\.html/);
  assert.match(html, /id="cc-metrics"/);
  assert.match(html, /id="cc-data-status"/);
  assert.match(script, /data\/command-center\/index\.json/);
  assert.match(script, /data\/command-center\/capabilities\.json/);
  assert.equal(index.schema, 'dreamco.command_center.index.v1');
  assert.ok(index.summary.bots > 0);
  assert.ok(index.summary.divisions > 0);
});

test('every command center button has a real event handler', () => {
  const buttonIds = [...html.matchAll(/<button[^>]+id="([^"]+)"/g)].map(match => match[1]);
  assert.ok(buttonIds.length >= 5);
  for (const id of buttonIds) {
    assert.match(script, new RegExp(`\\$\\('${id.replace(/[.*+?^${}()|[\\]\\\\]/g, '\\$&')}'\\)\\.addEventListener`), `missing handler for ${id}`);
  }
});

test('deployment truth is explicit', () => {
  assert.match(html, /Real code execution happens only through an explicitly configured local runner/);
  assert.match(script, /Production readiness remains evidence-gated/);
});
