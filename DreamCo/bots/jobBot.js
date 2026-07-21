'use strict';

/**
 * DreamCo Job Bot
 *
 * Searches job platforms, generates user leads, and monetises through resume
 * services, premium automation, and affiliate referrals.  Returns a
 * standardised revenue output for the DreamCo Money Operating System.
 *
 * BOT → ACTION → RESULT → REVENUE → VALIDATION → SCALE
 */

const JOB_PLATFORMS = ['indeed', 'linkedin', 'glassdoor', 'ziprecruiter', 'monster'];

const JOB_CATEGORIES = [
  'Software Engineer',
  'Data Analyst',
  'Project Manager',
  'Marketing Manager',
  'Sales Representative',
  'Operations Manager',
];

const MONETIZATION = {
  resume_service: 50,
  premium_automation: 99,
  affiliate_per_signup: 15,
};

/**
 * Simulate searching job platforms for open positions.
 * @param {string} role - Job title / keyword
 * @param {string} platform - Platform to search
 * @returns {Array<Object>} List of job postings
 */
function searchJobs(role = 'Software Engineer', platform = 'indeed') {
  const count = Math.floor(Math.random() * 5) + 3;
  const jobs = [];
  for (let i = 0; i < count; i++) {
    jobs.push({
      id: `JOB-${Date.now()}-${i}`,
      title: role,
      company: `Company ${String.fromCharCode(65 + i)}`,
      location: Math.random() > 0.4 ? 'Remote' : 'On-site',
      platform,
      salary: `$${Math.floor(Math.random() * 60000) + 50000} - $${Math.floor(Math.random() * 40000) + 110000}`,
      applied: false,
    });
  }
  return jobs;
}

/**
 * Simulate applying to a job and capturing user lead for monetisation.
 * @param {Object} job - Job posting object
 * @returns {{ applied: boolean, revenue: number, monetizationType: string }}
 */
function applyAndMonetize(job) {
  const success = Math.random() > 0.3;
  if (!success) return { applied: false, revenue: 0, monetizationType: null };

  const types = Object.keys(MONETIZATION);
  const chosen = types[Math.floor(Math.random() * types.length)];
  return {
    applied: true,
    revenue: MONETIZATION[chosen],
    monetizationType: chosen,
  };
}

/**
 * Main bot entry point — runs a single cycle and returns revenue output.
 * @param {Object} [options]
 * @param {string} [options.role] - Job role to search
 * @param {string} [options.platform] - Platform to search
 * @returns {Object} Standardised bot output
 */
function run(options = {}) {
  const role = options.role || JOB_CATEGORIES[Math.floor(Math.random() * JOB_CATEGORIES.length)];
  const platform =
    options.platform || JOB_PLATFORMS[Math.floor(Math.random() * JOB_PLATFORMS.length)];

  const jobs = searchJobs(role, platform);
  let totalRevenue = 0;
  let conversions = 0;

  for (const job of jobs) {
    const result = applyAndMonetize(job);
    if (result.applied) {
      totalRevenue += result.revenue;
      conversions++;
    }
  }

  const leadsGenerated = jobs.length;
  const conversionRate =
    leadsGenerated > 0 ? parseFloat((conversions / leadsGenerated).toFixed(2)) : 0;

  const botOutput = {
    bot: 'jobBot',
    role,
    platform,
    revenue: totalRevenue,
    leads_generated: leadsGenerated,
    conversion_rate: conversionRate,
    action: `Searched ${platform} for "${role}" — found ${leadsGenerated} job(s), monetised ${conversions}`,
    timestamp: new Date().toISOString(),
  };

  return botOutput;
}

module.exports = { run, searchJobs, applyAndMonetize, JOB_PLATFORMS, JOB_CATEGORIES, MONETIZATION };
