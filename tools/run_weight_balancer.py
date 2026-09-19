#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from foundry.weight_balancer import simulate

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "config" / "generated" / "weight-balance-report.json"
REPORT = ROOT / "reports" / "WEIGHT_BALANCING.md"


def main() -> int:
    result = simulate()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    bal = result["balance"]
    REPORT.write_text(
        "\n".join(
            [
                "# Weight Balancing",
                "",
                f"- Experts: **{bal['experts']}**",
                f"- Tokens: **{bal['tokens']}**",
                f"- Load CV: **{bal['load_cv']:.3f}**",
                f"- Overflow: **{bal['overflow']}**",
                f"- Balanced: **{bal['balanced']}**",
                f"- US route share: **{result['route_mix']['us_share']:.3f}**",
                "",
                result["truth"],
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(json.dumps({"ok": bal["balanced"], "load_cv": bal["load_cv"], "us_share": result["route_mix"]["us_share"]}))
    return 0 if bal["balanced"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
