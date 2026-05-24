"""
DreamCo OS — E2E Tests: Full Bot Execution Scenario
"""

import asyncio
import pytest
from python_bots.core.base_bot import DreamCoBot
from python_bots.core.lifecycle import BotState
from python_bots.orchestrator import DreamCoOrchestrator
import dreamco_mcp_server as mcp


class FullPlatformBot(DreamCoBot):
    """A complete bot that exercises all platform features."""

    async def run(self) -> dict:
        # Use memory
        self.memory.save("run_start", {"timestamp": "now"})
        self.memory.store_doc("run_doc", "This bot ran successfully")
        self.memory.event("run_started", {"bot": self.name})

        analysis = await self.analyze()
        revenue = await self.monetize()
        self.memory.save("last_result", {**analysis, **revenue})

        return {**analysis, **revenue}

    async def analyze(self) -> dict:
        recalled = self.memory.recall("bot ran", top_k=1)
        return {"analysis": "complete", "memory_results": len(recalled)}

    async def monetize(self) -> dict:
        return {"revenue_usd": 1.50, "credits_earned": 3}

    async def report(self) -> dict:
        history = self.memory.structured.get_run_history(5)
        return {
            "total_runs": len(history),
            "last_result": self.memory.load("last_result"),
        }


class TestEndToEnd:
    @pytest.mark.asyncio
    async def test_full_platform_lifecycle(self):
        bot = FullPlatformBot("e2e_bot")
        orch = DreamCoOrchestrator()
        orch.register(bot)

        # Run
        result = await orch.dispatch("e2e_bot")
        assert result["success"] is True
        assert result["result"]["revenue_usd"] == 1.50

        # Health
        health = bot.health_check()
        assert health["state"] == "IDLE"
        assert health["total_runs"] == 1
        assert health["error_count"] == 0

        # Memory
        last = bot.memory.load("last_result")
        assert last is not None
        assert last["revenue_usd"] == 1.50

        # Report
        report = await bot.report()
        assert report["total_runs"] >= 1

    @pytest.mark.asyncio
    async def test_mcp_full_roundtrip(self):
        bot = FullPlatformBot("mcp_e2e_bot")
        orch = DreamCoOrchestrator()
        orch.register(bot)
        mcp.init_server(orch, {"mcp_e2e_bot": bot})

        # Initialize
        init_resp = await mcp._handle_request({
            "jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}
        })
        assert init_resp["result"]["serverInfo"]["name"] == "dreamco-mcp-server"

        # List tools
        list_resp = await mcp._handle_request({
            "jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}
        })
        tool_names = [t["name"] for t in list_resp["result"]["tools"]]
        assert "run_bot" in tool_names
        assert "list_bots" in tool_names

        # Run bot via MCP
        run_resp = await mcp._handle_request({
            "jsonrpc": "2.0", "id": 3,
            "method": "tools/call",
            "params": {"name": "run_bot", "arguments": {"bot_name": "mcp_e2e_bot"}},
        })
        import json
        result = json.loads(run_resp["result"]["content"][0]["text"])
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_governance_full_pipeline(self):
        from python_bots.governance import PolicyRegistry, BotPolicy, GovernanceAuditLog, PIIDetector

        # Policy
        registry = PolicyRegistry()
        registry.load_from_dict({
            "governed_bot": {
                "max_execution_time": 60,
                "allowed_capabilities": ["web_search"],
                "allow_file_write": False,
            }
        })
        policy = registry.get("governed_bot")

        # Audit log
        audit = GovernanceAuditLog(log_file="/tmp/e2e_audit.jsonl")
        entry_id = audit.record("e2e_test", "policy_checked", "governed_bot", "success")
        entries = audit.query(actor="e2e_test")
        assert any(e["entry_id"] == entry_id for e in entries)

        # PII detection
        detector = PIIDetector()
        clean, findings = detector.scrub("Contact alice@example.com or call 555-123-4567")
        assert "alice@example.com" not in clean
        assert len(findings) == 2

        # Policy enforcement
        from python_bots.governance.policies import PolicyViolationError
        with pytest.raises(PolicyViolationError):
            policy.check_capability("file_write")
