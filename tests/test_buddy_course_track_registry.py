from __future__ import annotations

import unittest

from buddy.learning.course_track_registry import (
    load_course_lessons,
    plan_next_for_division,
    resources_for_division,
    resources_for_masterbot,
)
from buddy.learning.study_resource_scheduler import Capability


class BuddyCourseTrackRegistryTests(unittest.TestCase):
    def test_all_tracks_are_exposed_as_ordered_course_lessons(self):
        lessons = load_course_lessons()
        from pathlib import Path
        import json
        root = Path(__file__).resolve().parents[1]
        def load(path):
            return json.loads((root / path).read_text(encoding="utf-8"))
        tol = load("config/buddy-tolkien-study-track.json")
        tok = load("config/buddy-tokenizer-training-curriculum.json")
        cpu = load("config/buddy-25m-cpu-llm-course.json")
        onet = load("config/buddy-onet-content-model-curriculum.json")
        hf_tasks = load("config/huggingface-task-taxonomy.json")
        fcc = load("config/freecodecamp-complete-learning-path.json")
        hf_full = load("config/buddy-huggingface-full-learning-map.json")
        fcc_catalog = load("buddy/bootcamp/sources/freecodecamp/catalog.json")
        fcc_overrides = load("config/freecodecamp-division-routing-overrides.json")
        library_ecosystems = load("config/library_ecosystems.json")
        library_seed_catalog = load("data/buddy-library-seed-catalog.json")
        workforce = load("config/buddy-workforce-entrepreneurship-bootcamp.json")
        benchmark_index = load("config/buddy-benchmark-index.json")
        benchmark_tasks = load("config/buddy-benchmark-task-registry.json")
        onet_task_index_path = root / "data/onet/onet-task-index.json"
        onet_task_count = 0
        if onet_task_index_path.is_file():
            onet_task_index = load("data/onet/onet-task-index.json")
            if onet_task_index.get("inventory", {}).get("complete") is True:
                onet_task_count = len(onet_task_index.get("tasks", []))
        specialist_entries = {str(row.get("video_id")) for row in fcc_overrides.get("entries", [])}
        specialist_rules = fcc_overrides.get("routing_rules", [])
        specialist_video_ids = set()
        for video in fcc_catalog["videos"]:
            searchable = f"{video.get('title', '')} {video.get('description', '')}".casefold()
            categories = {str(value).casefold() for value in video.get("categories", [])}
            if str(video.get("video_id")) in specialist_entries or any(
                any(str(term).casefold() in searchable for term in rule.get("match_title_terms", []))
                or bool(categories.intersection(str(value).casefold() for value in rule.get("match_categories", [])))
                for rule in specialist_rules
            ):
                specialist_video_ids.add(str(video["video_id"]))
        specialist_paths = [
            lesson for lesson in lessons if lesson.track_id == "freecodecamp-specialist-learning-paths"
        ]
        triage_video_ids = {
            str(video["video_id"]) for video in fcc_catalog["videos"]
            if {str(value).casefold() for value in video.get("categories", [])} == {"other_or_unclassified"}
            and str(video["video_id"]) not in specialist_video_ids
        }
        expected_count = (
            len(tol["curriculum"]) + len(tol["extended_study_path"])
            + len(tok["lessons"]) + len(cpu["modules"]) + len(onet["subject_inventory"]) + onet_task_count
            + len(hf_tasks["task_families"])
            + len(fcc["official_platform_inventory"]["core_certifications"])
            + len(fcc["official_platform_inventory"]["additional_certifications"])
            + len(fcc["official_platform_inventory"]["curriculum_primitives"]) + 1
            + len(fcc["study_sequence"]) + len(fcc["video_learning_tracks"])
            + len(hf_full["official_courses"]) + len(hf_full["ecosystem_modules"])
            + len(fcc_catalog["videos"])
            + len(library_ecosystems["ecosystems"])
            + len(library_seed_catalog["candidates"])
            + sum(len(path["subjects"]) for path in workforce["training_paths"])
            + len(benchmark_index["programs"]) + len(benchmark_tasks["tasks"])
            + len(specialist_video_ids) + len(triage_video_ids)
        )
        self.assertEqual(len(lessons), expected_count)
        fcc_lessons = [lesson for lesson in lessons if lesson.track_id == "freecodecamp"]
        self.assertTrue(any(lesson.lesson_id == "a2-english-for-developers" for lesson in fcc_lessons))
        self.assertTrue(any(lesson.lesson_id == "fcc-legacy-curriculum-inventory" for lesson in fcc_lessons))
        self.assertTrue(any(lesson.lesson_id == "fcc-primitive-workshops" for lesson in fcc_lessons))
        self.assertEqual(len({lesson.resource_id for lesson in lessons}), len(lessons))
        self.assertEqual(len({(lesson.track_id, lesson.lesson_id) for lesson in lessons}), len(lessons))
        expected = {"tolkien", "tokenizer", "cpu-first-llm", "onet", "hugging-face", "freecodecamp", "huggingface-full", "freecodecamp-video-catalog", "freecodecamp-specialist-learning-paths", "freecodecamp-metadata-triage", "universal-software-libraries", "workforce-entrepreneurship", "benchmark-guides"}
        self.assertEqual({lesson.track_id for lesson in lessons}, expected)


    def test_specialist_paths_are_original_authoring_backlog_not_study_ready(self):
        lessons = [
            lesson for lesson in load_course_lessons()
            if lesson.track_id == "freecodecamp-specialist-learning-paths"
        ]
        catalog = json.loads((ROOT / "buddy/bootcamp/sources/freecodecamp/catalog.json").read_text(encoding="utf-8"))
        routing = load("config/freecodecamp-division-routing-overrides.json")
        specialist_ids = {str(row.get("video_id")) for row in routing.get("entries", [])}
        for video in catalog["videos"]:
            searchable = f"{video.get('title', '')} {video.get('description', '')}".casefold()
            categories = {str(value).casefold() for value in video.get("categories", [])}
            if any(
                any(str(term).casefold() in searchable for term in rule.get("match_title_terms", []))
                or bool(categories.intersection(str(value).casefold() for value in rule.get("match_categories", [])))
                for rule in routing.get("routing_rules", [])
            ):
                specialist_ids.add(str(video["video_id"]))
        triage_count = sum(
            {str(value).casefold() for value in video.get("categories", [])} == {"other_or_unclassified"}
            and str(video["video_id"]) not in specialist_ids
            for video in catalog["videos"]
        )
        self.assertEqual(len(lessons), len(catalog["videos"]) - triage_count)
        self.assertTrue(all(lesson.content_status == "original_implementation_brief" for lesson in lessons))
        self.assertTrue(all(lesson.source_video_id for lesson in lessons))
        self.assertTrue(all(lesson.division_targets and lesson.masterbot_targets for lesson in lessons))
        self.assertTrue(all(lesson.implementation_steps and lesson.buddy_demo for lesson in lessons))
        self.assertFalse(any(
            resource.name == lesson.title
            for resource in resources_for_division("DreamAIInfra")
            for lesson in lessons
        ))


    def test_unclassified_videos_enter_metadata_triage_not_study_content(self):
        catalog = json.loads((ROOT / "buddy/bootcamp/sources/freecodecamp/catalog.json").read_text(encoding="utf-8"))
        routing = load("config/freecodecamp-division-routing-overrides.json")
        specialist_ids = {str(row.get("video_id")) for row in routing.get("entries", [])}
        for video in catalog["videos"]:
            searchable = f"{video.get('title', '')} {video.get('description', '')}".casefold()
            categories = {str(value).casefold() for value in video.get("categories", [])}
            if any(
                any(str(term).casefold() in searchable for term in rule.get("match_title_terms", []))
                or bool(categories.intersection(str(value).casefold() for value in rule.get("match_categories", [])))
                for rule in routing.get("routing_rules", [])
            ):
                specialist_ids.add(str(video["video_id"]))
        expected = {
            str(video["video_id"]) for video in catalog["videos"]
            if {str(value).casefold() for value in video.get("categories", [])} == {"other_or_unclassified"}
            and str(video["video_id"]) not in specialist_ids
        }
        triage = [
            lesson for lesson in load_course_lessons()
            if lesson.track_id == "freecodecamp-metadata-triage"
        ]
        self.assertEqual({lesson.source_video_id for lesson in triage}, expected)
        self.assertTrue(all(lesson.content_status == "metadata_only" for lesson in triage))
        self.assertTrue(all(lesson.rights_mode == "metadata_only_until_item_level_permissions" for lesson in triage))
        self.assertTrue(all(lesson.implementation_steps and lesson.buddy_demo for lesson in triage))
        self.assertTrue(all(lesson.division_targets and lesson.masterbot_targets for lesson in triage))
        self.assertTrue(all(set(lesson.division_targets) == {"DreamEducation", "CommandCore"} for lesson in triage))
        self.assertTrue(all("DreamDiscovery" in lesson.masterbot_targets for lesson in triage))
        self.assertFalse(any(
            resource.name == lesson.title
            for resource in resources_for_division("DreamEducation")
            for lesson in triage
        ))

    def test_every_video_is_in_a_specialist_path_or_metadata_triage(self):
        catalog = json.loads((ROOT / "buddy/bootcamp/sources/freecodecamp/catalog.json").read_text(encoding="utf-8"))
        all_ids = {str(video["video_id"]) for video in catalog["videos"]}
        specialist_ids = {
            lesson.source_video_id for lesson in load_course_lessons()
            if lesson.track_id == "freecodecamp-specialist-learning-paths"
        }
        triage_ids = {
            lesson.source_video_id for lesson in load_course_lessons()
            if lesson.track_id == "freecodecamp-metadata-triage"
        }
        self.assertFalse(specialist_ids.intersection(triage_ids))
        self.assertEqual(specialist_ids.union(triage_ids), all_ids)

    def test_every_canonical_division_receives_the_shared_course_queue(self):
        from pathlib import Path
        import json
        root = Path(__file__).resolve().parents[1]
        crosswalk = json.loads((root / "config/generated/masterbot-55-domain-crosswalk.json").read_text(encoding="utf-8"))
        expected = sum(lesson.content_status == "authored" for lesson in load_course_lessons())
        for row in crosswalk["domains"]:
            with self.subTest(division=row["domain_name"]):
                self.assertEqual(len(resources_for_division(row["domain_name"])), expected)

    def test_every_masterbot_lane_receives_shared_foundations(self):
        from pathlib import Path
        import json
        root = Path(__file__).resolve().parents[1]
        registry = json.loads((root / "config/masterbot-65-registry.json").read_text(encoding="utf-8"))
        expected = sum(lesson.content_status == "authored" for lesson in load_course_lessons())
        for row in registry["divisions"]:
            with self.subTest(masterbot=row["name"]):
                self.assertEqual(len(resources_for_masterbot(row["name"])), expected)

    def test_huggingface_full_map_includes_all_official_courses_and_ecosystem_modules(self):
        from pathlib import Path
        import json
        root = Path(__file__).resolve().parents[1]
        data = json.loads((root / "config/buddy-huggingface-full-learning-map.json").read_text(encoding="utf-8"))
        self.assertEqual(len(data["official_courses"]), 12)
        self.assertEqual(len(data["ecosystem_modules"]), 18)
        self.assertEqual(data["task_family_count"], 37)
        self.assertTrue(any(c["id"] == "hf-context-course" for c in data["official_courses"]))
        deep_rl = next(c for c in data["official_courses"] if c["id"] == "hf-deep-rl-course")
        self.assertEqual(deep_rl["status"], "available_low_maintenance")
        self.assertTrue(all(not c["training_data_authorized"] for c in data["official_courses"]))

    def test_freecodecamp_video_inventory_is_queued_but_truthfully_partial(self):
        from pathlib import Path
        import json
        root = Path(__file__).resolve().parents[1]
        catalog = json.loads((root / "buddy/bootcamp/sources/freecodecamp/catalog.json").read_text(encoding="utf-8"))
        self.assertEqual(catalog["video_count"], len(catalog["videos"]))
        self.assertEqual(catalog["inventory"]["observed_entry_count"], len(catalog["videos"]))
        expected_complete = (
            catalog["inventory"].get("expected_entry_count") == len(catalog["videos"])
            and catalog["inventory"].get("observed_entry_count") == len(catalog["videos"])
            and catalog["inventory"].get("null_entry_count") == 0
            and catalog["inventory"].get("duplicate_video_id_count") == 0
        )
        self.assertEqual(catalog["inventory"]["complete"], expected_complete)
        self.assertEqual(catalog["inventory_status"], "complete" if expected_complete else "partial")
        lessons = [lesson for lesson in load_course_lessons() if lesson.track_id == "freecodecamp-video-catalog"]
        self.assertEqual(len(lessons), len(catalog["videos"]))
        self.assertTrue(all(lesson.rights_mode == "metadata_only_until_item_level_permissions" for lesson in lessons))
        self.assertTrue(all(lesson.source_url.startswith("https://www.youtube.com/watch?v=") for lesson in lessons))
        self.assertTrue(all(lesson.content_status == "metadata_only" for lesson in lessons))
        video_titles = {lesson.title for lesson in lessons}
        self.assertFalse(any(resource.name in video_titles for resource in resources_for_division("DreamAIInfra")))

    def test_course_scheduler_returns_queued_lesson_not_mastery(self):
        from pathlib import Path
        root = Path(__file__).resolve().parents[1]
        plan = plan_next_for_division(
            "DreamAIInfra",
            [Capability("LLM architecture", "ai_ml", score=0.1, failed_benchmarks=2)],
            root,
        )
        self.assertIsNotNone(plan)
        self.assertEqual(plan["completion_status"], "queued_not_studied")
        self.assertFalse(plan["mastery_awarded"])
        self.assertFalse(plan["model_weight_training_authorized"])
        self.assertFalse(plan["paid_compute_authorized"])
        self.assertTrue(plan["assessment"])
        self.assertTrue(plan["benchmark"])


    def test_workforce_paths_are_visible_as_authoring_backlog_not_study_material(self):
        lessons = [lesson for lesson in load_course_lessons() if lesson.track_id == "workforce-entrepreneurship"]
        self.assertGreater(len(lessons), 100)
        self.assertTrue(all(lesson.content_status == "authoring_backlog" for lesson in lessons))
        self.assertTrue(all("author" in lesson.objective.lower() for lesson in lessons))
        self.assertFalse(any(
            resource.name == lesson.title
            for resource in resources_for_division("DreamAIInfra")
            for lesson in lessons
        ))



    def test_onet_subject_and_task_outlines_are_authoring_backlog(self):
        lessons = [lesson for lesson in load_course_lessons() if lesson.track_id == "onet"]
        self.assertTrue(lessons)
        self.assertTrue(all(lesson.content_status == "authoring_backlog" for lesson in lessons))
        lesson_titles = {lesson.title for lesson in lessons}
        self.assertFalse(any(resource.name in lesson_titles
                             for resource in resources_for_division("DreamAIInfra")))

    def test_benchmark_programs_and_tasks_are_internal_authoring_backlog(self):
        lessons = [lesson for lesson in load_course_lessons() if lesson.track_id == "benchmark-guides"]
        self.assertEqual(len(lessons), 13 + 11)
        self.assertTrue(all(lesson.content_status == "authoring_backlog" for lesson in lessons))
        self.assertTrue(all("benchmark" in lesson.objective.lower() for lesson in lessons))
        self.assertFalse(any(resource.name == lesson.title
                             for resource in resources_for_division("DreamAIInfra")
                             for lesson in lessons))

    def test_unknown_division_is_rejected(self):
        with self.assertRaises(ValueError):
            resources_for_division("not-a-canonical-division")


if __name__ == "__main__":
    unittest.main()
