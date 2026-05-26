import { useState } from 'react';
import ActionsMonitor from './ActionsMonitor.jsx';
import BuddyCommandCenter from './BuddyCommandCenter.jsx';

/**
 * ActionsPage keeps Actions monitoring and command-center launch together.
 * To test keyboard command submits, pass `onBuddyCommandSubmit` from tests.
 */
export default function ActionsPage({
  ActionsMonitorComponent = ActionsMonitor,
  onBuddyCommandSubmit = () => {},
}) {
  const [showBuddyCenter, setShowBuddyCenter] = useState(false);

  return (
    <section>
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-lg font-semibold text-white">⚡ Actions</h2>
        <button
          type="button"
          onClick={() => setShowBuddyCenter(true)}
          className="rounded-lg bg-dreamco-accent px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-dreamco-accent/80"
        >
          Launch Full Buddy Command Center
        </button>
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
