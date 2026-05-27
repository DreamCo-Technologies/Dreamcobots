import { useMemo } from 'react';

const DASHBOARD_LINKS = [
  { id: 'dashboard', label: 'Main Dashboard', url: '/dashboard' },
  { id: 'division', label: 'Division Dashboard', url: '/DivisionDashboard' },
  { id: 'dashboards', label: 'Dashboards Suite', url: '/dashboards' },
];

export default function EmbeddedDashboard() {
  const cards = useMemo(() => DASHBOARD_LINKS, []);

  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold text-slate-200">Connected Dashboards</h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {cards.map((card) => (
          <a
            key={card.id}
            href={card.url}
            target="_blank"
            rel="noreferrer"
            className="bg-dreamco-card border border-slate-700 rounded-xl p-4 hover:border-dreamco-accent transition-colors"
          >
            <p className="text-white text-sm font-semibold">{card.label}</p>
            <p className="text-xs text-slate-400 mt-2">{card.url}</p>
          </a>
        ))}
      </div>
    </div>
  );
}
