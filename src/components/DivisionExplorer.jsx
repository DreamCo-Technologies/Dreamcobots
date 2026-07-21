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

const PROSPECTUS_BY_DIVISION = {
  CommandCore: {
    mission: 'Control tower, orchestration, governance, and command workflows.',
    lanes: ['Bot registry', 'Workflow command', 'System health', 'Release approval'],
    revenue: 'Internal control, governance, and reliability infrastructure.',
  },
  DreamSalesPro: {
    mission: 'Lead generation, outreach, follow-up, closing, and sales enablement.',
    lanes: ['Prospecting', 'Enrichment', 'Outreach', 'Pipeline conversion'],
    revenue: 'Subscriptions, lead services, and approved sales automation.',
  },
  DreamFinance: {
    mission: 'Finance operations, forecasting, budget support, and reporting.',
    lanes: ['Cash flow', 'Forecasting', 'Optimization', 'Finance dashboards'],
    revenue: 'Finance tooling, reporting, advisory workflows, and subscriptions.',
  },
  DreamRealEstate: {
    mission: 'Property analysis, real estate workflows, valuation, and deal support.',
    lanes: ['Deal discovery', 'Property scoring', 'Portfolio checks', 'Market research'],
    revenue: 'Property intelligence, deal analysis, and real estate workflow tools.',
  },
  DreamAIInfra: {
    mission: 'Model routing, AI enablement, usage gates, and shared AI infrastructure.',
    lanes: ['Model routing', 'Prompt registry', 'Usage caps', 'AI safety checks'],
    revenue: 'Internal AI infrastructure and platform metering.',
  },
  DreamRetail: {
    mission: 'Retail operations, product workflows, pricing, and customer conversion.',
    lanes: ['Catalogs', 'Pricing', 'Merchandising', 'Retail analytics'],
    revenue: 'Retail automation, optimization tools, and commerce support.',
  },
  DreamProServices: {
    mission: 'Professional services workflows, proposals, delivery, and client ops.',
    lanes: ['Proposals', 'Client intake', 'Delivery tracking', 'Service reporting'],
    revenue: 'Service packages, retained workflows, and professional automation.',
  },
  DreamData: {
    mission: 'Data pipelines, analytics, cataloging, quality, and monetization.',
    lanes: ['Data quality', 'Catalogs', 'Dashboards', 'Data products'],
    revenue: 'Data products, analytics services, and governed datasets.',
  },
  DreamGlobal: {
    mission: 'Global expansion, localization, compliance routing, and regional ops.',
    lanes: ['Localization', 'Regional routing', 'Market entry', 'Global compliance'],
    revenue: 'International expansion workflows and regional intelligence.',
  },
  DreamAutomation: {
    mission: 'Workflow automation, task execution, process monitoring, and ops tooling.',
    lanes: ['Task runners', 'Workflow builders', 'Process checks', 'Automation reporting'],
    revenue: 'Automation systems, workflow subscriptions, and managed ops tooling.',
  },
  DreamContent: {
    mission: 'Content production, copy, scripts, publishing support, and creative systems.',
    lanes: ['Copy', 'Scripts', 'Publishing', 'Creative calendars'],
    revenue: 'Content packages, creative automation, and publishing services.',
  },
  DreamTrade: {
    mission: 'Trade workflows, market monitoring, logistics support, and risk checks.',
    lanes: ['Trade research', 'Compliance checks', 'Logistics', 'Market signals'],
    revenue: 'Trade intelligence and approved workflow automation.',
  },
  DreamFlow: {
    mission: 'Process design, workflow mapping, routing, and throughput improvement.',
    lanes: ['Flow mapping', 'Bottleneck checks', 'Routing', 'Throughput reports'],
    revenue: 'Process optimization and workflow operating systems.',
  },
  DreamMarket: {
    mission: 'Marketing systems, campaign support, positioning, and growth analytics.',
    lanes: ['Campaigns', 'Audience research', 'Positioning', 'Growth analytics'],
    revenue: 'Marketing systems, campaign tools, and growth services.',
  },
  DreamEmpire: {
    mission: 'Enterprise-wide operating systems, portfolio oversight, and expansion.',
    lanes: ['Portfolio ops', 'Expansion', 'Executive dashboards', 'System strategy'],
    revenue: 'Platform orchestration and enterprise operating packages.',
  },
  GameTitan: {
    mission: 'Game systems, interactive products, engagement loops, and game analytics.',
    lanes: ['Game loops', 'Player systems', 'Monetization', 'Analytics'],
    revenue: 'Games, engagement tools, and interactive product systems.',
  },
  DreamInfluence: {
    mission: 'Influencer systems, audience growth, creator operations, and partnerships.',
    lanes: ['Creator ops', 'Audience growth', 'Partnerships', 'Campaign tracking'],
    revenue: 'Creator tools, influence campaigns, and partnership workflows.',
  },
  DreamDecision: {
    mission: 'Decision intelligence, scoring, simulations, and recommendation support.',
    lanes: ['Scoring', 'Scenario modeling', 'Recommendations', 'Decision logs'],
    revenue: 'Decision tools, scoring engines, and advisory workflows.',
  },
  DreamOps: {
    mission: 'Operations monitoring, reliability, runbooks, and execution systems.',
    lanes: ['Runbooks', 'Monitoring', 'Incident flow', 'Operational reports'],
    revenue: 'Ops tooling, monitoring systems, and managed workflows.',
  },
  DreamPlanetary: {
    mission: 'Planetary risk, sustainability, climate, and global systems intelligence.',
    lanes: ['Risk modeling', 'Sustainability', 'Climate signals', 'Impact reporting'],
    revenue: 'Risk intelligence, sustainability tools, and impact reporting.',
  },
  DreamEntFinance: {
    mission: 'Enterprise finance strategy, capital allocation, and executive finance ops.',
    lanes: ['Capital planning', 'Budget strategy', 'Forecasting', 'Executive reports'],
    revenue: 'Enterprise finance workflows and strategic planning tools.',
  },
  DreamCustIntel: {
    mission: 'Customer intelligence, segmentation, retention, and experience analytics.',
    lanes: ['Segments', 'Retention', 'Experience signals', 'Customer analytics'],
    revenue: 'Customer intelligence tools and retention systems.',
  },
  DreamLegal: {
    mission: 'Legal workflow support, contract review, compliance tracking, and risk triage.',
    lanes: ['Contracts', 'Compliance', 'Risk triage', 'Review queues'],
    revenue: 'Legal workflow support with human approval gates.',
  },
  DreamCyber: {
    mission: 'Cybersecurity monitoring, posture checks, vulnerability workflows, and defense ops.',
    lanes: ['Posture checks', 'Threat tracking', 'Vulnerability queues', 'Security reports'],
    revenue: 'Security tooling and approved cyber defense workflows.',
  },
  DreamHealth: {
    mission: 'Health operations support, wellness workflows, care administration, and safety gates.',
    lanes: ['Wellness', 'Care admin', 'Scheduling', 'Safety review'],
    revenue: 'Health workflow support with approval and compliance gates.',
  },
  DreamEducation: {
    mission: 'Education tools, tutoring support, curriculum workflows, and learning analytics.',
    lanes: ['Curriculum', 'Tutoring', 'Student analytics', 'Learning tools'],
    revenue: 'Education systems, learning tools, and support workflows.',
  },
  DreamConstruction: {
    mission: 'Construction estimating, project controls, jobsite workflows, and safety tracking.',
    lanes: ['Estimating', 'Scheduling', 'Safety', 'Project controls'],
    revenue: 'Construction tools, project automation, and field reporting.',
  },
  DreamTransport: {
    mission: 'Transport workflows, dispatch, routing, fleet checks, and logistics intelligence.',
    lanes: ['Routing', 'Dispatch', 'Fleet checks', 'Logistics reports'],
    revenue: 'Transportation workflow systems and logistics tools.',
  },
  DreamFood: {
    mission: 'Food service, inventory, safety, kitchen ops, and hospitality workflows.',
    lanes: ['Inventory', 'Menus', 'Safety checks', 'Service ops'],
    revenue: 'Food service tools and hospitality operating systems.',
  },
  DreamScience: {
    mission: 'Research workflows, science data, experiment support, and technical analysis.',
    lanes: ['Research support', 'Experiment tracking', 'Data review', 'Technical reports'],
    revenue: 'Research tooling, science workflows, and data products.',
  },
  DreamArts: {
    mission: 'Creative arts systems, production support, asset workflows, and portfolio tools.',
    lanes: ['Creative production', 'Assets', 'Portfolios', 'Publishing'],
    revenue: 'Creative tools, production systems, and portfolio services.',
  },
  DreamProtection: {
    mission: 'Protection workflows, safety monitoring, emergency readiness, and risk response.',
    lanes: ['Safety checks', 'Risk response', 'Emergency readiness', 'Protection reports'],
    revenue: 'Protection tooling and approved safety workflows.',
  },
  DreamAgriculture: {
    mission: 'Agriculture management, crop intelligence, livestock support, and farm operations.',
    lanes: ['Crop planning', 'Livestock', 'Weather impact', 'Farm reports'],
    revenue: 'Agriculture tools, farm intelligence, and operations support.',
  },
  DreamMaintenance: {
    mission: 'Maintenance planning, work orders, preventive checks, and asset reliability.',
    lanes: ['Work orders', 'Preventive checks', 'Asset tracking', 'Maintenance reports'],
    revenue: 'Maintenance systems and asset reliability workflows.',
  },
  DreamProduction: {
    mission: 'Production scheduling, manufacturing support, quality, and throughput systems.',
    lanes: ['Scheduling', 'Quality', 'Throughput', 'Production reports'],
    revenue: 'Production tooling and manufacturing workflow systems.',
  },
  DreamSocial: {
    mission: 'Social systems, community workflows, scheduling, and engagement analytics.',
    lanes: ['Scheduling', 'Community', 'Engagement', 'Social analytics'],
    revenue: 'Social automation, community tools, and engagement systems.',
  },
  DreamAdmin: {
    mission: 'Administrative workflows, office systems, records, and coordination tools.',
    lanes: ['Records', 'Scheduling', 'Office ops', 'Admin reports'],
    revenue: 'Administrative automation and coordination systems.',
  },
  DreamCrypto: {
    mission: 'Crypto research, portfolio support, compliance-aware workflows, and risk review.',
    lanes: ['Portfolio checks', 'Risk review', 'Market signals', 'Compliance gates'],
    revenue: 'Crypto intelligence workflows with approval gates.',
  },
  DreamPayments: {
    mission: 'Payment workflows, billing support, reconciliation, and payment safety checks.',
    lanes: ['Billing', 'Reconciliation', 'Payment checks', 'Approval queues'],
    revenue: 'Payment operations tooling with strict human approval gates.',
  },
  DreamBizLaunch: {
    mission: 'Business launch systems, startup planning, offers, and go-to-market workflows.',
    lanes: ['Launch plans', 'Offers', 'Startup costs', 'Go-to-market'],
    revenue: 'Business launch packages and startup workflow systems.',
  },
  DreamCodeLab: {
    mission: 'Code systems, developer tooling, test generation, and software automation.',
    lanes: ['Code generation', 'Testing', 'Tool builders', 'Developer workflows'],
    revenue: 'Developer tools, code automation, and software systems.',
  },
  DreamLoans: {
    mission: 'Loan research, eligibility support, credit workflows, and approval-safe guidance.',
    lanes: ['Eligibility', 'Loan research', 'Credit review', 'Approval gates'],
    revenue: 'Loan workflow support with human review and compliance gates.',
  },
  DreamPersonalCare: {
    mission: 'Personal care operations, wellness scheduling, salon/spa workflows, and client support.',
    lanes: ['Scheduling', 'Client care', 'Wellness plans', 'Service reports'],
    revenue: 'Personal care business systems and client workflow tools.',
  },
  DreamMilitary: {
    mission: 'Military transition, readiness support, training, and resource workflows.',
    lanes: ['Transition', 'Training', 'Readiness', 'Resource support'],
    revenue: 'Military support tools and approved resource workflows.',
  },
  DreamAgents: {
    mission: 'Agent capabilities, task execution, memory, and user-facing assistant workflows.',
    lanes: ['Task agents', 'Memory', 'Capability routing', 'Assistant workflows'],
    revenue: 'Agent systems, assistant capabilities, and workflow subscriptions.',
  },
};

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

function prospectusForDivision(division) {
  return (
    PROSPECTUS_BY_DIVISION[division] || {
      mission: `${division} operating lane for bots, workflows, dashboards, and governed releases.`,
      lanes: ['Bot intake', 'Workflow buildout', 'Dashboard tracking', 'Revenue review'],
      revenue: 'Division-specific tooling, automation, and service workflows.',
    }
  );
}

function systemSummaryFor(division) {
  const bots = botsForDivision(division);
  const categories = [...new Set(bots.map((bot) => bot.category))].sort();
  const enabledCount = bots.filter((bot) => bot.enabled !== false).length;
  const prospectus = prospectusForDivision(division);
  return {
    id: `division-system-${slugFor(division)}`,
    prospectusId: `division-prospectus-${slugFor(division)}`,
    name: division,
    bots,
    botCount: bots.length,
    enabledCount,
    categories,
    tiers: tierSummaryFor(bots),
    prospectus,
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
                    aria-describedby={system.prospectusId}
                    aria-pressed={selectedDivision === div}
                  >
                    <span>
                      <span className="division-name">{div}</span>
                      <span className="division-prospectus-mini" id={system.prospectusId}>
                        {system.prospectus.mission}
                      </span>
                    </span>
                    <span className="division-count" aria-label={`${system.botCount} bots`}>
                      {system.botCount}
                    </span>
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

              <div className="division-prospectus-card">
                <div>
                  <p className="system-kicker">Division prospectus</p>
                  <h3>{selectedSystem.name} Prospectus</h3>
                  <p>{selectedSystem.prospectus.mission}</p>
                </div>
                <div className="prospectus-grid">
                  <div>
                    <span className="prospectus-label">Operating lanes</span>
                    <ul>
                      {selectedSystem.prospectus.lanes.map((lane) => (
                        <li key={lane}>{lane}</li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <span className="prospectus-label">Revenue model</span>
                    <p>{selectedSystem.prospectus.revenue}</p>
                  </div>
                  <div>
                    <span className="prospectus-label">Readiness path</span>
                    <p>
                      Connect bots, run smoke tests, keep dashboards current, and route high-risk work
                      through approval before production release.
                    </p>
                  </div>
                </div>
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
