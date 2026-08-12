#!/usr/bin/env python3
"""Generate DreamCo library-specialist discovery records without installing packages.

The generator is additive and evidence-first. It inventories repository-declared
packages plus curated ecosystem seeds, creates distinct specialist identities,
and never marks a specialist certified merely because a record exists.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ECOSYSTEMS = ROOT / "config" / "library_ecosystems.json"
PACKAGE_JSON = ROOT / "package.json"
OUTPUT = ROOT / "config" / "generated" / "library_specialist_registry.json"

PYTHON_SEEDS = [
    "numpy", "pandas", "scipy", "scikit-learn", "matplotlib", "fastapi",
    "flask", "django", "requests", "httpx", "pydantic", "pytest", "selenium",
    "playwright", "sqlalchemy", "transformers", "torch", "tensorflow",
]


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9._@/+:-]+", "-", value.lower()).strip("-")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def package_specialist(ecosystem: str, package: str, source: str) -> dict[str, Any]:
    specialist_id = f"{ecosystem}:{slug(package)}"
    return {
        "id": specialist_id,
        "displayName": f"{package} Library Specialist",
        "ecosystem": ecosystem,
        "package": package,
        "discoverySource": source,
        "status": "discovered",
        "certified": False,
        "capabilities": [
            "study official documentation and public API surface",
            "map common and advanced use cases",
            "generate examples and test plans",
            "analyze compatibility and dependency requirements",
            "propose DreamCo integrations and new product ideas",
            "route implementation questions to the correct library context",
        ],
        "evidenceRequiredForCertification": True,
        "executionIsolationRequired": True,
    }


def build_registry() -> dict[str, Any]:
    ecosystem_data = load_json(ECOSYSTEMS)
    records: dict[str, dict[str, Any]] = {}

    if PACKAGE_JSON.exists():
        package_json = load_json(PACKAGE_JSON)
        for section in ("dependencies", "devDependencies", "optionalDependencies"):
            for package in package_json.get(section, {}):
                record = package_specialist("javascript", package, f"package.json:{section}")
                records.setdefault(record["id"], record)

    for package in PYTHON_SEEDS:
        record = package_specialist("python", package, "curated_high_value_seed")
        records.setdefault(record["id"], record)

    specialists = sorted(records.values(), key=lambda item: item["id"])
    return {
        "schema": "dreamco.library_specialist_registry.v1",
        "truthContract": {
            "recordMeansInstalled": False,
            "recordMeansCertified": False,
            "recordMeansConnected": False,
            "certificationRequiresEvidence": True,
            "thirdPartyCodeRunsInMainProcess": False,
        },
        "summary": {
            "specialists": len(specialists),
            "ecosystemDiscoveryTargets": len(ecosystem_data["ecosystems"]),
            "certified": 0,
        },
        "ecosystemDiscoveryTargets": ecosystem_data["ecosystems"],
        "specialists": specialists,
        "expansionPolicy": [
            "discover additional packages from approved official registries",
            "deduplicate by normalized ecosystem and package identity",
            "keep registry discovery separate from package execution",
            "sandbox install and representative tests before certification",
            "attach version, license, source, security, and compatibility evidence",
            "allow Buddy to propose new ecosystem adapters when coverage gaps appear",
        ],
    }


def render() -> str:
    return json.dumps(build_registry(), indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = render()
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != content:
            print(f"OUT OF DATE: {OUTPUT.relative_to(ROOT)}")
            return 1
        print(f"PASS: {OUTPUT.relative_to(ROOT)}")
        return 0
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(content, encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
