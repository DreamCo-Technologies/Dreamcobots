import unittest
from tools.validate_original_lesson import validate_lesson

class OriginalLessonTests(unittest.TestCase):
    def lesson(self):
        return {
            "schema":"dreamco.original_lesson.v1","lesson_id":"dreamco-python-001",
            "division_id":6,"title":"Thinking in Python Functions",
            "learning_objectives":["Explain why a function groups reusable behavior.","Write and test a function with clear inputs and outputs."],
            "original_explanation":"A function is a named unit of behavior. It accepts inputs, performs a focused operation, and can return a result. Good functions make a program easier to test, reuse, and explain.",
            "worked_examples":[{"problem":"Convert a temperature value.","solution":"Define a conversion function.","reasoning":"A named operation can be tested independently."}],
            "practice":[{"prompt":"Write a formatter.","expected_artifact":"A tested function.","difficulty":"guided"},{"prompt":"Build a reusable validator.","expected_artifact":"A tested validator.","difficulty":"independent"}],
            "assessment":{"questions":["What is a parameter?","What is a return value?","Why test a function?"],"answer_key":["An input name.","The result sent back.","To verify behavior."],"benchmark_spec":"Run unseen input/output cases."},
            "authorship":{"authoring_entity":"DreamCo","created_at":"2026-11-24T00:00:00Z","human_contribution":"Human reviewed the lesson outline, examples, and technical accuracy.","human_owner_confirmation":"pending","revision_history_ref":None},
            "provenance":{"source_name":"freeCodeCamp.org","source_url":"https://www.freecodecamp.org/","retrieved_at":"2026-11-24T00:00:00Z","source_usage":"inspiration_only","rights_review_ref":None},
            "rights":{"review_status":"pending","owner_label":"DreamCo","ownership_claim_status":"pending_review","third_party_material_included":False,"source_material_copied":False,"training_allowed":False}
        }
    def test_valid_original_lesson(self):
        self.assertEqual(validate_lesson(self.lesson()), [])
    def test_rejects_copied_source_material(self):
        item=self.lesson(); item["rights"]["source_material_copied"]=True
        self.assertTrue(any("must be original" in x for x in validate_lesson(item)))
    def test_rejects_training_without_separate_approval(self):
        item=self.lesson(); item["rights"]["training_allowed"]=True
        self.assertTrue(any("training remains disabled" in x for x in validate_lesson(item)))

    def test_rejects_unrecorded_ownership_or_third_party_material(self):
        item=self.lesson(); item["rights"]["third_party_material_included"]=True
        self.assertTrue(any("third-party material" in x for x in validate_lesson(item)))
        item=self.lesson(); item["rights"]["ownership_claim_status"]="confirmed"
        self.assertTrue(any("human owner confirmation" in x for x in validate_lesson(item)))
        item=self.lesson(); del item["rights"]["owner_label"]
        self.assertTrue(any("owner label" in x for x in validate_lesson(item)))

    def test_rejects_incomplete_assessment(self):
        item=self.lesson(); item["assessment"]["questions"]=[]
        self.assertTrue(any("three questions" in x for x in validate_lesson(item)))
if __name__ == "__main__":
    unittest.main()
