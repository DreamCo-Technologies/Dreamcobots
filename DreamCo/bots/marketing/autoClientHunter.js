'use strict';

/**
 * DreamCo Auto Client Hunter Bot
 *
 * Lead scraping simulation + proposal generation + follow-up sequences.
 * Discovers high-value prospects across five business niches, crafts
 * personalised proposals, and builds automated follow-up campaigns.
 *
 * BOT → ACTION → RESULT → REVENUE → VALIDATION → SCALE
 */

/** Supported prospect niches. */
const NICHES = ['ecommerce', 'real_estate', 'health_wellness', 'tech_startups', 'local_business'];

const NICHE_PAIN_POINTS = {
  ecommerce: ['low conversion rate', 'high cart abandonment', 'poor ROAS', 'slow site speed'],
  real_estate: ['too few leads', 'low listing visibility', 'slow follow-up', 'manual CRM'],
  health_wellness: ['hard to stand out', 'booking friction', 'low retention', 'poor reviews'],
  tech_startups: ['not enough users', 'high churn', 'bad onboarding', 'unclear positioning'],
  local_business: [
    'no online presence',
    'poor Google ranking',
    'no referral system',
    'manual invoicing',
  ],
};

const COMPANY_SUFFIXES = ['Inc.', 'LLC', 'Co.', 'Group', 'Studios', 'Labs', 'Agency', 'Solutions'];

/**
 * Generate a simulated lead object.
 * @param {string} niche
 * @param {number} index
 * @returns {Object} Lead object
 */
function _createLead(niche, index) {
  const painPoints = NICHE_PAIN_POINTS[niche] || NICHE_PAIN_POINTS.local_business;
  const suffix = COMPANY_SUFFIXES[Math.floor(Math.random() * COMPANY_SUFFIXES.length)];
  return {
    id: `LEAD-${Date.now()}-${index}`,
    niche,
    company: `${niche.charAt(0).toUpperCase() + niche.slice(1).replace('_', ' ')} Venture ${index + 1} ${suffix}`,
    contact_name: `Contact ${index + 1}`,
    email: `contact${index + 1}@${niche.replace('_', '')}.example.com`,
    phone: `+1-555-${String(Math.floor(Math.random() * 9000) + 1000)}`,
    pain_point: painPoints[Math.floor(Math.random() * painPoints.length)],
    score: Math.floor(Math.random() * 40) + 60,
    qualified: Math.random() > 0.35,
    scraped_at: new Date().toISOString(),
  };
}

/**
 * Simulate scraping leads for a niche.
 * @param {string} niche - One of NICHES
 * @param {number} count - Number of leads to return
 * @returns {Object[]} Array of lead objects
 */
function scrapeLeads(niche = 'ecommerce', count = 10) {
  const leads = [];
  for (let i = 0; i < count; i++) {
    leads.push(_createLead(niche, i));
  }
  return leads;
}

/**
 * Generate a personalised proposal for a lead.
 * @param {Object} lead - Lead object from scrapeLeads()
 * @returns {string} Proposal text
 */
function generateProposal(lead) {
  return (
    `Hi ${lead.contact_name},\n\n` +
    `I noticed that ${lead.company} may be experiencing challenges with ${lead.pain_point}. ` +
    `We specialise in helping ${lead.niche.replace('_', ' ')} businesses solve exactly this.\n\n` +
    `Our clients typically see a 30–60% improvement within 90 days. ` +
    `I'd love to show you a quick demo tailored to ${lead.company}.\n\n` +
    `Would you be open to a 15-minute call this week?\n\n` +
    `Best,\nDreamCo Growth Team`
  );
}

/**
 * Build a multi-step follow-up message sequence for a lead.
 * @param {Object} lead - Lead object
 * @returns {Object[]} Array of follow-up message objects with delay days
 */
function createFollowUpSequence(lead) {
  return [
    {
      step: 1,
      delay_days: 2,
      channel: 'email',
      subject: `Quick follow-up — ${lead.company}`,
      message: `Hi ${lead.contact_name}, just circling back on my previous message. Did you get a chance to review it?`,
    },
    {
      step: 2,
      delay_days: 5,
      channel: 'linkedin',
      subject: null,
      message: `Hi ${lead.contact_name}, sent you an email about improving ${lead.pain_point} for ${lead.company}. Would love to connect!`,
    },
    {
      step: 3,
      delay_days: 9,
      channel: 'email',
      subject: `Case study for ${lead.niche.replace('_', ' ')} businesses`,
      message: `Hi ${lead.contact_name}, sharing a quick case study showing how we solved ${lead.pain_point} for a similar company. Let me know your thoughts!`,
    },
    {
      step: 4,
      delay_days: 14,
      channel: 'email',
      subject: `Last touch — ${lead.company}`,
      message: `Hi ${lead.contact_name}, I don't want to keep bothering you, so this will be my last note. If timing ever works out, feel free to reach back.`,
    },
  ];
}

/**
 * Main bot entry point — scrapes leads, generates proposals, and builds follow-up sequences.
 * @param {Object} [options]
 * @param {string} [options.niche] - Target niche (default: random)
 * @param {number} [options.count] - Leads to scrape (default: 10)
 * @returns {Object} Standardised bot output
 */
function run(options = {}) {
  const niche = options.niche || NICHES[Math.floor(Math.random() * NICHES.length)];
  const count = options.count || Math.floor(Math.random() * 20) + 10;

  const leads = scrapeLeads(niche, count);
  const qualifiedLeads = leads.filter((l) => l.qualified);
  const proposals = qualifiedLeads.map((l) => generateProposal(l));

  const revenue = Math.floor(Math.random() * (8000 - 3000 + 1)) + 3000;
  const leadsGenerated = Math.floor(Math.random() * (150 - 80 + 1)) + 80;
  const conversionRate =
    leads.length > 0 ? parseFloat((qualifiedLeads.length / leads.length).toFixed(2)) : 0;

  return {
    bot: 'autoClientHunter',
    niche,
    revenue,
    leads_generated: leadsGenerated,
    conversion_rate: conversionRate,
    scraped: leads.length,
    qualified: qualifiedLeads.length,
    proposals_generated: proposals.length,
    action: `Scraped ${leads.length} leads in "${niche}" — ${qualifiedLeads.length} qualified, ${proposals.length} proposals generated`,
    timestamp: new Date().toISOString(),
  };
}

module.exports = { run, scrapeLeads, generateProposal, createFollowUpSequence, NICHES };
