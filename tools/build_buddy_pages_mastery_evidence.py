#!/usr/bin/env python3
"""Build public-safe Buddy mastery evidence from repository artifacts.

Fail closed: no external execution or self-reported mastery. No secrets.
"""
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports/BUDDY_BENCHMARK_INDEX.md"
OUT = ROOT / "website/data/buddy-mastery-evidence.json"
FIELDS = {"benchmark_programs": "Benchmark programs",
          "repository_suites": "Repository suites",
          "tracked_surfaces": "Tracked benchmark surfaces",
          "live_programs_with_evidence": "Live benchmark programs with evidence"}

def build():
    content = REPORT.read_text(encoding="utf-8") if REPORT.is_file() else ""
    counts = {}
    for key, label in FIELDS.items():
        match = re.search(r"^-\s*" + re.escape(label) + r":\s*(\d+)\s*$", content, re.M)
        counts[key] = int(match.group(1)) if match else None
    programs = []
    for name, area, status in re.findall(r"^- \*\*(.+?)\*\* \((.+?)\): \x60([^\x60]+)\x60\s*$", content, re.M):
        programs.append({"name": name, "area": area, "reported_status": status,
                         "mastered": False, "verified_live": False})
    return {"schema": "dreamco.buddy_mastery_evidence.v1",
            "source": "reports/BUDDY_BENCHMARK_INDEX.md",
            "source_type": "repository_report_not_live_probe",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "counts": counts, "programs": programs,
            "coding_mastery_verified": False,
            "worldwide_code_study_verified": False,
            "external_repositories_studied": None,
            "code_files_studied": None,
            "independent_mastery_results": [],
            "limitations": [
                "Static repository report only; no GitHub Actions or external repository runs checked.",
                "Missing evidence means unknown, not necessarily that no learning occurred.",
                "A catalog, contract, plan, or local smoke test is not verified mastery.",
                "Do not expose user data, secrets, private sources or private benchmark inputs."
            ]}

def main():
    result = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)}")

if __name__ == "__main__":
    main()
