'use strict';

/**
 * DreamCo — Email Campaign Automation
 *
 * Manages email campaigns: creation, audience management,
 * simulated sending, open/click tracking, and follow-up generation.
 */

const crypto = require('crypto');

/** In-memory campaign store: campaignId → campaign */
const campaigns = new Map();

/** In-memory email event store: emailId → event log */
const emailEvents = new Map();

/**
 * Create a new email campaign.
 * @param {string} name - Campaign name.
 * @param {Object} template - Email template { subject, body, html? }.
 * @param {string[]} [audience] - Initial list of email addresses.
 * @returns {Object} The created campaign.
 */
function createCampaign(name, template, audience) {
  if (!name) {
    throw new Error('Campaign name is required.');
  }
  if (!template || !template.subject) {
    throw new Error('Campaign template must have a subject.');
  }
  const campaignId = `camp_${crypto.randomBytes(6).toString('hex')}`;
  const campaign = {
    campaignId,
    name,
    template,
    recipients: [],
    status: 'draft',
    stats: { sent: 0, opened: 0, clicked: 0, converted: 0, bounced: 0 },
    createdAt: new Date().toISOString(),
    sentAt: null,
  };
  (audience || []).forEach((email) => {
    campaign.recipients.push({
      email,
      emailId: crypto.randomBytes(6).toString('hex'),
      personalization: {},
    });
  });
  campaigns.set(campaignId, campaign);
  return campaign;
}

/**
 * Add a recipient to a campaign audience.
 * @param {string} campaignId - Campaign identifier.
 * @param {string} email - Recipient email address.
 * @param {Object} [personalization] - Merge tags { firstName, lastName, etc. }.
 * @returns {{ campaignId: string, emailId: string, email: string }}
 */
function addToAudience(campaignId, email, personalization) {
  const campaign = campaigns.get(campaignId);
  if (!campaign) {
    throw new Error(`Campaign '${campaignId}' not found.`);
  }
  const emailId = crypto.randomBytes(6).toString('hex');
  campaign.recipients.push({ email, emailId, personalization: personalization || {} });
  return { campaignId, emailId, email };
}

/**
 * Simulate sending all emails in a campaign.
 * @param {string} campaignId - Campaign identifier.
 * @returns {{ campaignId: string, sent: number, failed: number }}
 */
function sendCampaign(campaignId) {
  const campaign = campaigns.get(campaignId);
  if (!campaign) {
    throw new Error(`Campaign '${campaignId}' not found.`);
  }
  if (campaign.recipients.length === 0) {
    throw new Error('Campaign has no recipients.');
  }

  let sent = 0;
  let failed = 0;
  campaign.recipients.forEach((recipient) => {
    // Simulate 2% bounce rate
    if (Math.random() < 0.02) {
      failed++;
      campaign.stats.bounced++;
    } else {
      sent++;
      campaign.stats.sent++;
      emailEvents.set(recipient.emailId, {
        emailId: recipient.emailId,
        campaignId,
        email: recipient.email,
        opens: 0,
        clicks: [],
      });
    }
  });

  campaign.status = 'sent';
  campaign.sentAt = new Date().toISOString();
  return { campaignId, sent, failed };
}

/**
 * Track an email open event.
 * @param {string} emailId - Email identifier.
 * @returns {{ emailId: string, opens: number }}
 */
function trackOpen(emailId) {
  const event = emailEvents.get(emailId);
  if (!event) {
    throw new Error(`Email '${emailId}' not found.`);
  }
  event.opens += 1;
  const campaign = campaigns.get(event.campaignId);
  if (campaign && event.opens === 1) {
    campaign.stats.opened++;
  }
  return { emailId, opens: event.opens };
}

/**
 * Track a link click within an email.
 * @param {string} emailId - Email identifier.
 * @param {string} link - URL that was clicked.
 * @returns {{ emailId: string, clickCount: number }}
 */
function trackClick(emailId, link) {
  const event = emailEvents.get(emailId);
  if (!event) {
    throw new Error(`Email '${emailId}' not found.`);
  }
  event.clicks.push({ link, at: new Date().toISOString() });
  const campaign = campaigns.get(event.campaignId);
  if (campaign && event.clicks.length === 1) {
    campaign.stats.clicked++;
  }
  return { emailId, clickCount: event.clicks.length };
}

/**
 * Get campaign statistics.
 * @param {string} campaignId - Campaign identifier.
 * @returns {{ campaignId: string, name: string, stats: Object }}
 */
function getStats(campaignId) {
  const campaign = campaigns.get(campaignId);
  if (!campaign) {
    throw new Error(`Campaign '${campaignId}' not found.`);
  }
  const openRate =
    campaign.stats.sent > 0
      ? Number(((campaign.stats.opened / campaign.stats.sent) * 100).toFixed(1))
      : 0;
  const clickRate =
    campaign.stats.opened > 0
      ? Number(((campaign.stats.clicked / campaign.stats.opened) * 100).toFixed(1))
      : 0;
  return {
    campaignId,
    name: campaign.name,
    status: campaign.status,
    stats: { ...campaign.stats, openRate, clickRate },
  };
}

/**
 * Auto-generate a follow-up email sequence for a campaign.
 * @param {string} campaignId - Campaign identifier.
 * @returns {{ campaignId: string, followUps: Object[] }}
 */
function generateFollowUp(campaignId) {
  const campaign = campaigns.get(campaignId);
  if (!campaign) {
    throw new Error(`Campaign '${campaignId}' not found.`);
  }
  const followUps = [
    {
      sequence: 1,
      sendAfterDays: 3,
      subject: `Re: ${campaign.template.subject} — Quick follow-up`,
      body: 'Just wanted to circle back and make sure you received my previous email...',
    },
    {
      sequence: 2,
      sendAfterDays: 7,
      subject: `Last chance: ${campaign.template.subject}`,
      body: 'This is my final follow-up. I wanted to offer you an exclusive 10% discount...',
    },
    {
      sequence: 3,
      sendAfterDays: 14,
      subject: `Checking in — ${campaign.template.subject}`,
      body: "I noticed you opened our email but haven't responded. Here's what you might be missing...",
    },
  ];
  return { campaignId, followUps };
}

module.exports = {
  createCampaign,
  addToAudience,
  sendCampaign,
  trackOpen,
  trackClick,
  getStats,
  generateFollowUp,
};
