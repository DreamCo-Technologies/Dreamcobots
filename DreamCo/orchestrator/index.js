'use strict';

/**
 * DreamCo Orchestrator
 *
 * Central brain for the DreamCo Money Operating System.
 * Wires all bots together, validates revenue output, and triggers scaling
 * for profitable bots.
 *
 * BOT → ACTION → RESULT → REVENUE → VALIDATION → SCALE
 */

const realEstateBot = require('../bots/realEstateBot');
const contractBot = require('../bots/contractBot');
const jobBot = require('../bots/jobBot');
const dealBot = require('../bots/dealBot');
const pennyBot = require('../bots/pennyBot');
const receiptBot = require('../bots/receiptBot');
const flipBot = require('../bots/flipBot');
const couponBot = require('../bots/couponBot');

// ---------------------------------------------------------------------------
// Revenue Validator
// ---------------------------------------------------------------------------

const REVENUE_THRESHOLDS = {
  scale: 1000,
  maintain: 100,
};

/**
 * Validate a bot's revenue output.
 * @param {Object} botOutput - Standardised bot output object
 * @returns {Object} Validation result with scale recommendation
 */
function validateRevenue(botOutput) {
  const { revenue = 0, conversion_rate = 0, leads_generated = 0 } = botOutput;

  let status = 'underperforming';
  let scale = false;

  if (revenue >= REVENUE_THRESHOLDS.scale) {
    status = 'scale';
    scale = true;
  } else if (revenue >= REVENUE_THRESHOLDS.maintain) {
    status = 'maintain';
  }

  return {
    bot: botOutput.bot,
    revenue,
    leads_generated,
    conversion_rate,
    status,
    scale,
    message: scale
      ? `🚀 Scale "${botOutput.bot}" — revenue $${revenue} exceeded threshold`
      : `📊 "${botOutput.bot}" status: ${status} (revenue: $${revenue})`,
  };
}

// ---------------------------------------------------------------------------
// Auto Scaler
// ---------------------------------------------------------------------------

/**
 * Clone a bot into a new niche when revenue threshold is exceeded.
 * @param {string} botName - Name of the bot to clone
 * @returns {string} Clone notification message
 */
function cloneBot(botName) {
  return `[AutoScaler] Cloning "${botName}" into new niche — deploying scaled instance`;
}

// ---------------------------------------------------------------------------
// Orchestrator
// ---------------------------------------------------------------------------

const BOTS = [
  { name: 'realEstateBot', module: realEstateBot },
  { name: 'contractBot', module: contractBot },
  { name: 'jobBot', module: jobBot },
  { name: 'dealBot', module: dealBot },
  { name: 'pennyBot', module: pennyBot },
  { name: 'receiptBot', module: receiptBot },
  { name: 'flipBot', module: flipBot },
  { name: 'couponBot', module: couponBot },
];

/**
 * Process a single bot: run it, validate output, and optionally scale.
 * @param {string} botName - Identifier for the bot
 * @param {Object} botModule - Module with a `run()` function
 * @param {Object} [options] - Options passed to bot.run()
 * @returns {Object} Full result including output and validation
 */
function processBot(botName, botModule, options = {}) {
  try {
    const output = botModule.run(options);
    const validation = validateRevenue(output);

    console.log(`[${botName}] →`, validation.message);

    if (validation.scale) {
      console.log(cloneBot(botName));
    }

    return { bot: botName, output, validation, error: null };
  } catch (err) {
    console.error(`[${botName}] ERROR:`, err.message);
    return { bot: botName, output: null, validation: null, error: err.message };
  }
}

/**
 * Run all registered bots and collect results.
 * @returns {Array<Object>} Results for every bot
 */
function runAllBots() {
  console.log('\n🚀 DreamCo Orchestrator — Starting full bot cycle\n');

  const results = BOTS.map(({ name, module }) => processBot(name, module));

  const totalRevenue = results.reduce((sum, r) => sum + (r.output ? r.output.revenue : 0), 0);
  const totalLeads = results.reduce((sum, r) => sum + (r.output ? r.output.leads_generated : 0), 0);
  const scalingBots = results.filter((r) => r.validation && r.validation.scale).map((r) => r.bot);

  console.log('\n─────────────────────────────────────');
  console.log(`💰 Total Revenue:   $${totalRevenue}`);
  console.log(`📋 Total Leads:     ${totalLeads}`);
  console.log(`📈 Scaling Bots:    ${scalingBots.length > 0 ? scalingBots.join(', ') : 'none'}`);
  console.log('─────────────────────────────────────\n');

  return {
    results,
    summary: {
      total_revenue: totalRevenue,
      total_leads: totalLeads,
      scaling_bots: scalingBots,
      bots_run: results.length,
      timestamp: new Date().toISOString(),
    },
  };
}

module.exports = { runAllBots, processBot, validateRevenue, cloneBot, BOTS };

// Run directly if invoked as a script
if (require.main === module) {
  runAllBots();
}
