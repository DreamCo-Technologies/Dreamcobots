import unittest

from tools.audit_bootcamp_division_masterbot_coverage import audit


def fixtures():
    bots = [{"id": i, "name": f"Bot{i}"} for i in range(1, 66)]
    domains = [{"domain_id": f"domain{i}", "domain_name": f"Domain{i}",
                "masterbot_id": i if i <= 45 else None,
                "mapping_status": "proposed_exact_name_match" if i <= 45 else "unresolved",
                "owner_approval": None} for i in range(1, 56)]
    owners = [{"masterbot_id": i, "masterbot_name": f"Bot{i}",
               "mapping_status": "proposed_exact_name_match" if i <= 45 else "unresolved",
               "owner_approval": None} for i in range(1, 66)]
    divisions = [{"domain_id": f"domain{i}", "domain_name": f"Domain{i}",
                  "delivery": "shared_ai_model_literacy_foundation",
                  "specialist_assignment": "review_required_before_owner_specific_work"}
                 for i in range(1, 56)]
    assignments = [{"masterbot_id": i, "masterbot_name": f"Bot{i}",
                    "mapping_status": "proposed_exact_name_match" if i <= 45 else "unresolved",
                    "shared_foundation": True, "specialist_ownership_review_required": True}
                   for i in range(1, 66)]
    modules = [{"id": f"LLM25-{i:02d}"} for i in range(1, 19)]
    return (
        {"divisions": bots},
        {"domains": domains, "masterbots": owners},
        {"delivery": {"division_assignments": divisions, "masterbot_assignments": assignments}, "modules": modules},
    )


class DivisionMasterBotCoverageTests(unittest.TestCase):
    def test_all_divisions_and_masterbots_receive_foundation_without_owner_inference(self):
        report = audit(*fixtures())
        self.assertEqual(report["status"], "coverage_present_ownership_pending")
        self.assertEqual(report["canonical_divisions"], 55)
        self.assertEqual(report["masterbot_lanes"], 65)
        self.assertEqual(report["course_modules"], 18)
        self.assertFalse(report["specialist_routing_authorized_by_audit"])

    def test_missing_division_assignment_fails(self):
        registry, crosswalk, course = fixtures()
        course["delivery"]["division_assignments"].pop()
        report = audit(registry, crosswalk, course)
        self.assertTrue(any("exactly 55 divisions" in error for error in report["errors"]))

    def test_unapproved_owner_cannot_bypass_specialist_gate(self):
        registry, crosswalk, course = fixtures()
        course["delivery"]["masterbot_assignments"][0]["specialist_ownership_review_required"] = False
        report = audit(registry, crosswalk, course)
        self.assertTrue(any("bypasses owner review" in error for error in report["errors"]))

    def test_owner_approval_requires_evidence_reference(self):
        registry, crosswalk, course = fixtures()
        crosswalk["domains"][0]["owner_approval"] = True
        report = audit(registry, crosswalk, course)
        self.assertTrue(any("approval lacks evidence" in error for error in report["errors"]))

    def test_module_order_must_be_contiguous(self):
        registry, crosswalk, course = fixtures()
        course["modules"][1]["id"] = "LLM25-03"
        report = audit(registry, crosswalk, course)
        self.assertTrue(any("contiguous" in error for error in report["errors"]))


if __name__ == "__main__":
    unittest.main()
