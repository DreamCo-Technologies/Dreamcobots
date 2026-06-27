#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const ROOT = process.cwd();
const STRICT = process.argv.includes('--strict');
const REPORT_DIR = path.join(ROOT, 'reports');
const JSON_REPORT = path.join(REPORT_DIR, 'bot-health-report.json');
const MD_REPORT = path.join(REPORT_DIR, 'bot-health-report.md');

const IGNORE_DIRS = new Set([
  '.git',
  'node_modules',
  'dist',
  'build',
  'coverage',
  '.next',
  '.turbo',
  '.cache',
  '.pnpm-store',
]);

const BOT_ROOTS = [
  'bots',
  'python_bots',
  'java_bots',
  'empire-os',
  'integrations',
];

function exists(filePath) {
  return fs.existsSync(filePath);
}

function isDirectory(filePath) {
  return exists(filePath) && fs.statSync(filePath).isDirectory();
}

function readJson(filePath) {
  try {
    return JSON.parse(fs.readFileSync(filePath, 'utf8'));
  } catch (error) {
    return null;
  }
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

function findBotCandidates() {
  const candidates = [];

  for (const rootName of BOT_ROOTS) {
    const rootPath = path.join(ROOT, rootName);
    if (!isDirectory(rootPath)) continue;

    if (rootName === 'python_bots' || rootName === 'java_bots') {
      for (const filePath of walk(rootPath)) {
        const ext = path.extname(filePath);
        if (['.py', '.java', '.kt', '.kts'].includes(ext)) {
          candidates.push({ name: path.basename(filePath, ext), root: rootName, path: filePath, kind: 'single-file-bot' });
        }
      }
      continue;
    }

    for (const entry of fs.readdirSync(rootPath, { withFileTypes: true })) {
      if (!entry.isDirectory() || IGNORE_DIRS.has(entry.name)) continue;
      const botPath = path.join(rootPath, entry.name);
      const files = walk(botPath);
      const hasBotSignal = files.some((filePath) => {
        const base = path.basename(filePath).toLowerCase();
        return base === 'bot.manifest.json'
          || base === 'replit_profile.json'
          || base === 'package.json'
          || base === 'readme.md'
          || /bot|agent|workflow|orchestrator/i.test(filePath);
      });

      if (hasBotSignal) {
        candidates.push({ name: entry.name, root: rootName, path: botPath, kind: 'folder-bot' });
      }
    }
  }

  return candidates;
}

function resolveRelativeImport(fromFile, request) {
  if (!request.startsWith('.')) return true;
  const base = path.resolve(path.dirname(fromFile), request);
  const candidates = [
    base,
    `${base}.js`,
    `${base}.cjs`,
    `${base}.mjs`,
    `${base}.ts`,
    `${base}.tsx`,
    `${base}.json`,
    path.join(base, 'index.js'),
    path.join(base, 'index.ts'),
    path.join(base, 'index.tsx'),
    path.join(base, 'package.json'),
  ];
  return candidates.some(exists);
}

function scanImports(filePath) {
  const ext = path.extname(filePath);
  if (!['.js', '.cjs', '.mjs', '.ts', '.tsx'].includes(ext)) return [];

  const text = fs.readFileSync(filePath, 'utf8');
  const missing = [];
  const patterns = [
    /require\(['"]([^'"]+)['"]\)/g,
    /from\s+['"]([^'"]+)['"]/g,
    /import\(['"]([^'"]+)['"]\)/g,
  ];

  for (const pattern of patterns) {
    let match;
    while ((match = pattern.exec(text)) !== null) {
      const request = match[1];
      if (!resolveRelativeImport(filePath, request)) {
        missing.push({ file: path.relative(ROOT, filePath), import: request });
      }
    }
  }

  return missing;
}

function scanBot(candidate) {
  const issues = [];
  const files = candidate.kind === 'folder-bot' ? walk(candidate.path) : [candidate.path];
  const bases = new Set(files.map((filePath) => path.basename(filePath).toLowerCase()));

  if (candidate.kind === 'folder-bot') {
    if (!bases.has('readme.md')) issues.push('Missing README.md');
    if (!bases.has('bot.manifest.json') && !bases.has('replit_profile.json') && !bases.has('package.json')) {
      issues.push('Missing bot manifest/profile/package metadata');
    }
  }

  for (const filePath of files) {
    for (const missingImport of scanImports(filePath)) {
      issues.push(`Missing relative import ${missingImport.import} from ${missingImport.file}`);
    }
  }

  const packagePath = path.join(candidate.path, 'package.json');
  if (candidate.kind === 'folder-bot' && exists(packagePath)) {
    const pkg = readJson(packagePath);
    if (!pkg) issues.push('package.json is invalid JSON');
    if (pkg && !pkg.scripts) issues.push('package.json has no scripts block');
  }

  return {
    name: candidate.name,
    root: candidate.root,
    kind: candidate.kind,
    path: path.relative(ROOT, candidate.path),
    issueCount: issues.length,
    issues,
  };
}

function writeReports(results) {
  fs.mkdirSync(REPORT_DIR, { recursive: true });

  const summary = {
    generatedAt: new Date().toISOString(),
    totalBots: results.length,
    botsWithIssues: results.filter((item) => item.issueCount > 0).length,
    totalIssues: results.reduce((sum, item) => sum + item.issueCount, 0),
    results,
  };

  fs.writeFileSync(JSON_REPORT, `${JSON.stringify(summary, null, 2)}\n`);

  const lines = [
    '# DreamCo Bot Health Report',
    '',
    `Generated: ${summary.generatedAt}`,
    '',
    `- Total bot candidates: ${summary.totalBots}`,
    `- Bots with issues: ${summary.botsWithIssues}`,
    `- Total issues: ${summary.totalIssues}`,
    '',
  ];

  for (const result of results) {
    lines.push(`## ${result.name}`);
    lines.push('');
    lines.push(`- Path: \`${result.path}\``);
    lines.push(`- Root: \`${result.root}\``);
    lines.push(`- Issues: ${result.issueCount}`);
    if (result.issues.length) {
      for (const issue of result.issues) lines.push(`- ${issue}`);
    } else {
      lines.push('- No missing-file issues detected by this scanner.');
    }
    lines.push('');
  }

  fs.writeFileSync(MD_REPORT, `${lines.join('\n')}\n`);
  return summary;
}

const candidates = findBotCandidates();
const results = candidates.map(scanBot).sort((a, b) => b.issueCount - a.issueCount || a.name.localeCompare(b.name));
const summary = writeReports(results);

console.log(`DreamCo bot scan complete: ${summary.totalBots} candidates, ${summary.totalIssues} issues.`);
console.log(`Reports written to ${path.relative(ROOT, JSON_REPORT)} and ${path.relative(ROOT, MD_REPORT)}.`);

if (STRICT && summary.totalIssues > 0) {
  process.exitCode = 1;
}
