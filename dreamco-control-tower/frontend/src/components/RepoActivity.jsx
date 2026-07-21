import { useEffect, useState } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';

function PRBadge({ count, label, highlight }) {
  return (
    <div
      className={`rounded-lg px-3 py-2 text-center ${highlight ? 'bg-dreamco-accent/20 border border-dreamco-accent/40' : 'bg-slate-700'}`}
    >
      <div className={`text-xl font-bold ${highlight ? 'text-dreamco-accent' : 'text-white'}`}>
        {count}
      </div>
      <div className="text-xs text-slate-400">{label}</div>
    </div>
  );
}

function buildActivityData(bots) {
  return bots.map((b) => ({
    name: b.name.split('-').slice(0, 2).join('-'),
    open: b.openPRs ?? 0,
    merged: b.mergedPRs ?? 0,
    issues: b.openIssues ?? 0,
  }));
}

export default function RepoActivity() {
  const [bots, setBots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [view, setView] = useState('list'); // 'list' | 'chart'

  useEffect(() => {
    fetch('/api/bots')
      .then((r) => r.json())
      .then((data) => {
        setBots(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) return <p className="text-slate-400">Loading activity…</p>;

  const totalOpenPRs = bots.reduce((s, b) => s + (b.openPRs ?? 0), 0);
  const totalMergedPRs = bots.reduce((s, b) => s + (b.mergedPRs ?? 0), 0);
  const totalIssues = bots.reduce((s, b) => s + (b.openIssues ?? 0), 0);
  const pendingUpgrades = bots.reduce((s, b) => s + (b.pendingPRs ?? 0), 0);

  const activityData = buildActivityData(bots);

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-white">📦 Repository Activity</h2>
        <div className="flex gap-2">
          <button
            onClick={() => setView('list')}
            className={`text-xs px-3 py-1.5 rounded-lg transition-colors ${view === 'list' ? 'bg-dreamco-accent text-white' : 'bg-slate-700 text-slate-400 hover:text-white'}`}
          >
            List
          </button>
          <button
            onClick={() => setView('chart')}
            className={`text-xs px-3 py-1.5 rounded-lg transition-colors ${view === 'chart' ? 'bg-dreamco-accent text-white' : 'bg-slate-700 text-slate-400 hover:text-white'}`}
          >
            Chart
          </button>
        </div>
      </div>

      {/* Aggregate stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-5">
        <PRBadge count={totalOpenPRs} label="Total Open PRs" highlight={totalOpenPRs > 0} />
        <PRBadge count={totalMergedPRs} label="Total Merged PRs" />
        <PRBadge count={totalIssues} label="Open Issues" highlight={totalIssues > 0} />
        <PRBadge count={pendingUpgrades} label="Pending Upgrades" highlight={pendingUpgrades > 0} />
      </div>

      {view === 'chart' && activityData.length > 0 && (
        <div className="bg-dreamco-card rounded-xl p-5 border border-slate-700 mb-5">
          <h3 className="text-sm font-semibold text-slate-300 mb-4">Activity by Bot</h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={activityData} margin={{ top: 0, right: 8, bottom: 0, left: -20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="name" stroke="#94a3b8" tick={{ fontSize: 10 }} />
              <YAxis stroke="#94a3b8" tick={{ fontSize: 10 }} allowDecimals={false} />
              <Tooltip contentStyle={{ background: '#1e293b', border: 'none', fontSize: 12 }} />
              <Legend wrapperStyle={{ fontSize: 11, color: '#94a3b8' }} />
              <Bar dataKey="open" fill="#6366f1" name="Open PRs" radius={[3, 3, 0, 0]} />
              <Bar dataKey="merged" fill="#22c55e" name="Merged PRs" radius={[3, 3, 0, 0]} />
              <Bar dataKey="issues" fill="#f59e0b" name="Issues" radius={[3, 3, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {view === 'list' && (
        <div className="space-y-4">
          {bots.map((bot) => (
            <div
              key={bot.name}
              className="bg-dreamco-card rounded-xl p-5 border border-slate-700"
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-white">{bot.name}</h3>
                <span className="text-xs text-slate-400">{bot.repoName}</span>
              </div>

              <div className="grid grid-cols-3 gap-3 mb-4">
                <PRBadge count={bot.openPRs ?? '—'} label="Open PRs" highlight={(bot.openPRs ?? 0) > 0} />
                <PRBadge count={bot.mergedPRs ?? '—'} label="Merged PRs" />
                <PRBadge count={bot.openIssues ?? '—'} label="Issues" highlight={(bot.openIssues ?? 0) > 0} />
              </div>

              {/* Workflow status pill */}
              <div className="flex items-center gap-2 text-xs">
                <span className="text-slate-400">Latest workflow:</span>
                <span
                  className={`px-2 py-0.5 rounded-full font-medium ${
                    bot.workflowStatus === 'success'
                      ? 'bg-green-900 text-green-300'
                      : bot.workflowStatus === 'failure'
                        ? 'bg-red-900 text-red-300'
                        : 'bg-slate-700 text-slate-400'
                  }`}
                >
                  {bot.workflowStatus ?? 'unknown'}
                </span>

                {(bot.pendingPRs ?? 0) > 0 && (
                  <span className="ml-auto px-2 py-0.5 rounded-full bg-dreamco-yellow/20 text-dreamco-yellow font-medium">
                    {bot.pendingPRs} pending upgrade{bot.pendingPRs !== 1 ? 's' : ''}
                  </span>
                )}
              </div>
            </div>
          ))}

          {bots.length === 0 && <p className="text-slate-500">No bots registered yet.</p>}
        </div>
      )}

      <p className="mt-4 text-xs text-slate-500">
        ℹ️ Live PR counts and commit history require a valid GITHUB_TOKEN in the backend.
      </p>
    </div>
  );
}
