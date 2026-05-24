"""
DreamCo OS — Unit Tests: Governance Layer
"""

import pytest
from python_bots.governance.policies import PolicyRegistry, BotPolicy, PolicyViolationError
from python_bots.governance.audit_log import GovernanceAuditLog
from python_bots.governance.quarantine import QuarantineManager
from python_bots.governance.rate_limiter import RateLimiter, RateLimitExceededError
from python_bots.governance.pii_detector import PIIDetector


class TestBotPolicy:
    def test_execution_time_check_passes(self):
        policy = BotPolicy(max_execution_time=60)
        policy.check_execution_time(30)  # Should not raise

    def test_execution_time_check_fails(self):
        policy = BotPolicy(max_execution_time=60)
        with pytest.raises(PolicyViolationError):
            policy.check_execution_time(90)

    def test_allowed_capability_passes(self):
        policy = BotPolicy(allowed_capabilities=["web_search"])
        policy.check_capability("web_search")  # Should not raise

    def test_blocked_capability_raises(self):
        policy = BotPolicy(allowed_capabilities=["web_search"])
        with pytest.raises(PolicyViolationError):
            policy.check_capability("file_write")

    def test_blocked_capability_list(self):
        policy = BotPolicy(blocked_capabilities=["file_write"])
        with pytest.raises(PolicyViolationError):
            policy.check_capability("file_write")

    def test_network_blocked(self):
        policy = BotPolicy(allow_network=False)
        with pytest.raises(PolicyViolationError):
            policy.check_network()

    def test_file_write_blocked(self):
        policy = BotPolicy(allow_file_write=False)
        with pytest.raises(PolicyViolationError):
            policy.check_file_write()

    def test_to_and_from_dict(self):
        policy = BotPolicy(bot_id="my_bot", max_execution_time=120, allow_network=True)
        d = policy.to_dict()
        restored = BotPolicy.from_dict(d)
        assert restored.bot_id == "my_bot"
        assert restored.max_execution_time == 120


class TestPolicyRegistry:
    def test_get_returns_matching_policy(self):
        registry = PolicyRegistry()
        registry.register(BotPolicy(bot_id="specific_bot", max_execution_time=30))
        policy = registry.get("specific_bot")
        assert policy.max_execution_time == 30

    def test_get_falls_back_to_wildcard(self):
        registry = PolicyRegistry()
        registry.register(BotPolicy(bot_id="*", max_execution_time=300))
        policy = registry.get("any_bot")
        assert policy.max_execution_time == 300

    def test_load_from_dict(self):
        registry = PolicyRegistry()
        registry.load_from_dict({
            "test_bot": {"max_execution_time": 45, "allow_file_write": True}
        })
        policy = registry.get("test_bot")
        assert policy.max_execution_time == 45
        assert policy.allow_file_write is True


class TestGovernanceAuditLog:
    def test_record_and_query(self, tmp_path):
        log = GovernanceAuditLog(log_file=str(tmp_path / "audit.jsonl"))
        entry_id = log.record("orchestrator", "bot.started", "my_bot", "success")
        assert entry_id
        entries = log.query(actor="orchestrator")
        assert any(e["entry_id"] == entry_id for e in entries)

    def test_stats(self, tmp_path):
        log = GovernanceAuditLog(log_file=str(tmp_path / "audit2.jsonl"))
        log.record("user", "action", "resource", "success")
        stats = log.stats()
        assert stats["total_entries"] == 1


class TestQuarantineManager:
    def test_quarantine_and_check(self):
        qm = QuarantineManager()
        qm.quarantine("bad_bot", "Too many errors")
        assert qm.is_quarantined("bad_bot")

    def test_release_removes_from_quarantine(self):
        qm = QuarantineManager()
        qm.quarantine("bad_bot", "reason")
        qm.release("bad_bot")
        assert not qm.is_quarantined("bad_bot")

    def test_release_nonexistent_returns_false(self):
        qm = QuarantineManager()
        assert not qm.release("nonexistent")


class TestRateLimiter:
    def test_under_limit_passes(self):
        rl = RateLimiter(default_calls_per_minute=100)
        rl.check_and_record("test_bot")  # Should not raise

    def test_over_limit_raises(self):
        rl = RateLimiter(default_calls_per_minute=2)
        rl.check_and_record("test_bot")
        rl.check_and_record("test_bot")
        with pytest.raises(RateLimitExceededError):
            rl.check("test_bot")

    def test_current_count(self):
        rl = RateLimiter(default_calls_per_minute=100)
        rl.record("my_bot")
        rl.record("my_bot")
        assert rl.current_count("my_bot") == 2


class TestPIIDetector:
    def test_detects_email(self):
        detector = PIIDetector()
        findings = detector.detect("Contact me at alice@example.com")
        assert any(f.pii_type == "email" for f in findings)

    def test_detects_phone(self):
        detector = PIIDetector()
        findings = detector.detect("Call 555-123-4567")
        assert any(f.pii_type == "phone" for f in findings)

    def test_scrub_replaces_pii(self):
        detector = PIIDetector()
        clean, findings = detector.scrub("Email me at bob@example.com")
        assert "bob@example.com" not in clean
        assert "[REDACTED]" in clean

    def test_clean_text_no_findings(self):
        detector = PIIDetector()
        findings = detector.detect("The weather is nice today.")
        assert len(findings) == 0

    def test_has_pii_true(self):
        detector = PIIDetector()
        assert detector.has_pii("My SSN is 123-45-6789")

    def test_has_pii_false(self):
        detector = PIIDetector()
        assert not detector.has_pii("The sky is blue")
