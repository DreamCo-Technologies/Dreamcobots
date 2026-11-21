"""Rights-aware task specification extraction; no model weights or copyrighted copying."""
import hashlib
import json
import re

def distill(records):
    tasks, seen = [], set()
    for source in records:
        if source.get("rights") not in ("owned", "licensed", "public_domain"):
            continue
        if source.get("permission_to_derive") is not True:
            continue
        domain = source.get("domain")
        if domain not in ("coding", "research", "multi_step_tools"):
            continue
        statement = source.get("task_description", "").strip()
        contract = source.get("success_criteria", "").strip()
        if not statement or not contract:
            continue
        # Fingerprint task intent and acceptance contract, not source-specific IDs.
        key = hashlib.sha256(json.dumps([domain, re.sub(r"\s+", " ", statement.lower()),
                                          re.sub(r"\s+", " ", contract.lower())]).encode()).hexdigest()
        if key in seen:
            continue
        seen.add(key)
        tasks.append({"id": key[:20], "domain": domain,
                      "description": statement, "success_criteria": contract,
                      "source_id": source.get("source_id"), "source_sha256": source.get("source_sha256"),
                      "rights": source["rights"], "license": source.get("license"),
                      "skills_to_study": source.get("skills_to_study", []),
                      "references": source.get("authorized_references", []),
                      "evaluation_status": "requires_independent_test",
                      "training_status": "not_started",
                      "holdout_answer_in_training": False})
    return {"schema": "dreamco.distilled_task_contracts.v1", "count": len(tasks),
            "tasks": tasks, "note": "Authorized task-contract distillation only; no source-code reproduction, automatic training, or holdout leakage."}
