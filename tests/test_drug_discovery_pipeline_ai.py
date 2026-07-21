import sys, os
REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, REPO_ROOT)

TOOL_DIR = os.path.join(REPO_ROOT, 'healthcare-tools', 'drug_discovery_pipeline_ai')
sys.path.insert(0, TOOL_DIR)

import pytest
from drug_discovery_pipeline_ai import DrugDiscoveryPipelineAI

ASPIRIN = {"name": "Aspirin", "molecular_weight": 180, "logp": 1.2,
           "h_bond_donors": 1, "h_bond_acceptors": 4, "tpsa": 63.6}
HEAVY = {"name": "Heavy", "molecular_weight": 600, "logp": 6.5,
         "h_bond_donors": 7, "h_bond_acceptors": 12, "tpsa": 150}


class TestDrugDiscoveryInstantiation:
    def test_default_tier_is_free(self):
        p = DrugDiscoveryPipelineAI()
        assert p.tier == "free"

    def test_pro_tier(self):
        p = DrugDiscoveryPipelineAI(tier="pro")
        assert p.tier == "pro"


class TestScreenCompound:
    def test_aspirin_passes(self):
        p = DrugDiscoveryPipelineAI()
        result = p.screen_compound(ASPIRIN)
        assert result["drug_like"] is True
        assert result["rule_of_five_passed"] is True

    def test_heavy_fails(self):
        p = DrugDiscoveryPipelineAI()
        result = p.screen_compound(HEAVY)
        assert result["rule_of_five_passed"] is False

    def test_violations_listed(self):
        p = DrugDiscoveryPipelineAI()
        result = p.screen_compound(HEAVY)
        assert len(result["violations"]) > 0

    def test_compound_name_in_result(self):
        p = DrugDiscoveryPipelineAI()
        result = p.screen_compound(ASPIRIN)
        assert result["compound"] == "Aspirin"


class TestPredictAdmet:
    def test_free_tier_raises_permission(self):
        p = DrugDiscoveryPipelineAI(tier="free")
        with pytest.raises(PermissionError):
            p.predict_admet(ASPIRIN)

    def test_aspirin_oral_bioavailability(self):
        p = DrugDiscoveryPipelineAI(tier="pro")
        result = p.predict_admet(ASPIRIN)
        assert result["oral_bioavailability"] is True

    def test_result_has_disclaimer(self):
        p = DrugDiscoveryPipelineAI(tier="pro")
        result = p.predict_admet(ASPIRIN)
        assert "disclaimer" in result


class TestScoreTargetDocking:
    def test_free_tier_raises_permission(self):
        p = DrugDiscoveryPipelineAI(tier="free")
        with pytest.raises(PermissionError):
            p.score_target_docking(ASPIRIN, "COX-2")

    def test_returns_score(self):
        p = DrugDiscoveryPipelineAI(tier="pro")
        result = p.score_target_docking(ASPIRIN, "COX-2")
        assert "docking_score_kcal_mol" in result
        assert isinstance(result["docking_score_kcal_mol"], float)

    def test_has_disclaimer(self):
        p = DrugDiscoveryPipelineAI(tier="pro")
        result = p.score_target_docking(ASPIRIN, "COX-2")
        assert "disclaimer" in result


class TestSuggestLeadOptimization:
    def test_free_tier_raises_permission(self):
        p = DrugDiscoveryPipelineAI(tier="free")
        with pytest.raises(PermissionError):
            p.suggest_lead_optimization({"drug_like": True})

    def test_drug_like_suggestions(self):
        p = DrugDiscoveryPipelineAI(tier="pro")
        result = p.suggest_lead_optimization({"drug_like": True})
        assert len(result) > 0

    def test_non_drug_like_suggestions(self):
        p = DrugDiscoveryPipelineAI(tier="pro")
        result = p.suggest_lead_optimization({"drug_like": False})
        assert len(result) > 0
