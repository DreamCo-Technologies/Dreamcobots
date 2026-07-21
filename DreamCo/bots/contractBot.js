'use strict';

/**
 * DreamCo Contract Bot
 *
 * Discovers government contracts and grants, scores them for bid-worthiness,
 * and returns a standardised revenue output for the DreamCo Money Operating
 * System.
 *
 * BOT → ACTION → RESULT → REVENUE → VALIDATION → SCALE
 */

const CONTRACT_CATEGORIES = [
  'IT Services',
  'Construction',
  'Consulting',
  'Logistics',
  'Healthcare',
  'Training',
];

const REVENUE_MODELS = {
  percentage_of_contract: 0.05, // 5% commission
  proposal_fee: 500,
  subscription_alert: 29,
};

/**
 * Simulate searching government contract databases (SAM.gov, grants.gov).
 * @param {string} keyword - Search keyword
 * @returns {Array<Object>} List of contract opportunities
 */
function searchContracts(keyword = 'IT') {
  const count = Math.floor(Math.random() * 4) + 1;
  const opportunities = [];
  for (let i = 0; i < count; i++) {
    const contractValue = Math.floor(Math.random() * 500000) + 50000;
    opportunities.push({
      id: `GOV-${Date.now()}-${i}`,
      title: `${keyword} ${CONTRACT_CATEGORIES[Math.floor(Math.random() * CONTRACT_CATEGORIES.length)]} Contract`,
      agency: `Federal Agency ${String.fromCharCode(65 + i)}`,
      value: contractValue,
      deadline: new Date(Date.now() + (Math.random() * 30 + 7) * 86400000).toISOString(),
      matchScore: parseFloat((Math.random() * 0.5 + 0.5).toFixed(2)),
    });
  }
  return opportunities;
}

/**
 * Calculate expected revenue from contract leads.
 * @param {Array<Object>} opportunities
 * @returns {{ revenue: number, qualifiedLeads: number }}
 */
function calculateRevenue(opportunities) {
  let revenue = 0;
  let qualifiedLeads = 0;
  for (const opp of opportunities) {
    if (opp.matchScore >= 0.7) {
      revenue += Math.floor(opp.value * REVENUE_MODELS.percentage_of_contract);
      qualifiedLeads++;
    } else {
      revenue += REVENUE_MODELS.proposal_fee;
    }
  }
  return { revenue, qualifiedLeads };
}

/**
 * Generate a simple contract proposal outline.
 * @param {Object} opportunity - Contract opportunity object
 * @returns {string} Proposal text
 */
function generateProposal(opportunity) {
  return [
    `PROPOSAL FOR: ${opportunity.title}`,
    `Agency: ${opportunity.agency}`,
    `Contract Value: $${opportunity.value.toLocaleString()}`,
    `Deadline: ${opportunity.deadline}`,
    '',
    'DreamCo is pleased to submit this proposal offering best-in-class',
    'automated solutions powered by our AI bot ecosystem.',
    '',
    'Signed,',
    'DreamCo Technologies',
  ].join('\n');
}

/**
 * Main bot entry point — runs a single cycle and returns revenue output.
 * @param {Object} [options]
 * @param {string} [options.keyword] - Search keyword for contracts
 * @returns {Object} Standardised bot output
 */
function run(options = {}) {
  const keyword =
    options.keyword || CONTRACT_CATEGORIES[Math.floor(Math.random() * CONTRACT_CATEGORIES.length)];

  const opportunities = searchContracts(keyword);
  const { revenue, qualifiedLeads } = calculateRevenue(opportunities);

  const leadsGenerated = opportunities.length;
  const conversionRate =
    leadsGenerated > 0 ? parseFloat((qualifiedLeads / leadsGenerated).toFixed(2)) : 0;

  const botOutput = {
    bot: 'contractBot',
    keyword,
    revenue,
    leads_generated: leadsGenerated,
    conversion_rate: conversionRate,
    action: `Searched for "${keyword}" contracts — found ${leadsGenerated} opportunity(ies), qualified ${qualifiedLeads}`,
    timestamp: new Date().toISOString(),
  };

  return botOutput;
}

module.exports = { run, searchContracts, calculateRevenue, generateProposal, CONTRACT_CATEGORIES };
