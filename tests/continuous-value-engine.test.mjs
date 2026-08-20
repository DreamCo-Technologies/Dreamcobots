import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';

const root = new URL('../', import.meta.url);
const read = p => readFileSync(new URL(p, root), 'utf8');

test('continuous value registry has persistent discovery loop', () => {
  const data = JSON.parse(read('website/data/buddy-continuous-value-engine.json'));
  assert.deepEqual(data.loop, ['observe','discover','classify','score','research','compare','validate','prototype','test','measure','learn','rerank','repeat']);
  assert.deepEqual(data.value_paths, ['earn','save','build','invent','improve','multiply']);
  assert.equal(data.always_truthful, true);
  assert.equal(data.never_treat_predictions_as_observed_results, true);
  assert.equal(data.requires_authorization_for_consequential_actions, true);
});

test('continuous value documentation defines business and invention paths', () => {
  const doc = read('docs/BUDDY_CONTINUOUS_VALUE_ENGINE.md');
  assert.match(doc, /Business builder pipeline/);
  assert.match(doc, /Invention pipeline/);
  assert.match(doc, /Productivity-to-income engine/);
  assert.match(doc, /Evidence ladder/);
  assert.match(doc, /Autonomy and safety/);
});

test('actions page exposes continuous value controls', () => {
  const html = read('website/actions.html');
  for (const label of ['Continuous Opportunity Scan','Problem → Business','Invention Lab','Productivity → Income','Failure Recovery','Scale What Works']) assert.match(html, new RegExp(label.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')));
  assert.match(html, /continuous-value-center\.css/);
});
