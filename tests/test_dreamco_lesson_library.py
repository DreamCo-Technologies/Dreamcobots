"""Contract tests for the original DreamCo lesson library and course links."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LESSON_PATH = ROOT / "data/dreamco_training/lessons/universal_task_mastery_lessons_v1.json"
COURSE_PATH = ROOT / "data/dreamco_training/courses/universal_task_mastery_v1.json"
CATALOG_PATH = ROOT / "data/dreamco_training/catalog.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_lesson_ids_are_unique_and_linked_to_course_modules():
    library = _load(LESSON_PATH)
    course = _load(COURSE_PATH)
    lessons = library["lessons"]
    ids = [lesson["lesson_id"] for lesson in lessons]
    linked = [lesson_id for module in course["modules"] for lesson_id in module["lesson_refs"]]
    assert len(ids) == len(set(ids))
    assert set(ids) == set(linked)
    assert len(course["modules"]) == 6


def test_every_lesson_has_instruction_practice_and_assessment():
    library = _load(LESSON_PATH)
    for lesson in library["lessons"]:
        assert lesson["learning_objectives"]
        assert len(lesson["lesson_text"]) >= 300, lesson["lesson_id"]
        assert lesson["worked_example"], lesson["lesson_id"]
        assert lesson["practice_task"], lesson["lesson_id"]
        assert lesson["common_failure_modes"], lesson["lesson_id"]
        assert lesson["assessment_rubric"], lesson["lesson_id"]
        assert lesson["content_provenance"], lesson["lesson_id"]


def test_unreviewed_lessons_cannot_become_training_data_or_certification():
    library = _load(LESSON_PATH)
    course = _load(COURSE_PATH)
    assert library["review_status"] == "draft_needs_independent_review"
    assert library["training_eligibility"] == "not_eligible_until_reviewed_and_split"
    assert course["certification_status"] == "not_certified"
    assert course["mastery_policy"]["require_unseen_transfer_task"] is True
    assert course["mastery_policy"]["require_regression_pass"] is True


def test_catalog_indexes_the_same_lesson_ids_and_review_state():
    library = _load(LESSON_PATH)
    catalog = _load(CATALOG_PATH)
    index = catalog["original_lesson_index"]
    assert {row["lesson_id"] for row in index} == {
        lesson["lesson_id"] for lesson in library["lessons"]
    }
    assert all(row["review_status"] == library["review_status"] for row in index)
    assert all(row["training_eligibility"] == library["training_eligibility"] for row in index)
    assert catalog["totals"]["dreamco_original_lesson_drafts"] == len(library["lessons"])
    assert catalog["totals"]["train_eligible_assets"] == 0
