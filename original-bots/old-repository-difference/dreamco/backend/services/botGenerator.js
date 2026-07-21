/**
 * DreamCo LeadGenBot — Bot Generator Service
 *
 * Dynamically generates new bot functionality based on templates and
 * commands.  Bots are registered in an in-memory registry and can be
 * retrieved or executed on demand.
 *
 * Supported bot templates:
 *   LeadGenBot       — lead scraping and qualification
 *   RealEstateBot    — property and realtor lead generation
 *   FinanceBot       — financial advisor and broker leads
 *   LocalBizBot      — local business outreach automation
 *   SalesBot         — sales pipeline automation
 */

const { generateId, formatTimestamp } = require('../utils/helpers');

// ---------------------------------------------------------------------------
// In-memory bot registry
// ---------------------------------------------------------------------------
const _botRegistry = new Map();

// Pre-register LeadGenBot as the flagship MVP bot
const _leadGenBot = {
  id: 'leadgenbot-001',
  name: 'LeadGenBot',
  industry: 'General',
  template: 'LeadGenBot',
  tier: 'pro',
  command: "createBot('LeadGenBot')",
  description:
    'AI-powered lead scraper and qualification engine. Generates 50–200 qualified leads per week for realtors, agencies, and small businesses.',
  features: ['lead_scraping', 'email_validation', 'csv_export', 'dashboard', 'stripe_monetization'],
  status: 'active',
  created_at: formatTimestamp(),
  dreamco_powered: true,
};
_botRegistry.set(_leadGenBot.id, _leadGenBot);

// ---------------------------------------------------------------------------
// Bot templates
// ---------------------------------------------------------------------------

const BOT_TEMPLATES = {
  LeadGenBot: {
    template: 'LeadGenBot',
    description: 'AI-powered lead scraping and qualification engine.',
    features: ['lead_scraping', 'email_validation', 'csv_export', 'stripe_monetization'],
    default_command: 'scrape_leads',
  },
  RealEstateBot: {
    template: 'RealEstateBot',
    description: 'Automated realtor and property lead generation for real estate professionals.',
    features: ['property_leads', 'realtor_contacts', 'mls_integration', 'email_campaigns'],
    default_command: 'find_realtors',
  },
  FinanceBot: {
    template: 'FinanceBot',
    description: 'Financial advisor and broker lead generation platform.',
    features: ['advisor_leads', 'broker_contacts', 'compliance_check', 'crm_export'],
    default_command: 'find_advisors',
  },
  LocalBizBot: {
    template: 'LocalBizBot',
    description: 'Local business discovery and outreach automation.',
    features: ['yelp_scraping', 'google_maps', 'business_enrichment', 'outreach_sequences'],
    default_command: 'find_local_businesses',
  },
  SalesBot: {
    template: 'SalesBot',
    description: 'Full sales pipeline automation from prospect to close.',
    features: ['prospect_research', 'email_sequences', 'crm_sync', 'deal_tracking'],
    default_command: 'manage_pipeline',
  },
};

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/**
 * Generate and register a new bot.
 *
 * @param {object} options
 * @param {string} options.name      - Bot name.
 * @param {string} options.industry  - Target industry.
 * @param {string} options.command   - Bot command/action.
 * @param {string} options.tier      - Subscription tier (free|pro|agency).
 * @returns {object} The created bot record.
 */
function generateBot({ name, industry = 'General', command, tier = 'free' }) {
  // Determine the best matching template
  const templateKey = _matchTemplate(name, industry);
  const template = BOT_TEMPLATES[templateKey];

  const bot = {
    id: generateId(),
    name,
    industry,
    template: templateKey,
    tier: tier.toLowerCase(),
    command: command || template.default_command,
    description: template.description,
    features: [...template.features],
    status: 'active',
    created_at: formatTimestamp(),
    dreamco_powered: true,
  };

  _botRegistry.set(bot.id, bot);
  return bot;
}

/**
 * Return all registered bots.
 * @returns {Array}
 */
function listBots() {
  return Array.from(_botRegistry.values());
}

/**
 * Retrieve a bot by ID.
 * @param {string} id
 * @returns {object|null}
 */
function getBot(id) {
  return _botRegistry.get(id) || null;
}

/**
 * Execute a bot with optional payload.
 * @param {object} bot
 * @param {object} payload
 * @returns {object} Execution result.
 */
function runBot(bot, payload = {}) {
  return {
    bot_id: bot.id,
    bot_name: bot.name,
    command: bot.command,
    status: 'executed',
    message: `${bot.name} executed command '${bot.command}' successfully.`,
    payload_received: payload,
    timestamp: formatTimestamp(),
    dreamco_powered: true,
  };
}

// ---------------------------------------------------------------------------
// Internal helpers
// ---------------------------------------------------------------------------

function _matchTemplate(name, industry) {
  const n = name.toLowerCase();
  const ind = (industry || '').toLowerCase();

  if (n.includes('real estate') || ind.includes('real estate')) {
    return 'RealEstateBot';
  }
  if (n.includes('finance') || n.includes('financial') || ind.includes('finance')) {
    return 'FinanceBot';
  }
  if (n.includes('local') || n.includes('biz') || ind.includes('local')) {
    return 'LocalBizBot';
  }
  if (n.includes('sales') || ind.includes('sales')) {
    return 'SalesBot';
  }
  return 'LeadGenBot';
}

module.exports = { generateBot, listBots, getBot, runBot };
