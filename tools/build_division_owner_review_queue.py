"""Build a source-backed owner review queue without guessing MasterBot/domain ownership."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "config/generated/division-resource-readiness-map.json"
RECONCILIATION = ROOT / "config/generated/division-reconciliation.json"
OUTPUT = ROOT / "config/generated/division-owner-review-queue.json"


class OwnerReviewQueueError(ValueError):
    pass


PLATFORM_EVIDENCE = [
    "config/masterbot-65-registry.json",
    "config/division-reconciliation-policy.json",
    "config/generated/division-reconciliation.json",
    "website/data/masterbot-homepage-featured.json",
]


def _unique_index(rows: list[dict[str, Any]], key: str, label: str) -> dict[int, dict[str, Any]]:
    result: dict[int, dict[str, Any]] = {}
    for row in rows:
        try:
            ident = int(row[key])
        except (KeyError, TypeError, ValueError) as exc:
            raise OwnerReviewQueueError(f"{label}_id_invalid") from exc
        if ident in result:
            raise OwnerReviewQueueError(f"duplicate_{label}_id")
        result[ident] = row
    return result


def build_owner_review_queue(
    source_path: Path = SOURCE,
    reconciliation_path: Path = RECONCILIATION,
) -> dict[str, Any]:
    source_raw = source_path.read_bytes()
    reconciliation_raw = reconciliation_path.read_bytes()
    source = json.loads(source_raw)
    reconciliation = json.loads(reconciliation_raw)
    review = source.get("owner_review") or {}

    platform_rows = reconciliation.get("shared_platform_masterbots", [])
    platform_by_id = _unique_index(platform_rows, "id", "shared_platform_masterbot")
    if platform_by_id and set(platform_by_id) != set(range(46, 66)):
        raise OwnerReviewQueueError("shared_platform_masterbots_must_cover_canonical_ids_46_through_65")

    source_routes = _unique_index(source.get("routes", []), "masterbot_id", "resource_route")
    source_decisions = _unique_index(
        review.get("masterbot_domain_decisions", []), "masterbot_id", "masterbot_decision"
    )
    for ident, platform in platform_by_id.items():
        route = source_routes.get(ident)
        decision = source_decisions.get(ident)
        if not route or not decision:
            raise OwnerReviewQueueError("shared_platform_masterbot_missing_resource_or_crosswalk_evidence")
        if route.get("masterbot_name") != platform.get("name") or decision.get("masterbot_name") != platform.get("name"):
            raise OwnerReviewQueueError("shared_platform_masterbot_identity_mismatch")
        if (
            platform.get("kind") != "shared_platform_service"
            or platform.get("ownership_status") != "shared_platform_not_a_domain_division"
            or platform.get("primary_domain_owner") is not None
            or platform.get("available_to_all_domain_divisions") is not True
            or not str(platform.get("purpose", "")).strip()
        ):
            raise OwnerReviewQueueError("shared_platform_role_lacks_source_backed_ownership_evidence")

    pending = []
    shared_platform = []
    for item in review.get("masterbot_domain_decisions", []):
        ident = int(item["masterbot_id"])
        if ident in platform_by_id:
            platform = platform_by_id[ident]
            route = source_routes[ident]
            shared_platform.append({
                "masterbot_id": ident,
                "masterbot_name": str(item["masterbot_name"]),
                "purpose": str(platform["purpose"]),
                "kind": "shared_platform_service",
                "ownership_status": "shared_platform_not_a_domain_division",
                "primary_domain_owner": None,
                "available_to_all_domain_divisions": True,
                "resource_bundle_id": route.get("resource_bundle_id"),
                "dataset_discovery_lane_id": route.get("dataset_discovery_lane_id"),
                "capability_pack_ids": list(route.get("capability_pack_ids") or []),
                "decision": "SHARED_PLATFORM_ROLE_REQUIRES_OWNER_CONFIRMATION",
                "owner_confirmation_required": True,
                "owner_approval": None,
                "evidence": PLATFORM_EVIDENCE,
                "no_domain_owner_inferred": True,
            })
            continue
        if item.get("decision") == "PENDING_OWNER_REVIEW" or item.get("primary_domain_id") is None:
            pending.append({
                "masterbot_id": ident,
                "masterbot_name": str(item["masterbot_name"]),
                "resource_bundle_id": item.get("resource_bundle_id"),
                "candidate_domain_ids": list(item.get("candidate_domain_ids") or []),
                "proposed_primary_domain_id": item.get("primary_domain_id"),
                "decision": "PENDING_OWNER_REVIEW",
                "owner_approval": item.get("owner_approval"),
                "evidence": list(item.get("evidence") or []),
                "no_mapping_inferred": True,
            })

    supplemental_by_name = {
        str(row.get("name", "")).casefold(): row
        for row in reconciliation.get("promoted_supplemental_divisions", [])
    }
    unassigned = []
    for item in review.get("unassigned_domain_profiles", []):
        if item.get("decision") != "PENDING_OWNER_REVIEW" and item.get("candidate_masterbot_ids"):
            continue
        supplemental = supplemental_by_name.get(str(item["domain_name"]).casefold())
        proposed_id = None
        related_domain = None
        evidence = list(item.get("evidence") or [])
        if supplemental:
            proposed_id = int(supplemental["proposed_collaborator_masterbot_id"])
            related_domain = str(supplemental["related_domain"])
            evidence.extend([
                "config/division-reconciliation-policy.json",
                "config/generated/division-reconciliation.json",
                str(supplemental["source_portfolio"]),
            ])
        candidates = [proposed_id] if proposed_id is not None else list(item.get("candidate_masterbot_ids") or [])
        unassigned.append({
            "domain_id": str(item["domain_id"]),
            "domain_name": str(item["domain_name"]),
            "candidate_masterbot_ids": candidates,
            "proposed_collaborator_masterbot_id": proposed_id,
            "related_domain": related_domain,
            "masterbot_link_status": "proposed_requires_owner_review" if proposed_id is not None else None,
            "resource_bundle_id": item.get("standalone_resource_bundle_id"),
            "decision": "PENDING_OWNER_REVIEW",
            "owner_approval": item.get("owner_approval"),
            "evidence": sorted(set(evidence)),
            "no_mapping_inferred": True,
        })

    pending.sort(key=lambda row: row["masterbot_id"])
    shared_platform.sort(key=lambda row: row["masterbot_id"])
    unassigned.sort(key=lambda row: row["domain_id"])
    all_masterbot_ids = [row["masterbot_id"] for row in pending + shared_platform]
    domain_ids = [row["domain_id"] for row in unassigned]
    if len(all_masterbot_ids) != len(set(all_masterbot_ids)) or len(domain_ids) != len(set(domain_ids)):
        raise OwnerReviewQueueError("duplicate_masterbot_or_domain_in_owner_review_source")

    return {
        "schema": "dreamco.division_owner_review_queue.v1",
        "source_map_sha256": hashlib.sha256(source_raw).hexdigest(),
        "reconciliation_sha256": hashlib.sha256(reconciliation_raw).hexdigest(),
        "masterbot_domain_decisions": pending,
        "shared_platform_masterbots": shared_platform,
        "unassigned_domain_profiles": unassigned,
        "counts": {
            "pending_masterbot_mappings": len(pending),
            "shared_platform_role_confirmations": len(shared_platform),
            "unassigned_domain_profiles": len(unassigned),
            "proposed_supplemental_collaborator_links": sum(
                row["proposed_collaborator_masterbot_id"] is not None for row in unassigned
            ),
        },
        "policy": {
            "auto_assignment": False,
            "name_similarity_is_not_approval": True,
            "owner_approval_required": True,
            "evidence_reference_required": True,
            "shared_platform_roles_are_not_domain_owners": True,
            "training_or_model_promotion_blocked_until_required_review": True,
        },
        "truth_boundary": (
            "The 20 MasterBots classified by the reconciliation policy as shared platform services "
            "are not assigned to a primary domain. Their role and operational owner still require "
            "owner confirmation. Supplemental-domain collaborator IDs are evidence-backed proposals, "
            "not approved assignments. No model training or production readiness is implied."
        ),
    }


def validate_owner_review_queue(queue: dict[str, Any]) -> None:
    if queue.get("schema") != "dreamco.division_owner_review_queue.v1":
        raise OwnerReviewQueueError("invalid_owner_review_queue_schema")
    counts = queue.get("counts", {})
    collections = {
        "pending_masterbot_mappings": queue.get("masterbot_domain_decisions", []),
        "shared_platform_role_confirmations": queue.get("shared_platform_masterbots", []),
        "unassigned_domain_profiles": queue.get("unassigned_domain_profiles", []),
    }
    for key, rows in collections.items():
        if counts.get(key) != len(rows):
            raise OwnerReviewQueueError(f"{key}_count_mismatch")
    proposed = sum(
        row.get("proposed_collaborator_masterbot_id") is not None
        for row in queue.get("unassigned_domain_profiles", [])
    )
    if counts.get("proposed_supplemental_collaborator_links") != proposed:
        raise OwnerReviewQueueError("proposed_supplemental_collaborator_count_mismatch")

    for item in queue.get("masterbot_domain_decisions", []) + queue.get("unassigned_domain_profiles", []):
        if item.get("decision") != "PENDING_OWNER_REVIEW" or item.get("no_mapping_inferred") is not True:
            raise OwnerReviewQueueError("unapproved_mapping_or_inferred_assignment_detected")
        if item.get("owner_approval") is not None:
            raise OwnerReviewQueueError("approved_source_item_requires_a_separate_signed_decision_record")

    for item in queue.get("shared_platform_masterbots", []):
        if (
            item.get("decision") != "SHARED_PLATFORM_ROLE_REQUIRES_OWNER_CONFIRMATION"
            or item.get("no_domain_owner_inferred") is not True
            or item.get("primary_domain_owner") is not None
            or item.get("owner_approval") is not None
            or item.get("kind") != "shared_platform_service"
            or item.get("ownership_status") != "shared_platform_not_a_domain_division"
            or item.get("available_to_all_domain_divisions") is not True
            or not str(item.get("purpose", "")).strip()
            or not item.get("evidence")
            or not item.get("resource_bundle_id")
        ):
            raise OwnerReviewQueueError("invalid_or_unapproved_shared_platform_masterbot_record")
        if item.get("masterbot_id") < 46 or item.get("masterbot_id") > 65:
            raise OwnerReviewQueueError("shared_platform_masterbot_id_out_of_range")

    for item in queue.get("unassigned_domain_profiles", []):
        proposed_id = item.get("proposed_collaborator_masterbot_id")
        if proposed_id is not None and (
            proposed_id not in item.get("candidate_masterbot_ids", [])
            or item.get("masterbot_link_status") != "proposed_requires_owner_review"
        ):
            raise OwnerReviewQueueError("supplemental_collaborator_proposal_must_remain_unapproved")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--reconciliation", type=Path, default=RECONCILIATION)
    parser.add_argument("--out", type=Path, default=OUTPUT)
    args = parser.parse_args()
    queue = build_owner_review_queue(args.source, args.reconciliation)
    validate_owner_review_queue(queue)
    rendered = json.dumps(queue, indent=2, ensure_ascii=False) + "\n"
    if args.check:
        if not args.out.exists() or args.out.read_text(encoding="utf-8") != rendered:
            raise SystemExit("owner review queue is stale; regenerate with tools/build_division_owner_review_queue.py")
        print(json.dumps({"ok": True, **queue["counts"]}, indent=2))
        return 0
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(rendered, encoding="utf-8")
    print(json.dumps({"written": args.out.relative_to(ROOT).as_posix(), **queue["counts"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
