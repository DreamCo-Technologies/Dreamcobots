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

// ---------------------------------------------------------------------------
// Static bot data — generated from master registry so the bundle is
// self-contained and aligned with governance metadata.
// ---------------------------------------------------------------------------
import divisionCatalogIndex from '../../divisions/generated/catalog_index.json';

/** All bots across every division, merged into a single flat array. */
const ALL_BOTS = divisionCatalogIndex.all_bots || [];

/** Derive unique division names from the data (order-preserving). */
const DIVISIONS = [...new Set(ALL_BOTS.map((b) => b.division))];

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
          Browse {ALL_BOTS.length} bots across {DIVISIONS.length} divisions
        </p>
        <div className="explorer-stats">
          <span className="stat">{ALL_BOTS.length} Total Bots</span>
          <span className="stat">{DIVISIONS.length} Divisions</span>
          <span className="stat">{filteredBots.length} Results</span>
        </div>
      </header>

      <div className="explorer-body">
        {/* ── Division Sidebar ── */}
        <aside className="division-sidebar">
          <h2>Divisions</h2>
          <ul className="division-list">
            <li>
              <button
                className={`division-btn ${selectedDivision === 'All' ? 'active' : ''}`}
                onClick={() => handleDivisionChange('All')}
              >
                All Divisions
                <span className="division-count">{ALL_BOTS.length}</span>
              </button>
            </li>
            {DIVISIONS.map((div) => {
              const count = ALL_BOTS.filter((b) => b.division === div).length;
              return (
                <li key={div}>
                  <button
                    className={`division-btn ${selectedDivision === div ? 'active' : ''}`}
                    onClick={() => handleDivisionChange(div)}
                  >
                    {div}
                    <span className="division-count">{count}</span>
                  </button>
                </li>
              );
            })}
          </ul>
        </aside>

        {/* ── Main Content ── */}
        <main className="explorer-main">
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
