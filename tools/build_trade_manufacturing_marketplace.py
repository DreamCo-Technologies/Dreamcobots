#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCOUT = ROOT / "config" / "china-us-tech-manufacturing-scout-program.json"
MARKET = ROOT / "config" / "us-manufacturer-rfq-marketplace-program.json"
OUT = ROOT / "config" / "generated" / "trade-manufacturing-marketplace.json"


def main() -> int:
    scout = json.loads(SCOUT.read_text(encoding="utf-8"))
    market = json.loads(MARKET.read_text(encoding="utf-8"))
    source_adapters = []
    for source in scout["source_classes"]:
        source_adapters.append({
            "source_class": source,
            "access_status": "adapter_or_authorized_export_required",
            "authorized_only": True,
            "provenance_required": True,
            "rate_limit_terms_required": True,
            "runtime_evidence": "missing_until_connected"
        })
    payload = {
        "schema": "dreamco.trade_manufacturing_marketplace.generated.v1",
        "scout": {
            "owner_division": scout["owner_division"],
            "comparison_dimensions": scout["comparison_dimensions"],
            "opportunity_types": scout["opportunity_types"],
            "source_adapters": source_adapters,
            "outputs": scout["outputs"],
        },
        "marketplace": {
            "roles": market["roles"],
            "manufacturer_profile_fields": market["manufacturer_profile"],
            "rfq_fields": market["rfq_fields"],
            "quote_fields": market["quote_fields"],
            "matching_score": market["matching_score"],
            "contract_flow": market["contract_flow"],
            "features": market["marketplace_features"],
            "payments": market["payments"],
        },
        "sandbox_requirements": [
            "manufacturer identity verification fixture",
            "buyer RFQ validation",
            "quote comparison",
            "landed-cost estimate",
            "MOQ and lead-time comparison",
            "false manufacturer claim rejection",
            "duplicate supplier detection",
            "trade compliance handoff",
            "IP/confidentiality warning",
            "sample/inspection workflow",
            "Stripe test payment",
            "refund/cancellation state",
            "production delay",
            "quality failure",
            "shipment delay",
            "dispute evidence",
            "mobile PWA flow",
            "offline draft/resume"
        ],
        "truth_boundary": "This generated catalog defines the marketplace/scout contracts. Live supplier discovery, quotes, certifications, payments and orders require connected authorized sources and runtime evidence."
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "sources": len(source_adapters), "rfq_fields": len(market["rfq_fields"]), "features": len(market["marketplace_features"]), "output": str(OUT.relative_to(ROOT))}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
