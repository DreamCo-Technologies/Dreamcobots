#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const ROOT = process.cwd();
const REPORT_DIR = path.join(ROOT, 'reports');
const REPORT_JSON = path.join(REPORT_DIR, 'buddy-connectivity-report.json');
const REPORT_MD = path.join(REPORT_DIR, 'buddy-connectivity-report.md');

const checks = [];

function exists(relativePath) {
  return fs.existsSync(path.join(ROOT, relativePath));
}

function readJson(relativePath) {
  const fullPath = path.join(ROOT, relativePath);
  try {
    return JSON.parse(fs.readFileSync(fullPath, 'utf8'));
  } catch (error) {
    return null;
  }
}

function addCheck(name, status, detail) {
  checks.push({ name, status, detail });
}

function validateToolRegistry() {
  const registryPath = 'config/buddy-mcp-tool-registry.json';
  const registry = readJson(registryPath);
  addCheck('MCP tool registry exists', Boolean(registry), registryPath);
  if (!registry) return;

  const tools = Array.isArray(registry.tools) ? registry.tools : [];
  addCheck('MCP tool registry has tools', tools.length > 0, `${tools.length} tools`);
  addCheck('GitHub read enabled', tools.some((tool) => tool.id === 'github_repository_read' && tool.enabled), 'github_repository_read');
  addCheck('GitHub write gated', tools.some((tool) => tool.id === 'github_repository_write' && tool.requiresApproval), 'github_repository_write requires approval');
  addCheck('Stripe tracking available', tools.some((tool) => tool.id === 'stripe_revenue_tracking'), 'stripe_revenue_tracking');
  addCheck('External Builder explicitly represented', tools.some((tool) => tool.id === 'external_builder'), 'external_builder slot');
  addCheck('High-risk write commands disabled by default', tools.some((tool) => tool.id === 'local_command_write' && !tool.enabled), 'local_command_write disabled');
}

function validateModelRouter() {
  const routerPath = 'config/buddy-model-router.json';
  const router = readJson(routerPath);
  addCheck('Buddy model router exists', Boolean(router), routerPath);
  if (!router) return;

  const providers = Array.isArray(router.providers) ? router.providers : [];
  const routes = Array.isArray(router.topInternetIntentRoutes) ? router.topInternetIntentRoutes : [];
  addCheck('Model router has provider slots', providers.length >= 8, `${providers.length} providers`);
  addCheck('Model router has 100 intent routes', routes.length >= 100, `${routes.length} routes`);
  addCheck('OpenAI provider enabled', providers.some((provider) => provider.id === 'openai' && provider.enabled), 'openai provider');
  addCheck('Money tasks require approval rule', JSON.stringify(router.routingRules || []).includes('money'), 'routingRules mention money');
}

function validateReportsAndDocs() {
  const required = [
    'docs/DASHBOARD_COMMAND_CENTER_TRACKING_MAP.md',
    'docs/ULTIMATE_DREAMCO_DASHBOARD_SPEC.md',
    'docs/BOT_TRACKING_LEARNING_SYSTEM.md',
    'docs/STRIPE_REVENUE_TRACKING_SYSTEM.md',
    'docs/SALES_REP_BOT_TEAM.md',
    'data/stripe/offers.template.json',
    'stripe/node/revenue-ledger.js',
    'stripe/node/revenue-report.js',
  ];

  for (const file of required) {
    addCheck(`Required file: ${file}`, exists(file), file);
  }
}

function writeReports() {
  const passed = checks.filter((check) => check.status).length;
  const failed = checks.length - passed;
  const report = {
    generatedAt: new Date().toISOString(),
    passed,
    failed,
    checks,
  };

  fs.mkdirSync(REPORT_DIR, { recursive: true });
  fs.writeFileSync(REPORT_JSON, `${JSON.stringify(report, null, 2)}\n`);

  const lines = [
    '# Buddy Connectivity Report',
    '',
    `Generated: ${report.generatedAt}`,
    '',
    `- Passed: ${passed}`,
    `- Failed: ${failed}`,
    '',
    '| Check | Status | Detail |',
    '| --- | --- | --- |',
  ];

  for (const check of checks) {
    lines.push(`| ${check.name} | ${check.status ? 'pass' : 'fail'} | ${check.detail} |`);
  }

  fs.writeFileSync(REPORT_MD, `${lines.join('\n')}\n`);
  console.log(`Buddy connectivity test complete: ${passed} passed, ${failed} failed.`);
  console.log(`Reports written to ${path.relative(ROOT, REPORT_JSON)} and ${path.relative(ROOT, REPORT_MD)}.`);

  if (failed > 0) process.exitCode = 1;
}

validateToolRegistry();
validateModelRouter();
validateReportsAndDocs();
writeReports();
