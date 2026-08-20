import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';

const goals = JSON.parse(readFileSync(new URL('../website/data/buddy-agi-actions-goals.json', import.meta.url), 'utf8'));
const html = readFileSync(new URL('../website/actions.html', import.meta.url), 'utf8');

test('Buddy mission registry covers core capability domains', () => {
  const ids = new Set(goals.goals.map((goal) => goal.id));
  for (const id of ['reasoning','agent-routing','coding','ci','benchmarks','learning','knowledge','memory','multimodal','navigation','business','devices','developer','security','ux','observability','release','professional-network','creative','governance']) {
    assert.ok(ids.has(id), `missing mission goal: ${id}`);
  }
  assert.equal(goals.maturity.length, 5);
  assert.match(goals.mastery_rule, /repeated task-relevant evidence/i);
});

test('Actions page loads the mission registry and specialist workbench', () => {
  assert.match(html, /data\/buddy-agi-actions-goals\.json/);
  assert.match(html, /agi-actions\.js/);
  assert.match(html, /agent-workbench\.js/);
  assert.match(html, /Best specialist for every step/);
});
