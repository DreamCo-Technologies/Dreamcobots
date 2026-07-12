"""Score supervised revenue experiments without performing external actions."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BLOCKED_ACTIONS = {
    "ad_spend",
    "contract_acceptance",
    "money_movement",
    "outreach",
    "purchase",
    "production_deploy",
}


@dataclass(frozen=True)
class Opportunity:
    opportunity_id: str
    title: str
    evidence_strength: float
    expected_value: float
    effort: float
    risk: float
    next_experiment: str
    required_actions: tuple[str, ...]

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "Opportunity":
        def bounded(name: str) -> float:
            result = float(value[name])
            if not 0 <= result <= 1:
                raise ValueError(f"{name} must be between 0 and 1")
            return result

        return cls(
            opportunity_id=str(value["id"]),
            title=str(value["title"]),
            evidence_strength=bounded("evidence_strength"),
            expected_value=bounded("expected_value"),
            effort=bounded("effort"),
            risk=bounded("risk"),
            next_experiment=str(value["next_experiment"]),
            required_actions=tuple(value.get("required_actions", ())),
        )

    @property
    def score(self) -> float:
        benefit = (self.evidence_strength * 0.45) + (self.expected_value * 0.35)
        cost = (self.effort * 0.10) + (self.risk * 0.10)
        return round(max(0.0, benefit - cost), 4)

    @property
    def requires_owner_approval(self) -> bool:
        return bool(BLOCKED_ACTIONS.intersection(self.required_actions))


def build_report(config_path: Path) -> dict[str, Any]:
    payload = json.loads(config_path.read_text())
    opportunities = [Opportunity.from_dict(item) for item in payload["opportunities"]]
    ranked = sorted(opportunities, key=lambda item: (-item.score, item.opportunity_id))
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": "research_and_draft_only",
        "external_actions_executed": False,
        "opportunities": [
            {
                **asdict(item),
                "required_actions": list(item.required_actions),
                "score": item.score,
                "requires_owner_approval": item.requires_owner_approval,
                "status": "awaiting_owner_approval"
                if item.requires_owner_approval
                else "safe_experiment_ready",
            }
            for item in ranked
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("config/opportunity_experiments.json"))
    parser.add_argument("--output", type=Path, default=Path("reports/opportunity_queue.json"))
    args = parser.parse_args()
    report = build_report(args.config)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(f"Ranked {len(report['opportunities'])} supervised opportunities")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
