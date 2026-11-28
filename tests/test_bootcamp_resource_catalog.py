import unittest

from buddy.learning.bootcamp_resource_catalog import (
    build_bootcamp_plan,
    build_catalog,
    build_reconstruction_plan,
)


def sample_catalog():
    return build_catalog({"resources": [{
        "id": "resource:github.com", "host": "github.com", "primary_url": "https://github.com",
        "source_lists": ["config/open_source.json"], "connection_status": "connection_request_required",
    }]}, {"resources": []})


class BootcampResourceCatalogTests(unittest.TestCase):
    def test_catalog_categorizes_resources_and_adds_uninstalled_rea_reference(self):
        catalog = sample_catalog()
        self.assertEqual(catalog["resource_count"], 2)
        rea = next(row for row in catalog["resources"] if row["id"] == "project:rea_reverse_engineer_anything")
        self.assertEqual(rea["category"], "code_repositories_and_tools")
        self.assertEqual(rea["connection_status"], "not_installed_or_connected")
        self.assertFalse(rea["live_verified"])

    def test_users_can_select_resources_for_a_local_bootcamp_export(self):
        catalog = sample_catalog()
        plan = build_bootcamp_plan(catalog, ["Learn reverse engineering"], ["resource:github.com"])
        self.assertEqual(plan["selected_resources"][0]["id"], "resource:github.com")
        self.assertFalse(plan["training_enabled"])
        with self.assertRaisesRegex(ValueError, "selected resource ids"):
            build_bootcamp_plan(catalog, ["Build a skill"], ["resource:missing"])

    def test_reconstruction_is_blocked_until_authorized_and_customized(self):
        catalog = sample_catalog()
        tool = "project:rea_reverse_engineer_anything"
        target = "https://example.org/app"
        blocked = build_reconstruction_plan(target, [tool], catalog,
                                           owner_authorized=True, clean_room=True)
        self.assertEqual(blocked["status"], "blocked")
        self.assertIn("add_two_or_more_distinct_customizations_and_an_original_differentiator", blocked["blockers"])
        ready = build_reconstruction_plan(
            target, [tool], catalog, owner_authorized=True, clean_room=True,
            rea_reviewed=True,
            customization_choices=["workflow", "accessibility"],
            original_differentiator="Build an offline-first tutor with simple language and adjustable reading levels.",
        )
        self.assertEqual(ready["status"], "ready_for_authorized_review")
        self.assertFalse(ready["execution_started"])
        self.assertFalse(ready["source_code_copied"])

    def test_reconstruction_requires_https_and_known_customization_choices(self):
        catalog = sample_catalog()
        with self.assertRaisesRegex(ValueError, "HTTPS URL"):
            build_reconstruction_plan("http://example.org", [], catalog,
                                      owner_authorized=True, clean_room=True)
        with self.assertRaisesRegex(ValueError, "unknown customization choices"):
            build_reconstruction_plan(
                "https://example.org", ["project:rea_reverse_engineer_anything"], catalog,
                owner_authorized=True, clean_room=True, customization_choices=["copy_source"],
                rea_reviewed=True,
                original_differentiator="A distinct, original feature direction for this product.",
            )


if __name__ == "__main__":
    unittest.main()
