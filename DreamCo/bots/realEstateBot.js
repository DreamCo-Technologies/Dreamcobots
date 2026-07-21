'use strict';

/**
 * DreamCo Real Estate Bot
 *
 * Discovers real estate leads, generates deal opportunities, and returns
 * a standardised revenue output for the DreamCo Money Operating System.
 *
 * BOT → ACTION → RESULT → REVENUE → VALIDATION → SCALE
 */

const PROPERTY_MARKETS = ['austin', 'phoenix', 'nashville', 'denver', 'tampa'];

const DEAL_TYPES = {
  wholesale: { minProfit: 5000, maxProfit: 20000 },
  rental: { minProfit: 500, maxProfit: 3000 },
  fix_and_flip: { minProfit: 15000, maxProfit: 50000 },
};

/**
 * Simulate finding motivated sellers and real estate leads.
 * @param {string} market - Target real estate market
 * @returns {Array<Object>} List of lead objects
 */
function findLeads(market = 'austin') {
  const count = Math.floor(Math.random() * 3) + 1;
  const leads = [];
  for (let i = 0; i < count; i++) {
    leads.push({
      id: `RE-${Date.now()}-${i}`,
      market,
      address: `${1000 + i * 100} Main St, ${market.charAt(0).toUpperCase() + market.slice(1)}`,
      estimatedValue: Math.floor(Math.random() * 200000) + 150000,
      dealType: Object.keys(DEAL_TYPES)[Math.floor(Math.random() * 3)],
      motivated: Math.random() > 0.4,
    });
  }
  return leads;
}

/**
 * Calculate expected revenue from a list of real estate leads.
 * @param {Array<Object>} leads
 * @returns {{ revenue: number, deals: number }}
 */
function calculateRevenue(leads) {
  let revenue = 0;
  let deals = 0;
  for (const lead of leads) {
    if (lead.motivated) {
      const dealType = DEAL_TYPES[lead.dealType] || DEAL_TYPES.wholesale;
      revenue += Math.floor(
        Math.random() * (dealType.maxProfit - dealType.minProfit) + dealType.minProfit
      );
      deals++;
    }
  }
  return { revenue, deals };
}

/**
 * Main bot entry point — runs a single cycle and returns revenue output.
 * @param {Object} [options]
 * @param {string} [options.market] - Market to search (default: random)
 * @returns {Object} Standardised bot output
 */
function run(options = {}) {
  const market =
    options.market || PROPERTY_MARKETS[Math.floor(Math.random() * PROPERTY_MARKETS.length)];

  const leads = findLeads(market);
  const { revenue, deals } = calculateRevenue(leads);

  const leadsGenerated = leads.length;
  const conversionRate = leadsGenerated > 0 ? parseFloat((deals / leadsGenerated).toFixed(2)) : 0;

  const botOutput = {
    bot: 'realEstateBot',
    market,
    revenue,
    leads_generated: leadsGenerated,
    conversion_rate: conversionRate,
    action: `Searched ${market} market — found ${leadsGenerated} lead(s), closed ${deals} deal(s)`,
    timestamp: new Date().toISOString(),
  };

  return botOutput;
}

module.exports = { run, findLeads, calculateRevenue, PROPERTY_MARKETS, DEAL_TYPES };
