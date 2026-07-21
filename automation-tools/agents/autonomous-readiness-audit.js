#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const ROOT = process.cwd();
const STRICT = process.argv.includes('--strict');
const REPORT_DIR = path.join(ROOT, 'reports');
const REPORT_JSON = path.join(REPORT_DIR, 'autonomous-readiness-report.json');
const REPORT_MD = path.join(REPORT_DIR, 'autonomous-readiness-report.md');

const REQUIRED_FILES = [
  'config/autonomous_business_engine.json',
  'config/social_connectors.template.json',
  'config/occupational_bot_registry.json',
  'config/tool_skill_discovery.json',
  'config/buddy-mcp-tool-registry.json',
  'config/buddy-model-router.json',
  'dreamco-control-tower/frontend/src/components/BuddyCommandCenter.jsx',
  'dreamco-control-tower/frontend/src/components/ActionsPage.jsx',
  'docs/BUDDY_LOCAL_CHAT_AND_AUTONOMOUS_OPS.md'
];

function exists(file) {
  return fs.existsSync(path.join(ROOT, file));
}

function readJson(file) {
  try {
    return JSON.parse(fs.readFileSync(path.join(ROOT, file), 'utf8'));
  } catch (error) {
    return null;
  }
}

function fileCheck(file) {
  return { name: file, ok: exists(file), type: 'file' };
}

function jsonCheck(name, file, predicate) {
  const value = readJson(file);
  let ok = false;
  try {
    ok = Boolean(value && predicate(value));
  } catch (error) {
    ok = false;
  }
  return { name, ok, type: 'json', file };
}

const checks = [
  ...REQUIRED_FILES.map(fileCheck),
  jsonCheck('cash loop has customer validation and KPI review', 'config/autonomous_business_engine.json', (value) => value.cashLoop.steps.includes('validate_with_real_customer') && value.cashLoop.steps.includes('measure_kpis')),
  jsonCheck('cash loop gates customer contact and money movement', 'config/autonomous_business_engine.json', (value) => value.cashLoop.approvalRequiredBefore.includes('contacting_customer') && value.cashLoop.approvalRequiredBefore.includes('moving_money')),
  jsonCheck('social connectors default to draft-only', 'config/social_connectors.template.json', (value) => value.defaultPostingMode === 'draft_only'),
  jsonCheck('occupational registry has worker bot families', 'config/occupational_bot_registry.json', (value) => Array.isArray(value.jobFamilies) && value.jobFamilies.length >= 6),
  jsonCheck('tool discovery includes GitHub and Wikipedia', 'config/tool_skill_discovery.json', (value) => value.sources.some((source) => source.id === 'github') && value.sources.some((source) => source.id === 'wikipedia')),
  jsonCheck('tool discovery rejects unsourced memory', 'config/tool_skill_discovery.json', (value) => value.memoryPolicy.rejectIfMissingSource === true),
];

const passed = checks.filter((check) => check.ok).length;
const failed = checks.length - passed;
const report = { generatedAt: new Date().toISOString(), strict: STRICT, passed, failed, checks };

fs.mkdirSync(REPORT_DIR, { recursive: true });
fs.writeFileSync(REPORT_JSON, `${JSON.stringify(report, null, 2)}\n`);

const lines = [
  '# DreamCo Autonomous Readiness Report',
  '',
  `Generated: ${report.generatedAt}`,
  '',
  `- Passed: ${passed}`,
  `- Failed: ${failed}`,
  '',
  '| Check | Status | Type |',
  '| --- | --- | --- |',
];
for (const check of checks) {
  lines.push(`| ${check.name} | ${check.ok ? 'pass' : 'fail'} | ${check.type} |`);
}
fs.writeFileSync(REPORT_MD, `${lines.join('\n')}\n`);

console.log(`DreamCo autonomous readiness audit complete: ${passed} passed, ${failed} failed.`);
console.log(`Reports written to ${path.relative(ROOT, REPORT_JSON)} and ${path.relative(ROOT, REPORT_MD)}.`);

if (failed > 0 || (STRICT && failed > 0)) {
  process.exitCode = 1;
}
