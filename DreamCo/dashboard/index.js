'use strict';

/**
 * DreamCo Dashboard
 *
 * Simple HTTP dashboard that displays live bot revenue, leads, and
 * scaling status for the DreamCo Money Operating System.
 */

const http = require('http');
const { runAllBots } = require('../orchestrator/index');

const PORT = process.env.DASHBOARD_PORT || 5001;

/**
 * Render a simple HTML page showing the latest bot cycle results.
 * @param {Object} cycleData - Results from runAllBots()
 * @returns {string} HTML string
 */
function renderDashboard(cycleData) {
  const { summary, results } = cycleData;
  const rows = results
    .map((r) => {
      if (!r.output) {
        return `<tr><td>${r.bot}</td><td colspan="4">ERROR: ${r.error}</td></tr>`;
      }
      return `<tr>
        <td>${r.bot}</td>
        <td>$${r.output.revenue}</td>
        <td>${r.output.leads_generated}</td>
        <td>${(r.output.conversion_rate * 100).toFixed(0)}%</td>
        <td>${r.validation.scale ? '🚀 Scaling' : r.validation.status}</td>
      </tr>`;
    })
    .join('\n');

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="refresh" content="30">
  <title>DreamCo Dashboard</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 2rem; background: #0d0d0d; color: #e0e0e0; }
    h1 { color: #00ff88; }
    .summary { display: flex; gap: 2rem; margin: 1rem 0; }
    .card { background: #1a1a2e; padding: 1rem 2rem; border-radius: 8px; }
    .card h2 { margin: 0; font-size: 2rem; color: #00ff88; }
    .card p { margin: 0.2rem 0 0; color: #aaa; }
    table { width: 100%; border-collapse: collapse; margin-top: 1rem; }
    th { background: #1a1a2e; padding: 0.5rem 1rem; text-align: left; }
    td { padding: 0.5rem 1rem; border-bottom: 1px solid #222; }
  </style>
</head>
<body>
  <h1>🤖 DreamCo Money Operating System</h1>
  <div class="summary">
    <div class="card"><h2>$${summary.total_revenue}</h2><p>Total Revenue</p></div>
    <div class="card"><h2>${summary.total_leads}</h2><p>Total Leads</p></div>
    <div class="card"><h2>${summary.bots_run}</h2><p>Bots Active</p></div>
    <div class="card"><h2>${summary.scaling_bots.length}</h2><p>Scaling Now</p></div>
  </div>
  <table>
    <thead><tr><th>Bot</th><th>Revenue</th><th>Leads</th><th>Conv. Rate</th><th>Status</th></tr></thead>
    <tbody>${rows}</tbody>
  </table>
  <p style="color:#555; margin-top:1rem">Last updated: ${summary.timestamp}</p>
</body>
</html>`;
}

/**
 * Start the dashboard HTTP server.
 * @param {number} [port] - Port to listen on (default: DASHBOARD_PORT env or 5001)
 * @returns {http.Server}
 */
function startServer(port = PORT) {
  const server = http.createServer((req, res) => {
    if (req.url === '/health') {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      return res.end(JSON.stringify({ status: 'ok', service: 'dreamco-dashboard' }));
    }

    const data = runAllBots();
    if (req.url === '/api/data') {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      return res.end(JSON.stringify(data));
    }

    res.writeHead(200, { 'Content-Type': 'text/html' });
    res.end(renderDashboard(data));
  });

  server.listen(port, () => {
    console.log(`🌐 DreamCo Dashboard running at http://localhost:${port}`);
  });

  return server;
}

module.exports = { startServer, renderDashboard };

if (require.main === module) {
  startServer();
}
