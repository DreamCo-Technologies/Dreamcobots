#!/usr/bin/env python3
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from foundry.local_rag import Chunk, LocalRagStore  # noqa: E402
from foundry.lora_plan import plan  # noqa: E402
from tools.build_foundry_guides import main  # noqa: E402


class FoundryTest(unittest.TestCase):
    def test_rag_ranks_relevant_chunk(self):
        store = LocalRagStore()
        store.add(Chunk("1", "Qdrant is a vector database for filtered search.", "docs", "internal"))
        store.add(Chunk("2", "LoRA adapters keep most base weights frozen.", "docs", "internal"))
        hits = store.query("which vector database filters results", k=1)
        self.assertTrue(hits)
        self.assertIn("Qdrant", hits[0][1].text)

    def test_lora_plan_does_not_launch(self):
        payload = plan("pack.code", "qlora-sft", "meta-llama/Llama-3.1-8B-Instruct")
        self.assertFalse(payload["launch_in_ci"])
        self.assertEqual(main(), 0)


if __name__ == "__main__":
    unittest.main()
