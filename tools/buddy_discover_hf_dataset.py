"""Review public Hugging Face dataset metadata at an immutable commit."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from buddy.learning.data_study import (DataStudyError, discover_huggingface_dataset,
                                       preview_huggingface_dataset)  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo_id", help="Hugging Face dataset namespace/name")
    parser.add_argument("revision", help="Branch, tag, or commit; output records the resolved full commit SHA")
    parser.add_argument("--preview", action="store_true", help="Fetch split metadata and a redacted schema preview before downloading files")
    parser.add_argument("--config", help="Dataset Viewer config/subset to preview (required with --preview)")
    parser.add_argument("--split", help="Dataset Viewer split to preview (required with --preview)")
    args = parser.parse_args()
    if args.preview != bool(args.config and args.split):
        parser.error("--preview requires both --config and --split; pass neither to do metadata-only discovery.")
    try:
        result = discover_huggingface_dataset(args.repo_id, args.revision)
        if args.preview:
            result = {"discovery": result, "preflight": preview_huggingface_dataset(result, args.config, args.split)}
    except DataStudyError as error:
        parser.error(str(error))
    json.dump(result, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
