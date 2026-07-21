import sys, os
REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, REPO_ROOT)

TOOL_DIR = os.path.join(REPO_ROOT, 'automation-tools', 'workplace_audit_tool')
sys.path.insert(0, TOOL_DIR)

import pytest
from workplace_audit_tool import WorkplaceAuditTool


class TestWorkplaceAuditToolInstantiation:
    def test_default_tier_is_free(self):
        tool = WorkplaceAuditTool()
        assert tool.tier == "free"

    def test_pro_tier(self):
        tool = WorkplaceAuditTool(tier="pro")
        assert tool.tier == "pro"

    def test_enterprise_tier(self):
        tool = WorkplaceAuditTool(tier="enterprise")
        assert tool.tier == "enterprise"

    def test_unknown_tier_falls_back_to_free(self):
        tool = WorkplaceAuditTool(tier="unknown")
        assert tool.tier_config.name == "Free"


class TestRunAudit:
    def test_returns_dict(self):
        tool = WorkplaceAuditTool()
        result = tool.run_audit("office", [])
        assert isinstance(result, dict)

    def test_category_preserved(self):
        tool = WorkplaceAuditTool()
        result = tool.run_audit("warehouse", [])
        assert result["category"] == "warehouse"

    def test_items_audited_count(self):
        items = [{"pillar": "sort", "score": 8}, {"pillar": "shine", "score": 6}]
        tool = WorkplaceAuditTool()
        result = tool.run_audit("lab", items)
        assert result["items_audited"] == 2

    def test_pillar_scores_present(self):
        tool = WorkplaceAuditTool()
        result = tool.run_audit("office", [])
        for pillar in WorkplaceAuditTool.PILLARS:
            assert pillar in result["scores"]

    def test_total_score_with_items(self):
        items = [{"pillar": p, "score": 8} for p in WorkplaceAuditTool.PILLARS]
        tool = WorkplaceAuditTool()
        result = tool.run_audit("office", items)
        assert result["total_score"] == 8.0

    def test_total_score_empty_items(self):
        tool = WorkplaceAuditTool()
        result = tool.run_audit("office", [])
        assert result["total_score"] == 0.0


class TestGenerateScore:
    def test_empty_responses(self):
        tool = WorkplaceAuditTool()
        assert tool.generate_score([]) == 0.0

    def test_full_score(self):
        tool = WorkplaceAuditTool()
        responses = [{"value": 10}] * 5
        assert tool.generate_score(responses) == 100.0

    def test_partial_score(self):
        tool = WorkplaceAuditTool()
        responses = [{"value": 5}] * 4
        assert tool.generate_score(responses) == 50.0


class TestGetRecommendations:
    def test_high_score(self):
        tool = WorkplaceAuditTool()
        recs = tool.get_recommendations(85)
        assert len(recs) > 0
        assert any("maintain" in r.lower() or "kaizen" in r.lower() for r in recs)

    def test_medium_score(self):
        tool = WorkplaceAuditTool()
        recs = tool.get_recommendations(65)
        assert len(recs) > 0

    def test_low_score(self):
        tool = WorkplaceAuditTool()
        recs = tool.get_recommendations(20)
        assert len(recs) > 0

    def test_very_low_score(self):
        tool = WorkplaceAuditTool()
        recs = tool.get_recommendations(10)
        assert len(recs) >= 3
