import unittest

from tools.fetch_onet_task_curricula import (
    DownloadLinkParser, discover_json_links, enrich_occupations, flatten_records, read_table_rows
)


class OnetFullInventoryTests(unittest.TestCase):
    def test_read_table_rows_handles_json_arrays_and_nested_records(self):
        import json
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/"skills.json"
            path.write_text(json.dumps({"data":[{"onetsoc_code":"15-1252.00","element_name":"Programming"}]}),encoding="utf-8")
            rows=read_table_rows(path)
        self.assertEqual(rows[0]["element_name"],"Programming")

    def test_flatten_records_accepts_camel_case_task_statements_container(self):
        document = {
            "TaskStatements": {
                "data": [
                    {"O*NET-SOC Code": "15-1252.00", "Task ID": "1", "Task": "Write code"}
                ]
            }
        }
        rows = flatten_records(document)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["Task ID"], "1")

    def test_current_page_link_discovery_uses_exact_json_file_names(self):
        parser=DownloadLinkParser()
        parser.feed('<a href="/dl_files/database/31_0/task_statements.json">Tasks</a><a href="/dl_files/database/31_0/skills.csv">CSV</a>')
        links=discover_json_links(parser)
        self.assertIn("task_statements",links)
        self.assertNotIn("skills",links)
        self.assertTrue(links["task_statements"].endswith("task_statements.json"))

    def test_table_reader_compatibility_alias_uses_json_reader(self):
        import json
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "skills.json"
            path.write_text(json.dumps({"data": [{"onetsoc_code": "15-1252.00", "element_name": "Programming"}]}), encoding="utf-8")
            self.assertEqual(read_table_rows(path)[0]["element_name"], "Programming")

    def test_occupation_profiles_attach_skills_software_tools_and_task_ratings(self):
        result={
            "source":{},
            "inventory":{"occupations":1,"task_statements":1},
            "occupations":[{
                "occupation_code":"15-1252.00","occupation_title":"Software Developers",
                "tasks":[{"task_id":"123","task":"Write software"}],
                "task_playbooks":[{"task_id":"123","guide_authoring_brief":{}}],
            }],
        }
        exports={
            "occupation_data":[{"onetsoc_code":"15-1252.00","title":"Software Developers","description":"Develop software."}],
            "essential_skills":[{"onetsoc_code":"15-1252.00","element_id":"2.A.1","element_name":"Programming","data_value":"4.5"}],
            "transferable_skills":[{"onetsoc_code":"15-1252.00","element_name":"Critical Thinking","data_value":"4.2"}],
            "knowledge":[{"onetsoc_code":"15-1252.00","element_name":"Computers and Electronics","data_value":"4.6"}],
            "abilities":[{"onetsoc_code":"15-1252.00","element_name":"Deductive Reasoning","data_value":"4.0"}],
            "software_skills":[{"onetsoc_code":"15-1252.00","workplace_example":"Python","hot_technology":"Y","in_demand":"Y"}],
            "work_activities":[{"onetsoc_code":"15-1252.00","element_name":"Interacting With Computers","data_value":"4.8"}],
            "work_context":[{"onetsoc_code":"15-1252.00","element_name":"Electronic Mail","data_value":"4.9"}],
            "work_styles":[{"onetsoc_code":"15-1252.00","element_name":"Attention to Detail","data_value":"4.2"}],
            "education":[{"onetsoc_code":"15-1252.00","category":"Bachelor's degree","data_value":"60"}],
            "training_and_experience":[{"onetsoc_code":"15-1252.00","category":"Job training","data_value":"25"}],
            "job_titles":[{"onetsoc_code":"15-1252.00","alternate_title":"Application Developer"}],
            "related_occupations":[{"onetsoc_code":"15-1252.00","related_onetsoc_code":"15-1253.00","related_title":"Software QA Analysts"}],
            "career_interest_types":[{"onetsoc_code":"15-1252.00","element_name":"Investigative"}],
            "specific_interest_areas":[{"onetsoc_code":"15-1252.00","element_name":"Computing"}],
            "job_zones":[{"onetsoc_code":"15-1252.00","job_zone":"4","job_zone_description":"Considerable preparation"}],
            "task_ratings":[{"onetsoc_code":"15-1252.00","task_id":"123","scale_name":"Importance","data_value":"4.7"}],
        }
        manifest={"software_skills":{"sha256":"abc","rows":1}}
        enriched=enrich_occupations(result,exports,manifest)
        occupation=enriched["occupations"][0]
        self.assertEqual(occupation["description"],"Develop software.")
        self.assertEqual(occupation["job_zone"]["job_zone"],"4")
        self.assertEqual(occupation["profile"]["software_skill_examples"],["Python"])
        self.assertEqual(occupation["profile"]["hot_technologies"],["Python"])
        self.assertEqual(occupation["profile"]["essential_skills"][0]["element_name"],"Programming")
        self.assertEqual(occupation["tasks"][0]["ratings"][0]["data_value"],"4.7")
        playbook=occupation["task_playbooks"][0]
        self.assertEqual(playbook["occupation_profile_ref"],"15-1252.00")
        self.assertIn("Python",playbook["guide_authoring_brief"]["official_software_examples"])
        self.assertNotIn("software_skills",playbook.get("official_occupation_profile",{}))
        self.assertEqual(enriched["source"]["license"].split(";")[0],"Creative Commons Attribution 4.0 International")


if __name__=="__main__":
    unittest.main()
