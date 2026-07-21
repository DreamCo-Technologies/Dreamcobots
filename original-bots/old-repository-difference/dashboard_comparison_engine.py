from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dashboard_feature_extractor import extract_features
from dashboard_inventory_builder import INVENTORY_DIR, build_inventory


REPO_ROOT = Path(__file__).resolve().parent


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _clamp(value: float, minimum: int = 0, maximum: int = 100) -> int:
    return int(max(minimum, min(maximum, round(value))))


def _score_dashboard(row: dict[str, Any]) -> dict[str, Any]:
    frontend = row.get("frontend", {})
    backend = row.get("backend", {})
    security_findings = row.get("security_findings", [])
    duplicates = row.get("duplicate_mappings", [])
    deployment = str(row.get("deployment_readiness", "unknown")).lower()

    operations = _clamp(
        frontend.get("button_count", 0) * 1.5
        + frontend.get("action_count", 0) * 1.8
        + len(frontend.get("rest_endpoints", [])) * 3
        + (15 if backend.get("queue_integrations") else 0)
        + (12 if backend.get("command_control_apis", 0) else 0)
    )
    governance = _clamp(
        (20 if row.get("feature_groups", {}).get("governance") else 0)
        + (18 if frontend.get("auth_session_signals") else 0)
        + (20 if backend.get("orchestrator_bindings") else 0)
        + (18 if backend.get("github_actions_integrations") else 0)
    )
    automation = _clamp(
        (25 if backend.get("queue_integrations") else 0)
        + (25 if backend.get("orchestrator_bindings") else 0)
        + (25 if backend.get("github_actions_integrations") else 0)
        + min(25, len(frontend.get("rest_endpoints", [])) * 2)
    )
    revenue = _clamp(
        (30 if row.get("feature_groups", {}).get("monetization") else 0)
        + min(30, frontend.get("telemetry_widgets", 0) * 5)
        + (20 if row.get("feature_groups", {}).get("growth_analytics") else 0)
    )
    security = 100
    maintainability = 100

    penalties: dict[str, int] = {}
    if "hardcoded_secret_like_value" in security_findings or frontend.get("embedded_secrets_tokens"):
        penalties["hardcoded_secrets"] = 30
    if duplicates:
        penalties["duplicate_functionality"] = 15
    if deployment in {"unknown", "experimental"}:
        penalties["stale_dependencies_or_low_readiness"] = 10
    if not frontend.get("rest_endpoints"):
        penalties["broken_or_missing_endpoints"] = 8
    if row.get("feature_groups", {}).get("operations") and not row.get("feature_groups", {}).get("governance"):
        penalties["non_governed_runtime_coupling"] = 12

    total_penalty = sum(penalties.values())
    security = _clamp(security - total_penalty)
    maintainability = _clamp(maintainability - (total_penalty * 0.7) - frontend.get("action_count", 0) * 0.5)
    overall = _clamp((operations + governance + automation + revenue + security + maintainability) / 6)

    return {
        "id": row["id"],
        "path": row["path"],
        "scores": {
            "operations": operations,
            "governance": governance,
            "automation": automation,
            "revenue": revenue,
            "security": security,
            "maintainability": maintainability,
            "overall": overall,
        },
        "penalties": penalties,
        "deployment_readiness": row.get("deployment_readiness", "unknown"),
        "duplicate_mappings": duplicates,
    }


def _build_html_report(rankings: list[dict[str, Any]]) -> str:
    rows = []
    for idx, row in enumerate(rankings, start=1):
        s = row["scores"]
        rows.append(
            "<tr>"
            f"<td>{idx}</td>"
            f"<td>{row['id']}</td>"
            f"<td>{s['overall']}</td>"
            f"<td>{s['operations']}</td>"
            f"<td>{s['governance']}</td>"
            f"<td>{s['automation']}</td>"
            f"<td>{s['revenue']}</td>"
            f"<td>{s['security']}</td>"
            f"<td>{s['maintainability']}</td>"
            f"<td>{', '.join(row.get('penalties', {}).keys()) or 'none'}</td>"
            "</tr>"
        )
    table = "".join(rows)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Dashboard Comparison Report</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; background: #0f172a; color: #e2e8f0; }}
    table {{ border-collapse: collapse; width: 100%; background: #111827; }}
    th, td {{ border: 1px solid #374151; padding: 8px; font-size: 12px; text-align: left; }}
    th {{ background: #1f2937; }}
    h1 {{ margin-bottom: 16px; }}
  </style>
</head>
<body>
  <h1>Dashboard Governance Comparison</h1>
  <table>
    <thead>
      <tr>
        <th>#</th><th>Dashboard</th><th>Overall</th><th>Operations</th><th>Governance</th>
        <th>Automation</th><th>Revenue</th><th>Security</th><th>Maintainability</th><th>Penalties</th>
      </tr>
    </thead>
    <tbody>{table}</tbody>
  </table>
</body>
</html>
"""


def run_comparison() -> dict[str, Any]:
    build_inventory()
    extract_features()

    matrix = _read_json(INVENTORY_DIR / "dashboard_feature_matrix.json")
    dead_report = _read_json(INVENTORY_DIR / "dead_dashboards.json")
    security = _read_json(INVENTORY_DIR / "dashboard_security_findings.json")
    migration_candidates = _read_json(INVENTORY_DIR / "migration_candidates.json")

    dashboards = matrix.get("dashboards", [])
    scored = [_score_dashboard(row) for row in dashboards]
    rankings = sorted(scored, key=lambda x: x["scores"]["overall"], reverse=True)

    feature_matrix_output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dashboard_count": matrix.get("dashboard_count", len(dashboards)),
        "endpoint_coverage": matrix.get("endpoint_coverage", {}),
        "button_action_density": [
            {
                "id": row["id"],
                "path": row["path"],
                "buttons": row.get("frontend", {}).get("button_count", 0),
                "actions": row.get("frontend", {}).get("action_count", 0),
            }
            for row in dashboards
        ],
        "governance_readiness": [
            {
                "id": row["id"],
                "readiness": bool(row.get("feature_groups", {}).get("governance")),
                "deployment_readiness": row.get("deployment_readiness", "unknown"),
            }
            for row in dashboards
        ],
        "dashboards": dashboards,
    }
    rankings_output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "rankings": rankings,
        "shortlist": rankings[:10],
    }
    dead_code_output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dead_dashboards": dead_report.get("dead_dashboards", []),
        "unused_api_candidates": [
            row["id"] for row in dashboards if not row.get("frontend", {}).get("rest_endpoints")
        ],
    }

    migration_plan = [
        "# Dashboard Migration Plan",
        "",
        "## Recommended shortlist",
    ]
    for item in rankings[:10]:
        migration_plan.append(f"- {item['id']} (overall score: {item['scores']['overall']})")
    migration_plan.extend(
        [
            "",
            "## Migration candidate inputs",
            f"- Candidates discovered: {len(migration_candidates.get('candidates', []))}",
            f"- Dead dashboards: {len(dead_code_output['dead_dashboards'])}",
            "",
            "## Consolidation direction",
            "- Keep one governed dashboard framework with modular capability panels.",
            "- Prioritize dashboards with high governance + automation + security scores.",
            "- Deprioritize duplicated dashboards with penalties.",
        ]
    )

    (REPO_ROOT / "dashboard-feature-matrix.json").write_text(
        json.dumps(feature_matrix_output, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (REPO_ROOT / "dashboard-rankings.json").write_text(
        json.dumps(rankings_output, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (REPO_ROOT / "dashboard-security-findings.json").write_text(
        json.dumps(security, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (REPO_ROOT / "dashboard-dead-code-report.json").write_text(
        json.dumps(dead_code_output, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (REPO_ROOT / "dashboard-comparison-report.html").write_text(
        _build_html_report(rankings),
        encoding="utf-8",
    )
    (REPO_ROOT / "dashboard-migration-plan.md").write_text("\n".join(migration_plan) + "\n", encoding="utf-8")

    return {
        "ranked_dashboards": len(rankings),
        "top_dashboard": rankings[0]["id"] if rankings else None,
    }


def main() -> None:
    result = run_comparison()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
