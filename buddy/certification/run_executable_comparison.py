"""Opt-in executable comparison across Buddy and configured provider adapters."""
import argparse
import json
import os
from pathlib import Path
from .executable_evaluations import compare
from .provider_adapters import ChatCompletionsAdapter

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--approved",action="store_true")
    p.add_argument("--max-tasks",type=int,default=3)
    args=p.parse_args()
    if not args.approved or os.getenv("BUDDY_LIVE_BENCHMARK_APPROVED")!="yes":
        p.error("Explicit approval and BUDDY_LIVE_BENCHMARK_APPROVED=yes required")
    if not 1<=args.max_tasks<=3:
        p.error("max-tasks must be 1..3")
    root=Path(__file__).resolve().parents[2]
    taskset=json.loads((root/"config/buddy/benchmarks/executable-starter.json").read_text())
    providers=json.loads(os.getenv("BUDDY_BENCHMARK_PROVIDERS_JSON","[]"))
    if not 2<=len(providers)<=6:
        p.error("Configure 2..6 approved providers, including Buddy if available")
    names=[item["name"] for item in providers]
    if len(set(names))!=len(names):
        p.error("Duplicate model adapter names")
    adapters=[ChatCompletionsAdapter(**item) for item in providers]
    report=compare(taskset["tasks"][:args.max_tasks],adapters)
    report["model_ids"]=names
    report["provider_endpoints_redacted"]=True
    report["training_on_holdouts_allowed"]=False
    out=root/"website/data/buddy-executable-model-comparison.json"
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({"tasks":args.max_tasks,"models":len(adapters),
                      "passed":sum(int(x["passed"]) for x in report["results"]),
                      "independent_verified":False}))

if __name__=="__main__":
    main()
