"""Generate complete fleet study manifest as bounded review-only pages."""
import argparse
import json
from pathlib import Path
from .fleet_study_queue import make_queue

def paginate(goals, champions, page_size=250):
    if not 1 <= page_size <= 1000:
        raise ValueError("invalid page size")
    total=len(goals["goals"])
    pages=[]
    for offset in range(0,total,page_size):
        page=make_queue(goals,champions,max_items=page_size,offset=offset)
        pages.append(page)
    seen=[task["goal_id"] for page in pages for task in page["tasks"]]
    if len(seen)!=total or len(set(seen))!=total:
        raise ValueError("duplicate or missing goal IDs; fleet inventory must be unique")
    return {"schema":"dreamco.fleet_study_manifest.v1",
            "total_goals":total,"page_size":page_size,"pages":len(pages),
            "queued_goals":len(seen),"duplicate_goals":0,
            "all_pages_review_only":True},pages

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--page-size",type=int,default=250)
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[2]
    goals=json.loads((root/"website/data/buddy-all-bot-goals.json").read_text())
    source=root/"website/data/buddy-task-champions.json"
    champions=json.loads(source.read_text()) if source.exists() else {
        "schema":"dreamco.task_champions.v1","champions":[]}
    manifest,pages=paginate(goals,champions,args.page_size)
    dest=root/"website/data/buddy-fleet-study-pages"
    dest.mkdir(parents=True,exist_ok=True)
    for old in dest.glob("page-*.json"):
        old.unlink()
    for idx,page in enumerate(pages):
        (dest/f"page-{idx+1:04d}.json").write_text(json.dumps(page,indent=2)+"\n")
    (dest/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(json.dumps(manifest))

if __name__=="__main__":
    main()
