import { useState } from 'react';

const PANELS = [
  {
    title: 'Bot Test Lab',
    detail: 'Run sandbox checks, issue coverage, missing-file scans, Buddy connectivity, and readiness reports before trusting a bot.',
  },
  {
    title: 'Customer Discovery',
    detail: 'Research customer segments, score fit, draft outreach, and hold every real contact for owner approval.',
  },
  {
    title: 'Tool & Skill Finder',
    detail: 'Search public sources such as GitHub, Wikipedia, official docs, and registries, then store sourced learning records.',
  },
  {
    title: 'Social Draft Studio',
    detail: 'Prepare social posts, campaigns, and ad ideas in draft-only mode until platform secrets and approvals are configured.',
  },
  {
    title: 'Cash Loop Tracker',
    detail: 'Move ideas through problem, customer, MVP offer, validation, pricing, sales process, KPI review, and improvement loops.',
  },
  {
    title: 'Memory & Learning',
    detail: 'Save source, confidence, usable knowledge, next experiment, and outcome so bots learn from evidence instead of guesses.',
  },
];

const QUICK_COMMANDS = [
  'npm run autonomous:readiness',
  'npm run scan:issues',
  'npm run sandbox:no-hallucinations',
  'npm run debug:all',
  'draft lead generation plan for DreamSalesPro',
  'find tools for real estate deal scoring',
];

/**
 * Full-size Buddy command center modal content used by ActionsPage.
 * Keep headings stable for UI tests when adding/removing future panels.
 */
export default function BuddyCommandCenter({ onClose, onCommandSubmit = () => {} }) {
  const [command, setCommand] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [terminalLines, setTerminalLines] = useState([
    '[Buddy] Terminal initialized in supervised semi-autonomous mode.',
    '[Buddy] Use local audits before trusting bot, customer, tool, skill, or cash-loop actions.',
  ]);

  async function queueCommand(nextCommand) {
    if (!nextCommand) return;

    setIsSubmitting(true);
    setTerminalLines((lines) => [
      ...lines,
      `$ ${nextCommand}`,
      '[Buddy] Creating governed operation packet...',
    ]);
    try {
      const result = await onCommandSubmit(nextCommand);
      const packet = result?.packet ?? result;
      setTerminalLines((lines) => [
        ...lines,
        `[Buddy] Packet ${packet?.id ?? 'local'} queued as ${packet?.operation_type ?? 'supervised_operation'}.`,
        `[Buddy] Mode: ${packet?.mode ?? 'sandbox_first_pull_request_review'}.`,
      ]);
      setCommand('');
    } catch (error) {
      setTerminalLines((lines) => [
        ...lines,
        `[Buddy] Packet API unavailable. Local supervised queue only: ${error.message}`,
      ]);
    } finally {
      setIsSubmitting(false);
    }
  }

  function handleKeyDown(event) {
    if (event.key !== 'Enter') return;
    queueCommand(command.trim());
  }

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="buddy-command-center-title"
      className="relative w-full max-w-6xl overflow-hidden rounded-2xl border border-amber-500/40 bg-[radial-gradient(circle_at_top_left,rgba(245,158,11,0.18),transparent_34%),linear-gradient(135deg,rgba(15,23,42,0.98),rgba(6,78,59,0.48),rgba(15,23,42,0.98))] p-5 shadow-2xl shadow-black/60"
    >
      <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-amber-300/80 to-transparent" />
      <div className="pointer-events-none absolute right-8 top-4 h-24 w-24 rounded-full border border-amber-300/20 bg-amber-300/10 blur-2xl" />
      <div className="mb-4 flex items-center justify-between">
        <h3 id="buddy-command-center-title" className="bg-gradient-to-r from-amber-200 via-yellow-100 to-emerald-200 bg-clip-text text-lg font-semibold text-transparent">
          👑 Buddy Command Center
        </h3>
        <div className="flex items-center gap-2">
          <span className="rounded-full border border-amber-400/40 bg-amber-950/40 px-2 py-0.5 text-xs font-medium text-amber-200">
            Semi-autonomous
          </span>
          <button
            type="button"
            aria-label="Close Buddy Command Center"
            onClick={onClose}
            className="rounded-lg border border-amber-500/30 bg-slate-950/40 px-3 py-1.5 text-xs font-medium text-slate-300 transition-colors hover:bg-amber-950/30 hover:text-white"
          >
            Close
          </button>
        </div>
      </div>

      <div className="mb-4 grid gap-3 lg:grid-cols-3">
        <div className="rounded-lg border border-amber-500/30 bg-slate-950/70 p-3 shadow-inner shadow-amber-950/30">
          <p className="text-xs font-semibold uppercase tracking-wide text-amber-200">Allowed automatically</p>
          <p className="mt-1 text-xs leading-5 text-slate-400">Read reports, research public sources, draft plans, run sandbox checks, and write local evidence reports.</p>
        </div>
        <div className="rounded-lg border border-amber-500/30 bg-slate-950/70 p-3 shadow-inner shadow-amber-950/30">
          <p className="text-xs font-semibold uppercase tracking-wide text-yellow-200">Approval required</p>
          <p className="mt-1 text-xs leading-5 text-slate-400">Customer contact, social posting, spending money, payment writes, deploys, and destructive commands.</p>
        </div>
        <div className="rounded-lg border border-emerald-400/30 bg-slate-950/70 p-3 shadow-inner shadow-emerald-950/30">
          <p className="text-xs font-semibold uppercase tracking-wide text-emerald-200">Evidence first</p>
          <p className="mt-1 text-xs leading-5 text-slate-400">Buddy should cite reports, source URLs, command results, and remaining risks before claiming progress.</p>
        </div>
      </div>

      <div
        role="log"
        aria-label="Buddy terminal output"
        className="mb-4 max-h-48 overflow-y-auto rounded-lg border border-amber-500/30 bg-slate-950/90 p-3 font-mono text-xs text-emerald-200 shadow-inner shadow-black/50"
      >
        {terminalLines.map((line, index) => (
          <p key={`${line}-${index}`} className="leading-5">
            {line}
          </p>
        ))}
      </div>

      <input
        type="text"
        value={command}
        onChange={(event) => setCommand(event.target.value)}
        onKeyDown={handleKeyDown}
        aria-label="Buddy command input"
        placeholder="Type a bot test, customer research, tool finder, skill finder, or cash-loop command…"
        className="mb-3 w-full rounded-lg border border-amber-500/30 bg-slate-950/80 px-3 py-2 text-sm text-white outline-none transition-colors placeholder:text-slate-500 focus:border-amber-300"
      />

      <button
        type="button"
        onClick={() => queueCommand(command.trim())}
        disabled={!command.trim() || isSubmitting}
        className="mb-3 rounded-lg border border-amber-300/60 bg-gradient-to-r from-amber-500 to-yellow-600 px-4 py-2 text-sm font-semibold text-slate-950 shadow-lg shadow-amber-950/30 transition-colors hover:from-amber-400 hover:to-yellow-500 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {isSubmitting ? 'Creating Packet...' : 'Create Buddy Packet'}
      </button>

      <div className="mb-5 flex flex-wrap gap-2" aria-label="Buddy quick commands">
        {QUICK_COMMANDS.map((quickCommand) => (
          <button
            key={quickCommand}
            type="button"
            onClick={() => queueCommand(quickCommand)}
            className="rounded-lg border border-amber-500/20 bg-slate-950/70 px-3 py-1.5 text-xs font-medium text-slate-300 transition-colors hover:border-amber-300 hover:text-amber-100"
          >
            {quickCommand}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        {PANELS.map((panel) => (
          <section key={panel.title} className="rounded-xl border border-amber-500/20 bg-slate-950/60 p-4">
            <h4 className="text-sm font-semibold text-amber-100">{panel.title}</h4>
            <p className="mt-2 text-xs leading-5 text-slate-400">{panel.detail}</p>
          </section>
        ))}
      </div>
    </div>
  );
}
