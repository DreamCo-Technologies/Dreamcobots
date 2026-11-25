"""CLI for Buddy's internal-first universal library knowledge registry."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from buddy.learning.universal_library_registry import (
    library_coverage_report,
    record_library_knowledge_gap,
    search_internal_library_knowledge,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    sub = parser.add_subparsers(dest="command", required=True)
    search = sub.add_parser("search", help="Search approved internal library study guides only")
    search.add_argument("query")
    search.add_argument("--limit", type=int, default=10)
    search.add_argument("--include-experimental", action="store_true")
    gap = sub.add_parser("record-gap", help="Append an internal knowledge gap without external routing")
    gap.add_argument("query")
    gap.add_argument("--reason", default="no_approved_internal_guide_match")
    report = sub.add_parser("report", help="Print library ecosystem and guide coverage")
    args = parser.parse_args()
    if args.command == "search":
        result = search_internal_library_knowledge(
            args.query, root=args.root, limit=args.limit,
            include_experimental=args.include_experimental,
        )
    elif args.command == "record-gap":
        result = record_library_knowledge_gap(args.query, reason=args.reason, root=args.root)
    else:
        result = library_coverage_report(root=args.root)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
