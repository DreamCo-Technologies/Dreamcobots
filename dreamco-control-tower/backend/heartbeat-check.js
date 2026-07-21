/**
 * DreamCo Control Tower — Heartbeat Check
 *
 * Verifies that every bot registered in config/bots.json is reachable and
 * operational.  For bots that expose an HTTP heartbeat URL the module performs
 * a real HTTP probe; for local-only bots it performs a git-status check.
 *
 * Usage (CLI):
 *   node heartbeat-check.js
 *
 * Usage (module):
 *   import { checkAllBots, checkBot } from "./heartbeat-check.js";
 *   const statuses = await checkAllBots();
 */

import { readFileSync } from 'fs';
import { execSync } from 'child_process';
import { fileURLToPath } from 'url';
import path from 'path';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const BOTS_CONFIG = path.join(__dirname, '..', 'config', 'bots.json');

// Default HTTP probe timeout in milliseconds.
const HTTP_TIMEOUT_MS = 5000;

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function loadBots() {
  try {
    return JSON.parse(readFileSync(BOTS_CONFIG, 'utf8'));
  } catch {
    return [];
  }
}

/**
 * Probe an HTTP heartbeat endpoint.
 *
 * @param {string} url
 * @returns {Promise<{ reachable: boolean, latencyMs: number, statusCode?: number }>}
 */
async function httpProbe(url) {
  const start = Date.now();
  try {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), HTTP_TIMEOUT_MS);
    const response = await fetch(url, { signal: controller.signal });
    clearTimeout(timer);
    return {
      reachable: response.ok,
      latencyMs: Date.now() - start,
      statusCode: response.status,
    };
  } catch {
    return { reachable: false, latencyMs: Date.now() - start };
  }
}

/**
 * Local git-health probe — checks that the repo path exists and is a git repo.
 *
 * @param {string} repoPath
 * @returns {{ healthy: boolean, branch?: string, lastCommit?: string }}
 */
function gitProbe(repoPath) {
  try {
    const branch = execSync(`git -C ${repoPath} rev-parse --abbrev-ref HEAD`, {
      stdio: 'pipe',
      encoding: 'utf8',
    }).trim();
    const lastCommit = execSync(`git -C ${repoPath} log -1 --format="%h %s" --no-merges`, {
      stdio: 'pipe',
      encoding: 'utf8',
    }).trim();
    return { healthy: true, branch, lastCommit };
  } catch {
    return { healthy: false };
  }
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/**
 * Check the heartbeat status of a single bot.
 *
 * @param {object} botConfig - One entry from bots.json.
 * @returns {Promise<object>}
 */
export async function checkBot(botConfig) {
  const now = new Date().toISOString();
  let probe = {};

  if (botConfig.heartbeatUrl) {
    probe = await httpProbe(botConfig.heartbeatUrl);
  } else if (botConfig.repoPath) {
    const gitResult = gitProbe(botConfig.repoPath);
    probe = { reachable: gitResult.healthy, ...gitResult };
  } else {
    probe = { reachable: false, reason: 'no heartbeatUrl or repoPath configured' };
  }

  return {
    name: botConfig.name,
    repoName: botConfig.repoName,
    tier: botConfig.tier,
    status: probe.reachable ? 'active' : 'offline',
    lastHeartbeat: now,
    ...probe,
  };
}

/**
 * Check heartbeat status for every bot in config/bots.json.
 *
 * @returns {Promise<object[]>}
 */
export async function checkAllBots() {
  const bots = loadBots();
  const results = await Promise.all(bots.map(checkBot));
  return results;
}

// ---------------------------------------------------------------------------
// CLI entry-point
// ---------------------------------------------------------------------------
if (process.argv[1] === fileURLToPath(import.meta.url)) {
  checkAllBots().then((statuses) => {
    console.log('🫀 DreamCo Control Tower — Heartbeat Report\n');
    statuses.forEach((s) => {
      const icon = s.status === 'active' ? '✅' : '❌';
      const detail = s.latencyMs != null ? `${s.latencyMs}ms` : (s.branch ?? '');
      console.log(`  ${icon} ${s.name.padEnd(25)} ${s.status.padEnd(8)} ${detail}`);
    });
    console.log(`\nTimestamp: ${new Date().toISOString()}`);
  });
}
