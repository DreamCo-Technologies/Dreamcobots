#!/usr/bin/env python3
"""Inventory the entire repository before Superbot consolidation.

This intentionally scans every tracked-looking file, not only bots/ or App_bots/.
It creates a provenance-preserving inventory and assigns every file a proposed
Superbot owner. Ambiguous files are marked review_required instead of being
silently merged into the wrong owner.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "superbot-consolidation-v1.json"
OUT = ROOT / "config" / "generated" / "superbot-repository-inventory.json"
REPORT = ROOT / "reports" / "SUPERBOT_REPOSITORY_INVENTORY.md"
SKIP = {".git", "node_modules", "dist", "build", "coverage", ".next", ".venv", "venv", ".buddy-local"}

ROOT_RULES = {
    "App_bots": "catalog", "bots": "runtime", "original-bots": "legacy", "attached_assets": "evidence",
    "server": "runtime", "shared": "contract", "framework": "ai", "global_learning_system": "ai",
    "learning_system": "ai", "memory": "ai", "tools": "engineering", "tests": "engineering",
    "website": "product", "frontend": "product", "backend": "engineering", "api": "engineering",
    ".github": "engineering", "docs": "governance", "reports": "governance", "config": "governance",
    "money_os": "money", "money": "money", "real_estate": "real_assets", "finance": "finance_risk",
    "security": "security_governance", "cyber": "security_governance", "sales": "sales_growth",
    "content": "content_media", "education": "people_services",
}
KEYWORDS = {
    "money": ["money", "deal", "coupon", "receipt", "cashback", "settlement", "grant", "lead", "wealth", "fiverr", "revenue", "profit", "job_application"],
    "real_assets": ["real_estate", "home_buyer", "construction", "maintenance", "transport", "agriculture", "equipment", "property"],
    "finance_risk": ["finance", "loan", "payment", "trade", "trading", "crypto", "mining", "billing", "token"],
    "sales_growth": ["sales", "lead", "crm", "customer", "influence", "social", "referral", "marketing"],
    "commerce": ["market", "retail", "shop", "store", "ecommerce", "product", "affiliate", "flip"],
    "content_media": ["content", "video", "audio", "creator", "game", "arts", "media"],
    "people_services": ["education", "health", "personal", "food", "service", "job", "career"],
    "security_governance": ["security", "cyber", "legal", "compliance", "governance", "audit", "trust", "protection"],
    "ai_infra": ["ai", "model", "learning", "memory", "embedding", "agent", "research", "science", "data"],
    "business": ["business", "enterprise", "consult", "strategy", "launch", "operations"],
    "engineering": ["code", "software", "debug", "test", "deploy", "workflow", "automation", "api", "runtime", "devops"],
    "command": ["command", "admin", "control", "orchestrat", "fleet", "decision", "monitor", "health"],
}


def owner_for(path: Path, division: str | None = None) -> tuple[str, str, bool]:
    parts = [p.lower() for p in path.parts]
    if division and division in division_map:
        return division_map[division], "division_mapping", False
    scores = {key: 0 for key in KEYWORDS}
    hay = " ".join(parts)
    for owner, words in KEYWORDS.items():
        scores[owner] = sum(2 if word in path.name.lower() else 1 for word in words if word in hay)
    best = max(scores, key=scores.get)
    if scores[best] == 0:
        root = parts[0] if parts else ""
        if root in ROOT_RULES:
            role = ROOT_RULES[root]
            role_map = {"catalog":"command", "runtime":"engineering", "legacy":"command", "evidence":"command", "contract":"engineering", "ai":"ai_infra", "product":"engineering", "governance":"security_governance"}
            return role_map.get(role, "command"), "root_default", True
        return "command", "unclassified_default", True
    tied = [k for k,v in scores.items() if v == scores[best] and v > 0]
    return best, "keyword" if len(tied) == 1 else "tie", len(tied) != 1


def load_divisions() -> dict[str, str]:
    data = json.loads(CONFIG.read_text(encoding="utf-8"))
    return data.get("division_mapping", {})


def detect_division(text: str) -> str | None:
    for match in re.findall(r'"division"\s*:\s*"([^"]+)"', text):
        return match
    return None


division_map = load_divisions()


def main() -> int:
    records = []
    counts = {}
    review = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or any(part in SKIP for part in path.parts):
            continue
        rel = path.relative_to(ROOT)
        try:
            raw = path.read_bytes()
            text = raw.decode("utf-8", errors="replace")
        except Exception:
            raw = b""; text = ""
        division = detect_division(text[:200000])
        owner, method, needs_review = owner_for(rel, division)
        rec = {
            "path": str(rel), "size_bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
            "division": division, "proposed_superbot": owner, "assignment_method": method,
            "review_required": needs_review,
            "is_bot_named": bool(re.search(r"(bot|agent|assistant|worker|scout|planner|optimizer|builder|manager)", rel.name, re.I)),
        }
        records.append(rec); counts[owner] = counts.get(owner, 0) + 1
        if needs_review: review.append(rec["path"])
    app_bots = [r for r in records if r["path"].startswith("App_bots/") and r["path"].endswith(".json")]
    bot_named = [r for r in records if r["is_bot_named"]]
    payload = {
        "schema":"dreamco.superbot_repository_inventory.v1",
        "repository":"DreamCo-Technologies/Dreamcobots",
        "scan_scope":"entire repository excluding generated/build/cache dependency directories",
        "file_count":len(records),
        "app_bot_profile_files":len(app_bots),
        "bot_named_files":len(bot_named),
        "review_required_count":len(review),
        "superbot_file_counts":counts,
        "records":records,
        "merge_rule":"Every file is preserved with provenance. No file is deleted until capability, dependency, route, permission, observability, revenue and E2E parity are proven.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True); REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    report = ["# Superbot Repository Inventory", "", f"- Files scanned: **{len(records):,}**", f"- App_bots profile files: **{len(app_bots):,}**", f"- Bot-named files: **{len(bot_named):,}**", f"- Files needing assignment review: **{len(review):,}**", "", "## Proposed ownership", ""]
    for owner, count in sorted(counts.items()): report.append(f"- **{owner}**: {count:,} files")
    report += ["", "## Consolidation safety", "", "No deletion is authorized by this inventory. It is a complete provenance map used by the Superbot migration gates."]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps({"ok":True,"files":len(records),"app_bot_profiles":len(app_bots),"bot_named_files":len(bot_named),"review_required":len(review),"owners":counts}, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
