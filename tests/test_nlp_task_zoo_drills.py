import importlib.util, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "study_packs" / "nlp-tasks"
spec = importlib.util.spec_from_file_location("drill_runner", ROOT / "drill_runner.py")
dr = importlib.util.module_from_spec(spec); spec.loader.exec_module(dr)

def test_all_five_tasks_present():
    idx = json.loads((ROOT / "index.json").read_text())
    assert [t["task"] for t in idx["tasks"]] == dr.TASKS
    for t in dr.TASKS:
        for f in ("CARD.md", "drills.jsonl", "evals.json", "sources.json"):
            assert (ROOT / t / f).exists()

def test_no_training_no_pins_claimed():
    for t in dr.TASKS:
        assert json.loads((ROOT / t / "evals.json").read_text())["train_allowed"] is False
        src = json.loads((ROOT / t / "sources.json").read_text())
        assert src["automatic_weight_download"] is False
        for e in src["hf_models"] + src["hf_datasets"]:
            assert e["revision"] is None and e["license"] == "TBD"

def test_selftest_scorer_separates_gold_from_wrong():
    r = dr.selftest()
    assert r["ok"], r

def test_unanswerable_qa_requires_empty():
    d = {"gold": "", "unanswerable": True}
    assert dr.item_score("qa", d, "") == 1.0
    assert dr.item_score("qa", d, "Bob") == 0.0
