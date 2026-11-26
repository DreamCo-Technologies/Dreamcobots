"""Tests keep 55 domain divisions separate from 65 MasterBots."""
from tools.benchmark_gap_planner import build_gap_queue
from tools.build_benchmark_training_queue import build_training_queue
from tools.convert_daily_division_benchmark import convert
from tools.execute_benchmark_training_queue import build_execution_plan


def fixtures():
    registry = {"divisions": [{"id": i, "name": f"MasterBot{i}"} for i in range(1, 66)]}
    domains = [
        {
            "domain_id": f"domain-{i}",
            "domain_name": f"Domain{i}",
            "masterbot_id": i if i <= 45 else None,
            "mapping_status": "proposed_exact_name_match" if i <= 45 else "unresolved",
            "owner_approval": None,
        }
        for i in range(55)
    ]
    crosswalk = {"domains": domains}
    source = {
        "divisions": 55,
        "divisionResults": [
            {"division": row["domain_name"], "score": 50 if i == 0 else 100,
             "status": "failed" if i == 0 else "pass", "passed": 5 if i == 0 else 10}
            for i, row in enumerate(domains)
        ],
    }
    return registry, crosswalk, source


def test_converter_preserves_domain_scope_without_inventing_masterbot_ownership():
    _, crosswalk, source = fixtures()
    converted = convert(source, crosswalk)
    assert converted["domain_division_count"] == 55
    assert converted["masterbot_evidence_count"] == 0
    assert all(row["scope"] == "domain_division" for row in converted["results"])
    assert all(row["masterbot_id"] is None for row in converted["results"])
    assert converted["results"][0]["domain_id"] == "domain-0"


def test_converter_rejects_unknown_duplicate_or_missing_domain_rows():
    _, crosswalk, source = fixtures()
    unknown = {**source, "divisionResults": [*source["divisionResults"][:-1], {
        **source["divisionResults"][-1], "division": "UnknownDivision"
    }]}
    try:
        convert(unknown, crosswalk)
    except ValueError as exc:
        assert "unknown domain" in str(exc)
    else:
        raise AssertionError("unknown domain was accepted")
    duplicate = {**source, "divisionResults": [*source["divisionResults"], source["divisionResults"][0]]}
    try:
        convert(duplicate, crosswalk)
    except ValueError as exc:
        assert "duplicate" in str(exc)
    else:
        raise AssertionError("duplicate domain result was accepted")
    missing = {**source, "divisionResults": source["divisionResults"][:-1], "divisions": 54}
    try:
        convert(missing, crosswalk)
    except ValueError as exc:
        assert "missing canonical domain" in str(exc)
    else:
        raise AssertionError("missing domain result was accepted")


def test_planner_builds_separate_65_masterbot_and_55_domain_queues():
    registry, crosswalk, source = fixtures()
    scores = convert(source, crosswalk)
    queue = build_gap_queue(scores, registry, crosswalk)
    assert queue["masterbot_count"] == 65
    assert queue["domain_division_count"] == 55
    assert len(queue["queue"]) == 120
    assert queue["summary"]["masterbots_measured"] == 0
    assert queue["summary"]["masterbots_unmeasured"] == 65
    assert queue["summary"]["domain_divisions_measured"] == 55
    masterbots = [row for row in queue["queue"] if row["scope"] == "masterbot"]
    domains = [row for row in queue["queue"] if row["scope"] == "domain_division"]
    assert len(masterbots) == 65 and len(domains) == 55
    assert all(row["action"] == "RUN_BENCHMARKS" for row in masterbots)
    failed = next(row for row in domains if row["domain_id"] == "domain-0")
    assert failed["action"] == "CLOSE_GAPS"
    assert failed["score"] == 50
    passed = next(row for row in domains if row["domain_id"] == "domain-1")
    assert passed["action"] == "RUN_SANDBOX"


def test_domain_evidence_cannot_be_promoted_to_masterbot_mastery():
    registry, crosswalk, source = fixtures()
    scores = convert(source, crosswalk)
    scores["results"][0]["masterbot_id"] = 1
    try:
        build_gap_queue(scores, registry, crosswalk)
    except ValueError as exc:
        assert "cannot assign MasterBot ownership or mastery" in str(exc)
    else:
        raise AssertionError("domain evidence was promoted to MasterBot evidence")


def test_training_queue_and_executor_preserve_scope_and_execute_nothing():
    registry, crosswalk, source = fixtures()
    gap_queue = build_gap_queue(convert(source, crosswalk), registry, crosswalk)
    training = build_training_queue(gap_queue)
    assert training["scope_counts"] == {"masterbot": 65, "domain_division": 55}
    plan = build_execution_plan(training, limit=10)
    assert plan["executed"] == 0
    assert plan["planned"] == 10
    assert all(row["scope"] in {"masterbot", "domain_division"} for row in plan["runs"])
    assert all(row["masterbot_id"] is not None for row in plan["runs"] if row["scope"] == "masterbot")
    assert all(row["domain_id"] for row in plan["runs"] if row["scope"] == "domain_division")
