"""Expand Buddy's compact web curriculum into explicit learning targets.

The source registry intentionally stores source families + learning tracks instead
of inventing hundreds of questionable URLs. This generator creates one explicit
record per source-family/track pair, preserving the expected gain for every target.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "buddy-web-learning-curriculum-1000.json"
OUTPUT = ROOT / "data" / "buddy_web_learning_targets.json"


def main() -> None:
    curriculum = json.loads(CONFIG.read_text(encoding="utf-8"))
    records = []
    number = 1
    for source in curriculum["source_families"]:
        for track in curriculum["learning_tracks"]:
            records.append(
                {
                    "target_id": f"T{number:04d}",
                    "source_family": source["id"],
                    "source_url": source["url"],
                    "learning_track": track,
                    "expected_gain": (
                        f"Buddy learns {track.replace('_', ' ')} using "
                        f"{source['gain']} while preserving provenance and uncertainty."
                    ),
                    "provenance_required": True,
                    "cross_source_validation_required": True,
                    "sandbox_before_durable_learning": True,
                    "evaluation_required": True,
                    "promotion_status": "candidate",
                }
            )
            number += 1

    # 50 source families x 18 tracks = 900 explicit targets.
    assert len(records) == 900, len(records)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps({
        "schema": "dreamco.buddy_web_learning_targets.v1",
        "target_count": len(records),
        "targets": records,
    }, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {len(records)} explicit web-learning targets: {OUTPUT}")


if __name__ == "__main__":
    main()
