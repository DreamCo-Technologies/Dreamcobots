/**
 * DreamCo Control Tower — Heartbeat Check
 *
 * Reads all registered bots from config/bots.json and reports their
 * current heartbeat age and status to the console.  Bots that have not
 * sent a heartbeat within the STALE_THRESHOLD are flagged as stale.
 *
 * Usage:
 *   node scripts/heartbeat-check.js
 *
 * Optional environment variable:
 *   STALE_MINUTES  — minutes before a bot is flagged stale (default: 5)
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const BOTS_FILE = path.join(__dirname, '../config/bots.json');
const STALE_MINUTES = parseInt(process.env.STALE_MINUTES ?? '5', 10);
const STALE_MS = STALE_MINUTES * 60 * 1000;

function readBots() {
  return JSON.parse(fs.readFileSync(BOTS_FILE, 'utf8'));
}

function formatAge(ms) {
  if (ms < 60_000) {
    return `${Math.round(ms / 1000)}s ago`;
  }
  if (ms < 3_600_000) {
    return `${Math.round(ms / 60_000)}m ago`;
  }
  return `${Math.round(ms / 3_600_000)}h ago`;
}

function checkHeartbeats() {
  const bots = readBots();
  const now = Date.now();

  console.log('\n💓 DreamCo Control Tower — Heartbeat Report');
  console.log('='.repeat(50));

  let healthyCount = 0;
  let staleCount = 0;
  let neverCount = 0;

  for (const bot of bots) {
    if (!bot.lastHeartbeat) {
      console.log(`  ⚫ ${bot.name.padEnd(25)} NEVER checked in`);
      neverCount++;
      continue;
    }

    const age = now - new Date(bot.lastHeartbeat).getTime();
    const isStale = age > STALE_MS;
    const icon = isStale ? '🔴' : '🟢';
    const label = isStale ? 'STALE' : 'OK';

    console.log(
      `  ${icon} ${bot.name.padEnd(25)} ${label.padEnd(6)} — last heartbeat: ${formatAge(age)}`
    );

    if (isStale) {
      staleCount++;
    } else {
      healthyCount++;
    }
  }

  console.log('='.repeat(50));
  console.log(
    `  Total: ${bots.length} | 🟢 Healthy: ${healthyCount} | 🔴 Stale: ${staleCount} | ⚫ Never: ${neverCount}`
  );
  console.log();

  if (staleCount > 0 || neverCount === bots.length) {
    process.exitCode = 1;
  }
}

checkHeartbeats();
