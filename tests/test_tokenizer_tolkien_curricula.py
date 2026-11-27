import unittest
from tools.audit_tokenizer_tolkien_curricula import audit


def fixtures():
    tokenizer={"schema":"dreamco.buddy_tokenizer_curriculum.v1","status":"curriculum_ready_training_not_executed",
        "lessons":[{"id":f"tok-{i:02d}","title":"lesson","outcome":"outcome","lab":"lab","assessment":"assessment"} for i in range(1,13)],
        "course_references":[{"url":"https://example.org","rights":"link only"} for _ in range(4)],
        "gates":{key:"required" for key in ("rights","evaluation","artifact","model_compatibility","compute","release")},
        "mastery":{"reading_alone_is_not_mastery":True,"tokenizer_training_is_not_model_weight_training":True}}
    tolkien={"schema":"dreamco.tolkien_study_track.v1",
        "rights_policy":{"copyrighted_tolkien_text_ingestion":False,"training_on_copyrighted_tolkien_text":False,
            "verbatim_text_reproduction":False,"unknown_rights":"BLOCK"},
        "curriculum":[{"id":f"area-{i}","lessons":["lesson"],"practice":"original"} for i in range(8)],
        "extended_study_path":[{"id":f"tolkien-adv-{i:02d}","title":"unit","outcome":"outcome","lab":"lab",
            "assessment":"assessment","rights_gate":"item-level rights review"} for i in range(1,13)],
        "course_integration":{"status":"NEEDS_USER_SUPPLIED_COURSE_REFERENCE","url":None},
        "mastery_policy":{"reading_or_catalog_discovery_is_mastery":False,"unknown_rights":"BLOCKED"}}
    return tokenizer,tolkien


class TokenizerTolkienCurriculumAuditTests(unittest.TestCase):
    def test_both_curricula_pass_structural_and_rights_checks(self):
        report=audit(*fixtures())
        self.assertEqual(report["status"],"curricula_valid_training_and_mastery_pending")
        self.assertEqual(report["tokenizer_lessons"],12)
        self.assertEqual(report["tolkien_extended_units"],12)
        self.assertFalse(report["mastery_awarded"])

    def test_tokenizer_missing_lesson_is_reported(self):
        tokenizer,tolkien=fixtures()
        tokenizer["lessons"].pop()
        self.assertTrue(any("exactly 12" in e for e in audit(tokenizer,tolkien)["errors"]))

    def test_copyrighted_text_ingestion_cannot_be_enabled(self):
        tokenizer,tolkien=fixtures()
        tolkien["rights_policy"]["copyrighted_tolkien_text_ingestion"]=True
        self.assertTrue(any("copyrighted_tolkien_text_ingestion=false" in e for e in audit(tokenizer,tolkien)["errors"]))

    def test_missing_tolkien_rights_gate_is_reported(self):
        tokenizer,tolkien=fixtures()
        tolkien["extended_study_path"][0]["rights_gate"]=""
        self.assertTrue(any("rights_gate" in e for e in audit(tokenizer,tolkien)["errors"]))

    def test_unapproved_course_reference_is_not_invented(self):
        tokenizer,tolkien=fixtures()
        tolkien["course_integration"]["url"]="https://example.org/unapproved"
        self.assertTrue(any("must remain empty" in e for e in audit(tokenizer,tolkien)["errors"]))


if __name__=="__main__": unittest.main()
