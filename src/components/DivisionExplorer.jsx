/**
 * DivisionExplorer.jsx
 *
 * Top-level component for browsing DreamCo divisions, categories, and bots.
 * Renders a filterable, searchable grid of bot cards grouped by division.
 *
 * Usage:
 *   import DivisionExplorer from './DivisionExplorer';
 *   <DivisionExplorer />
 *
 * Division data is generated from config/master_bot_registry.json into
 * divisions/generated/catalog_index.json.
 *
 * Developer notes:
 * - All filter state is lifted here and passed down as props.
 * - BotCard handles individual bot rendering and monetization links.
 * - FilterPanel handles tier / category / price-range controls.
 * - MonetizationLinks is embedded inside BotCard.
 */

import React, { useState, useMemo, useCallback } from 'react';
import FilterPanel from './FilterPanel';
import BotCard from './BotCard';
import './DivisionExplorer.css';

// ---------------------------------------------------------------------------
// Static bot data — generated from master registry so the bundle is
// self-contained and aligned with governance metadata.
// ---------------------------------------------------------------------------
import divisionCatalogIndex from '../../divisions/generated/catalog_index.json';

/** All bots across every division, merged into a single flat array. */
const ALL_BOTS = divisionCatalogIndex.all_bots || [];

/** Canonical DreamCo division system lanes. */
const DIVISION_SYSTEMS = [
  'CommandCore',
  'DreamSalesPro',
  'DreamFinance',
  'DreamRealEstate',
  'DreamAIInfra',
  'DreamRetail',
  'DreamProServices',
  'DreamData',
  'DreamGlobal',
  'DreamAutomation',
  'DreamContent',
  'DreamTrade',
  'DreamFlow',
  'DreamMarket',
  'DreamEmpire',
  'GameTitan',
  'DreamInfluence',
  'DreamDecision',
  'DreamOps',
  'DreamPlanetary',
  'DreamEntFinance',
  'DreamCustIntel',
  'DreamLegal',
  'DreamCyber',
  'DreamHealth',
  'DreamEducation',
  'DreamConstruction',
  'DreamTransport',
  'DreamFood',
  'DreamScience',
  'DreamArts',
  'DreamProtection',
  'DreamAgriculture',
  'DreamMaintenance',
  'DreamProduction',
  'DreamSocial',
  'DreamAdmin',
  'DreamCrypto',
  'DreamPayments',
  'DreamBizLaunch',
  'DreamCodeLab',
  'DreamLoans',
  'DreamPersonalCare',
  'DreamMilitary',
  'DreamAgents',
];

/** Include any generated division not yet in the canonical operating list. */
const DIVISIONS = [
  ...DIVISION_SYSTEMS,
  ...[...new Set(ALL_BOTS.map((b) => b.division))].filter(
    (division) => !DIVISION_SYSTEMS.includes(division),
  ),
];

/** Tier ordering for display. */
const TIER_ORDER = ['Free', 'Pro', 'Enterprise', 'Elite'];

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Parse "$199/mo" → 199. Returns Infinity for unparseable strings. */
function parsePriceNumber(priceStr) {
  const match = priceStr && priceStr.match(/\$?([\d,]+)/);
  return match ? parseInt(match[1].replace(',', ''), 10) : Infinity;
}

/** Return the set of categories for a given division name. */
function categoriesForDivision(division) {
  return [
    ...new Set(ALL_BOTS.filter((b) => b.division === division).map((b) => b.category)),
  ].sort();
}

function slugFor(value) {
  return String(value).replace(/([a-z])([A-Z])/g, '$1-$2').toLowerCase();
}

function botsForDivision(division) {
  return ALL_BOTS.filter((bot) => bot.division === division);
}

function tierSummaryFor(bots) {
  return TIER_ORDER.map((tier) => ({
    tier,
    count: bots.filter((bot) => bot.tier === tier).length,
  }));
}

function systemSummaryFor(division) {
  const bots = botsForDivision(division);
  const categories = [...new Set(bots.map((bot) => bot.category))].sort();
  const enabledCount = bots.filter((bot) => bot.enabled !== false).length;
  return {
    id: `division-system-${slugFor(division)}`,
    name: division,
    bots,
    botCount: bots.length,
    enabledCount,
    categories,
    tiers: tierSummaryFor(bots),
    status: bots.length > 0 ? 'Live system' : 'System ready',
  };
}

// ---------------------------------------------------------------------------
// DivisionExplorer
// ---------------------------------------------------------------------------

/**
 * DivisionExplorer component.
 *
 * Renders:
 *  1. A header with total bot / division stats.
 *  2. A division sidebar for quick navigation.
 *  3. A FilterPanel (tier, category, price range, search).
 *  4. A responsive grid of BotCards matching the active filters.
 */
export default function DivisionExplorer() {
  // ── Filter state ──────────────────────────────────────────────────────────
  const [selectedDivision, setSelectedDivision] = useState('All');
  const [selectedTier, setSelectedTier] = useState('All');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [maxPrice, setMaxPrice] = useState(500);
  const [searchQuery, setSearchQuery] = useState('');

  const selectedSystem = useMemo(
    () => (selectedDivision === 'All' ? null : systemSummaryFor(selectedDivision)),
    [selectedDivision],
  );

  // ── Derived category list changes when division changes ───────────────────
  const categories = useMemo(() => {
    if (selectedDivision === 'All') {
      return [...new Set(ALL_BOTS.map((b) => b.category))].sort();
    }
    return categoriesForDivision(selectedDivision);
  }, [selectedDivision]);

  // Reset category when division changes to avoid showing empty results.
  const handleDivisionChange = useCallback((division) => {
    setSelectedDivision(division);
    setSelectedCategory('All');
  }, []);

  // ── Filtered bots ─────────────────────────────────────────────────────────
  const filteredBots = useMemo(() => {
    const query = searchQuery.toLowerCase().trim();
    return ALL_BOTS.filter((bot) => {
      if (selectedDivision !== 'All' && bot.division !== selectedDivision) return false;
      if (selectedTier !== 'All' && bot.tier !== selectedTier) return false;
      if (selectedCategory !== 'All' && bot.category !== selectedCategory) return false;
      if (parsePriceNumber(bot.price) > maxPrice) return false;
      if (
        query &&
        !bot.botName.toLowerCase().includes(query) &&
        !bot.description.toLowerCase().includes(query) &&
        !bot.category.toLowerCase().includes(query) &&
        !bot.features.some((f) => f.toLowerCase().includes(query))
      )
        return false;
      return true;
    });
  }, [selectedDivision, selectedTier, selectedCategory, maxPrice, searchQuery]);

  // ── Render ────────────────────────────────────────────────────────────────
  return (
    <div className="division-explorer">
      {/* ── Header ── */}
      <header className="explorer-header">
        <h1>DreamCo Division Explorer</h1>
        <p className="explorer-subtitle">
          Browse {ALL_BOTS.length} bots across {DIVISIONS.length} live division systems
        </p>
        <div className="explorer-stats">
          <span className="stat">{ALL_BOTS.length} Total Bots</span>
          <span className="stat">{DIVISIONS.length} Division Systems</span>
          <span className="stat">{filteredBots.length} Results</span>
        </div>
      </header>

      <div className="explorer-body">
        {/* ── Division Sidebar ── */}
        <aside className="division-sidebar">
          <h2>🏢 Divisions ({DIVISIONS.length})</h2>
          <nav className="division-list" aria-label="Division systems">
            <div>
              <button
                className={`division-btn ${selectedDivision === 'All' ? 'active' : ''}`}
                onClick={() => handleDivisionChange('All')}
                aria-pressed={selectedDivision === 'All'}
              >
                All Divisions
                <span className="division-count">{ALL_BOTS.length}</span>
              </button>
            </div>
            {DIVISIONS.map((div) => {
              const system = systemSummaryFor(div);
              return (
                <div key={div}>
                  <button
                    className={`division-btn ${selectedDivision === div ? 'active' : ''}`}
                    onClick={() => handleDivisionChange(div)}
                    aria-controls={system.id}
                    aria-pressed={selectedDivision === div}
                  >
                    <span className="division-name">{div}</span>
                    <span className="division-count">{system.botCount}</span>
                  </button>
                </div>
              );
            })}
          </nav>
        </aside>

        {/* ── Main Content ── */}
        <main className="explorer-main">
          {selectedSystem ? (
            <section
              id={selectedSystem.id}
              className="division-system-panel"
              aria-labelledby={`${selectedSystem.id}-heading`}
            >
              <div>
                <p className="system-kicker">Working division system</p>
                <h2 id={`${selectedSystem.id}-heading`}>{selectedSystem.name}</h2>
                <p className="system-summary">
                  {selectedSystem.botCount > 0
                    ? `${selectedSystem.enabledCount} enabled bots are connected to this division.`
                    : 'This division lane is live and ready for bots, tools, workflows, dashboards, and revenue checks.'}
                </p>
              </div>

              <div className="system-actions" aria-label={`${selectedSystem.name} system actions`}>
                <a className="system-action" href={`#${selectedSystem.id}`}>
                  Open System
                </a>
                <button
                  type="button"
                  className="system-action"
                  onClick={() => setSearchQuery(selectedSystem.name)}
                >
                  Scan Bots
                </button>
                <button
                  type="button"
                  className="system-action"
                  onClick={() => {
                    setSelectedTier('All');
                    setSelectedCategory('All');
                    setMaxPrice(500);
                    setSearchQuery('');
                  }}
                >
                  Clear Filters
                </button>
              </div>

              <div className="system-metrics">
                <div>
                  <span className="metric-value">{selectedSystem.status}</span>
                  <span className="metric-label">Status</span>
                </div>
                <div>
                  <span className="metric-value">{selectedSystem.botCount}</span>
                  <span className="metric-label">Bots</span>
                </div>
                <div>
                  <span className="metric-value">{selectedSystem.categories.length}</span>
                  <span className="metric-label">Categories</span>
                </div>
              </div>

              <div className="system-tier-row" aria-label={`${selectedSystem.name} bot tiers`}>
                <strong>💰 Bot Tiers</strong>
                {selectedSystem.tiers.map(({ tier, count }) => (
                  <button
                    key={tier}
                    type="button"
                    className={`tier-chip ${selectedTier === tier ? 'active' : ''}`}
                    onClick={() => setSelectedTier(tier)}
                  >
                    {tier} <span>{count}</span>
                  </button>
                ))}
              </div>
            </section>
          ) : (
            <section className="division-system-panel division-system-panel--all">
              <div>
                <p className="system-kicker">Working division systems</p>
                <h2>All DreamCo Divisions</h2>
                <p className="system-summary">
                  Pick any division name on the left to open its live system lane, tier mix, and bot grid.
                </p>
              </div>
              <div className="system-metrics">
                <div>
                  <span className="metric-value">{DIVISIONS.length}</span>
                  <span className="metric-label">Systems</span>
                </div>
                <div>
                  <span className="metric-value">{ALL_BOTS.length}</span>
                  <span className="metric-label">Bots</span>
                </div>
                <div>
                  <span className="metric-value">{TIER_ORDER.length}</span>
                  <span className="metric-label">Tiers</span>
                </div>
              </div>
            </section>
          )}

          {/* Filters */}
          <FilterPanel
            tiers={TIER_ORDER}
            categories={categories}
            selectedTier={selectedTier}
            selectedCategory={selectedCategory}
            maxPrice={maxPrice}
            searchQuery={searchQuery}
            onTierChange={setSelectedTier}
            onCategoryChange={setSelectedCategory}
            onMaxPriceChange={setMaxPrice}
            onSearchChange={setSearchQuery}
          />

          {/* Results count */}
          <p className="results-count">
            {filteredBots.length} {filteredBots.length === 1 ? 'bot' : 'bots'} found
            {selectedDivision !== 'All' ? ` in ${selectedDivision}` : ''}
          </p>

          {/* Bot grid */}
          {filteredBots.length > 0 ? (
            <div className="bot-grid">
              {filteredBots.map((bot) => (
                <BotCard key={bot.botId} bot={bot} />
              ))}
            </div>
          ) : (
            <div className="no-results">
              <p>No bots match your current filters.</p>
              <button
                className="reset-btn"
                onClick={() => {
                  setSelectedDivision('All');
                  setSelectedTier('All');
                  setSelectedCategory('All');
                  setMaxPrice(500);
                  setSearchQuery('');
                }}
              >
                Reset Filters
              </button>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
