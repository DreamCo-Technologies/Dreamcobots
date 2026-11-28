import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from stages.09_watchtower.adapters import validate_public_https_url
from stages.09_watchtower.cli import _atomic_write
from stages.09_watchtower.engine import Observation, WatchRule, evaluate


class WatchtowerEngineTests(unittest.TestCase):
    def rule(self, **overrides):
        values = {
            "rule_id": "deal-watch",
            "name": "Deal feed",
            "adapter": "manual",
            "target": "fixture://deals",
            "include_any": ["laptop", "monitor"],
            "exclude": ["expired"],
            "max_price": 500,
            "min_score": 50,
        }
        values.update(overrides)
        return WatchRule.from_dict(values)

    def item(self, **overrides):
        values = {
            "item_id": "item-1",
            "title": "Laptop sale",
            "source": "fixture",
            "price": 300,
            "currency": "USD",
        }
        values.update(overrides)
        return Observation.from_dict(values)

    def test_rule_rejects_invalid_interval_and_adapter(self):
        with self.assertRaises(ValueError):
            self.rule(interval_seconds=1)
        with self.assertRaises(ValueError):
            self.rule(adapter="shell")

    def test_keyword_price_and_exclusion_filters(self):
        rule = self.rule()
        self.assertEqual(evaluate([rule], {rule.rule_id: [self.item()]}, now="2026-01-01T00:00:00Z")[0][0].score, 60)
        self.assertEqual(evaluate([rule], {rule.rule_id: [self.item(price=900)]})[0], [])
        self.assertEqual(evaluate([rule], {rule.rule_id: [self.item(title="Expired laptop") ]})[0], [])

    def test_duplicate_fingerprint_is_suppressed_but_price_change_alerts(self):
        rule = self.rule()
        item = self.item()
        alerts, state = evaluate([rule], {rule.rule_id: [item]}, now="2026-01-01T00:00:00Z")
        self.assertEqual(len(alerts), 1)
        self.assertEqual(evaluate([rule], {rule.rule_id: [item]}, state)[0], [])
        changed, _ = evaluate([rule], {rule.rule_id: [self.item(price=250)]}, state)
        self.assertEqual(len(changed), 1)

    def test_state_writer_is_atomic_and_valid_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "nested" / "state.json"
            _atomic_write(str(path), {"ok": True})
            self.assertEqual(json.loads(path.read_text()), {"ok": True})

    def test_public_https_url_policy(self):
        with self.assertRaises(ValueError):
            validate_public_https_url("http://example.com/feed.json")
        with self.assertRaises(ValueError):
            validate_public_https_url("https://127.0.0.1/feed.json")
        with self.assertRaises(ValueError):
            validate_public_https_url("https://user:pass@example.com/feed.json")
        with patch("stages.09_watchtower.adapters.socket.getaddrinfo", return_value=[
            (None, None, None, None, ("10.0.0.5", 443))
        ]):
            with self.assertRaises(ValueError):
                validate_public_https_url("https://private.example/feed.json")


if __name__ == "__main__":
    unittest.main()
