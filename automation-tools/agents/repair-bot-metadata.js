#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const ROOT = process.cwd();
const APPLY = process.argv.includes('--apply');
const BOT_ROOT = path.join(ROOT, 'bots');
const REPORT_DIR = path.join(ROOT, 'reports');
const REPORT_PATH = path.join(REPORT_DIR, 'bot-metadata-repair-plan.json');

function toTitle(slug) {
  return slug
    .replace(/[-_]+/g, ' ')
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function guessDivision(slug) {
  const value = slug.toLowerCase();
  if (/sales|lead|client|buyer|crm|marketing/.test(value)) return 'DreamSalesPro';
  if (/finance|payment|invoice|stripe|crypto|trade|loan/.test(value)) return 'DreamFinance';
  if (/real|property|housing|estate/.test(value)) return 'DreamRealEstate';
  if (/code|api|dev|github|ci|deploy/.test(value)) return 'DreamCodeLab';
  if (/content|media|video|post|social/.test(value)) return 'DreamContent';
  if (/security|trust|legal|compliance/.test(value)) return 'DreamProtection';
  return 'CommandCore';
}

function buildReadme(slug) {
  const title = toTitle(slug);
  return `# ${title}\n\n## Purpose\n\n${title} is a DreamCo bot. Its detailed operating instructions need owner review.\n\n## Required metadata\n\n- Division: ${guessDivision(slug)}\n- Mode: supervised\n- Command policy: GitHub Actions supervised\n- Memory policy: approved sources only\n\n## Runbook\n\n1. Confirm the bot purpose.\n2. Add required inputs and outputs.\n3. Add examples and tests.\n4. Run \`npm run scan:missing\`.\n5. Promote the bot only after its manifest and control file are reviewed.\n\n## Learning path\n\nThis bot follows the controlled two-year DreamCo learning system in \`docs/BOT_TRACKING_LEARNING_SYSTEM.md\`.\n`;
}

function buildManifest(slug) {
  return {
    botId: slug,
    displayName: toTitle(slug),
    division: guessDivision(slug),
    tier: 'draft',
    status: 'metadata-generated',
    purpose: 'Owner review required before production use.',
    inputs: [],
    outputs: [],
    workflows: [],
    abilities: [],
    risks: ['purpose_not_reviewed', 'tests_missing'],
    owner: 'DreamCo',
    source: 'Dreamcobots metadata repair generator',
  };
}

function buildControl(slug) {
  return {
    botId: slug,
    displayName: toTitle(slug),
    mode: 'supervised',
    division: guessDivision(slug),
    abilities: [],
    workflows: [],
    goals: [],
    learningPace: 'weekly',
    memoryPolicy: 'approved_sources_only',
    commandPolicy: 'github_actions_supervised',
    reviewers: ['owner', 'buddyai'],
    riskLevel: 'medium',
  };
}

function main() {
  if (!fs.existsSync(BOT_ROOT)) {
    console.error('No bots/ directory found.');
    process.exitCode = 1;
    return;
  }

  const plan = [];
  for (const entry of fs.readdirSync(BOT_ROOT, { withFileTypes: true })) {
    if (!entry.isDirectory()) continue;
    const slug = entry.name;
    const botDir = path.join(BOT_ROOT, slug);
    const targets = [
      { path: path.join(botDir, 'README.md'), content: buildReadme(slug) },
      { path: path.join(botDir, 'bot.manifest.json'), content: `${JSON.stringify(buildManifest(slug), null, 2)}\n` },
      { path: path.join(botDir, 'bot.control.json'), content: `${JSON.stringify(buildControl(slug), null, 2)}\n` },
    ];

    for (const target of targets) {
      if (!fs.existsSync(target.path)) {
        plan.push({ bot: slug, path: path.relative(ROOT, target.path), action: APPLY ? 'created' : 'would_create' });
        if (APPLY) fs.writeFileSync(target.path, target.content);
      }
    }
  }

  fs.mkdirSync(REPORT_DIR, { recursive: true });
  fs.writeFileSync(REPORT_PATH, `${JSON.stringify({ apply: APPLY, count: plan.length, plan }, null, 2)}\n`);
  console.log(`${APPLY ? 'Created' : 'Planned'} ${plan.length} metadata files.`);
  console.log(`Report written to ${path.relative(ROOT, REPORT_PATH)}.`);
}

main();
