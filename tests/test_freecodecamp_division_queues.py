import json
import unittest
from pathlib import Path
from tools.build_freecodecamp_division_queues import build_queues, validate


def crosswalk_fixture():
    core_names = ["DreamCyber", "DreamCodeLab", "DreamRealEstate"] + [f"DreamCore{i}" for i in range(4, 46)]
    supplemental_names = ["DreamFood"] + [f"DreamSupplemental{i}" for i in range(2, 11)]
    domains = []
    for index, name in enumerate(core_names, 1):
        domains.append({"domain_id": name.casefold(), "domain_name": name, "masterbot_id": index,
                        "mapping_status": "proposed_exact_name_match", "review_required": True,
                        "owner_approval": None})
    for name in supplemental_names:
        domains.append({"domain_id": name.casefold(), "domain_name": name, "masterbot_id": None,
                        "mapping_status": "unresolved", "review_required": True, "owner_approval": None})
    return {"domains": domains}


class FreeCodeCampDomainQueueTests(unittest.TestCase):
    def setUp(self):
        self.catalog = {
            "schema": "dreamco.freecodecamp_catalog.v1",
            "inventory_status": "complete",
            "inventory": {"enumerator": "yt-dlp", "enumerator_version": "2026.11.23",
                          "expected_entry_count": 3, "observed_entry_count": 3,
                          "null_entry_count": 0, "duplicate_video_id_count": 0,
                          "complete": True, "completeness_basis": "test fixture"},
            "rights_policy": {"media_download_enabled": False, "transcript_ingestion_enabled": False,
                              "model_training_requires_review": True},
            "categories": [{"id": x} for x in ["computer_science_and_fundamentals", "python_and_automation",
                "cybersecurity_and_privacy", "databases_and_sql", "javascript_and_typescript"]],
            "videos": [
                {"video_id": "a", "title": "Python foundations", "url": "https://www.youtube.com/watch?v=a",
                 "categories": ["python_and_automation"]},
                {"video_id": "b", "title": "Cybersecurity basics", "url": "https://www.youtube.com/watch?v=b",
                 "categories": ["cybersecurity_and_privacy"]},
                {"video_id": "c", "title": "Computer science foundations", "url": "https://www.youtube.com/watch?v=c",
                 "categories": ["computer_science_and_fundamentals"]},
            ],
        }
        self.crosswalk = crosswalk_fixture()

    def test_builds_unique_queues_for_55_domains_not_65_masterbots(self):
        result = build_queues(self.catalog, self.crosswalk, limit=10)
        validate(result)
        self.assertEqual(result["domain_count"], 55)
        self.assertEqual(len(result["domains"]), 55)
        self.assertEqual(len({x["domain_id"] for x in result["domains"]}), 55)
        self.assertEqual(sum(x["mapping_status"] == "proposed_exact_name_match" for x in result["domains"]), 45)
        self.assertEqual(sum(x["mapping_status"] == "unresolved" for x in result["domains"]), 10)

    def test_real_repository_routes_all_45_core_domains_and_holds_10_unresolved(self):
        root = Path(__file__).resolve().parents[1]
        catalog = json.loads((root / "buddy/bootcamp/sources/freecodecamp/catalog.json").read_text(encoding="utf-8"))
        crosswalk = json.loads((root / "config/generated/masterbot-55-domain-crosswalk.json").read_text(encoding="utf-8"))
        result = build_queues(catalog, crosswalk, limit=30, allow_partial=True)
        validate(result)

        core = [row for row in result["domains"] if row["mapping_status"] == "proposed_exact_name_match"]
        unresolved = [row for row in result["domains"] if row["mapping_status"] == "unresolved"]
        self.assertEqual(len(core), 45)
        self.assertTrue(all(row["target_categories"] for row in core))
        self.assertTrue(all(row["queue_status"] == "subject_routed" for row in core))
        self.assertEqual(len(unresolved), 10)
        self.assertTrue(all(not row["target_categories"] for row in unresolved))
        self.assertTrue(all(row["queue_status"] == "foundation_only_owner_mapping_pending" for row in unresolved))

    def test_domain_hints_route_specialist_content(self):
        result = build_queues(self.catalog, self.crosswalk, limit=10)
        cyber = next(x for x in result["domains"] if x["domain_name"] == "DreamCyber")
        self.assertIn("cybersecurity_and_privacy", cyber["target_categories"])
        self.assertTrue(any("cybersecurity_and_privacy" in x["categories"] for x in cyber["items"]))

    def test_unassigned_supplemental_domain_keeps_owner_review_pending(self):
        result = build_queues(self.catalog, self.crosswalk, limit=10)
        food = next(x for x in result["domains"] if x["domain_name"] == "DreamFood")
        self.assertEqual(food["mapping_status"], "unresolved")
        self.assertIsNone(food["masterbot_id"])
        self.assertTrue(food["owner_review_required"])
        self.assertTrue(all(x["assignment_status"] == "queued_not_studied" for x in food["items"]))

    def test_camel_case_domain_name_routes_real_estate_specialty(self):
        result = build_queues(self.catalog, self.crosswalk, limit=10)
        estate = next(x for x in result["domains"] if x["domain_name"] == "DreamRealEstate")
        self.assertIn("databases_and_sql", estate["target_categories"])
        self.assertEqual(estate["queue_status"], "subject_routed")

    def test_partial_catalog_cannot_create_domain_queues(self):
        catalog = dict(self.catalog)
        catalog["inventory_status"] = "partial"
        catalog["inventory"] = {**self.catalog["inventory"], "complete": False}
        with self.assertRaisesRegex(ValueError, "verified complete freeCodeCamp inventory required"):
            build_queues(catalog, self.crosswalk, limit=10)

    def test_no_queue_item_is_authorized_for_training_or_media_ingestion(self):
        result = build_queues(self.catalog, self.crosswalk, limit=10)
        for domain in result["domains"]:
            for item in domain["items"]:
                self.assertFalse(item["training_eligible"])
                self.assertFalse(item["media_download_allowed"])
                self.assertFalse(item["transcript_ingestion_allowed"])
                self.assertEqual(item["rights_status"], "review_required")

    def test_rejects_wrong_domain_count_and_claims_of_learning(self):
        with self.assertRaisesRegex(ValueError, "55-domain"):
            build_queues(self.catalog, {"domains": self.crosswalk["domains"][:54]})
        result = build_queues(self.catalog, self.crosswalk, limit=10)
        result["domains"][0]["items"][0]["assignment_status"] = "mastered"
        with self.assertRaisesRegex(ValueError, "cannot claim study"):
            validate(result)


    def test_partial_catalog_can_create_explicitly_provisional_queues(self):
        catalog = dict(self.catalog)
        catalog["inventory_status"] = "partial"
        catalog["inventory"] = {
            **self.catalog["inventory"],
            "expected_entry_count": None,
            "complete": False,
            "completeness_basis": "partial fixture; full archive not verified",
        }
        result = build_queues(catalog, self.crosswalk, limit=10, allow_partial=True)
        validate(result)
        self.assertEqual(result["queue_mode"], "provisional_partial_inventory")
        self.assertEqual(result["source_inventory_status"], "partial")
        self.assertIn("full historical freeCodeCamp video archive is not verified", result["coverage_warning"])
        self.assertEqual(result["domain_count"], 55)
        self.assertTrue(all(item["assignment_status"] == "queued_not_studied"
                            for domain in result["domains"] for item in domain["items"]))

    def test_partial_mode_does_not_allow_duplicate_or_missing_observed_rows(self):
        catalog = dict(self.catalog)
        catalog["inventory_status"] = "partial"
        catalog["inventory"] = {
            **self.catalog["inventory"],
            "expected_entry_count": None,
            "complete": False,
            "observed_entry_count": 2,
        }
        with self.assertRaisesRegex(ValueError, "verified complete freeCodeCamp inventory required") as raised:
            build_queues(catalog, self.crosswalk, limit=10, allow_partial=True)
        self.assertIn("provisional queue", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
