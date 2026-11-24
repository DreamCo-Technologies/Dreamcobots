#!/usr/bin/env python3
"""Sync public FreeCodeCamp YouTube RSS metadata only; never fetch media or captions."""
import argparse,json,urllib.request,xml.etree.ElementTree as ET
from datetime import datetime,timezone
from pathlib import Path
CHANNEL_ID="UC8butISFwT-Wl7EV0hUK0BQ"
FEED_URL=f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}"
NS={"atom":"http://www.w3.org/2005/Atom","yt":"http://www.youtube.com/xml/schemas/2015","media":"http://search.yahoo.com/mrss/"}

def categorize(title,description=""):
 text=f"{title} {description}".casefold()
 rules={"python_and_automation":("python","automation","scripting"),"cybersecurity_and_privacy":("cyber","security","ethical hacker","privacy"),
 "web_development":("javascript","html","css","react","node.js","web development","typescript"),
 "ai_ml":("machine learning","deep learning","llm","artificial intelligence","pytorch","tensorflow","ai coding"),
 "data_science":("data science","statistics","pandas","numpy","visualization"),
 "databases_and_data_engineering":("sql","postgres","database","vector database","mongodb"),
 "cloud_devops":("aws","azure","cloud","docker","kubernetes","devops"),
 "game_development":("game","godot","three.js","unity","unreal"),
 "computer_science":("algorithm","data structures","computer science","operating system")}
 return [k for k,terms in rules.items() if any(t in text for t in terms)] or ["other_or_unclassified"]

def parse_feed(xml_text):
 root=ET.fromstring(xml_text); rows=[]
 for entry in root.findall("atom:entry",NS):
  vid=entry.findtext("yt:videoId",default="",namespaces=NS).strip()
  title=entry.findtext("atom:title",default="",namespaces=NS).strip()
  link=entry.find("atom:link",NS); url=link.attrib.get("href","") if link is not None else ""
  published=entry.findtext("atom:published",default="",namespaces=NS)
  group=entry.find("media:group",NS); desc=""; thumb=None
  if group is not None:
   desc=group.findtext("media:description",default="",namespaces=NS).strip()
   image=group.find("media:thumbnail",NS); thumb=image.attrib.get("url") if image is not None else None
  if not vid or not title or not url.startswith("https://www.youtube.com/watch"): continue
  rows.append({"video_id":vid,"title":title,"url":url,"published_at":published,"description":desc,"thumbnail":thumb,
   "categories":categorize(title,desc),"rights_status":"review_required","learning_status":"not_studied",
   "transcript_status":"not_ingested_rights_gate","transcript_ingestion_allowed":False,
   "media_download_allowed":False,"model_training_allowed":False})
 return rows

def merge_catalog(existing,entries,generated_at=None):
 merged={x["video_id"]:dict(x) for x in existing.get("videos",[]) if x.get("video_id")}
 for row in entries:
  old=merged.get(row["video_id"],{})
  merged[row["video_id"]]={**old,**row}
  merged[row["video_id"]]["categories"]=sorted(set(old.get("categories",[]))|set(row.get("categories",[])))
 return {"schema":"dreamco.freecodecamp_catalog.v1","generated_at":generated_at or datetime.now(timezone.utc).isoformat(),
  "source":{"name":"freeCodeCamp.org","channel_id":CHANNEL_ID,"channel_url":f"https://www.youtube.com/channel/{CHANNEL_ID}",
   "feed_url":FEED_URL,"coverage":"curated_seed_plus_latest_public_channel_rss_entries_per_poll_not_full_archive",\n   "curated_metadata_seed_count":sum(1 for row in merged.values() if row.get("metadata_source")=="official_freecodecamp_youtube_video_metadata")},
  "rights_policy":{"media_download_enabled":False,"transcript_ingestion_enabled":False,"model_training_requires_review":True,
   "metadata_only":True,"weekly_transcript_evaluation_requires_rights_cleared_transcript":True},
  "categories":[{"id":x} for x in sorted({c for row in merged.values() for c in row.get("categories",[])}|{"other_or_unclassified"})],
  "videos":sorted(merged.values(),key=lambda x:(x.get("published_at",""),x["video_id"]),reverse=True)}

def fetch_feed(url=FEED_URL):
 req=urllib.request.Request(url,headers={"User-Agent":"DreamCoStudyCatalog/1.0 (metadata-only)"})
 with urllib.request.urlopen(req,timeout=20) as response: return response.read().decode("utf-8")

def main():
 p=argparse.ArgumentParser();p.add_argument("--input-xml");p.add_argument("--output",default="config/generated/freecodecamp-youtube-catalog.json")
 p.add_argument("--existing");a=p.parse_args()
 out=Path(a.output); old=Path(a.existing) if a.existing else out
 existing=json.loads(old.read_text(encoding="utf-8")) if old.exists() else {}
 xml=Path(a.input_xml).read_text(encoding="utf-8") if a.input_xml else fetch_feed()
 entries=parse_feed(xml); result=merge_catalog(existing,entries)
 out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 print(json.dumps({"videos_cataloged":len(result["videos"]),"latest_feed_entries":len(entries),
  "coverage":result["source"]["coverage"],"media_downloaded":False,"transcripts_ingested":False,"model_training_allowed":False},indent=2))
if __name__=="__main__": main()
