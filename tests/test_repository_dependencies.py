import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch
from tools import check_repository_dependencies as checker

from tools.check_repository_dependencies import (
    audit_dependencies,
    declared_python_roots,
    standard_library_roots,
)


class RepositoryDependencyAuditTest(unittest.TestCase):
    def test_optional_import_does_not_hide_required_import_in_another_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            required = root / "a_required.py"
            optional = root / "z_optional.py"
            required.write_text("import missing_dependency\n")
            optional.write_text("try:\n import missing_dependency\nexcept ImportError:\n pass\n")
            with patch.object(checker, "ROOT", root):
                imports, errors = checker.scan_python_imports([required, optional])
            self.assertIn("missing_dependency", imports)
            self.assertFalse(errors)

    def test_optional_import_does_not_hide_required_import_in_same_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "fixture.py"
            source.write_text(
                "try:\n import missing_dependency\nexcept ImportError:\n pass\n"
                "import missing_dependency\n"
            )
            with patch.object(checker, "ROOT", root):
                imports, errors = checker.scan_python_imports([source])
            self.assertFalse(errors)
            self.assertIn("missing_dependency", imports)

    def test_fallback_and_finally_imports_are_required(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "fixture.py"
            source.write_text(
                "try:\n import optional_package\nexcept ImportError:\n"
                " import required_fallback\nfinally:\n import required_cleanup\n"
            )
            with patch.object(checker, "ROOT", root):
                imports, errors = checker.scan_python_imports([source])
            self.assertFalse(errors)
            self.assertNotIn("optional_package", imports)
            self.assertIn("required_fallback", imports)
            self.assertIn("required_cleanup", imports)

    def test_try_else_import_is_required(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "fixture.py"
            source.write_text(
                "try:\n import optional_package\nexcept ModuleNotFoundError:\n"
                " pass\nelse:\n import required_after_success\n"
            )
            with patch.object(checker, "ROOT", root):
                imports, errors = checker.scan_python_imports([source])
            self.assertFalse(errors)
            self.assertNotIn("optional_package", imports)
            self.assertIn("required_after_success", imports)

    def test_standard_library_discovery_supports_older_python(self) -> None:
        roots = standard_library_roots()
        for module in ("argparse", "json", "pathlib", "sysconfig", "unittest"):
            self.assertIn(module, roots)

    def test_repository_dependency_audit_passes(self) -> None:
        result = audit_dependencies()
        self.assertTrue(result["ok"], result["errors"])

    def test_tool_dependencies_are_declared_without_environment_secrets(self) -> None:
        roots, manifests = declared_python_roots()
        self.assertIn("requirements-tools.txt", manifests)
        self.assertIn("openpyxl", roots)


if __name__ == "__main__":
    unittest.main()
