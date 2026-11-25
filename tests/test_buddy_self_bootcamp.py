import unittest
from tools.build_buddy_self_bootcamp import build, division_names, map_subjects

class SelfBootcampTests(unittest.TestCase):
    def test_parser_requires_exactly_55_complete_division_profiles(self):
        source="\n".join(
            f"  Division{i}: {{\n    purpose: 'purpose',\n    focusAreas: [],\n    serves: [],\n    outcome: 'outcome',\n    boundary: 'boundary',\n  }}"
            for i in range(55)
        )
        self.assertEqual(len(division_names(source)),55)
        incomplete="\n".join(
            f"  Division{i}: {{\n    purpose: 'purpose',\n    focusAreas: [],\n    serves: [],\n    outcome: 'outcome',\n    boundary: 'boundary',\n  }}"
            for i in range(54)
        )
        with self.assertRaises(ValueError):
            division_names(incomplete)

    def test_hugging_face_subjects_are_matched_not_broadcast_to_every_division(self):
        record={"division":"DreamData","purpose":"Build data platforms and analytics",
          "outcome":"Reliable analytics and data pipelines","focus_areas":["SQL","data engineering","dashboards"],
          "serves":["data teams"]}
        selected,matched=map_subjects(record,["audio","music-generation","data-engineering","sql","vision","statistics","business"])
        self.assertIn("data-engineering",matched)
        self.assertIn("sql",matched)
        self.assertNotIn("audio",matched)
        self.assertNotIn("vision",matched)
        self.assertIn("statistics",selected)

    def test_builds_all_division_paths_and_preserves_truth_boundary(self):
        names=[f"Division{i}" for i in range(55)]
        workforce={"training_paths":[{"id":"sales"}]}
        government={"official_sources":[{"id":"onet"}]}
        result=build(names,{"subject_terms":["audio","vision"]},{"inventory":{"occupations":2,"task_statements":8}},
          {"counts":{"discovered":12,"guide_authoring_eligible":1,"rights_pending":11}},workforce,government)
        self.assertEqual(result["coverage"]["domain_divisions"],55)
        self.assertEqual(len(result["divisions"]),55)
        self.assertEqual(result["coverage"]["onet_task_statements"],8)
        self.assertIn("not proof",result["truth_boundary"])
        self.assertTrue(result["buddy_bootcamp_builder_loop"]["steps"])
        self.assertIn("buddy_ai_college", result)
        self.assertIn("tool_capability_families", result["divisions"][0]["autonomous_agent_capability_curriculum"])

    def test_freecodecamp_certifications_and_university_domains_are_routed_per_division(self):
        divisions = [
            {"division": "DreamCodeLab", "purpose": "Build software", "outcome": "Ship applications",
             "focus_areas": ["JavaScript", "Python", "web development"], "serves": ["developers"]},
            {"division": "DreamData", "purpose": "Build data platforms", "outcome": "Reliable analytics",
             "focus_areas": ["SQL", "data engineering"], "serves": ["analysts"]},
        ]
        fcc = {"scope": {"coverage_status": "ROADMAP_DEFINED"},
               "official_platform_inventory": {"core_certifications": [
                   {"id": "javascript-v9", "name": "JavaScript", "skills": ["JavaScript", "DOM", "testing"]},
                   {"id": "relational-databases-v9", "name": "Relational Databases", "skills": ["SQL", "database design"]}
               ], "additional_certifications": []},
               "video_learning_tracks": ["javascript_and_typescript"]}
        college = {"knowledge_domains": [{"id": "software-engineering", "name": "Software Engineering",
                                           "tracks": ["JavaScript", "testing"]}]}
        result = build(divisions, {"subject_terms": ["javascript", "sql"]}, {"inventory": {}},
                       {"counts": {}}, {"training_paths": []}, {"official_sources": []}, college, fcc)
        code = next(x for x in result["divisions"] if x["division"] == "DreamCodeLab")
        data = next(x for x in result["divisions"] if x["division"] == "DreamData")
        self.assertIn("javascript-v9", [x["id"] for x in code["freecodecamp_learning_paths"]["matched_certifications"]])
        self.assertIn("relational-databases-v9", [x["id"] for x in data["freecodecamp_learning_paths"]["matched_certifications"]])
        self.assertTrue(code["college_curriculum"]["matched_domains"])

if __name__=="__main__": unittest.main()
