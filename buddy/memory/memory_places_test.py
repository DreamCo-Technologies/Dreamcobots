#!/usr/bin/env python3
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import memory_places as mp


class MemoryPlacesTests(unittest.TestCase):
    def test_six_places(self) -> None:
        ids = [p["id"] for p in mp.list_places()]
        self.assertGreaterEqual(len(ids), 6)
        self.assertIn("this_computer", ids)
        self.assertIn("custom_folder", ids)

    def test_choose_and_remember(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            mp.choose("custom_folder", tmp)
            out = mp.remember("teach", "Ask for the downside first", bot="deal")
            self.assertTrue(out["saved"])
            notes = mp.read_memory()
            self.assertEqual(notes[-1]["text"], "Ask for the downside first")
            self.assertEqual(notes[-1]["kind"], "teach")
            self.assertTrue((Path(tmp) / "memory.jsonl").exists())

    def test_blocks_secrets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            mp.choose("custom_folder", tmp)
            with self.assertRaises(ValueError):
                mp.remember("learn", "api_key: sk-test")


if __name__ == "__main__":
    unittest.main()
