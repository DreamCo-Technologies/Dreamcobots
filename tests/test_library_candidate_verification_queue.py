import unittest
from tools.build_library_candidate_verification_queue import build_queue


class LibraryCandidateVerificationQueueTests(unittest.TestCase):
    def setUp(self):
        self.catalog={"schema":"dreamco.buddy_library_seed_catalog.v1","status":"partial_unverified_seed_inventory",
            "unique_candidate_count":2,"candidates":[
                {"id":"seed-a","name":"Alpha","categories":["python"],"status":"seed_candidate_unverified",
                 "rights":{"download":"pending","execution":"prohibited_by_seed_catalog","evaluation":"pending","training":"pending"},
                 "source":{"path":"seed.ts"}},
                {"id":"seed-b","name":"Beta","categories":["javascript"],"status":"seed_candidate_unverified",
                 "rights":{"download":"pending","execution":"prohibited_by_seed_catalog","evaluation":"pending","training":"pending"},
                 "source":{"path":"seed.ts"}}]}
        self.ecosystems={"schema":"dreamco.library_ecosystems.v1","ecosystems":[{"id":"python"},{"id":"javascript"}]}

    def test_every_seed_becomes_unverified_queue_item_without_download_or_execution(self):
        report=build_queue(self.catalog,self.ecosystems)
        self.assertEqual(report["candidate_count"],2)
        self.assertEqual(report["ecosystem_count"],2)
        self.assertTrue(all(row["verification_status"]=="unverified_candidate" for row in report["candidates"]))
        self.assertTrue(all(row["package_downloaded"] is False and row["code_executed"] is False for row in report["candidates"]))
        self.assertFalse(report["worldwide_completeness_claimed"])

    def test_duplicate_candidate_ids_are_rejected(self):
        self.catalog["candidates"].append(dict(self.catalog["candidates"][0]))
        report=build_queue(self.catalog,self.ecosystems)
        self.assertTrue(any("duplicate candidate ID" in error for error in report["errors"]))

    def test_seed_cannot_grant_execution_permission(self):
        self.catalog["candidates"][0]["rights"]["execution"]="allowed"
        report=build_queue(self.catalog,self.ecosystems)
        self.assertTrue(any("execution must remain prohibited" in error for error in report["errors"]))

    def test_declared_count_must_match_rows(self):
        self.catalog["unique_candidate_count"]=9
        report=build_queue(self.catalog,self.ecosystems)
        self.assertTrue(any("unique_candidate_count" in error for error in report["errors"]))

    def test_missing_ecosystem_schema_fails(self):
        with self.assertRaisesRegex(ValueError,"ecosystem schema"):
            build_queue(self.catalog,{"ecosystems":[]})


if __name__=="__main__": unittest.main()
