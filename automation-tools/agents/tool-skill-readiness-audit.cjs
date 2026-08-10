#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const ROOT = process.cwd();
const STRICT = process.argv.includes('--strict');
const REPORT_DIR = path.join(ROOT, 'reports');
const REPORT_JSON = path.join(REPORT_DIR, 'tool-skill-readiness-report.json');
const REPORT_MD = path.join(REPORT_DIR, 'tool-skill-readiness-report.md');
const CATALOG_PATH = path.join(ROOT, 'config', 'buddy_tool_skill_catalog.json');

function readJson(filePath) {
  try {
    return JSON.parse(fs.readFileSync(filePath, 'utf8'));
  } catch (error) {
    return null;
  }
}

function hasText(value) {
  return typeof value === 'string' && value.trim().length > 0;
}

function validateItem(item, type) {
  const checks = [
    { name: 'has id', ok: hasText(item.id) },
    { name: 'has name', ok: hasText(item.name) },
    { name: 'states whether needed', ok: typeof item.needed === 'boolean' },
    { name: 'explains what it does', ok: hasText(item.whatItDoes) },
    { name: 'explains how to use it', ok: hasText(item.howToUse) },
    { name: 'has test command', ok: hasText(item.testCommand) },
  ];

  return {
    id: item.id || 'missing-id',
    type,
    ok: checks.every((check) => check.ok),
    checks,
  };
}

const catalog = readJson(CATALOG_PATH);
const results = [];

if (catalog) {
  for (const tool of catalog.tools || []) {
    results.push(validateItem(tool, 'tool'));
  }
  for (const skill of catalog.skills || []) {
    results.push(validateItem(skill, 'skill'));
  }
}

const approvalList = catalog?.evidencePolicy?.approvalRequiredFor || [];
const requiredApprovals = [
  'posting_to_social_media',
  'contacting_customers',
  'spending_money',
  'moving_money',
  'installing_dependencies',
  'publishing_code',
  'training_external_model_with_private_data',
];

const requiredTopLevelChecks = [
  { name: 'catalog exists', ok: Boolean(catalog) },
  { name: 'catalog has evidence policy', ok: Boolean(catalog?.evidencePolicy?.noHallucinationRule) },
  { name: 'catalog has at least 10 tools', ok: (catalog?.tools || []).length >= 10 },
  { name: 'catalog has at least 5 skills', ok: (catalog?.skills || []).length >= 5 },
  {
    name: 'catalog protects social/customer/money/code/model-training actions',
    ok: requiredApprovals.every((approval) => approvalList.includes(approval)),
  },
];

const riskyItems = [...(catalog?.tools || []), ...(catalog?.skills || [])].filter((item) => {
  const text = `${item.id || ''} ${item.name || ''} ${item.whatItDoes || ''} ${item.howToUse || ''}`.toLowerCase();
  return ['social', 'customer', 'money', 'publishing', 'training external model', 'private data'].some((word) => text.includes(word));
});

const riskyItemChecks = riskyItems.map((item) => ({
  name: `${item.id || item.name} has approval/evidence guard`,
  ok: item.requiresApproval === true || /approval|required|draft-only|approved|safe data|not include secrets/i.test(item.howToUse || ''),
}));

const failedItems = results.filter((item) => !item.ok);
const failedTopLevelChecks = [...requiredTopLevelChecks, ...riskyItemChecks].filter((check) => !check.ok);
const passed = results.length - failedItems.length + requiredTopLevelChecks.length + riskyItemChecks.length - failedTopLevelChecks.length;
const failed = failedItems.length + failedTopLevelChecks.length;

const report = {
  generatedAt: new Date().toISOString(),
  strict: STRICT,
  passed,
  failed,
  topLevelChecks: requiredTopLevelChecks,
  riskyItemChecks,
  itemResults: results,
};

fs.mkdirSync(REPORT_DIR, { recursive: true });
fs.writeFileSync(REPORT_JSON, `${JSON.stringify(report, null, 2)}\n`);

const lines = [
  '# DreamCo Tool and Skill Readiness Report',
  '',
  `Generated: ${report.generatedAt}`,
  '',
  `- Passed checks/items: ${passed}`,
  `- Failed checks/items: ${failed}`,
  '',
  '## Top-Level Checks',
  '',
  '| Check | Status |',
  '| --- | --- |',
];

for (const check of requiredTopLevelChecks) {
  lines.push(`| ${check.name} | ${check.ok ? 'pass' : 'fail'} |`);
}

lines.push('', '## Risk Guards', '', '| Check | Status |', '| --- | --- |');
for (const check of riskyItemChecks) {
  lines.push(`| ${check.name} | ${check.ok ? 'pass' : 'fail'} |`);
}

lines.push('', '## Tools and Skills', '', '| Type | ID | Status | Missing |', '| --- | --- | --- | --- |');
for (const item of results) {
  const missing = item.checks.filter((check) => !check.ok).map((check) => check.name).join(', ');
  lines.push(`| ${item.type} | ${item.id} | ${item.ok ? 'pass' : 'fail'} | ${missing || 'none'} |`);
}

lines.push('', '## Buddy Training Rule', '');
lines.push('- Buddy may use these tools and skills to train or evaluate other AI models only with sourced, approved, non-secret data.');
lines.push('- Every handoff must include what the tool does, how to use it, test evidence, source quality, and remaining risks.');
lines.push('- If a tool cannot be tested, Buddy must mark it `not verified` instead of claiming it works.');

fs.writeFileSync(REPORT_MD, `${lines.join('\n')}\n`);

console.log(`DreamCo tool/skill readiness audit complete: ${passed} passed, ${failed} failed.`);
console.log(`Reports written to ${path.relative(ROOT, REPORT_JSON)} and ${path.relative(ROOT, REPORT_MD)}.`);

if (failed > 0) {
  process.exitCode = 1;
}
