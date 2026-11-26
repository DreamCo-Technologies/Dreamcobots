"""Rights-aware, complete routing coverage for the current FreeCodeCamp metadata snapshot."""
from pathlib import Path
import json
import unittest

from buddy.learning.course_track_registry import load_course_lessons, resources_for_division, resources_for_masterbot

ROOT = Path(__file__).resolve().parents[1]


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def routed_video_ids(catalog, routing):
    specialist_ids = {str(row.get("video_id")) for row in routing.get("entries", [])}
    for video in catalog.get("videos", []):
        searchable = f"{video.get('title', '')} {video.get('description', '')}".casefold()
        categories = {str(value).casefold() for value in video.get("categories", [])}
        if any(
            any(str(term).casefold() in searchable for term in rule.get("match_title_terms", []))
            or bool(categories.intersection(str(value).casefold() for value in rule.get("match_categories", [])))
            for rule in routing.get("routing_rules", [])
        ):
            specialist_ids.add(str(video["video_id"]))
    triage_ids = {
        str(video["video_id"]) for video in catalog.get("videos", [])
        if {str(value).casefold() for value in video.get("categories", [])} == {"other_or_unclassified"}
        and str(video["video_id"]) not in specialist_ids
    }
    return specialist_ids, triage_ids


class FreeCodeCampSpecialistRoutingTests(unittest.TestCase):
    def setUp(self):
        self.catalog = load("buddy/bootcamp/sources/freecodecamp/catalog.json")
        self.routing = load("config/freecodecamp-division-routing-overrides.json")
        self.lessons = load_course_lessons()
        self.specialist_ids, self.triage_ids = routed_video_ids(self.catalog, self.routing)

    def test_every_video_has_one_specialist_authoring_or_metadata_triage_record(self):
        all_ids = {str(row["video_id"]) for row in self.catalog["videos"]}
        specialist = {
            row.source_video_id for row in self.lessons
            if row.track_id == "freecodecamp-specialist-learning-paths"
        }
        triage = {
            row.source_video_id for row in self.lessons
            if row.track_id == "freecodecamp-metadata-triage"
        }
        self.assertFalse(specialist.intersection(triage))
        self.assertEqual(specialist, self.specialist_ids)
        self.assertEqual(triage, self.triage_ids)
        self.assertEqual(specialist.union(triage), all_ids)

    def test_only_explicitly_curated_videos_are_original_implementation_briefs(self):
        curated_ids = {str(row["video_id"]) for row in self.routing.get("entries", [])}
        specialist = [
            row for row in self.lessons
            if row.track_id == "freecodecamp-specialist-learning-paths"
        ]
        briefs = [row for row in specialist if row.content_status == "original_implementation_brief"]
        backlog = [row for row in specialist if row.content_status == "authoring_backlog"]
        self.assertEqual({row.source_video_id for row in briefs}, curated_ids)
        self.assertEqual(len(briefs), len(curated_ids))
        self.assertEqual(len(specialist), len(self.specialist_ids))
        self.assertEqual(len(backlog), len(specialist) - len(curated_ids))
        self.assertTrue(all(row.implementation_steps and row.buddy_demo for row in specialist))
        self.assertTrue(all(row.source_video_id and row.division_targets and row.masterbot_targets for row in specialist))
        self.assertTrue(all(row.rights_mode == "original_dreamco_learning_path_video_metadata_reference_only" for row in briefs))
        self.assertTrue(all(row.rights_mode == "metadata_only_until_item_level_permissions" for row in backlog))
        self.assertTrue(all(not row.guide_path for row in specialist))
        # Authoring work is not study-ready curriculum and cannot award mastery.
        self.assertFalse(any(
            resource.title == row.title
            for resource in resources_for_division("DreamFinance")
            for row in specialist
        ))

    def test_unclassified_items_are_metadata_only_and_review_lane_scoped(self):
        triage = [
            row for row in self.lessons
            if row.track_id == "freecodecamp-metadata-triage"
        ]
        self.assertEqual({row.source_video_id for row in triage}, self.triage_ids)
        self.assertTrue(all(row.content_status == "metadata_only" for row in triage))
        self.assertTrue(all(row.rights_mode == "metadata_only_until_item_level_permissions" for row in triage))
        self.assertTrue(all(set(row.division_targets) == {"DreamEducation", "CommandCore"} for row in triage))
        self.assertTrue(all("DreamDiscovery" in row.masterbot_targets for row in triage))
        self.assertTrue(all(set(row.learning_modes) == {
            "metadata_review", "guided_classification", "rights_check", "human_review"
        } for row in triage))
        self.assertFalse(any(
            resource.title == row.title
            for resource in resources_for_division("DreamEducation")
            for row in triage
        ))
        self.assertFalse(any(
            resource.title == row.title
            for resource in resources_for_masterbot("DreamDiscovery")
            for row in triage
        ))

    def test_all_routing_targets_exist_in_canonical_registries(self):
        domains = {
            row["domain_name"]
            for row in load("config/generated/masterbot-55-domain-crosswalk.json")["domains"]
        }
        masterbots = {
            row["name"]
            for row in load("config/masterbot-65-registry.json")["divisions"]
        }
        routed = [
            row for row in self.lessons
            if row.track_id in {"freecodecamp-specialist-learning-paths", "freecodecamp-metadata-triage"}
        ]
        self.assertTrue(all(set(row.division_targets).issubset(domains) for row in routed))
        self.assertTrue(all(set(row.masterbot_targets).issubset(masterbots) for row in routed))


if __name__ == "__main__":
    unittest.main()
