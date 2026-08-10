import json
import unittest

from tools.audit_actions_health import MAX_MAJOR, OUT_JSON, main


class ActionsHealthAuditTest(unittest.TestCase):
    def test_current_official_action_baseline_is_recognized(self) -> None:
        self.assertEqual(MAX_MAJOR["actions/checkout"], 7)
        self.assertEqual(MAX_MAJOR["actions/upload-pages-artifact"], 5)

    def test_all_workflows_pass_the_static_health_gate(self) -> None:
        self.assertEqual(main(), 0)
        report = json.loads(OUT_JSON.read_text(encoding="utf-8"))
        self.assertEqual(report["critical_error_count"], 0)
        self.assertEqual(report["warning_count"], 0)


if __name__ == "__main__":
    unittest.main()
