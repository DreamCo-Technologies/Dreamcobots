import unittest
from pathlib import Path

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
        self.assertNotIn("glob(\"**", source)

    def test_migration_helper_is_idempotence_aware(self) -> None:
        source = (ROOT / "tools/migrate_zod4_compat.py").read_text(encoding="utf-8")
        self.assertIn("elif new in text", source)
        self.assertIn("already_current", source)


if __name__ == "__main__":
    unittest.main()
