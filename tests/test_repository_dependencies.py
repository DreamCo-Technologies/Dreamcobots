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
