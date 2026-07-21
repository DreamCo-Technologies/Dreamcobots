/**
 * DreamCo Control Tower — Auto-Upgrade Bots
 *
 * Scheduled automation script that:
 *   1. Pulls the latest main branch changes for each registered bot repo.
 *   2. Auto-resolves conflicts using "merge -X theirs" strategy.
 *   3. Optionally runs npm tests.
 *   4. Opens a pull request for any upgrades via the GitHub API.
 *
 * Usage:
 *   node automation/auto-upgrade-bots.js
 *
 * Environment variables:
 *   GITHUB_TOKEN  — Personal Access Token with repo scope
 *   GITHUB_OWNER  — GitHub username / org (default: ireanjordan24)
 */

import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { Octokit } from '@octokit/rest';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const BOTS_FILE = path.join(__dirname, '../config/bots.json');

const octokit = new Octokit({ auth: process.env.GITHUB_TOKEN });
const OWNER = process.env.GITHUB_OWNER || 'ireanjordan24';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function readBots() {
  return JSON.parse(fs.readFileSync(BOTS_FILE, 'utf8'));
}

/**
 * Pull the latest changes from origin/main, auto-resolving conflicts.
 */
function pullLatest(repoPath) {
  try {
    execSync(`git -C ${repoPath} pull --rebase origin main`, { stdio: 'pipe' });
    console.log(`  ✅ Pulled latest for ${repoPath}`);
    return true;
  } catch (_err) {
    console.warn(`  ⚠️  Conflict detected in ${repoPath} — auto-resolving with "theirs" strategy`);
    try {
      execSync(`git -C ${repoPath} merge -X theirs origin/main`, { stdio: 'pipe' });
      console.log(`  ✅ Conflict resolved for ${repoPath}`);
      return true;
    } catch (mergeErr) {
      console.error(`  ❌ Failed to resolve conflict: ${mergeErr.message}`);
      return false;
    }
  }
}

/**
 * Run npm tests in the repo directory (skips if no package.json).
 */
function runTests(repoPath) {
  const pkgPath = path.join(repoPath, 'package.json');
  if (!fs.existsSync(pkgPath)) {
    console.log(`  ℹ️  No package.json in ${repoPath} — skipping npm test`);
    return true;
  }
  try {
    execSync(`npm --prefix ${repoPath} test`, { stdio: 'pipe' });
    console.log(`  ✅ Tests passed for ${repoPath}`);
    return true;
  } catch (err) {
    console.error(`  ❌ Tests failed for ${repoPath}: ${err.message}`);
    return false;
  }
}

/**
 * Create an auto-upgrade pull request via the GitHub API.
 */
async function createUpgradePR(repoName, branch, title) {
  try {
    const { data } = await octokit.pulls.create({
      owner: OWNER,
      repo: repoName,
      title,
      head: branch,
      base: 'main',
      body: '🤖 Automated upgrade created by DreamCo Control Tower.',
    });
    console.log(`  🔀 PR opened: ${data.html_url}`);
    return data.html_url;
  } catch (err) {
    console.warn(`  ⚠️  Could not open PR for ${repoName}: ${err.message}`);
    return null;
  }
}

// ---------------------------------------------------------------------------
// Main upgrade loop
// ---------------------------------------------------------------------------

async function runUpgrades() {
  const bots = readBots();
  console.log(`🤖 Starting auto-upgrade for ${bots.length} bot(s)...\n`);

  for (const bot of bots) {
    console.log(`🔧 Upgrading bot: ${bot.name}`);

    const pulled = pullLatest(bot.repoPath);
    if (!pulled) {
      console.log(`  ⏭️  Skipping tests and PR for ${bot.name} due to pull failure\n`);
      continue;
    }

    const testsPassed = runTests(bot.repoPath);

    if (testsPassed) {
      await createUpgradePR(
        bot.repoName,
        bot.branch ?? 'auto-update',
        `🤖 Auto-upgrade from Control Tower — ${bot.name}`
      );
    }

    console.log();
  }

  console.log('✅ Auto-upgrade run complete.');
}

runUpgrades().catch((err) => {
  console.error('Fatal error during upgrade run:', err);
  process.exit(1);
});
