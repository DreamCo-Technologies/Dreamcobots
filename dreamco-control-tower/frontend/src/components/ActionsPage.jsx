import { useMemo, useState } from 'react';
import ActionsMonitor from './ActionsMonitor.jsx';
import BuddyCommandCenter from './BuddyCommandCenter.jsx';
import githubActionsButtonCatalog, { actionCategories } from '../data/githubActionsButtonCatalog.js';

const fleetFacts = [
  { label: 'Bot candidates scanned', value: '1,308', tone: 'text-dreamco-accent' },
  { label: 'Known open issues', value: '1,349', tone: 'text-dreamco-yellow' },
  { label: 'Metadata files planned', value: '3,638', tone: 'text-dreamco-yellow' },
  { label: 'Buddy checks passing', value: '20/20', tone: 'text-green-300' },
];

const statusPanels = [
  {
    title: 'Bot Fleet Truth',
    status: 'Not fully green',
    copy: 'The fleet is discoverable, but thousands of bot metadata and readiness gaps still need repair before we can claim everything is running cleanly.',
  },
  {
    title: 'Buddy Connection',
    status: 'Switchboard passing',
    copy: 'Buddy has a tested registry, model router, and tool switchboard. Full live wiring still depends on each bot adopting control files and approved tool permissions.',
  },
  {
    title: 'GitHub Actions',
    status: '500 controls staged',
    copy: 'Buttons are categorized, risk-tagged, and approval-aware. Backend dispatch should only activate approved workflows.',
  },
];

const agentSections = [
  {
    name: 'Missing Files Scanner',
    status: 'Ready',
    owner: 'automation-tools/agents/dreamco-missing-files-scan.js',
    signal: 'Finds bots with missing manifests, package files, prompts, env templates, and run instructions.',
    action: 'Run bot-health-scan.yml',
  },
  {
    name: 'Bot Metadata Repair Planner',
    status: 'Ready for PR',
    owner: 'automation-tools/agents/repair-bot-metadata.js',
    signal: 'Plans 3,638 bot control files so Buddy can understand ownership, tools, risks, goals, and learning paths.',
    action: 'Run repair-bot-metadata-pr.yml',
  },
  {
    name: 'Dependency Audit Agent',
    status: 'Passing',
    owner: 'automation-tools/agents/dependency-audit.js',
    signal: 'Checks lockfiles and package consistency across Node projects before dashboards go live.',
    action: 'Run dreamco-debug-audit.yml',
  },
  {
    name: 'Sandbox No-Hallucination Audit',
    status: 'Ready',
    owner: 'automation-tools/agents/sandbox-hallucination-audit.js',
    signal: 'Runs sandbox-safe evidence checks and reports unsupported absolute success claims before bots say work is complete.',
    action: 'Run sandbox:no-hallucinations',
  },
  {
    name: 'Buddy Connectivity Tester',
    status: 'Passing',
    owner: 'automation-tools/agents/buddy-connectivity-test.js',
    signal: 'Verifies Buddy registry, model routing, command permissions, and MCP switchboard readiness.',
    action: 'Run buddy-connectivity.yml',
  },
  {
    name: 'Sales Rep Bot Team',
    status: 'Configured',
    owner: 'data/sales/sales-bot-team.json',
    signal: 'Defines prospecting, discovery, pricing, KPI, validation, and repeatable sales workflow roles.',
    action: 'Run stripe-revenue-tracking.yml',
  },
  {
    name: 'Revenue Tracking Agent',
    status: 'Configured',
    owner: 'stripe/node/revenue-ledger.js',
    signal: 'Tracks Stripe events by bot, offer, and workflow so revenue can be traced back to the system that earned it.',
    action: 'Run stripe-revenue-tracking.yml',
  },
];

const issueSections = [
  {
    title: 'Actions detail rendering',
    state: 'Completed this pass',
    severity: 'fixed',
    detail: 'Selected workflow names now render as real values instead of a literal template expression.',
  },
  {
    title: 'Actions page test coverage',
    state: 'Completed this pass',
    severity: 'fixed',
    detail: 'Tests now cover the 500-button catalog, selected action detail, Agents section, and Issues section.',
  },
  {
    title: 'Bot metadata gaps',
    state: 'Open',
    severity: 'open',
    detail: '3,638 metadata files are planned. Keep this visible until the repair PR workflow lands and verifies the generated files.',
  },
  {
    title: 'Fleet readiness gaps',
    state: 'Open',
    severity: 'open',
    detail: 'The latest scan found 1,349 readiness issues. These should be closed only after the health scan proves the count dropped.',
  },
  {
    title: 'Workflow dispatch backend',
    state: 'Open',
    severity: 'open',
    detail: 'The 500 buttons are staged. Live dispatch still needs backend workflow_dispatch wiring, approval checks, and audit logs.',
  },
];

function riskClass(risk) {
  if (risk === 'low') return 'bg-green-950 text-green-300 border-green-800';
  if (risk === 'medium') return 'bg-yellow-950 text-yellow-300 border-yellow-800';
  return 'bg-red-950 text-red-300 border-red-800';
}

function issueClass(severity) {
  if (severity === 'fixed') return 'border-green-800 bg-green-950/30 text-green-300';
  return 'border-yellow-800 bg-yellow-950/30 text-yellow-300';
}

/**
 * ActionsPage keeps Actions monitoring and command-center launch together.
 * To test keyboard command submits, pass `onBuddyCommandSubmit` from tests.
 */
export default function ActionsPage({
  ActionsMonitorComponent = ActionsMonitor,
  onBuddyCommandSubmit = () => {},
}) {
  const [showBuddyCenter, setShowBuddyCenter] = useState(false);
  const [category, setCategory] = useState('All');
  const [showEnabledOnly, setShowEnabledOnly] = useState(true);
  const [selectedAction, setSelectedAction] = useState(null);

  const filteredActions = useMemo(() => {
    return githubActionsButtonCatalog.filter((action) => {
      const categoryMatch = category === 'All' || action.category === category;
      const enabledMatch = !showEnabledOnly || action.enabled;
      return categoryMatch && enabledMatch;
    });
  }, [category, showEnabledOnly]);

  const enabledCount = githubActionsButtonCatalog.filter((action) => action.enabled).length;
  const highRiskCount = githubActionsButtonCatalog.filter((action) => action.risk === 'high').length;
  const completedIssueCount = issueSections.filter((issue) => issue.severity === 'fixed').length;
  const openIssueCount = issueSections.length - completedIssueCount;

  function handleActionClick(action) {
    setSelectedAction(action);
  }

  return (
    <section className="space-y-6">
      <div className="rounded-2xl border border-slate-700 bg-slate-950/80 p-5 shadow-2xl shadow-black/20">
        <div className="mb-5 flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-xs font-bold uppercase tracking-wide text-dreamco-accent">
              DreamCo Operator Layer
            </p>
            <h2 className="text-lg font-semibold text-white">⚡ Actions</h2>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">
              Command Center controls for bot repair, Buddy wiring, GitHub workflows,
              revenue tracking, sales operations, MCP tools, and model routing.
            </p>
          </div>
          <button
            type="button"
            onClick={() => setShowBuddyCenter(true)}
            className="rounded-lg bg-dreamco-accent px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-dreamco-accent/80"
          >
            Launch Full Buddy Command Center
          </button>
        </div>

        <div className="grid gap-3 md:grid-cols-4">
          {fleetFacts.map((fact) => (
            <div key={fact.label} className="rounded-xl border border-slate-800 bg-slate-900/80 p-4">
              <p className={`text-2xl font-black ${fact.tone}`}>{fact.value}</p>
              <p className="mt-1 text-xs font-medium uppercase text-slate-500">{fact.label}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        {statusPanels.map((panel) => (
          <article key={panel.title} className="rounded-xl border border-slate-800 bg-dreamco-card p-4">
            <div className="mb-3 flex items-center justify-between gap-3">
              <h3 className="font-semibold text-white">{panel.title}</h3>
              <span className="rounded-full border border-slate-700 px-2 py-1 text-xs font-semibold text-slate-300">
                {panel.status}
              </span>
            </div>
            <p className="text-sm leading-6 text-slate-400">{panel.copy}</p>
          </article>
        ))}
      </div>

      <div className="rounded-2xl border border-slate-700 bg-slate-950/80 p-5">
        <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
          <div>
            <h3 className="text-base font-semibold text-white">GitHub Action Button Grid</h3>
            <p className="mt-1 text-sm text-slate-400">
              {githubActionsButtonCatalog.length} total controls, {enabledCount} enabled now,
              {highRiskCount} high-risk controls gated for approval.
            </p>
          </div>
          <label className="flex items-center gap-2 text-sm text-slate-300">
            <input
              type="checkbox"
              checked={showEnabledOnly}
              onChange={(event) => setShowEnabledOnly(event.target.checked)}
              className="h-4 w-4 accent-dreamco-accent"
            />
            Enabled only
          </label>
        </div>

        <div className="mb-4 flex gap-2 overflow-x-auto pb-2" aria-label="Action category filters">
          {['All', ...actionCategories].map((item) => (
            <button
              key={item}
              type="button"
              onClick={() => setCategory(item)}
              className={`whitespace-nowrap rounded-lg border px-3 py-2 text-xs font-semibold transition-colors ${
                category === item
                  ? 'border-dreamco-accent bg-dreamco-accent text-white'
                  : 'border-slate-700 bg-slate-900 text-slate-300 hover:text-white'
              }`}
            >
              {item}
            </button>
          ))}
        </div>

        <div className="grid max-h-[520px] gap-2 overflow-y-auto pr-1 sm:grid-cols-2 xl:grid-cols-4" aria-label="GitHub action controls">
          {filteredActions.map((action) => (
            <button
              key={action.id}
              type="button"
              aria-label={`Action ${action.number}: ${action.label}`}
              onClick={() => handleActionClick(action)}
              className={`min-h-28 rounded-xl border p-3 text-left transition-colors ${
                action.enabled
                  ? 'border-slate-700 bg-slate-900 hover:border-dreamco-accent hover:bg-slate-800'
                  : 'border-slate-800 bg-slate-950/70 opacity-60 hover:opacity-90'
              }`}
            >
              <div className="mb-2 flex items-start justify-between gap-2">
                <span className="text-xs font-mono text-slate-500">#{action.number}</span>
                <span className={`rounded-full border px-2 py-0.5 text-[10px] font-bold uppercase ${riskClass(action.risk)}`}>
                  {action.risk}
                </span>
              </div>
              <p className="text-sm font-bold text-white">{action.label}</p>
              <p className="mt-1 text-xs leading-5 text-slate-400">{action.workflow}</p>
              <div className="mt-3 flex flex-wrap gap-1">
                <span className="rounded bg-slate-800 px-2 py-0.5 text-[10px] uppercase text-slate-300">
                  {action.mode}
                </span>
                {action.requiresApproval && (
                  <span className="rounded bg-yellow-950 px-2 py-0.5 text-[10px] uppercase text-yellow-300">
                    approval
                  </span>
                )}
              </div>
            </button>
          ))}
        </div>

        {selectedAction && (
          <div className="mt-4 rounded-xl border border-dreamco-accent/40 bg-slate-900 p-4">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <p className="text-xs font-mono text-slate-500">{selectedAction.id}</p>
                <h4 className="text-base font-bold text-white">{selectedAction.label}</h4>
                <p className="mt-1 text-sm text-slate-400">{selectedAction.description}</p>
              </div>
              <span className="rounded-full bg-slate-800 px-3 py-1 text-xs font-semibold text-slate-300">
                Dispatch wiring pending
              </span>
            </div>
            <p className="mt-3 text-xs leading-5 text-slate-500">
              This button is staged for <code className="text-slate-300">{selectedAction.workflow}</code>.
              Real workflow dispatch should be connected through the backend with approval checks and audit logging.
            </p>
          </div>
        )}
      </div>

      <div className="rounded-2xl border border-slate-700 bg-slate-950/80 p-5">
        <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
          <div>
            <h3 className="text-base font-semibold text-white">Agents Section</h3>
            <p className="mt-1 text-sm text-slate-400">
              Buddy-facing automation agents, their source files, current readiness, and the action that should run them.
            </p>
          </div>
          <span className="rounded-full border border-green-800 bg-green-950/30 px-3 py-1 text-xs font-semibold text-green-300">
            {agentSections.length} tracked agents
          </span>
        </div>

        <div className="grid gap-3 lg:grid-cols-2">
          {agentSections.map((agent) => (
            <article key={agent.name} className="rounded-xl border border-slate-800 bg-dreamco-card p-4">
              <div className="mb-2 flex flex-wrap items-start justify-between gap-2">
                <div>
                  <h4 className="font-semibold text-white">{agent.name}</h4>
                  <p className="mt-1 text-xs font-mono text-slate-500">{agent.owner}</p>
                </div>
                <span className="rounded-full border border-slate-700 px-2 py-1 text-xs font-semibold text-slate-300">
                  {agent.status}
                </span>
              </div>
              <p className="text-sm leading-6 text-slate-400">{agent.signal}</p>
              <p className="mt-3 text-xs font-semibold uppercase text-dreamco-accent">{agent.action}</p>
            </article>
          ))}
        </div>
      </div>

      <div className="rounded-2xl border border-slate-700 bg-slate-950/80 p-5">
        <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
          <div>
            <h3 className="text-base font-semibold text-white">Issues Section</h3>
            <p className="mt-1 text-sm text-slate-400">
              Completed issues are listed separately from open gaps. Open GitHub issues should only be closed after their checks prove green.
            </p>
          </div>
          <div className="flex gap-2 text-xs font-semibold">
            <span className="rounded-full border border-green-800 bg-green-950/30 px-3 py-1 text-green-300">
              {completedIssueCount} completed
            </span>
            <span className="rounded-full border border-yellow-800 bg-yellow-950/30 px-3 py-1 text-yellow-300">
              {openIssueCount} open
            </span>
          </div>
        </div>

        <div className="grid gap-3 lg:grid-cols-5">
          {issueSections.map((issue) => (
            <article key={issue.title} className="rounded-xl border border-slate-800 bg-dreamco-card p-4">
              <span className={`mb-3 inline-flex rounded-full border px-2 py-1 text-xs font-semibold ${issueClass(issue.severity)}`}>
                {issue.state}
              </span>
              <h4 className="font-semibold text-white">{issue.title}</h4>
              <p className="mt-2 text-sm leading-6 text-slate-400">{issue.detail}</p>
            </article>
          ))}
        </div>
      </div>

      <ActionsMonitorComponent />

      {showBuddyCenter && (
        <div
          className="fixed inset-0 z-40 flex items-center justify-center bg-slate-950/85 px-4 py-6"
          onClick={() => setShowBuddyCenter(false)}
        >
          <div onClick={(event) => event.stopPropagation()}>
            <BuddyCommandCenter
              onClose={() => setShowBuddyCenter(false)}
              onCommandSubmit={onBuddyCommandSubmit}
            />
          </div>
        </div>
      )}
    </section>
  );
}
