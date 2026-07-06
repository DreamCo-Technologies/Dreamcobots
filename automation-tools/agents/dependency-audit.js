#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const ROOT = process.cwd();
const REPORT_DIR = path.join(ROOT, 'reports');
const JSON_REPORT = path.join(REPORT_DIR, 'dependency-audit-report.json');
const MD_REPORT = path.join(REPORT_DIR, 'dependency-audit-report.md');
const STRICT = process.argv.includes('--strict');

const IGNORE_DIRS = new Set(['.git', 'node_modules', 'dist', 'build', 'coverage', '.cache', '.next']);

function walk(dir, files = []) {
  if (!fs.existsSync(dir)) return files;
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (IGNORE_DIRS.has(entry.name)) continue;
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) walk(full, files);
    else files.push(full);
  }
  return files;
}

function rel(filePath) {
  return path.relative(ROOT, filePath) || '.';
}

function readJson(filePath) {
  try {
    return JSON.parse(fs.readFileSync(filePath, 'utf8'));
  } catch (error) {
    return null;
  }
}

function nearest(fileSet, dir, names) {
  return names
    .filter((name) => fileSet.has(path.join(dir, name)))
    .map((name) => path.join(dir, name));
}

function audit() {
  const allFiles = walk(ROOT);
  const fileSet = new Set(allFiles);
  const issues = [];
  const findings = [];

  const packageFiles = allFiles.filter((file) => path.basename(file) === 'package.json');
  for (const packageFile of packageFiles) {
    const dir = path.dirname(packageFile);
    const pkg = readJson(packageFile);
    const locks = nearest(fileSet, dir, ['package-lock.json', 'pnpm-lock.yaml', 'yarn.lock']);
    findings.push({ type: 'node-package', path: rel(packageFile), lockfiles: locks.map(rel) });

    if (!pkg) issues.push({ path: rel(packageFile), issue: 'Invalid package.json' });
    if (pkg && !pkg.scripts) issues.push({ path: rel(packageFile), issue: 'Missing scripts block' });
    if (pkg && !pkg.dependencies && !pkg.devDependencies && !pkg.peerDependencies) {
      issues.push({ path: rel(packageFile), issue: 'No dependency fields declared' });
    }
    if (!locks.length) issues.push({ path: rel(packageFile), issue: 'No lockfile beside package.json' });
  }

  const pythonFiles = allFiles.filter((file) => ['requirements.txt', 'pyproject.toml', 'Pipfile'].includes(path.basename(file)));
  for (const pythonFile of pythonFiles) {
    findings.push({ type: 'python-dependencies', path: rel(pythonFile) });
    const text = fs.readFileSync(pythonFile, 'utf8').trim();
    if (!text) issues.push({ path: rel(pythonFile), issue: 'Python dependency file is empty' });
  }

  const javaFiles = allFiles.filter((file) => ['pom.xml', 'build.gradle', 'build.gradle.kts', 'settings.gradle', 'settings.gradle.kts'].includes(path.basename(file)));
  for (const javaFile of javaFiles) {
    findings.push({ type: 'jvm-build-file', path: rel(javaFile) });
  }

  if (!fs.existsSync(path.join(ROOT, '.nvmrc')) && !fs.existsSync(path.join(ROOT, '.node-version'))) {
    issues.push({ path: '.', issue: 'Missing root Node version file (.nvmrc or .node-version)' });
  }

  if (!packageFiles.length && !pythonFiles.length && !javaFiles.length) {
    issues.push({ path: '.', issue: 'No dependency files discovered' });
  }

  return {
    generatedAt: new Date().toISOString(),
    summary: {
      nodePackages: packageFiles.length,
      pythonDependencyFiles: pythonFiles.length,
      jvmBuildFiles: javaFiles.length,
      issues: issues.length,
    },
    findings,
    issues,
  };
}

function writeReports(report) {
  fs.mkdirSync(REPORT_DIR, { recursive: true });
  fs.writeFileSync(JSON_REPORT, `${JSON.stringify(report, null, 2)}\n`);

  const lines = [
    '# DreamCo Dependency Audit Report',
    '',
    `Generated: ${report.generatedAt}`,
    '',
    `- Node packages: ${report.summary.nodePackages}`,
    `- Python dependency files: ${report.summary.pythonDependencyFiles}`,
    `- JVM build files: ${report.summary.jvmBuildFiles}`,
    `- Issues: ${report.summary.issues}`,
    '',
    '## Issues',
    '',
  ];

  if (!report.issues.length) lines.push('- No dependency issues detected by this audit.');
  for (const issue of report.issues) lines.push(`- \`${issue.path}\`: ${issue.issue}`);

  lines.push('', '## Findings', '');
  for (const finding of report.findings) {
    const lockInfo = finding.lockfiles ? `; lockfiles: ${finding.lockfiles.map((item) => `\`${item}\``).join(', ') || 'none'}` : '';
    lines.push(`- ${finding.type}: \`${finding.path}\`${lockInfo}`);
  }

  fs.writeFileSync(MD_REPORT, `${lines.join('\n')}\n`);
}

const report = audit();
writeReports(report);
console.log(`DreamCo dependency audit complete: ${report.summary.issues} issues.`);
console.log(`Reports written to ${rel(JSON_REPORT)} and ${rel(MD_REPORT)}.`);

if (STRICT && report.issues.length > 0) {
  process.exitCode = 1;
}
