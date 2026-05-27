import { useMemo, useState } from 'react';
import BuddyTester from './BuddyTester.jsx';
import CommandCenter from './CommandCenter.jsx';
import EmbeddedDashboard from './EmbeddedDashboard.jsx';

const SIDEBAR_ITEMS = [
  { id: 'bots', label: 'Bots' },
  { id: 'swarms', label: 'Swarms' },
  { id: 'dreamos', label: 'DreamOS' },
  { id: 'marketplace', label: 'Marketplace' },
];

const METRICS = [
  { label: 'Stigmergy density', value: '0.84' },
  { label: 'HotStuff consensus', value: 'Healthy' },
  { label: 'Economic loop', value: '+$1,250/day sim' },
  { label: 'Bot evolution', value: '82% toward target' },
];

export default function BuddyCommandCenter() {
  const [activeSection, setActiveSection] = useState('bots');
  const [deterministicMode, setDeterministicMode] = useState(true);
  const metrics = useMemo(() => METRICS, []);

  return (
    <div className="grid grid-cols-1 xl:grid-cols-[220px_1fr_280px] gap-4">
      <aside className="bg-dreamco-card border border-slate-700 rounded-xl p-4">
        <p className="text-xs uppercase tracking-wide text-slate-400 mb-3">Repo Navigation</p>
        <div className="space-y-2">
          {SIDEBAR_ITEMS.map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveSection(item.id)}
              className={`w-full text-left text-sm rounded-lg px-3 py-2 ${
                activeSection === item.id
                  ? 'bg-dreamco-accent text-white'
                  : 'bg-slate-800 text-slate-300 hover:text-white'
              }`}
            >
              {item.label}
            </button>
          ))}
        </div>
      </aside>

      <section className="space-y-4">
        <div className="bg-dreamco-card border border-slate-700 rounded-xl p-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <p className="text-sm text-slate-200">
              Live Buddy execution pane connected to event bus + BuddyAI core.
            </p>
            <label className="inline-flex items-center gap-2 text-xs text-slate-300">
              <input
                type="checkbox"
                checked={deterministicMode}
                onChange={(e) => setDeterministicMode(e.target.checked)}
                className="accent-indigo-500"
              />
              Deterministic mode
            </label>
          </div>
          <p className="text-xs text-slate-400 mt-2">
            Seeded simulations: {deterministicMode ? 'enabled' : 'disabled'}
          </p>
        </div>
        <BuddyTester />
        <CommandCenter />
        <EmbeddedDashboard />
      </section>

      <aside className="bg-dreamco-card border border-slate-700 rounded-xl p-4">
        <p className="text-xs uppercase tracking-wide text-slate-400 mb-3">Real-time Metrics</p>
        <div className="space-y-3">
          {metrics.map((metric) => (
            <div key={metric.label} className="border border-slate-700 rounded-lg p-3 bg-slate-900/40">
              <p className="text-xs text-slate-400">{metric.label}</p>
              <p className="text-sm text-white font-medium mt-1">{metric.value}</p>
            </div>
          ))}
        </div>
      </aside>
    </div>
  );
}
