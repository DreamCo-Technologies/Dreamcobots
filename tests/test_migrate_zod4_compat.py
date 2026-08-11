import unittest
from pathlib import Path

from tools.migrate_zod4_compat import (
    GITHUB_ICON_FILES,
    LOCAL_GITHUB_IMPORT,
    rewrite_github_icon_imports,
)

ROOT = Path(__file__).resolve().parents[1]


class Zod4CompatibilityMigrationTests(unittest.TestCase):
    def test_migration_helper_is_bounded_to_known_files_and_patterns(self) -> None:
        source = (ROOT / "tools/migrate_zod4_compat.py").read_text(encoding="utf-8")
        self.assertIn('"server/fleet-runtime.ts"', source)
        self.assertIn('"server/media-quality-lab.ts"', source)
        self.assertIn('"server/routes.ts"', source)
        self.assertIn('"server/communication-behavior.ts"', source)
        self.assertIn('"tools/generate_buddy_fleet_quality_program.ts"', source)
        self.assertNotIn("rglob", source)
        self.assertNotIn('glob("**', source)
        self.assertEqual(len(GITHUB_ICON_FILES), 5)

    def test_github_icon_rewrite_does_not_cross_unrelated_imports(self) -> None:
        original = '''import { ReactNode } from "react";\nimport { Link } from "wouter";\nimport {\n  Bot,\n  Github,\n  Wrench,\n} from "lucide-react";\nimport ThemeToggle from "@/components/ThemeToggle";\n'''
        migrated = rewrite_github_icon_imports(original)
        self.assertTrue(migrated.startswith(LOCAL_GITHUB_IMPORT + "\n"))
        self.assertIn('import { ReactNode } from "react";', migrated)
        self.assertIn('import { Link } from "wouter";', migrated)
        self.assertIn('import ThemeToggle from "@/components/ThemeToggle";', migrated)
        self.assertIn("  Bot,", migrated)
        self.assertIn("  Wrench,", migrated)
        self.assertNotIn("  Github,", migrated)

    def test_github_icon_rewrite_is_idempotent(self) -> None:
        original = '''import {\n  Bot,\n  Github,\n} from "lucide-react";\n'''
        migrated = rewrite_github_icon_imports(original)
        self.assertEqual(rewrite_github_icon_imports(migrated), migrated)
        self.assertEqual(migrated.count(LOCAL_GITHUB_IMPORT), 1)

    def test_non_github_lucide_import_is_unchanged(self) -> None:
        original = 'import { Bot, Wrench } from "lucide-react";\n'
        self.assertEqual(rewrite_github_icon_imports(original), original)


if __name__ == "__main__":
    unittest.main()
