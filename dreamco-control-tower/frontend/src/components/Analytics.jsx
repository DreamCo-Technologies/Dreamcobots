import { useEffect, useState } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from 'recharts';

const COLORS = ['#6366f1', '#22c55e', '#f59e0b', '#ef4444', '#06b6d4'];

function StatCard({ label, value, sub }) {
  return (
    <div className="bg-dreamco-card rounded-xl p-5 border border-slate-700">
      <div className="text-2xl font-bold text-white">{value}</div>
      <div className="text-sm text-slate-300 mt-1">{label}</div>
      {sub && <div className="text-xs text-slate-500 mt-0.5">{sub}</div>}
    </div>
  );
}

// Build mock uptime data from bots list
function buildUptimeData(bots) {
  return bots.map((b, i) => ({
    name: b.name.split('-').slice(0, 2).join('-'),
    uptime: b.lastHeartbeat ? Math.max(60, 99 - i * 3) : 0,
  }));
}

// Build mock PR trend data (last 7 days placeholder)
const PR_TREND = [
  { day: 'Mon', opened: 2, merged: 1 },
  { day: 'Tue', opened: 3, merged: 2 },
  { day: 'Wed', opened: 1, merged: 3 },
  { day: 'Thu', opened: 4, merged: 2 },
  { day: 'Fri', opened: 2, merged: 4 },
  { day: 'Sat', opened: 0, merged: 1 },
  { day: 'Sun', opened: 1, merged: 0 },
];

export default function Analytics() {
  const [bots, setBots] = useState([]);
  const [systemStatus, setSystemStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([fetch('/api/bots'), fetch('/api/status')])
      .then(([b, s]) => Promise.all([b.json(), s.json()]))
      .then(([botsData, statusData]) => {
        setBots(botsData);
        setSystemStatus(statusData);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) return <p className="text-slate-400">Loading analytics…</p>;

  const activeCount = systemStatus?.bots?.active ?? 0;
  const totalCount = systemStatus?.bots?.total ?? bots.length;
  const staleCount = systemStatus?.bots?.stale ?? 0;
  const healthLabel = systemStatus?.health ?? 'unknown';

  const uptimeData = buildUptimeData(bots);

  // Pie: status distribution
  const statusCounts = bots.reduce((acc, b) => {
    acc[b.status] = (acc[b.status] ?? 0) + 1;
    return acc;
  }, {});
  const pieData = Object.entries(statusCounts).map(([name, value]) => ({ name, value }));

  return (
    <div>
      <h2 className="text-lg font-semibold text-white mb-4">📊 Analytics</h2>

      {/* Stat cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatCard label="Total Bots" value={totalCount} />
        <StatCard label="Active Bots" value={activeCount} sub="sent heartbeat recently" />
        <StatCard label="Stale Bots" value={staleCount} sub="no heartbeat > 5 min" />
        <StatCard
          label="System Health"
          value={healthLabel === 'healthy' ? '✅' : '⚠️'}
          sub={healthLabel}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* PR Trend (last 7 days) */}
        <div className="bg-dreamco-card rounded-xl p-5 border border-slate-700">
          <h3 className="text-sm font-semibold text-slate-300 mb-4">PR Trend (last 7 days)</h3>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={PR_TREND}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="day" stroke="#94a3b8" tick={{ fontSize: 11 }} />
              <YAxis stroke="#94a3b8" tick={{ fontSize: 11 }} />
              <Tooltip contentStyle={{ background: '#1e293b', border: 'none' }} />
              <Line
                type="monotone"
                dataKey="opened"
                stroke="#6366f1"
                strokeWidth={2}
                dot={false}
                name="Opened"
              />
              <Line
                type="monotone"
                dataKey="merged"
                stroke="#22c55e"
                strokeWidth={2}
                dot={false}
                name="Merged"
              />
              <Legend wrapperStyle={{ fontSize: 11, color: '#94a3b8' }} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Uptime by bot */}
        <div className="bg-dreamco-card rounded-xl p-5 border border-slate-700">
          <h3 className="text-sm font-semibold text-slate-300 mb-4">Bot Uptime (%)</h3>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={uptimeData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="name" stroke="#94a3b8" tick={{ fontSize: 10 }} />
              <YAxis domain={[0, 100]} stroke="#94a3b8" tick={{ fontSize: 11 }} />
              <Tooltip contentStyle={{ background: '#1e293b', border: 'none' }} />
              <Line
                type="monotone"
                dataKey="uptime"
                stroke="#f59e0b"
                strokeWidth={2}
                dot={false}
                name="Uptime %"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Status distribution pie */}
        {pieData.length > 0 && (
          <div className="bg-dreamco-card rounded-xl p-5 border border-slate-700">
            <h3 className="text-sm font-semibold text-slate-300 mb-4">Bot Status Distribution</h3>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={pieData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={70}
                  label
                >
                  {pieData.map((_, idx) => (
                    <Cell key={idx} fill={COLORS[idx % COLORS.length]} />
                  ))}
                </Pie>
                <Legend wrapperStyle={{ fontSize: 11, color: '#94a3b8' }} />
                <Tooltip contentStyle={{ background: '#1e293b', border: 'none' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    </div>
  );
}
