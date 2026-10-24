"""Offline, fail-closed regression tests for the public fiscal evidence adapter."""
import contextlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

MODULE_PATH = Path(__file__).resolve().parents[1] / 'tools' / 'refresh_public_fiscal_data.py'
spec = importlib.util.spec_from_file_location('refresh_public_fiscal_data', MODULE_PATH)
refresh = importlib.util.module_from_spec(spec)
spec.loader.exec_module(refresh)

DEBT = {'data': [{'record_date': '2026-10-23', 'tot_pub_debt_out_amt': '100', 'debt_held_public_amt': '80'}]}
AGENCIES = {'results': [{'agency_id': 123, 'agency_name': 'Example Agency', 'outlay_amount': 4}]}


class FiscalRefreshEvidenceTests(unittest.TestCase):
    def run_refresh(self, debt, agencies, allow_offline=False):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'evidence.json'
            def fake_fetch(url):
                return debt if url == refresh.US_DEBT_URL else agencies
            args = ['refresh_public_fiscal_data.py'] + (['--allow-offline'] if allow_offline else [])
            with patch.object(refresh, 'fetch_json', side_effect=fake_fetch), patch.object(refresh, 'OUT', output), patch.object(refresh, 'ROOT', Path(tmp)), patch.object(sys, 'argv', args), contextlib.redirect_stdout(io.StringIO()) as stdout:
                code = refresh.main()
            return code, json.loads(output.read_text()), json.loads(stdout.getvalue())

    def test_valid_sources_both_verified(self):
        code, payload, status = self.run_refresh(DEBT, AGENCIES)
        self.assertEqual(code, 0)
        self.assertEqual(payload['runtime_verified_source_count'], 2)
        self.assertEqual(payload['failed_source_count'], 0)
        self.assertEqual(status['failed_sources'], [])

    def test_empty_agencies_fail_closed(self):
        code, payload, status = self.run_refresh(DEBT, {'results': []})
        self.assertEqual(code, 1)
        self.assertEqual(payload['runtime_verified_source_count'], 1)
        self.assertEqual(payload['agency_spending_records'], [])
        self.assertEqual(status['failed_sources'], ['us_usaspending'])

    def test_missing_debt_amount_is_not_verified(self):
        code, payload, status = self.run_refresh({'data': [{'record_date': '2026-10-23'}]}, AGENCIES)
        self.assertEqual(code, 1)
        self.assertEqual(payload['runtime_verified_source_count'], 1)
        self.assertEqual(payload['debt_records'], [])
        self.assertEqual(status['failed_sources'], ['us_treasury_debt_to_penny'])

    def test_invalid_agency_row_rejects_entire_batch(self):
        agencies = {'results': [AGENCIES['results'][0], {'agency_id': 124}]}
        code, payload, status = self.run_refresh(DEBT, agencies)
        self.assertEqual(code, 1)
        self.assertEqual(payload['agency_spending_records'], [])
        self.assertEqual(status['failed_sources'], ['us_usaspending'])

    def test_invalid_source_envelopes_are_blocked(self):
        code, payload, status = self.run_refresh({}, {'results': 'not a list'})
        self.assertEqual(code, 1)
        self.assertEqual(payload['runtime_verified_source_count'], 0)
        self.assertEqual(set(status['failed_sources']), {'us_treasury_debt_to_penny', 'us_usaspending'})

    def test_allow_offline_retains_blocked_evidence(self):
        code, payload, status = self.run_refresh({}, {}, allow_offline=True)
        self.assertEqual(code, 0)
        self.assertEqual(payload['failed_source_count'], 2)
        self.assertFalse(status['ok'])


if __name__ == '__main__':
    unittest.main()
