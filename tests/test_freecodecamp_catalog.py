import json
import unittest
from pathlib import Path

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

class FreeCodeCampCatalogTests(unittest.TestCase):
    def test_parse_feed_is_metadata_only_and_classifies_topics(self):
        entries=parse_feed(ATOM_FIXTURE)
        self.assertEqual(len(entries),2)
        self.assertIn("python_and_automation",next(x for x in entries if x["video_id"]=="v-python")["categories"])
        self.assertIn("cybersecurity_and_privacy",next(x for x in entries if x["video_id"]=="v-cyber")["categories"])
        for row in entries:
            self.assertEqual(row["rights_status"],"review_required")
            self.assertEqual(row["transcript_status"],"not_ingested_rights_gate")
            self.assertFalse(row["media_download_allowed"])
            self.assertFalse(row["transcript_ingestion_allowed"])
            self.assertFalse(row["model_training_allowed"])

    def test_merge_catalog_deduplicates_and_preserves_curated_tags(self):
        entries=parse_feed(ATOM_FIXTURE)
        old={"videos":[{**entries[0],"categories":["python_and_automation","dreamco_curated"]}]}
        merged=merge_catalog(old,entries,generated_at="2026-11-24T00:00:00+00:00")
        self.assertEqual(len(merged["videos"]),2)
        self.assertIn("dreamco_curated",next(x for x in merged["videos"] if x["video_id"]=="v-python")["categories"])

    def test_seed_catalog_contains_official_metadata_only_records(self):
        root=Path(__file__).resolve().parents[1]
        catalog=json.loads((root/"config/generated/freecodecamp-youtube-catalog.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(catalog["videos"]),5)
        self.assertEqual(catalog["source"]["channel_id"],"UC8butISFwT-Wl7EV0hUK0BQ")
        for row in catalog["videos"]:
            self.assertTrue(row["url"].startswith("https://www.youtube.com/watch?v="))
            self.assertEqual(row["rights_status"],"review_required")
            self.assertEqual(row["transcript_status"],"not_ingested_rights_gate")
            self.assertFalse(row["media_download_allowed"])
            self.assertFalse(row["transcript_ingestion_allowed"])
            self.assertFalse(row["model_training_allowed"])

    def test_daily_lesson_plan_targets_five_per_55_domains_and_reports_blocked_slots(self):
        entries=parse_feed(ATOM_FIXTURE)
        catalog=merge_catalog({},entries,generated_at="2026-11-24T00:00:00+00:00")
        registry={"divisions":[{"id":i,"name":"DreamCyber" if i==1 else f"DreamDivision{i}"} for i in range(1,66)]}
        profiles=[{"domain_id":f"domain-{i}","domain_name":f"Domain {i}","masterbot_id":i} for i in range(1,56)]
        result=build_routes(catalog,registry,profiles,lessons_per_domain=5);validate(result)
        plan=result["daily_lesson_plan"]
        self.assertEqual(plan["domain_count"],55)
        self.assertEqual(plan["lessons_per_domain_per_day"],5)
        self.assertEqual(plan["daily_target"],275)
        self.assertEqual(plan["planned_lessons"],110)
        self.assertEqual(plan["blocked_lessons"],165)
        self.assertTrue(all(len(x["lessons"])==5 for x in plan["divisions"]))
