#!/usr/bin/env python3
"""Read-only evidence gate for proposed chat archival; never archives or deletes.

A passing result validates the evidence contract, not the correctness of the
linked code or tests. A reviewer must verify those artifacts before applying it.
Raw chat exports and private requirement ledgers must stay outside public Pages.
"""
import argparse
import json
import re
from pathlib import Path


def archive_eligibility(conversation):
    """Return blockers without copying source text or private evidence into output."""
    blockers = []
    source = conversation.get("source", {})
    for flag in ("complete", "semantic_review_complete", "attachments_complete"):
        if source.get(flag) is not True:
            blockers.append("source_" + flag + "_unverified")
    if source.get("truncated_blocks", 0):
        blockers.append("truncated_source")
    if source.get("unresolved_references", 0):
        blockers.append("unresolved_source_references")
    messages = conversation.get("messages", [])
    requirements = conversation.get("requirements", [])
    if not messages:
        blockers.append("message_inventory_missing")
    if not requirements:
        blockers.append("requirement_inventory_missing")
    ids = [r.get("id") for r in requirements]
    if any(not x for x in ids) or len(ids) != len(set(ids)):
        blockers.append("invalid_requirement_ids")
    by_id = {r.get("id"): r for r in requirements}
    for message in messages:
        mid = message.get("id", "unknown")
        if not re.fullmatch(r"[0-9a-f]{64}", str(message.get("sha256", ""))):
            blockers.append("message_hash_missing:" + mid)
        refs = message.get("requirement_ids", [])
        # Even short approvals need a reviewed link to the scope they approved.
        if message.get("reviewed") is not True or not refs or any(x not in by_id for x in refs):
            blockers.append("message_coverage_unverified:" + mid)
    for requirement in requirements:
        rid = requirement.get("id", "unknown")
        evidence = requirement.get("evidence", {})
        if requirement.get("status") != "implemented":
            blockers.append("requirement_not_implemented:" + rid)
        if not evidence.get("code_refs") or not re.fullmatch(r"[0-9a-f]{40}", str(evidence.get("commit", ""))):
            blockers.append("code_evidence_missing:" + rid)
        if (evidence.get("acceptance_verified") is not True
                or evidence.get("reviewed") is not True
                or evidence.get("test_result") != "passed"
                or not evidence.get("test_artifact")):
            blockers.append("acceptance_evidence_missing:" + rid)
        if requirement.get("requires_live_verification", True) and (
                evidence.get("live_verified") is not True
                or evidence.get("deployed_commit") != evidence.get("commit")
                or not evidence.get("live_artifact")):
            blockers.append("live_evidence_missing:" + rid)
        if requirement.get("requires_real_execution", False) and evidence.get("execution_mode") != "real":
            blockers.append("real_execution_unverified:" + rid)
    return {"id": conversation.get("id"), "archive_candidate": not blockers,
            "blockers": blockers, "requirements": len(requirements),
            "messages": len(messages), "action_taken": "none"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    ledger = json.loads(args.ledger.read_text())
    results = [archive_eligibility(c) for c in ledger.get("conversations", [])]
    output = {"schema": "dreamco.chat_archive_review.v1", "action_taken": "none",
              "notice": "Evidence contract only; linked artifacts still require review. No chats were archived.",
              "archive_candidates": sum(x["archive_candidate"] for x in results),
              "conversations": results}
    content = json.dumps(output, indent=2) + "\n"
    if args.output:
        args.output.write_text(content)
    else:
        print(content, end="")


if __name__ == "__main__":
    main()
