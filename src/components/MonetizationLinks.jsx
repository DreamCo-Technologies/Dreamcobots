/**
 * MonetizationLinks.jsx
 *
 * Renders purchase, subscription, and demo action buttons for a single bot.
 * Each link is constructed from the DreamCo payment base URL so the entire
 * catalog stays in sync when the base URL changes.
 *
 * Props:
 *  - bot  {object}  A single bot object from the division JSON data.
 *
 * Pricing-type → action mapping:
 *  - "SaaS subscription"    → Subscribe button
 *  - "Enterprise license"   → Contact Sales button
 *  - "Per-project fee"      → Purchase button
 *  - "Per-exchange fee"     → Purchase button
 *  - "Per-valuation fee"    → Purchase button
 *  - "Per-analysis fee"     → Purchase button
 *  - "Success fee + SaaS"   → Subscribe button
 *
 * Developer notes:
 * - Replace PAYMENT_BASE_URL with your production DreamCo payment endpoint.
 * - Add DEMO_BASE_URL if you host bot demo pages.
 * - Bundle pricing is handled separately in the DreamCo checkout flow;
 *   pass a `bundle` query param if needed.
 */

import React from 'react';

// ---------------------------------------------------------------------------
// Configuration — update these constants for your environment
// ---------------------------------------------------------------------------

/** Base URL for the DreamCo payment / checkout system. */
const PAYMENT_BASE_URL = process.env.REACT_APP_DREAMCO_PAYMENT_URL || 'https://pay.dreamco.ai';

/** Base URL for bot demo pages. */
const DEMO_BASE_URL = process.env.REACT_APP_DREAMCO_DEMO_URL || 'https://demo.dreamco.ai';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Map pricingType to the primary CTA label. */
function primaryCtaLabel(pricingType) {
  if (!pricingType) return 'Get Started';
  const lower = pricingType.toLowerCase();
  if (lower.includes('enterprise')) return 'Contact Sales';
  if (lower.includes('saas') || lower.includes('subscription')) return 'Subscribe';
  if (lower.includes('per-')) return 'Purchase';
  if (lower.includes('success fee')) return 'Subscribe';
  return 'Get Started';
}

/** Build the primary checkout URL for a bot. */
function checkoutUrl(bot) {
  const params = new URLSearchParams({
    product: bot.botId,
    division: bot.division,
    tier: bot.tier,
    price: bot.price,
    type: bot.pricingType,
  });
  return `${PAYMENT_BASE_URL}/checkout?${params.toString()}`;
}

/** Build the demo URL for a bot. */
function demoUrl(bot) {
  return `${DEMO_BASE_URL}/${bot.division.toLowerCase()}/${bot.botId}`;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

/**
 * MonetizationLinks
 *
 * Renders three action buttons:
 *  1. Primary CTA (Subscribe / Purchase / Contact Sales)
 *  2. Demo button
 *  3. Bundle info link (optional — shown for non-enterprise bots)
 */
export default function MonetizationLinks({ bot }) {
  if (!bot) return null;

  const isEnterprise = bot.pricingType && bot.pricingType.toLowerCase().includes('enterprise');

  const primaryLabel = primaryCtaLabel(bot.pricingType);
  const primaryHref = checkoutUrl(bot);
  const demoHref = demoUrl(bot);

  return (
    <div className="monetization-links">
      {/* Primary CTA */}
      <a
        href={primaryHref}
        className={`mono-btn mono-btn--primary ${isEnterprise ? 'mono-btn--enterprise' : ''}`}
        target="_blank"
        rel="noopener noreferrer"
        aria-label={`${primaryLabel} ${bot.botName}`}
      >
        {primaryLabel}
      </a>

      {/* Demo link */}
      <a
        href={demoHref}
        className="mono-btn mono-btn--demo"
        target="_blank"
        rel="noopener noreferrer"
        aria-label={`View demo for ${bot.botName}`}
      >
        Live Demo
      </a>

      {/* Bundle info — shown only for non-enterprise bots */}
      {!isEnterprise && (
        <a
          href={`${PAYMENT_BASE_URL}/bundles?division=${bot.division}`}
          className="mono-btn mono-btn--bundle"
          target="_blank"
          rel="noopener noreferrer"
          aria-label="View bundle packages"
        >
          Bundle &amp; Save
        </a>
      )}
    </div>
  );
}
