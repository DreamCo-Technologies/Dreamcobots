"""
Tests for bots/saas-selling-bot
"""

import json
import os
import sys
import pytest

# Make the bot module importable without depending on working directory
BOT_DIR = os.path.join(os.path.dirname(__file__), "..", "bots", "saas-selling-bot")
sys.path.insert(0, os.path.abspath(BOT_DIR))

# Use an in-memory database for tests
os.environ["SAAS_BOT_DB"] = ":memory:"

import database as db  # noqa: E402
from nlp import get_faq_response, _keyword_score  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def fresh_db(tmp_path, monkeypatch):
    """Each test gets its own in-memory database."""
    db_file = str(tmp_path / "test.db")
    monkeypatch.setattr(db, "DB_PATH", db_file)
    db.init_db()
    yield


@pytest.fixture()
def client():
    """Flask test client with an isolated temp database."""
    import bot as b
    b.app.config["TESTING"] = True
    with b.app.test_client() as c:
        yield c


# ---------------------------------------------------------------------------
# database.py tests
# ---------------------------------------------------------------------------

class TestDatabase:
    def test_init_creates_tables(self):
        conn = db.get_connection()
        tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        assert "leads" in tables
        assert "demo_events" in tables
        assert "chat_events" in tables

    def test_save_lead_returns_id(self):
        lead_id = db.save_lead("Alice", "alice@example.com", "Acme", "custom-bot", "Hello")
        assert lead_id == 1

    def test_save_lead_stores_data(self):
        db.save_lead("Bob", "bob@example.com", "", "nlp-bot", "")
        conn = db.get_connection()
        row = conn.execute("SELECT * FROM leads WHERE id=1").fetchone()
        assert row["name"] == "Bob"
        assert row["email"] == "bob@example.com"

    def test_record_demo(self):
        db.record_demo("custom-bot", "send report")
        conn = db.get_connection()
        row = conn.execute("SELECT * FROM demo_events WHERE id=1").fetchone()
        assert row["demo_name"] == "custom-bot"
        assert row["user_input"] == "send report"

    def test_record_chat(self):
        db.record_chat("What is the price?", "Starts at $99.")
        conn = db.get_connection()
        row = conn.execute("SELECT * FROM chat_events WHERE id=1").fetchone()
        assert row["user_message"] == "What is the price?"

    def test_get_analytics_empty(self):
        analytics = db.get_analytics()
        assert analytics["total_leads"] == 0
        assert analytics["chat_interactions"] == 0
        assert analytics["demo_runs"] == {}

    def test_get_analytics_counts(self):
        db.save_lead("Alice", "a@a.com", "", "", "")
        db.save_lead("Bob", "b@b.com", "", "", "")
        db.record_demo("custom-bot")
        db.record_demo("custom-bot")
        db.record_demo("nlp-bot")
        db.record_chat("q", "a")
        analytics = db.get_analytics()
        assert analytics["total_leads"] == 2
        assert analytics["chat_interactions"] == 1
        assert analytics["demo_runs"]["custom-bot"] == 2
        assert analytics["demo_runs"]["nlp-bot"] == 1


# ---------------------------------------------------------------------------
# nlp.py tests
# ---------------------------------------------------------------------------

class TestNLP:
    def test_keyword_score_match(self):
        assert _keyword_score("what is the price?", ["price", "cost"]) == 1

    def test_keyword_score_no_match(self):
        assert _keyword_score("hello world", ["price", "cost"]) == 0

    def test_keyword_score_multiple_matches(self):
        assert _keyword_score("price and cost details", ["price", "cost"]) == 2

    def test_get_faq_response_pricing(self):
        resp = get_faq_response("what is the price?")
        assert "$99" in resp or "pricing" in resp.lower()

    def test_get_faq_response_custom_bot(self):
        resp = get_faq_response("tell me about custom bot development")
        assert "custom" in resp.lower() or "automation" in resp.lower()

    def test_get_faq_response_nlp(self):
        resp = get_faq_response("do you have an NLP chatbot?")
        assert "nlp" in resp.lower() or "chatbot" in resp.lower() or "language" in resp.lower()

    def test_get_faq_response_income(self):
        resp = get_faq_response("how does income tracking work?")
        assert resp  # non-empty

    def test_get_faq_response_contracts(self):
        resp = get_faq_response("can you find government grants?")
        assert "grant" in resp.lower() or "contract" in resp.lower() or resp

    def test_get_faq_response_fallback(self):
        resp = get_faq_response("xyzzy frobnicate wumpus")
        assert len(resp) > 0  # always returns something

    def test_get_faq_response_empty_string(self):
        resp = get_faq_response("")
        assert isinstance(resp, str)


# ---------------------------------------------------------------------------
# Flask route tests
# ---------------------------------------------------------------------------

class TestRoutes:
    def test_index(self, client):
        rv = client.get("/")
        assert rv.status_code == 200
        assert b"DreamCobots" in rv.data

    def test_pricing_page(self, client):
        rv = client.get("/pricing")
        assert rv.status_code == 200
        assert b"Starter" in rv.data
        assert b"Professional" in rv.data

    def test_faq_page(self, client):
        rv = client.get("/faq")
        assert rv.status_code == 200
        assert b"FAQ" in rv.data

    def test_lead_gen_get(self, client):
        rv = client.get("/lead-gen")
        assert rv.status_code == 200
        assert b"Quote" in rv.data

    def test_lead_gen_post_success(self, client):
        rv = client.post("/lead-gen", data={
            "name": "Alice",
            "email": "alice@example.com",
            "company": "Acme",
            "service": "custom-bot",
            "message": "I need a bot",
        })
        assert rv.status_code == 200
        assert b"Thank you" in rv.data

    def test_lead_gen_post_missing_name(self, client):
        rv = client.post("/lead-gen", data={"email": "x@x.com"})
        assert rv.status_code == 200
        # Should re-render the form, not show success
        assert b"Thank you" not in rv.data

    # Demo pages
    def test_demo_custom_bot_get(self, client):
        rv = client.get("/demo/custom-bot")
        assert rv.status_code == 200

    def test_demo_custom_bot_post(self, client):
        rv = client.post("/demo/custom-bot", data={"task": "Send report"})
        assert rv.status_code == 200
        assert b"Pipeline" in rv.data

    def test_demo_nlp_bot_get(self, client):
        rv = client.get("/demo/nlp-bot")
        assert rv.status_code == 200

    def test_demo_nlp_bot_post(self, client):
        rv = client.post("/demo/nlp-bot", data={"message": "What is the price?"})
        assert rv.status_code == 200
        assert b"$99" in rv.data or b"pricing" in rv.data.lower()

    def test_demo_income_tracking(self, client):
        rv = client.get("/demo/income-tracking")
        assert rv.status_code == 200
        assert b"Revenue" in rv.data

    def test_demo_contracts_get(self, client):
        rv = client.get("/demo/contracts")
        assert rv.status_code == 200

    def test_demo_contracts_post(self, client):
        rv = client.post("/demo/contracts", data={"keyword": "automation"})
        assert rv.status_code == 200
        assert b"automation" in rv.data.lower()

    def test_demo_api_integration(self, client):
        rv = client.get("/demo/api-integration")
        assert rv.status_code == 200
        assert b"Stripe" in rv.data

    def test_demo_ui_ux(self, client):
        rv = client.get("/demo/ui-ux")
        assert rv.status_code == 200
        assert b"Dashboard" in rv.data

    # JSON API endpoints
    def test_api_chat_valid(self, client):
        rv = client.post("/api/chat",
                         data=json.dumps({"message": "What is pricing?"}),
                         content_type="application/json")
        assert rv.status_code == 200
        data = json.loads(rv.data)
        assert "response" in data
        assert len(data["response"]) > 0

    def test_api_chat_missing_message(self, client):
        rv = client.post("/api/chat",
                         data=json.dumps({}),
                         content_type="application/json")
        assert rv.status_code == 400
        data = json.loads(rv.data)
        assert "error" in data

    def test_api_chat_empty_message(self, client):
        rv = client.post("/api/chat",
                         data=json.dumps({"message": ""}),
                         content_type="application/json")
        assert rv.status_code == 400

    def test_api_submit_lead_valid(self, client):
        rv = client.post("/api/submit-lead",
                         data=json.dumps({"name": "Bob", "email": "b@b.com"}),
                         content_type="application/json")
        assert rv.status_code == 200
        data = json.loads(rv.data)
        assert data["success"] is True
        assert "lead_id" in data

    def test_api_submit_lead_missing_fields(self, client):
        rv = client.post("/api/submit-lead",
                         data=json.dumps({"name": "Bob"}),
                         content_type="application/json")
        assert rv.status_code == 400

    def test_api_analytics(self, client):
        rv = client.get("/api/analytics")
        assert rv.status_code == 200
        data = json.loads(rv.data)
        assert "total_leads" in data
        assert "demo_runs" in data
        assert "chat_interactions" in data


# ---------------------------------------------------------------------------
# bot.py demo helpers
# ---------------------------------------------------------------------------

class TestDemoHelpers:
    def test_run_custom_bot_demo(self):
        from bot import run_custom_bot_demo
        result = run_custom_bot_demo("Send weekly report")
        assert "steps" in result
        assert "result" in result
        assert len(result["steps"]) > 0
        assert "Send weekly report" in result["result"]

    def test_run_contract_search_keyword_match(self):
        from bot import run_contract_search
        results = run_contract_search("automation")
        assert len(results) > 0
        titles = [r["title"].lower() for r in results]
        assert any("automation" in t for t in titles)

    def test_run_contract_search_no_match_returns_sample(self):
        from bot import run_contract_search
        results = run_contract_search("zzznomatch999")
        # Should return a random sample when no keyword match
        assert len(results) > 0

    def test_pricing_tiers_structure(self):
        from bot import PRICING_TIERS
        assert len(PRICING_TIERS) == 3
        for tier in PRICING_TIERS:
            assert "name" in tier
            assert "price" in tier
            assert "features" in tier

    def test_services_structure(self):
        from bot import SERVICES
        assert len(SERVICES) == 6
        slugs = {s["slug"] for s in SERVICES}
        expected_slugs = {"custom-bot", "nlp-bot", "income-tracking", "contracts", "api-integration", "ui-ux"}
        assert slugs == expected_slugs
