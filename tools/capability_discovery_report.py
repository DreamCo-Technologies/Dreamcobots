"""Repository capability-discovery report.

This first-pass scanner creates an inventory from filenames and text without
pretending that discovery equals mastery. Future versions can connect directly
to the canonical registry and benchmark evidence store.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(".")
OUTPUT = ROOT / "artifacts" / "capability_discovery_report.json"
SKIP = {".git", "node_modules", ".venv", "venv", "dist", "build", "__pycache__"}
DOMAIN_KEYWORDS = {
    "coding": ["code", "coding", "developer", "programming", "software", "library", "debug"],
    "benchmarking": ["benchmark", "eval", "evaluation", "score", "test"],
    "media": ["audio", "video", "image", "music", "movie", "film", "voice"],
    "games": ["game", "gaming", "npc", "level", "unity", "unreal"],
    "agents": ["agent", "bot", "orchestrator", "workflow"],
    "learning": ["learn", "training", "curriculum", "bootcamp", "mastery"],
}


def classify(text: str) -> list[str]:
    lowered = text.lower()
    return sorted({domain for domain, words in DOMAIN_KEYWORDS.items() if any(re.search(rf"\\b{re.escape(w)}\\b", lowered) for w in words)})


def main() -> None:
    records = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in SKIP for part in path.parts):
            continue
        try:
            sample = path.read_text(encoding="utf-8", errors="ignore")[:20000]
        except OSError:
            continue
        text = f"{path} {sample}"
        domains = classify(text)
        if domains:
            records.append({
                "source": str(path),
                "domains": domains,
                "discovery_confidence_percent": 50,
                "mastery_percent": None,
                "benchmark_percent": None,
                "status": "discovered_needs_validation",
            })
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps({
        "schema": "dreamco.capability_discovery_report.v1",
        "warning": "Discovery is not evidence of implementation or mastery.",
        "record_count": len(records),
        "records": records,
    }, indent=2), encoding="utf-8")
    print(f"Wrote {len(records)} discovered capability-related records to {OUTPUT}")


if __name__ == "__main__":
    main()
