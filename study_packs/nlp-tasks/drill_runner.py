#!/usr/bin/env python3
"""Score HF NLP task-zoo drill predictions (stdlib only, no network, no weights)."""
import argparse, json, re, string, sys, collections
from pathlib import Path

HERE = Path(__file__).resolve().parent
TASKS = ["classification", "ner", "qa", "summarization", "translation"]

def load(task):
    return [json.loads(l) for l in (HERE / task / "drills.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]

def norm(s):
    s = s.lower()
    s = "".join(c for c in s if c not in string.punctuation + "¿¡")
    s = re.sub(r"\b(a|an|the)\b", " ", s)
    return " ".join(s.split())

def tok_f1(p, g):
    pt, gt = norm(p).split(), norm(g).split()
    if not pt and not gt: return 1.0
    common = sum((collections.Counter(pt) & collections.Counter(gt)).values())
    if common == 0: return 0.0
    pr, rc = common / len(pt), common / len(gt)
    return 2 * pr * rc / (pr + rc)

def lcs(a, b):
    dp = [0] * (len(b) + 1)
    for x in a:
        prev = 0
        for j, y in enumerate(b, 1):
            cur = dp[j]
            dp[j] = prev + 1 if x == y else max(dp[j], dp[j - 1])
            prev = cur
    return dp[-1]

def rouge_l(p, g):
    pt, gt = norm(p).split(), norm(g).split()
    if not pt or not gt: return 0.0
    l = lcs(pt, gt)
    if l == 0: return 0.0
    pr, rc = l / len(pt), l / len(gt)
    return 2 * pr * rc / (pr + rc)

def chrf(p, g, n=3):
    def grams(s):
        s = s.replace(" ", "")
        return collections.Counter(s[i:i + n] for i in range(len(s) - n + 1))
    pg, gg = grams(p.lower()), grams(g.lower())
    if not pg or not gg: return 0.0
    m = sum((pg & gg).values())
    if m == 0: return 0.0
    pr, rc = m / sum(pg.values()), m / sum(gg.values())
    b2 = 4.0
    return (1 + b2) * pr * rc / (b2 * pr + rc)

def ent_f1(p, g):
    ps = {(e.lower(), t) for e, t in p}; gs = {(e.lower(), t) for e, t in g}
    if not ps and not gs: return 1.0
    tp = len(ps & gs)
    if tp == 0: return 0.0
    pr, rc = tp / len(ps), tp / len(gs)
    return 2 * pr * rc / (pr + rc)

def item_score(task, d, pred):
    if task == "classification": return float(str(pred).strip().lower() == d["gold"].lower())
    if task == "ner": return ent_f1(pred or [], d["gold"])
    if task == "qa":
        if d.get("unanswerable"): return float(norm(pred or "") == "")
        return max(float(norm(pred) == norm(d["gold"])), tok_f1(pred, d["gold"]))
    if task == "summarization": return rouge_l(pred or "", d["gold"])
    if task == "translation": return chrf(pred or "", d["gold"])
    raise ValueError(task)

def score(task, preds):
    drills = load(task)
    floor = json.loads((HERE / task / "evals.json").read_text())["floor"]
    per = {d["id"]: round(item_score(task, d, preds.get(d["id"], "" if task != "ner" else [])), 4) for d in drills}
    mean = round(sum(per.values()) / len(per), 4)
    return {"task": task, "n": len(per), "mean": mean, "floor": floor, "pass": mean >= floor,
            "missing": [i for i in per if i not in preds], "per_item": per}

WRONG = {"classification": lambda d: "WRONG", "ner": lambda d: [], "qa": lambda d: "zzz" if not d.get("unanswerable") else "zzz",
         "summarization": lambda d: "unrelated words only", "translation": lambda d: "xyz"}

def selftest():
    out = {"schema": "dreamco.nlp_task_zoo_selftest.v1", "kind": "harness_selftest_not_model_eval", "tasks": {}}
    ok = True
    for t in TASKS:
        ds = load(t)
        gold = score(t, {d["id"]: d["gold"] for d in ds})
        bad = score(t, {d["id"]: WRONG[t](d) for d in ds})
        good = gold["mean"] == 1.0 and bad["mean"] < gold["floor"]
        ok &= good
        out["tasks"][t] = {"gold_mean": gold["mean"], "wrong_mean": bad["mean"], "floor": gold["floor"], "ok": good}
    out["ok"] = ok
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("task", nargs="?", choices=TASKS)
    ap.add_argument("--preds"); ap.add_argument("--out"); ap.add_argument("--model"); ap.add_argument("--revision")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        r = selftest()
    else:
        if not (a.task and a.preds): ap.error("task and --preds required")
        preds = {}
        for l in Path(a.preds).read_text(encoding="utf-8").splitlines():
            if l.strip():
                o = json.loads(l); preds[o["id"]] = o["pred"]
        r = score(a.task, preds); r.update(model=a.model, revision=a.revision,
            evidence_valid=bool(a.model and a.revision))
    txt = json.dumps(r, indent=2, ensure_ascii=False)
    if a.out: Path(a.out).parent.mkdir(parents=True, exist_ok=True); Path(a.out).write_text(txt + "\n", encoding="utf-8")
    print(txt)
    return 0 if r.get("ok", r.get("pass")) else 1

if __name__ == "__main__":
    sys.exit(main())
