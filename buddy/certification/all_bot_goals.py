"""Inventory every canonical bot's declared goals and build evidence-gated study tasks."""
import argparse
import hashlib
import json
from pathlib import Path

def build(root):
    root=Path(root)
    entries=[]; seen=set(); divisions=0
    for path in sorted((root/"App_bots").glob("*.json")):
        try:
            payload=json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not isinstance(payload,dict) or not isinstance(payload.get("bots"),list):
            continue
        divisions+=1
        division=payload.get("division",path.stem)
        for bot in payload["bots"]:
            if not isinstance(bot,dict):
                continue
            slug=bot.get("slug")
            if not isinstance(slug,str) or not slug:
                continue
            key=f"{division}/{slug}"
            if key in seen:
                continue
            seen.add(key)
            caps=[v for v in bot.get("capabilities",[]) if isinstance(v,str) and v.strip()]
            benchmarks=bot.get("benchmarks",[])
            learning=bot.get("learningPlan",[])
            for idx,cap in enumerate(caps):
                goal_id=hashlib.sha256((key+"|"+cap).encode()).hexdigest()[:20]
                entries.append({"id":goal_id,"bot_id":key,"division":division,
                                "bot_name":bot.get("displayName",slug),"goal":cap,
                                "description":bot.get("description",""),
                                "declared_benchmarks":benchmarks if isinstance(benchmarks,list) else [],
                                "declared_learning_plan":learning if isinstance(learning,list) else [],
                                "tools_needed":bot.get("toolsNeeded",[]),
                                "status":"declared_not_verified",
                                "champion_model":None,"independent_benchmark":None,
                                "training_started":False,
                                "next_steps":["Define executable acceptance test","Find authorized task references",
                                              "Evaluate eligible models on comparable heldout tasks",
                                              "Compare Buddy against independently measured champion",
                                              "Propose lowest-cost improvement with approval"]})
    return {"schema":"dreamco.all_bot_goals.v1","divisions_scanned":divisions,
            "bots_scanned":len(seen),"goals_scanned":len(entries),
            "goals":entries,"note":"Profile goals are claims, not evidence of functioning implementations or model rankings."}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",default="website/data/buddy-all-bot-goals.json")
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[2]
    dest=(root/args.output).resolve()
    if not dest.is_relative_to(root/"website"/"data"):
        parser.error("Output must be within website/data")
    result=build(root)
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:result[k] for k in ("divisions_scanned","bots_scanned","goals_scanned")}))

if __name__=="__main__":
    main()
