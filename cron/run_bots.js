'use strict';

/**
 * DreamCo — Bot Scheduler
 *
 * Manages interval-based scheduling of all DreamCo bots.
 * Uses setInterval under the hood — no external cron library needed.
 */

const HOUR = 60 * 60 * 1000;
const SIX_HOURS = 6 * HOUR;
const DAY = 24 * HOUR;

/**
 * Predefined schedules for all registered bots.
 * Each entry is { botName, intervalMs, category, description }.
 */
const SCHEDULES = [
  {
    botName: 'multi_source_lead_scraper',
    intervalMs: HOUR,
    category: 'revenue',
    description: 'Scrape leads hourly',
  },
  {
    botName: 'fiverr_auto_apply',
    intervalMs: SIX_HOURS,
    category: 'freelance',
    description: 'Apply to Fiverr gigs every 6h',
  },
  {
    botName: 'real_estate_scanner',
    intervalMs: DAY,
    category: 'real_estate',
    description: 'Scan listings daily',
  },
  {
    botName: 'crypto_trader',
    intervalMs: 15 * 60 * 1000,
    category: 'crypto',
    description: 'Trade every 15 minutes',
  },
  {
    botName: 'grant_finder',
    intervalMs: 7 * DAY,
    category: 'grants',
    description: 'Search grants weekly',
  },
  {
    botName: 'email_campaign_sender',
    intervalMs: DAY,
    category: 'marketing',
    description: 'Send campaigns daily',
  },
  {
    botName: 'affiliate_link_optimizer',
    intervalMs: SIX_HOURS,
    category: 'affiliate',
    description: 'Optimize affiliate links every 6h',
  },
  {
    botName: 'lead_scorer',
    intervalMs: 2 * HOUR,
    category: 'crm',
    description: 'Rescore leads every 2h',
  },
  {
    botName: 'pricing_optimizer',
    intervalMs: SIX_HOURS,
    category: 'monetization',
    description: 'Adjust prices every 6h',
  },
  {
    botName: 'dashboard_refresher',
    intervalMs: 30 * 1000,
    category: 'monitoring',
    description: 'Refresh dashboard every 30s',
  },
];

/** Active timer handles: botName → intervalHandle */
const activeTimers = new Map();

/** Execution history: botName → last result */
const executionHistory = new Map();

/**
 * Schedule a bot to run at the given interval.
 * @param {string} botName - Unique bot identifier.
 * @param {number} intervalMs - Run interval in milliseconds.
 * @param {Function} botFn - Async or sync function to execute.
 * @returns {{ botName: string, intervalMs: number, scheduled: boolean }}
 */
function scheduleBot(botName, intervalMs, botFn) {
  if (activeTimers.has(botName)) {
    clearInterval(activeTimers.get(botName));
  }
  const handle = setInterval(async () => {
    const start = Date.now();
    let result;
    try {
      result = await botFn();
      executionHistory.set(botName, {
        success: true,
        result,
        duration: Date.now() - start,
        runAt: new Date().toISOString(),
      });
    } catch (err) {
      executionHistory.set(botName, {
        success: false,
        error: err.message,
        duration: Date.now() - start,
        runAt: new Date().toISOString(),
      });
    }
  }, intervalMs);
  activeTimers.set(botName, handle);
  return { botName, intervalMs, scheduled: true };
}

/**
 * Run all scheduled bots once immediately (synchronous test cycle).
 * @returns {Promise<Object[]>} Array of { botName, success, result } records.
 */
async function runScheduledCycle() {
  const results = [];
  for (const schedule of SCHEDULES) {
    const start = Date.now();
    try {
      // Simulate bot execution
      const result = { simulated: true, bot: schedule.botName, category: schedule.category };
      executionHistory.set(schedule.botName, {
        success: true,
        result,
        duration: Date.now() - start,
        runAt: new Date().toISOString(),
      });
      results.push({ botName: schedule.botName, success: true, result });
    } catch (err) {
      executionHistory.set(schedule.botName, {
        success: false,
        error: err.message,
        duration: Date.now() - start,
        runAt: new Date().toISOString(),
      });
      results.push({ botName: schedule.botName, success: false, error: err.message });
    }
  }
  return results;
}

/**
 * Start all bot timers based on SCHEDULES.
 * @returns {{ started: number, bots: string[] }}
 */
function startScheduler() {
  let started = 0;
  const bots = [];
  SCHEDULES.forEach((schedule) => {
    scheduleBot(schedule.botName, schedule.intervalMs, async () => {
      return {
        bot: schedule.botName,
        category: schedule.category,
        ran: true,
        at: new Date().toISOString(),
      };
    });
    started++;
    bots.push(schedule.botName);
  });
  return { started, bots };
}

/**
 * Stop all active bot timers.
 * @returns {{ stopped: number }}
 */
function stopScheduler() {
  let stopped = 0;
  activeTimers.forEach((handle, botName) => {
    clearInterval(handle);
    activeTimers.delete(botName);
    stopped++;
  });
  return { stopped };
}

/**
 * Get the current status of all scheduled bots.
 * @returns {Object[]} Array of status objects per bot.
 */
function getStatus() {
  return SCHEDULES.map((schedule) => {
    const history = executionHistory.get(schedule.botName) || null;
    return {
      botName: schedule.botName,
      category: schedule.category,
      intervalMs: schedule.intervalMs,
      description: schedule.description,
      isRunning: activeTimers.has(schedule.botName),
      lastRun: history,
    };
  });
}

module.exports = {
  SCHEDULES,
  scheduleBot,
  runScheduledCycle,
  startScheduler,
  stopScheduler,
  getStatus,
};
