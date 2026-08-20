import unittest
from tools.buddy_knowledge_synthesis import Evidence, build_learning_artifact, synthesize


class BuddyKnowledgeSynthesisTests(unittest.TestCase):
    def test_synthesis_keeps_evidence(self):
        result = synthesize("machine learning", [Evidence("a", "Models learn patterns from data.", confidence=.9, citation="A")])
        self.assertEqual(len(result.claims), 1)
        self.assertEqual(len(result.evidence_ids), 1)

    def test_artifact_requires_independent_writing(self):
        result = build_learning_artifact("AI", [Evidence("a", "AI systems can optimize objectives.", citation="A")])
        self.assertTrue(result["rules"]["retain_provenance"])
        self.assertTrue(result["rules"]["write_independently"])
        self.assertTrue(result["rules"]["benchmark_unseen_tasks"])


if __name__ == "__main__":
    unittest.main()
