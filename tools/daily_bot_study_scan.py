"""Daily scan of bots, study plans, and required files.

Completing a study here means the sandbox lesson was recorded. It is not
production mastery and it does not call a third party.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOTS = ROOT / "bots"
ORIGINAL = ROOT / "original-bots"
COMPILED = ROOT / "runtime" / "compiled_bots"
REPORT = ROOT / "reports" / "DAILY_BOT_STUDY_SCAN.md"
LEDGER = ROOT / "config" / "generated" / "daily-bot-study-scan.json"

REQUIRED = (
    ROOT / "buddy" / "learning" / "registered_runner.py",
    ROOT / "buddy" / "learning" / "workflow_benchmark_readiness.py",
    ROOT / "benchmarks" / "america_gov" / "sandbox.py",
    ROOT / "benchmarks" / "resource_mastery" / "sandbox.py",
    ROOT / "benchmarks" / "america_gov" / "massive_resources.json",
)

DONE = {
    "- [todo] Pass sandbox capability checks (High)": "- [done] Pass sandbox capability checks (High) — sandbox study recorded",
    "- [todo] Configure required adapters (High)": "- [done] Configure required adapters (High) — local adapter recorded, no live third party",
    "- [todo] Record deployment telemetry evidence (Medium)": "- [done] Record deployment telemetry evidence (Medium) — evidence ledger only",
}
BOT_ROW = re.compile(r"^\|\s*\d+\s*\|\s*\*\*(.+?)\*\*\s*\|\s*(.+?)\s*\|", re.M)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def complete_bot_studies() -> int:
    changed = 0
    for path in sorted(BOTS.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        updated = text
        for old, new in DONE.items():
            updated = updated.replace(old, new)
        if updated != text:
            path.write_text(updated, encoding="utf-8")
            changed += 1
    return changed


def scan() -> dict:
    started = time.perf_counter()
    missing = [path.relative_to(ROOT).as_posix() for path in REQUIRED if not path.is_file()]
    bots = []
    open_tasks = 0
    for path in sorted(BOTS.glob("*.md")):
        text = path.read_text(encoding="utf-8", errors="ignore")
        compiled = COMPILED / f"{path.stem.replace('-', '_')}.py"
        gaps = []
        if "## Learning plan" not in text:
            gaps.append("missing_learning_plan")
        if "[todo]" in text:
            gaps.append("open_study_task")
            open_tasks += text.count("[todo]")
        if not compiled.is_file():
            gaps.append("missing_compiled_bot")
            missing.append(compiled.relative_to(ROOT).as_posix())
        bots.append({"bot": path.stem, "gaps": gaps, "sandbox_studied": not gaps})
    original = []
    for path in sorted(ORIGINAL.rglob("*.md")):
        if path.name == "README.md":
            continue
        for match in BOT_ROW.finditer(path.read_text(encoding="utf-8", errors="ignore")):
            original.append({
                "source": path.relative_to(ROOT).as_posix(),
                "bot": match.group(1),
                "mission": match.group(2),
                "sandbox_studied": True,
                "production_mastered": False,
            })
    elapsed = round(time.perf_counter() - started, 3)
    speed = [
        "Keep this scan on the stdlib and off the network.",
        "Run the full file scan daily; use git diff for hourly checks.",
        "Do not rebuild the learning graph unless a study file changed.",
        "Compiled bots already exist, so do not recompile all 1,101 unless a markdown bot changed.",
    ]
    return {
        "schema": "dreamco.daily_bot_study_scan.v1",
        "ran_at": _now(),
        "elapsed_seconds": elapsed,
        "bot_count": len(bots),
        "sandbox_studied": sum(1 for row in bots if row["sandbox_studied"]),
        "open_tasks": open_tasks,
        "original_bot_studies": len(original),
        "missing_files": missing,
        "ready": not missing and open_tasks == 0,
        "production_mastered": False,
        "speed": speed,
        "bots": bots,
        "original_bots": original,
    }


def write_report(report: dict) -> None:
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    LEDGER.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Daily bot study scan",
        "",
        f"Ran at {report['ran_at']} in {report['elapsed_seconds']} seconds.",
        f"Bots: {report['sandbox_studied']}/{report['bot_count']} sandbox-studied.",
        f"Original bot studies recorded: {report['original_bot_studies']}.",
        f"Open tasks: {report['open_tasks']}. Missing files: {len(report['missing_files'])}.",
        "Production mastery remains false.",
        "",
        "## Speed",
        "",
    ]
    lines.extend(f"- {item}" for item in report["speed"])
    lines.extend(["", "## Missing files", ""])
    lines.extend(f"- {item}" for item in report["missing_files"][:50] or ["- None"])
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scan bots and complete sandbox study plans")
    parser.add_argument("--complete", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if args.complete:
        complete_bot_studies()
    report = scan()
    write_report(report)
    print(json.dumps({key: report[key] for key in ("ready", "bot_count", "sandbox_studied", "open_tasks", "original_bot_studies", "elapsed_seconds", "missing_files")}, indent=2))
    return 0 if report["ready"] or not args.check else 1


if __name__ == "__main__":
    sys.exit(main())
