import unittest
from datetime import datetime, timezone
from buddy.certification.task_champions import choose_champions, METRICS

def record(model, domain, task, score):
    return {"model_id":model,"domain":domain,"task_id":task,"task_set_hash":"same",
            "scorer_version":"v1","independent_verified":True,"receipt_sha256":"abc",
            "trials":5,"measured_at":datetime.now(timezone.utc).isoformat(),
            "scores":{m:score for m in METRICS}}

class TaskChampionsTests(unittest.TestCase):
    def test_different_task_different_champion(self):
        rows=[record("gpt","coding","debug",.95),record("qwen","coding","debug",.8),
              record("gpt","research","sources",.8),record("qwen","research","sources",.96)]
        result=choose_champions(rows)
        self.assertEqual([x["champion_model"] for x in result["champions"]],["gpt","qwen"])
    def test_no_unverified_winner(self):
        x=record("unverified","coding","debug",1)
        x["independent_verified"]=False
        self.assertEqual(choose_champions([x])["champions"],[])
    def test_buddy_gap(self):
        result=choose_champions([record("buddy","coding","debug",.8),record("gpt","coding","debug",.95)])
        self.assertGreater(result["champions"][0]["buddy_gap"],0)
    def test_separate_task_set(self):
        a=record("gpt","coding","debug",.95)
        b=record("qwen","coding","debug",.98)
        b["task_set_hash"]="different"
        self.assertEqual(len(choose_champions([a,b])["champions"]),2)

if __name__=="__main__":
    unittest.main()
