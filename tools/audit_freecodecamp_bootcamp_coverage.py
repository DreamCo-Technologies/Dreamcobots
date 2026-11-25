"""Audit end-to-end FreeCodeCamp Bootcamp coverage without overstating completion."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from typing import Any

OFFICIAL_CHANNEL_ID = "UC8butISFwT-Wl7EV0hUK0BQ"

def _rows(value: Any) -> list:
    return value if isinstance(value, list) else []

def _ids(rows: Any) -> list[str]:
    return [str(row.get("video_id", "")) for row in _rows(rows) if isinstance(row, dict)]

def audit_coverage(catalog: dict[str, Any], roadmap: dict[str, Any], manifest: dict[str, Any],
                   *, queue: dict[str, Any] | None = None, routes: dict[str, Any] | None = None,
                   domain_crosswalk: dict[str, Any] | None = None,
                   masterbot_registry: dict[str, Any] | None = None) -> dict[str, Any]:
    source = catalog.get("source") if isinstance(catalog.get("source"), dict) else {}
    videos = _rows(catalog.get("videos"))
    ids = _ids(videos)
    unique_ids = set(ids)
    duplicates = len(ids) - len(unique_ids)
    inv = catalog.get("inventory") if isinstance(catalog.get("inventory"), dict) else {}
    expected, observed = inv.get("expected_entry_count"), inv.get("observed_entry_count")
    inventory_complete = (
        catalog.get("inventory_status") == "complete" and inv.get("complete") is True
        and isinstance(expected, int) and expected == len(videos) and observed == len(videos)
        and inv.get("null_entry_count") == 0 and inv.get("duplicate_video_id_count") == 0
        and duplicates == 0
    )
    categories = {str(x.get("id")) for x in _rows(catalog.get("categories")) if isinstance(x, dict) and x.get("id")}
    unclassified, missing_categories, unknown_categories, malformed = [], [], {}, []
    for row in videos:
        if not isinstance(row, dict) or not row.get("video_id") or not row.get("title") or not row.get("url"):
            malformed.append(str(row.get("video_id", "<missing>")) if isinstance(row, dict) else "<non-object>")
            continue
        tags = row.get("categories")
        if not isinstance(tags, list) or not tags:
            missing_categories.append(str(row["video_id"]))
            continue
        unknown = sorted(set(map(str, tags)) - categories)
        if unknown:
            unknown_categories[str(row["video_id"])] = unknown
        if "other_or_unclassified" in tags or "other_needs_review" in tags:
            unclassified.append(str(row["video_id"]))

    scope = roadmap.get("scope") if isinstance(roadmap.get("scope"), dict) else {}
    official = roadmap.get("official_platform_inventory") if isinstance(roadmap.get("official_platform_inventory"), dict) else {}
    interactive = roadmap.get("interactive_curriculum_inventory") if isinstance(roadmap.get("interactive_curriculum_inventory"), dict) else {}
    tracks = _rows(roadmap.get("video_learning_tracks"))
    core = _rows(official.get("core_certifications"))
    additional = _rows(official.get("additional_certifications"))
    primitives = _rows(official.get("curriculum_primitives"))

    queue_report = {"status": "NOT_PROVIDED"}
    if queue is not None:
        qrows = _rows(queue.get("videos")); qids = _ids(qrows); qset = set(qids)
        queue_report = {
            "status": "COMPLETE" if qset == unique_ids and len(qids) == len(unique_ids) else "GAPS",
            "rows": len(qrows), "missing_video_ids": sorted(unique_ids-qset),
            "extra_video_ids": sorted(qset-unique_ids), "duplicate_rows": len(qids)-len(qset),
            "approved_guides": queue.get("guide_approved_count", 0),
            "authorized_for_guide": queue.get("authorized_for_guide_count", 0),
            "pending_or_blocked": queue.get("pending_or_blocked_count", len(qrows)),
        }
    route_report = {"status": "NOT_PROVIDED"}
    if routes is not None:
        rrows = _rows(routes.get("videos")); rids = _ids(rrows); rset = set(rids)
        divisions = _rows(routes.get("divisions"))
        route_report = {
            "status": "COMPLETE" if rset == unique_ids and len(rids) == len(unique_ids) and len(divisions) == 65 else "GAPS",
            "video_rows": len(rrows), "missing_video_ids": sorted(unique_ids-rset),
            "extra_video_ids": sorted(rset-unique_ids), "division_rows": len(divisions),
        }

    domain_count = len(_rows((domain_crosswalk or {}).get("domains"))) if domain_crosswalk is not None else None
    lane_count = len(_rows((masterbot_registry or {}).get("divisions"))) if masterbot_registry is not None else None
    rights_policy = manifest.get("rights_policy") if isinstance(manifest.get("rights_policy"), dict) else {}
    transcript_rows = _rows(manifest.get("transcripts"))
    authorized = [x for x in transcript_rows if isinstance(x, dict)
        and x.get("rights_status") == "VERIFIED" and x.get("study_permission") is True
        and x.get("summary_derivative_permission") is True and x.get("evaluation_permission") is True
        and bool(x.get("rights_evidence_ref"))]
    training = [x for x in authorized if x.get("training_permission") is True and x.get("training_rights_evidence_ref")]

    gaps = []
    if source.get("channel_id") != OFFICIAL_CHANNEL_ID: gaps.append("catalog_source_is_not_verified_official_freecodecamp_channel")
    if not scope.get("include_all_public_channel_videos"): gaps.append("roadmap_does_not_require_all_public_channel_videos")
    if not inventory_complete: gaps.append("official_channel_video_inventory_is_partial_or_unverified")
    if duplicates: gaps.append("catalog_contains_duplicate_video_ids")
    if malformed: gaps.append("catalog_contains_malformed_video_records")
    if missing_categories: gaps.append("some_videos_have_no_subject_category")
    if unknown_categories: gaps.append("some_videos_use_categories_missing_from_taxonomy")
    if unclassified: gaps.append("some_videos_remain_in_the_unclassified_human_review_queue")
    if len(tracks) != 22: gaps.append("video_subject_track_count_differs_from_expected_22_track_taxonomy")
    if len(core) < 7: gaps.append("current_core_certification_inventory_is_incomplete")
    if len(additional) < 5: gaps.append("additional_language_or_specialist_certification_inventory_is_incomplete")
    if len(primitives) < 7: gaps.append("curriculum_primitives_are_incomplete")
    if interactive.get("status") != "verified_current": gaps.append("interactive_curriculum_inventory_is_a_dated_snapshot_or_unverified")
    if domain_count is not None and domain_count != 55: gaps.append("canonical_domain_crosswalk_does_not_contain_55_domains")
    if lane_count is not None and lane_count != 65: gaps.append("canonical_masterbot_registry_does_not_contain_65_lanes")
    if queue is None or queue_report["status"] != "COMPLETE": gaps.append("per_video_detailed_study_queue_is_missing_or_incomplete")
    if routes is None or route_report["status"] != "COMPLETE": gaps.append("per_video_division_route_manifest_is_missing_or_incomplete")
    if queue_report.get("approved_guides", 0) < len(videos): gaps.append("not_every_catalog_video_has_an_approved_detailed_study_guide")
    if not authorized: gaps.append("no_item_level_authorized_transcripts_are_registered_for_detailed_guides")
    if not training: gaps.append("no_source_has_separate_model_weight_training_permission")

    return {
        "schema": "dreamco.freecodecamp_bootcamp_coverage_audit.v1",
        "source": {"name": "freeCodeCamp.org", "channel_id": source.get("channel_id"), "channel_url": source.get("channel_url")},
        "status": "COMPLETE" if not gaps else "INCOMPLETE",
        "video_inventory": {"catalog_rows": len(videos), "unique_video_ids": len(unique_ids),
            "duplicate_ids": duplicates, "expected_upstream_count": expected, "observed_upstream_count": observed,
            "inventory_complete": inventory_complete, "unclassified_video_count": len(unclassified),
            "unclassified_video_ids": sorted(unclassified), "missing_category_count": len(missing_categories),
            "unknown_category_video_count": len(unknown_categories), "malformed_video_count": len(malformed)},
        "curriculum": {"video_subject_tracks": len(tracks), "core_certifications": len(core),
            "additional_certifications": len(additional), "curriculum_primitives": len(primitives),
            "interactive_curriculum_inventory_status": interactive.get("status", "missing"),
            "interactive_curriculum_snapshot": {k: interactive.get(k) for k in ("superblocks","chapters","modules","unique_blocks","challenges")}},
        "division_coverage": {"domain_divisions": domain_count, "masterbot_lanes": lane_count},
        "per_video_study_queue": queue_report, "per_video_division_routes": route_report,
        "rights_and_learning": {"registered_transcript_assets": len(transcript_rows),
            "authorized_for_study_summary_and_evaluation": len(authorized),
            "separately_authorized_for_model_weight_training": len(training),
            "automatic_caption_scraping": rights_policy.get("automatic_caption_scraping"),
            "automatic_transcript_download": rights_policy.get("automatic_transcript_download"),
            "automatic_model_training": rights_policy.get("automatic_model_training")},
        "gaps": gaps,
        "truth_boundary": "Metadata discovery and queue placement are not video study, detailed guide completion, model training, user completion, or mastery. Transcript/media ingestion and model-weight training remain separately rights-gated."
    }

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=Path("buddy/bootcamp/sources/freecodecamp/catalog.json"))
    parser.add_argument("--roadmap", type=Path, default=Path("config/freecodecamp-complete-learning-path.json"))
    parser.add_argument("--transcript-manifest", type=Path, default=Path("config/authorized-transcripts/manifest.json"))
    parser.add_argument("--queue", type=Path)
    parser.add_argument("--routes", type=Path)
    parser.add_argument("--domain-crosswalk", type=Path, default=Path("config/generated/masterbot-55-domain-crosswalk.json"))
    parser.add_argument("--masterbot-registry", type=Path, default=Path("config/masterbot-65-registry.json"))
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()
    def read(path):
        return json.loads(path.read_text(encoding="utf-8")) if path else None
    report = audit_coverage(read(args.catalog) or {}, read(args.roadmap) or {}, read(args.transcript_manifest) or {},
        queue=read(args.queue), routes=read(args.routes), domain_crosswalk=read(args.domain_crosswalk),
        masterbot_registry=read(args.masterbot_registry))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "catalog_rows": report["video_inventory"]["catalog_rows"],
        "unclassified_video_count": report["video_inventory"]["unclassified_video_count"], "gaps": report["gaps"]}, indent=2))
    return 1 if args.require_complete and report["status"] != "COMPLETE" else 0

if __name__ == "__main__":
    raise SystemExit(main())
