/**
 * ActionsMonitor.jsx
 *
 * Displays live GitHub Actions workflow runs fetched from the Control Tower
 * backend at /api/actions.  Read-only view — no workflow triggers.
 *
 * Features:
 *  - Auto-refresh every 60 seconds (configurable via REFRESH_INTERVAL_MS)
 *  - Status/conclusion badge colour coding
 *  - Branch, event, and started-at columns
 *  - Link to the run on GitHub
 */

import { useEffect, useRef, useState } from 'react';

const REFRESH_INTERVAL_MS = 60_000;

const CONCLUSION_STYLE = {
  success: 'bg-green-900 text-green-300',
  failure: 'bg-red-900 text-red-300',
  cancelled: 'bg-slate-700 text-slate-400',
  skipped: 'bg-slate-700 text-slate-400',
  timed_out: 'bg-orange-900 text-orange-300',
  action_required: 'bg-yellow-900 text-yellow-300',
};

const STATUS_STYLE = {
  completed: 'text-slate-300',
  in_progress: 'text-dreamco-yellow',
  queued: 'text-slate-400',
  waiting: 'text-slate-400',
};

function ConclusionBadge({ conclusion }) {
  const cls = CONCLUSION_STYLE[conclusion] ?? 'bg-slate-700 text-slate-400';
  return (
    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${cls}`}>
      {conclusion ?? '—'}
    </span>
  );
}

function StatusText({ status }) {
  const cls = STATUS_STYLE[status] ?? 'text-slate-400';
  return <span className={`text-xs font-medium ${cls}`}>{status ?? '—'}</span>;
}

function formatDate(iso) {
  if (!iso) return '—';
  const d = new Date(iso);
  if (isNaN(d)) return iso;
  return d.toLocaleString(undefined, { dateStyle: 'short', timeStyle: 'short' });
}

export default function ActionsMonitor() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastRefresh, setLastRefresh] = useState(null);
  const intervalRef = useRef(null);

  function fetchActions() {
    fetch('/api/actions')
      .then((r) => r.json())
      .then((json) => {
        setData(json);
        setLastRefresh(new Date());
        setLoading(false);
        setError(null);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }

  useEffect(() => {
    fetchActions();
    intervalRef.current = setInterval(fetchActions, REFRESH_INTERVAL_MS);
    return () => clearInterval(intervalRef.current);
  }, []);

  const runs = data?.runs ?? [];
  const source = data?.source ?? 'unknown';

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-white">⚡ GitHub Actions Monitor</h2>
        <div className="flex items-center gap-3">
          {lastRefresh && (
            <span className="text-xs text-slate-500">
              Last refresh: {lastRefresh.toLocaleTimeString()}
            </span>
          )}
          <button
            onClick={fetchActions}
            className="text-xs px-3 py-1.5 bg-slate-700 text-slate-300 hover:text-white rounded-lg transition-colors"
          >
            🔄 Refresh
          </button>
        </div>
      </div>

      {/* Source badge */}
      <div className="mb-4">
        <span
          className={`text-xs px-2 py-0.5 rounded-full font-medium ${
            source === 'github_api'
              ? 'bg-green-900 text-green-300'
              : 'bg-slate-700 text-slate-400'
          }`}
        >
          {source === 'github_api' ? '🟢 Live from GitHub API' : '⚠️ Data unavailable'}
        </span>
        {source !== 'github_api' && (
          <span className="ml-2 text-xs text-slate-500">
            — set GITHUB_TOKEN in the backend environment for live data
          </span>
        )}
      </div>

      {loading && <p className="text-slate-400">Loading workflow runs…</p>}
      {error && <p className="text-dreamco-red">Error: {error}</p>}

      {!loading && runs.length === 0 && (
        <div className="bg-dreamco-card rounded-xl p-6 border border-slate-700 text-center">
          <p className="text-slate-400 text-sm">No workflow runs found.</p>
          <p className="text-slate-500 text-xs mt-1">
            Ensure GITHUB_TOKEN is configured and the repository has Actions enabled.
          </p>
        </div>
      )}

      {runs.length > 0 && (
        <div className="overflow-x-auto rounded-xl border border-slate-700">
          <table className="w-full text-sm text-left">
            <thead className="bg-slate-800 text-slate-400 text-xs uppercase">
              <tr>
                <th className="px-4 py-3">Workflow</th>
                <th className="px-4 py-3">Branch</th>
                <th className="px-4 py-3">Event</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Conclusion</th>
                <th className="px-4 py-3">Started</th>
                <th className="px-4 py-3">Link</th>
              </tr>
            </thead>
            <tbody>
              {runs.map((run) => (
                <tr
                  key={run.id}
                  className="border-t border-slate-700 bg-dreamco-card hover:bg-slate-700/30 transition-colors"
                >
                  <td className="px-4 py-3 font-medium text-white">
                    {run.name ?? `Run #${run.id}`}
                  </td>
                  <td className="px-4 py-3 text-slate-300 text-xs font-mono">
                    {run.branch ?? '—'}
                  </td>
                  <td className="px-4 py-3 text-slate-400 text-xs">{run.event ?? '—'}</td>
                  <td className="px-4 py-3">
                    <StatusText status={run.status} />
                  </td>
                  <td className="px-4 py-3">
                    <ConclusionBadge conclusion={run.conclusion} />
                  </td>
                  <td className="px-4 py-3 text-slate-400 text-xs">
                    {formatDate(run.run_started_at)}
                  </td>
                  <td className="px-4 py-3">
                    {run.url ? (
                      <a
                        href={run.url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-dreamco-accent underline text-xs"
                      >
                        View
                      </a>
                    ) : (
                      '—'
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
