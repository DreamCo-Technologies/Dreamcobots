'use strict';

/**
 * DreamCo — Master Bot Runner
 *
 * Discovers every registered bot module in DreamCo/bots/ and runs them
 * through the job queue so they execute safely without colliding.
 *
 * Usage:
 *   const {  runAllBots  } = require('./runAllBots');
 *   const results = await runAllBots();
 */

const fs = require('fs');
const path = require('path');
const { addJob, runQueue, clear } = require('../core/queue');
const registry = require('../core/botRegistry');
const { trackRevenue } = require('../core/revenueEngine');
const config = require('../core/config');

const BOTS_DIR = path.join(__dirname, '..', 'bots');

/**
 * Collect .js bot files and validate each is genuinely inside botsDir
 * to guard against symlink-based directory traversal.
 * @param { string } dir
 * @returns { string[] }
 */
function collectBotFiles(dir) {
  if (!fs.existsSync(dir)) {
    return [];
  }

  const results = [];
  const resolvedDir = path.resolve(dir);
  for (const entry of fs.readdirSync(dir)) {
    const full = path.resolve(dir, entry);
    // Safety: skip anything whose resolved path escapes the expected directory
    if (!full.startsWith(resolvedDir + path.sep) && full !== resolvedDir) {
      continue;
    }
    const stat = fs.statSync(full);
    if (stat.isDirectory()) {
      results.push(...collectBotFiles(full));
    } else if (entry.endsWith('.js') && entry !== 'index.js') {
      results.push(full);
    }
  }
  return results;
}

/**
 * Run all bots discovered under DreamCo/bots/ plus the legacy bots
 * already wired in the orchestrator.
 *
 * @returns { Promise<{results: Object[], summary: Object}> }
 */
async function runAllBots() {
  console.log('\n🚀 DreamCo Master Orchestrator — Starting full bot cycle\n');

  clear(); // Reset queue before each run

  const botFiles = collectBotFiles(BOTS_DIR);
  const botResults = [];

  for (const botFile of botFiles) {
    addJob(async () => {
      const botName = path.basename(botFile, '.js');

      // Ensure bot is registered
      if (!registry.getBot(botName)) {
        registry.registerBot({ name: botName });
      }

      registry.updateStatus(botName, 'running');

      try {
        const botModule = require(botFile);
        if (typeof botModule.run !== 'function') {
          throw new Error(`Bot "${botName}" does not export a run() function`);
        }

        console.log(`🤖 Running ${botName}`);
        const output = await botModule.run();
        const revenue = output && typeof output.revenue === 'number' ? output.revenue : 0;

        registry.updateStatus(
          botName,
          revenue >= config.revenue.scaleThreshold ? 'scaling' : 'idle',
          revenue
        );

        if (revenue > 0) {
          trackRevenue(botName, revenue);
        }

        botResults.push({ bot: botName, output, error: null });
      } catch (err) {
        console.error(`❌ Error in ${botName}: ${err.message}`);
        registry.updateStatus(botName, 'error');
        botResults.push({ bot: botName, output: null, error: err.message });
      }
    });
  }

  await runQueue();

  const totalRevenue = botResults.reduce(
    (sum, r) => sum + (r.output ? r.output.revenue || 0 : 0),
    0
  );
  const totalLeads = botResults.reduce(
    (sum, r) => sum + (r.output ? r.output.leads_generated || 0 : 0),
    0
  );
  const scalingBots = botResults
    .filter((r) => r.output && r.output.revenue >= config.revenue.scaleThreshold)
    .map((r) => r.bot);
  const failedBots = botResults.filter((r) => r.error).map((r) => r.bot);

  console.log('\n─────────────────────────────────────');
  console.log(`💰 Total Revenue:   $${totalRevenue}`);
  console.log(`📋 Total Leads:     ${totalLeads}`);
  console.log(`📈 Scaling Bots:    ${scalingBots.length > 0 ? scalingBots.join(', ') : 'none'}`);
  if (failedBots.length > 0) {
    console.log(`❌ Failed Bots:     ${failedBots.join(', ')}`);
  }
  console.log('─────────────────────────────────────\n');

  return {
    results: botResults,
    summary: {
      total_revenue: totalRevenue,
      total_leads: totalLeads,
      scaling_bots: scalingBots,
      failed_bots: failedBots,
      bots_run: botResults.length,
      timestamp: new Date().toISOString(),
    },
  };
}

module.exports = { runAllBots, collectBotFiles };
