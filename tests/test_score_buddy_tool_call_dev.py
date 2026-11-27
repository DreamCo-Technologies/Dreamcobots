"""Public synthetic tool-call grading only; no real tools or model calls."""
import json
import unittest

from tools.score_buddy_tool_call_dev import score_response


GOOD = '{"name":"weather_read_only","arguments":{"location":"Madison, WI","units":"celsius"}}'


class ToolCallDevTests(unittest.TestCase):
    def test_exact_read_only_call_matches_public_contract(self):
        result = score_response(GOOD)
        self.assertTrue(result["matches_public_read_only_contract"])
        self.assertEqual(result["model_calls"], 0)
        self.assertEqual(result["tools_executed"], 0)
        self.assertFalse(result["permissions_verified"])
        self.assertFalse(result["independent_holdout_verified"])
        self.assertFalse(result["eligible_for_model_promotion"])
        self.assertNotIn("Madison", json.dumps(result))

    def test_reject_unsafe_or_ambiguous_calls(self):
        bad = [
            GOOD.replace("weather_read_only", "weather_write"),
            GOOD.replace("weather_read_only", "Weather_Read_Only"),
            GOOD.replace('"units":"celsius"', '"units":"fahrenheit"'),
            GOOD.replace('"location":"Madison, WI"', '"location":"Chicago, IL"'),
            GOOD.replace('"name":"weather_read_only"', '"name":"weather_read_only","name":"weather_write"'),
            GOOD.replace('"units":"celsius"', '"units":"celsius","units":"fahrenheit"'),
            GOOD[:-1] + ',"permission_scope":"weather.read"}',
            GOOD[:-1] + ',"approval":true}',
            GOOD.replace('"units":"celsius"', '"units":null'),
            GOOD.replace('"units":"celsius"', '"units":NaN'),
            '[]', 'null', 'not json', '{"name":"weather_read_only","arguments":{}}',
            '{"name":"weather_read_only","arguments":' + '[' * 1500 + '0' + ']' * 1500 + '}',
        ]
        for candidate in bad:
            with self.subTest(candidate=candidate[:70]):
                self.assertFalse(score_response(candidate)["matches_public_read_only_contract"])

    def test_invalid_unicode_is_input_error(self):
        with self.assertRaisesRegex(ValueError, "valid UTF-8"):
            score_response("\ud800")

    def test_response_size_bound(self):
        with self.assertRaisesRegex(ValueError, "at most 20000"):
            score_response("x" * 20001)

    def test_public_contract_hash_is_stable_and_does_not_hash_response(self):
        good = score_response(GOOD)
        bad = score_response("private text not to be saved")
        self.assertEqual(good["public_contract_sha256"], bad["public_contract_sha256"])
        self.assertNotIn("private text", json.dumps(bad))
        self.assertNotIn("response_sha256", bad)


if __name__ == "__main__":
    unittest.main()
