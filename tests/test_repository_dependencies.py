import unittest

from tools.check_repository_dependencies import audit_dependencies, standard_library_roots


class RepositoryDependencyAuditTest(unittest.TestCase):
    def test_standard_library_discovery_supports_older_python(self) -> None:
        roots = standard_library_roots()
        for module in ("argparse", "json", "pathlib", "sysconfig", "unittest"):
            self.assertIn(module, roots)

    def test_repository_dependency_audit_passes(self) -> None:
        result = audit_dependencies()
        self.assertTrue(result["ok"], result["errors"])


if __name__ == "__main__":
    unittest.main()
