import json
from pathlib import Path

from buddy.learning.action_failure_learning import build_evidence, classify_failure


def test_failure_signature_is_stable_and_classified():
    log_a = "TypeError: unsupported format string passed to list.__format__ at run 33286859982"
    log_b = "TypeError: unsupported format string passed to list.__format__ at run 33286860001"
    first = build_evidence("superbot-migration-ledger", "Compile migration ledger", log_a, "count records before formatting")
    second = build_evidence("superbot-migration-ledger", "Compile migration ledger", log_b, "count records before formatting")
    assert first.failure_class == "python_runtime"
    assert first.signature == second.signature


def test_learning_evidence_shape_is_json_serializable():
    evidence = build_evidence("buddy-benchmark-smoke", "benchmark", "assert failed", "repair capability")
    record = evidence.to_record()
    json.dumps(record)
    assert record["outcome"] == "unresolved"
    assert record["workflow"] == "buddy-benchmark-smoke"
