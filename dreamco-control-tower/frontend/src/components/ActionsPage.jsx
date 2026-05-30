import { useState } from 'react';
import ActionsMonitor from './ActionsMonitor.jsx';
import BuddyCommandCenter from './BuddyCommandCenter.jsx';
import BuddyCommandSections from './BuddyCommandSections.jsx';

/**
 * ActionsPage keeps Actions monitoring and command-center launch together.
 * To test keyboard command submits, pass `onBuddyCommandSubmit` from tests.
 */
export default function ActionsPage({
  ActionsMonitorComponent = ActionsMonitor,
  onBuddyCommandSubmit = () => {},
  lastDispatch = null,
  onOpenAgentsPage = () => {},
}) {
  const [showBuddyCenter, setShowBuddyCenter] = useState(false);

  function handleRunCommand(command) {
    onBuddyCommandSubmit(command);
  }

  return (
    <section>
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-lg font-semibold text-white">⚡ Actions</h2>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={onOpenAgentsPage}
            className="rounded-lg border border-slate-600 px-4 py-2 text-sm font-medium text-slate-200 transition-colors hover:bg-slate-700"
          >
            Open Agents Coordination
          </button>
          <button
            type="button"
            onClick={() => setShowBuddyCenter(true)}
            className="rounded-lg bg-dreamco-accent px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-dreamco-accent/80"
          >
            Launch Full Buddy Command Center
          </button>
        </div>
      </div>

      {lastDispatch && (
        <div className="mb-4 rounded-xl border border-slate-700 bg-dreamco-card p-4">
          <p className="text-xs uppercase tracking-wide text-slate-400">Latest command arbitration</p>
          <p className="mt-1 text-sm text-white">
            {lastDispatch.command?.command || '—'}
          </p>
          <p className="mt-1 text-xs text-slate-300">
            {lastDispatch.duplicate
              ? `Duplicate detected — linked to ${lastDispatch.duplicate_of}`
              : `Selected agent: ${lastDispatch.selected_agent?.name || 'unassigned'}`}
          </p>
        </div>
      )}

      <ActionsMonitorComponent />
      <BuddyCommandSections onRunCommand={handleRunCommand} />

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
