"""
Tests for bots/ai-models-integration/tiers.py and
bots/ai-models-integration/ai_models_integration.py
"""

import sys
import os

# Allow imports from the ai-models-integration directory
AI_MODELS_DIR = os.path.join(
    os.path.dirname(__file__), '..', 'bots', 'ai-models-integration'
)
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, os.path.join(AI_MODELS_DIR, 'models'))

# Clear cached modules to prevent cross-test sys.modules pollution.
# These modules import 'tiers' at load time; if 'tiers' was previously cached
# from another bot's directory, their Tier class identity would mismatch.
_MODULES_TO_CLEAR = ('tiers', 'registry', 'models.registry', 'ai_models_integration')
for _mod in _MODULES_TO_CLEAR:
    sys.modules.pop(_mod, None)

import pytest
from tiers import (
    Tier, TierConfig, TIER_CATALOGUE, get_tier_config, get_upgrade_path,
    list_tiers, FREE_MODELS, PRO_MODELS, ENTERPRISE_MODELS,
    FEATURE_BASIC_INFERENCE, FEATURE_BATCH_PROCESSING,
    FEATURE_FINE_TUNING, FEATURE_CUSTOM_MODELS, FEATURE_SLA_GUARANTEE,
    NLP_GPT35, NLP_GPT4, CV_CLIP, GEN_GPT4V,
)
from models.registry import (
    MODEL_REGISTRY, get_model_info, list_models_for_tier,
    list_models_by_category,
)
from ai_models_integration import (
    AIModelsIntegration, TierAccessError, RequestLimitExceededError,
)


# -----------------------------------------------------------------------
# Tier catalogue tests
# -----------------------------------------------------------------------

class TestTierCatalogue:
    def test_all_tiers_exist(self):
        for tier in Tier:
            assert tier.value in TIER_CATALOGUE

    def test_free_tier_price_is_zero(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.price_usd_monthly == 0.0

    def test_pro_tier_price(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.price_usd_monthly == 49.0

    def test_enterprise_tier_price(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.price_usd_monthly == 299.0

    def test_enterprise_is_unlimited(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.is_unlimited()

    def test_free_has_request_limit(self):
        cfg = get_tier_config(Tier.FREE)
        assert not cfg.is_unlimited()
        assert cfg.requests_per_month == 500

    def test_pro_has_request_limit(self):
        cfg = get_tier_config(Tier.PRO)
        assert not cfg.is_unlimited()
        assert cfg.requests_per_month == 10_000

    def test_paid_tiers_have_more_models_than_free(self):
        free = get_tier_config(Tier.FREE)
        pro = get_tier_config(Tier.PRO)
        ent = get_tier_config(Tier.ENTERPRISE)
        assert len(pro.models_allowed) > len(free.models_allowed)
        assert len(ent.models_allowed) >= len(pro.models_allowed)

    def test_pro_models_superset_of_free(self):
        assert set(FREE_MODELS).issubset(set(PRO_MODELS))

    def test_enterprise_models_superset_of_pro(self):
        assert set(PRO_MODELS).issubset(set(ENTERPRISE_MODELS))

    def test_feature_inclusion(self):
        free_cfg = get_tier_config(Tier.FREE)
        pro_cfg = get_tier_config(Tier.PRO)
        ent_cfg = get_tier_config(Tier.ENTERPRISE)
        assert free_cfg.has_feature(FEATURE_BASIC_INFERENCE)
        assert pro_cfg.has_feature(FEATURE_BATCH_PROCESSING)
        assert pro_cfg.has_feature(FEATURE_FINE_TUNING)
        assert ent_cfg.has_feature(FEATURE_CUSTOM_MODELS)
        assert ent_cfg.has_feature(FEATURE_SLA_GUARANTEE)

    def test_free_does_not_have_batch_processing(self):
        free_cfg = get_tier_config(Tier.FREE)
        assert not free_cfg.has_feature(FEATURE_BATCH_PROCESSING)

    def test_can_use_model(self):
        free_cfg = get_tier_config(Tier.FREE)
        assert free_cfg.can_use_model(NLP_GPT35)
        assert not free_cfg.can_use_model(NLP_GPT4)

    def test_list_tiers_ordered(self):
        tiers = list_tiers()
        prices = [t.price_usd_monthly for t in tiers]
        assert prices == sorted(prices)

    def test_upgrade_path_free_to_pro(self):
        next_cfg = get_upgrade_path(Tier.FREE)
        assert next_cfg is not None
        assert next_cfg.tier == Tier.PRO

    def test_upgrade_path_pro_to_enterprise(self):
        next_cfg = get_upgrade_path(Tier.PRO)
        assert next_cfg is not None
        assert next_cfg.tier == Tier.ENTERPRISE

    def test_upgrade_path_enterprise_is_none(self):
        assert get_upgrade_path(Tier.ENTERPRISE) is None


# -----------------------------------------------------------------------
# Model registry tests
# -----------------------------------------------------------------------

class TestModelRegistry:
    def test_registry_not_empty(self):
        assert len(MODEL_REGISTRY) > 0

    def test_get_known_model(self):
        info = get_model_info(NLP_GPT35)
        assert info.model_id == NLP_GPT35
        assert info.display_name == "GPT-3.5 Turbo"
        assert info.min_tier == Tier.FREE

    def test_get_paid_model_metadata(self):
        info = get_model_info(NLP_GPT4)
        assert info.min_tier == Tier.PRO

    def test_get_unknown_model_raises(self):
        with pytest.raises(KeyError):
            get_model_info("nonexistent/model")

    def test_list_models_for_free_tier(self):
        models = list_models_for_tier(Tier.FREE)
        ids = [m.model_id for m in models]
        assert NLP_GPT35 in ids
        assert NLP_GPT4 not in ids
        assert CV_CLIP not in ids

    def test_list_models_for_pro_tier(self):
        models = list_models_for_tier(Tier.PRO)
        ids = [m.model_id for m in models]
        assert NLP_GPT35 in ids
        assert NLP_GPT4 in ids
        assert CV_CLIP not in ids

    def test_list_models_for_enterprise_tier(self):
        models = list_models_for_tier(Tier.ENTERPRISE)
        ids = [m.model_id for m in models]
        assert CV_CLIP in ids
        assert GEN_GPT4V in ids

    def test_models_have_correct_categories(self):
        nlp_models = list_models_by_category("nlp")
        cv_models = list_models_by_category("computer_vision")
        gen_models = list_models_by_category("generative_ai")
        da_models = list_models_by_category("data_analytics")
        assert len(nlp_models) >= 2
        assert len(cv_models) >= 2
        assert len(gen_models) >= 2
        assert len(da_models) >= 2

    def test_paid_upgrade_note_on_free_models(self):
        """Free-tier models should suggest upgrading to access better variants."""
        info = get_model_info(NLP_GPT35)
        assert info.paid_upgrade_note != ""

    def test_enterprise_only_model_has_no_note(self):
        """Top-tier models need no upgrade note."""
        info = get_model_info(CV_CLIP)
        assert info.paid_upgrade_note == ""

    def test_model_input_output_types_populated(self):
        for model_id, info in MODEL_REGISTRY.items():
            assert len(info.input_types) > 0, f"No input_types for {model_id}"
            assert len(info.output_types) > 0, f"No output_types for {model_id}"


# -----------------------------------------------------------------------
# AIModelsIntegration tests
# -----------------------------------------------------------------------

class TestAIModelsIntegration:
    def test_free_client_can_run_free_model(self):
        client = AIModelsIntegration(tier=Tier.FREE)
        result = client.run_model(NLP_GPT35, {"prompt": "Hello"})
        assert result["model_id"] == NLP_GPT35
        assert result["tier"] == Tier.FREE.value
        assert result["output"]["status"] == "success"

    def test_free_client_cannot_run_paid_model(self):
        client = AIModelsIntegration(tier=Tier.FREE)
        with pytest.raises(TierAccessError):
            client.run_model(NLP_GPT4, {"prompt": "Hello"})

    def test_pro_client_can_run_pro_model(self):
        client = AIModelsIntegration(tier=Tier.PRO)
        result = client.run_model(NLP_GPT4, {"prompt": "Hello"})
        assert result["tier"] == Tier.PRO.value

    def test_pro_client_cannot_run_enterprise_model(self):
        client = AIModelsIntegration(tier=Tier.PRO)
        with pytest.raises(TierAccessError):
            client.run_model(CV_CLIP, {"image": "data"})

    def test_enterprise_client_can_run_all_models(self):
        client = AIModelsIntegration(tier=Tier.ENTERPRISE)
        for model_id in ENTERPRISE_MODELS:
            result = client.run_model(model_id, {"input": "test"})
            assert result["output"]["status"] == "success"

    def test_request_counter_increments(self):
        client = AIModelsIntegration(tier=Tier.FREE)
        client.run_model(NLP_GPT35, {"prompt": "a"})
        client.run_model(NLP_GPT35, {"prompt": "b"})
        assert client._request_count == 2

    def test_request_limit_exceeded(self):
        client = AIModelsIntegration(tier=Tier.FREE)
        client._request_count = client.config.requests_per_month
        with pytest.raises(RequestLimitExceededError):
            client.run_model(NLP_GPT35, {"prompt": "over limit"})

    def test_enterprise_no_request_limit(self):
        client = AIModelsIntegration(tier=Tier.ENTERPRISE)
        client._request_count = 1_000_000
        # Should not raise
        result = client.run_model(NLP_GPT35, {"prompt": "high volume"})
        assert result["requests_remaining"] == "unlimited"

    def test_available_models_match_tier(self):
        free_client = AIModelsIntegration(tier=Tier.FREE)
        pro_client = AIModelsIntegration(tier=Tier.PRO)
        assert len(pro_client.available_models()) > len(free_client.available_models())

    def test_available_model_ids_are_strings(self):
        client = AIModelsIntegration(tier=Tier.FREE)
        ids = client.available_model_ids()
        assert all(isinstance(i, str) for i in ids)

    def test_describe_tier_returns_string(self):
        client = AIModelsIntegration(tier=Tier.FREE)
        output = client.describe_tier()
        assert "Free" in output
        assert "$0.00" in output

    def test_show_upgrade_path_free(self):
        client = AIModelsIntegration(tier=Tier.FREE)
        output = client.show_upgrade_path()
        assert "Pro" in output

    def test_show_upgrade_path_enterprise(self):
        client = AIModelsIntegration(tier=Tier.ENTERPRISE)
        output = client.show_upgrade_path()
        assert "already on the top-tier" in output

    def test_compare_tiers_output(self):
        output = AIModelsIntegration.compare_tiers()
        assert "Free" in output
        assert "Pro" in output
        assert "Enterprise" in output

    def test_unknown_model_raises_key_error(self):
        client = AIModelsIntegration(tier=Tier.ENTERPRISE)
        with pytest.raises(KeyError):
            client.run_model("unknown/model", {})

    def test_result_contains_expected_keys(self):
        client = AIModelsIntegration(tier=Tier.PRO)
        result = client.run_model(NLP_GPT4, {"prompt": "test"})
        for key in ("model_id", "tier", "input", "output", "requests_used",
                    "requests_remaining"):
            assert key in result
