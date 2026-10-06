"""Study-course catalog. A row is a course Buddy can study, not a certificate."""

from __future__ import annotations

import json
from pathlib import Path

OUT = Path(__file__).with_name("course_catalog.json")
DOMAINS = {
    "college": ["writing", "biology", "chemistry", "physics", "calculus", "statistics", "history", "economics", "psychology", "computer science"],
    "union": ["steward basics", "contract reading", "grievance steps", "safety committee", "apprenticeship"],
    "osha": ["hazard communication", "fall protection", "lockout tagout", "forklift", "bloodborne pathogens"],
    "games": ["rules design", "balance", "level design", "playtesting", "narrative"],
    "simulation": ["discrete event", "agent based", "physics sandbox", "emergency drill", "flight procedures"],
    "commercials": ["script", "claims review", "consent", "edit", "disclosure"],
    "trades": ["electrical", "plumbing", "hvac", "welding", "carpentry"],
    "health": ["first aid", "nutrition", "medical terminology", "patient privacy", "billing codes"],
    "business": ["bookkeeping", "sales", "hiring", "tax basics", "customer support"],
    "government": ["records", "privacy", "procurement", "public comment", "benefits navigation"],
    "language": ["spanish", "french", "english writing", "public speaking", "translation notes"],
    "media": ["voice consent", "image consent", "captioning", "editing", "watermarking"],
}


def catalog() -> dict:
    courses = []
    for domain, names in DOMAINS.items():
        for name in names:
            courses.append({"id": f"{domain}-{name.replace(' ', '-')}", "domain": domain, "name": name, "mastered": False})
    return {"schema": "dreamco.study_courses.v1", "courses": courses, "certified": False}


def main() -> int:
    report = catalog()
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"courses": len(report["courses"]), "domains": len(DOMAINS), "certified": False}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
