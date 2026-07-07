#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');

const ROOT = process.cwd();
const STRICT = process.argv.includes('--strict');
const REPORT_DIR = path.join(ROOT, 'reports');
const JSON_REPORT = path.join(REPORT_DIR, 'sandbox-hallucination-audit.json');
const MD_REPORT = path.join(REPORT_DIR, 'sandbox-hallucination-audit.md');

const IGNORE_DIRS = new Set([
  '.git',
  '.cache',
  '.next',
  '.pnpm-store',
  '.turbo',
  'build',
  'coverage',
  'dist',
  'node_modules',
  'reports',
]);

const TEXT_EXTENSIONS = new Set([
  '.js', '.cjs', '.mjs', '.ts', '.tsx', '.jsx', '.py', '.md', '.json', '.yml', '.yaml', '.txt', '.toml', '.env', '.example',
]);

const HALLUCINATION_PATTERNS = [
  /\ball bots (are )?(running|working|live|green)\b/i,
  /\bno bugs\b/i,
  /\bzero bugs\b/i,
  /\bfully debugged\b/i,
  /\b100% (working|complete|fixed|production ready)\b/i,
  /\bguaranteed\b/i,
  /\bbulletproof\b/i,
  /\bproduction ready\b/i,
  /\bchatgpt approved\b/i,
];

const REQUIRED_EVIDENCE_FILES = [
  'automation-tools/agents/dreamco-missing-files-scan.js',
  'automation-tools/agents/dependency-audit.js',
  'automation-tools/agents/repair-bot-metadata.js',
  'automation-tools/agents/buddy-connectivity-test.js',
  'automation-tools/agents/sandbox-hallucination-audit.js',
  '.github/workflows/bot-health-scan.yml',
  '.github/workflows/buddy-connectivity.yml',
  '.github/workflows/dreamco-debug-audit.yml',
  'dreamco-control-tower/frontend/src/components/ActionsPage.jsx',
  'dreamco-control-tower/frontend/src/components/__tests__/ActionsPage.test.jsx',
  'dreamco-control-tower/frontend/src/data/githubActionsButtonCatalog.js',
];

function exists(relativePath) {
  return fs.existsSync(path.join(ROOT, relativePath));
}

function isDirectory(fullPath) {
  return fs.existsSync(fullPath) && fs.statSync(fullPath).isDirectory();
}

function walk(dir, files = []) {
  if (!isDirectory(dir)) return files;

  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (IGNORE_DIRS.has(entry.name)) continue;
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      walk(fullPath, files);
    } else {
      files.push(fullPath);
    }
  }

  return files;
}

function relative(fullPath) {
  return path.relative(ROOT, fullPath);
}

function run(command, args) {
  const result = spawnSync(command, args, {
    cwd: ROOT,
    encoding: 'utf8',
    env: { ...process.env, CI: 'true' },
  });

  return {
    command: [command, ...args].join(' '),
    ok: result.status === 0,
    status: result.status,
    stdout: (result.stdout || '').trim().slice(0, 4000),
    stderr: (result.stderr || '').trim().slice(0, 4000),
  };
}

function checkJson(files) {
  const results = [];
  for (const file of files.filter((item) => path.extname(item) === '.json')) {
    try {
      JSON.parse(fs.readFileSync(file, 'utf8'));
      results.push({ file: relative(file), ok: true });
    } catch (error) {
      results.push({ file: relative(file), ok: false, error: error.message });
    }
  }
  return results;
}

function checkJavaScript(files) {
  const extensions = new Set(['.js', '.cjs', '.mjs']);
  const results = [];
  for (const file of files.filter((item) => extensions.has(path.extname(item)))) {
    const result = run(process.execPath, ['--check', file]);
    results.push({ file: relative(file), ok: result.ok, stderr: result.stderr });
  }
  return results;
}

function checkPython(files) {
  const pythonFiles = files.filter((item) => path.extname(item) === '.py');
  if (pythonFiles.length === 0) return { available: true, results: [] };

  const probe = run('python3', ['--version']);
  if (!probe.ok) {
    return {
      available: false,
      results: pythonFiles.map((file) => ({ file: relative(file), ok: null, skipped: 'python3 unavailable' })),
    };
  }

  const results = pythonFiles.map((file) => {
    const result = run('python3', ['-m', 'py_compile', file]);
    return { file: relative(file), ok: result.ok, stderr: result.stderr };
  });

  return { available: true, results };
}

function scanUnsupportedClaims(files) {
  const warnings = [];
  const textFiles = files.filter((file) => TEXT_EXTENSIONS.has(path.extname(file)));

  for (const file of textFiles) {
    const text = fs.readFileSync(file, 'utf8');
    const lines = text.split(/\r?\n/);
    lines.forEach((line, index) => {
      for (const pattern of HALLUCINATION_PATTERNS) {
        if (pattern.test(line)) {
          warnings.push({
            file: relative(file),
            line: index + 1,
            phrase: line.trim().slice(0, 220),
            rule: pattern.toString(),
            guidance: 'Replace absolute success claims with measured evidence, command output, report links, or a clear remaining-risk note.',
          });
          break;
        }
      }
    });
  }

  return warnings;
}

function checkEvidenceFiles() {
  return REQUIRED_EVIDENCE_FILES.map((file) => ({ file, ok: exists(file) }));
}

function checkActionsPageEvidence() {
  const file = 'dreamco-control-tower/frontend/src/components/ActionsPage.jsx';
  const testFile = 'dreamco-control-tower/frontend/src/components/__tests__/ActionsPage.test.jsx';
  const page = exists(file) ? fs.readFileSync(path.join(ROOT, file), 'utf8') : '';
  const tests = exists(testFile) ? fs.readFileSync(path.join(ROOT, testFile), 'utf8') : '';

  return [
    { name: 'Actions page has Agents section', ok: page.includes('Agents Section') },
    { name: 'Actions page has Issues section', ok: page.includes('Issues Section') },
    { name: 'Selected workflow renders from state', ok: page.includes('{selectedAction.workflow}') && page.includes('<code') },
    { name: 'Actions page tests cover 500 catalog', ok: tests.includes('toHaveLength(500)') },
    { name: 'Actions page tests cover agent issue state', ok: tests.includes('2 completed') && tests.includes('3 open') },
  ];
}

function summarizeChecks(name, results) {
  const failed = results.filter((item) => item.ok === false);
  return { name, total: results.length, failed: failed.length, passed: results.length - failed.length, failedItems: failed.slice(0, 100) };
}

function writeReports(report) {
  fs.mkdirSync(REPORT_DIR, { recursive: true });
  fs.writeFileSync(JSON_REPORT, `${JSON.stringify(report, null, 2)}\n`);

  const lines = [
    '# DreamCo Sandbox Hallucination Audit',
    '',
    `Generated: ${report.generatedAt}`,
    '',
    `- Critical failures: ${report.criticalFailures}`,
    `- Unsupported claim warnings: ${report.unsupportedClaimWarnings.length}`,
    `- Strict mode: ${report.strict}`,
    '',
    '## Evidence Checks',
    '',
  ];

  for (const check of report.checks) {
    lines.push(`- ${check.name}: ${check.passed}/${check.total} passed, ${check.failed} failed`);
  }

  lines.push('', '## Unsupported Claim Warnings', '');
  if (report.unsupportedClaimWarnings.length === 0) {
    lines.push('- No unsupported absolute success claims found.');
  } else {
    for (const warning of report.unsupportedClaimWarnings.slice(0, 100)) {
      lines.push(`- ${warning.file}:${warning.line} - ${warning.phrase}`);
    }
  }

  lines.push('', '## Sandbox Rule', '');
  lines.push('- Bots may only claim a task passed when this audit or another named command produced evidence.');
  lines.push('- Bots must report remaining open issues instead of saying everything is fixed.');
  lines.push('- Web, money, write, and deployment actions require explicit tool permission and audit logs.');

  fs.writeFileSync(MD_REPORT, `${lines.join('\n')}\n`);
}

const allFiles = walk(ROOT);
const jsonResults = checkJson(allFiles);
const jsResults = checkJavaScript(allFiles);
const pythonResults = checkPython(allFiles);
const evidenceResults = checkEvidenceFiles();
const actionsPageResults = checkActionsPageEvidence();
const unsupportedClaimWarnings = scanUnsupportedClaims(allFiles);

const checks = [
  summarizeChecks('JSON parse checks', jsonResults),
  summarizeChecks('JavaScript syntax checks', jsResults),
  summarizeChecks('Python syntax checks', pythonResults.results),
  summarizeChecks('Required evidence files', evidenceResults),
  summarizeChecks('Actions/Agents/Issues evidence', actionsPageResults),
];

const criticalFailures = checks.reduce((sum, check) => sum + check.failed, 0);
const report = {
  generatedAt: new Date().toISOString(),
  strict: STRICT,
  criticalFailures,
  unsupportedClaimWarnings,
  pythonAvailable: pythonResults.available,
  checks,
};

writeReports(report);

console.log(`DreamCo sandbox hallucination audit complete: ${criticalFailures} critical failures, ${unsupportedClaimWarnings.length} unsupported-claim warnings.`);
console.log(`Reports written to ${path.relative(ROOT, JSON_REPORT)} and ${path.relative(ROOT, MD_REPORT)}.`);

if (criticalFailures > 0 || (STRICT && unsupportedClaimWarnings.length > 0)) {
  process.exitCode = 1;
}
