"""
DreamCo Dashboard

Displays live revenue, lead counts, and bot scaling status for the DreamCo
Money Operating System.  Uses Flask when available; provides a JSON-only
fallback otherwise.

Routes
------
GET /           — HTML dashboard (auto-refreshes every 30 s)
GET /api/data   — Raw JSON cycle data
GET /health     — Liveness probe
"""

from __future__ import annotations

import os
from typing import Any

from core.dreamco_orchestrator import DreamCoOrchestrator

_orch = DreamCoOrchestrator()


def _render_html(results: list, summary: dict) -> str:
    """Build a simple HTML page from cycle data."""
    rows = []
    for r in results:
        if "error" in r:
            rows.append(
                f"<tr><td>{r['bot']}</td><td colspan='4'>ERROR: {r['error']}</td></tr>"
            )
        else:
            out = r.get("output") or {}
            val = r.get("validation") or {}
            rows.append(
                f"<tr>"
                f"<td>{r['bot']}</td>"
                f"<td>${out.get('revenue', 0):.2f}</td>"
                f"<td>{out.get('leads_generated', 0)}</td>"
                f"<td>{out.get('conversion_rate', 0) * 100:.0f}%</td>"
                f"<td>{'🚀 Scaling' if val.get('scale') else val.get('status', 'N/A')}</td>"
                f"</tr>"
            )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="refresh" content="30">
  <title>DreamCo Dashboard</title>
  <style>
    body{{font-family:Arial,sans-serif;margin:2rem;background:#0d0d0d;color:#e0e0e0}}
    h1{{color:#00ff88}}
    .summary{{display:flex;gap:2rem;margin:1rem 0}}
    .card{{background:#1a1a2e;padding:1rem 2rem;border-radius:8px}}
    .card h2{{margin:0;font-size:2rem;color:#00ff88}}
    .card p{{margin:.2rem 0 0;color:#aaa}}
    table{{width:100%;border-collapse:collapse;margin-top:1rem}}
    th{{background:#1a1a2e;padding:.5rem 1rem;text-align:left}}
    td{{padding:.5rem 1rem;border-bottom:1px solid #222}}
  </style>
</head>
<body>
  <h1>🤖 DreamCo Money Operating System</h1>
  <div class="summary">
    <div class="card"><h2>${summary['total_revenue']:.2f}</h2><p>Total Revenue</p></div>
    <div class="card"><h2>{summary['total_leads']}</h2><p>Total Leads</p></div>
    <div class="card"><h2>{summary['bots_run']}</h2><p>Bots Active</p></div>
    <div class="card"><h2>{len(summary['scaling_bots'])}</h2><p>Scaling Now</p></div>
  </div>
  <table>
    <thead><tr><th>Bot</th><th>Revenue</th><th>Leads</th><th>Conv.</th><th>Status</th></tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table>
</body>
</html>"""


try:
    from flask import Flask, jsonify  # type: ignore[import]

    app = Flask(__name__)

    @app.route("/health")
    def health() -> Any:
        return jsonify({"status": "ok", "service": "dreamco-dashboard"})

    @app.route("/api/data")
    def api_data() -> Any:
        results = _orch.run_all_bots()
        summary = _orch.summary(results)
        return jsonify({"results": results, "summary": summary})

    @app.route("/")
    def dashboard() -> Any:
        from flask import make_response  # noqa: PLC0415
        results = _orch.run_all_bots()
        summary = _orch.summary(results)
        html = _render_html(results, summary)
        resp = make_response(html)
        resp.headers["Content-Type"] = "text/html"
        return resp

    FLASK_AVAILABLE = True

except ImportError:  # pragma: no cover
    app = None  # type: ignore[assignment]
    FLASK_AVAILABLE = False


def create_app(leads_path: str = None) -> Any:
    """Create and return a Flask application instance."""
    try:
        from flask import Flask, jsonify, make_response  # type: ignore[import]
        import json as _json
    except ImportError:
        return None

    _leads_path = leads_path or os.path.join("data", "leads.json")

    flask_app = Flask(__name__)

    def _load_leads():
        leads = []
        if os.path.isfile(_leads_path):
            with open(_leads_path) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            leads.append(_json.loads(line))
                        except Exception:
                            pass
        return leads

    @flask_app.route("/health")
    def health():
        return jsonify({"status": "ok", "service": "dreamco-dashboard"})

    @flask_app.route("/api/leads")
    def api_leads():
        leads = _load_leads()
        est_revenue = len(leads) * 10.0
        return jsonify({"leads": leads, "est_revenue": est_revenue})

    @flask_app.route("/")
    def dashboard():
        leads = _load_leads()
        lead_count = len(leads)
        html = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>DreamCo Empire Dashboard</title></head>
<body>
<h1>DreamCo Empire Dashboard</h1>
<p>Leads: {lead_count}</p>
<p>Est. Revenue: ${lead_count * 10.0:.2f}</p>
</body>
</html>"""
        resp = make_response(html)
        resp.headers["Content-Type"] = "text/html"
        return resp

    return flask_app


class DashboardApp:
    """Programmatic dashboard interface (no Flask required).

    Parameters
    ----------
    orchestrator : DreamCoOrchestrator
        The orchestrator to fetch bot results from.
    scale_threshold : float
        Revenue threshold above which a bot is counted as a scaling event.
    """

    def __init__(
        self,
        orchestrator: Any = None,
        scale_threshold: float = 100.0,
    ) -> None:
        self._orch = orchestrator if orchestrator is not None else _orch
        self._scale_threshold = scale_threshold

    def get_view(self) -> dict:
        """Run all bots and return a dashboard view dict."""
        from datetime import datetime, timezone

        results = self._orch.run_all_bots()
        bots = []
        total_revenue = 0.0
        scaling_events = 0

        for r in results:
            if r.get("error"):
                continue
            out = r.get("output") or {}
            val = r.get("validation") or {}
            rev = float(out.get("revenue", 0))
            total_revenue += rev
            scale = val.get("scale", rev >= self._scale_threshold)
            if scale:
                scaling_events += 1
            bots.append({
                "bot_name": r.get("bot_name", r.get("bot", "unknown")),
                "revenue": rev,
                "conversion_rate": float(out.get("conversion_rate", 0)),
                "scaling": scale,
            })

        top_performers = sorted(bots, key=lambda x: x["revenue"], reverse=True)[:5]

        return {
            "bots": bots,
            "total_revenue": total_revenue,
            "top_performers": top_performers,
            "scaling_events": scaling_events,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def get_summary_stats(self) -> dict:
        """Return aggregate statistics."""
        view = self.get_view()
        return {
            "total_revenue": view["total_revenue"],
            "bots_count": len(view["bots"]),
            "scaling_events": view["scaling_events"],
            "top_performers_count": len(view["top_performers"]),
        }


def main() -> None:  # pragma: no cover
    if not FLASK_AVAILABLE:
        print("Flask not installed.  Run: pip install flask")
        return
    port = int(os.environ.get("DASHBOARD_PORT", 5001))
    app.run(debug=False, port=port)


if __name__ == "__main__":  # pragma: no cover
    main()
