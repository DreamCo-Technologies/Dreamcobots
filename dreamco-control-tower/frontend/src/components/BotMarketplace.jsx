/**
 * BotMarketplace.jsx
 *
 * Build-a-Bot marketplace — browse, compare, and purchase DreamCo bots.
 *
 * Features:
 *  - Fetches bot catalog from /api/catalog (with fallback to static demo data)
 *  - Filter by category and tier
 *  - Side-by-side comparison of up to 3 bots (toggle via Compare checkbox)
 *  - Pricing display and CTA buttons (Subscribe / Buy / Demo)
 *  - Responsive grid layout
 */

import { useEffect, useState, useMemo } from 'react';

// ---------------------------------------------------------------------------
// Static fallback data used when the API is unavailable.
// Reflects the real DreamCo bot catalog.
// ---------------------------------------------------------------------------

const FALLBACK_CATALOG = [
  {
    bot_id: 'buddy_bot',
    display_name: 'Buddy Bot',
    category: 'AI Companion',
    tier: 'PRO',
    description: 'The most human-like AI companion — emotion-aware, voice-enabled, and fully personalised.',
    price_usd: 49,
    features: ['Emotion detection', 'Voice synthesis', '3D avatar', 'Memory system', 'Creativity engine'],
    is_live: true,
  },
  {
    bot_id: 'god_mode_bot',
    display_name: 'God Mode Bot',
    category: 'Automation',
    tier: 'ENTERPRISE',
    description: 'Full-stack autonomous client acquisition and closing engine.',
    price_usd: 199,
    features: ['AutoClientHunter', 'AutoCloser', 'PaymentAutoCollector', 'ViralEngine', 'Self-ImprovingAI'],
    is_live: true,
  },
  {
    bot_id: 'cinecore_bot',
    display_name: 'CineCore Bot',
    category: 'Content',
    tier: 'PRO',
    description: 'End-to-end video creation pipeline from script to published content.',
    price_usd: 79,
    features: ['ScriptEngine', 'VideoEngine', 'VoiceEngine', 'PlatformOptimizer', 'BulkGenerator'],
    is_live: true,
  },
  {
    bot_id: 'stack_and_profit_bot',
    display_name: 'Stack & Profit Bot',
    category: 'Finance',
    tier: 'PRO',
    description: 'Deal-stacking money OS with 5 sub-bots and AI profit ranking.',
    price_usd: 39,
    features: ['DealBot', 'PennyBot', 'ReceiptBot', 'FlipBot', 'ProfitEngine'],
    is_live: true,
  },
  {
    bot_id: 'real_estate_bot',
    display_name: 'Real Estate Bot',
    category: 'Real Estate',
    tier: 'PRO',
    description: 'AI-powered property sourcing, valuation, and lead generation for investors.',
    price_usd: 69,
    features: ['ForecastingEngine', 'LeadScraper', 'ValuationAI', 'DealScorer', 'CRM'],
    is_live: false,
  },
  {
    bot_id: 'sales_bot',
    display_name: 'Sales Bot',
    category: 'Sales',
    tier: 'FREE',
    description: 'Automated outreach, follow-up sequences, and pipeline management.',
    price_usd: 0,
    features: ['LeadQualifier', 'EmailSequencer', 'FollowUpBot', 'PipelineDashboard'],
    is_live: true,
  },
  {
    bot_id: 'crypto_bot',
    display_name: 'Crypto Bot',
    category: 'Finance',
    tier: 'ENTERPRISE',
    description: 'Autonomous crypto trading, mining optimisation, and portfolio management.',
    price_usd: 149,
    features: ['TradingEngine', 'MiningOptimizer', 'PortfolioAI', 'AlertSystem', 'RiskManager'],
    is_live: false,
  },
  {
    bot_id: 'commercial_bot',
    display_name: 'Commercial Bot',
    category: 'Content',
    tier: 'PRO',
    description: 'Professional commercial video production from concept to delivery.',
    price_usd: 59,
    features: ['ScriptEngine', 'VideoEngine', 'VoiceEngine', 'ClientFinder', 'BulkGenerator'],
    is_live: true,
  },
];

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const TIER_COLOR = {
  FREE: 'bg-slate-700 text-slate-300',
  PRO: 'bg-indigo-900 text-indigo-300',
  ENTERPRISE: 'bg-amber-900 text-amber-300',
  ELITE: 'bg-purple-900 text-purple-300',
};

function TierBadge({ tier }) {
  const cls = TIER_COLOR[tier] ?? 'bg-slate-700 text-slate-300';
  return (
    <span className={`text-xs px-2 py-0.5 rounded-full font-semibold ${cls}`}>{tier}</span>
  );
}

function PriceTag({ price }) {
  if (price === 0) return <span className="text-dreamco-green font-bold text-lg">Free</span>;
  return (
    <span className="font-bold text-lg text-white">
      ${price}
      <span className="text-xs text-slate-400 font-normal">/mo</span>
    </span>
  );
}

// ---------------------------------------------------------------------------
// ComparePanel — side-by-side comparison of up to 3 bots
// ---------------------------------------------------------------------------

function ComparePanel({ bots, onRemove }) {
  if (bots.length === 0) return null;

  const allFeatures = [...new Set(bots.flatMap((b) => b.features))];

  return (
    <div className="mb-6 bg-dreamco-card rounded-xl border border-dreamco-accent/40 p-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-white">🔍 Compare ({bots.length} selected)</h3>
        <button
          onClick={() => bots.forEach((b) => onRemove(b.bot_id))}
          className="text-xs text-slate-400 hover:text-white"
        >
          Clear all
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr>
              <th className="text-left text-xs text-slate-400 pb-2 pr-4 w-32">Feature</th>
              {bots.map((b) => (
                <th key={b.bot_id} className="text-center pb-2 px-3">
                  <div className="font-semibold text-white text-xs">{b.display_name}</div>
                  <PriceTag price={b.price_usd} />
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {allFeatures.map((feat) => (
              <tr key={feat} className="border-t border-slate-700">
                <td className="py-1.5 pr-4 text-xs text-slate-400">{feat}</td>
                {bots.map((b) => (
                  <td key={b.bot_id} className="text-center py-1.5 px-3">
                    {b.features.includes(feat) ? (
                      <span className="text-dreamco-green">✓</span>
                    ) : (
                      <span className="text-slate-600">—</span>
                    )}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// BotCard (marketplace variant)
// ---------------------------------------------------------------------------

function MarketplaceBotCard({ bot, isCompared, onCompareToggle }) {
  return (
    <div
      className={`bg-dreamco-card rounded-xl p-5 border transition-all ${
        isCompared ? 'border-dreamco-accent' : 'border-slate-700'
      }`}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div>
          <h3 className="font-semibold text-white">{bot.display_name}</h3>
          <span className="text-xs text-slate-400">{bot.category}</span>
        </div>
        <div className="flex flex-col items-end gap-1">
          <TierBadge tier={bot.tier} />
          {bot.is_live && (
            <span className="text-xs text-dreamco-green font-medium">● Live</span>
          )}
        </div>
      </div>

      {/* Description */}
      <p className="text-xs text-slate-400 mb-3 leading-relaxed">{bot.description}</p>

      {/* Features */}
      <ul className="space-y-1 mb-4">
        {bot.features.slice(0, 4).map((f) => (
          <li key={f} className="flex items-center gap-1.5 text-xs text-slate-300">
            <span className="text-dreamco-green">✓</span> {f}
          </li>
        ))}
        {bot.features.length > 4 && (
          <li className="text-xs text-slate-500">+{bot.features.length - 4} more</li>
        )}
      </ul>

      {/* Price + CTAs */}
      <div className="flex items-center justify-between pt-3 border-t border-slate-700">
        <PriceTag price={bot.price_usd} />
        <div className="flex gap-2">
          <label className="flex items-center gap-1 text-xs text-slate-400 cursor-pointer hover:text-white">
            <input
              type="checkbox"
              checked={isCompared}
              onChange={() => onCompareToggle(bot)}
              className="accent-indigo-500"
            />
            Compare
          </label>
          <button className="text-xs px-3 py-1.5 bg-dreamco-accent text-white rounded-lg hover:bg-indigo-500 transition-colors font-medium">
            {bot.price_usd === 0 ? 'Get Free' : 'Subscribe'}
          </button>
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

const MAX_COMPARE = 3;

export default function BotMarketplace() {
  const [catalog, setCatalog] = useState(FALLBACK_CATALOG);
  const [loading, setLoading] = useState(true);
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [tierFilter, setTierFilter] = useState('all');
  const [search, setSearch] = useState('');
  const [compareSet, setCompareSet] = useState([]); // array of bot objects

  useEffect(() => {
    fetch('/api/catalog')
      .then((r) => r.json())
      .then((data) => {
        const bots = Array.isArray(data) ? data : data.bots ?? [];
        if (bots.length > 0) setCatalog(bots);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  // Derived filter options
  const categories = useMemo(
    () => ['all', ...new Set(catalog.map((b) => b.category))],
    [catalog],
  );
  const tiers = useMemo(
    () => ['all', ...new Set(catalog.map((b) => b.tier))],
    [catalog],
  );

  const visible = useMemo(
    () =>
      catalog.filter((b) => {
        const matchCat = categoryFilter === 'all' || b.category === categoryFilter;
        const matchTier = tierFilter === 'all' || b.tier === tierFilter;
        const matchSearch =
          !search ||
          b.display_name.toLowerCase().includes(search.toLowerCase()) ||
          b.description.toLowerCase().includes(search.toLowerCase());
        return matchCat && matchTier && matchSearch;
      }),
    [catalog, categoryFilter, tierFilter, search],
  );

  function handleCompareToggle(bot) {
    setCompareSet((prev) => {
      const exists = prev.find((b) => b.bot_id === bot.bot_id);
      if (exists) return prev.filter((b) => b.bot_id !== bot.bot_id);
      if (prev.length >= MAX_COMPARE) return prev; // cap at MAX_COMPARE
      return [...prev, bot];
    });
  }

  function removeFromCompare(bot_id) {
    setCompareSet((prev) => prev.filter((b) => b.bot_id !== bot_id));
  }

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-white">🛒 Bot Marketplace</h2>
        <span className="text-xs text-slate-400">
          {visible.length} of {catalog.length} bots
        </span>
      </div>

      {/* Compare panel */}
      <ComparePanel bots={compareSet} onRemove={removeFromCompare} />

      {/* Filters */}
      <div className="flex flex-wrap gap-3 mb-5">
        <input
          type="text"
          placeholder="Search bots…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="bg-slate-700 border border-slate-600 text-white text-sm rounded-lg px-3 py-1.5 focus:outline-none focus:border-dreamco-accent"
        />

        <select
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value)}
          className="bg-slate-700 border border-slate-600 text-white text-sm rounded-lg px-3 py-1.5 focus:outline-none focus:border-dreamco-accent"
        >
          {categories.map((c) => (
            <option key={c} value={c}>
              Category: {c}
            </option>
          ))}
        </select>

        <select
          value={tierFilter}
          onChange={(e) => setTierFilter(e.target.value)}
          className="bg-slate-700 border border-slate-600 text-white text-sm rounded-lg px-3 py-1.5 focus:outline-none focus:border-dreamco-accent"
        >
          {tiers.map((t) => (
            <option key={t} value={t}>
              Tier: {t}
            </option>
          ))}
        </select>
      </div>

      {loading && <p className="text-slate-400 text-sm">Loading marketplace…</p>}

      {/* Bot grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {visible.map((bot) => (
          <MarketplaceBotCard
            key={bot.bot_id}
            bot={bot}
            isCompared={compareSet.some((b) => b.bot_id === bot.bot_id)}
            onCompareToggle={handleCompareToggle}
          />
        ))}
        {visible.length === 0 && (
          <p className="col-span-3 text-slate-500 text-sm">No bots match the current filters.</p>
        )}
      </div>

      <p className="mt-6 text-xs text-slate-600">
        Select up to {MAX_COMPARE} bots to compare side by side. Prices shown are monthly
        subscriptions. Custom enterprise pricing available on request.
      </p>
    </div>
  );
}
