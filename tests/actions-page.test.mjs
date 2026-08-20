import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';

const html = readFileSync(new URL('../website/actions.html', import.meta.url), 'utf8');
const source = readFileSync(new URL('../website/actions.js', import.meta.url), 'utf8');
const growthSource = readFileSync(new URL('../website/actions-growth-lab.js', import.meta.url), 'utf8');
const growthCss = readFileSync(new URL('../website/actions-growth-lab.css', import.meta.url), 'utf8');
const missionMap = JSON.parse(readFileSync(new URL('../website/data/buddy-repository-mission-map.json', import.meta.url), 'utf8'));
const missionMapCss = readFileSync(new URL('../website/agi-repository-map.css', import.meta.url), 'utf8');
const commandCss = readFileSync(new URL('../website/actions-command-center.css', import.meta.url), 'utf8');
const browserCheck = readFileSync(new URL('../tools/verify_actions_page_browser.mjs', import.meta.url), 'utf8');
const agentSource = readFileSync(new URL('../website/agent-workbench.js', import.meta.url), 'utf8');
const agiSource = readFileSync(new URL('../website/agi-actions.js', import.meta.url), 'utf8');
const agents = JSON.parse(readFileSync(new URL('../website/data/buddy-actions-agent-workbench.json', import.meta.url), 'utf8'));
const goals = JSON.parse(readFileSync(new URL('../website/data/buddy-agi-actions-goals.json', import.meta.url), 'utf8'));
const nav = readFileSync(new URL('../website/nav.js', import.meta.url), 'utf8');
const worker = readFileSync(new URL('../website/service-worker.js', import.meta.url), 'utf8');
const report = JSON.parse(readFileSync(new URL('../website/data/actions-health-report.json', import.meta.url), 'utf8'));

test('Actions page exposes mission control, filters, prospectuses and safe GitHub handoff', () => {
  assert.match(html, /AGI Mission Control/);
  assert.match(html, /actions-command-center\.css/);
  assert.match(html, /actions-growth-lab\.css/);
  assert.match(html, /agi-repository-map\.css/);
  assert.match(html, /id="agi-goals-grid"/);
  assert.match(html, /id="agi-mastery-rule"/);
  assert.match(html, /id="workflow-list"/);
  assert.match(html, /id="agent-workbench"/);
  assert.match(html, /agi-actions\.js/);
  assert.match(html, /actions-growth-lab\.js/);
  assert.match(source, /api\.github\.com\/repos\/\$\{REPOSITORY\}\/actions\/runs/);
  assert.match(source, /ensureShell\(\)/);
  assert.match(source, /Safe boundary: browser actions do not execute arbitrary shell commands/);
  assert.match(html, /Download Buddy/);
});

test('Command center has searchable status and trigger filters plus detail dialog', () => {
  assert.match(source, /actions-search/);
  assert.match(source, /actions-status-filter/);
  assert.match(source, /actions-trigger-filter/);
  assert.match(source, /workflow-detail/);
  assert.match(source, /actions-control-cards/);
  assert.match(commandCss, /actions-filter-bar/);
  assert.match(commandCss, /workflow-detail-dialog/);
});

test('Growth lab connects learning, writing, evaluation, recovery and engineering controls', () => {
  assert.match(growthSource, /buddy-original-writing-manifest\.json/);
  assert.match(growthSource, /buddy-knowledge-synthesis-actions\.json/);
  assert.match(growthSource, /buddy-adaptive-curriculum-actions\.json/);
  assert.match(growthSource, /buddy-learning-economics-actions\.json/);
  assert.match(growthSource, /buddy-learning-memory-actions\.json/);
  assert.match(growthSource, /buddy-mastery-ledger-actions\.json/);
  assert.match(growthSource, /buddy-parenting-principles-actions\.json/);
  assert.match(growthSource, /best specialist for each step/);
  assert.match(growthCss, /buddy-growth-groups/);
});

test('Repository mission map contains the accumulated Buddy goal surface', () => {
  assert.ok(missionMap.categories.length >= 15);
  const total = missionMap.categories.reduce((n, category) => n + category.goals.length, 0);
  assert.ok(total >= 250);
  for (const id of ['core-intelligence','engineering','learning','benchmarks','agents','navigation','devices','commerce','real-estate','professional-network','creative','developer-experience','observability','security-governance','memory-data','distribution','agi-research','maturity']) {
    assert.ok(missionMap.categories.some((category) => category.id === id), id);
  }
  assert.equal(missionMap.dashboard_policy.unknown_is_not_success, true);
  assert.equal(missionMap.dashboard_policy.mastered_requires_repeatable_evidence, true);
  assert.match(agiSource, /buddy-repository-mission-map\.json/);
  assert.match(missionMapCss, /agi-repository-category-grid/);
});

test('All 16 specialist roles remain represented', () => {
  assert.equal(agents.agents.length, 16);
  for (const agent of agents.agents) assert.ok(agent.name && agent.purpose && agent.primary_action && agent.success);
  assert.match(agentSource, /re-evaluates when the task changes/);
  assert.match(agentSource, /exact-task benchmark evidence/);
});

test('Mission registry contains broad capability goals and honest mastery policy', () => {
  assert.ok(goals.goals.length >= 20);
  for (const id of ['agent-routing','benchmarks','navigation','devices','security']) assert.ok(goals.goals.some((g) => g.id === id));
  assert.match(goals.mastery_rule, /not labeled Mastered/i);
  assert.match(agiSource, /exact step/);
});

test('Every workflow has three upgrades and a workflow-specific GitHub URL', () => {
  assert.equal(report.findings.length, report.workflow_count);
  assert.equal(report.critical_error_count, 0);
  for (const workflow of report.findings) { assert.equal(workflow.upgrades.length, 3, workflow.filename); assert.ok(workflow.github_url.endsWith(workflow.filename)); }
});

test('Browser verification matches the current AGI Mission Control contract', () => {
  assert.match(browserCheck, /AGI Mission Control/);
  assert.match(browserCheck, /prospectus controls/);
  assert.match(browserCheck, /horizontal overflow/);
  assert.match(browserCheck, /browser console/);
});

test('Actions remains linked and cached in the GitHub Pages shell', () => {
  assert.match(nav, /actions\.html/);
  assert.match(worker, /\.\/actions\.html/);
  assert.match(worker, /\.\/data\/actions-health-report\.json/);
});