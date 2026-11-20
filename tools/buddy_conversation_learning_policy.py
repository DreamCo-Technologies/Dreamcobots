"""Consent and privacy gate for Buddy conversation-learning candidates."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from typing import Any
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POLICY = ROOT / "config" / "buddy-conversation-learning-governance.json"
ALLOWED_FORMS = {"structured_preference", "user_correction", "task_outcome", "verified_procedure", "aggregate_pattern"}

def evaluate_candidate(candidate: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    reasons = []
    scope, form = candidate.get("scope", "personal_memory"), candidate.get("content_form")
    if scope not in {"personal_memory", "product_aggregate", "cross_user_shared", "foundation_model_training"}: reasons.append("unknown_scope")
    if candidate.get("raw_transcript") is True or form == "raw_transcript": reasons.append("raw_transcript_prohibited")
    if form not in ALLOWED_FORMS: reasons.append("unsupported_or_unreviewed_content_form")
    if candidate.get("contains_credentials") is True: reasons.append("credentials_prohibited")
    if candidate.get("contains_child_data") is True: reasons.append("child_data_excluded")
    if candidate.get("contains_sensitive_data") is True and scope != "personal_memory": reasons.append("sensitive_data_excluded_from_shared_learning")
    if candidate.get("contains_third_party_personal_data") is True and scope != "personal_memory": reasons.append("third_party_data_excluded_from_shared_learning")
    if scope == "personal_memory":
        if candidate.get("personal_memory_opt_in") is not True: reasons.append("personal_memory_opt_in_required")
        if not candidate.get("user_id"): reasons.append("user_scope_required")
        days = candidate.get("retention_days", 0)
        if not isinstance(days, int) or days < 1 or days > 365: reasons.append("retention_out_of_bounds")
    elif scope in {"product_aggregate", "cross_user_shared"}:
        if candidate.get("product_improvement_opt_in") is not True: reasons.append("product_improvement_opt_in_required")
        if scope == "cross_user_shared":
            if candidate.get("cross_user_sharing_opt_in") is not True: reasons.append("cross_user_sharing_opt_in_required")
            if candidate.get("deidentified") is not True: reasons.append("deidentification_required")
            if candidate.get("cohort_size", 0) < policy["cross_user_learning"]["minimum_cohort_size"]: reasons.append("minimum_cohort_not_met")
            if candidate.get("contains_sensitive_data") is True: reasons.append("sensitive_data_excluded_from_shared_learning")
            if candidate.get("contains_third_party_personal_data") is True: reasons.append("third_party_data_excluded_from_shared_learning")
            if candidate.get("user_id") or candidate.get("conversation_id"): reasons.append("direct_identifiers_prohibited_in_shared_record")
            if form not in {"aggregate_pattern", "verified_procedure"}: reasons.append("shared_learning_requires_generalized_lesson")
    elif scope == "foundation_model_training":
        gates = {"foundation_model_training_opt_in":"separate_model_training_opt_in_required","rights_evidence":"rights_and_provenance_evidence_required","deidentified":"deidentification_required","privacy_review_passed":"privacy_review_required","human_review_passed":"human_review_required","dataset_card_present":"dataset_card_required","withdrawal_path_present":"withdrawal_path_required"}
        for field, reason in gates.items():
            if candidate.get(field) is not True: reasons.append(reason)
    allowed = not reasons
    return {"schema":"dreamco.buddy_conversation_learning_decision.v1","decision":"ALLOW_CANDIDATE" if allowed else "DENY","scope":scope,"content_form":form,"reasons":reasons,"raw_transcript_stored":False,"cross_user_memory_written":False,"model_weights_updated":False,"note":"ALLOW_CANDIDATE is not ingestion, storage, model training, or deployment authorization."}

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--policy", default=str(DEFAULT_POLICY))
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    candidate = json.loads(Path(args.candidate).read_text(encoding="utf-8"))
    policy = json.loads(Path(args.policy).read_text(encoding="utf-8"))
    result = evaluate_candidate(candidate, policy)
    Path(args.output).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))
    return 0 if result["decision"] == "ALLOW_CANDIDATE" else 2

if __name__ == "__main__": raise SystemExit(main())
