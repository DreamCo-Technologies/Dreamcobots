import json
import unittest
from buddy.certification.research_evidence import verify_research_answer
from buddy.certification.tool_execution_bench import execute

class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.task={"expected":"Paris","sources":[
            {"id":"source-1","text":"The capital of France is Paris."}]}
    def test_cited_source_support(self):
        result=verify_research_answer(json.dumps({"answer":"Paris","source_ids":["source-1"]}),self.task)
        self.assertTrue(result["passed"])
        self.assertFalse(result["source_verified"])
        self.assertEqual(len(result["source_receipts"][0]["sha256"]),64)
    def test_fake_citation_rejected(self):
        result=verify_research_answer(json.dumps({"answer":"Paris","source_ids":["fake"]}),self.task)
        self.assertFalse(result["passed"])
    def test_unsupported_source_rejected(self):
        self.task["sources"][0]["text"]="France is in Europe."
        result=verify_research_answer(json.dumps({"answer":"Paris","source_ids":["source-1"]}),self.task)
        self.assertFalse(result["passed"])
    def test_tool_prerequisite_required(self):
        result=execute(["calculate_available","publish"])
        self.assertFalse(result["state"]["published"])
        self.assertEqual(result["receipts"][0]["status"],"blocked")

if __name__=="__main__":
    unittest.main()
