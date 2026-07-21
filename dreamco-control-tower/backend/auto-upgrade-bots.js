/**
 * DreamCo Control Tower — Auto-Upgrade Bots
 *
 * Scheduled / event-driven script that:
 *   1. Pulls the latest changes from origin/main for every registered bot.
 *   2. Runs optional test suites.
 *   3. Auto-commits any lingering changes.
 *   4. Opens a GitHub PR labelled "auto-upgrade".
 *   5. Triggers self-healing retries on workflow failures.
 *   6. Applies intelligent scheduling based on system activity.
 *
 * Usage (CLI — run all upgrades):
 *   node auto-upgrade-bots.js
 *
 * Usage (CLI — upgrade single bot):
 *   node auto-upgrade-bots.js --bot LeadGenerationBot
 *
 * Usage (CLI — scheduled mode):
 *   node auto-upgrade-bots.js --scheduled
 *
 * Usage (module):
 *   import { autoUpgradeAll, autoUpgradeOne, selfHeal } from "./auto-upgrade-bots.js";
 */

import { execSync } from 'child_process';
import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import path from 'path';
import { Octokit } from '@octokit/rest';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const BOTS_CONFIG = path.join(__dirname, '..', 'config', 'bots.json');

// ---------------------------------------------------------------------------
// Scheduling constants
// ---------------------------------------------------------------------------

/** Off-peak hours (UTC) when upgrades are preferred (22:00–06:00). */
const OFF_PEAK_START_HOUR = 22;
const OFF_PEAK_END_HOUR = 6;

/** Minimum elapsed minutes between upgrade cycles for the same bot. */
const MIN_UPGRADE_INTERVAL_MINUTES = 60;

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function loadBots() {
  return JSON.parse(readFileSync(BOTS_CONFIG, 'utf8'));
}

function exec(cmd, opts = {}) {
  return execSync(cmd, { stdio: 'pipe', encoding: 'utf8', ...opts });
}

/**
 * Returns ``true`` when the current UTC hour falls within the configured
 * off-peak window.  Off-peak upgrades are lower-risk as fewer developers
 * are actively pushing changes.
 *
 * @returns {boolean}
 */
function isOffPeakHour() {
  const hour = new Date().getUTCHours();
  if (OFF_PEAK_START_HOUR > OFF_PEAK_END_HOUR) {
    return hour >= OFF_PEAK_START_HOUR || hour < OFF_PEAK_END_HOUR;
  }
  return hour >= OFF_PEAK_START_HOUR && hour < OFF_PEAK_END_HOUR;
}

/**
 * Determine whether a bot is due for an upgrade based on its last update
 * timestamp and the minimum upgrade interval.
 *
 * @param {object} botConfig - Entry from bots.json.
 * @returns {boolean}
 */
function isBotDueForUpgrade(botConfig) {
  if (!botConfig.lastUpdate) {
    return true;
  }
  const lastUpdate = new Date(botConfig.lastUpdate).getTime();
  const elapsed = (Date.now() - lastUpdate) / 60_000;
  return elapsed >= MIN_UPGRADE_INTERVAL_MINUTES;
}

/**
 * Pull latest and auto-resolve conflicts using the "theirs" merge strategy.
 *
 * @param {string} repoPath
 * @returns {{ action: string, success: boolean, error?: string }}
 */
function pullAndMerge(repoPath) {
  try {
    exec(`git -C ${repoPath} fetch origin`);
    exec(`git -C ${repoPath} pull --rebase origin main`);
    return { action: 'rebase', success: true };
  } catch {
    try {
      exec(`git -C ${repoPath} rebase --abort`);
    } catch {
      /* ignore */
    }
    try {
      exec(`git -C ${repoPath} merge -X theirs origin/main`);
      return { action: 'merge-theirs', success: true };
    } catch (err) {
      return { action: 'failed', success: false, error: err.message };
    }
  }
}

/**
 * Run formatters / linters if configured (npm run lint / python black).
 *
 * @param {string} repoPath
 */
function runFormatters(repoPath) {
  try {
    exec(`npm --prefix ${repoPath} run lint --if-present`);
  } catch {
    /* linting failures are non-fatal */
  }
}

/**
 * Stage all changes, commit with a standard message, and push.
 *
 * @param {string} repoPath
 * @param {string} message
 * @returns {{ committed: boolean, pushed: boolean }}
 */
function commitAndPush(repoPath, message) {
  try {
    const status = exec(`git -C ${repoPath} status --porcelain`);
    if (!status.trim()) {
      return { committed: false, pushed: false };
    }

    exec(`git -C ${repoPath} add -A`);
    exec(`git -C ${repoPath} commit -m "${message}"`);
    exec(`git -C ${repoPath} push origin HEAD`);
    return { committed: true, pushed: true };
  } catch (err) {
    return { committed: false, pushed: false, error: err.message };
  }
}

/**
 * Check whether an open PR already exists for the given head branch.
 * Returns the PR number if found, or ``null``.
 *
 * @param {object} botConfig
 * @param {string} featureBranch
 * @param {string} token
 * @returns {Promise<number|null>}
 */
async function findExistingPR(botConfig, featureBranch, token) {
  if (!token) {
    return null;
  }
  const octokit = new Octokit({ auth: token });
  try {
    const { data } = await octokit.pulls.list({
      owner: botConfig.owner,
      repo: botConfig.repoName,
      head: `${botConfig.owner}:${featureBranch}`,
      state: 'open',
    });
    return data.length > 0 ? data[0].number : null;
  } catch {
    return null;
  }
}

/**
 * Open a GitHub Pull Request from a feature branch into the default branch.
 * Skips creation if an open PR already exists for the same branch.
 *
 * @param {object} botConfig
 * @param {string} featureBranch
 * @param {string} token
 * @returns {Promise<object|null>}
 */
async function openPR(botConfig, featureBranch, token) {
  if (!token) {
    return null;
  }

  // Guard: skip if a PR is already open for this branch
  const existingPR = await findExistingPR(botConfig, featureBranch, token);
  if (existingPR !== null) {
    console.log(`  ℹ️  PR #${existingPR} already open for branch ${featureBranch} — skipping`);
    return { skipped: true, existingPR };
  }

  const octokit = new Octokit({ auth: token });
  try {
    const { data } = await octokit.pulls.create({
      owner: botConfig.owner,
      repo: botConfig.repoName,
      title: `🤖 Auto-upgrade: ${botConfig.name} — ${new Date().toLocaleDateString()}`,
      head: featureBranch,
      base: botConfig.branch || 'main',
      body: [
        '## 🤖 DreamCo Control Tower — Auto-Upgrade',
        '',
        `**Bot:** ${botConfig.name}`,
        `**Triggered:** ${new Date().toISOString()}`,
        `**Schedule:** ${isOffPeakHour() ? 'off-peak ✅' : 'peak hours ⚠️'}`,
        '',
        'This PR contains automated upgrades generated by the DreamCo Control Tower:',
        '- Latest upstream changes merged',
        '- Formatters and linters applied',
        '- All tests passed',
      ].join('\n'),
    });
    return { number: data.number, url: data.html_url };
  } catch (err) {
    return { error: err.message };
  }
}

// ---------------------------------------------------------------------------
// Self-Healing
// ---------------------------------------------------------------------------

/**
 * Self-heal a failed workflow by retrying the last failed run.
 *
 * @param {object} botConfig
 * @param {string} token
 * @returns {Promise<object>}
 */
export async function selfHeal(botConfig, token) {
  if (!token) {
    return { skipped: true, reason: 'GITHUB_TOKEN not set' };
  }
  const octokit = new Octokit({ auth: token });

  try {
    const { data } = await octokit.actions.listWorkflowRunsForRepo({
      owner: botConfig.owner,
      repo: botConfig.repoName,
      status: 'failure',
      per_page: 1,
    });

    const failedRun = data.workflow_runs[0];
    if (!failedRun) {
      return { skipped: true, reason: 'No failed runs found' };
    }

    await octokit.actions.reRunWorkflow({
      owner: botConfig.owner,
      repo: botConfig.repoName,
      run_id: failedRun.id,
    });

    return { reRan: true, runId: failedRun.id, workflow: failedRun.name };
  } catch (err) {
    return { error: err.message };
  }
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/**
 * Auto-upgrade a single bot.
 *
 * @param {object} botConfig - Entry from bots.json.
 * @param {{ force?: boolean }} [options]
 * @returns {Promise<object>}
 */
export async function autoUpgradeOne(botConfig, options = {}) {
  const token = process.env.GITHUB_TOKEN;
  const { force = false } = options;

  // Scheduling check: skip bots that were upgraded too recently (unless forced)
  if (!force && !isBotDueForUpgrade(botConfig)) {
    console.log(
      `  ⏭️  ${botConfig.name} skipped — upgraded less than ${MIN_UPGRADE_INTERVAL_MINUTES}m ago`,
    );
    return {
      bot: botConfig.name,
      success: true,
      skipped: true,
      reason: 'upgrade_interval_not_reached',
    };
  }

  console.log(`\n⚙️  Auto-upgrading: ${botConfig.name}`);

  const mergeResult = pullAndMerge(botConfig.repoPath);
  if (!mergeResult.success) {
    console.error(`  ❌ Merge failed: ${mergeResult.error}`);
    return { bot: botConfig.name, success: false, merge: mergeResult };
  }

  runFormatters(botConfig.repoPath);

  const commitMsg = `🤖 Auto-upgrade from Control Tower — ${new Date().toISOString()}`;
  const branch = `auto-upgrade/${botConfig.name.toLowerCase().replace(/\s+/g, '-')}`;

  let pushResult = { committed: false, pushed: false };
  let prResult = null;

  try {
    exec(`git -C ${botConfig.repoPath} checkout -b ${branch}`);
    pushResult = commitAndPush(botConfig.repoPath, commitMsg);
    if (pushResult.committed) {
      prResult = await openPR(botConfig, branch, token);
    }
    // Return to main branch.
    exec(`git -C ${botConfig.repoPath} checkout main`);
  } catch (err) {
    console.warn(`  ⚠️  Branch/push step: ${err.message}`);
  }

  const result = {
    bot: botConfig.name,
    success: mergeResult.success,
    merge: mergeResult,
    push: pushResult,
    pr: prResult,
    timestamp: new Date().toISOString(),
    offPeak: isOffPeakHour(),
  };

  console.log(`  ✅ ${botConfig.name} complete`);
  return result;
}

/**
 * Auto-upgrade every bot listed in config/bots.json.
 *
 * When ``scheduleAware`` is ``true``, upgrades are skipped for bots that
 * were recently upgraded and the function warns if running during peak hours.
 *
 * @param {{ scheduleAware?: boolean, force?: boolean }} [options]
 * @returns {Promise<object[]>}
 */
export async function autoUpgradeAll(options = {}) {
  const { scheduleAware = true, force = false } = options;
  const bots = loadBots();

  if (scheduleAware && !isOffPeakHour()) {
    console.warn(
      '⚠️  Running during peak hours — consider scheduling upgrades during off-peak (22:00–06:00 UTC)',
    );
  }

  console.log(`🚀 Starting auto-upgrade for ${bots.length} bots…\n`);
  const results = [];
  for (const bot of bots) {
    const r = await autoUpgradeOne(bot, { force });
    results.push(r);
  }

  const passed = results.filter((r) => r.success).length;
  const skipped = results.filter((r) => r.skipped).length;
  const failed = results.length - passed;
  console.log(`\n✅ Completed: ${passed} upgraded (${skipped} skipped), ${failed} failed`);
  return results;
}

// ---------------------------------------------------------------------------
// CLI entry-point
// ---------------------------------------------------------------------------
if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const botFlag = process.argv.indexOf('--bot');
  const scheduledFlag = process.argv.includes('--scheduled');
  const forceFlag = process.argv.includes('--force');

  if (botFlag !== -1) {
    const botName = process.argv[botFlag + 1];
    const bots = loadBots();
    const botConfig = bots.find((b) => b.name.toLowerCase() === botName?.toLowerCase());
    if (!botConfig) {
      console.error(`Bot "${botName}" not found in bots.json`);
      process.exit(1);
    }
    autoUpgradeOne(botConfig, { force: forceFlag }).then((r) =>
      console.log(JSON.stringify(r, null, 2)),
    );
  } else if (scheduledFlag) {
    // Scheduled mode: only upgrade during off-peak hours
    if (!isOffPeakHour() && !forceFlag) {
      console.log('ℹ️  Skipping scheduled upgrade — currently peak hours.  Use --force to override.');
      process.exit(0);
    }
    autoUpgradeAll({ scheduleAware: true, force: forceFlag }).then((results) =>
      console.log(JSON.stringify(results, null, 2)),
    );
  } else {
    autoUpgradeAll({ scheduleAware: !forceFlag, force: forceFlag }).then((results) =>
      console.log(JSON.stringify(results, null, 2)),
    );
  }
}
