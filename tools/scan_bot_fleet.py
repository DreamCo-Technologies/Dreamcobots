#!/usr/bin/env python3
"""Scan bots/, App_bots/, and original-bots/ and write inventory + worklist."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def list_files(rel: str, suffixes: tuple[str, ...]) -> list[str]:
    base = ROOT / rel
    if not base.exists():
        return []
    out = []
    for p in sorted(base.rglob("*")):
        if p.is_file() and p.suffix.lower() in suffixes:
            out.append(str(p.relative_to(ROOT)))
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="reports/BOT_FLEET_SCAN.json")
    parser.add_argument("--md", default="reports/BOT_FLEET_SCAN.md")
    parser.add_argument("--worklist", default="")
    args = parser.parse_args()

    scan = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "bots_specs": list_files("bots", (".md", ".json", ".txt", ".py", ".ts")),
        "app_bots_divisions": list_files("App_bots", (".json",)),
        "original_bots": list_files("original-bots", (".md", ".json", ".py", ".ts", ".js")),
        "systems": list_files("systems", (".json", ".py", ".md")),
    }
    scan["counts"] = {k: len(v) for k, v in scan.items() if isinstance(v, list)}

    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(scan, indent=2) + "\n", encoding="utf-8")

    md = ROOT / args.md
    lines = [
        "# Bot Fleet Scan",
        "",
        f"Generated: {scan['generated_at']}",
        "",
        f"- bots/ specs: **{scan['counts'].get('bots_specs', 0)}**",
        f"- App_bots divisions: **{scan['counts'].get('app_bots_divisions', 0)}**",
        f"- original-bots files: **{scan['counts'].get('original_bots', 0)}**",
        f"- systems packages: **{scan['counts'].get('systems', 0)}**",
        "",
        "A catalog file is not proof of a live runtime. Promote only with tests.",
        "",
        "## App_bots divisions",
        "",
    ]
    for item in scan["app_bots_divisions"]:
        lines.append(f"- `{item}`")
    lines += ["", "## bots/ specs", ""]
    for item in scan["bots_specs"]:
        lines.append(f"- `{item}`")
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    if args.worklist:
        work = ROOT / args.worklist
        work.parent.mkdir(parents=True, exist_ok=True)
        work.write_text(
            "\n".join(
                [
                    "# Autonomous Worklist",
                    "",
                    f"Generated: {scan['generated_at']}",
                    "",
                    "## Always-on Actions jobs",
                    "- Autonomous Systems Builder (this workflow)",
                    "- Run Everything Now",
                    "- Self Working System",
                    "- Actions Page Gate + Actions Health",
                    "- Buddy Fleet Health + Buddy Actions Test Lab",
                    "",
                    "## Build next",
                    "1. Refresh systems/ packages from App_bots JSON",
                    "2. Mark each bots/*.md as stub vs tested runtime",
                    "3. Promote original-bots winners into Buddy fleet",
                    "4. Keep money/outreach behind permission gates",
                    "5. Do not green CI by deleting tests",
                    "",
                    "## Counts",
                    json.dumps(scan["counts"], indent=2),
                    "",
                ]
            ),
            encoding="utf-8",
        )
    print(json.dumps(scan["counts"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
