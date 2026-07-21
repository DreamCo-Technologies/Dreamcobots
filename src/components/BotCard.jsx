/**
 * BotCard.jsx
 *
 * Renders a single bot as a styled card showing:
 *  - Name, division, category, and tier badge
 *  - Description and pricing
 *  - Top 3 features (expandable to all)
 *  - MonetizationLinks (Subscribe / Purchase / Demo / Bundle)
 *
 * Props:
 *  - bot  {object}  A single bot object from the division JSON data.
 *
 * Developer notes:
 * - Tier badge colours are controlled via CSS classes: .tier--pro,
 *   .tier--enterprise, .tier--elite.
 * - Feature list is collapsed to 3 items by default; clicking "Show all"
 *   expands it inline without a modal so the page stays accessible.
 * - MonetizationLinks handles all payment/demo URL construction.
 */

import React, { useState } from 'react';
import MonetizationLinks from './MonetizationLinks';

/** How many features to show before the "Show all" toggle. */
const FEATURE_PREVIEW_COUNT = 3;

/** Map tier names to CSS modifier classes. */
const TIER_CLASS = {
  Pro: 'tier--pro',
  Enterprise: 'tier--enterprise',
  Elite: 'tier--elite',
};

export default function BotCard({ bot }) {
  const [featuresExpanded, setFeaturesExpanded] = useState(false);

  if (!bot) return null;

  const {
    botName,
    botId,
    division,
    category,
    tier,
    description,
    pricingType,
    audience,
    price,
    features = [],
  } = bot;

  const tierClass = TIER_CLASS[tier] || 'tier--pro';
  const visibleFeatures = featuresExpanded ? features : features.slice(0, FEATURE_PREVIEW_COUNT);
  const hasMore = features.length > FEATURE_PREVIEW_COUNT;

  return (
    <article className="bot-card" data-bot-id={botId} data-division={division}>
      {/* ── Header ── */}
      <header className="bot-card__header">
        <div className="bot-card__meta">
          <span className="bot-card__division">{division}</span>
          <span className="bot-card__category">{category}</span>
        </div>
        <span className={`bot-card__tier-badge ${tierClass}`}>{tier}</span>
      </header>

      {/* ── Bot name & description ── */}
      <h3 className="bot-card__name">{botName}</h3>
      <p className="bot-card__description">{description}</p>

      {/* ── Pricing info ── */}
      <div className="bot-card__pricing">
        <span className="bot-card__price">{price}</span>
        <span className="bot-card__pricing-type">{pricingType}</span>
      </div>

      {/* ── Target audience ── */}
      <p className="bot-card__audience">
        <strong>For:</strong> {audience}
      </p>

      {/* ── Features list ── */}
      <ul className="bot-card__features">
        {visibleFeatures.map((feature) => (
          <li key={feature} className="bot-card__feature">
            <span className="bot-card__feature-icon" aria-hidden="true">
              ✓
            </span>
            {feature}
          </li>
        ))}
      </ul>

      {/* Feature expand/collapse toggle */}
      {hasMore && (
        <button
          className="bot-card__features-toggle"
          onClick={() => setFeaturesExpanded((prev) => !prev)}
          aria-expanded={featuresExpanded}
          aria-controls={`features-${botId}`}
        >
          {featuresExpanded
            ? 'Show less'
            : `+${features.length - FEATURE_PREVIEW_COUNT} more features`}
        </button>
      )}

      {/* ── Monetization links ── */}
      <MonetizationLinks bot={bot} />
    </article>
  );
}
