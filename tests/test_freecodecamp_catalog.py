from tools.sync_freecodecamp_youtube_catalog import merge_catalog, parse_feed
from tools.build_freecodecamp_routes import build_routes, validate

ATOM_FIXTURE = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:yt="http://www.youtube.com/xml/schemas/2015" xmlns:media="http://search.yahoo.com/mrss/">
 <entry><id>yt:video:v-python</id><yt:videoId>v-python</yt:videoId><title>Python for Beginners Full Course</title>
 <link rel="alternate" href="https://www.youtube.com/watch?v=v-python"/><published>2026-11-20T10:00:00+00:00</published>
 <media:group><media:description>Learn Python programming and automation.</media:description></media:group></entry>
 <entry><id>yt:video:v-cyber</id><yt:videoId>v-cyber</yt:videoId><title>How Ethical Hackers Actually Break Into Systems</title>
 <link rel="alternate" href="https://www.youtube.com/watch?v=v-cyber"/><published>2026-11-21T10:00:00+00:00</published>
 <media:group><media:description>Cybersecurity fundamentals and security labs.</media:description></media:group></entry>
</feed>"""

def test_parse_feed_is_metadata_only_and_classifies_topics():
 entries=parse_feed(ATOM_FIXTURE)
 assert len(entries)==2
 assert "python_and_automation" in next(x for x in entries if x["video_id"]=="v-python")["categories"]
 assert "cybersecurity_and_privacy" in next(x for x in entries if x["video_id"]=="v-cyber")["categories"]
 for row in entries:
  assert row["rights_status"]=="review_required"
  assert row["transcript_status"]=="not_ingested_rights_gate"
  assert row["media_download_allowed"] is False
  assert row["transcript_ingestion_allowed"] is False
  assert row["model_training_allowed"] is False

def test_merge_catalog_deduplicates_and_preserves_curated_tags():
 entries=parse_feed(ATOM_FIXTURE)
 old={"videos":[{**entries[0],"categories":["python_and_automation","dreamco_curated"]}]}
 merged=merge_catalog(old,entries,generated_at="2026-11-24T00:00:00+00:00")
 assert len(merged["videos"])==2
 assert "dreamco_curated" in next(x for x in merged["videos"] if x["video_id"]=="v-python")["categories"]

def test_seed_catalog_contains_official_metadata_only_records():
 from pathlib import Path
 import json
 catalog=json.loads((Path(__file__).resolve().parents[1]/"config/generated/freecodecamp-youtube-catalog.json").read_text(encoding="utf-8"))
 assert len(catalog["videos"])>=5
 assert catalog["source"]["channel_id"]=="UC8butISFwT-Wl7EV0hUK0BQ"
 assert all(row["url"].startswith("https://www.youtube.com/watch?v=") for row in catalog["videos"])
 assert all(row["rights_status"]=="review_required" and row["transcript_status"]=="not_ingested_rights_gate" for row in catalog["videos"])
 assert all(row["media_download_allowed"] is False and row["transcript_ingestion_allowed"] is False and row["model_training_allowed"] is False for row in catalog["videos"])

def test_daily_lesson_plan_targets_five_per_55_domains_and_reports_blocked_slots():
 entries=parse_feed(ATOM_FIXTURE);catalog=merge_catalog({},entries,generated_at="2026-11-24T00:00:00+00:00")
 registry={"divisions":[{"id":i,"name":"DreamCyber" if i==1 else f"DreamDivision{i}"} for i in range(1,66)]}
 profiles=[{"domain_id":f"domain-{i}","domain_name":f"Domain {i}","masterbot_id":i} for i in range(1,56)]
 result=build_routes(catalog,registry,profiles,lessons_per_domain=5);validate(result)
 plan=result["daily_lesson_plan"]
 assert plan["domain_count"]==55 and plan["lessons_per_domain_per_day"]==5 and plan["daily_target"]==275
 assert plan["planned_lessons"]==110 and plan["blocked_lessons"]==165
 assert all(len(x["lessons"])==5 for x in plan["divisions"])
