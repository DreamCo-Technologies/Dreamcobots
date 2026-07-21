'use strict';

/**
 * DreamCo — Automated Lead Scraping
 *
 * Simulates scraping leads from LinkedIn, Indeed, Google, and Zillow.
 * In production, replace simulation logic with real HTTP/Puppeteer calls.
 */

const crypto = require('crypto');
const path = require('path');
const fs = require('fs');

/** Data directory for persisting scrape results. */
const DATA_DIR = path.resolve('data');

/**
 * Generate a realistic simulated lead object.
 * @param {Object} overrides - Field overrides.
 * @returns {Object} Lead object.
 */
function _makeLead(overrides) {
  const id = crypto.randomBytes(6).toString('hex');
  return {
    leadId: id,
    name: overrides.name || `Lead_${id}`,
    email: overrides.email || `lead_${id}@example.com`,
    phone: overrides.phone || `555-${Math.floor(1000 + Math.random() * 9000)}`,
    source: overrides.source || 'scraper',
    category: overrides.category || 'general',
    score: overrides.score || Math.floor(30 + Math.random() * 60),
    scrapedAt: new Date().toISOString(),
  };
}

/**
 * Simulate LinkedIn lead scraping.
 * @param {string[]} keywords - Search keywords.
 * @returns {Object[]} Array of scraped leads.
 */
function scrapeLinkedIn(keywords) {
  const kws = Array.isArray(keywords) ? keywords : [keywords];
  const count = 3 + Math.floor(Math.random() * 5);
  const leads = [];
  for (let i = 0; i < count; i++) {
    leads.push(
      _makeLead({
        name: `LI Contact ${i + 1} (${kws[0] || 'general'})`,
        source: 'linkedin',
        category: 'business',
        score: 55 + Math.floor(Math.random() * 40),
      })
    );
  }
  return leads;
}

/**
 * Simulate Indeed job-seeker/employer lead scraping.
 * @param {string} jobTitle - Job title to search for.
 * @returns {Object[]} Array of scraped leads.
 */
function scrapeIndeed(jobTitle) {
  const count = 2 + Math.floor(Math.random() * 4);
  const leads = [];
  for (let i = 0; i < count; i++) {
    leads.push(
      _makeLead({
        name: `Indeed Lead ${i + 1} (${jobTitle})`,
        source: 'indeed',
        category: 'marketing',
        score: 40 + Math.floor(Math.random() * 35),
      })
    );
  }
  return leads;
}

/**
 * Simulate Google search lead scraping.
 * @param {string} query - Search query string.
 * @returns {Object[]} Array of scraped leads.
 */
function scrapeGoogle(query) {
  const count = 4 + Math.floor(Math.random() * 6);
  const leads = [];
  for (let i = 0; i < count; i++) {
    leads.push(
      _makeLead({
        name: `Google Lead ${i + 1}`,
        source: 'google',
        category: query.includes('estate') ? 'real_estate' : 'general',
        score: 35 + Math.floor(Math.random() * 50),
      })
    );
  }
  return leads;
}

/**
 * Simulate Zillow real estate lead scraping.
 * @param {string} zipCode - ZIP code to search.
 * @returns {Object[]} Array of scraped leads.
 */
function scrapeZillow(zipCode) {
  const count = 3 + Math.floor(Math.random() * 5);
  const leads = [];
  for (let i = 0; i < count; i++) {
    leads.push(
      _makeLead({
        name: `Zillow Seller ${i + 1} (${zipCode})`,
        source: 'zillow',
        category: 'real_estate',
        score: 60 + Math.floor(Math.random() * 35),
        phone: `${zipCode.slice(0, 3)}-${Math.floor(1000 + Math.random() * 9000)}`,
      })
    );
  }
  return leads;
}

/**
 * Run all scrapers, deduplicate by email, and return combined leads.
 * @param {Object} [config] - Scrape configuration.
 * @param {string[]} [config.linkedInKeywords] - LinkedIn keywords.
 * @param {string} [config.indeedJobTitle] - Indeed job title.
 * @param {string} [config.googleQuery] - Google query.
 * @param {string} [config.zillowZip] - Zillow ZIP code.
 * @returns {Promise<Object[]>} Deduplicated leads array.
 */
async function runFullScrape(config) {
  const cfg = config || {};
  const all = [
    ...scrapeLinkedIn(cfg.linkedInKeywords || ['digital marketing']),
    ...scrapeIndeed(cfg.indeedJobTitle || 'Marketing Manager'),
    ...scrapeGoogle(cfg.googleQuery || 'buy real estate'),
    ...scrapeZillow(cfg.zillowZip || '90210'),
  ];

  // Deduplicate by email
  const seen = new Set();
  const unique = all.filter((lead) => {
    if (seen.has(lead.email)) {
      return false;
    }
    seen.add(lead.email);
    return true;
  });

  return unique;
}

/**
 * Save scrape results to a JSON file in the data directory.
 * @param {Object[]} leads - Array of lead objects.
 * @returns {{ saved: number, file: string }}
 */
function saveScrapeResults(leads) {
  if (!fs.existsSync(DATA_DIR)) {
    fs.mkdirSync(DATA_DIR, { recursive: true });
  }
  const filename = `scrape_${Date.now()}.json`;
  const filepath = path.join(DATA_DIR, filename);
  fs.writeFileSync(filepath, JSON.stringify(leads, null, 2));
  return { saved: leads.length, file: filepath };
}

module.exports = {
  scrapeLinkedIn,
  scrapeIndeed,
  scrapeGoogle,
  scrapeZillow,
  runFullScrape,
  saveScrapeResults,
};
