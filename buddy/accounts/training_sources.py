"""Massive training-source catalog. A row is allowed only after a grant.

Nothing here is copied from a book, site, or lecture. Hugging Face study
does not download weights.
"""

from __future__ import annotations

import json
from pathlib import Path

KINDS = [
    "school-course", "subject", "site", "book", "ebook", "lecture", "file",
    "youtube", "podcast", "lab", "syllabus", "worksheet", "exam-note",
    "union-course", "osha-course", "codecademy", "freecodecamp", "khan-academy",
    "mit-ocw", "college-catalog", "library-record", "paper-citation",
    "huggingface-model", "github-repo", "chatgpt-note",
]
EXPERTS = ["official", "counterexample", "measured", "practitioner", "critic"]
LANGUAGES = ["python", "javascript", "typescript", "go", "rust", "java", "c", "cpp", "sql", "swift"]
PRACTICES = ["tests", "permissions", "fail closed", "small diffs", "no secrets", "cite sources"]


def catalog() -> dict:
    return {
        "kinds": KINDS,
        "experts": EXPERTS,
        "languages": LANGUAGES,
        "practices": PRACTICES,
        "frontier_claim": False,
        "weights_downloaded": False,
    }


def main() -> int:
    path = Path(__file__).with_name("training_sources.json")
    path.write_text(json.dumps(catalog(), indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"kinds": len(KINDS), "frontier_claim": False}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
