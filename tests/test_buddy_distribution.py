from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dreamco_platform.launch import (
    BuddyDistributionService,
    DistributionBrief,
    DistributionError,
)
from tools.generate_buddy_distribution_catalog import CONFIG_OUT, WEB_OUT, build_catalog, stable_json


class BuddyDistributionTests(unittest.TestCase):
    def test_catalog_covers_device_store_and_service_families(self):
        catalog = build_catalog()
        self.assertEqual(catalog["summary"]["targets"], 26)
        self.assertEqual(catalog["summary"]["families"], 8)
        self.assertEqual(catalog["summary"]["services"], 7)
        self.assertEqual(catalog["summary"]["available_now"], 2)
        self.assertEqual(len({item["target_id"] for item in catalog["targets"]}), 26)
        self.assertEqual(len({item["service_id"] for item in catalog["service_packages"]}), 7)

    def test_builds_multi_platform_release_plan_without_external_action(self):
        plan = BuddyDistributionService().build_plan(DistributionBrief(
            owner_user_id="owner-1",
            project_name="Learning Worlds",
            product_type="game",
            target_ids=("pwa", "android", "apple_tv", "steam", "lms"),
            audience="teachers, students, and families",
            source_reference="repository:learning-worlds",
            rights_confirmed=True,
            targets_children=True,
        ))
        self.assertEqual(len(plan["targets"]), 5)
        self.assertTrue(plan["owner_account_required"])
        self.assertTrue(plan["provider_review_required"])
        self.assertTrue(plan["children_review_required"])
        self.assertFalse(plan["automatic_store_submission"])
        self.assertFalse(plan["automatic_payment"])
        self.assertFalse(plan["quote_generated"])
        self.assertIn("game_store_release", plan["matched_services"])
        self.assertIn("course_lms_delivery", plan["matched_services"])

    def test_rejects_unknown_duplicate_and_unlicensed_distribution(self):
        base = dict(
            owner_user_id="owner-1",
            project_name="Project One",
            product_type="web_app",
            target_ids=("pwa",),
            audience="small businesses",
            source_reference="repository:project-one",
            rights_confirmed=True,
        )
        with self.assertRaisesRegex(DistributionError, "Unknown"):
            BuddyDistributionService().build_plan(DistributionBrief(**{**base, "target_ids": ("unknown",)}))
        with self.assertRaisesRegex(DistributionError, "unique"):
            BuddyDistributionService().build_plan(DistributionBrief(**{**base, "target_ids": ("pwa", "pwa")}))
        with self.assertRaisesRegex(DistributionError, "rights"):
            BuddyDistributionService().build_plan(DistributionBrief(**{**base, "rights_confirmed": False}))

    def test_generated_catalog_and_public_install_contract_are_current(self):
        catalog = build_catalog()
        expected = stable_json(catalog)
        self.assertEqual(CONFIG_OUT.read_text(encoding="utf-8"), expected)
        self.assertEqual(WEB_OUT.read_text(encoding="utf-8"), expected)
        manifest = json.loads((ROOT / "website" / "manifest.webmanifest").read_text(encoding="utf-8"))
        self.assertEqual(manifest["id"], "./buddy.html")
        self.assertEqual({icon["sizes"] for icon in manifest["icons"]}, {"192x192", "512x512"})
        self.assertTrue(all((ROOT / "website" / icon["src"]).exists() for icon in manifest["icons"]))
        worker = (ROOT / "website" / "service-worker.js").read_text(encoding="utf-8")
        self.assertIn("./install.html", worker)
        self.assertIn("./buddy.html", worker)
        self.assertIn("self.addEventListener('fetch'", worker)


if __name__ == "__main__":
    unittest.main()
