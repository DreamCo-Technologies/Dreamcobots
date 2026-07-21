"""Extended compliance checker for DreamCo bot framework expectations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "compliance_report.json"


class ExtendedComplianceChecker:
    """Validate framework, metadata, pricing, and health endpoint compliance."""

    def _has_health_endpoint(self, bot_dir: Path) -> bool:
        for path in bot_dir.glob("*.py"):
            if "/health" in path.read_text(errors="ignore"):
                return True
        return False

    def _check_bot(self, bot_dir: Path) -> dict[str, Any]:
        profile = bot_dir / "bot_profile.json"
        tiers = bot_dir / "tiers.py"
        init_file = bot_dir / "__init__.py"
        report = {"bot": bot_dir.name, "checks": {}, "passed": True}
        report["checks"]["bot_profile.json"] = profile.exists()
        report["checks"]["tiers.py"] = tiers.exists()
        report["checks"]["__init__.py"] = init_file.exists()
        report["checks"]["health_endpoint"] = self._has_health_endpoint(bot_dir)
        import_ok = False
        for path in bot_dir.glob("*.py"):
            if "GlobalAISourcesFlow" in path.read_text(errors="ignore"):
                import_ok = True
                break
        report["checks"]["GlobalAISourcesFlow_import"] = import_ok
        if profile.exists():
            data = json.loads(profile.read_text())
            required = ["slug", "displayName", "description", "tier", "capabilities"]
            report["checks"]["profile_schema_complete"] = all(key in data for key in required)
            if tiers.exists():
                report["checks"]["pricing_consistency"] = str(data.get("priceRange", "")).strip() != ""
            else:
                report["checks"]["pricing_consistency"] = False
        else:
            report["checks"]["profile_schema_complete"] = False
            report["checks"]["pricing_consistency"] = False
        report["passed"] = all(report["checks"].values())
        return report

    def run(self) -> dict[str, Any]:
        results = [self._check_bot(bot_dir) for bot_dir in sorted((ROOT / "bots").iterdir()) if bot_dir.is_dir()]
        payload = {"bots": results, "passed": sum(1 for item in results if item["passed"]), "failed": sum(1 for item in results if not item["passed"])}
        REPORT.write_text(json.dumps(payload, indent=2) + "\n")
        return payload


def main() -> None:
    print(json.dumps(ExtendedComplianceChecker().run(), indent=2))


if __name__ == "__main__":
    main()
