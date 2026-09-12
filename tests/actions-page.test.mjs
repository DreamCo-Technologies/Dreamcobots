import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';

const html = readFileSync(new URL('../website/actions.html', import.meta.url), 'utf8');
const source = readFileSync(new URL('../website/actions.js', import.meta.url), 'utf8');
const review = readFileSync(new URL('../website/actions-code-review.js', import.meta.url), 'utf8');
const nav = readFileSync(new URL('../website/nav.js', import.meta.url), 'utf8');
const worker = readFileSync(new URL('../website/service-worker.js', import.meta.url), 'utf8');
const report = JSON.parse(readFileSync(new URL('../website/data/actions-health-report.json', import.meta.url), 'utf8'));
const prospectus = JSON.parse(readFileSync(new URL('../website/data/actions-prospectus.json', import.meta.url), 'utf8'));
const repositoryProspectus = JSON.parse(readFileSync(new URL('../config/generated/actions-prospectus.json', import.meta.url), 'utf8'));
const codingGate = JSON.parse(readFileSync(new URL('../config/buddy-coding-mastery-gate.json', import.meta.url), 'utf8'));
const college = JSON.parse(readFileSync(new URL('../config/buddy-college-curriculum.json', import.meta.url), 'utf8'));

test('Actions page exposes health, filters, upgrades, safe GitHub handoff, and code review', () => {
  assert.match(html, /Actions control room/);
  assert.match(html, /id="workflow-list"/);
  assert.match(html, /id="refresh-actions"/);
  assert.match(html, /id="metric-benchmarks"/);
  assert.match(html, /id="metric-duplicates"/);
  assert.match(html, /id="actions-review-pr"/);
  assert.match(html, /Code Review Council/);
  assert.match(html, /Repository stages/);
  assert.match(source, /master-directive-status\.json/);
  assert.match(source, /api\.github\.com\/repos\/\$\{REPOSITORY\}\/actions\/runs/);
  assert.match(review, /heuristic review score/);
  assert.match(review, /secret-like token/);
  assert.match(html, /cannot execute arbitrary shell commands/i);
  assert.match(html, /cannot.*deploy production/i);
});

test('Actions prospectus explains every workflow without turning static checks into runtime proof', () => {
  assert.equal(report.schema, 'dreamco.actions_health.v2');
  assert.equal(prospectus.schema, 'dreamco.actions_prospectus.v2');
  assert.equal(prospectus.workflow_count, report.workflow_count);
  assert.equal(prospectus.workflow_catalog_url, 'data/actions-health-report.json');
  assert.equal(repositoryProspectus.workflows.length, report.workflow_count);
  assert.equal(report.summary.runtime_unknown_workflows, report.workflow_count);
  assert.equal(report.operational_workflow_count, 0);
  for (const workflow of report.findings) {
    assert.ok(workflow.goal.length > 2, workflow.filename);
    assert.ok(workflow.purpose.length > 10, workflow.filename);
    assert.ok(workflow.what_happens.length > 0, workflow.filename);
    assert.ok(workflow.outputs.length > 0, workflow.filename);
    assert.equal(workflow.runtime_status, 'unknown_until_run_evidence_loaded');
    assert.equal(typeof workflow.possible_duplicate, 'boolean');
  }
  assert.match(source, /What happens when it runs/);
  assert.match(source, /Known findings/);
  assert.match(source, /Duplication review/);
  assert.match(source, /Declared benchmark commands/);
});

test('Every workflow has at least three upgrades and a workflow-specific GitHub URL', () => {
  assert.equal(report.findings.length, report.workflow_count);
  assert.equal(report.critical_error_count, 0);
  for (const workflow of report.findings) {
    // The first three upgrades are the stable workflow contract. The health
    // auditor may append evidence-backed maintenance recommendations (for
    // example, an action-major upgrade), so the contract must not reject a
    // useful additional recommendation.
    assert.ok(workflow.upgrades.length >= 3, workflow.filename);
    assert.ok(workflow.github_url.endsWith(workflow.filename));
  }
});

test('Coding mastery gates college curriculum and requires evidence', () => {
  assert.equal(codingGate.promotion.includes('college curriculum'), true);
  assert.equal(codingGate.gate_levels.length >= 4, true);
  assert.equal(codingGate.anti_shortcut_rules.length >= 5, true);
  assert.equal(college.unlock, 'config/buddy-coding-mastery-gate.json');
  assert.equal(college.domains.length >= 15, true);
  assert.equal(college.mastery_rules.never_mark_mastered_from_reading_only, true);
});

test('Actions is linked and cached in the GitHub Pages shell', () => {
  assert.match(nav, /actions\.html/);
  assert.match(worker, /\.\/actions\.html/);
  assert.match(worker, /\.\/data\/actions-health-report\.json/);
});
