"""
Tests for the GLOBAL AI SOURCES FLOW framework.

Validates:
  1. Individual stage dataclasses (DataIngestionLayer, etc.)
  2. GlobalAISourcesFlow orchestrator (instantiation, validate, run_pipeline)
  3. FrameworkViolationError is raised when constraints are violated
  4. All existing bots are wired to the framework (integration check)
  5. Static analysis checker (tools/check_bot_framework.py)
"""

from __future__ import annotations

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest
from framework import (
    GlobalAISourcesFlow,
    DataIngestionLayer,
    LearningMethodClassifier,
    SandboxTestLab,
    PerformanceAnalytics,
    HybridEvolutionEngine,
    DeploymentEngine,
    ProfitMarketIntelligence,
    GovernanceSecurityLayer,
    FrameworkViolationError,
    FRAMEWORK_VERSION,
    REQUIRED_STAGES,
)


# ===========================================================================
# Framework constants
# ===========================================================================

class TestFrameworkConstants:
    def test_framework_version_is_string(self):
        assert isinstance(FRAMEWORK_VERSION, str)

    def test_framework_version_format(self):
        parts = FRAMEWORK_VERSION.split(".")
        assert len(parts) == 3
        assert all(p.isdigit() for p in parts)

    def test_required_stages_count(self):
        assert len(REQUIRED_STAGES) == 8

    def test_required_stages_contains_governance(self):
        assert "governance_security" in REQUIRED_STAGES

    def test_required_stages_contains_data_ingestion(self):
        assert "data_ingestion" in REQUIRED_STAGES

    def test_required_stages_contains_deployment(self):
        assert "deployment" in REQUIRED_STAGES

    def test_required_stages_contains_profit_market_intelligence(self):
        assert "profit_market_intelligence" in REQUIRED_STAGES

    def test_required_stages_tuple(self):
        assert isinstance(REQUIRED_STAGES, tuple)


# ===========================================================================
# Stage 1 — DataIngestionLayer
# ===========================================================================

class TestDataIngestionLayer:
    def test_default_stage_id(self):
        layer = DataIngestionLayer()
        assert layer.stage_id == "data_ingestion"

    def test_default_sources_not_empty(self):
        layer = DataIngestionLayer()
        assert len(layer.sources) > 0

    def test_default_sources_include_github(self):
        layer = DataIngestionLayer()
        assert "github" in layer.sources

    def test_normalization_enabled_by_default(self):
        assert DataIngestionLayer().normalization_enabled is True

    def test_translation_enabled_by_default(self):
        assert DataIngestionLayer().translation_enabled is True

    def test_ingest_returns_dict(self):
        result = DataIngestionLayer().ingest({"key": "value"})
        assert isinstance(result, dict)

    def test_ingest_stage_key(self):
        result = DataIngestionLayer().ingest({})
        assert result["stage"] == "data_ingestion"

    def test_ingest_preserves_payload(self):
        payload = {"text": "hello"}
        result = DataIngestionLayer().ingest(payload)
        assert result["payload"] == payload

    def test_ingest_sources_present(self):
        result = DataIngestionLayer().ingest({})
        assert "sources_used" in result
        assert isinstance(result["sources_used"], list)


# ===========================================================================
# Stage 2 — LearningMethodClassifier
# ===========================================================================

class TestLearningMethodClassifier:
    def test_default_stage_id(self):
        assert LearningMethodClassifier().stage_id == "learning_classifier"

    def test_supported_methods_not_empty(self):
        clf = LearningMethodClassifier()
        assert len(clf.supported_methods) >= 7

    def test_supported_includes_supervised(self):
        assert "supervised" in LearningMethodClassifier().supported_methods

    def test_supported_includes_federated(self):
        assert "federated_learning" in LearningMethodClassifier().supported_methods

    def test_classify_returns_dict(self):
        clf = LearningMethodClassifier()
        result = clf.classify({"payload": {}}, method="supervised")
        assert isinstance(result, dict)

    def test_classify_stage_key(self):
        clf = LearningMethodClassifier()
        result = clf.classify({}, method="unsupervised")
        assert result["stage"] == "learning_classifier"

    def test_classify_method_recorded(self):
        clf = LearningMethodClassifier()
        for method in clf.supported_methods:
            result = clf.classify({}, method=method)
            assert result["method"] == method

    def test_classify_unknown_method_raises(self):
        clf = LearningMethodClassifier()
        with pytest.raises(FrameworkViolationError):
            clf.classify({}, method="telepathy")

    def test_classify_upstream_present(self):
        clf = LearningMethodClassifier()
        upstream = {"payload": {"x": 1}}
        result = clf.classify(upstream, method="reinforcement")
        assert result["upstream"] == upstream


# ===========================================================================
# Stage 3 — SandboxTestLab
# ===========================================================================

class TestSandboxTestLab:
    def test_default_stage_id(self):
        assert SandboxTestLab().stage_id == "sandbox_test"

    def test_containerized_by_default(self):
        assert SandboxTestLab().containerized is True

    def test_ab_experiments_enabled_by_default(self):
        assert SandboxTestLab().ab_experiments_enabled is True

    def test_adversarial_tests_enabled_by_default(self):
        assert SandboxTestLab().adversarial_tests_enabled is True

    def test_run_tests_returns_dict(self):
        result = SandboxTestLab().run_tests({})
        assert isinstance(result, dict)

    def test_run_tests_stage_key(self):
        result = SandboxTestLab().run_tests({})
        assert result["stage"] == "sandbox_test"

    def test_run_tests_passed_flag(self):
        result = SandboxTestLab().run_tests({})
        assert result["passed"] is True


# ===========================================================================
# Stage 4 — PerformanceAnalytics
# ===========================================================================

class TestPerformanceAnalytics:
    def test_default_stage_id(self):
        assert PerformanceAnalytics().stage_id == "performance_analytics"

    def test_metrics_not_empty(self):
        pa = PerformanceAnalytics()
        assert len(pa.metrics) >= 4

    def test_metrics_include_accuracy(self):
        assert "accuracy" in PerformanceAnalytics().metrics

    def test_metrics_include_global_learning_matrix(self):
        assert "global_learning_matrix" in PerformanceAnalytics().metrics

    def test_analyse_returns_dict(self):
        result = PerformanceAnalytics().analyse({})
        assert isinstance(result, dict)

    def test_analyse_stage_key(self):
        result = PerformanceAnalytics().analyse({})
        assert result["stage"] == "performance_analytics"

    def test_analyse_metrics_computed_list(self):
        result = PerformanceAnalytics().analyse({})
        assert isinstance(result["metrics_computed"], list)
        assert len(result["metrics_computed"]) >= 4


# ===========================================================================
# Stage 5 — HybridEvolutionEngine
# ===========================================================================

class TestHybridEvolutionEngine:
    def test_default_stage_id(self):
        assert HybridEvolutionEngine().stage_id == "hybrid_evolution"

    def test_genetic_algorithms_enabled_by_default(self):
        assert HybridEvolutionEngine().genetic_algorithms_enabled is True

    def test_rl_optimization_enabled_by_default(self):
        assert HybridEvolutionEngine().rl_optimization_enabled is True

    def test_hybrid_model_creation_enabled_by_default(self):
        assert HybridEvolutionEngine().hybrid_model_creation_enabled is True

    def test_evolve_returns_dict(self):
        result = HybridEvolutionEngine().evolve({})
        assert isinstance(result, dict)

    def test_evolve_stage_key(self):
        result = HybridEvolutionEngine().evolve({})
        assert result["stage"] == "hybrid_evolution"


# ===========================================================================
# Stage 6 — DeploymentEngine
# ===========================================================================

class TestDeploymentEngine:
    def test_default_stage_id(self):
        assert DeploymentEngine().stage_id == "deployment"

    def test_continuous_retraining_by_default(self):
        assert DeploymentEngine().continuous_retraining is True

    def test_deploy_returns_dict(self):
        result = DeploymentEngine().deploy({})
        assert isinstance(result, dict)

    def test_deploy_stage_key(self):
        result = DeploymentEngine().deploy({})
        assert result["stage"] == "deployment"

    def test_deploy_deployed_flag(self):
        result = DeploymentEngine().deploy({})
        assert result["deployed"] is True


# ===========================================================================
# Stage 7 — ProfitMarketIntelligence
# ===========================================================================

class TestProfitMarketIntelligence:
    def test_default_stage_id(self):
        assert ProfitMarketIntelligence().stage_id == "profit_market_intelligence"

    def test_verticals_not_empty(self):
        pmi = ProfitMarketIntelligence()
        assert len(pmi.verticals) >= 4

    def test_verticals_include_real_estate(self):
        assert "real_estate" in ProfitMarketIntelligence().verticals

    def test_verticals_include_trading(self):
        assert "trading" in ProfitMarketIntelligence().verticals

    def test_verticals_include_lead_generation(self):
        assert "lead_generation" in ProfitMarketIntelligence().verticals

    def test_apply_returns_dict(self):
        result = ProfitMarketIntelligence().apply({})
        assert isinstance(result, dict)

    def test_apply_stage_key(self):
        result = ProfitMarketIntelligence().apply({})
        assert result["stage"] == "profit_market_intelligence"

    def test_apply_verticals_list(self):
        result = ProfitMarketIntelligence().apply({})
        assert isinstance(result["verticals"], list)


# ===========================================================================
# Stage 8 — GovernanceSecurityLayer
# ===========================================================================

class TestGovernanceSecurityLayer:
    def test_default_stage_id(self):
        assert GovernanceSecurityLayer().stage_id == "governance_security"

    def test_encryption_enabled_by_default(self):
        assert GovernanceSecurityLayer().encryption_enabled is True

    def test_audit_logs_enabled_by_default(self):
        assert GovernanceSecurityLayer().audit_logs_enabled is True

    def test_compliance_checks_enabled_by_default(self):
        assert GovernanceSecurityLayer().compliance_checks_enabled is True

    def test_ai_safety_controls_enabled_by_default(self):
        assert GovernanceSecurityLayer().ai_safety_controls_enabled is True

    def test_secure_returns_dict(self):
        result = GovernanceSecurityLayer().secure({})
        assert isinstance(result, dict)

    def test_secure_stage_key(self):
        result = GovernanceSecurityLayer().secure({})
        assert result["stage"] == "governance_security"

    def test_secure_encryption_flag(self):
        result = GovernanceSecurityLayer().secure({})
        assert result["encryption"] is True

    def test_secure_audit_logs_flag(self):
        result = GovernanceSecurityLayer().secure({})
        assert result["audit_logs"] is True

    def test_secure_ai_safety_controls_flag(self):
        result = GovernanceSecurityLayer().secure({})
        assert result["ai_safety_controls"] is True

    def test_secure_raises_if_encryption_disabled(self):
        gov = GovernanceSecurityLayer(encryption_enabled=False)
        with pytest.raises(FrameworkViolationError):
            gov.secure({})

    def test_secure_raises_if_audit_logs_disabled(self):
        gov = GovernanceSecurityLayer(audit_logs_enabled=False)
        with pytest.raises(FrameworkViolationError):
            gov.secure({})

    def test_secure_raises_if_ai_safety_disabled(self):
        gov = GovernanceSecurityLayer(ai_safety_controls_enabled=False)
        with pytest.raises(FrameworkViolationError):
            gov.secure({})


# ===========================================================================
# GlobalAISourcesFlow orchestrator
# ===========================================================================

class TestGlobalAISourcesFlowInit:
    def test_instantiation_with_bot_name(self):
        flow = GlobalAISourcesFlow(bot_name="TestBot")
        assert flow.bot_name == "TestBot"

    def test_default_bot_name(self):
        flow = GlobalAISourcesFlow()
        assert flow.bot_name == "UnnamedBot"

    def test_all_stage_attributes_present(self):
        flow = GlobalAISourcesFlow()
        assert isinstance(flow.ingestion, DataIngestionLayer)
        assert isinstance(flow.classifier, LearningMethodClassifier)
        assert isinstance(flow.sandbox, SandboxTestLab)
        assert isinstance(flow.analytics, PerformanceAnalytics)
        assert isinstance(flow.evolution, HybridEvolutionEngine)
        assert isinstance(flow.deployment, DeploymentEngine)
        assert isinstance(flow.profit_intel, ProfitMarketIntelligence)
        assert isinstance(flow.governance, GovernanceSecurityLayer)

    def test_get_stages_returns_all_required(self):
        flow = GlobalAISourcesFlow()
        stages = flow.get_stages()
        for stage_id in REQUIRED_STAGES:
            assert stage_id in stages

    def test_repr_contains_bot_name(self):
        flow = GlobalAISourcesFlow(bot_name="Buddy")
        assert "Buddy" in repr(flow)

    def test_repr_contains_version(self):
        flow = GlobalAISourcesFlow()
        assert FRAMEWORK_VERSION in repr(flow)


class TestGlobalAISourcesFlowValidation:
    def test_validate_returns_true(self):
        flow = GlobalAISourcesFlow(bot_name="ValidBot")
        assert flow.validate() is True

    def test_validate_raises_if_encryption_disabled(self):
        flow = GlobalAISourcesFlow()
        flow.governance = GovernanceSecurityLayer(encryption_enabled=False)
        with pytest.raises(FrameworkViolationError, match="encryption"):
            flow.validate()

    def test_validate_raises_if_audit_logs_disabled(self):
        flow = GlobalAISourcesFlow()
        flow.governance = GovernanceSecurityLayer(audit_logs_enabled=False)
        with pytest.raises(FrameworkViolationError, match="audit logs"):
            flow.validate()

    def test_validate_raises_if_compliance_checks_disabled(self):
        flow = GlobalAISourcesFlow()
        flow.governance = GovernanceSecurityLayer(compliance_checks_enabled=False)
        with pytest.raises(FrameworkViolationError, match="compliance checks"):
            flow.validate()

    def test_validate_raises_if_ai_safety_disabled(self):
        flow = GlobalAISourcesFlow()
        flow.governance = GovernanceSecurityLayer(ai_safety_controls_enabled=False)
        with pytest.raises(FrameworkViolationError, match="AI safety"):
            flow.validate()


class TestGlobalAISourcesFlowRunPipeline:
    def test_run_pipeline_returns_dict(self):
        result = GlobalAISourcesFlow(bot_name="TestBot").run_pipeline()
        assert isinstance(result, dict)

    def test_run_pipeline_complete_flag(self):
        result = GlobalAISourcesFlow().run_pipeline()
        assert result["pipeline_complete"] is True

    def test_run_pipeline_framework_version(self):
        result = GlobalAISourcesFlow().run_pipeline()
        assert result["framework_version"] == FRAMEWORK_VERSION

    def test_run_pipeline_bot_name(self):
        result = GlobalAISourcesFlow(bot_name="MyBot").run_pipeline()
        assert result["bot_name"] == "MyBot"

    def test_run_pipeline_result_key_present(self):
        result = GlobalAISourcesFlow().run_pipeline()
        assert "result" in result

    def test_run_pipeline_with_raw_data(self):
        raw = {"domain": "test", "input": "hello"}
        result = GlobalAISourcesFlow().run_pipeline(raw_data=raw)
        assert result["pipeline_complete"] is True

    def test_run_pipeline_default_raw_data_none(self):
        result = GlobalAISourcesFlow().run_pipeline(raw_data=None)
        assert result["pipeline_complete"] is True

    def test_run_pipeline_all_learning_methods(self):
        clf = LearningMethodClassifier()
        for method in clf.supported_methods:
            result = GlobalAISourcesFlow().run_pipeline(learning_method=method)
            assert result["pipeline_complete"] is True

    def test_run_pipeline_invalid_method_raises(self):
        with pytest.raises(FrameworkViolationError):
            GlobalAISourcesFlow().run_pipeline(learning_method="magic")

    def test_run_pipeline_result_has_governance_stage(self):
        result = GlobalAISourcesFlow().run_pipeline()
        assert result["result"]["stage"] == "governance_security"


# ===========================================================================
# Bot integration checks — existing bots must use the framework
# ===========================================================================

class TestGovernmentContractGrantBotFramework:
    def setup_method(self):
        self._inserted_path = os.path.join(REPO_ROOT, "bots", "government-contract-grant-bot")
        sys.path.insert(0, self._inserted_path)
        from government_contract_grant_bot import GovernmentContractGrantBot
        self.BotClass = GovernmentContractGrantBot

    def teardown_method(self):
        if self._inserted_path in sys.path:
            sys.path.remove(self._inserted_path)

    def test_bot_has_flow_attribute(self):
        bot = self.BotClass()
        assert hasattr(bot, "flow")

    def test_flow_is_global_ai_sources_flow(self):
        bot = self.BotClass()
        assert isinstance(bot.flow, GlobalAISourcesFlow)

    def test_flow_validates(self):
        bot = self.BotClass()
        assert bot.flow.validate() is True

    def test_run_returns_pipeline_result(self):
        bot = self.BotClass()
        result = bot.run()
        assert result["pipeline_complete"] is True


class TestAIModelsIntegrationFramework:
    def setup_method(self):
        ai_models_dir = os.path.join(REPO_ROOT, "bots", "ai-models-integration")
        self._inserted_paths = [ai_models_dir, os.path.join(ai_models_dir, "models")]
        for p in self._inserted_paths:
            sys.path.insert(0, p)
        from ai_models_integration import AIModelsIntegration
        self.BotClass = AIModelsIntegration

    def teardown_method(self):
        for p in self._inserted_paths:
            if p in sys.path:
                sys.path.remove(p)

    def test_bot_has_flow_attribute(self):
        bot = self.BotClass()
        assert hasattr(bot, "flow")

    def test_flow_is_global_ai_sources_flow(self):
        bot = self.BotClass()
        assert isinstance(bot.flow, GlobalAISourcesFlow)

    def test_flow_validates(self):
        bot = self.BotClass()
        assert bot.flow.validate() is True


class TestAIChatbotFramework:
    def setup_method(self):
        ai_models_dir = os.path.join(REPO_ROOT, "bots", "ai-models-integration")
        self._inserted_paths = [ai_models_dir, os.path.join(ai_models_dir, "models")]
        for p in self._inserted_paths:
            sys.path.insert(0, p)
        from bots.ai_chatbot.chatbot import Chatbot
        self.BotClass = Chatbot

    def teardown_method(self):
        for p in self._inserted_paths:
            if p in sys.path:
                sys.path.remove(p)

    def test_bot_has_flow_attribute(self):
        bot = self.BotClass()
        assert hasattr(bot, "flow")

    def test_flow_is_global_ai_sources_flow(self):
        bot = self.BotClass()
        assert isinstance(bot.flow, GlobalAISourcesFlow)

    def test_flow_validates(self):
        bot = self.BotClass()
        assert bot.flow.validate() is True


# ===========================================================================
# Static analysis checker
# ===========================================================================

class TestCheckBotFrameworkTool:
    """Validate the tools/check_bot_framework.py static analysis script."""

    def _run_checker(self, extra_args: list[str] | None = None) -> int:
        """Import and run the checker's main() function; return exit code."""
        checker_path = os.path.join(REPO_ROOT, "tools")
        sys.path.insert(0, checker_path)
        from check_bot_framework import main
        args = extra_args or []
        return main(["--path", REPO_ROOT] + args)

    def test_checker_returns_zero_for_compliant_repo(self):
        exit_code = self._run_checker()
        assert exit_code == 0

    def test_checker_no_strict_always_zero(self):
        exit_code = self._run_checker(["--no-strict"])
        assert exit_code == 0

    def test_checker_scan_function_compliant_files(self):
        from pathlib import Path
        from check_bot_framework import scan_directory
        root = Path(REPO_ROOT)
        compliant, violations = scan_directory(root)
        assert violations == [], (
            f"Non-compliant bot files found: {violations}"
        )

    def test_checker_is_bot_file_excludes_init(self):
        from pathlib import Path
        from check_bot_framework import is_bot_file
        assert not is_bot_file(Path("__init__.py"))

    def test_checker_is_bot_file_excludes_tiers(self):
        from pathlib import Path
        from check_bot_framework import is_bot_file
        assert not is_bot_file(Path("tiers.py"))

    def test_checker_is_bot_file_excludes_test_files(self):
        from pathlib import Path
        from check_bot_framework import is_bot_file
        assert not is_bot_file(Path("test_something.py"))

    def test_checker_is_bot_file_accepts_bot_py(self):
        from pathlib import Path
        from check_bot_framework import is_bot_file
        assert is_bot_file(Path("my_bot.py"))

    def test_file_is_compliant_with_marker(self, tmp_path):
        from check_bot_framework import file_is_compliant
        f = tmp_path / "bot.py"
        f.write_text("from framework import GlobalAISourcesFlow\n")
        assert file_is_compliant(f) is True

    def test_file_is_compliant_without_marker(self, tmp_path):
        from check_bot_framework import file_is_compliant
        f = tmp_path / "bot.py"
        f.write_text("print('hello world')\n")
        assert file_is_compliant(f) is False

    def test_file_is_compliant_with_comment_marker(self, tmp_path):
        from check_bot_framework import file_is_compliant
        f = tmp_path / "bot.py"
        f.write_text("# GLOBAL AI SOURCES FLOW\nprint('hi')\n")
        assert file_is_compliant(f) is True
