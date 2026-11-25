import unittest

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
        result = build(self.profiles, self.hf, self.fcc, self.onet, self.taxonomy, self.university)
        self.assertEqual(result["coverage"]["domain_divisions"], 55)
        self.assertEqual(result["coverage"]["freecodecamp_tracks"], 1)
        code = next(row for row in result["divisions"] if row["division"] == "DreamCodeLab")
        self.assertIn("javascript_and_typescript", code["freecodecamp_tracks"])
        self.assertTrue(code["shared_core"])
        self.assertIn("programming", code["freecodecamp_video_subject_categories"])
        self.assertTrue(code["college_domains"])
        self.assertTrue(code["source_families"])
        self.assertGreater(result["coverage"]["hugging_face_subject_terms"], 0)

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
        self.assertIn("IDE", task["task_specific_software_categories"])
        self.assertIn("debugging", task["agent_capabilities_to_assess"])

    def test_map_does_not_claim_training_or_mastery(self):
        result = build(self.profiles, self.hf, self.fcc, self.onet, self.taxonomy)
        self.assertIn("does not prove", result["truth_boundary"])
        self.assertTrue(result["training_policy"]["no_weight_training_without_asset_level_permission"])
        self.assertEqual(result["university_curriculum"]["title"], "DreamCo Buddy University")
        self.assertTrue(result["source_family_routes"])


if __name__ == "__main__":
    unittest.main()
