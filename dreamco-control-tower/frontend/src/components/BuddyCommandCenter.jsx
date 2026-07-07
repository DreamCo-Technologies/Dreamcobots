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
  const [terminalLines, setTerminalLines] = useState([
    '[Buddy] Terminal initialized in supervised semi-autonomous mode.',
    '[Buddy] Use local audits before trusting bot, customer, tool, skill, or cash-loop actions.',
  ]);

  function queueCommand(nextCommand) {
    if (!nextCommand) return;

    onCommandSubmit(nextCommand);
    setTerminalLines((lines) => [
      ...lines,
      `$ ${nextCommand}`,
      `[Buddy] Command queued with evidence policy: ${nextCommand}`,
    ]);
    setCommand('');
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
      className="w-full max-w-6xl rounded-2xl border border-slate-700 bg-dreamco-card p-5 shadow-2xl"
    >
      <div className="mb-4 flex items-center justify-between">
        <h3 id="buddy-command-center-title" className="text-lg font-semibold text-white">
          🤖 Buddy Command Center
        </h3>
        <div className="flex items-center gap-2">
          <span className="rounded-full bg-yellow-900 px-2 py-0.5 text-xs font-medium text-yellow-300">
            Semi-autonomous
          </span>
          <button
            type="button"
            aria-label="Close Buddy Command Center"
            onClick={onClose}
            className="rounded-lg border border-slate-600 px-3 py-1.5 text-xs font-medium text-slate-300 transition-colors hover:bg-slate-700 hover:text-white"
          >
            Close
          </button>
        </div>
      </div>

      <div className="mb-4 grid gap-3 lg:grid-cols-3">
        <div className="rounded-lg border border-slate-700 bg-slate-900 p-3">
          <p className="text-xs font-semibold uppercase text-dreamco-accent">Allowed automatically</p>
          <p className="mt-1 text-xs leading-5 text-slate-400">Read reports, research public sources, draft plans, run sandbox checks, and write local evidence reports.</p>
        </div>
        <div className="rounded-lg border border-slate-700 bg-slate-900 p-3">
          <p className="text-xs font-semibold uppercase text-yellow-300">Approval required</p>
          <p className="mt-1 text-xs leading-5 text-slate-400">Customer contact, social posting, spending money, payment writes, deploys, and destructive commands.</p>
        </div>
        <div className="rounded-lg border border-slate-700 bg-slate-900 p-3">
          <p className="text-xs font-semibold uppercase text-green-300">Evidence first</p>
          <p className="mt-1 text-xs leading-5 text-slate-400">Buddy should cite reports, source URLs, command results, and remaining risks before claiming progress.</p>
        </div>
      </div>

      <div
        role="log"
        aria-label="Buddy terminal output"
        className="mb-4 max-h-48 overflow-y-auto rounded-lg border border-slate-700 bg-slate-950 p-3 font-mono text-xs text-green-300"
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
        className="mb-3 w-full rounded-lg border border-slate-600 bg-slate-800 px-3 py-2 text-sm text-white outline-none transition-colors focus:border-dreamco-accent"
      />

      <div className="mb-5 flex flex-wrap gap-2" aria-label="Buddy quick commands">
        {QUICK_COMMANDS.map((quickCommand) => (
          <button
            key={quickCommand}
            type="button"
            onClick={() => queueCommand(quickCommand)}
            className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-1.5 text-xs font-medium text-slate-300 transition-colors hover:border-dreamco-accent hover:text-white"
          >
            {quickCommand}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        {PANELS.map((panel) => (
          <section key={panel.title} className="rounded-xl border border-slate-700 bg-slate-800/50 p-4">
            <h4 className="text-sm font-semibold text-slate-200">{panel.title}</h4>
            <p className="mt-2 text-xs leading-5 text-slate-400">{panel.detail}</p>
          </section>
        ))}
      </div>
    </div>
  );
}
