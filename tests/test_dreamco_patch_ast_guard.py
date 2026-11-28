import unittest

from tools.dreamco_patch_ast_guard import inspect_source


class DreamCoPatchAstGuardTests(unittest.TestCase):
    def test_simple_pure_python_patch_passes_static_preflight(self):
        result = inspect_source("def normalize(value):\n    return str(value).strip()\n")
        self.assertTrue(result["passed"])
        self.assertEqual(result["status"], "PASS_STATIC_PREFLIGHT")
        self.assertFalse(result["execution_performed"])

    def test_dynamic_execution_is_blocked(self):
        result = inspect_source("def run(payload):\n    return eval(payload)\n")
        self.assertFalse(result["passed"])
        self.assertIn("blocked_dynamic_execution", {item["rule"] for item in result["findings"]})

    def test_process_and_network_imports_are_blocked(self):
        result = inspect_source("import subprocess\nimport socket\n")
        rules = {item["rule"] for item in result["findings"]}
        self.assertIn("blocked_import", rules)

    def test_syntax_errors_fail_closed(self):
        result = inspect_source("def broken(:\n")
        self.assertEqual(result["status"], "BLOCKED_SYNTAX_ERROR")
        self.assertFalse(result["passed"])


if __name__ == "__main__":
    unittest.main()
