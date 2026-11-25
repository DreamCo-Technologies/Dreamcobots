import tempfile
import unittest
from pathlib import Path
from tools.build_freecodecamp_study_guides import build_work_queue, validate_guide

def catalog():
    return {
        "schema":"dreamco.freecodecamp_catalog.v1",
        "source":{"channel_id":"UC8butISFwT-Wl7EV0hUK0BQ"},
        "inventory_status":"complete",
        "inventory":{"complete":True,"expected_entry_count":2,"observed_entry_count":2},
        "videos":[
            {"video_id":"v1","title":"Python foundations","url":"https://www.youtube.com/watch?v=v1","categories":["python_and_automation"]},
            {"video_id":"v2","title":"SQL basics","url":"https://www.youtube.com/watch?v=v2","categories":["databases_and_sql"]}
        ]
    }

def manifest(records=None):
    return {"schema":"dreamco.authorized_transcript_manifest.v1","rights_policy":{
        "automatic_caption_scraping":False,"automatic_transcript_download":False,"automatic_model_training":False
    },"transcripts":records or []}

class StudyGuideQueueTests(unittest.TestCase):
    def test_builder_source_compiles_before_queue_execution(self):
        root = Path(__file__).resolve().parents[1]
        source = root / "tools" / "build_freecodecamp_study_guides.py"
        compile(source.read_text(encoding="utf-8"), str(source), "exec")

    def test_every_catalog_video_gets_a_queue_row_without_fabricating_summaries(self):
        result=build_work_queue(catalog(),manifest())
        self.assertEqual(result["catalog_video_count"],2)
        self.assertEqual(result["source_inventory_status"],"COMPLETE")
        self.assertEqual(result["authorized_for_guide_count"],0)
        self.assertTrue(all(row["guide_status"]=="NOT_CREATED" for row in result["videos"]))
        self.assertTrue(all(row["teacher_model"]=="GPT-6" and row["student_model"]=="Buddy" for row in result["videos"]))
        self.assertTrue(all(row["authoring_prompt"].endswith("freecodecamp-video-study-guide-authoring.md") for row in result["videos"]))
        self.assertIn("not a summary",result["truth_boundary"])

    def test_transcript_requires_all_three_separate_permissions_and_valid_hash(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            transcript=root/"data/freecodecamp/authorized-transcripts/v1.txt"
            transcript.parent.mkdir(parents=True)
            transcript.write_text("authorized source transcript",encoding="utf-8")
            import hashlib
            digest=hashlib.sha256(transcript.read_bytes()).hexdigest()
            row={"video_id":"v1","source_url":"https://www.youtube.com/watch?v=v1",
                "transcript_path":"data/freecodecamp/authorized-transcripts/v1.txt","transcript_sha256":digest,
                "rights_status":"VERIFIED","rights_evidence_ref":"permission-1",
                "study_permission":True,"summary_derivative_permission":True,"evaluation_permission":True,
                "training_permission":False}
            result=build_work_queue(catalog(),manifest([row]),root=root)
            self.assertEqual(result["authorized_for_guide_count"],1)
            self.assertEqual(result["videos"][0]["guide_status"],"READY_TO_AUTHOR")
            self.assertFalse(result["videos"][0]["model_training_authorized"])
            self.assertFalse(result["videos"][0]["model_training_started"])
            self.assertEqual(result["videos"][0]["authoring_status"],"ready_for_teacher_authoring")
            row["summary_derivative_permission"]=False
            result=build_work_queue(catalog(),manifest([row]),root=root)
            self.assertEqual(result["authorized_for_guide_count"],0)
            self.assertEqual(result["videos"][0]["rights_status"],"BLOCKED_PERMISSION_SCOPE")

    def test_approved_guide_requires_named_human_review_evidence_and_timestamp(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            transcript=root/"data/freecodecamp/authorized-transcripts/v1.txt"
            transcript.parent.mkdir(parents=True)
            transcript.write_text("authorized source transcript",encoding="utf-8")
            import hashlib
            digest=hashlib.sha256(transcript.read_bytes()).hexdigest()
            rights={"video_id":"v1","source_url":"https://www.youtube.com/watch?v=v1",
                "transcript_path":"data/freecodecamp/authorized-transcripts/v1.txt","transcript_sha256":digest,
                "rights_status":"VERIFIED","rights_evidence_ref":"permission-1",
                "study_permission":True,"summary_derivative_permission":True,"evaluation_permission":True,
                "training_permission":False}
            video=catalog()["videos"][0]
            guide={
                "schema":"dreamco.freecodecamp_video_study_guide.v1",
                "video_id":"v1",
                "source":{"url":video["url"],"title":video["title"],"transcript_sha256":digest},
                "rights":{"evidence_ref":"permission-1"},
                "summary":{"executive_overview":"x"*120,"detailed_explanation":"y"*600},
                "chapter_summaries":[{"start_seconds":0,"summary":"intro"}],
                "learning_objectives":["one","two","three"],
                "key_concepts":["one","two","three","four","five"],
                "terminology":["term"],"code_patterns":["pattern"],"worked_examples":["example"],
                "exercises":["one","two","three"],"projects":["project"],"common_mistakes":["mistake"],
                "debugging_playbook":["debug"],"prerequisites":["prerequisite"],
                "division_applications":["application"],"knowledge_checks":["1","2","3","4","5"],
                "answer_key":["1","2","3","4","5"],"references":["https://www.youtube.com/watch?v=v1"],
                "review":{"review_status":"approved"},
            }
            result=build_work_queue(catalog(),manifest([rights]),{"v1":guide},root=root)
            self.assertEqual(result["videos"][0]["guide_status"],"NEEDS_REVIEW")
            self.assertTrue(any("named human reviewer" in error for error in result["videos"][0]["guide_validation_errors"]))
            guide["review"].update({
                "reviewer":"human-reviewer-1",
                "reviewed_at":"2026-11-25T12:00:00Z",
                "review_evidence_ref":"review-record-1",
            })
            result=build_work_queue(catalog(),manifest([rights]),{"v1":guide},root=root)
            self.assertEqual(result["videos"][0]["guide_status"],"APPROVED")
            self.assertEqual(result["videos"][0]["guide_validation_errors"],[])

    def test_path_traversal_is_blocked(self):
        with tempfile.TemporaryDirectory() as temp:
            row={"video_id":"v1","source_url":"https://www.youtube.com/watch?v=v1",
                "transcript_path":"data/freecodecamp/authorized-transcripts/../../secret.txt",
                "transcript_sha256":"a"*64,"rights_status":"VERIFIED","rights_evidence_ref":"p",
                "study_permission":True,"summary_derivative_permission":True,"evaluation_permission":True}
            result=build_work_queue(catalog(),manifest([row]),root=Path(temp))
            self.assertEqual(result["videos"][0]["rights_status"],"BLOCKED_TRANSCRIPT_PATH")

    def test_partial_inventory_never_claims_complete(self):
        source=catalog()
        source["inventory_status"]="partial"
        result=build_work_queue(source,manifest())
        self.assertEqual(result["source_inventory_status"],"PARTIAL_OR_UNVERIFIED")

    def test_duplicate_ids_and_unsafe_scraping_policy_are_rejected(self):
        source=catalog()
        source["videos"].append(dict(source["videos"][0]))
        with self.assertRaisesRegex(ValueError,"unique"):
            build_work_queue(source,manifest())
        bad=manifest()
        bad["rights_policy"]["automatic_caption_scraping"]=True
        with self.assertRaisesRegex(ValueError,"automatic caption scraping"):
            build_work_queue(catalog(),bad)

if __name__=="__main__":
    unittest.main()
