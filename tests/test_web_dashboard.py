"""
Tests for ui/web_dashboard.py

Covers:
  1. App creation
  2. Landing page (HTML)
  3. /api/status
  4. /api/bots (GET)
  5. /api/bots/register (POST)
  6. /api/revenue
  7. /api/leaderboard
  8. /api/underperformers
  9. /api/record_run (POST)
  10. /api/history/<bot_name>
  11. /api/github/workflows (GitHub Actions read-only)
  12. /api/github/artifacts (GitHub Actions read-only)
  13. /api/quantum/status (Quantum Bot health)
  14. Helper functions (_fetch_github_workflows, _fetch_github_artifacts, _check_quantum_bot_status)
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

# Only import the ai-models-integration tiers path needed by ControlCenter
AI_MODELS_DIR = os.path.join(REPO_ROOT, "bots", "ai-models-integration")
sys.path.insert(0, AI_MODELS_DIR)

import json
import pytest
from unittest.mock import patch, MagicMock

from ui.web_dashboard import (
    create_app,
    _fetch_github_workflows,
    _fetch_github_artifacts,
    _check_quantum_bot_status,
    _get_governance,
    _update_governance,
    _get_bot_config,
    _set_bot_config,
    _append_failure,
    _get_failures,
    _detect_uncoded_bots,
    _build_runtime_registry,
    _build_runtime_overview,
)
from bots.ai_learning_system.database import BotPerformanceDB
from bots.control_center.control_center import ControlCenter


@pytest.fixture
def client():
    """Return a Flask test client backed by fresh in-memory components."""
    cc = ControlCenter()
    db = BotPerformanceDB()          # in-memory
    app = create_app(control_center=cc, db=db)
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c
    db.close()


@pytest.fixture
def client_with_data():
    """Test client pre-populated with a registered bot and recorded runs."""
    cc = ControlCenter()
    db = BotPerformanceDB()

    class _FakeBot:
        class tier:
            value = "pro"

    cc.register_bot("affiliate_bot", _FakeBot())
    cc.add_income_entry("affiliate_bot", 120.50)
    db.record_run("affiliate_bot", kpis={"revenue_usd": 120.5, "tasks_completed": 6})
    db.record_run("weak_bot", kpis={"revenue_usd": 0.0, "tasks_completed": 0}, status="error")

    app = create_app(control_center=cc, db=db)
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c
    db.close()


# ===========================================================================
# 1. App creation
# ===========================================================================

class TestAppCreation:
    def test_create_app_returns_flask_app(self):
        app = create_app()
        assert app is not None

    def test_create_app_without_args(self):
        app = create_app()
        assert hasattr(app, "test_client")


# ===========================================================================
# 2. Landing page
# ===========================================================================

class TestLandingPage:
    def test_get_root_returns_200(self, client):
        resp = client.get("/")
        assert resp.status_code == 200

    def test_root_content_type_html(self, client):
        resp = client.get("/")
        assert "text/html" in resp.content_type

    def test_root_contains_dreamco(self, client):
        resp = client.get("/")
        assert b"DreamCo" in resp.data

    def test_root_contains_dashboard_title(self, client):
        resp = client.get("/")
        assert b"Dashboard" in resp.data

    def test_dashboard_chooser_returns_200(self, client):
        resp = client.get("/dashboard/chooser")
        assert resp.status_code == 200

    def test_dashboard_chooser_contains_title(self, client):
        resp = client.get("/dashboard/chooser")
        assert b"Dashboard Chooser" in resp.data


# ===========================================================================
# 3. /api/status
# ===========================================================================

class TestApiStatus:
    def test_status_returns_200(self, client):
        resp = client.get("/api/status")
        assert resp.status_code == 200

    def test_status_is_json(self, client):
        resp = client.get("/api/status")
        data = json.loads(resp.data)
        assert isinstance(data, dict)

    def test_status_has_registered_bots(self, client):
        resp = client.get("/api/status")
        data = json.loads(resp.data)
        assert "registered_bots" in data

    def test_status_has_avg_composite_kpi(self, client):
        resp = client.get("/api/status")
        data = json.loads(resp.data)
        assert "avg_composite_kpi" in data

    def test_status_has_underperformers(self, client):
        resp = client.get("/api/status")
        data = json.loads(resp.data)
        assert "underperformers" in data

    def test_status_with_bot(self, client_with_data):
        resp = client_with_data.get("/api/status")
        data = json.loads(resp.data)
        assert data["registered_bots"] >= 1


# ===========================================================================
# 4. /api/bots
# ===========================================================================

class TestApiBots:
    def test_bots_returns_200(self, client):
        resp = client.get("/api/bots")
        assert resp.status_code == 200

    def test_bots_has_bots_key(self, client):
        data = json.loads(client.get("/api/bots").data)
        assert "bots" in data

    def test_bots_has_total_key(self, client):
        data = json.loads(client.get("/api/bots").data)
        assert "total" in data

    def test_bots_shows_registered_bots(self, client_with_data):
        data = json.loads(client_with_data.get("/api/bots").data)
        assert data["total"] >= 1


# ===========================================================================
# 4b. Runtime manifest APIs
# ===========================================================================

class TestRuntimeManifestApis:
    def test_runtime_manifests_returns_200(self, client):
        resp = client.get("/api/runtime/manifests")
        assert resp.status_code == 200

    def test_runtime_manifests_include_buddy_ai(self, client):
        data = json.loads(client.get("/api/runtime/manifests").data)
        ids = {manifest["bot_id"] for manifest in data["manifests"]}
        assert "buddy_ai" in ids

    def test_runtime_manifest_exposes_autonomous_metadata(self, client_with_data):
        data = json.loads(client_with_data.get("/api/runtime/manifests").data)
        affiliate = next(manifest for manifest in data["manifests"] if manifest["bot_id"] == "affiliate_bot")
        for key in ("lifecycle_state", "swarm_role", "memory_nodes", "revenue_attribution", "permissions", "trust_score"):
            assert key in affiliate
        assert affiliate["lifecycle_state"] == "active"

    def test_runtime_overview_returns_layered_architecture(self, client):
        data = json.loads(client.get("/api/runtime/overview").data)
        assert data["schema"] == "dreamco_runtime_overview.v1"
        assert len(data["runtime_layers"]) == 4
        assert "coordination_efficiency" in data["metrics"]

    def test_runtime_helpers_return_registry_and_overview(self):
        cc = ControlCenter()
        db = BotPerformanceDB()
        registry = _build_runtime_registry(cc, db)
        overview = _build_runtime_overview(cc, db)
        assert registry.get("buddy_ai") is not None
        assert overview["buddy_ai"]["bot_id"] == "buddy_ai"
        db.close()


# ===========================================================================
# 5. /api/bots/register
# ===========================================================================

class TestRegisterBot:
    def test_register_returns_201(self, client):
        resp = client.post(
            "/api/bots/register",
            data=json.dumps({"name": "new_bot", "tier": "pro"}),
            content_type="application/json",
        )
        assert resp.status_code == 201

    def test_register_response_contains_name(self, client):
        resp = client.post(
            "/api/bots/register",
            data=json.dumps({"name": "my_bot"}),
            content_type="application/json",
        )
        data = json.loads(resp.data)
        assert data["registered"] == "my_bot"

    def test_register_missing_name_returns_400(self, client):
        resp = client.post(
            "/api/bots/register",
            data=json.dumps({}),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_register_empty_name_returns_400(self, client):
        resp = client.post(
            "/api/bots/register",
            data=json.dumps({"name": "   "}),
            content_type="application/json",
        )
        assert resp.status_code == 400


# ===========================================================================
# 6. /api/revenue
# ===========================================================================

class TestApiRevenue:
    def test_revenue_returns_200(self, client):
        assert client.get("/api/revenue").status_code == 200

    def test_revenue_has_total_income(self, client):
        data = json.loads(client.get("/api/revenue").data)
        assert "total_income_usd" in data

    def test_revenue_has_by_source(self, client):
        data = json.loads(client.get("/api/revenue").data)
        assert "by_source" in data

    def test_revenue_reflects_income_entry(self, client_with_data):
        data = json.loads(client_with_data.get("/api/revenue").data)
        assert data["total_income_usd"] >= 120.50


# ===========================================================================
# 7. /api/leaderboard
# ===========================================================================

class TestApiLeaderboard:
    def test_leaderboard_returns_200(self, client):
        assert client.get("/api/leaderboard").status_code == 200

    def test_leaderboard_has_leaderboard_key(self, client):
        data = json.loads(client.get("/api/leaderboard").data)
        assert "leaderboard" in data

    def test_leaderboard_with_data(self, client_with_data):
        data = json.loads(client_with_data.get("/api/leaderboard").data)
        assert len(data["leaderboard"]) >= 1

    def test_leaderboard_top_n_param(self, client_with_data):
        data = json.loads(client_with_data.get("/api/leaderboard?top=1").data)
        assert len(data["leaderboard"]) <= 1


# ===========================================================================
# 8. /api/underperformers
# ===========================================================================

class TestApiUnderperformers:
    def test_underperformers_returns_200(self, client):
        assert client.get("/api/underperformers").status_code == 200

    def test_underperformers_has_list(self, client):
        data = json.loads(client.get("/api/underperformers").data)
        assert "underperformers" in data

    def test_underperformers_detects_weak_bot(self, client_with_data):
        data = json.loads(client_with_data.get("/api/underperformers?threshold=50").data)
        names = [b["bot_name"] for b in data["underperformers"]]
        assert "weak_bot" in names


# ===========================================================================
# 9. /api/record_run
# ===========================================================================

class TestRecordRun:
    def test_record_run_returns_201(self, client):
        resp = client.post(
            "/api/record_run",
            data=json.dumps({"bot_name": "test_bot", "kpis": {"revenue_usd": 50.0}}),
            content_type="application/json",
        )
        assert resp.status_code == 201

    def test_record_run_response_has_bot_name(self, client):
        resp = client.post(
            "/api/record_run",
            data=json.dumps({"bot_name": "my_bot"}),
            content_type="application/json",
        )
        data = json.loads(resp.data)
        assert data["bot_name"] == "my_bot"

    def test_record_run_missing_bot_name_returns_400(self, client):
        resp = client.post(
            "/api/record_run",
            data=json.dumps({"kpis": {}}),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_record_run_appears_in_history(self, client):
        client.post(
            "/api/record_run",
            data=json.dumps({"bot_name": "tracked_bot", "kpis": {"revenue_usd": 30.0}}),
            content_type="application/json",
        )
        data = json.loads(client.get("/api/history/tracked_bot").data)
        assert len(data["history"]) == 1


# ===========================================================================
# 10. /api/history/<bot_name>
# ===========================================================================

class TestApiHistory:
    def test_history_returns_200(self, client):
        assert client.get("/api/history/some_bot").status_code == 200

    def test_history_has_correct_bot_name(self, client):
        data = json.loads(client.get("/api/history/my_bot").data)
        assert data["bot_name"] == "my_bot"

    def test_history_empty_for_unknown_bot(self, client):
        data = json.loads(client.get("/api/history/nonexistent").data)
        assert data["history"] == []

    def test_history_with_data(self, client_with_data):
        data = json.loads(client_with_data.get("/api/history/affiliate_bot").data)
        assert len(data["history"]) >= 1

    def test_history_limit_param(self, client):
        for _ in range(5):
            client.post(
                "/api/record_run",
                data=json.dumps({"bot_name": "h_bot"}),
                content_type="application/json",
            )
        data = json.loads(client.get("/api/history/h_bot?limit=2").data)
        assert len(data["history"]) <= 2


# ===========================================================================
# 11. /api/bots/catalog
# ===========================================================================

class TestBotCatalog:
    def test_catalog_returns_200(self, client):
        resp = client.get("/api/bots/catalog")
        assert resp.status_code == 200

    def test_catalog_has_catalog_key(self, client):
        data = json.loads(client.get("/api/bots/catalog").data)
        assert "catalog" in data

    def test_catalog_has_total_key(self, client):
        data = json.loads(client.get("/api/bots/catalog").data)
        assert "total" in data

    def test_catalog_contains_lead_generator(self, client):
        data = json.loads(client.get("/api/bots/catalog").data)
        names = [b["name"] for b in data["catalog"]]
        assert "multi_source_lead_scraper" in names

    def test_catalog_contains_real_estate_bot(self, client):
        data = json.loads(client.get("/api/bots/catalog").data)
        names = [b["name"] for b in data["catalog"]]
        assert "real_estate_bot" in names

    def test_catalog_contains_stripe_payment_bot(self, client):
        data = json.loads(client.get("/api/bots/catalog").data)
        names = [b["name"] for b in data["catalog"]]
        assert "stripe_payment_bot" in names

    def test_catalog_bots_have_required_fields(self, client):
        data = json.loads(client.get("/api/bots/catalog").data)
        for bot in data["catalog"]:
            for field in ("name", "display_name", "description", "revenue_model", "category", "is_live"):
                assert field in bot, f"Bot '{bot.get('name')}' missing field '{field}'"

    def test_catalog_not_live_by_default(self, client):
        data = json.loads(client.get("/api/bots/catalog").data)
        # No bots are registered on a fresh client, so none should be live
        for bot in data["catalog"]:
            assert bot["is_live"] is False

    def test_catalog_bot_becomes_live_after_go_live(self, client):
        client.post(
            "/api/bots/multi_source_lead_scraper/go_live",
            data=json.dumps({"tier": "pro"}),
            content_type="application/json",
        )
        data = json.loads(client.get("/api/bots/catalog").data)
        lead_gen = next(b for b in data["catalog"] if b["name"] == "multi_source_lead_scraper")
        assert lead_gen["is_live"] is True

    def test_catalog_total_matches_list_length(self, client):
        data = json.loads(client.get("/api/bots/catalog").data)
        assert data["total"] == len(data["catalog"])


# ===========================================================================
# 12. /api/bots/<name>/go_live
# ===========================================================================

class TestGoLive:
    def test_go_live_returns_201(self, client):
        resp = client.post(
            "/api/bots/lead_generator/go_live",
            data=json.dumps({"tier": "pro"}),
            content_type="application/json",
        )
        assert resp.status_code == 201

    def test_go_live_response_has_status_live(self, client):
        resp = client.post(
            "/api/bots/my_revenue_bot/go_live",
            data=json.dumps({}),
            content_type="application/json",
        )
        data = json.loads(resp.data)
        assert data["status"] == "live"

    def test_go_live_response_has_bot_name(self, client):
        resp = client.post(
            "/api/bots/test_bot/go_live",
            data=json.dumps({}),
            content_type="application/json",
        )
        data = json.loads(resp.data)
        assert data["bot_name"] == "test_bot"

    def test_go_live_response_has_deployed_at(self, client):
        resp = client.post(
            "/api/bots/time_bot/go_live",
            data=json.dumps({}),
            content_type="application/json",
        )
        data = json.loads(resp.data)
        assert "deployed_at" in data

    def test_go_live_response_has_message(self, client):
        resp = client.post(
            "/api/bots/msg_bot/go_live",
            data=json.dumps({}),
            content_type="application/json",
        )
        data = json.loads(resp.data)
        assert "message" in data

    def test_go_live_registers_bot(self, client):
        client.post(
            "/api/bots/registered_bot/go_live",
            data=json.dumps({"tier": "pro"}),
            content_type="application/json",
        )
        status_data = json.loads(client.get("/api/status").data)
        assert status_data["registered_bots"] >= 1

    def test_go_live_records_run_in_history(self, client):
        client.post(
            "/api/bots/history_bot/go_live",
            data=json.dumps({}),
            content_type="application/json",
        )
        history = json.loads(client.get("/api/history/history_bot").data)
        assert len(history["history"]) >= 1

    def test_go_live_idempotent_second_call(self, client):
        for _ in range(2):
            resp = client.post(
                "/api/bots/idempotent_bot/go_live",
                data=json.dumps({}),
                content_type="application/json",
            )
            assert resp.status_code == 201

    def test_go_live_uses_specified_tier(self, client):
        resp = client.post(
            "/api/bots/tier_bot/go_live",
            data=json.dumps({"tier": "enterprise"}),
            content_type="application/json",
        )
        data = json.loads(resp.data)
        assert data["tier"] == "enterprise"

    def test_go_live_lead_generator(self, client):
        resp = client.post(
            "/api/bots/multi_source_lead_scraper/go_live",
            data=json.dumps({"tier": "pro"}),
            content_type="application/json",
        )
        assert resp.status_code == 201

    def test_go_live_real_estate_bot(self, client):
        resp = client.post(
            "/api/bots/real_estate_bot/go_live",
            data=json.dumps({"tier": "enterprise"}),
            content_type="application/json",
        )
        assert resp.status_code == 201

    def test_go_live_stripe_payment_bot(self, client):
        resp = client.post(
            "/api/bots/stripe_payment_bot/go_live",
            data=json.dumps({"tier": "growth"}),
            content_type="application/json",
        )
        assert resp.status_code == 201

    def test_dashboard_html_contains_go_live_section(self, client):
        resp = client.get("/")
        assert b"Go Live" in resp.data

    def test_dashboard_html_contains_bot_catalog(self, client):
        resp = client.get("/")
        assert b"bot-catalog" in resp.data

    def test_dashboard_html_contains_workflow_monitor(self, client):
        resp = client.get("/")
        assert b"workflow" in resp.data.lower() or b"Workflow" in resp.data

    def test_dashboard_html_contains_quantum_section(self, client):
        resp = client.get("/")
        assert b"quantum" in resp.data.lower() or b"Quantum" in resp.data


# ===========================================================================
# 11. /api/github/workflows (read-only, GitHub Actions integration)
# ===========================================================================

class TestGitHubWorkflowsEndpoint:
    def test_endpoint_returns_200(self, client):
        resp = client.get("/api/github/workflows")
        assert resp.status_code == 200

    def test_response_has_runs_key(self, client):
        data = json.loads(client.get("/api/github/workflows").data)
        assert "runs" in data

    def test_response_has_source_key(self, client):
        data = json.loads(client.get("/api/github/workflows").data)
        assert "source" in data

    def test_runs_is_list(self, client):
        data = json.loads(client.get("/api/github/workflows").data)
        assert isinstance(data["runs"], list)

    def test_no_exception_without_token(self, client):
        """Endpoint must not raise even when GITHUB_TOKEN is absent."""
        import os
        env = {k: v for k, v in os.environ.items() if k != "GITHUB_TOKEN"}
        with patch.dict(os.environ, env, clear=True):
            resp = client.get("/api/github/workflows")
        assert resp.status_code == 200

    def test_mocked_github_api_success(self, client):
        fake_run = {
            "id": 1,
            "name": "CI",
            "workflow_id": 10,
            "status": "completed",
            "conclusion": "success",
            "head_branch": "main",
            "event": "push",
            "run_started_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:01:00Z",
            "html_url": "https://github.com/example/run/1",
        }
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"workflow_runs": [fake_run], "total_count": 1}
        with patch("ui.web_dashboard._requests") as mock_req:
            mock_req.get.return_value = mock_resp
            data = _fetch_github_workflows(repo="owner/repo")
        assert data["source"] == "github_api"
        assert len(data["runs"]) == 1
        assert data["runs"][0]["name"] == "CI"
        assert data["runs"][0]["conclusion"] == "success"

    def test_mocked_github_api_non_200(self, client):
        mock_resp = MagicMock()
        mock_resp.status_code = 403
        with patch("ui.web_dashboard._requests") as mock_req:
            mock_req.get.return_value = mock_resp
            data = _fetch_github_workflows(repo="owner/repo")
        assert data["source"] == "unavailable"
        assert data["runs"] == []

    def test_mocked_github_api_exception(self, client):
        with patch("ui.web_dashboard._requests") as mock_req:
            mock_req.get.side_effect = Exception("network error")
            data = _fetch_github_workflows(repo="owner/repo")
        assert data["source"] == "unavailable"
        assert data["runs"] == []

    def test_workflow_run_fields_present(self, client):
        """Each run dict must include all expected keys."""
        fake_run = {
            "id": 99,
            "name": "Test",
            "workflow_id": 5,
            "status": "in_progress",
            "conclusion": None,
            "head_branch": "feature",
            "event": "pull_request",
            "run_started_at": None,
            "updated_at": None,
            "html_url": None,
        }
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"workflow_runs": [fake_run], "total_count": 1}
        with patch("ui.web_dashboard._requests") as mock_req:
            mock_req.get.return_value = mock_resp
            data = _fetch_github_workflows(repo="owner/repo")
        run = data["runs"][0]
        for key in ("id", "name", "status", "conclusion", "branch", "event", "url"):
            assert key in run


# ===========================================================================
# 12. /api/github/artifacts (read-only, GitHub Actions integration)
# ===========================================================================

class TestGitHubArtifactsEndpoint:
    def test_endpoint_returns_200(self, client):
        resp = client.get("/api/github/artifacts")
        assert resp.status_code == 200

    def test_response_has_artifacts_key(self, client):
        data = json.loads(client.get("/api/github/artifacts").data)
        assert "artifacts" in data

    def test_response_has_source_key(self, client):
        data = json.loads(client.get("/api/github/artifacts").data)
        assert "source" in data

    def test_artifacts_is_list(self, client):
        data = json.loads(client.get("/api/github/artifacts").data)
        assert isinstance(data["artifacts"], list)

    def test_no_exception_without_token(self, client):
        import os
        env = {k: v for k, v in os.environ.items() if k != "GITHUB_TOKEN"}
        with patch.dict(os.environ, env, clear=True):
            resp = client.get("/api/github/artifacts")
        assert resp.status_code == 200

    def test_mocked_artifacts_success(self, client):
        fake_artifact = {
            "id": 42,
            "name": "bot-logs",
            "size_in_bytes": 2048,
            "created_at": "2024-01-01T00:00:00Z",
            "expires_at": "2024-02-01T00:00:00Z",
            "expired": False,
            "url": "https://api.github.com/repos/owner/repo/actions/artifacts/42",
        }
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"artifacts": [fake_artifact], "total_count": 1}
        with patch("ui.web_dashboard._requests") as mock_req:
            mock_req.get.return_value = mock_resp
            data = _fetch_github_artifacts(repo="owner/repo")
        assert data["source"] == "github_api"
        assert len(data["artifacts"]) == 1
        assert data["artifacts"][0]["name"] == "bot-logs"

    def test_mocked_artifacts_non_200(self, client):
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        with patch("ui.web_dashboard._requests") as mock_req:
            mock_req.get.return_value = mock_resp
            data = _fetch_github_artifacts(repo="owner/repo")
        assert data["source"] == "unavailable"
        assert data["artifacts"] == []

    def test_mocked_artifacts_exception(self, client):
        with patch("ui.web_dashboard._requests") as mock_req:
            mock_req.get.side_effect = ConnectionError("timeout")
            data = _fetch_github_artifacts(repo="owner/repo")
        assert data["source"] == "unavailable"
        assert data["artifacts"] == []

    def test_artifact_fields_present(self, client):
        fake_artifact = {
            "id": 1,
            "name": "logs",
            "size_in_bytes": 512,
            "created_at": "2024-01-01T00:00:00Z",
            "expires_at": "2024-02-01T00:00:00Z",
            "expired": False,
            "url": "https://example.com",
        }
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"artifacts": [fake_artifact], "total_count": 1}
        with patch("ui.web_dashboard._requests") as mock_req:
            mock_req.get.return_value = mock_resp
            data = _fetch_github_artifacts(repo="owner/repo")
        art = data["artifacts"][0]
        for key in ("id", "name", "size_in_bytes", "created_at", "expires_at", "expired"):
            assert key in art


# ===========================================================================
# 13. /api/quantum/status (Quantum Bot health check, read-only)
# ===========================================================================

class TestQuantumStatusEndpoint:
    def test_endpoint_returns_200(self, client):
        resp = client.get("/api/quantum/status")
        assert resp.status_code == 200

    def test_response_has_status_key(self, client):
        data = json.loads(client.get("/api/quantum/status").data)
        assert "status" in data

    def test_response_has_bot_key(self, client):
        data = json.loads(client.get("/api/quantum/status").data)
        assert "bot" in data

    def test_response_has_checked_at(self, client):
        data = json.loads(client.get("/api/quantum/status").data)
        assert "checked_at" in data

    def test_quantum_status_ok(self, client):
        data = json.loads(client.get("/api/quantum/status").data)
        assert data["status"] in ("ok", "error")

    def test_check_quantum_bot_returns_dict(self):
        result = _check_quantum_bot_status()
        assert isinstance(result, dict)

    def test_check_quantum_bot_has_required_keys(self):
        result = _check_quantum_bot_status()
        assert "status" in result
        assert "bot" in result
        assert "checked_at" in result

    def test_check_quantum_bot_status_ok_has_engines(self):
        result = _check_quantum_bot_status()
        if result["status"] == "ok":
            assert "engines" in result
            assert isinstance(result["engines"], list)
            assert len(result["engines"]) > 0

    def test_check_quantum_bot_never_raises(self):
        """_check_quantum_bot_status must never propagate exceptions."""
        try:
            result = _check_quantum_bot_status()
            assert isinstance(result, dict)
        except Exception as exc:
            pytest.fail(f"_check_quantum_bot_status raised unexpectedly: {exc}")

    def test_check_quantum_bot_error_has_reason(self):
        """When import fails the response must contain a reason."""
        import builtins
        import ui.web_dashboard as _wdash
        real_import = builtins.__import__

        def _fail_import(name, *args, **kwargs):
            if "quantum_ai_bot" in name:
                raise ImportError("simulated import failure")
            return real_import(name, *args, **kwargs)

        # Clear the module-level cache so the mocked import path is exercised
        _wdash._quantum_cache.clear()
        with patch("builtins.__import__", side_effect=_fail_import):
            result = _check_quantum_bot_status()
        assert result["status"] == "error"
        assert "reason" in result


# ===========================================================================
# 14. Helper function unit tests (_fetch_github_workflows / _fetch_github_artifacts)
# ===========================================================================

class TestFetchGitHubHelpers:
    def test_fetch_workflows_returns_dict(self):
        result = _fetch_github_workflows()
        assert isinstance(result, dict)

    def test_fetch_artifacts_returns_dict(self):
        result = _fetch_github_artifacts()
        assert isinstance(result, dict)

    def test_fetch_workflows_graceful_without_requests(self):
        with patch("ui.web_dashboard._REQUESTS_AVAILABLE", False):
            result = _fetch_github_workflows()
        assert result["source"] == "unavailable"
        assert result["runs"] == []

    def test_fetch_artifacts_graceful_without_requests(self):
        with patch("ui.web_dashboard._REQUESTS_AVAILABLE", False):
            result = _fetch_github_artifacts()
        assert result["source"] == "unavailable"
        assert result["artifacts"] == []

    def test_fetch_workflows_per_page_param(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"workflow_runs": [], "total_count": 0}
        with patch("ui.web_dashboard._requests") as mock_req:
            mock_req.get.return_value = mock_resp
            _fetch_github_workflows(per_page=5)
        call_kwargs = mock_req.get.call_args
        assert call_kwargs[1]["params"]["per_page"] == 5

    def test_fetch_artifacts_per_page_param(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"artifacts": [], "total_count": 0}
        with patch("ui.web_dashboard._requests") as mock_req:
            mock_req.get.return_value = mock_resp
            _fetch_github_artifacts(per_page=3)
        call_kwargs = mock_req.get.call_args
        assert call_kwargs[1]["params"]["per_page"] == 3

    def test_github_headers_include_accept(self):
        from ui.web_dashboard import _github_headers
        headers = _github_headers()
        assert "Accept" in headers
        assert headers["Accept"] == "application/vnd.github+json"

    def test_github_headers_include_auth_when_token_set(self):
        from ui.web_dashboard import _github_headers
        with patch.dict(__import__("os").environ, {"GITHUB_TOKEN": "test_token_xyz"}):
            headers = _github_headers()
        assert "Authorization" in headers
        assert "test_token_xyz" in headers["Authorization"]

    def test_github_headers_no_auth_without_token(self):
        from ui.web_dashboard import _github_headers
        import os
        env = {k: v for k, v in os.environ.items() if k != "GITHUB_TOKEN"}
        with patch.dict(os.environ, env, clear=True):
            headers = _github_headers()
        assert "Authorization" not in headers


# ===========================================================================
# 15. Governance API (/api/governance, /api/governance/settings)
# ===========================================================================

class TestGovernanceApi:
    def test_get_governance_returns_200(self, client):
        resp = client.get("/api/governance")
        assert resp.status_code == 200

    def test_get_governance_has_required_fields(self, client):
        data = json.loads(client.get("/api/governance").data)
        assert "aggressiveness" in data
        assert "max_execution_seconds" in data
        assert "retry_policy" in data

    def test_get_governance_defaults(self, client):
        data = json.loads(client.get("/api/governance").data)
        assert data["aggressiveness"] in ("passive", "balanced", "aggressive", "max")
        assert isinstance(data["max_execution_seconds"], int)
        assert data["retry_policy"] in ("none", "once", "twice", "auto")

    def test_post_governance_settings_returns_200(self, client):
        resp = client.post(
            "/api/governance/settings",
            data=json.dumps({"aggressiveness": "aggressive"}),
            content_type="application/json",
        )
        assert resp.status_code == 200

    def test_post_governance_settings_updates_aggressiveness(self, client):
        client.post(
            "/api/governance/settings",
            data=json.dumps({"aggressiveness": "max"}),
            content_type="application/json",
        )
        data = json.loads(client.get("/api/governance").data)
        assert data["aggressiveness"] == "max"

    def test_post_governance_settings_updates_max_exec(self, client):
        client.post(
            "/api/governance/settings",
            data=json.dumps({"max_execution_seconds": 600}),
            content_type="application/json",
        )
        data = json.loads(client.get("/api/governance").data)
        assert data["max_execution_seconds"] == 600

    def test_post_governance_settings_clamps_max_exec_low(self, client):
        client.post(
            "/api/governance/settings",
            data=json.dumps({"max_execution_seconds": 5}),
            content_type="application/json",
        )
        data = json.loads(client.get("/api/governance").data)
        assert data["max_execution_seconds"] >= 30

    def test_post_governance_settings_clamps_max_exec_high(self, client):
        client.post(
            "/api/governance/settings",
            data=json.dumps({"max_execution_seconds": 99999}),
            content_type="application/json",
        )
        data = json.loads(client.get("/api/governance").data)
        assert data["max_execution_seconds"] <= 3600

    def test_post_governance_settings_updates_retry_policy(self, client):
        client.post(
            "/api/governance/settings",
            data=json.dumps({"retry_policy": "twice"}),
            content_type="application/json",
        )
        data = json.loads(client.get("/api/governance").data)
        assert data["retry_policy"] == "twice"

    def test_post_governance_no_fields_returns_400(self, client):
        resp = client.post(
            "/api/governance/settings",
            data=json.dumps({}),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_post_governance_invalid_aggressiveness_ignored(self, client):
        client.post(
            "/api/governance/settings",
            data=json.dumps({"aggressiveness": "balanced"}),
            content_type="application/json",
        )
        client.post(
            "/api/governance/settings",
            data=json.dumps({"aggressiveness": "turbo_invalid"}),
            content_type="application/json",
        )
        data = json.loads(client.get("/api/governance").data)
        assert data["aggressiveness"] == "balanced"

    def test_governance_has_updated_at_after_update(self, client):
        client.post(
            "/api/governance/settings",
            data=json.dumps({"retry_policy": "once"}),
            content_type="application/json",
        )
        data = json.loads(client.get("/api/governance").data)
        assert data["updated_at"] is not None


# ===========================================================================
# 16. Per-bot configuration (/api/bots/<name>/configure, /api/bots/<name>/config)
# ===========================================================================

class TestBotConfigureApi:
    def test_configure_returns_200(self, client):
        resp = client.post(
            "/api/bots/test_bot/configure",
            data=json.dumps({"aggressiveness": "aggressive"}),
            content_type="application/json",
        )
        assert resp.status_code == 200

    def test_configure_response_has_bot_name(self, client):
        resp = client.post(
            "/api/bots/my_bot/configure",
            data=json.dumps({"aggressiveness": "max"}),
            content_type="application/json",
        )
        data = json.loads(resp.data)
        assert data["bot_name"] == "my_bot"

    def test_configure_aggressiveness_stored(self, client):
        client.post(
            "/api/bots/cfg_bot/configure",
            data=json.dumps({"aggressiveness": "passive"}),
            content_type="application/json",
        )
        data = json.loads(client.get("/api/bots/cfg_bot/config").data)
        assert data["aggressiveness"] == "passive"

    def test_configure_max_exec_stored(self, client):
        client.post(
            "/api/bots/exec_bot/configure",
            data=json.dumps({"max_execution_seconds": 120}),
            content_type="application/json",
        )
        data = json.loads(client.get("/api/bots/exec_bot/config").data)
        assert data["max_execution_seconds"] == 120

    def test_configure_retry_policy_stored(self, client):
        client.post(
            "/api/bots/retry_bot/configure",
            data=json.dumps({"retry_policy": "twice"}),
            content_type="application/json",
        )
        data = json.loads(client.get("/api/bots/retry_bot/config").data)
        assert data["retry_policy"] == "twice"

    def test_configure_marks_custom_true(self, client):
        client.post(
            "/api/bots/custom_bot/configure",
            data=json.dumps({"aggressiveness": "max"}),
            content_type="application/json",
        )
        data = json.loads(client.get("/api/bots/custom_bot/config").data)
        assert data["custom"] is True

    def test_config_get_unconfigured_bot_returns_defaults(self, client):
        data = json.loads(client.get("/api/bots/unknown_bot_xyz/config").data)
        assert data["custom"] is False
        assert "aggressiveness" in data

    def test_config_get_returns_200(self, client):
        resp = client.get("/api/bots/any_bot/config")
        assert resp.status_code == 200

    def test_configure_clamps_max_exec(self, client):
        client.post(
            "/api/bots/clamp_bot/configure",
            data=json.dumps({"max_execution_seconds": 0}),
            content_type="application/json",
        )
        data = json.loads(client.get("/api/bots/clamp_bot/config").data)
        assert data["max_execution_seconds"] >= 30


# ===========================================================================
# 17. Uncoded bot monitor (/api/bots/uncoded)
# ===========================================================================

class TestUncodedBotsApi:
    def test_endpoint_returns_200(self, client):
        resp = client.get("/api/bots/uncoded")
        assert resp.status_code == 200

    def test_response_has_uncoded_count(self, client):
        data = json.loads(client.get("/api/bots/uncoded").data)
        assert "uncoded_count" in data

    def test_response_has_stubbed_count(self, client):
        data = json.loads(client.get("/api/bots/uncoded").data)
        assert "stubbed_count" in data

    def test_uncoded_list_is_list(self, client):
        data = json.loads(client.get("/api/bots/uncoded").data)
        assert isinstance(data["uncoded"], list)

    def test_stubbed_list_is_list(self, client):
        data = json.loads(client.get("/api/bots/uncoded").data)
        assert isinstance(data["stubbed"], list)

    def test_has_scanned_at(self, client):
        data = json.loads(client.get("/api/bots/uncoded").data)
        assert "scanned_at" in data

    def test_detect_uncoded_bots_returns_dict(self):
        from ui.web_dashboard import _detect_uncoded_bots
        result = _detect_uncoded_bots()
        assert isinstance(result, dict)
        assert "uncoded_count" in result
        assert "stubbed_count" in result

    def test_detect_uncoded_bots_never_raises(self):
        from ui.web_dashboard import _detect_uncoded_bots
        try:
            result = _detect_uncoded_bots()
            assert isinstance(result, dict)
        except Exception as exc:
            pytest.fail(f"_detect_uncoded_bots raised unexpectedly: {exc}")


# ===========================================================================
# 18. Failure and conflict log (/api/failures, /api/failures/report)
# ===========================================================================

class TestFailuresApi:
    def test_get_failures_returns_200(self, client):
        resp = client.get("/api/failures")
        assert resp.status_code == 200

    def test_get_failures_has_failures_key(self, client):
        data = json.loads(client.get("/api/failures").data)
        assert "failures" in data

    def test_get_failures_has_total_key(self, client):
        data = json.loads(client.get("/api/failures").data)
        assert "total" in data

    def test_failures_list_is_list(self, client):
        data = json.loads(client.get("/api/failures").data)
        assert isinstance(data["failures"], list)

    def test_report_failure_returns_201(self, client):
        resp = client.post(
            "/api/failures/report",
            data=json.dumps({
                "bot_name": "crash_bot",
                "failure_type": "failure",
                "message": "Test failure",
            }),
            content_type="application/json",
        )
        assert resp.status_code == 201

    def test_reported_failure_appears_in_log(self, client):
        client.post(
            "/api/failures/report",
            data=json.dumps({
                "bot_name": "tracked_fail_bot",
                "failure_type": "failure",
                "message": "Something broke",
            }),
            content_type="application/json",
        )
        data = json.loads(client.get("/api/failures").data)
        bot_names = [f["bot_name"] for f in data["failures"]]
        assert "tracked_fail_bot" in bot_names

    def test_report_failure_missing_fields_returns_400(self, client):
        resp = client.post(
            "/api/failures/report",
            data=json.dumps({"bot_name": "x"}),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_report_failure_response_has_timestamp(self, client):
        resp = client.post(
            "/api/failures/report",
            data=json.dumps({
                "bot_name": "time_bot",
                "failure_type": "conflict",
                "message": "Merge conflict detected",
            }),
            content_type="application/json",
        )
        data = json.loads(resp.data)
        assert "timestamp" in data

    def test_get_failures_filtered_by_bot_name(self, client):
        client.post(
            "/api/failures/report",
            data=json.dumps({
                "bot_name": "filter_bot",
                "failure_type": "warning",
                "message": "Slow execution",
            }),
            content_type="application/json",
        )
        data = json.loads(client.get("/api/failures?bot_name=filter_bot").data)
        assert all(f["bot_name"] == "filter_bot" for f in data["failures"])

    def test_get_failures_limit_param(self, client):
        for i in range(5):
            client.post(
                "/api/failures/report",
                data=json.dumps({
                    "bot_name": f"limit_bot_{i}",
                    "failure_type": "failure",
                    "message": f"Failure {i}",
                }),
                content_type="application/json",
            )
        data = json.loads(client.get("/api/failures?limit=2").data)
        assert len(data["failures"]) <= 2

    def test_append_failure_helper_returns_entry(self):
        from ui.web_dashboard import _append_failure
        entry = _append_failure("helper_bot", "failure", "test msg")
        assert entry["bot_name"] == "helper_bot"
        assert entry["failure_type"] == "failure"
        assert "timestamp" in entry

    def test_get_failures_helper_returns_list(self):
        from ui.web_dashboard import _get_failures
        result = _get_failures()
        assert isinstance(result, list)


# ===========================================================================
# 19. Per-bot dashboard HTML page (/bots/<name>)
# ===========================================================================

class TestBotDashboardPage:
    def test_bot_page_returns_200(self, client):
        resp = client.get("/bots/multi_source_lead_scraper")
        assert resp.status_code == 200

    def test_bot_page_content_type_html(self, client):
        resp = client.get("/bots/real_estate_bot")
        assert "text/html" in resp.content_type

    def test_bot_page_contains_bot_name(self, client):
        resp = client.get("/bots/multi_source_lead_scraper")
        assert b"multi_source_lead_scraper" in resp.data or b"Lead Generator" in resp.data

    def test_bot_page_contains_runtime_parameters(self, client):
        resp = client.get("/bots/crypto_bot")
        assert b"Runtime Parameters" in resp.data or b"Aggressiveness" in resp.data

    def test_bot_page_contains_back_link(self, client):
        resp = client.get("/bots/fiverr_bot")
        assert b"Back to Dashboard" in resp.data or b"href=\"/\"" in resp.data

    def test_bot_page_for_unknown_bot_returns_200(self, client):
        resp = client.get("/bots/completely_unknown_bot_xyz")
        assert resp.status_code == 200

    def test_bot_page_contains_failures_section(self, client):
        resp = client.get("/bots/affiliate_bot")
        assert b"Failures" in resp.data or b"failure" in resp.data.lower()

    def test_bot_page_contains_run_history_section(self, client):
        resp = client.get("/bots/ai_chatbot")
        assert b"Run History" in resp.data or b"history" in resp.data.lower()

    def test_catalog_has_dashboard_link_section(self, client):
        resp = client.get("/")
        assert b"Bot Dashboard" in resp.data or b"bot-dash-link" in resp.data

    def test_dashboard_html_contains_governance_section(self, client):
        resp = client.get("/")
        assert b"Governance" in resp.data or b"governance" in resp.data.lower()

    def test_dashboard_html_contains_runtime_core_section(self, client):
        resp = client.get("/")
        assert b"Autonomous Runtime Core" in resp.data or b"Runtime Layers" in resp.data

    def test_dashboard_html_contains_uncoded_monitor(self, client):
        resp = client.get("/")
        assert b"Uncoded" in resp.data or b"uncoded" in resp.data.lower()

    def test_dashboard_html_contains_failure_section(self, client):
        resp = client.get("/")
        assert b"Failures" in resp.data or b"failure" in resp.data.lower()

    def test_bot_page_contains_prospectus_manifest_section(self, client):
        resp = client.get("/bots/affiliate_bot")
        assert b"Prospectus" in resp.data or b"Runtime Manifest" in resp.data


# ===========================================================================
# 20. Governance helper function unit tests
# ===========================================================================

class TestGovernanceHelpers:
    def test_get_governance_returns_dict(self):
        from ui.web_dashboard import _get_governance
        result = _get_governance()
        assert isinstance(result, dict)

    def test_update_governance_aggressiveness(self):
        from ui.web_dashboard import _get_governance, _update_governance
        _update_governance(aggressiveness="passive")
        assert _get_governance()["aggressiveness"] == "passive"
        _update_governance(aggressiveness="balanced")  # restore default

    def test_update_governance_max_exec(self):
        from ui.web_dashboard import _get_governance, _update_governance
        _update_governance(max_execution_seconds=120)
        assert _get_governance()["max_execution_seconds"] == 120
        _update_governance(max_execution_seconds=300)  # restore

    def test_update_governance_invalid_aggressiveness_ignored(self):
        from ui.web_dashboard import _get_governance, _update_governance
        _update_governance(aggressiveness="balanced")
        _update_governance(aggressiveness="invalid_value")
        assert _get_governance()["aggressiveness"] == "balanced"

    def test_get_bot_config_returns_dict(self):
        from ui.web_dashboard import _get_bot_config
        result = _get_bot_config("any_bot")
        assert isinstance(result, dict)
        assert "aggressiveness" in result

    def test_set_bot_config_persists(self):
        from ui.web_dashboard import _get_bot_config, _set_bot_config
        _set_bot_config("my_test_bot", aggressiveness="max")
        cfg = _get_bot_config("my_test_bot")
        assert cfg["aggressiveness"] == "max"

    def test_set_bot_config_marks_custom(self):
        from ui.web_dashboard import _get_bot_config, _set_bot_config
        _set_bot_config("custom_check_bot", retry_policy="once")
        assert _get_bot_config("custom_check_bot")["custom"] is True
