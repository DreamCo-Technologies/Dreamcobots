from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class BuddyCISafeRepairWorkflowTests(unittest.TestCase):
    def test_node_setup_and_npm_install_cover_every_fleet_generator_event(self):
        workflow = (ROOT / ".github/workflows/buddy-ci-safe-repair.yml").read_text(encoding="utf-8")
        condition = "github.event_name == 'push' || (github.event_name == 'workflow_run' && github.event.workflow_run.name == 'Full System Certification')"
        setup = workflow.index("      - name: Install Node for canonical fleet regeneration")
        install = workflow.index("      - name: Install locked Node dependencies for fleet regeneration")
        generator = workflow.index("      - name: Regenerate canonical fleet end-to-end evidence after certification drift")
        self.assertIn(condition, workflow[setup:install])
        self.assertIn(condition, workflow[install:generator])
        self.assertIn("run: npm ci", workflow[install:generator])

    def test_generator_events_match_dependency_install_events(self):
        workflow = (ROOT / ".github/workflows/buddy-ci-safe-repair.yml").read_text(encoding="utf-8")
        generator = workflow[workflow.index("      - name: Regenerate canonical fleet end-to-end evidence after certification drift"):workflow.index("      - name: Verify repaired indexes and Buddy repair-learning tests")]
        self.assertIn("github.event_name == 'push'", generator)
        self.assertIn("github.event.workflow_run.name == 'Full System Certification'", generator)


if __name__ == "__main__":
    unittest.main()
