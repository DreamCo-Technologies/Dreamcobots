"""Tests for bots/control_tower/control_tower.py"""
import json
import os
import sys
import tempfile
import unittest.mock as mock
from pathlib import Path

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest
from bots.control_tower.control_tower import (
    BotRegistrySync,
    GitHubRepoManager,
    HeartbeatClient,
    _http_get,
    _http_post,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def tmp_registry(tmp_path):
    """Temporary bots.json registry file."""
    registry_file = tmp_path / "bots.json"
    registry_file.write_text(json.dumps([]), encoding="utf-8")
    return str(registry_file)


@pytest.fixture()
def populated_registry(tmp_path):
    """Temporary registry with two pre-registered bots."""
    data = [
        {
            "name": "LeadBot",
            "repoName": "Dreamcobots",
            "repoPath": "./bots/lead",
            "branch": "main",
            "owner": "ireanjordan24",
            "status": "active",
            "tier": "pro",
            "heartbeatUrl": None,
            "lastHeartbeat": None,
            "lastPR": None,
            "openIssues": 0,
        },
        {
            "name": "RealEstateBot",
            "repoName": "Dreamcobots",
            "repoPath": "./bots/real_estate_bot",
            "branch": "main",
            "owner": "ireanjordan24",
            "status": "offline",
            "tier": "enterprise",
            "heartbeatUrl": None,
            "lastHeartbeat": None,
            "lastPR": None,
            "openIssues": 2,
        },
    ]
    registry_file = tmp_path / "bots.json"
    registry_file.write_text(json.dumps(data), encoding="utf-8")
    return str(registry_file)


# ---------------------------------------------------------------------------
# BotRegistrySync
# ---------------------------------------------------------------------------


class TestBotRegistrySync:
    def test_load_empty_registry(self, tmp_registry):
        sync = BotRegistrySync(registry_path=tmp_registry)
        assert sync.load() == []

    def test_register_new_bot(self, tmp_registry):
        sync = BotRegistrySync(registry_path=tmp_registry)
        entry = sync.register(
            name="TestBot",
            repo_name="Dreamcobots",
            owner="ireanjordan24",
            repo_path="./bots/test_bot",
            tier="pro",
        )
        assert entry["name"] == "TestBot"
        assert entry["repoName"] == "Dreamcobots"
        assert entry["tier"] == "pro"
        loaded = sync.load()
        assert len(loaded) == 1
        assert loaded[0]["name"] == "TestBot"

    def test_register_updates_existing_bot(self, populated_registry):
        sync = BotRegistrySync(registry_path=populated_registry)
        entry = sync.register(
            name="LeadBot",
            repo_name="Dreamcobots",
            owner="ireanjordan24",
            tier="enterprise",
        )
        assert entry["tier"] == "enterprise"
        loaded = sync.load()
        assert len(loaded) == 2  # still two bots, not three
        lead = next(b for b in loaded if b["name"] == "LeadBot")
        assert lead["tier"] == "enterprise"

    def test_get_existing_bot(self, populated_registry):
        sync = BotRegistrySync(registry_path=populated_registry)
        bot = sync.get("LeadBot")
        assert bot is not None
        assert bot["name"] == "LeadBot"

    def test_get_missing_bot_returns_none(self, populated_registry):
        sync = BotRegistrySync(registry_path=populated_registry)
        assert sync.get("NonExistentBot") is None

    def test_list_all_returns_all_bots(self, populated_registry):
        sync = BotRegistrySync(registry_path=populated_registry)
        bots = sync.list_all()
        assert len(bots) == 2
        names = {b["name"] for b in bots}
        assert names == {"LeadBot", "RealEstateBot"}

    def test_update_heartbeat_sets_timestamp(self, populated_registry):
        sync = BotRegistrySync(registry_path=populated_registry)
        result = sync.update_heartbeat("LeadBot", status="active")
        assert result is not None
        assert result["lastHeartbeat"] is not None
        assert result["status"] == "active"

    def test_update_heartbeat_unknown_bot_returns_none(self, populated_registry):
        sync = BotRegistrySync(registry_path=populated_registry)
        result = sync.update_heartbeat("GhostBot")
        assert result is None

    def test_update_heartbeat_persists_to_disk(self, populated_registry):
        sync = BotRegistrySync(registry_path=populated_registry)
        sync.update_heartbeat("RealEstateBot", status="active")
        reloaded = sync.load()
        real_estate = next(b for b in reloaded if b["name"] == "RealEstateBot")
        assert real_estate["lastHeartbeat"] is not None
        assert real_estate["status"] == "active"

    def test_load_handles_missing_file_gracefully(self, tmp_path):
        sync = BotRegistrySync(registry_path=str(tmp_path / "nonexistent.json"))
        assert sync.load() == []

    def test_load_handles_invalid_json_gracefully(self, tmp_path):
        bad_file = tmp_path / "bots.json"
        bad_file.write_text("not valid json", encoding="utf-8")
        sync = BotRegistrySync(registry_path=str(bad_file))
        assert sync.load() == []

    def test_register_multiple_bots(self, tmp_registry):
        sync = BotRegistrySync(registry_path=tmp_registry)
        for i in range(5):
            sync.register(name=f"Bot{i}", repo_name="Dreamcobots", owner="ireanjordan24")
        assert len(sync.load()) == 5

    def test_register_sets_default_status_active(self, tmp_registry):
        sync = BotRegistrySync(registry_path=tmp_registry)
        entry = sync.register(name="Alpha", repo_name="Dreamcobots", owner="ireanjordan24")
        assert entry["status"] == "active"

    def test_register_sets_default_branch_main(self, tmp_registry):
        sync = BotRegistrySync(registry_path=tmp_registry)
        entry = sync.register(name="Beta", repo_name="Dreamcobots", owner="ireanjordan24")
        assert entry["branch"] == "main"

    def test_save_and_reload(self, tmp_registry):
        sync = BotRegistrySync(registry_path=tmp_registry)
        sync.register(name="Gamma", repo_name="Dreamcobots", owner="ireanjordan24", tier="enterprise")
        sync2 = BotRegistrySync(registry_path=tmp_registry)
        assert sync2.get("Gamma")["tier"] == "enterprise"


# ---------------------------------------------------------------------------
# HeartbeatClient
# ---------------------------------------------------------------------------


class TestHeartbeatClient:
    def test_instantiates_with_default_url(self):
        client = HeartbeatClient()
        assert client is not None

    def test_instantiates_with_custom_url(self):
        client = HeartbeatClient(tower_url="http://custom:4000")
        assert client._url == "http://custom:4000"

    def test_tower_alive_returns_true_on_ok_response(self):
        client = HeartbeatClient(tower_url="http://tower:3001")
        with mock.patch(
            "bots.control_tower.control_tower._http_get",
            return_value={"status": "ok"},
        ):
            assert client.tower_alive() is True

    def test_tower_alive_returns_false_on_error(self):
        client = HeartbeatClient(tower_url="http://tower:3001")
        with mock.patch(
            "bots.control_tower.control_tower._http_get",
            return_value={"error": "connection refused"},
        ):
            assert client.tower_alive() is False

    def test_ping_sends_correct_payload(self):
        client = HeartbeatClient(tower_url="http://tower:3001")
        captured = {}

        def fake_post(url, data, token=""):
            captured["url"] = url
            captured["data"] = data
            return {"ok": True}

        with mock.patch("bots.control_tower.control_tower._http_post", side_effect=fake_post):
            client.ping("LeadBot", status="active", metadata={"version": "2.0"})

        assert "heartbeat" in captured["url"].lower()
        assert captured["data"]["bot"] == "LeadBot"
        assert captured["data"]["status"] == "active"
        assert captured["data"]["version"] == "2.0"
        assert "timestamp" in captured["data"]

    def test_ping_includes_timestamp(self):
        client = HeartbeatClient()
        received = {}

        def fake_post(url, data, token=""):
            received.update(data)
            return {}

        with mock.patch("bots.control_tower.control_tower._http_post", side_effect=fake_post):
            client.ping("TestBot")

        assert "timestamp" in received


# ---------------------------------------------------------------------------
# GitHubRepoManager
# ---------------------------------------------------------------------------


class TestGitHubRepoManager:
    def test_instantiates(self):
        mgr = GitHubRepoManager(token="fake-token")
        assert mgr is not None

    def test_get_open_prs_returns_list(self):
        mgr = GitHubRepoManager(token="fake-token")
        mock_prs = [
            {
                "number": 1,
                "title": "Fix bug",
                "user": {"login": "dev"},
                "head": {"ref": "fix-bug"},
                "created_at": "2024-01-01T00:00:00Z",
                "html_url": "https://github.com/test/repo/pull/1",
            }
        ]
        with mock.patch("bots.control_tower.control_tower._http_get", return_value=mock_prs):
            result = mgr.get_open_prs("owner", "repo")
        assert len(result) == 1
        assert result[0]["number"] == 1
        assert result[0]["title"] == "Fix bug"
        assert result[0]["author"] == "dev"

    def test_get_open_prs_filters_out_pull_requests_from_issues(self):
        mgr = GitHubRepoManager(token="fake-token")
        mock_issues = [
            {"number": 10, "title": "Issue A", "user": {"login": "user1"}, "labels": [], "html_url": "url1"},
            {"number": 11, "title": "PR B", "user": {"login": "user2"}, "labels": [], "html_url": "url2", "pull_request": {}},
        ]
        with mock.patch("bots.control_tower.control_tower._http_get", return_value=mock_issues):
            result = mgr.get_open_issues("owner", "repo")
        assert len(result) == 1
        assert result[0]["number"] == 10

    def test_get_latest_commit_returns_dict(self):
        mgr = GitHubRepoManager(token="fake-token")
        mock_commits = [
            {
                "sha": "abc1234567890",
                "commit": {
                    "message": "Initial commit\n\nMore details",
                    "author": {"name": "Alice", "date": "2024-01-01T00:00:00Z"},
                },
                "html_url": "https://github.com/test/repo/commit/abc1234",
            }
        ]
        with mock.patch("bots.control_tower.control_tower._http_get", return_value=mock_commits):
            result = mgr.get_latest_commit("owner", "repo")
        assert result is not None
        assert result["sha"] == "abc1234"  # truncated to 7 chars
        assert result["message"] == "Initial commit"
        assert result["author"] == "Alice"

    def test_get_latest_commit_returns_none_on_empty(self):
        mgr = GitHubRepoManager(token="fake-token")
        with mock.patch("bots.control_tower.control_tower._http_get", return_value=[]):
            result = mgr.get_latest_commit("owner", "repo")
        assert result is None

    def test_get_workflow_runs_returns_list(self):
        mgr = GitHubRepoManager(token="fake-token")
        mock_data = {
            "workflow_runs": [
                {
                    "id": 99,
                    "name": "CI",
                    "status": "completed",
                    "conclusion": "success",
                    "head_branch": "main",
                    "created_at": "2024-01-01T00:00:00Z",
                    "html_url": "https://github.com/actions/runs/99",
                }
            ]
        }
        with mock.patch("bots.control_tower.control_tower._http_get", return_value=mock_data):
            result = mgr.get_workflow_runs("owner", "repo")
        assert len(result) == 1
        assert result[0]["id"] == 99
        assert result[0]["conclusion"] == "success"

    def test_get_repo_status_returns_full_snapshot(self):
        mgr = GitHubRepoManager(token="fake-token")
        with mock.patch.object(mgr, "get_open_prs", return_value=[{"number": 1, "title": "PR"}]):
            with mock.patch.object(mgr, "get_open_issues", return_value=[]):
                with mock.patch.object(mgr, "get_latest_commit", return_value={"sha": "abc1234"}):
                    with mock.patch.object(mgr, "get_workflow_runs", return_value=[]):
                        status = mgr.get_repo_status("owner", "repo")

        assert status["owner"] == "owner"
        assert status["repo"] == "repo"
        assert status["summary"]["open_pr_count"] == 1
        assert status["summary"]["open_issue_count"] == 0
        assert "timestamp" in status

    def test_get_repo_status_detects_conflict_in_pr_title(self):
        mgr = GitHubRepoManager(token="fake-token")
        with mock.patch.object(mgr, "get_open_prs", return_value=[{"number": 2, "title": "Resolve conflict in main"}]):
            with mock.patch.object(mgr, "get_open_issues", return_value=[]):
                with mock.patch.object(mgr, "get_latest_commit", return_value=None):
                    with mock.patch.object(mgr, "get_workflow_runs", return_value=[]):
                        status = mgr.get_repo_status("owner", "repo")

        assert status["summary"]["has_conflicts"] is True

    def test_create_pull_request_calls_github_api(self):
        mgr = GitHubRepoManager(token="fake-token")
        mock_response = {"number": 42, "html_url": "https://github.com/pr/42", "title": "My PR", "head": {"ref": "feature"}}
        captured = {}

        def fake_post(url, data, token=""):
            captured["url"] = url
            captured["data"] = data
            return mock_response

        with mock.patch("bots.control_tower.control_tower._http_post", side_effect=fake_post):
            result = mgr.create_pull_request(
                owner="owner",
                repo="repo",
                title="My PR",
                head="feature",
                base="main",
                body="Auto-generated",
            )

        assert "pulls" in captured["url"]
        assert captured["data"]["title"] == "My PR"
        assert captured["data"]["head"] == "feature"
        assert result["number"] == 42

    def test_re_run_workflow_calls_correct_endpoint(self):
        mgr = GitHubRepoManager(token="fake-token")
        captured = {}

        def fake_post(url, data, token=""):
            captured["url"] = url
            return {"message": "ok"}

        with mock.patch("bots.control_tower.control_tower._http_post", side_effect=fake_post):
            mgr.re_run_workflow("owner", "repo", run_id=12345)

        assert "12345" in captured["url"]
        assert "rerun" in captured["url"]


# ---------------------------------------------------------------------------
# HTTP helpers (_http_get / _http_post) — network-isolated
# ---------------------------------------------------------------------------


class TestHttpHelpers:
    def test_http_get_error_returns_dict_with_error_key(self):
        import urllib.error as ue

        with mock.patch("urllib.request.urlopen", side_effect=Exception("network error")):
            result = _http_get("http://nonexistent.example.com/api")
        assert "error" in result

    def test_http_post_error_returns_dict_with_error_key(self):
        with mock.patch("urllib.request.urlopen", side_effect=Exception("network error")):
            result = _http_post("http://nonexistent.example.com/api", {"key": "value"})
        assert "error" in result
