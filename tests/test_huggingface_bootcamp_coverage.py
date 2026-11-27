import unittest
from tools.audit_huggingface_bootcamp_coverage import audit


def fixtures():
    courses=[{"id":f"course-{i}","title":f"Course {i}","topics":"topics",
              "url":f"https://huggingface.co/learn/course-{i}","training_data_authorized":False,
              "transcript_permission":"not_granted","assessment":"original transfer project"} for i in range(12)]
    modules=[{"id":f"HFEC-{i:02d}","title":f"Module {i}","objective":"objective",
              "practice":"practice","assessment":"assessment","benchmark":"benchmark",
              "status":"DEFINED_NOT_EXECUTED"} for i in range(1,19)]
    families=[{"id":f"task-{i}","family":"family","modality":"text","description":"description"} for i in range(37)]
    learning={"schema":"dreamco.buddy_huggingface_full_learning_map.v1","course_count":12,
        "ecosystem_module_count":18,"official_courses":courses,"ecosystem_modules":modules,
        "division_delivery":{"canonical_divisions":55,"masterbot_lanes":65,"shared_foundation_available_to_all":True}}
    taxonomy={"schema":"dreamco.huggingface_task_taxonomy.v1","task_family_count":37,"task_families":families}
    registry={"schema":"dreamco.buddy_course_track_registry.v1","tracks":[
        {"parser":"huggingface_learning_map","source":"config/buddy-huggingface-full-learning-map.json"},
        {"parser":"huggingface","source":"config/huggingface-task-taxonomy.json"}]}
    return learning,taxonomy,registry


class HuggingFaceBootcampCoverageTests(unittest.TestCase):
    def test_full_catalog_and_internal_routing_are_valid_without_completion_claims(self):
        report=audit(*fixtures())
        self.assertEqual(report["status"],"coverage_catalog_valid_content_study_pending")
        self.assertEqual(report["official_course_count"],12)
        self.assertEqual(report["ecosystem_module_count"],18)
        self.assertEqual(report["task_family_count"],37)
        self.assertFalse(report["mastery_awarded"])

    def test_missing_course_is_reported(self):
        learning,taxonomy,registry=fixtures()
        learning["official_courses"].pop()
        report=audit(learning,taxonomy,registry)
        self.assertTrue(any("exactly 12" in e for e in report["errors"]))

    def test_course_without_training_rights_is_required(self):
        learning,taxonomy,registry=fixtures()
        learning["official_courses"][0]["training_data_authorized"]=True
        report=audit(learning,taxonomy,registry)
        self.assertTrue(any("cannot be presumed training data" in e for e in report["errors"]))

    def test_module_order_is_enforced(self):
        learning,taxonomy,registry=fixtures()
        learning["ecosystem_modules"][1]["id"]="HFEC-03"
        report=audit(learning,taxonomy,registry)
        self.assertTrue(any("contiguous" in e for e in report["errors"]))

    def test_missing_course_track_route_is_reported(self):
        learning,taxonomy,registry=fixtures()
        registry["tracks"].pop()
        report=audit(learning,taxonomy,registry)
        self.assertTrue(any("task taxonomy" in e for e in report["errors"]))


if __name__=="__main__": unittest.main()
