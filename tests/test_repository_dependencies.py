import unittest

from tools.check_repository_dependencies import audit_dependencies, declared_python_roots, standard_library_roots


class RepositoryDependencyAuditTest(unittest.TestCase):
    def test_standard_library_discovery_supports_older_python(self) -> None:
        roots = standard_library_roots()
        for module in ("argparse", "json", "pathlib", "sysconfig", "unittest"):
            self.assertIn(module, roots)

    def test_declared_python_roots_include_repository_manifest_dependencies(self) -> None:
        roots = declared_python_roots()
        self.assertIn("openpyxl", roots)

    def test_repository_dependency_audit_passes(self) -> None:
        result = audit_dependencies()
        self.assertTrue(result["ok"], result["errors"])
        self.assertIn("openpyxl", result["declared_python_import_roots"])


if __name__ == "__main__":
    unittest.main()
