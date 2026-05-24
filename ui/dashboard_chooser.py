from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent
INVENTORY_DIR = REPO_ROOT / "dashboard_inventory"


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _to_bool(value: str | None) -> bool | None:
    if value is None:
        return None
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    return None


def load_dashboard_entries(catalog: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    rankings = _load_json(REPO_ROOT / "dashboard-rankings.json").get("rankings", [])
    matrix_dashboards = _load_json(REPO_ROOT / "dashboard-feature-matrix.json").get("dashboards", [])
    migration_ids = {x["id"] for x in _load_json(INVENTORY_DIR / "migration_candidates.json").get("candidates", [])}
    matrix_index = {row["id"]: row for row in matrix_dashboards}

    entries = []
    for rank in rankings:
        row = matrix_index.get(rank["id"], {})
        entries.append(
            {
                "id": rank["id"],
                "path": rank["path"],
                "category": "governance" if row.get("feature_groups", {}).get("governance") else "operations",
                "capabilities": sorted(
                    cap
                    for cap, enabled in row.get("feature_groups", {}).items()
                    if enabled
                ),
                "overall_score": rank.get("scores", {}).get("overall", 0),
                "production_ready": str(rank.get("deployment_readiness", "")).lower() in {"production", "ready", "high"},
                "governance_compatible": bool(row.get("feature_groups", {}).get("governance")),
                "migration_candidate": rank["id"] in migration_ids,
            }
        )

    if entries:
        return entries

    fallback = []
    for item in catalog or []:
        fallback.append(
            {
                "id": item.get("name", "unknown"),
                "path": item.get("name", "unknown"),
                "category": item.get("category", "operations"),
                "capabilities": ["operations"],
                "overall_score": 0,
                "production_ready": False,
                "governance_compatible": False,
                "migration_candidate": False,
            }
        )
    return fallback


def filter_entries(
    entries: list[dict[str, Any]],
    categories: set[str] | None = None,
    production_ready: bool | None = None,
    governance_compatible: bool | None = None,
    migration_candidate: bool | None = None,
) -> list[dict[str, Any]]:
    filtered = []
    for entry in entries:
        if categories and entry["category"] not in categories:
            continue
        if production_ready is not None and entry["production_ready"] != production_ready:
            continue
        if governance_compatible is not None and entry["governance_compatible"] != governance_compatible:
            continue
        if migration_candidate is not None and entry["migration_candidate"] != migration_candidate:
            continue
        filtered.append(entry)
    return filtered


def render_dashboard_chooser_html(
    entries: list[dict[str, Any]],
    categories: set[str] | None = None,
    production_ready: bool | None = None,
    governance_compatible: bool | None = None,
    migration_candidate: bool | None = None,
) -> str:
    filtered = filter_entries(
        entries=entries,
        categories=categories,
        production_ready=production_ready,
        governance_compatible=governance_compatible,
        migration_candidate=migration_candidate,
    )
    rows = []
    for entry in filtered:
        rows.append(
            "<tr>"
            f"<td>{html.escape(entry['id'])}</td>"
            f"<td>{html.escape(entry['category'])}</td>"
            f"<td>{entry['overall_score']}</td>"
            f"<td>{'✅' if entry['production_ready'] else '—'}</td>"
            f"<td>{'✅' if entry['governance_compatible'] else '—'}</td>"
            f"<td>{'✅' if entry['migration_candidate'] else '—'}</td>"
            f"<td>{html.escape(', '.join(entry['capabilities']) or '—')}</td>"
            f"<td>{html.escape(entry['path'])}</td>"
            "</tr>"
        )
    rows_html = "".join(rows) or "<tr><td colspan='8'>No dashboards match the selected filters.</td></tr>"
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Dashboard Chooser</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; background: #0f172a; color: #e2e8f0; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 12px; background: #111827; }}
    th, td {{ border: 1px solid #374151; padding: 8px; font-size: 12px; text-align: left; }}
    th {{ background: #1f2937; }}
    .meta {{ font-size: 12px; color: #94a3b8; margin: 8px 0; }}
  </style>
</head>
<body>
  <h1>Dashboard Chooser</h1>
  <div class="meta">Compare dashboards by category, governance readiness, production readiness, and migration candidacy.</div>
  <table>
    <thead>
      <tr>
        <th>Dashboard</th><th>Category</th><th>Score</th><th>Prod Ready</th><th>Governance</th><th>Migration</th><th>Capabilities</th><th>Source</th>
      </tr>
    </thead>
    <tbody>{rows_html}</tbody>
  </table>
</body>
</html>
"""


def parse_filter_args(args: Any) -> dict[str, Any]:
    category_raw = args.get("category", "") if hasattr(args, "get") else ""
    categories = {
        c.strip().lower()
        for c in str(category_raw).split(",")
        if c.strip()
    }
    return {
        "categories": categories or None,
        "production_ready": _to_bool(args.get("production_ready")) if hasattr(args, "get") else None,
        "governance_compatible": _to_bool(args.get("governance_compatible")) if hasattr(args, "get") else None,
        "migration_candidate": _to_bool(args.get("migration_candidate")) if hasattr(args, "get") else None,
    }
