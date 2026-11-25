import unittest
import json
from pathlib import Path

from tools.build_buddy_university_curriculum import build, division_profiles


def profile_source():
    names = ["CommandCore", "DreamAIInfra", "DreamAdmin", "DreamAgents", "DreamAgriculture",
             "DreamArts", "DreamAutomation", "DreamBizLaunch", "DreamCodeLab", "DreamConstruction",
             "DreamContent", "DreamCrypto", "DreamCustIntel", "DreamCyber", "DreamData",
             "DreamDecision", "DreamEducation", "DreamEmpire", "DreamEntFinance", "DreamFinance",
             "DreamFlow", "DreamFood", "DreamGlobal", "DreamHealth", "DreamInfluence",
             "DreamLegal", "DreamLoans", "DreamMaintenance", "DreamMarket", "DreamMilitary",
             "DreamOps", "DreamPayments", "DreamPersonalCare", "DreamPlanetary", "DreamProServices",
             "DreamProduction", "DreamProtection", "DreamRealEstate", "DreamRetail", "DreamSalesPro",
             "DreamScience", "DreamSocial", "DreamTrade", "DreamTransport", "GameTitan",
             "DreamAffiliate", "DreamAgency", "DreamFoundry", "DreamFranchise", "DreamIntegrations",
             "DreamLicensing", "DreamRobotics", "DreamSaaS", "DreamStreaming", "DreamTravel"]
    rows = ["export const DIVISION_DOMAIN_PROFILES = {"] 
    for name in names:
        rows.append(f'''  {name}: {{
    purpose: "Build software and professional services for customers.",
    serves: ["learners", "operators"],
    outcome: "Deliver verified customer outcomes.",
    boundary: "Human approval and professional rules apply.",
    focusAreas: ["software development", "customer service", "data analysis"],
  }},''')
    rows.append("};")
    return "\n".join(rows)


class BuddyUniversityCurriculumTests(unittest.TestCase):
    def setUp(self):
        self.profiles = division_profiles(profile_source())
        self.hf = {"discovery": {"hugging_face_subjects": ["audio", "quux-ontology"]}}
        self.taxonomy = {"subject_terms": ["text-generation", "quux-ontology"]}
        self.fcc = {"specialist_track_details": [{
            "id": "javascript_and_typescript", "name": "JavaScript",
            "related_divisions": ["DreamCodeLab"], "learning_outcomes": ["Build tested software"],
            "capstone": "Build an app", "required_before_mastery": ["unseen holdout"]
        }], "video_learning_tracks": ["programming", "audio production"]}
        self.fcc_catalog = {"schema": "dreamco.freecodecamp_catalog.v1", "inventory_status": "partial", "video_count": 2, "inventory": {"complete": False, "expected_entry_count": 1800, "observed_entry_count": 2}, "videos": [{"video_id": "abc123", "title": "JavaScript course", "categories": ["javascript_and_typescript"], "rights_status": "review_required", "learning_status": "not_studied"}, {"video_id": "xyz789", "title": "Unclassified lesson", "categories": ["other_or_unclassified"], "rights_status": "review_required", "learning_status": "not_studied"}]}
        self.university = {"title": "DreamCo Buddy University", "knowledge_domains": [{"id": "computer-science", "scope": "Algorithms and software engineering"}], "source_families": [{"id": "open-academic-research", "scope": "research papers and scholarly datasets"}], "academic_structure": {"levels": [{"level": "100"}]}, "instructional_model": {"teacher": {"role": "ChatGPT"}, "student": {"role": "Buddy"}}}
        self.onet = {"source": {"name": "O*NET"}, "inventory": {"occupations": 1, "task_statements": 1},
                     "occupations": [{"occupation_code": "15-1252.00", "occupation_title": "Software Developers",
                                      "tasks": [{"task_id": "123", "task": "Write software code and test applications"}],
                                      "task_playbooks": [{"task_id": "123", "guide_authoring_brief": {"software_categories_to_assess": ["IDE", "testing"], "agent_capabilities_to_assess": ["debugging"], "must_include": ["capstone"]}, "commercial_pathway": {"status": "research_required"}}]}]}

    def test_requires_exactly_55_complete_domain_profiles(self):
        self.assertEqual(len(self.profiles), 55)
        with self.assertRaises(ValueError):
            division_profiles(profile_source().replace('  DreamTravel: {', '  DreamTravelRemoved: {').replace('  DreamTravelRemoved: {\n    purpose:', ''))

    def test_huggingface_and_freecodecamp_routes_are_connected(self):
        result = build(self.profiles, self.hf, self.fcc, self.onet, self.taxonomy, self.university, self.fcc_catalog)
        self.assertEqual(result["coverage"]["domain_divisions"], 55)
        self.assertEqual(result["coverage"]["freecodecamp_tracks"], 1)
        code = next(row for row in result["divisions"] if row["division"] == "DreamCodeLab")
        self.assertIn("javascript_and_typescript", code["freecodecamp_tracks"])
        self.assertTrue(code["shared_core"])
        self.assertIn("programming", code["freecodecamp_video_subject_categories"])
        self.assertTrue(code["college_domains"])
        self.assertTrue(code["source_families"])
        self.assertGreater(result["coverage"]["hugging_face_subject_terms"], 0)
        self.assertEqual(result["coverage"]["freecodecamp_catalog_videos"], 2)
        self.assertEqual(result["coverage"]["freecodecamp_inventory_status"], "partial")
        self.assertEqual(len(result["freecodecamp_video_routes"]), 2)
        self.assertIn("DreamCodeLab", result["freecodecamp_video_routes"][0]["specialty_division_ids"])

    def test_unclassified_topics_are_not_silently_dropped(self):
        result = build(self.profiles, self.hf, self.fcc, self.onet, self.taxonomy)
        row = next(row for row in result["hugging_face_subject_routes"] if row["subject"] == "quux-ontology")
        self.assertEqual(row["mapping_status"], "unclassified_shared_review")
        self.assertTrue(result["unclassified_subjects"])

    def test_onet_task_is_in_global_and_division_catalog(self):
        result = build(self.profiles, self.hf, self.fcc, self.onet, self.taxonomy)
        self.assertEqual(result["coverage"]["onet_task_statements"], 1)
        task = result["onet_task_routes"][0]
        self.assertIn("DreamCodeLab", task["division_ids"])
        self.assertIn(task["task_ref"], next(x for x in result["divisions"] if x["division"] == "DreamCodeLab")["onet_task_refs"])
        self.assertEqual(task["teacher_model"],"GPT-6")
        self.assertEqual(task["student_model"],"Buddy")
        self.assertTrue(task["software_capability_categories"])
        self.assertTrue(task["agent_capabilities_to_assess"])
        self.assertFalse(task["model_training_eligible"])
        self.assertEqual(task["task_specific_software_category_count"], 2)
        self.assertEqual(task["agent_capability_count"], 1)
        self.assertIn("O*NET", task["task_playbook_source"])

    def test_college_domains_and_full_freecodecamp_catalog_are_attached(self):
        college = {
            "knowledge_domains": [{"id": "computer-science", "scope": "software engineering and programming"}],
            "source_families": [{"id": "official-docs", "scope": "programming and engineering documentation"}],
            "agent_capability_matrix": [{"id": "software", "capabilities": ["coding", "testing"]}],
            "academic_structure": {"levels": [{"level": "100"}]},
            "instructional_model": {"teacher": {"role": "GPT-6 instructor"}, "student": {"role": "Buddy learner"}},
        }
        catalog = {
            "schema": "dreamco.freecodecamp_catalog.v1",
            "inventory_status": "complete",
            "inventory": {"complete": True, "expected_entry_count": 1, "observed_entry_count": 1},
            "videos": [{"video_id": "video-1", "title": "JavaScript", "url": "https://youtube.com/watch?v=video-1",
                        "categories": ["javascript_and_typescript"], "rights_status": "review_required",
                        "learning_status": "not_studied"}],
        }
        workforce = {"training_paths": [{"id": "public-procurement", "title": "Government Contracting", "subjects": ["procurement", "sales", "compliance"]}]}
        government = {"official_sources": [{"id": "sam", "url": "https://sam.gov"}],
                      "procurement_pipeline": ["market_research", "bid_no_bid"],
                      "grant_pipeline": ["eligibility_review"],
                      "benefit_protections": {"no_eligibility_guarantees": True}}
        result = build(self.profiles, self.hf, self.fcc, self.onet, self.taxonomy, college, catalog, workforce, government)
        self.assertEqual(result["coverage"]["freecodecamp_channel_videos"], 1)
        self.assertEqual(result["coverage"]["freecodecamp_channel_inventory_status"], "complete")
        code = next(row for row in result["divisions"] if row["division"] == "DreamCodeLab")
        self.assertIn("video-1", code["freecodecamp_video_ids"])
        self.assertTrue(code["college_domains"])
        self.assertEqual(code["agent_capability_catalog"][0]["id"], "software")
        self.assertEqual(result["instructional_model"]["teacher"]["role"], "GPT-6 instructor")
        self.assertTrue(result["source_family_routes"])
        self.assertTrue(result["venture_and_workforce_tracks"])
        self.assertTrue(all(row["teacher_model"]=="GPT-6" and row["student_model"]=="Buddy" for row in result["venture_and_workforce_tracks"]))
        self.assertTrue(result["government_and_community_curriculum"]["benefit_protections"]["no_eligibility_guarantees"])

    def test_full_freecodecamp_specialist_and_certification_inventory_maps(self):
        root = Path(__file__).resolve().parents[1]
        roadmap = json.loads((root / "config/freecodecamp-complete-learning-path.json").read_text(encoding="utf-8"))
        result = build(self.profiles, self.hf, roadmap, {"occupations": [], "inventory": {}}, self.taxonomy)
        self.assertEqual(result["coverage"]["freecodecamp_tracks"], 34)
        self.assertEqual(result["coverage"]["freecodecamp_video_subject_categories"], 22)
        self.assertTrue(all(row["division_ids"] for row in result["freecodecamp_track_routes"]))
        self.assertTrue(all(row["division_ids"] for row in result["freecodecamp_video_category_routes"]))
        self.assertGreater(result["coverage"]["divisions_with_freecodecamp_tracks"], 0)

    def test_full_university_has_course_blueprints_for_every_division(self):
        root = Path(__file__).resolve().parents[1]
        college = json.loads((root / "config/buddy-university-curriculum.json").read_text(encoding="utf-8"))
        roadmap = json.loads((root / "config/freecodecamp-complete-learning-path.json").read_text(encoding="utf-8"))
        bootcamp = json.loads((root / "config/buddy-open-source-bootcamp.json").read_text(encoding="utf-8"))
        workforce = json.loads((root / "config/buddy-workforce-entrepreneurship-bootcamp.json").read_text(encoding="utf-8"))
        government = json.loads((root / "config/buddy-government-community-enterprise-curriculum.json").read_text(encoding="utf-8"))
        result = build(self.profiles, bootcamp, roadmap, {"occupations": [], "inventory": {}},
                       self.taxonomy, college, None, workforce, government)
        self.assertEqual(result["coverage"]["college_domains"], 45)
        self.assertEqual(result["coverage"]["college_courses"], 45 * 4 + len(college["shared_core"]["required_for_all_divisions"]))
        self.assertEqual(len(result["divisions"]), 55)
        self.assertTrue(all(len(row["shared_core_course_ids"]) == 10 for row in result["divisions"]))
        self.assertTrue(all(row["college_course_ids"] for row in result["divisions"]))
        self.assertEqual(result["instructional_model"]["teacher"]["role"].split()[0], "ChatGPT/GPT-6")
        self.assertEqual(result["instructional_model"]["student"]["role"], "Buddy is the student and must demonstrate learning through observable work")

    def test_map_does_not_claim_training_or_mastery(self):
        result = build(self.profiles, self.hf, self.fcc, self.onet, self.taxonomy)
        self.assertIn("does not prove", result["truth_boundary"])
        self.assertTrue(result["training_policy"]["no_weight_training_without_asset_level_permission"])
        self.assertEqual(result["university_curriculum"]["title"], "DreamCo Buddy University")
        self.assertTrue(result["source_family_routes"])


if __name__ == "__main__":
    unittest.main()
