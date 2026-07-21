"""
Tests for the DreamCo Model Router System.

Covers:
  1.  ModelRouter — routing table, execute(), helpers
  2.  TaskClassifier — classify(), explain(), list_task_types()
  3.  RouterAgent — run(), explain(), get_summary()
  4.  ResourceManager — use(), built-in tools, register_tool()
  5.  agent_runner.run() — full end-to-end cycle
  6.  Bot Library registration
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

# ---------------------------------------------------------------------------
# Module imports
# ---------------------------------------------------------------------------
from ai.model_router import ModelRouter, DEFAULT_ROUTES, PROVIDER_INFO
from ai.task_classifier import TaskClassifier
from ai.router_agent import RouterAgent
from tools.resource_manager import ResourceManager
from ai.agent_runner import run as agent_run


# ===========================================================================
# 1. ModelRouter tests
# ===========================================================================

class TestModelRouter:
    def setup_method(self):
        self.router = ModelRouter()

    # --- route() ---

    def test_route_coding_returns_anthropic(self):
        assert self.router.route("coding") == "anthropic"

    def test_route_general_returns_openai(self):
        assert self.router.route("general") == "openai"

    def test_route_vision_returns_google(self):
        assert self.router.route("vision") == "google"

    def test_route_cheap_returns_mistral(self):
        assert self.router.route("cheap") == "mistral"

    def test_route_search_returns_cohere(self):
        assert self.router.route("search") == "cohere"

    def test_route_real_time_returns_xai(self):
        assert self.router.route("real_time") == "xai"

    def test_route_unknown_returns_default(self):
        assert self.router.route("unknown_task") == "openai"

    def test_route_custom_default_provider(self):
        router = ModelRouter(default_provider="mistral")
        assert router.route("unknown") == "mistral"

    # --- execute() ---

    def test_execute_returns_dict_with_required_keys(self):
        result = self.router.execute("coding", "write a function")
        assert "model" in result
        assert "task_type" in result
        assert "response" in result

    def test_execute_model_matches_route(self):
        result = self.router.execute("vision", "analyse this image")
        assert result["model"] == "google"

    def test_execute_task_type_preserved(self):
        result = self.router.execute("search", "find documents")
        assert result["task_type"] == "search"

    def test_execute_response_contains_prompt(self):
        prompt = "build an app"
        result = self.router.execute("coding", prompt)
        assert prompt in result["response"]

    # --- add_route() ---

    def test_add_route_registers_new_type(self):
        self.router.add_route("translation", "deepl")
        assert self.router.route("translation") == "deepl"

    def test_add_route_overrides_existing(self):
        self.router.add_route("coding", "openai")
        assert self.router.route("coding") == "openai"

    # --- list_routes() ---

    def test_list_routes_returns_dict(self):
        routes = self.router.list_routes()
        assert isinstance(routes, dict)
        assert "coding" in routes

    def test_list_routes_is_copy(self):
        routes = self.router.list_routes()
        routes["coding"] = "hacked"
        assert self.router.route("coding") == "anthropic"

    # --- get_provider_info() ---

    def test_get_provider_info_known_provider(self):
        info = self.router.get_provider_info("anthropic")
        assert "strengths" in info
        assert "best_for" in info

    def test_get_provider_info_unknown_provider(self):
        info = self.router.get_provider_info("nonexistent")
        assert info == {}

    # --- get_summary() ---

    def test_get_summary_structure(self):
        summary = self.router.get_summary()
        assert "total_routes" in summary
        assert "routes" in summary
        assert "default_provider" in summary
        assert "supported_providers" in summary

    def test_get_summary_route_count(self):
        summary = self.router.get_summary()
        assert summary["total_routes"] == len(DEFAULT_ROUTES)

    # --- custom routes ---

    def test_custom_routes_override_defaults(self):
        router = ModelRouter(routes={"coding": "deepseek"})
        assert router.route("coding") == "deepseek"

    # --- PROVIDER_INFO completeness ---

    def test_all_default_providers_have_info(self):
        for provider in DEFAULT_ROUTES.values():
            assert provider in PROVIDER_INFO, f"Missing PROVIDER_INFO entry for {provider}"


# ===========================================================================
# 2. TaskClassifier tests
# ===========================================================================

class TestTaskClassifier:
    def setup_method(self):
        self.clf = TaskClassifier()

    # --- classify() coding ---

    def test_classify_code_keyword(self):
        assert self.clf.classify("write some code") == "coding"

    def test_classify_build_keyword(self):
        assert self.clf.classify("build a lead generation system") == "coding"

    def test_classify_debug_keyword(self):
        assert self.clf.classify("debug this error") == "coding"

    def test_classify_implement_keyword(self):
        assert self.clf.classify("implement a REST API") == "coding"

    # --- classify() vision ---

    def test_classify_image_keyword(self):
        assert self.clf.classify("analyse this image") == "vision"

    def test_classify_video_keyword(self):
        assert self.clf.classify("process the video file") == "vision"

    def test_classify_ocr_keyword(self):
        assert self.clf.classify("run ocr on this document") == "vision"

    # --- classify() cheap ---

    def test_classify_cheap_keyword(self):
        assert self.clf.classify("use a cheap model") == "cheap"

    def test_classify_budget_keyword(self):
        assert self.clf.classify("budget-friendly response") == "cheap"

    # --- classify() search ---

    def test_classify_search_keyword(self):
        assert self.clf.classify("search for documents") == "search"

    def test_classify_database_keyword(self):
        assert self.clf.classify("query the database") == "search"

    def test_classify_rag_keyword(self):
        assert self.clf.classify("run a rag pipeline") == "search"

    # --- classify() real_time ---

    def test_classify_live_keyword(self):
        assert self.clf.classify("get live trending topics") == "real_time"

    def test_classify_trend_keyword(self):
        assert self.clf.classify("what are the current trends") == "real_time"

    def test_classify_news_keyword(self):
        assert self.clf.classify("breaking news today") == "real_time"

    # --- classify() general (default) ---

    def test_classify_general_no_keyword(self):
        assert self.clf.classify("summarise this paragraph") == "general"

    def test_classify_empty_string(self):
        assert self.clf.classify("") == "general"

    # --- case insensitivity ---

    def test_classify_case_insensitive(self):
        assert self.clf.classify("CODE this feature") == "coding"

    # --- explain() ---

    def test_explain_coding_task(self):
        result = self.clf.explain("build a scraper")
        assert result["task_type"] == "coding"
        assert result["matched_keyword"] == "build"

    def test_explain_general_task(self):
        result = self.clf.explain("say hello")
        assert result["task_type"] == "general"
        assert result["matched_keyword"] is None

    def test_explain_contains_task(self):
        task = "generate a report"
        result = self.clf.explain(task)
        assert result["task"] == task

    # --- list_task_types() ---

    def test_list_task_types_includes_general(self):
        assert "general" in self.clf.list_task_types()

    def test_list_task_types_includes_coding(self):
        assert "coding" in self.clf.list_task_types()

    # --- custom default ---

    def test_custom_default_task_type(self):
        clf = TaskClassifier(default_task_type="misc")
        assert clf.classify("random input") == "misc"


# ===========================================================================
# 3. RouterAgent tests
# ===========================================================================

class TestRouterAgent:
    def setup_method(self):
        self.agent = RouterAgent()

    # --- run() ---

    def test_run_returns_dict_with_required_keys(self):
        result = self.agent.run("build an API")
        for key in ("task", "task_type", "model", "response"):
            assert key in result

    def test_run_coding_task_uses_anthropic(self):
        result = self.agent.run("write a Python function")
        assert result["model"] == "anthropic"
        assert result["task_type"] == "coding"

    def test_run_vision_task_uses_google(self):
        result = self.agent.run("analyse the image")
        assert result["model"] == "google"

    def test_run_search_task_uses_cohere(self):
        result = self.agent.run("find data in the knowledge base")
        assert result["model"] == "cohere"

    def test_run_real_time_task_uses_xai(self):
        result = self.agent.run("get live news feed")
        assert result["model"] == "xai"

    def test_run_general_task_uses_openai(self):
        result = self.agent.run("give me a summary")
        assert result["model"] == "openai"

    def test_run_task_preserved_in_result(self):
        task = "do something interesting"
        result = self.agent.run(task)
        assert result["task"] == task

    # --- explain() ---

    def test_explain_returns_provider_info(self):
        result = self.agent.explain("code a bot")
        assert "provider_best_for" in result
        assert "provider_strengths" in result

    def test_explain_matched_keyword(self):
        result = self.agent.explain("build something")
        assert result["matched_keyword"] == "build"

    # --- get_summary() ---

    def test_get_summary_contains_router_and_classifier(self):
        summary = self.agent.get_summary()
        assert "router" in summary
        assert "classifier_task_types" in summary

    # --- custom components ---

    def test_custom_router_used(self):
        custom_router = ModelRouter(routes={"coding": "deepseek"})
        agent = RouterAgent(router=custom_router)
        result = agent.run("code this feature")
        assert result["model"] == "deepseek"

    def test_custom_classifier_used(self):
        custom_clf = TaskClassifier(default_task_type="general")
        agent = RouterAgent(classifier=custom_clf)
        result = agent.run("some random task")
        assert result["task_type"] == "general"


# ===========================================================================
# 4. ResourceManager tests
# ===========================================================================

class TestResourceManager:
    def setup_method(self):
        self.rm = ResourceManager()

    # --- use() dispatching ---

    def test_use_returns_none_for_unknown_tool(self):
        result = self.rm.use("nonexistent_tool", {})
        assert result is None

    # --- send_email ---

    def test_send_email_status_sent(self):
        result = self.rm.use("email", {"email": "test@example.com"})
        assert result["status"] == "sent"

    def test_send_email_recipient_preserved(self):
        result = self.rm.use("email", {"email": "user@domain.com"})
        assert result["recipient"] == "user@domain.com"

    def test_send_email_tool_key(self):
        result = self.rm.use("email", {"email": "x@y.com"})
        assert result["tool"] == "email"

    def test_send_email_subject_default(self):
        result = self.rm.use("email", {"email": "a@b.com"})
        assert "subject" in result

    def test_send_email_subject_custom(self):
        result = self.rm.use("email", {"email": "a@b.com", "subject": "Hello!"})
        assert result["subject"] == "Hello!"

    # --- save_crm ---

    def test_save_crm_status_saved(self):
        result = self.rm.use("crm", {"name": "Alice", "email": "alice@example.com"})
        assert result["status"] == "saved"

    def test_save_crm_record_preserved(self):
        payload = {"name": "Bob", "company": "Acme"}
        result = self.rm.use("crm", payload)
        assert result["record"] == payload

    def test_save_crm_tool_key(self):
        result = self.rm.use("crm", {})
        assert result["tool"] == "crm"

    # --- process_payment ---

    def test_process_payment_status_processed(self):
        result = self.rm.use("payment", {"email": "pay@example.com", "amount": 97.0})
        assert result["status"] == "processed"

    def test_process_payment_amount_preserved(self):
        result = self.rm.use("payment", {"email": "pay@example.com", "amount": 297.0})
        assert result["amount"] == 297.0

    def test_process_payment_default_amount_zero(self):
        result = self.rm.use("payment", {"email": "pay@example.com"})
        assert result["amount"] == 0.0

    def test_process_payment_tool_key(self):
        result = self.rm.use("payment", {"email": "x@y.com"})
        assert result["tool"] == "payment"

    # --- fetch_data ---

    def test_fetch_data_status_fetched(self):
        result = self.rm.use("data", {"source": "web", "query": "deals"})
        assert result["status"] == "fetched"

    def test_fetch_data_source_preserved(self):
        result = self.rm.use("data", {"source": "serpapi"})
        assert result["source"] == "serpapi"

    def test_fetch_data_default_source(self):
        result = self.rm.use("data", {})
        assert result["source"] == "default"

    def test_fetch_data_contains_data_key(self):
        result = self.rm.use("data", {})
        assert "data" in result

    def test_fetch_data_tool_key(self):
        result = self.rm.use("data", {})
        assert result["tool"] == "data"

    # --- list_tools() ---

    def test_list_tools_returns_list(self):
        tools = self.rm.list_tools()
        assert isinstance(tools, list)

    def test_list_tools_contains_builtins(self):
        tools = self.rm.list_tools()
        for name in ("email", "crm", "payment", "data"):
            assert name in tools

    # --- register_tool() ---

    def test_register_tool_callable(self):
        called = []

        def my_tool(payload):
            called.append(payload)
            return {"ok": True}

        self.rm.register_tool("my_tool", my_tool)
        result = self.rm.use("my_tool", {"x": 1})
        assert result == {"ok": True}
        assert called == [{"x": 1}]

    def test_register_tool_appears_in_list(self):
        self.rm.register_tool("sms", lambda p: None)
        assert "sms" in self.rm.list_tools()

    # --- extra_tools via constructor ---

    def test_extra_tools_constructor(self):
        extra = {"custom": lambda p: {"custom": True}}
        rm = ResourceManager(extra_tools=extra)
        assert "custom" in rm.list_tools()
        assert rm.use("custom", {}) == {"custom": True}

    # --- get_summary() ---

    def test_get_summary_structure(self):
        summary = self.rm.get_summary()
        assert "total_tools" in summary
        assert "tools" in summary

    def test_get_summary_count_matches_list(self):
        summary = self.rm.get_summary()
        assert summary["total_tools"] == len(self.rm.list_tools())


# ===========================================================================
# 5. agent_runner.run() — full end-to-end cycle
# ===========================================================================

class TestAgentRunner:
    def test_run_returns_agent_and_action_result(self):
        result = agent_run("build a lead generation system")
        assert "agent_result" in result
        assert "action_result" in result

    def test_run_coding_task(self):
        result = agent_run("implement a Python script")
        ar = result["agent_result"]
        assert ar["task_type"] == "coding"
        assert ar["model"] == "anthropic"

    def test_run_vision_task(self):
        result = agent_run("analyse the uploaded image")
        ar = result["agent_result"]
        assert ar["task_type"] == "vision"
        assert ar["model"] == "google"

    def test_run_general_task_emails(self):
        result = agent_run("plan a marketing strategy", email="boss@dreamco.io")
        action = result["action_result"]
        assert action["tool"] == "email"
        assert action["recipient"] == "boss@dreamco.io"

    def test_run_search_task_fetches_data(self):
        result = agent_run("search for the best CRM tools")
        action = result["action_result"]
        assert action["tool"] == "data"

    def test_run_real_time_task_fetches_feed(self):
        result = agent_run("get live trending topics on Twitter")
        action = result["action_result"]
        assert action["tool"] == "data"
        assert action["source"] == "feed"

    def test_run_preserves_task_text(self):
        task = "build an autonomous sales agent"
        result = agent_run(task)
        assert result["agent_result"]["task"] == task


# ===========================================================================
# 6. Bot Library registration
# ===========================================================================

class TestBotLibraryRegistration:
    def _get_library(self):
        from bots.global_bot_network.bot_library import BotLibrary
        lib = BotLibrary()
        lib.populate_dreamco_bots()
        return lib

    def test_model_router_registered(self):
        lib = self._get_library()
        bot_ids = [b["bot_id"] for b in lib.list_bots()]
        assert "model_router_bot" in bot_ids

    def test_model_router_category_is_ai(self):
        from bots.global_bot_network.bot_library import BotCategory
        lib = self._get_library()
        bots = lib.list_bots(category=BotCategory.AI)
        ids = [b["bot_id"] for b in bots]
        assert "model_router_bot" in ids

    def test_model_router_has_routing_capability(self):
        lib = self._get_library()
        entry = lib.get_bot("model_router_bot")
        assert "model_routing" in entry.capabilities

    def test_model_router_entry_has_display_name(self):
        lib = self._get_library()
        entry = lib.get_bot("model_router_bot")
        assert entry.display_name

    def test_model_router_entry_has_description(self):
        lib = self._get_library()
        entry = lib.get_bot("model_router_bot")
        assert entry.description
