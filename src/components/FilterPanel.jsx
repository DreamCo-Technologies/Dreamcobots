/**
 * FilterPanel.jsx
 *
 * Renders tier selector, category dropdown, price-range slider, and a
 * full-text search box for the DivisionExplorer.
 *
 * Props:
 *  - tiers           {string[]}   Available tier labels (e.g. ['Pro', 'Enterprise'])
 *  - categories      {string[]}   Available category names for the active division
 *  - selectedTier    {string}     Currently active tier filter
 *  - selectedCategory{string}     Currently active category filter
 *  - maxPrice        {number}     Current maximum price filter (numeric, $/mo)
 *  - searchQuery     {string}     Current full-text search string
 *  - onTierChange    {Function}   Called with new tier string
 *  - onCategoryChange{Function}   Called with new category string
 *  - onMaxPriceChange{Function}   Called with new max price number
 *  - onSearchChange  {Function}   Called with new search string
 *
 * Developer notes:
 * - Keep this component stateless; all state lives in DivisionExplorer.
 * - To add a new filter dimension, add a prop pair and wire it here.
 */

import React from 'react';

/** Maximum price shown on the slider (matches highest tier price). */
const SLIDER_MAX = 500;

export default function FilterPanel({
  tiers,
  categories,
  selectedTier,
  selectedCategory,
  maxPrice,
  searchQuery,
  onTierChange,
  onCategoryChange,
  onMaxPriceChange,
  onSearchChange,
}) {
  return (
    <div className="filter-panel">
      {/* ── Full-text search ── */}
      <div className="filter-group filter-search">
        <label htmlFor="filter-search-input" className="filter-label">
          Search
        </label>
        <input
          id="filter-search-input"
          type="text"
          className="filter-input"
          placeholder="Search bots, features, categories…"
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
        />
      </div>

      {/* ── Tier selector ── */}
      <div className="filter-group filter-tier">
        <span className="filter-label">Tier</span>
        <div className="tier-buttons" role="group" aria-label="Tier filter">
          <button
            className={`tier-btn ${selectedTier === 'All' ? 'active' : ''}`}
            onClick={() => onTierChange('All')}
          >
            All
          </button>
          {tiers.map((tier) => (
            <button
              key={tier}
              className={`tier-btn tier-btn--${tier.toLowerCase()} ${
                selectedTier === tier ? 'active' : ''
              }`}
              onClick={() => onTierChange(tier)}
            >
              {tier}
            </button>
          ))}
        </div>
      </div>

      {/* ── Category dropdown ── */}
      <div className="filter-group filter-category">
        <label htmlFor="filter-category-select" className="filter-label">
          Category
        </label>
        <select
          id="filter-category-select"
          className="filter-select"
          value={selectedCategory}
          onChange={(e) => onCategoryChange(e.target.value)}
        >
          <option value="All">All Categories</option>
          {categories.map((cat) => (
            <option key={cat} value={cat}>
              {cat}
            </option>
          ))}
        </select>
      </div>

      {/* ── Price range slider ── */}
      <div className="filter-group filter-price">
        <label htmlFor="filter-price-slider" className="filter-label">
          Max Price:{' '}
          <strong>{maxPrice >= SLIDER_MAX ? `$${SLIDER_MAX}+` : `$${maxPrice}/mo`}</strong>
        </label>
        <input
          id="filter-price-slider"
          type="range"
          className="filter-slider"
          min={49}
          max={SLIDER_MAX}
          step={50}
          value={maxPrice}
          onChange={(e) => onMaxPriceChange(Number(e.target.value))}
        />
        <div className="price-range-labels">
          <span>$49</span>
          <span>${SLIDER_MAX}+</span>
        </div>
      </div>
    </div>
  );
}
