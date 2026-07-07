#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const ROOT = process.cwd();
const STRICT = process.argv.includes('--strict');
const REPORT_DIR = path.join(ROOT, 'reports');
const JSON_REPORT = path.join(REPORT_DIR, 'issue-goal-coverage.json');
const MD_REPORT = path.join(REPORT_DIR, 'issue-goal-coverage.md');

const GOAL_GROUPS = [
  {
    issue: '#428 Massive update',
    goal: '45 living division registry and dynamic home-screen source',
    requiredFiles: ['config/divisions.json'],
    requiredChecks: [
      {
        name: 'divisions registry has 45 divisions',
        check: () => {
          const divisions = readJson('config/divisions.json');
          return Array.isArray(divisions?.divisions) && divisions.divisions.length >= 45;
        },
      },
      {
        name: 'division routes are configured',
        check: () => {
          const divisions = readJson('config/divisions.json');
          return Array.isArray(divisions?.divisions) && divisions.divisions.every((item) => item.id && item.name && item.route);
        },
      },
    ],
  },
  {
    issue: '#428 Massive update',
    goal: 'configuration-as-code for scaling, upgrades, thresholds, queues, and feature flags',
    requiredFiles: [
      'config/divisions.json',
      'config/bot_registry.json',
      'config/scaling.yaml',
      'config/upgrade_rules.yaml',
      'config/thresholds.yaml',
      'config/task_queues.yaml',
      'config/feature_flags.yaml',
    ],
  },
  {
    issue: '#428 Massive update',
    goal: 'central bot registry with health/version/capability metadata',
    requiredFiles: ['registry/bots.json', 'config/bot_registry.json'],
    requiredChecks: [
      {
        name: 'registry has Buddy and DreamAgents entries',
        check: () => {
          const registry = readJson('registry/bots.json');
          return Boolean(registry?.bots?.DreamBuddy && registry?.bots?.DreamAgentsRegistry);
        },
      },
    ],
  },
  {
    issue: '#428 Massive update',
    goal: 'self-healing Kubernetes runtime manifests',
    requiredFiles: [
      'kubernetes/deployment.yaml',
      'kubernetes/service.yaml',
      'kubernetes/hpa.yaml',
      'kubernetes/keda-scaledobject.yaml',
      'kubernetes/networkpolicy.yaml',
      'kubernetes/poddisruptionbudget.yaml',
    ],
  },
  {
    issue: '#428 Massive update',
    goal: 'automated rollout and rollback definitions',
    requiredFiles: [
      'argo/rollout.yaml',
      'argo/analysis-template.yaml',
      'argo/rollback-policy.yaml',
      'helm/dreamco/Chart.yaml',
      'helm/dreamco/values.yaml',
    ],
  },
  {
    issue: '#428, #126, #123, #118, #115, #113',
    goal: 'continuous self-build and audit workflow',
    requiredFiles: [
      '.github/workflows/dreamco-debug-audit.yml',
      '.github/workflows/dreamco-continuous-self-build.yml',
      'automation-tools/agents/sandbox-hallucination-audit.js',
      'automation-tools/agents/issue-goal-coverage.js',
    ],
  },
  {
    issue: '#427, #426',
    goal: 'Buddy model routing and coding-agent governance',
    requiredFiles: ['config/buddy-model-router.json', 'config/buddy-mcp-tool-registry.json'],
  },
  {
    issue: '#425, #117, #116',
    goal: 'lead, sales, and revenue tracking foundation',
    requiredFiles: [
      'data/sales/sales-bot-team.json',
      'data/sales/client-tracking.schema.json',
      'stripe/node/revenue-ledger.js',
      'docs/SALES_REP_BOT_TEAM.md',
      'docs/STRIPE_REVENUE_TRACKING_SYSTEM.md',
    ],
  },
];

function exists(relativePath) {
  return fs.existsSync(path.join(ROOT, relativePath));
}

function readJson(relativePath) {
  try {
    return JSON.parse(fs.readFileSync(path.join(ROOT, relativePath), 'utf8'));
  } catch (error) {
    return null;
  }
}

function evaluateGroup(group) {
  const fileChecks = group.requiredFiles.map((file) => ({ name: file, ok: exists(file), type: 'file' }));
  const customChecks = (group.requiredChecks || []).map((check) => {
    let ok = false;
    try {
      ok = Boolean(check.check());
    } catch (error) {
      ok = false;
    }
    return { name: check.name, ok, type: 'logic' };
  });
  const checks = [...fileChecks, ...customChecks];
  const missing = checks.filter((check) => !check.ok);
  return {
    issue: group.issue,
    goal: group.goal,
    status: missing.length === 0 ? 'covered' : 'missing',
    totalChecks: checks.length,
    passedChecks: checks.length - missing.length,
    missing,
  };
}

function writeReports(results) {
  fs.mkdirSync(REPORT_DIR, { recursive: true });
  const missingGoals = results.filter((item) => item.status !== 'covered');
  const report = {
    generatedAt: new Date().toISOString(),
    strict: STRICT,
    totalGoals: results.length,
    coveredGoals: results.length - missingGoals.length,
    missingGoals: missingGoals.length,
    results,
  };

  fs.writeFileSync(JSON_REPORT, `${JSON.stringify(report, null, 2)}\n`);

  const lines = [
    '# DreamCo Issue Goal Coverage',
    '',
    `Generated: ${report.generatedAt}`,
    '',
    `- Covered goals: ${report.coveredGoals}/${report.totalGoals}`,
    `- Missing goals: ${report.missingGoals}`,
    '',
    '| Issue | Goal | Status | Evidence |',
    '| --- | --- | --- | --- |',
  ];

  for (const result of results) {
    const missing = result.missing.map((item) => item.name).join(', ');
    const evidence = result.status === 'covered' ? `${result.passedChecks}/${result.totalChecks} checks passed` : `Missing: ${missing}`;
    lines.push(`| ${result.issue} | ${result.goal} | ${result.status} | ${evidence} |`);
  }

  fs.writeFileSync(MD_REPORT, `${lines.join('\n')}\n`);
  return report;
}

const results = GOAL_GROUPS.map(evaluateGroup);
const report = writeReports(results);

console.log(`DreamCo issue goal coverage complete: ${report.coveredGoals}/${report.totalGoals} goals covered.`);
console.log(`Reports written to ${path.relative(ROOT, JSON_REPORT)} and ${path.relative(ROOT, MD_REPORT)}.`);

if (STRICT && report.missingGoals > 0) {
  process.exitCode = 1;
}
