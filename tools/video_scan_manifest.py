"""Create an AI-readable manifest from the fast video inventory.

This stage does not claim semantic understanding. It creates stable records that
later authorized speech/vision/embedding workers can enrich.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def build(input_path: Path, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with input_path.open() as src, output_path.open("w") as dst:
        for line in src:
            if not line.strip():
                continue
            row = json.loads(line)
            record = {
                "schema": "dreamco.video.knowledge_seed.v1",
                "video_id": row.get("content_hash_prefix"),
                "source": row.get("path"),
                "provenance": {"inventory": str(input_path)},
                "evidence": [],
                "confidence": "unknown",
                "claims": [],
                "timestamps": [],
                "next_workers": [
                    "scene_detection",
                    "speech_transcription",
                    "ocr",
                    "visual_event_detection",
                    "embedding_indexing",
                ],
                "status": "awaiting_semantic_analysis",
            }
            dst.write(json.dumps(record, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("input", type=Path)
    p.add_argument("--output", type=Path, default=Path("artifacts/video_knowledge_seed.jsonl"))
    args = p.parse_args()
    build(args.input, args.output)
