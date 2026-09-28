import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch
from tools import check_repository_dependencies as checker
from tools import generate_repository_test_registry as registry

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

    def test_media_manifest_maps_distribution_names_to_imports(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "requirements-media.txt").write_text("pillow>=10,<12\nchatterbox-tts>=0.1.1\nsoundfile>=0.12,<1\n")
            with patch.object(checker, "ROOT", root):
                imports, manifests = checker.declared_python_roots()
            self.assertEqual(manifests, ["requirements-media.txt"])
            self.assertTrue({"pil", "chatterbox", "soundfile"}.issubset(imports))

    def test_route_inventory_excludes_test_fixtures_but_preserves_real_duplicates(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            files = []
            for name in ("server/routes.ts", "server/extra.ts", "tests/http.ts", "server/routes.test.ts"):
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('app.get("/api/bots", handler);\n')
                files.append(path)
            with patch.object(registry, "ROOT", root):
                routes = registry.scan_routes(files)
            self.assertEqual({row["source"] for row in routes}, {"server/routes.ts", "server/extra.ts"})
            self.assertEqual(len(routes), 2)
            self.assertTrue(all(row["path"] == "/api/bots" for row in routes))

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
