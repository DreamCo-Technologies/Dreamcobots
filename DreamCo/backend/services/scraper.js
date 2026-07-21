/**
 * DreamCo LeadGenBot — Scraper Service
 *
 * Defines simulated lead-scraping logic.  In production, replace the
 * _simulateScrape() function with real HTTP/headless-browser calls
 * (Puppeteer, Playwright, or API integrations).
 *
 * Supported industries: Real Estate, Finance, Local Business, General
 */

const { generateId, formatTimestamp } = require('../utils/helpers');

// ---------------------------------------------------------------------------
// Sample data pools (used for simulation)
// ---------------------------------------------------------------------------

const SAMPLE_NAMES = [
  'Alex Johnson',
  'Maria Garcia',
  'James Lee',
  'Sarah Kim',
  'David Chen',
  'Emily Davis',
  'Michael Brown',
  'Jessica Wilson',
  'Chris Martinez',
  'Ashley Taylor',
  'Robert Anderson',
  'Jennifer Thomas',
  'William Jackson',
  'Linda White',
  'Charles Harris',
  'Barbara Martin',
  'Daniel Thompson',
  'Susan Garcia',
  'Paul Martinez',
  'Karen Robinson',
];

const REAL_ESTATE_COMPANIES = [
  'Keller Williams Realty',
  'RE/MAX Holdings',
  'Century 21 Real Estate',
  'Coldwell Banker',
  'Berkshire Hathaway HomeServices',
  'Compass Real Estate',
  'eXp Realty',
  "Sotheby's International Realty",
  'Douglas Elliman',
  'HomeSmart',
];

const FINANCE_COMPANIES = [
  'Chase Financial',
  'Wells Fargo Advisors',
  'Merrill Lynch',
  'Edward Jones',
  'Raymond James',
  'Ameriprise Financial',
  'LPL Financial',
  'Northwestern Mutual',
  'New York Life',
  'Principal Financial Group',
];

const LOCAL_COMPANIES = [
  'Main Street Marketing',
  'Downtown Digital',
  'City Center Consulting',
  'Local Leads Pro',
  'Neighborhood Networking',
  'Community Business Hub',
  'Regional Growth Partners',
  'Metro Business Solutions',
  'Urban Startup Co',
  'Suburban Services Group',
];

const GENERAL_COMPANIES = [
  'TechNova Inc.',
  'GrowthHive',
  'CodeBridge',
  'MarketPulse',
  'StartupForge',
  'NexGen Labs',
  'BlueSky Digital',
  'IronFist Media',
  'ProdigyWorks',
  'VisionEdge',
];

const LOCATIONS = [
  'New York, NY',
  'Los Angeles, CA',
  'Chicago, IL',
  'Houston, TX',
  'Phoenix, AZ',
  'Philadelphia, PA',
  'San Antonio, TX',
  'San Diego, CA',
  'Dallas, TX',
  'San Jose, CA',
  'Austin, TX',
  'Jacksonville, FL',
  'Fort Worth, TX',
  'Columbus, OH',
  'Charlotte, NC',
];

const INDUSTRY_COMPANY_MAP = {
  'Real Estate': REAL_ESTATE_COMPANIES,
  Finance: FINANCE_COMPANIES,
  'Local Business': LOCAL_COMPANIES,
  General: GENERAL_COMPANIES,
};

// ---------------------------------------------------------------------------
// Simulation helpers
// ---------------------------------------------------------------------------

function _pickRandom(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

function _simulateScrape({ industry, count }) {
  const companies = INDUSTRY_COMPANY_MAP[industry] || GENERAL_COMPANIES;
  const leads = [];

  for (let i = 0; i < count; i++) {
    const name = _pickRandom(SAMPLE_NAMES);
    const [first, ...rest] = name.split(' ');
    const last = rest.join('') || `${i}`;
    const company = _pickRandom(companies);
    const safeCompany = company.toLowerCase().replace(/[^a-z0-9]/g, '');

    leads.push({
      id: generateId(),
      name,
      email: `${first.toLowerCase()}.${last.toLowerCase()}@${safeCompany}.com`,
      phone: `+1-${_rand(200, 999)}-${_rand(100, 999)}-${_rand(1000, 9999)}`,
      company,
      industry,
      location: _pickRandom(LOCATIONS),
      score: _rand(55, 98),
      source: 'scraper',
      created_at: formatTimestamp(),
      dreamco_powered: true,
    });
  }

  return leads;
}

function _rand(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/**
 * Scrape leads for a given industry and quantity.
 *
 * @param {object} options
 * @param {string} options.industry - Target industry (e.g., "Real Estate").
 * @param {number} options.count   - Number of leads to scrape (max 200).
 * @returns {Promise<Array>}
 */
async function scrapeLeads({ industry = 'General', count = 50 } = {}) {
  const safeCount = Math.min(Math.max(1, count), 200);
  // Simulate async I/O delay (replace with real scraping logic)
  await new Promise((resolve) => setTimeout(resolve, 100));
  return _simulateScrape({ industry, count: safeCount });
}

module.exports = { scrapeLeads };
