import json
from pathlib import Path

from tools.audit_buddy_bootcamp_coverage import audit


def _write(root: Path, relative: str, value: dict) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def _fixture(root: Path) -> None:
    _write(root, "config/buddy-huggingface-full-learning-map.json", {
        "course_count": 1, "official_courses": [{"id": "hf-a"}],
        "ecosystem_modules": [{"id": "module-a"}], "ecosystem_module_count": 1
    })
    _write(root, "config/buddy-onet-content-model-curriculum.json", {
        "status": "curriculum_defined_source_refresh_required",
        "content_model_areas": [{"id": "skills"}]
    })
    _write(root, "buddy/bootcamp/sources/freecodecamp/catalog.json", {
        "inventory_status": "partial", "video_count": 1, "videos": [{"video_id": "abc"}]
    })
    _write(root, "config/freecodecamp-complete-learning-path.json", {
        "scope": {"coverage_status": "ROADMAP_DEFINED_VIDEO_CATALOG_REFRESH_REQUIRED"}
    })
    _write(root, "config/buddy-tokenizer-training-curriculum.json", {
        "status": "curriculum_ready_training_not_executed"
    })
    _write(root, "config/buddy-tolkien-study-track.json", {
        "status": "extended_curriculum_defined_course_reference_pending",
        "curriculum": [{"id": "philology"}]
    })
    _write(root, "config/masterbot-65-registry.json", {
        "canonical_count": 65, "divisions": [{"id": i} for i in range(65)]
    })
    _write(root, "config/generated/masterbot-55-domain-crosswalk.json", {
        "status": "proposed_requires_owner_review",
        "counts": {"domain_divisions": 55},
        "domains": [{"owner_approval": None} for _ in range(55)]
    })
    _write(root, "config/buddy-workforce-entrepreneurship-bootcamp.json", {
        "training_paths": [
            {"id": "career", "subjects": ["resume", "interview"]},
            {"id": "business", "subjects": ["pricing"]}
        ],
        "task_capability_catalog": {"task_playbook_requirements": ["task_definition", "workflow_steps", "acceptance_tests"]}
    })
    _write(root, "config/buddy-benchmark-index.json", {
        "programs": [{"id": "repo", "name": "Repository tests"}]
    })
    _write(root, "config/buddy-benchmark-task-registry.json", {
        "tasks": ["coding", "reasoning"]
    })
    _write(root, "config/buddy-25m-cpu-architecture-profile.json", {
        "parameter_target": 25000000,
        "training_policy": {"enabled": False, "weight_updates_authorized": False}
    })


def test_audit_reports_inventory_without_claiming_mastery(tmp_path: Path):
    _fixture(tmp_path)
    report = audit(tmp_path)
    assert report["completion_claim"] is False
    assert report["tracks"]["masterbots"]["records"] == 65
    assert report["tracks"]["division_crosswalk"]["declared_divisions"] == 55
    assert report["tracks"]["freecodecamp"]["transcripts_complete"] is False
    assert report["errors"] == []
    assert report["status"] == "coverage_gaps_present"



def test_audit_includes_revenue_benchmark_and_cpu_model_backlogs(tmp_path: Path):
    _fixture(tmp_path)
    report = audit(tmp_path)
    assert report["tracks"]["workforce_and_revenue"]["training_path_count"] == 2
    assert report["tracks"]["workforce_and_revenue"]["subject_work_items"] == 3
    assert report["tracks"]["benchmarks"]["program_count"] == 1
    assert report["tracks"]["benchmarks"]["task_count"] == 2
    assert report["tracks"]["benchmarks"]["measured_count"] == 0
    assert report["tracks"]["cpu_25m_model"]["parameter_target"] == 25000000
    assert report["tracks"]["cpu_25m_model"]["training_enabled"] is False
    assert report["tracks"]["onet_task_index"]["status"] == "refresh_workflow_required"
    assert report["errors"] == []


def test_optional_complete_onet_task_index_is_reported(tmp_path: Path):
    _fixture(tmp_path)
    _write(tmp_path, "data/onet/onet-task-index.json", {
        "source": {"release_version": "31.0"},
        "inventory": {"complete": True},
        "tasks": [{"task_id": "1"}, {"task_id": "2"}]
    })
    report = audit(tmp_path)
    assert report["tracks"]["onet_task_index"]["complete"] is True
    assert report["tracks"]["onet_task_index"]["task_records"] == 2


def test_audit_fails_when_required_manifest_is_missing(tmp_path: Path):
    _fixture(tmp_path)
    (tmp_path / "config/masterbot-65-registry.json").unlink()
    report = audit(tmp_path)
    assert any("masterbot-65-registry.json" in error for error in report["errors"])
