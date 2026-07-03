"""Flask web interface for Super Dashboard."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from flask import Flask, Response, jsonify, request

from dashboards.super_dashboard import SuperDashboard

_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>DreamCo Super Dashboard</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 0; padding: 1rem; background: var(--bg); color: var(--fg); }
    :root { --bg: #f5f5f5; --fg: #111; --card: #fff; }
    body.dark { --bg: #121212; --fg: #ececec; --card: #1f1f1f; }
    .toolbar { display: flex; gap: 0.5rem; margin-bottom: 1rem; flex-wrap: wrap; }
    .card { background: var(--card); border-radius: 8px; padding: 1rem; margin-bottom: 1rem; }
    table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
    th, td { border-bottom: 1px solid #8884; text-align: left; padding: 0.4rem; }
    .healthy { color: #1f9d55; font-weight: bold; }
    .warning { color: #e67e22; font-weight: bold; }
    .critical { color: #c0392b; font-weight: bold; }
  </style>
</head>
<body>
  <h1>DreamCo Super Dashboard</h1>
  <div class="toolbar">
    <button onclick="toggleTheme()">Toggle Dark/Light</button>
    <select id="categoryFilter" onchange="refresh()"><option value="">All categories</option></select>
    <select id="statusFilter" onchange="refresh()"><option value="">All status</option><option>healthy</option><option>warning</option><option>critical</option></select>
    <button onclick="window.open('/api/export/json')">Export JSON</button>
    <button onclick="window.open('/api/export/csv')">Export CSV</button>
    <button onclick="window.open('/api/export/html')">Export HTML</button>
  </div>
  <div class="card" id="summary"></div>
  <div class="card" style="overflow:auto;">
    <table>
      <thead><tr><th onclick="sortBy('id')">ID</th><th onclick="sortBy('category')">Category</th><th>Name</th><th>Division</th><th>Bot</th><th onclick="sortBy('value')">Value</th><th>Status</th><th>Health</th></tr></thead>
      <tbody id="rows"></tbody>
    </table>
  </div>
<script>
let sortField = 'id';
let sortOrder = 'asc';

function toggleTheme(){ document.body.classList.toggle('dark'); }
function sortBy(field){ sortOrder = (sortField === field && sortOrder === 'asc') ? 'desc' : 'asc'; sortField = field; refresh(); }

async function refresh(){
  const category = document.getElementById('categoryFilter').value;
  const status = document.getElementById('statusFilter').value;
  const url = `/api/metrics?sort_by=${sortField}&order=${sortOrder}&category=${encodeURIComponent(category)}&status=${encodeURIComponent(status)}`;
  const payload = await (await fetch(url)).json();

  const cats = document.getElementById('categoryFilter');
  if (cats.options.length === 1) {
    payload.available_categories.forEach(c => {
      const op = document.createElement('option');
      op.value = c; op.textContent = c;
      cats.appendChild(op);
    });
  }

  document.getElementById('summary').innerHTML = `
    <strong>Updated:</strong> ${payload.timestamp}<br/>
    <strong>Total checks:</strong> ${payload.summary.total_checks} |
    <strong>Overall health:</strong> ${payload.summary.overall_health_score}
  `;

  const rows = document.getElementById('rows');
  rows.innerHTML = payload.metrics.map(m =>
    `<tr><td>${m.id}</td><td>${m.category}</td><td>${m.name}</td><td>${m.division || '-'}</td><td>${m.bot || '-'}</td><td>${m.value}</td><td class="${m.status}">${m.status}</td><td>${m.health_score}</td></tr>`
  ).join('');
}

refresh();
setInterval(refresh, 10000);
</script>
</body>
</html>
"""


def create_app(engine: SuperDashboard | None = None) -> Flask:
    app = Flask(__name__)
    dashboard = engine or SuperDashboard()

    @app.route("/")
    def index() -> Response:
        return Response(_HTML, mimetype="text/html")

    @app.route("/api/metrics")
    def api_metrics() -> Any:
        snapshot = dashboard.build_snapshot()
        metrics = snapshot["metrics"]

        category = (request.args.get("category") or "").strip()
        status = (request.args.get("status") or "").strip()
        division = (request.args.get("division") or "").strip()
        sort_by = request.args.get("sort_by", "id")
        order = request.args.get("order", "asc")

        if category:
            metrics = [m for m in metrics if m["category"] == category]
        if status:
            metrics = [m for m in metrics if m["status"] == status]
        if division:
            metrics = [m for m in metrics if m.get("division") == division]

        reverse = order == "desc"
        metrics = sorted(metrics, key=lambda m: m.get(sort_by, ""), reverse=reverse)

        return jsonify(
            {
                "timestamp": snapshot["timestamp"],
                "summary": {**snapshot["summary"], "total_checks": len(metrics)},
                "metrics": metrics,
                "available_categories": sorted({m["category"] for m in snapshot["metrics"]}),
            }
        )

    @app.route("/api/health-scores")
    def api_health_scores() -> Any:
        snapshot = dashboard.latest_snapshot()
        return jsonify(
            {
                "timestamp": snapshot["timestamp"],
                "division_scores": snapshot["division_scores"],
                "bot_scores": snapshot["bot_scores"],
            }
        )

    @app.route("/api/trends")
    def api_trends() -> Any:
        days = request.args.get("days", 30, type=int)
        return jsonify({"days": days, "trend": dashboard.get_historical_trend(days=days)})

    @app.route("/api/compare")
    def api_compare() -> Any:
        return jsonify(dashboard.comparative_analysis())

    @app.route("/api/export/<fmt>")
    def api_export(fmt: str) -> Response:
        fmt = fmt.lower().strip()
        if fmt == "json":
            return Response(dashboard.export_json(), mimetype="application/json")
        if fmt == "csv":
            return Response(
                dashboard.export_csv(),
                mimetype="text/csv",
                headers={"Content-Disposition": "attachment; filename=super_dashboard.csv"},
            )
        if fmt == "html":
            return Response(dashboard.export_html_report(), mimetype="text/html")
        return Response(
            json.dumps({"error": "Unsupported export format."}),
            mimetype="application/json",
            status=400,
        )

    @app.route("/api/heartbeat")
    def api_heartbeat() -> Any:
        return jsonify(
            {
                "status": "ok",
                "service": "super_dashboard_web",
                "refresh_interval_seconds": dashboard.refresh_interval_seconds,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    return app


if __name__ == "__main__":  # pragma: no cover
    create_app().run(host="0.0.0.0", port=5080, debug=True)
