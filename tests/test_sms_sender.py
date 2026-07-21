"""Tests for integrations/sms_sender.py"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest
from integrations.sms_sender import SMSSender, SMSRecord


# ---------------------------------------------------------------------------
# Instantiation
# ---------------------------------------------------------------------------

class TestInstantiation:
    def test_mock_mode_when_no_credentials(self):
        sender = SMSSender()
        assert sender.is_mock is True

    def test_mock_forced(self):
        sender = SMSSender(mock=True)
        assert sender.is_mock is True

    def test_from_number_set(self):
        sender = SMSSender(from_number="+15550000000")
        assert sender.from_number == "+15550000000"


# ---------------------------------------------------------------------------
# send_sms (mock mode)
# ---------------------------------------------------------------------------

class TestSendSMS:
    def setup_method(self):
        self.sender = SMSSender(mock=True)

    def test_send_returns_sms_record(self):
        record = self.sender.send_sms("+15551234567", "Hello!")
        assert isinstance(record, SMSRecord)

    def test_mock_status(self):
        record = self.sender.send_sms("+15551234567", "Hi")
        assert record.status == "mock"

    def test_sid_assigned(self):
        record = self.sender.send_sms("+15551234567", "Hi")
        assert record.sid is not None

    def test_to_dict_has_keys(self):
        record = self.sender.send_sms("+15551234567", "Hi")
        d = record.to_dict()
        for key in ("to", "message", "from_number", "status", "sid", "sent_at"):
            assert key in d

    def test_sent_log_grows(self):
        self.sender.send_sms("+15550000001", "msg 1")
        self.sender.send_sms("+15550000002", "msg 2")
        assert len(self.sender.get_sent_log()) == 2


# ---------------------------------------------------------------------------
# send_bulk
# ---------------------------------------------------------------------------

class TestSendBulk:
    def test_bulk_sends_to_all_recipients(self):
        sender = SMSSender(mock=True)
        recipients = ["+15550000001", "+15550000002", "+15550000003"]
        records = sender.send_bulk(recipients, "Bulk message")
        assert len(records) == 3

    def test_all_records_have_mock_status(self):
        sender = SMSSender(mock=True)
        records = sender.send_bulk(["+15550000001", "+15550000002"], "msg")
        for r in records:
            assert r.status == "mock"


# ---------------------------------------------------------------------------
# SMSRecord
# ---------------------------------------------------------------------------

class TestSMSRecord:
    def test_to_dict_structure(self):
        r = SMSRecord(
            to="+15550000001",
            message="Test",
            from_number="+15559999999",
            status="mock",
            sid="MOCK_0001",
        )
        d = r.to_dict()
        assert d["to"] == "+15550000001"
        assert d["status"] == "mock"
