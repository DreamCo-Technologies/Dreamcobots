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

const AGENT_DEBUG_PLAYBOOK = [
  ['Capture', 'Heartbeat, workflow status, last PR, dashboard link, and failed command.'],
  ['Diagnose', 'Separate bot code, workflow config, stale data, resource library, and integration failures.'],
  ['Repair', 'Prepare a supervised patch packet with tests, rollback notes, and owner approval gates.'],
  ['Retest', 'Run bot smoke checks, workflow rerun, dashboard proof, and prospectus link verification.'],
];

const AGENT_PAST_FAILURE_REBUILD_FLOW = [
  ['Collect history', 'Past runtime errors, workflow failures, pending PRs, stale heartbeats, and broken links.'],
  ['Rebuild packet', 'Create the bot route, smoke test, resource check, dashboard link, and prospectus proof.'],
  ['Retest agent', 'Run the smallest safe bot test and capture workflow or dashboard evidence.'],
  ['Promote or assign', 'Mark rebuilt, still blocked, duplicate, or owner approval needed.'],
];

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
  const failedOrRiskyBots = bots.filter((bot) => (
    bot.status === 'error'
    || bot.workflowStatus === 'failure'
    || Number(bot.pendingPRs || 0) > 0
  ));
  const pastAgentFailurePackets = failedOrRiskyBots.map((bot) => ({
    id: bot.slug ?? bot.name,
    title: bot.name,
    source: bot.workflowStatus === 'failure' ? 'Past workflow failure' : bot.status === 'error' ? 'Past runtime failure' : 'Past PR blocker',
    evidence: bot.workflowStatus === 'failure' ? 'Workflow failure' : bot.status === 'error' ? 'Runtime error' : `${bot.pendingPRs} pending PR(s)`,
  }));

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

      <section className="mb-5 border border-slate-700 bg-slate-950 p-5">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-xs font-bold uppercase text-dreamco-accent">Agent failure command deck</p>
            <h3 className="mt-1 text-lg font-semibold text-white">Debug every bot before client handoff</h3>
            <p className="mt-1 max-w-3xl text-sm leading-6 text-slate-400">
              Buddy treats every agent failure as an evidence packet: capture the signal, diagnose the source,
              prepare a supervised repair, and retest before the bot is shown as ready.
            </p>
          </div>
          <span className={`rounded-full border px-3 py-1 text-xs font-semibold ${
            failedOrRiskyBots.length === 0
              ? 'border-green-800 bg-green-950/30 text-green-300'
              : 'border-yellow-800 bg-yellow-950/30 text-yellow-300'
          }`}>
            {failedOrRiskyBots.length} bot debug target(s)
          </span>
        </div>

        <div className="mt-4 grid gap-px overflow-hidden border border-slate-800 bg-slate-800 md:grid-cols-4">
          {AGENT_DEBUG_PLAYBOOK.map(([title, detail], index) => (
            <div key={title} className="min-h-28 bg-slate-900 p-3">
              <p className="font-mono text-[11px] text-dreamco-accent">0{index + 1}</p>
              <h4 className="mt-2 text-sm font-semibold text-white">{title}</h4>
              <p className="mt-2 text-xs leading-5 text-slate-400">{detail}</p>
            </div>
          ))}
        </div>

        {failedOrRiskyBots.length > 0 && (
          <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
            {failedOrRiskyBots.slice(0, 6).map((bot) => (
              <article key={`${bot.name}-debug`} className="border border-yellow-800 bg-yellow-950/10 p-3">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="text-sm font-semibold text-white">{bot.emoji ?? '🤖'} {bot.name}</p>
                    <p className="mt-1 text-xs text-yellow-100">
                      {bot.workflowStatus === 'failure' ? 'Workflow failure' : bot.status === 'error' ? 'Runtime error' : 'Pending PR review'}
                    </p>
                  </div>
                  <span className="rounded-full border border-yellow-700 px-2 py-0.5 text-[11px] font-semibold uppercase text-yellow-200">
                    debug route
                  </span>
                </div>
                <p className="mt-3 text-xs leading-5 text-slate-300">
                  Run the smallest bot smoke test, inspect the latest workflow evidence, verify dashboard and prospectus links,
                  then package the fix for owner review.
                </p>
              </article>
            ))}
          </div>
        )}

        <div className="mt-4 border border-slate-800 bg-slate-900 p-4">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <h4 className="text-sm font-semibold text-white">Past agent failure rebuild backlog</h4>
              <p className="mt-1 max-w-3xl text-xs leading-5 text-slate-400">
                Buddy converts old agent failures into rebuild work: route, smoke test, resource proof, dashboard link,
                prospectus link, and owner-ready retest evidence.
              </p>
            </div>
            <span className="rounded-full border border-slate-700 px-3 py-1 text-xs font-semibold text-slate-300">
              {pastAgentFailurePackets.length} rebuild packet(s)
            </span>
          </div>

          <div className="mt-4 grid gap-px overflow-hidden border border-slate-800 bg-slate-800 md:grid-cols-4">
            {AGENT_PAST_FAILURE_REBUILD_FLOW.map(([title, detail], index) => (
              <div key={title} className="min-h-28 bg-slate-950 p-3">
                <p className="font-mono text-[11px] text-dreamco-accent">0{index + 1}</p>
                <h5 className="mt-2 text-sm font-semibold text-white">{title}</h5>
                <p className="mt-2 text-xs leading-5 text-slate-400">{detail}</p>
              </div>
            ))}
          </div>

          {pastAgentFailurePackets.length > 0 && (
            <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
              {pastAgentFailurePackets.slice(0, 6).map((packet) => (
                <article key={`past-${packet.id}`} className="border border-slate-800 bg-slate-950 p-3">
                  <p className="text-[11px] font-bold uppercase text-dreamco-accent">{packet.source}</p>
                  <h5 className="mt-1 text-sm font-semibold text-white">{packet.title}</h5>
                  <p className="mt-2 text-xs leading-5 text-yellow-100">{packet.evidence}</p>
                  <p className="mt-2 text-xs leading-5 text-slate-400">
                    Build missing route, test, resources, dashboard proof, and prospectus proof before marking ready.
                  </p>
                </article>
              ))}
            </div>
          )}
        </div>
      </section>

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

              {(bot.status === 'error' || bot.workflowStatus === 'failure') && (
                <div className="mt-3 border border-yellow-800 bg-yellow-950/20 p-3">
                  <p className="text-xs font-semibold uppercase text-yellow-200">Buddy debug packet</p>
                  <p className="mt-1 text-xs leading-5 text-slate-300">
                    Capture failing signal, isolate bot or workflow cause, prepare supervised patch, and retest before ready.
                  </p>
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
