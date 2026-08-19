import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';

const html = readFileSync(new URL('../website/actions.html', import.meta.url), 'utf8');
const source = readFileSync(new URL('../website/actions.js', import.meta.url), 'utf8');
const agentSource = readFileSync(new URL('../website/agent-workbench.js', import.meta.url), 'utf8');
const agents = JSON.parse(readFileSync(new URL('../website/data/buddy-actions-agent-workbench.json', import.meta.url), 'utf8'));
const nav = readFileSync(new URL('../website/nav.js', import.meta.url), 'utf8');
const worker = readFileSync(new URL('../website/service-worker.js', import.meta.url), 'utf8');
const report = JSON.parse(readFileSync(new URL('../website/data/actions-health-report.json', import.meta.url), 'utf8'));

test('Actions page exposes health, filters, upgrades, specialist routing, and safe GitHub handoff', () => {
  assert.match(html, /Actions control room/);
  assert.match(html, /id="workflow-list"/);
  assert.match(html, /id="refresh-actions"/);
  assert.match(html, /id="metric-benchmarks"/);
  assert.match(html, /id="agent-workbench"/);
  assert.match(html, /Choose the right specialist for each step/);
  assert.match(html, /agent-workbench\.js/);
  assert.match(source, /api\.github\.com\/repos\/\$\{REPOSITORY\}\/actions\/runs/);
  assert.match(html, /Plan upgrades with Buddy/);
  assert.match(html, /cannot dispatch a workflow/i);
});

test('All 16 specialist roles have beginner-facing controls and success conditions', () => {
  assert.equal(agents.agents.length, 16);
  for (const agent of agents.agents) {
    assert.ok(agent.name);
    assert.ok(agent.purpose);
    assert.ok(agent.primary_action);
    assert.ok(agent.success);
  }
  assert.match(agentSource, /re-evaluates when the task changes/);
  assert.match(agentSource, /exact-task benchmark evidence/);
});

test('Every workflow has three upgrades and a workflow-specific GitHub URL', () => {
  assert.equal(report.findings.length, report.workflow_count);
  assert.equal(report.critical_error_count, 0);
  for (const workflow of report.findings) {
    assert.equal(workflow.upgrades.length, 3, workflow.filename);
    assert.ok(workflow.github_url.endsWith(workflow.filename));
  }
});

test('Actions is linked and cached in the GitHub Pages shell', () => {
  assert.match(nav, /actions\.html/);
  assert.match(worker, /\.\/actions\.html/);
  assert.match(worker, /\.\/data\/actions-health-report\.json/);
});
