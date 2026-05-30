import { useState } from 'react';
import { PINNED_TOP_ACTIONS } from './buddyCommandCatalog.js';

const PANELS = ['Swarm Status', 'HotStuff Consensus', 'Economic Feedback Loops'];
const SWARM_SHORTCUTS = ['Start Agent Swarm', 'Stop Agent Swarm', 'Memory Sync', 'Agent Diagnostics'];

/**
 * Full-size Buddy command center modal content used by ActionsPage.
 * Keep headings stable for UI tests when adding/removing future panels.
 */
export default function BuddyCommandCenter({ onClose, onCommandSubmit = () => {} }) {
  const [command, setCommand] = useState('');
  const [terminalLines, setTerminalLines] = useState([
    '[Buddy] Terminal initialized in autonomous mode.',
    '[Buddy] Type a command and press Enter.',
  ]);

  function handleKeyDown(event) {
    if (event.key !== 'Enter') return;

    const nextCommand = command.trim();
    if (!nextCommand) return;

    onCommandSubmit(nextCommand);
    setTerminalLines((lines) => [
      ...lines,
      `$ ${nextCommand}`,
      `[Buddy] Command queued: ${nextCommand}`,
    ]);
    setCommand('');
  }

  function runQuickAction(nextCommand) {
    onCommandSubmit(nextCommand);
    setTerminalLines((lines) => [
      ...lines,
      `$ ${nextCommand}`,
      `[Buddy] Quick action executed: ${nextCommand}`,
    ]);
  }

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="buddy-command-center-title"
      className="w-full max-w-5xl rounded-2xl border border-slate-700 bg-dreamco-card p-5 shadow-2xl"
    >
      <div className="mb-4 flex items-center justify-between">
        <h3 id="buddy-command-center-title" className="text-lg font-semibold text-white">
          🤖 Buddy Command Center
        </h3>
        <div className="flex items-center gap-2">
          <span className="rounded-full bg-green-900 px-2 py-0.5 text-xs font-medium text-green-300">
            Autonomous
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

      <section className="mb-4 rounded-lg border border-slate-700 bg-slate-900/50 p-3">
        <h4 className="text-xs font-semibold uppercase tracking-wide text-slate-300">
          Pinned Mission Controls
        </h4>
        <div className="mt-2 grid grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-4">
          {PINNED_TOP_ACTIONS.map((action) => (
            <button
              key={action}
              type="button"
              onClick={() => runQuickAction(action)}
              className="rounded-lg border border-slate-600 px-3 py-2 text-left text-xs text-slate-200 transition-colors hover:border-dreamco-accent hover:text-white"
            >
              {action}
            </button>
          ))}
        </div>
      </section>

      {/*
       * Keep this output region stable for UI tests and future command-render updates.
       * New command handlers should append summary lines instead of replacing this log.
       */}
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
        placeholder="Type a command and press Enter…"
        className="mb-5 w-full rounded-lg border border-slate-600 bg-slate-800 px-3 py-2 text-sm text-white outline-none transition-colors focus:border-dreamco-accent"
      />

      <section className="mb-5 rounded-lg border border-slate-700 bg-slate-900/50 p-3">
        <h4 className="text-xs font-semibold uppercase tracking-wide text-slate-300">Swarm Shortcuts</h4>
        <div className="mt-2 flex flex-wrap gap-2">
          {SWARM_SHORTCUTS.map((action) => (
            <button
              key={action}
              type="button"
              onClick={() => runQuickAction(action)}
              className="rounded-full border border-slate-600 px-3 py-1.5 text-xs text-slate-200 transition-colors hover:border-dreamco-accent hover:text-white"
            >
              {action}
            </button>
          ))}
        </div>
      </section>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        {PANELS.map((title) => (
          <section key={title} className="rounded-xl border border-slate-700 bg-slate-800/50 p-4">
            <h4 className="text-sm font-semibold text-slate-200">{title}</h4>
            <p className="mt-2 text-xs text-slate-400">
              Real-time command telemetry and execution summaries render here.
            </p>
          </section>
        ))}
      </div>
    </div>
  );
}
