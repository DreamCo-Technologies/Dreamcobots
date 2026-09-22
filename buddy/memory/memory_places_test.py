#!/usr/bin/env python3
from __future__ import annotations

import tempfile
import unittest

import memory_places as mp


class MemoryPlacesTests(unittest.TestCase):
    def test_twenty_places(self) -> None:
        places = mp.list_places()
        self.assertEqual(len(places), 20)
        ids = [p["id"] for p in places]
        self.assertEqual(len(ids), len(set(ids)))
        for needed in ("google_drive", "google_cloud_storage", "icloud_drive", "apple_icloud", "dropbox", "onedrive"):
            self.assertIn(needed, ids)

    def test_choose_cloud_export(self) -> None:
        out = mp.choose("google_drive")
        self.assertEqual(out["place_id"], "google_drive")
        saved = mp.remember("teach", "Keep answers short", bot="buddy")
        self.assertTrue(saved["saved"])
        self.assertIn("Drive", saved["next"] + saved["place"])

    def test_blocks_secrets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            mp.choose("custom_folder", tmp)
            with self.assertRaises(ValueError):
                mp.remember("learn", "api_key: sk-test")


if __name__ == "__main__":
    unittest.main()
