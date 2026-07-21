"""
Unit tests for Dreamcobot modules.
Each test class is grouped by bot category to support incremental,
per-category test runs (e.g. ``pytest -k app_bot``).
"""
import importlib.util
import os
import sys

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")

# The government-contract-grant-bot directory uses hyphens (not a valid Python
# package name), so we load it explicitly via importlib.
_GOV_BOT_PATH = os.path.join(
    _REPO_ROOT,
    "bots",
    "government-contract-grant-bot",
    "government_contract_grant_bot.py",
)
_spec = importlib.util.spec_from_file_location("government_contract_grant_bot", _GOV_BOT_PATH)
_gov_bot_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_gov_bot_module)
GovernmentContractGrantBot = _gov_bot_module.GovernmentContractGrantBot


# ---------------------------------------------------------------------------
# Government Contract & Grant Bot
# ---------------------------------------------------------------------------

class TestGovernmentContractGrantBot:
    """Tests for the GovernmentContractGrantBot (bots/government-contract-grant-bot)."""

    @pytest.fixture(autouse=True)
    def _bot(self):
        self.bot = GovernmentContractGrantBot()

    def test_initialization(self):
        assert self.bot is not None

    def test_start(self, capsys):
        self.bot.start()
        captured = capsys.readouterr()
        assert "starting" in captured.out.lower()

    def test_process_contracts(self, capsys):
        self.bot.process_contracts()
        captured = capsys.readouterr()
        assert "contract" in captured.out.lower()

    def test_process_grants(self, capsys):
        self.bot.process_grants()
        captured = capsys.readouterr()
        assert "grant" in captured.out.lower()

    def test_run(self, capsys):
        self.bot.run()
        captured = capsys.readouterr()
        assert captured.out  # something was printed

    def test_conversational_data_keywords(self, conversational_data):
        """Verify the pre-loaded data includes keywords relevant to this bot."""
        assert "contract_keywords" in conversational_data
        assert "contract" in conversational_data["contract_keywords"]
        assert "grant" in conversational_data["contract_keywords"]


# ---------------------------------------------------------------------------
# App Bots (app_bot marker enables incremental filtering)
# ---------------------------------------------------------------------------

@pytest.mark.app_bot
class TestAppBots:
    """Smoke tests for App_bots category."""

    def test_app_bot_greeting(self, conversational_data):
        assert "Hello" in conversational_data["greetings"]

    def test_app_bot_commands(self, conversational_data):
        assert "help" in conversational_data["bot_commands"]


# ---------------------------------------------------------------------------
# Business Bots
# ---------------------------------------------------------------------------

@pytest.mark.business_bot
class TestBusinessBots:
    """Smoke tests for Business_bots category."""

    def test_business_bot_commands(self, conversational_data):
        assert "start" in conversational_data["bot_commands"]

    def test_business_bot_affirmations(self, conversational_data):
        assert len(conversational_data["affirmations"]) > 0


# ---------------------------------------------------------------------------
# Fiverr Bots
# ---------------------------------------------------------------------------

@pytest.mark.fiverr_bot
class TestFiverrBots:
    """Smoke tests for Fiverr_bots category."""

    def test_fiverr_bot_queries(self, conversational_data):
        assert len(conversational_data["queries"]) > 0


# ---------------------------------------------------------------------------
# Marketing Bots
# ---------------------------------------------------------------------------

@pytest.mark.marketing_bot
class TestMarketingBots:
    """Smoke tests for Marketing_bots category."""

    def test_marketing_bot_greetings(self, conversational_data):
        assert len(conversational_data["greetings"]) > 0


# ---------------------------------------------------------------------------
# Occupational Bots
# ---------------------------------------------------------------------------

@pytest.mark.occupational_bot
class TestOccupationalBots:
    """Smoke tests for Occupational_bots category."""

    def test_occupational_bot_queries(self, conversational_data):
        assert "Help me" in conversational_data["queries"]


# ---------------------------------------------------------------------------
# Real Estate Bots
# ---------------------------------------------------------------------------

@pytest.mark.real_estate_bot
class TestRealEstateBots:
    """Smoke tests for Real_Estate_bots category."""

    def test_real_estate_bot_farewells(self, conversational_data):
        assert "Goodbye" in conversational_data["farewells"]
