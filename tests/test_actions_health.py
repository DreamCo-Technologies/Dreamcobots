import json
import unittest
from unittest.mock import patch

from tools.audit_actions_health import MAX_MAJOR, OUT_JSON, OUT_MD, PUBLIC_JSON, main


class ActionsHealthAuditTest(unittest.TestCase):
    def test_current_official_action_baseline_is_recognized(self) -> None:
        self.assertEqual(MAX_MAJOR["actions/checkout"], 7)
        self.assertEqual(MAX_MAJOR["actions/upload-pages-artifact"], 5)

    def test_markdown_report_is_written_as_utf8(self) -> None:
        with patch("tools.audit_actions_health.Path.write_text", autospec=True) as write_text:
            main()

        self.assertTrue(any(call.args[0] == OUT_MD and call.kwargs.get("encoding") == "utf-8" for call in write_text.call_args_list))

    def test_all_workflows_pass_the_static_health_gate(self) -> None:
        result = main()
        report = json.loads(OUT_JSON.read_text(encoding="utf-8"))
        blockers = [
            f"{item['workflow']}: {error}"
            for item in report["findings"]
            for error in item.get("errors", [])
        ]
        self.assertEqual(result, 0, "Static Actions blockers:\n" + "\n".join(blockers))
        self.assertEqual(report["critical_error_count"], 0)
        self.assertEqual(report["warning_count"], 0)
        self.assertEqual(report["schema"], "dreamco.actions_health.v2")
        self.assertEqual(report["summary"]["static_passing_workflows"], report["workflow_count"])
        self.assertEqual(report["summary"]["runtime_unknown_workflows"], report["workflow_count"])
        self.assertTrue(all(item["what_happens"] for item in report["findings"]))
        self.assertTrue(all(item["goal"] for item in report["findings"]))
        self.assertTrue(all(item["runtime_status"] == "unknown_until_run_evidence_loaded" for item in report["findings"]))
        public_report = json.loads(PUBLIC_JSON.read_text(encoding="utf-8"))
        self.assertEqual(public_report, report)
        self.assertEqual(len(report["findings"]), report["workflow_count"])
        self.assertTrue(all(len(item["upgrades"]) >= 3 for item in report["findings"]))
        self.assertTrue(all(item["github_url"].startswith("https://github.com/DreamCo-Technologies/Dreamcobots/actions/workflows/") for item in report["findings"]))


if __name__ == "__main__":
    unittest.main()
