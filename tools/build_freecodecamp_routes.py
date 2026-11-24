#!/usr/bin/env python3
"""Build FreeCodeCamp metadata routes and a five-lesson/day plan for 55 domains."""
import argparse, json
from pathlib import Path

CATEGORY_TERMS = {
 "python_and_automation":("python","automation","scripting"),
 "cybersecurity_and_privacy":("cyber","security","privacy","ethical hacker"),
 "web_development":("javascript","html","css","react","node.js","typescript","web development"),
 "ai_ml":("machine learning","deep learning","llm","artificial intelligence","pytorch","tensorflow","ai coding"),
 "data_science":("data science","statistics","pandas","numpy","visualization"),
 "databases_and_data_engineering":("sql","postgres","database","vector database","mongodb"),
 "cloud_devops":("aws","azure","cloud","docker","kubernetes","devops"),
 "game_development":("game","godot","three.js","unity","unreal"),
 "computer_science":("algorithm","data structures","computer science","operating system"),
}

def categorize_text(title, description=""):
 text=f"{title} {description}".casefold()
 return [k for k,terms in CATEGORY_TERMS.items() if any(t in text for t in terms)] or ["other_or_unclassified"]

def _specialty_ids(categories, divisions):
 ids=[]
 for d in divisions:
  name=str(d.get("name","")).casefold()
  if any(term in name for category in categories for term in CATEGORY_TERMS.get(category,())):
   ids.append(int(d["id"]))
  elif "cybersecurity_and_privacy" in categories and any(x in name for x in ("cyber","security")):
   ids.append(int(d["id"]))
  elif "ai_ml" in categories and any(x in name for x in ("ai","ml","research")):
   ids.append(int(d["id"]))
 return sorted(set(ids))

def _daily_plan(profiles,videos,quota):
 divisions=[]; planned=0
 for profile in profiles:
  did=profile.get("domain_id",str(profile.get("id")))
  name=profile.get("domain_name",profile.get("name",str(did)))
  mid=profile.get("masterbot_id",profile.get("id"))
  specialty=[v for v in videos if mid in v.get("specialty_division_ids",[])]
  shared=[v for v in videos if mid not in v.get("specialty_division_ids",[])]
  candidates=sorted(specialty,key=lambda x:x.get("published_at",""),reverse=True)+sorted(shared,key=lambda x:x.get("published_at",""),reverse=True)
  lessons=[]
  for slot in range(quota):
   if slot < len(candidates):
    v=candidates[slot]; planned+=1
    lessons.append({"lesson_number":slot+1,"video_id":v["video_id"],"title":v["title"],"source_url":v["url"],
      "categories":v.get("categories",[]),"routing_scope":"specialty" if mid in v.get("specialty_division_ids",[]) else "shared_foundation",
      "transcript_status":v.get("transcript_status","not_ingested_rights_gate"),
      "status":"queued_not_studied","execution_status":"PLAN_ONLY_NOT_EXECUTED","media_download_allowed":False,
      "transcript_ingestion_allowed":False,"model_training_allowed":False})
   else:
    lessons.append({"lesson_number":slot+1,"video_id":None,"title":None,"source_url":None,"categories":[],
      "transcript_status":"not_available","status":"blocked_no_video_metadata","execution_status":"NOT_EXECUTED",
      "media_download_allowed":False,"transcript_ingestion_allowed":False,"model_training_allowed":False})
  divisions.append({"domain_id":did,"domain_name":name,"masterbot_id":mid,"lessons":lessons,
    "planned_lessons":sum(x["status"]=="queued_not_studied" for x in lessons),
    "blocked_lessons":sum(x["status"]=="blocked_no_video_metadata" for x in lessons)})
 target=len(profiles)*quota
 return {"scope":"55_domain_profiles_when_readiness_map_is_supplied","domain_count":len(profiles),
  "lessons_per_domain_per_day":quota,"daily_target":target,"planned_lessons":planned,
  "blocked_lessons":target-planned,"status":"PLAN_ONLY_NOT_EXECUTED" if planned else "BLOCKED_NO_VIDEO_METADATA",
  "divisions":divisions}

def build_routes(catalog,registry,domain_profiles=None,lessons_per_domain=5):
 if lessons_per_domain<1: raise ValueError("lessons_per_domain must be at least 1")
 divisions=registry.get("divisions",[])
 if len(divisions)!=65 or len({x.get("id") for x in divisions})!=65:
  raise ValueError("routes must cover all 65 divisions; canonical registry requires 65 unique records")
 routed=[]; seen=set()
 for v in catalog.get("videos",[]):
  vid=str(v.get("video_id","")).strip(); title=str(v.get("title","")).strip(); url=str(v.get("url","")).strip()
  if not vid or not title or not url.startswith("https://"): raise ValueError("every video requires a video_id, title, and HTTPS URL")
  if vid in seen: raise ValueError(f"duplicate video id: {vid}")
  seen.add(vid); cats=list(v.get("categories") or categorize_text(title,v.get("description","")))
  specialty=_specialty_ids(cats,divisions)
  routed.append({**v,"categories":cats,"specialty_division_ids":specialty,
   "routing_status":"specialty_and_shared" if specialty else "shared_only","shared_catalog_access":True,
   "rights_status":v.get("rights_status","review_required"),"media_download_allowed":False,
   "transcript_ingestion_allowed":False,"model_training_allowed":False,
   "transcript_status":v.get("transcript_status","not_ingested_rights_gate")})
 profiles=domain_profiles if domain_profiles is not None else divisions
 result={"schema":"dreamco.freecodecamp_division_routes.v1","catalog_video_count":len(routed),
  "catalog_generated_at":catalog.get("generated_at"),
  "rights_policy":catalog.get("rights_policy",{"media_download_enabled":False,"transcript_ingestion_enabled":False,"model_training_requires_review":True}),
  "divisions":[{"id":int(x["id"]),"name":x["name"],"available_video_count":len(routed),"shared_catalog_access":True} for x in divisions],
  "videos":routed,"daily_lesson_plan":_daily_plan(profiles,routed,lessons_per_domain)}
 validate(result); return result

def validate(payload):
 divs=payload.get("divisions",[]); videos=payload.get("videos",[])
 if len(divs)!=65 or len({x.get("id") for x in divs})!=65: raise ValueError("routes must cover all 65 divisions")
 ids=[x.get("video_id") for x in videos]
 if len(ids)!=len(set(ids)): raise ValueError("duplicate video ids in route catalog")
 for v in videos:
  if v.get("media_download_allowed") or v.get("transcript_ingestion_allowed") or v.get("model_training_allowed"):
   raise ValueError("unreviewed FreeCodeCamp material cannot be downloaded, transcribed, or used for training")
 plan=payload.get("daily_lesson_plan",{})
 if plan and any(len(x.get("lessons",[]))!=plan.get("lessons_per_domain_per_day") for x in plan.get("divisions",[])):
  raise ValueError("daily lesson plan does not meet its per-domain slot contract")

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--catalog",default="config/generated/freecodecamp-youtube-catalog.json")
 p.add_argument("--registry",default="config/masterbot-65-registry.json")
 p.add_argument("--domain-map",default="config/generated/division-resource-readiness-map.json")
 p.add_argument("--output",default="artifacts/buddy-dataset-hub/freecodecamp-routes.json")
 p.add_argument("--lessons-per-domain",type=int,default=5)
 a=p.parse_args()
 catalog=json.loads(Path(a.catalog).read_text(encoding="utf-8"))
 registry=json.loads(Path(a.registry).read_text(encoding="utf-8"))
 readiness=json.loads(Path(a.domain_map).read_text(encoding="utf-8"))
 result=build_routes(catalog,registry,readiness.get("domain_routes",[]),a.lessons_per_domain)
 out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 plan=result["daily_lesson_plan"]
 print(json.dumps({"catalog_videos":result["catalog_video_count"],"domain_profiles":plan["domain_count"],
  "lessons_per_domain_per_day":plan["lessons_per_domain_per_day"],"daily_lesson_target":plan["daily_target"],
  "planned_lessons":plan["planned_lessons"],"blocked_lessons":plan["blocked_lessons"],"status":plan["status"],
  "media_downloaded":False,"transcripts_ingested":False,"weights_trained":False},indent=2))

if __name__=="__main__": main()
