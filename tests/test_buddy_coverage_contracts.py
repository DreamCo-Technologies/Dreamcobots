from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]


class BuddyCoverageContractTests(unittest.TestCase):
    def read(self, path):
        return (ROOT / path).read_text(encoding="utf-8")

    def test_coverage_matrix_preserves_full_product_scope(self):
        text = self.read("buddy_os/governance/coverage_matrix.yaml")
        for domain in ("input:", "processing:", "memory:", "debate:", "execution:", "tools:", "bots:", "dashboards:", "skills:", "learning:", "debugging:", "product:", "operations:", "governance:"):
            self.assertIn(domain, text)
        self.assertIn("debugging_work_must_not_hide_product_gaps: true", text)

    def test_debate_schema_requires_dissent_and_evidence(self):
        payload = json.loads(self.read("buddy_os/debate/debate_output.schema.json"))
        self.assertIn("dissent", payload["required"])
        self.assertIn("evidence_requirements", payload["required"])
        self.assertIn("execution_plan", payload["required"])

    def test_skill_contract_requires_benchmarks_and_safety(self):
        text = self.read("buddy_os/skills/skill_registry_contract.yaml")
        self.assertIn("no_verified_skill_without_benchmark: true", text)
        self.assertIn("no_production_skill_without_safety_review: true", text)
        self.assertIn("generate_training_plan: true", text)
        self.assertIn("generate_sandbox_tests: true", text)


if __name__ == "__main__":
    unittest.main()
