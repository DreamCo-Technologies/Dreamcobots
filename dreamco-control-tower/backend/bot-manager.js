/**
 * DreamCo Control Tower — Bot Manager
 *
 * Monitors all registered bots, triggers auto-upgrades (git pull + merge),
 * and opens GitHub Pull Requests for any auto-generated changes.
 *
 * Usage (CLI):
 *   node bot-manager.js
 *
 * Usage (module):
 *   import { runAllUpgrades, upgradeSingleBot } from "./bot-manager.js";
 */

import { execSync } from 'child_process';
import { readFileSync, writeFileSync } from 'fs';
import { fileURLToPath } from 'url';
import path from 'path';
import { Octokit } from '@octokit/rest';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const BOTS_CONFIG = path.join(__dirname, '..', 'config', 'bots.json');

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function loadBots() {
  return JSON.parse(readFileSync(BOTS_CONFIG, 'utf8'));
}

function saveBots(bots) {
  writeFileSync(BOTS_CONFIG, JSON.stringify(bots, null, 2));
}

/**
 * Pull and rebase the latest changes from origin/main.
 * Falls back to merge -X theirs on conflict.
 *
 * @param {string} repoPath - Absolute or relative path to the git repo.
 * @returns {{ success: boolean, action: string }}
 */
function pullLatest(repoPath) {
  try {
    execSync(`git -C ${repoPath} pull --rebase origin main`, { stdio: 'pipe' });
    return { success: true, action: 'rebase' };
  } catch {
    console.warn(`⚠️  Conflict in ${repoPath} — auto-resolving with theirs strategy`);
    try {
      execSync(`git -C ${repoPath} merge -X theirs origin/main`, { stdio: 'pipe' });
      return { success: true, action: 'merge-theirs' };
    } catch (mergeErr) {
      return { success: false, action: 'failed', error: mergeErr.message };
    }
  }
}

/**
 * Run the test suite for a bot repo (if a package.json or pytest setup exists).
 *
 * @param {string} repoPath
 * @returns {{ passed: boolean, output: string }}
 */
function runTests(repoPath) {
  try {
    const hasPackageJson = (() => {
      try {
        readFileSync(path.join(repoPath, 'package.json'));
        return true;
      } catch {
        return false;
      }
    })();

    if (hasPackageJson) {
      const output = execSync(`npm --prefix ${repoPath} test --if-present`, {
        stdio: 'pipe',
        encoding: 'utf8',
      });
      return { passed: true, output };
    }
    return { passed: true, output: 'no tests configured' };
  } catch (err) {
    return { passed: false, output: err.message };
  }
}

/**
 * Open a GitHub Pull Request for auto-upgrades.
 *
 * @param {object} botConfig
 * @param {string} token - GitHub personal access token.
 */
async function createUpgradePR(botConfig, token) {
  if (!token) {
    console.warn('GITHUB_TOKEN not set — skipping PR creation');
    return null;
  }

  const octokit = new Octokit({ auth: token });
  const branch = `auto-upgrade/${botConfig.name.toLowerCase()}-${Date.now()}`;

  try {
    // Ensure there are commits to push before creating a PR.
    const hasChanges = (() => {
      try {
        const out = execSync(`git -C ${botConfig.repoPath} status --porcelain`, {
          encoding: 'utf8',
        });
        return out.trim().length > 0;
      } catch {
        return false;
      }
    })();

    if (!hasChanges) {
      return { skipped: true, reason: 'no changes to push' };
    }

    execSync(
      `git -C ${botConfig.repoPath} checkout -b ${branch} && git -C ${botConfig.repoPath} push origin ${branch}`,
      { stdio: 'pipe' }
    );

    const pr = await octokit.pulls.create({
      owner: botConfig.owner,
      repo: botConfig.repoName,
      title: `🤖 Auto-upgrade: ${botConfig.name} from Control Tower`,
      head: branch,
      base: botConfig.branch || 'main',
      body: [
        '## Auto-Upgrade from DreamCo Control Tower',
        '',
        `Bot: **${botConfig.name}**`,
        `Triggered at: ${new Date().toISOString()}`,
        '',
        'This PR was automatically created by the DreamCo Control Tower bot manager.',
        'It includes the latest upstream changes pulled and merged automatically.',
      ].join('\n'),
    });

    return { prNumber: pr.data.number, prUrl: pr.data.html_url };
  } catch (err) {
    return { error: err.message };
  }
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/**
 * Upgrade a single bot: pull latest, run tests, open PR if changes exist.
 *
 * @param {object} botConfig - Single entry from bots.json.
 * @returns {Promise<object>} Result summary.
 */
export async function upgradeSingleBot(botConfig) {
  console.log(`\n🔄 Upgrading bot: ${botConfig.name}`);
  const token = process.env.GITHUB_TOKEN;

  const pullResult = pullLatest(botConfig.repoPath);
  const testResult = runTests(botConfig.repoPath);
  const prResult = testResult.passed ? await createUpgradePR(botConfig, token) : null;

  const summary = {
    bot: botConfig.name,
    pull: pullResult,
    tests: testResult,
    pr: prResult,
    timestamp: new Date().toISOString(),
  };

  if (pullResult.success) {
    console.log(`✅ ${botConfig.name} upgraded (${pullResult.action})`);
  } else {
    console.error(`❌ ${botConfig.name} upgrade failed: ${pullResult.error}`);
  }

  return summary;
}

/**
 * Upgrade all bots listed in config/bots.json.
 *
 * @returns {Promise<object[]>} Array of per-bot result summaries.
 */
export async function runAllUpgrades() {
  const bots = loadBots();
  const results = [];

  for (const bot of bots) {
    const result = await upgradeSingleBot(bot);
    results.push(result);
  }

  // Persist last-run timestamps back to config.
  const updatedBots = bots.map((b) => ({
    ...b,
    lastUpgraded: new Date().toISOString(),
  }));
  saveBots(updatedBots);

  return results;
}

// ---------------------------------------------------------------------------
// CLI entry-point
// ---------------------------------------------------------------------------
if (process.argv[1] === fileURLToPath(import.meta.url)) {
  runAllUpgrades()
    .then((results) => {
      console.log('\n📋 Upgrade Summary:');
      results.forEach((r) => {
        const status = r.pull.success ? '✅' : '❌';
        console.log(`  ${status} ${r.bot}`);
      });
    })
    .catch((err) => {
      console.error('Fatal error:', err);
      process.exit(1);
    });
}
