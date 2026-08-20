import unittest

from tools.buddy_source_learning_engine import Source, build_study_plan, classify_uri, make_chunks, dedupe_sources, score_source


class BuddySourceLearningEngineTests(unittest.TestCase):
    def test_classifies_common_sources(self):
        self.assertEqual(classify_uri("https://example.org/book.pdf"), "book")
        self.assertEqual(classify_uri("https://example.org/video.mp4"), "movie")
        self.assertEqual(classify_uri("https://example.org/data.json"), "database")
        self.assertEqual(classify_uri("https://github.com/DreamCo-Technologies/Dreamcobots"), "repo")

    def test_deduplicates_sources(self):
        source = Source("https://example.org/a", "website")
        self.assertEqual(len(dedupe_sources([source, source])), 1)

    def test_chunks_are_deterministic_and_overlap(self):
        source = Source("https://example.org/a", "website", license="CC")
        chunks = make_chunks(source, "a" * 500, chunk_size=200, overlap=20)
        self.assertGreater(len(chunks), 1)
        self.assertEqual(chunks[0].source_id, chunks[1].source_id)
        self.assertEqual(chunks[0].license, "CC")

    def test_authoritative_course_can_rank_high(self):
        source = Source("https://ocw.mit.edu/", "course", authority=1, relevance=1, freshness=.9, accessibility=1)
        self.assertGreater(score_source(source, "machine learning"), .7)

    def test_plan_contains_practice_and_mastery_requirements(self):
        source = Source("https://ocw.mit.edu/", "course", authority=1, relevance=1)
        plan = build_study_plan("machine learning", [source], ["ml-quality"])
        self.assertEqual(plan.benchmark_ids, ("ml-quality",))
        self.assertGreaterEqual(len(plan.practice_tasks), 5)
        self.assertIn("repeatable correctness threshold", plan.mastery_requirements)


if __name__ == "__main__":
    unittest.main()
