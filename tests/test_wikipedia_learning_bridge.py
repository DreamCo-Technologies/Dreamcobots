import json
import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from buddy.learning.wikipedia_learning_bridge import (
    ROOT,
    _fetch_json,
    build_target_map,
    create_learning_event,
    search_wikipedia,
)


class WikipediaLearningBridgeTests(unittest.TestCase):
    def test_every_registered_goal_and_benchmark_gets_a_wikipedia_query(self):
        goals = json.loads((ROOT / "reports/goals_to_gates.json").read_text())
        benchmarks = json.loads((ROOT / "config/buddy-benchmark-task-registry.json").read_text())
        target_map = build_target_map(goals, benchmarks)
        self.assertEqual(target_map["goal_count"], len(goals["goals"]))
        self.assertEqual(target_map["benchmark_count"], len(benchmarks["tasks"]))
        self.assertTrue(all(row["wikipedia_search_url"].startswith("https://en.wikipedia.org/w/index.php?search=")
                            for row in target_map["goals"] + target_map["benchmarks"]))

    def test_search_is_read_only_cited_and_does_not_return_article_bodies(self):
        requests = []

        def fetch(url, timeout):
            requests.append((url, timeout))
            return {"pages": [{"key": "Artificial_intelligence", "title": "Artificial intelligence",
                               "description": "Intelligence demonstrated by machines", "excerpt": "ignored"}]}

        result = search_wikipedia("AI safety", fetch_json=fetch)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["source_family"], "wikipedia")
        self.assertEqual(result[0]["url"], "https://en.wikipedia.org/wiki/Artificial_intelligence")
        self.assertFalse(result[0]["body_stored"])
        self.assertNotIn("excerpt", result[0])
        self.assertEqual(parse_qs(urlparse(requests[0][0]).query)["q"], ["AI safety"])
        self.assertEqual(requests[0][1], 8)

    def test_benchmark_gap_flows_to_goal_and_practice_but_training_fails_closed(self):
        sources = [{"source_id": "wiki:abc", "source_family": "wikipedia",
                    "title": "Python", "url": "https://en.wikipedia.org/wiki/Python",
                    "license_status": "unknown", "terms_checked": False}]
        event = create_learning_event("software_engineering", {
            "benchmark_id": "python", "capability": "coding", "passed": False,
            "verified": True, "safety_passed": True,
        }, sources)
        self.assertEqual(event["goal_ids"], ["software_engineering"])
        self.assertEqual(event["wikipedia_source_ids"], ["wiki:abc"])
        self.assertEqual(event["recommended_next_step"], "review_cited_sources_then_create_original_sandbox_practice_and_retest")
        self.assertEqual(event["training_eligibility"], "blocked")
        self.assertIn("explicit_training_consent_or_evidence_missing", event["training_block_reasons"])
        self.assertFalse(event["raw_article_text_retained"])

    def test_training_candidate_requires_consent_rights_isolation_and_holdout(self):
        source = {"source_id": "wiki:abc", "source_family": "wikipedia",
                  "title": "Python", "url": "https://en.wikipedia.org/wiki/Python",
                  "revision_id": 123, "retrieved_at": "2026-11-03T12:00:00+00:00",
                  "content_hash": "sha256:abc", "license_status": "approved", "terms_checked": True}
        event = create_learning_event("software_engineering", {
            "benchmark_id": "python", "passed": True, "verified": True,
            "regression_passed": True, "safety_passed": True,
        }, [source], training_consent=True, isolated_training=True,
            holdout_verified=True, rights_reviewed=True,
            training_consent_ref="consent:owner-1", isolation_run_id="sandbox:train-1",
            holdout_evidence_ref="holdout:eval-1", rights_review_id="rights:review-1")
        self.assertEqual(event["training_eligibility"], "candidate_ready_for_review")
        self.assertEqual(event["recommended_next_step"], "regression_check_and_retest")
        self.assertEqual(event["wikipedia_source_refs"][0]["revision_id"], 123)

    def test_invalid_queries_and_non_wikipedia_sources_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "query must contain"):
            search_wikipedia("   ", fetch_json=lambda *_: {})
        with self.assertRaisesRegex(ValueError, "sources must be Wikipedia"):
            create_learning_event("g", {"passed": False}, [{"source_id": "x", "source_family": "other", "url": "https://example.com"}])
        with self.assertRaisesRegex(ValueError, "allowed host"):
            _fetch_json("https://example.com/redirect", 1)


if __name__ == "__main__":
    unittest.main()
