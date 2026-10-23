import unittest
from buddy.wiki_search.benchmark import evaluate
class BenchmarkTests(unittest.TestCase):
 def setUp(self):
  self.c=[{"id":"h1","split":"holdout","question":"Moon","rights_verified":True,"privacy_safe":True,"expected_external_ids":["moon"]}]
 def test_hit(self): self.assertEqual(evaluate(self.c,{"h1":["moon"]})["recall_at_k"],1)
 def test_miss(self): self.assertEqual(evaluate(self.c,{"h1":["mars"]})["mrr_at_k"],0)
 def test_missing_predictions(self):
  with self.assertRaises(ValueError): evaluate(self.c,{})
 def test_rights(self):
  self.c[0]["rights_verified"]=False
  with self.assertRaises(ValueError): evaluate(self.c,{"h1":["moon"]})
 def test_repeatable(self): self.assertEqual(evaluate(self.c,{"h1":["moon"]}),evaluate(self.c,{"h1":["moon"]}))
if __name__=="__main__": unittest.main()
