import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';

const html = readFileSync(new URL('../website/actions.html', import.meta.url), 'utf8');
const source = readFileSync(new URL('../website/actions.js', import.meta.url), 'utf8');
const agentSource = readFileSync(new URL('../website/agent-workbench.js', import.meta.url), 'utf8');
const agiSource = readFileSync(new URL('../website/agi-actions.js', import.meta.url), 'utf8');
const agents = JSON.parse(readFileSync(new URL('../website/data/buddy-actions-agent-workbench.json', import.meta.url), 'utf8'));
const goals = JSON.parse(readFileSync(new URL('../website/data/buddy-agi-actions-goals.json', import.meta.url), 'utf8'));
const nav = readFileSync(new URL('../website/nav.js', import.meta.url), 'utf8');
const worker = readFileSync(new URL('../website/service-worker.js', import.meta.url), 'utf8');
const report = JSON.parse(readFileSync(new URL('../website/data/actions-health-report.json', import.meta.url), 'utf8'));

test('Actions page exposes mission control and safe GitHub handoff', () => {
  assert.match(html, /AGI Mission Control/);
  assert.match(html, /id="agi-goals-grid"/);
  assert.match(html, /id="agi-mastery-rule"/);
  assert.match(html, /id="workflow-list"/);
  assert.match(html, /id="agent-workbench"/);
  assert.match(html, /agi-actions\.js/);
  assert.match(source, /api\.github\.com\/repos\/\$\{REPOSITORY\}\/actions\/runs/);
  assert.match(html, /Download Buddy/);
});

test('All 16 specialist roles remain represented', () => {
  assert.equal(agents.agents.length, 16);
  for (const agent of agents.agents) {
    assert.ok(agent.name && agent.purpose && agent.primary_action && agent.success);
  }
  assert.match(agentSource, /re-evaluates when the task changes/);
  assert.match(agentSource, /exact-task benchmark evidence/);
});

test('Mission registry contains broad capability goals and honest mastery policy', () => {
  assert.ok(goals.goals.length >= 20);
  assert.ok(goals.goals.some((g) => g.id === 'agent-routing'));
  assert.ok(goals.goals.some((g) => g.id === 'benchmarks'));
  assert.ok(goals.goals.some((g) => g.id === 'navigation'));
  assert.ok(goals.goals.some((g) => g.id === 'devices'));
  assert.ok(goals.goals.some((g) => g.id === 'security'));
  assert.match(goals.mastery_rule, /not labeled Mastered/i);
  assert.match(agiSource, /exact step/);
});

test('Every workflow has three upgrades and a workflow-specific GitHub URL', () => {
  assert.equal(report.findings.length, report.workflow_count);
  assert.equal(report.critical_error_count, 0);
  for (const workflow of report.findings) {
    assert.equal(workflow.upgrades.length, 3, workflow.filename);
    assert.ok(workflow.github_url.endsWith(workflow.filename));
  }
});

test('Actions remains linked and cached in the GitHub Pages shell', () => {
  assert.match(nav, /actions\.html/);
  assert.match(worker, /\.\/actions\.html/);
  assert.match(worker, /\.\/data\/actions-health-report\.json/);
});
