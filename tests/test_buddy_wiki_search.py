import unittest
from buddy.wiki_search.search import SearchOptions, search

class Cursor:
    description = [type("Col", (), {"name": "title"})()]
    def __init__(self): self.sql = None; self.params = None
    def execute(self, sql, params): self.sql = sql; self.params = params
    def fetchall(self): return [("Test",)]
    def __enter__(self): return self
    def __exit__(self, *args): return False

class Connection:
    def __init__(self): self.cur = Cursor()
    def cursor(self): return self.cur

class SearchTests(unittest.TestCase):
    def test_keyword_without_vector(self):
        db=Connection()
        self.assertEqual(search(db, "Apollo 13"), [{"title":"Test"}])
        self.assertIn("search_text <@>",db.cur.sql)
    def test_hybrid_query(self):
        db=Connection()
        search(db,"space",embedding=[0.0]*384)
        self.assertIn("FULL OUTER JOIN",db.cur.sql)
    def test_limits(self):
        with self.assertRaises(ValueError): SearchOptions(limit=101).validate()
    def test_negative_weight(self):
        with self.assertRaises(ValueError): SearchOptions(keyword_weight=-1).validate()
    def test_bad_vector(self):
        with self.assertRaises(ValueError): search(Connection(),"x",embedding=[1,2])
    def test_blank_query(self):
        with self.assertRaises(ValueError): search(Connection(),"  ")
    def test_no_semantic_without_vector(self):
        with self.assertRaises(ValueError): search(Connection(),"x",options=SearchOptions(keyword_weight=0))
if __name__ == "__main__": unittest.main()
