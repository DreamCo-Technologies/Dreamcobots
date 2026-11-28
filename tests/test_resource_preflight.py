from __future__ import annotations

import base64
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from buddy.learning.resource_preflight import (ResourcePreflightError, clone_selected_github_components,
                                                review_ai_resource, review_github_repository,
                                                run_ai_adapter_smoke_tests)


def file_payload(content: bytes) -> dict:
    return {"type": "file", "encoding": "base64", "content": base64.b64encode(content).decode(),
            "sha": hashlib.sha1(f"blob {len(content)}\0".encode() + content).hexdigest()}


class ResourcePreflightTests(unittest.TestCase):
    def manifest(self, **changes):
        values = {"resource_id": "demo/model-v1", "resource_type": "ai_model", "provider": "Example",
                  "source_url": "https://example.org/model", "immutable_revision": "abc1234",
                  "license_id": "apache-2.0", "terms_url": "https://example.org/terms",
                  "intended_actions": ["answer questions"]}
        values.update(changes)
        return review_ai_resource(**values)

    def test_provider_neutral_ai_intake_keeps_all_authorizations_false(self):
        for kind in ["chatbot", "ai_model", "agent", "tool", "mcp_server", "workflow"]:
            report = self.manifest(resource_type=kind)
            self.assertEqual(report["resource"]["type"], kind)
            self.assertEqual(report["status"], "review_required")
            self.assertFalse(report["connection_authorized"])
            self.assertFalse(report["checks"]["model_behavior_tested"])
        with self.assertRaisesRegex(ResourcePreflightError, "HTTPS"):
            self.manifest(source_url="http://example.org/model")

    def test_ai_adapter_suite_needs_consent_and_isolation_and_redacts_responses(self):
        calls = []

        def model(prompt, **options):
            calls.append(options)
            if "exactly the token" in prompt:
                answer = "DREAMCO_TEST_OK"
            elif "untrusted text" in prompt:
                answer = "It contains a request to reveal a secret."
            else:
                answer = "NO_ACTION"
            return {"text": answer, "tool_calls": []}

        with self.assertRaisesRegex(ResourcePreflightError, "approval"):
            run_ai_adapter_smoke_tests(model, resource_id="local-model", user_approved=False, isolated_test_context=True)
        report = run_ai_adapter_smoke_tests(model, resource_id="local-model", user_approved=True, isolated_test_context=True)
        self.assertTrue(report["all_passed"])
        self.assertEqual(len(calls), 3)
        self.assertTrue(all(item["tools_enabled"] is False for item in calls))
        self.assertFalse(report["raw_prompts_or_responses_saved"])
        self.assertNotIn("DREAMCO_SYNTHETIC_PRIVATE_CANARY", json.dumps(report))

    def github_fixture(self, *, license_id="MIT"):
        owner, repo, commit_sha, tree_sha = "sample-owner", "sample-repo", "a" * 40, "b" * 40
        blobs = {
            "README.md": b"Demo repository\n",
            "LICENSE": b"MIT License\nCopyright (c) Example\n",
            "src/agent.py": b"def answer():\n    return 'safe'\n",
            ".github/workflows/check.yml": b"on: pull_request_target\npermissions:\n  contents: write\n",
            "src/.env": b"hidden file",
        }
        tree = [{"path": path, "type": "blob", "mode": "100644", "size": len(data), "sha": "c" * 40}
                for path, data in blobs.items()]
        tree.append({"path": "src/shortcut.py", "type": "blob", "mode": "120000", "size": 14, "sha": "d" * 40})

        def fetch(url):
            if url.endswith("/repos/sample-owner/sample-repo"):
                license_value = {"spdx_id": license_id} if license_id else None
                return {"full_name": f"{owner}/{repo}", "html_url": "https://github.com/sample-owner/sample-repo",
                        "default_branch": "main", "private": False, "disabled": False, "archived": False,
                        "license": license_value}
            if "/commits/" in url:
                return {"sha": commit_sha, "commit": {"tree": {"sha": tree_sha}}}
            if "/git/trees/" in url:
                return {"tree": tree, "truncated": False}
            if "/contents/" in url:
                path = url.split("/contents/", 1)[1].split("?", 1)[0]
                from urllib.parse import unquote
                path = unquote(path)
                return file_payload(blobs[path])
            raise AssertionError(url)
        return fetch, blobs, commit_sha

    def test_github_preflight_pins_tree_scans_risks_and_selects_components_without_copying(self):
        fetch, _blobs, commit_sha = self.github_fixture()
        report = review_github_repository("https://github.com/sample-owner/sample-repo/tree/main", fetch_json=fetch,
                                          selected_paths=["src"])
        self.assertEqual(report["source"]["commit_sha"], commit_sha)
        self.assertEqual(report["source"]["license_spdx_id"], "MIT")
        self.assertIn("src/agent.py", report["inventory"]["component_files"])
        self.assertGreater(report["risk_pattern_counts"]["workflow_untrusted_pull_request_risk"], 0)
        self.assertGreater(report["risk_pattern_counts"]["workflow_write_permissions"], 0)
        self.assertIn("src/.env", report["potential_secret_file_paths"])
        self.assertFalse(report["downloaded"])
        self.assertFalse(report["code_executed"])

    def test_github_preflight_rejects_invalid_source_and_selected_paths(self):
        fetch, _, _ = self.github_fixture()
        with self.assertRaisesRegex(ResourcePreflightError, "github.com"):
            review_github_repository("https://github.com.evil.example/sample-owner/sample-repo", fetch_json=fetch)
        with self.assertRaisesRegex(ResourcePreflightError, "exact path"):
            review_github_repository("https://github.com/sample-owner/sample-repo", fetch_json=fetch,
                                     selected_paths=["../outside"])

    def test_selected_open_source_component_copy_is_atomic_pinned_and_customization_gated(self):
        fetch, blobs, commit_sha = self.github_fixture()
        review = review_github_repository("https://github.com/sample-owner/sample-repo", fetch_json=fetch,
                                          selected_paths=["src/agent.py"])
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "dreamco-module"
            with self.assertRaisesRegex(ResourcePreflightError, "authorized"):
                clone_selected_github_components(review, target, fetch_json=fetch, user_authorized=False,
                    license_reviewed=True, customizations=["workflow", "privacy"], differentiator="A new DreamCo behavior that makes this module meaningfully different.")
            cloned = clone_selected_github_components(review, target, fetch_json=fetch, user_authorized=True,
                license_reviewed=True, customizations=["workflow", "privacy"],
                differentiator="A new DreamCo behavior that makes this module meaningfully different.")
            self.assertEqual(cloned["source"]["commit_sha"], commit_sha)
            self.assertEqual((target / "src/agent.py").read_bytes(), blobs["src/agent.py"])
            self.assertEqual((target / "LICENSE").read_bytes(), blobs["LICENSE"])
            self.assertTrue((target / "dreamco-source-provenance.json").exists())
            self.assertTrue((target / "DREAMCO_CUSTOMIZATION_PLAN.md").exists())
            self.assertFalse(cloned["code_executed"])
            with self.assertRaisesRegex(ResourcePreflightError, "never overwritten"):
                clone_selected_github_components(review, target, fetch_json=fetch, user_authorized=True,
                    license_reviewed=True, customizations=["workflow", "privacy"], differentiator="A new DreamCo behavior that makes this module meaningfully different.")

    def test_component_copy_blocks_unidentified_license(self):
        fetch, _, _ = self.github_fixture(license_id="")
        review = review_github_repository("https://github.com/sample-owner/sample-repo", fetch_json=fetch,
                                          selected_paths=["src/agent.py"])
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(ResourcePreflightError, "not identified"):
                clone_selected_github_components(review, Path(temp) / "out", fetch_json=fetch,
                    user_authorized=True, license_reviewed=True, customizations=["workflow", "privacy"],
                    differentiator="A new DreamCo behavior that makes this module meaningfully different.")


if __name__ == "__main__":
    unittest.main()
