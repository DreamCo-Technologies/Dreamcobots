from __future__ import annotations

import json
import unittest
from pathlib import Path

from buddy_os.integration.learning_os_connection_graph import BuddyConnectionGraph
from tools.build_buddy_learning_os_connection_graph import CATEGORIES, build_graph, render

ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "config/generated/buddy-learning-os-connections.json"
PUBLIC_GRAPH = ROOT / "website/data/buddy-learning-os-connections.json"


class BuddyLearningOSConnectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = json.loads(GRAPH.read_text(encoding="utf-8"))
        self.graph = BuddyConnectionGraph(self.payload, ROOT)

    def test_graph_is_current_and_public_copy_matches(self) -> None:
        graph = build_graph()
        self.assertEqual(GRAPH.read_text(encoding="utf-8"), render(graph))
        self.assertEqual(PUBLIC_GRAPH.read_text(encoding="utf-8"), render(graph, public=True))

    def test_every_category_is_discoverable_and_every_node_is_linked(self) -> None:
        for category in CATEGORIES:
            self.assertTrue(self.graph.discover(category), category)
        self.assertEqual(self.graph.validate(), [])
        self.assertEqual(self.payload["summary"]["unlinked_node_count"], 0)

    def test_external_resources_are_not_falsely_reported_live(self) -> None:
        external = [node for node in self.payload["nodes"] if node["kind"] == "external_resource"]
        self.assertTrue(external)
        for node in external:
            if node["readiness"] != "runtime_verified":
                self.assertNotEqual(node["status"], "connected")

    def test_learning_sources_require_authorization_before_live_use(self) -> None:
        sources = [node for node in self.payload["nodes"] if node["kind"] == "learning_source_adapter"]
        self.assertGreaterEqual(len(sources), 10)
        self.assertTrue(any(node["id"] == "learning-source:apple_intelligence_video_exports" for node in sources))
        self.assertTrue(all(node["status"] == "partial" for node in sources))

    def test_referenced_study_and_competitor_sources_are_routed_but_not_activated(self) -> None:
        references = [node for node in self.payload["nodes"] if node["kind"] == "referenced_external_source"]
        self.assertGreaterEqual(len(references), 100)
        self.assertTrue(any(node["role"] == "competitor_or_baseline" for node in references))
        self.assertTrue(all(node["readiness"] == "terms_and_authorization_required" for node in references))

    def test_runtime_router_discovers_and_enforces_live_evidence(self) -> None:
        self.assertIn("learning", self.graph.route("learning")["categories"])
        with self.assertRaises(LookupError):
            self.graph.route("resources", require_runtime=True)


if __name__ == "__main__":
    unittest.main()
