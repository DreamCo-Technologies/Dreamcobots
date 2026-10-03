#!/usr/bin/env python3
"""Lesson 2: score a toy Buddy F0-style run the way bench_map.json says.

Synthetic data only. This is NOT a Buddy result and must never be pasted into a
scorecard; it proves the scoring path works.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(HERE))
import metrics_adapter as m  # noqa: E402

bench_map = json.loads((HERE / "bench_map.json").read_text(encoding="utf-8"))
families = {b["id"]: b for b in bench_map["benches"]}

# Toy math items (exact_match) and toy code items (pass@k from n samples / c passing).
math_em = m.exact_match(["12", "7", "3.5"], ["12", "8", "3.5"])
code_p1 = m.mean_pass_at_k([(5, 5), (5, 2), (5, 0)], k=1)
code_p5 = m.mean_pass_at_k([(5, 5), (5, 2), (5, 0)], k=5)
ok = (abs(math_em - 2 / 3) < 1e-9 and abs(code_p1 - (1 + 0.4 + 0) / 3) < 1e-9
      and abs(code_p5 - 2 / 3) < 1e-9 and "f0.math" in families and "f0.code" in families)
print(json.dumps({"ok": ok, "synthetic": True, "f0.math.exact_match": round(math_em, 6),
                  "f0.code.pass@1": round(code_p1, 6), "f0.code.pass@5": round(code_p5, 6)}))
sys.exit(0 if ok else 1)
