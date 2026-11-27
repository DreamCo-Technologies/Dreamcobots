import json
import tempfile
import unittest
from pathlib import Path
from integration.validate_pages_index import validate

class PagesIndexValidationTests(unittest.TestCase):
    def check(self, data):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "index.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            return validate(path)
    def test_reject_empty_json(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "index.json"
            path.write_text("", encoding="utf-8")
            self.assertTrue(validate(path))
    def test_reject_invalid_source(self):
        data={"files":[{"path":"a.txt","source":"https://evil.example/a.txt"}]*1000}
        self.assertTrue(self.check(data))
    def test_reject_duplicate_paths(self):
        data={"files":[{"path":"a.txt","source":"a.txt"}]*1000,"source_base":"https://github.com/DreamCo-Technologies/Dreamcobots/blob/main/"}
        self.assertTrue(self.check(data))
    def test_accept_valid_compact_index(self):
        data={"files":[{"path":f"docs/{i}.md","source":f"docs/{i}.md"} for i in range(1000)],"source_base":"https://github.com/DreamCo-Technologies/Dreamcobots/blob/main/"}
        self.assertEqual(self.check(data),[])

if __name__ == "__main__":
    unittest.main()
