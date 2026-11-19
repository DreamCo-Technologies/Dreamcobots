"""Tests for Buddy's open-vocabulary technology radar."""
import json
import unittest
from pathlib import Path
from tools.refresh_buddy_technology_radar import extract_source, merge_catalog, normalize_item, parse_feed, validate_catalog, validate_policy

ROOT = Path(__file__).resolve().parents[1]
POLICY = json.loads((ROOT / "config/buddy/technology-discovery-policy.json").read_text(encoding="utf-8"))

class BuddyTechnologyRadarTests(unittest.TestCase):
    def test_source_registry_and_seed_catalog_are_valid(self):
        validate_policy(POLICY)
        catalog = json.loads((ROOT / "config/generated/buddy-technology-radar.json").read_text(encoding="utf-8"))
        validate_catalog(catalog)
        self.assertEqual(catalog["summary"]["sources_pending"], len(catalog["source_runs"]))
        self.assertTrue(all(run["status"] in {"seeded_from_web_search", "not_yet_checked"} for run in catalog["source_runs"]))

    def test_feed_parser_accepts_rss_and_atom(self):
        rss = b"""<rss><channel><item><title>New AI coding agent</title><link>https://example.com/a</link><description>Build software with agents</description><pubDate>Sun, 08 Nov 2026 12:00:00 GMT</pubDate></item></channel></rss>"""
        atom = b"""<feed xmlns='http://www.w3.org/2005/Atom'><entry><title>Remote work AI</title><link href='https://example.com/b'/><summary>Work from home with AI</summary><updated>2026-11-08T12:00:00Z</updated></entry></feed>"""
        self.assertEqual(parse_feed(rss)[0]["title"], "New AI coding agent")
        self.assertEqual(parse_feed(atom)[0]["url"], "https://example.com/b")

    def test_html_directory_sources_extract_title_and_description(self):
        source = {"id": "page", "name": "Example directory", "kind": "html_page", "url": "https://example.com", "record_kind": "tool_catalog"}
        content = b"<html><head><title>AI tools directory</title><meta name='description' content='Vibe coding and home business tools'></head></html>"
        rows = extract_source(source, content, "2026-11-08T00:00:00Z", POLICY)
        self.assertEqual(rows[0]["title"], "AI tools directory")
        self.assertIn("Vibe coding", rows[0]["summary"])

    def test_priority_lenses_are_discovered_without_fixed_category_count(self):
        source = {"id": "fixture", "name": "Fixture", "url": "https://example.com/feed", "trust_tier": "test"}
        record = normalize_item(source, {"title": "Vibe coding for a home business", "url": "https://example.com/post", "summary": "AI app builder for remote work and freelancers"}, "2026-11-08T12:00:00Z", POLICY)
        self.assertIn("vibe_coding", record["priority_lenses"])
        self.assertIn("home_business", record["priority_lenses"])
        self.assertIn("remote_work", record["priority_lenses"])
        self.assertIn("freelancing", record["priority_lenses"])

    def test_merge_preserves_history_and_marks_missing_records_stale(self):
        source = {"id": "feed"}
        old = {"id": "old", "source_id": "feed", "first_seen_at": "2026-11-01T00:00:00Z", "last_seen_at": "2026-11-01T00:00:00Z", "status": "active", "record_kind": "announcement", "priority_lenses": [], "evidence_class": "discovery_lead_not_verified", "verified_capability": False, "income_claim_verified": False}
        new = {"id": "new", "source_id": "feed", "first_seen_at": "2026-11-08T00:00:00Z", "last_seen_at": "2026-11-08T00:00:00Z", "status": "active", "record_kind": "research_paper", "priority_lenses": [], "evidence_class": "discovery_lead_not_verified", "verified_capability": False, "income_claim_verified": False}
        merged = merge_catalog({"records": [old]}, [new], [{"source_id": "feed", "status": "success"}], "2026-11-08T12:00:00Z")
        self.assertEqual({item["id"] for item in merged["records"]}, {"old", "new"})
        self.assertEqual(next(item for item in merged["records"] if item["id"] == "old")["status"], "stale_not_seen_in_latest_successful_refresh")

    def test_failed_source_does_not_mark_prior_records_stale(self):
        old = {"id": "old", "source_id": "feed", "status": "active", "record_kind": "announcement", "priority_lenses": []}
        merged = merge_catalog({"records": [old]}, [], [{"source_id": "feed", "status": "failed"}], "2026-11-08T12:00:00Z")
        self.assertEqual(merged["records"][0]["status"], "active")

    def test_counts_are_derived_and_no_fixed_ceiling_exists(self):
        self.assertIsNone(POLICY["catalog_policy"]["fixed_category_ceiling"])
        self.assertIsNone(POLICY["catalog_policy"]["fixed_item_ceiling"])
        self.assertTrue(POLICY["catalog_policy"]["new_sources_may_be_added_without_code_changes"])
        self.assertEqual(POLICY["catalog_policy"]["taxonomy_mode"], "open_vocabulary")
        self.assertTrue(POLICY["catalog_policy"]["never_delete_historical_observations"])

    def test_validation_rejects_unverified_capability_or_income_claims(self):
        bad = {
            "schema": "dreamco.buddy.technology_radar.v1",
            "records": [{"id": "x", "record_kind": "test", "priority_lenses": [], "evidence_class": "discovery_lead_not_verified", "verified_capability": True, "income_claim_verified": False, "status": "active"}],
            "source_runs": [],
            "summary": {"records_total": 1, "sources_total": 0, "sources_succeeded": 0, "sources_failed": 0, "sources_pending": 0, "records_by_kind": {"test": 1}, "records_by_status": {"active": 1}, "records_by_priority_lens": {}}
        }
        with self.assertRaises(ValueError):
            validate_catalog(bad)

if __name__ == "__main__":
    unittest.main()
