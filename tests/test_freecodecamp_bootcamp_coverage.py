import unittest
from tools.audit_freecodecamp_bootcamp_coverage import audit_coverage

def fixture():
    catalog = {"schema":"dreamco.freecodecamp_catalog.v1",
      "source":{"channel_id":"UC8butISFwT-Wl7EV0hUK0BQ","channel_url":"https://www.youtube.com/@freecodecamp"},
      "inventory_status":"complete","inventory":{"complete":True,"expected_entry_count":2,"observed_entry_count":2,"null_entry_count":0,"duplicate_video_id_count":0},
      "categories":[{"id":"python_and_automation"},{"id":"other_or_unclassified"}],
      "videos":[{"video_id":"v1","title":"Python","url":"https://www.youtube.com/watch?v=v1","categories":["python_and_automation"]},
                {"video_id":"v2","title":"Needs review","url":"https://www.youtube.com/watch?v=v2","categories":["other_or_unclassified"]}]}
    roadmap = {"scope":{"include_all_public_channel_videos":True},
      "official_platform_inventory":{"core_certifications":[{} for _ in range(7)],"additional_certifications":[{} for _ in range(5)],
        "curriculum_primitives":["theory_lessons","workshops","labs","review_pages","quizzes","required_projects","exams"]},
      "video_learning_tracks":[f"track-{i}" for i in range(22)],"interactive_curriculum_inventory":{"status":"verified_current"}}
    manifest = {"transcripts":[],"rights_policy":{"automatic_caption_scraping":False,"automatic_transcript_download":False,"automatic_model_training":False}}
    queue = {"videos":[{"video_id":"v1"},{"video_id":"v2"}],"guide_approved_count":2,"authorized_for_guide_count":0,"pending_or_blocked_count":2}
    routes = {"videos":[{"video_id":"v1"},{"video_id":"v2"}],"divisions":[{} for _ in range(65)]}
    return catalog,roadmap,manifest,queue,routes

class FreeCodeCampBootcampCoverageTests(unittest.TestCase):
    def test_queue_and_routes_cover_every_video_but_rights_and_classification_remain_separate(self):
        c,r,m,q,rt=fixture()
        report=audit_coverage(c,r,m,queue=q,routes=rt,domain_crosswalk={"domains":[{} for _ in range(55)]},masterbot_registry={"divisions":[{} for _ in range(65)]})
        self.assertEqual(report["per_video_study_queue"]["status"],"COMPLETE")
        self.assertEqual(report["per_video_division_routes"]["status"],"COMPLETE")
        self.assertEqual(report["division_coverage"],{"domain_divisions":55,"masterbot_lanes":65})
        self.assertIn("some_videos_remain_in_the_unclassified_human_review_queue",report["gaps"])
        self.assertIn("no_item_level_authorized_transcripts_are_registered_for_detailed_guides",report["gaps"])
        self.assertEqual(report["status"],"INCOMPLETE")
    def test_partial_or_count_mismatched_inventory_never_passes(self):
        c,r,m,q,rt=fixture(); c["inventory"]["expected_entry_count"]=3
        report=audit_coverage(c,r,m,queue=q,routes=rt)
        self.assertFalse(report["video_inventory"]["inventory_complete"])
        self.assertIn("official_channel_video_inventory_is_partial_or_unverified",report["gaps"])
    def test_missing_video_queue_and_route_ids_are_reported(self):
        c,r,m,q,rt=fixture(); q["videos"].pop(); rt["videos"].pop()
        report=audit_coverage(c,r,m,queue=q,routes=rt)
        self.assertEqual(report["per_video_study_queue"]["missing_video_ids"],["v2"])
        self.assertEqual(report["per_video_division_routes"]["missing_video_ids"],["v2"])
    def test_duplicate_ids_unknown_categories_and_wrong_source_are_reported(self):
        c,r,m,q,rt=fixture(); c["videos"][1]["categories"]=["not-in-taxonomy"]; c["videos"].append(dict(c["videos"][0])); c["source"]["channel_id"]="not-freecodecamp"
        report=audit_coverage(c,r,m,queue=q,routes=rt)
        self.assertEqual(report["video_inventory"]["duplicate_ids"],1)
        self.assertEqual(report["video_inventory"]["unknown_category_video_count"],1)
        self.assertIn("catalog_source_is_not_verified_official_freecodecamp_channel",report["gaps"])
        self.assertIn("catalog_contains_duplicate_video_ids",report["gaps"])
    def test_missing_queue_or_routes_is_not_complete(self):
        c,r,m,_,_=fixture(); report=audit_coverage(c,r,m)
        self.assertEqual(report["per_video_study_queue"]["status"],"NOT_PROVIDED")
        self.assertEqual(report["per_video_division_routes"]["status"],"NOT_PROVIDED")
        self.assertEqual(report["status"],"INCOMPLETE")

if __name__=="__main__": unittest.main()
