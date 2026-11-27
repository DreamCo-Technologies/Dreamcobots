from __future__ import annotations

import io
import json
import tempfile
import unittest
from pathlib import Path

from buddy.learning.library_registry_discovery import search_public_registry


class LibraryRegistryDiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "config").mkdir()
        config = {
            "schema": "dreamco.buddy_library_registry_adapters.v1",
            "timeout_seconds": 5,
            "max_response_bytes": 4096,
            "providers": [{
                "id": "npm", "kind": "package_search",
                "endpoint": "https://registry.npmjs.org/-/v1/search",
                "host": "registry.npmjs.org", "query_parameter": "text",
                "page_parameter": "from", "page_size_parameter": "size",
                "parser": "npm", "supports_pagination": True,
            }, {
                "id": "maven-central", "kind": "package_search",
                "endpoint": "https://search.maven.org/solrsearch/select",
                "host": "search.maven.org", "query_parameter": "q",
                "page_parameter": "start", "page_size_parameter": "rows",
                "parser": "maven", "supports_pagination": True,
            }, {
                "id": "metacpan", "kind": "package_search",
                "endpoint": "https://fastapi.metacpan.org/v1/release/_search",
                "host": "fastapi.metacpan.org", "query_parameter": "q",
                "page_parameter": "from", "page_size_parameter": "size",
                "parser": "metacpan", "supports_pagination": True,
            }],
        }
        (self.root / "config/buddy-library-registry-adapters.json").write_text(json.dumps(config), encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_network_is_disabled_without_explicit_approval(self):
        with self.assertRaises(PermissionError):
            search_public_registry("npm", "react", root=self.root)

    def test_normalizes_metadata_and_never_grants_download_or_training(self):
        payload = {
            "objects": [{
                "package": {
                    "name": "react", "version": "19.0.0", "description": "UI library",
                    "links": {"npm": "https://www.npmjs.com/package/react", "repository": "https://github.com/facebook/react"},
                }
            }]
        }
        captured = {}
        def opener(request, timeout):
            captured["url"] = request.full_url
            captured["timeout"] = timeout
            captured["agent"] = request.get_header("User-agent")
            return io.BytesIO(json.dumps(payload).encode("utf-8"))
        result = search_public_registry("npm", "react", allow_network=True, root=self.root, opener=opener)
        self.assertEqual(result["candidates"][0]["name"], "react")
        self.assertFalse(result["candidates"][0]["download_authorized"])
        self.assertFalse(result["candidates"][0]["execution_authorized"])
        self.assertEqual(result["candidates"][0]["training_permission"], "pending")
        self.assertIn("text=react", captured["url"])
        self.assertEqual(captured["timeout"], 5)
        self.assertIn("DreamCo-Buddy", captured["agent"])

    def test_maven_central_normalizes_coordinates_and_uses_zero_based_pagination(self):
        payload = {"response": {"docs": [{
            "id": "org.example:demo-client", "g": "org.example", "a": "demo-client",
            "latestVersion": "4.2.1", "p": "jar", "versionCount": 12,
        }]}}
        captured = {}
        def opener(request, timeout):
            captured["url"] = request.full_url
            return io.BytesIO(json.dumps(payload).encode("utf-8"))
        result = search_public_registry(
            "maven-central", "http client", allow_network=True, page=2, limit=10,
            root=self.root, opener=opener,
        )
        candidate = result["candidates"][0]
        self.assertEqual(candidate["name"], "org.example:demo-client")
        self.assertEqual(candidate["group"], "org.example")
        self.assertEqual(candidate["artifact"], "demo-client")
        self.assertEqual(candidate["version"], "4.2.1")
        self.assertFalse(candidate["download_authorized"])
        self.assertEqual(candidate["training_permission"], "pending")
        self.assertIn("start=20", captured["url"])
        self.assertIn("rows=10", captured["url"])
        self.assertIn("wt=json", captured["url"])
        self.assertIsNone(result["next_page"])

    def test_metacpan_normalizes_release_metadata_and_uses_offset_pagination(self):
        payload = {"hits": {"hits": [{
            "_source": {
                "distribution": "HTTP-Message", "version": "7.00",
                "abstract": "HTTP message parsing and construction.",
                "resources": {
                    "homepage": "https://metacpan.org/pod/HTTP::Message",
                    "repository": {"url": "https://github.com/libwww-perl/HTTP-Message"},
                },
                "license": ["perl_5"], "author": "OALDERS", "date": "2026-10-01",
            }
        }]}}
        captured = {}
        def opener(request, timeout):
            captured["url"] = request.full_url
            return io.BytesIO(json.dumps(payload).encode("utf-8"))
        result = search_public_registry(
            "metacpan", "HTTP", allow_network=True, page=2, limit=10,
            root=self.root, opener=opener,
        )
        candidate = result["candidates"][0]
        self.assertEqual(candidate["name"], "HTTP-Message")
        self.assertEqual(candidate["version"], "7.00")
        self.assertEqual(candidate["license"], ["perl_5"])
        self.assertEqual(candidate["repository"], "https://github.com/libwww-perl/HTTP-Message")
        self.assertFalse(candidate["download_authorized"])
        self.assertEqual(candidate["training_permission"], "pending")
        self.assertIn("from=20", captured["url"])
        self.assertIn("size=10", captured["url"])
        self.assertIn("status%3Alatest", captured["url"])
        self.assertIn("HTTP", captured["url"])
        self.assertIsNone(result["next_page"])

    def test_rejects_unknown_provider_and_invalid_query(self):
        with self.assertRaises(ValueError):
            search_public_registry("missing", "x", allow_network=True, root=self.root)
        with self.assertRaises(ValueError):
            search_public_registry("npm", " ", allow_network=True, root=self.root)

    def test_rejects_oversized_registry_response(self):
        def opener(request, timeout):
            return io.BytesIO(b"x" * 4097)
        with self.assertRaises(ValueError):
            search_public_registry("npm", "react", allow_network=True, root=self.root, opener=opener)


if __name__ == "__main__":
    unittest.main()
