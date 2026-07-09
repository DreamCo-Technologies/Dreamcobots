import { useEffect, useState } from 'react';

const STATUS_COLOR = {
  active: 'text-dreamco-green',
  idle: 'text-slate-400',
  error: 'text-dreamco-red',
  updating: 'text-dreamco-yellow',
};

const STATUS_DOT = {
  active: 'bg-dreamco-green',
  idle: 'bg-slate-500',
  error: 'bg-dreamco-red',
  updating: 'bg-dreamco-yellow',
};

function formatHeartbeat(ts) {
  if (!ts) return 'Never';
  const diff = Date.now() - new Date(ts).getTime();
  const mins = Math.floor(diff / 60_000);
  if (mins < 1) return 'Just now';
  if (mins < 60) return `${mins}m ago`;
  return `${Math.floor(mins / 60)}h ago`;
}

function StatusSummaryBar({ bots }) {
  const counts = bots.reduce(
    (acc, b) => {
      acc[b.status] = (acc[b.status] ?? 0) + 1;
      return acc;
    },
    { active: 0, idle: 0, error: 0, updating: 0 },
  );
  return (
    <div className="flex gap-4 mb-4 text-xs">
      {Object.entries(counts).map(([status, count]) => (
        <div key={status} className="flex items-center gap-1.5">
          <span className={`w-2 h-2 rounded-full ${STATUS_DOT[status] ?? 'bg-slate-500'}`} />
          <span className="text-slate-300">
            {count} {status}
          </span>
        </div>
      ))}
    </div>
  );
}

export default function BotOverview() {
  const [bots, setBots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [teamFilter, setTeamFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [search, setSearch] = useState('');

  useEffect(() => {
    fetch('/api/bots')
      .then((r) => r.json())
      .then((data) => {
        setBots(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) return <p className="text-slate-400">Loading bots…</p>;
  if (error) return <p className="text-dreamco-red">Error: {error}</p>;

  // Derive team list from bot data
  const teams = ['all', ...new Set(bots.map((b) => b.team || 'default'))];

  const visible = bots.filter((bot) => {
    const matchTeam = teamFilter === 'all' || (bot.team || 'default') === teamFilter;
    const matchStatus = statusFilter === 'all' || bot.status === statusFilter;
    const matchSearch =
      !search || bot.name.toLowerCase().includes(search.toLowerCase());
    return matchTeam && matchStatus && matchSearch;
  });

  return (
    <div>
      <h2 className="text-lg font-semibold text-white mb-4">🤖 Bot Overview</h2>

      {/* Summary bar */}
      <StatusSummaryBar bots={bots} />

      {/* Filters */}
      <div className="flex flex-wrap gap-3 mb-5">
        <input
          type="text"
          placeholder="Search bots…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="bg-slate-700 border border-slate-600 text-white text-sm rounded-lg px-3 py-1.5 focus:outline-none focus:border-dreamco-accent"
        />

        <select
          value={teamFilter}
          onChange={(e) => setTeamFilter(e.target.value)}
          className="bg-slate-700 border border-slate-600 text-white text-sm rounded-lg px-3 py-1.5 focus:outline-none focus:border-dreamco-accent"
        >
          {teams.map((t) => (
            <option key={t} value={t}>
              Team: {t}
            </option>
          ))}
        </select>

        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="bg-slate-700 border border-slate-600 text-white text-sm rounded-lg px-3 py-1.5 focus:outline-none focus:border-dreamco-accent"
        >
          {['all', 'active', 'idle', 'error', 'updating'].map((s) => (
            <option key={s} value={s}>
              Status: {s}
            </option>
          ))}
        </select>

        <span className="text-xs text-slate-400 self-center">
          {visible.length} / {bots.length} bots
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {visible.map((bot) => (
          <div key={bot.name} className="bg-dreamco-card rounded-xl p-5 border border-slate-700">
            {/* Bot name + status dot */}
            <div className="flex items-center justify-between mb-3">
              <div>
                <span className="mr-2 text-xl" aria-hidden="true">{bot.emoji ?? '🤖'}</span>
                <span className="font-semibold text-white">{bot.name}</span>
                {bot.team && (
                  <span className="ml-2 text-xs px-1.5 py-0.5 bg-slate-700 text-slate-400 rounded">
                    {bot.team}
                  </span>
                )}
              </div>
              <span
                className={`inline-flex items-center gap-1.5 text-xs font-medium ${STATUS_COLOR[bot.status] ?? 'text-slate-400'}`}
              >
                <span
                  className={`w-2 h-2 rounded-full ${STATUS_DOT[bot.status] ?? 'bg-slate-500'}`}
                />
                {bot.status ?? 'unknown'}
              </span>
            </div>

            {/* Tier badge */}
            {bot.tier && (
              <div className="mb-2">
                <span className="text-xs px-2 py-0.5 bg-dreamco-accent/20 text-dreamco-accent rounded-full font-medium">
                  {bot.tier}
                </span>
              </div>
            )}

            {/* Heartbeat + workflow */}
            <div className="text-xs text-slate-400 space-y-1">
              <div>
                💓 Last heartbeat:{' '}
                <span className="text-slate-300">{formatHeartbeat(bot.lastHeartbeat)}</span>
              </div>

              <div>
                ⚙️ Workflow:{' '}
                <span
                  className={
                    bot.workflowStatus === 'success'
                      ? 'text-dreamco-green'
                      : bot.workflowStatus === 'failure'
                        ? 'text-dreamco-red'
                        : 'text-slate-400'
                  }
                >
                  {bot.workflowStatus ?? 'unknown'}
                </span>
              </div>

              {typeof bot.pendingPRs === 'number' && bot.pendingPRs > 0 && (
                <div>
                  🔀 Pending PRs:{' '}
                  <span className="text-dreamco-yellow font-semibold">{bot.pendingPRs}</span>
                </div>
              )}

              <div className="flex gap-3 pt-2">
                <a
                  href={`/${bot.dashboardUrl ?? `docs/bots/index.html?bot=${encodeURIComponent(bot.slug ?? bot.bot_id)}`}`}
                  className="text-dreamco-accent underline"
                >
                  Dashboard
                </a>
                <a
                  href={`/${bot.prospectusUrl ?? `docs/bots/index.html?bot=${encodeURIComponent(bot.slug ?? bot.bot_id)}#prospectus`}`}
                  className="text-dreamco-accent underline"
                >
                  Prospectus
                </a>
              </div>

              {/* Last PR */}
              {bot.lastPR && (
                <div>
                  🔀 Last PR:{' '}
                  <a
                    href={bot.lastPR}
                    target="_blank"
                    rel="noreferrer"
                    className="text-dreamco-accent underline"
                  >
                    view
                  </a>
                </div>
              )}
            </div>
          </div>
        ))}

        {visible.length === 0 && (
          <p className="text-slate-500 col-span-3">No bots match the current filters.</p>
        )}
      </div>
    </div>
  );
}
