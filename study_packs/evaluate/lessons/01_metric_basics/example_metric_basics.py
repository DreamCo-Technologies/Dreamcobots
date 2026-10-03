#!/usr/bin/env python3
"""Lesson 1: exact_match / accuracy / f1 on synthetic rows, offline by default."""
import json
import os
import sys
from pathlib import Path

if os.environ.get("HF_PACK_ALLOW_NETWORK") != "1":
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["HF_EVALUATE_OFFLINE"] = "1"
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import metrics_adapter as m  # noqa: E402

preds = ["Paris", "4", "blue whale", "H2O"]
refs = ["paris", "4", "Blue Whale", "CO2"]
em_strict = m.compute("exact_match", preds, refs)["result"]["exact_match"]
em_loose = m.compute("exact_match", preds, refs, ignore_case=True)["result"]["exact_match"]
acc = m.compute("accuracy", [1, 0, 1, 1], [1, 0, 0, 1])["result"]["accuracy"]
f1v = m.compute("f1", [1, 0, 1, 1], [1, 0, 0, 1])["result"]["f1"]
ok = em_strict == 0.25 and em_loose == 0.75 and acc == 0.75 and abs(f1v - 0.8) < 1e-9
print(json.dumps({"ok": ok, "exact_match": em_strict, "exact_match_ignore_case": em_loose,
                  "accuracy": acc, "f1": round(f1v, 6), "backend": m.compute("accuracy", [1], [1])["backend"]}))
sys.exit(0 if ok else 1)
