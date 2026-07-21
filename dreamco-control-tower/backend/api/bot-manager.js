/**
 * DreamCo Control Tower — Bot Manager
 *
 * Handles the bot registry: reading generated catalog data and runtime updates.
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const LEGACY_BOTS_FILE = path.join(__dirname, '../../config/bots.json');
const GENERATED_BOTS_FILE = path.join(__dirname, '../../config/generated/bots.catalog.json');

// ---------------------------------------------------------------------------
// Read / write helpers
// ---------------------------------------------------------------------------

export function readBots() {
  if (process.env.NODE_ENV === 'test') {
    return JSON.parse(fs.readFileSync(LEGACY_BOTS_FILE, 'utf8'));
  }
  if (fs.existsSync(GENERATED_BOTS_FILE)) {
    const generatedPayload = JSON.parse(fs.readFileSync(GENERATED_BOTS_FILE, 'utf8'));
    const generatedBots = Array.isArray(generatedPayload)
      ? generatedPayload
      : generatedPayload.bots ?? [];
    if (!fs.existsSync(LEGACY_BOTS_FILE)) {
      return generatedBots;
    }
    const runtimeBots = JSON.parse(fs.readFileSync(LEGACY_BOTS_FILE, 'utf8'));
    const runtimeByName = new Map(runtimeBots.map((bot) => [bot.name, bot]));
    return generatedBots.map((bot) => ({ ...bot, ...(runtimeByName.get(bot.name) ?? {}) }));
  }
  return JSON.parse(fs.readFileSync(LEGACY_BOTS_FILE, 'utf8'));
}

export function writeBots(bots) {
  fs.writeFileSync(LEGACY_BOTS_FILE, JSON.stringify(bots, null, 2));
}

// ---------------------------------------------------------------------------
// Registry operations
// ---------------------------------------------------------------------------

/**
 * Return all registered bots.
 */
export function getAllBots() {
  return readBots();
}

/**
 * Find a single bot by name.
 */
export function getBotByName(name) {
  return readBots().find((b) => b.name === name) ?? null;
}

/**
 * Register a new bot or update an existing one.
 */
export function upsertBot(botData) {
  const bots = readBots();
  const index = bots.findIndex((b) => b.name === botData.name);
  if (index >= 0) {
    bots[index] = { ...bots[index], ...botData };
  } else {
    bots.push({
      status: 'idle',
      lastHeartbeat: null,
      lastPR: null,
      workflowStatus: 'unknown',
      ...botData,
    });
  }
  writeBots(bots);
  return getBotByName(botData.name);
}

/**
 * Update bot heartbeat timestamp and status.
 */
export function updateHeartbeat(botName, status = 'active') {
  const bots = readBots();
  const bot = bots.find((b) => b.name === botName);
  if (!bot) {
    return null;
  }
  bot.lastHeartbeat = new Date().toISOString();
  bot.status = status;
  writeBots(bots);
  return bot;
}

/**
 * Mark a bot's last PR reference.
 */
export function updateLastPR(botName, prUrl) {
  const bots = readBots();
  const bot = bots.find((b) => b.name === botName);
  if (!bot) {
    return null;
  }
  bot.lastPR = prUrl;
  writeBots(bots);
  return bot;
}

/**
 * Return a summary of all bots: totals by status.
 */
export function getBotSummary() {
  const bots = readBots();
  const summary = { total: bots.length, byStatus: {} };
  for (const bot of bots) {
    summary.byStatus[bot.status] = (summary.byStatus[bot.status] ?? 0) + 1;
  }
  return summary;
}
