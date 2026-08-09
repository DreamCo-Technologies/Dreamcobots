import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class GlobalGovernmentSystemTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gov=json.loads((ROOT/'config/government-nonprofit-contract-readiness.json').read_text())
        cls.model=json.loads((ROOT/'config/global-government-operating-model.json').read_text())
        cls.sources=json.loads((ROOT/'config/global-government-source-adapters.json').read_text())
        cls.discovery=json.loads((ROOT/'config/global-government-jurisdiction-discovery.json').read_text())
        cls.ontology=json.loads((ROOT/'config/dreamco-operational-ontology.json').read_text())

    def test_global_functions_cover_cofog_level_one(self):
        expected={'general public services','defence','public order and safety','economic affairs','environmental protection','housing and community amenities','health','recreation culture and religion','education','social protection'}
        self.assertEqual(set(self.model['reference_taxonomy']['functions']),expected)
        self.assertEqual(set(self.gov['global_function_taxonomy']),expected)

    def test_every_department_gets_iterative_benchmarks(self):
        rule=self.discovery['department_iteration_rule'].lower()
        for phrase in ['service','job/task','spending','procurement','data/api','accessibility','productivity','parallel builders']:
            self.assertIn(phrase,rule)

    def test_service_simplification_is_measured(self):
        metrics=set(self.gov['service_simplification_metrics'])
        for item in {'steps per journey','forms per journey','documents required','average completion time','processing time','error/rejection rate','cost to citizen','agency processing cost','digital completion rate'}:
            self.assertIn(item,metrics)

    def test_public_money_requires_source_and_freshness(self):
        rule=self.gov['fiscal_transparency']['rule'].lower()
        self.assertIn('authoritative',rule)
        self.assertIn('freshness',rule)
        self.assertIn('never manufacture',rule)
        source_ids={x['id'] for x in self.sources['sources']}
        self.assertIn('us_treasury_debt_to_penny',source_ids)
        self.assertIn('us_usaspending',source_ids)
        self.assertIn('jurisdiction_official_debt',source_ids)
        self.assertIn('jurisdiction_official_spending',source_ids)

    def test_economic_development_and_housing_are_first_class(self):
        self.assertGreaterEqual(len(self.gov['local_economic_development']),15)
        self.assertGreaterEqual(len(self.gov['housing_real_estate_intelligence']),15)
        self.assertIn('foreclosure/public auction sources',self.gov['housing_real_estate_intelligence'])
        self.assertIn('measurable city growth plan',self.gov['local_economic_development'])

    def test_ontology_models_government_and_fiscal_records(self):
        types=set(self.ontology['object_types'])
        for item in {'Government','Jurisdiction','GovernmentDepartment','GovernmentProgram','GovernmentService','GovernmentJob','PublicBudget','PublicSpendingRecord','PublicDebtRecord','PublicContract','PublicGrant','EconomicDevelopmentPlan','HousingProgram','PropertyOpportunity'}:
            self.assertIn(item,types)
        self.assertTrue(self.ontology['governance']['government_facts_require_authoritative_source'])
        self.assertTrue(self.ontology['governance']['fiscal_values_require_source_date_and_definition'])

    def test_worldwide_discovery_does_not_assume_us_structure(self):
        self.assertIn('M49',self.discovery['seed_standard'])
        self.assertIn('do not assume every country uses U.S.-style',self.discovery['local_government_rule'])
        self.assertIn('authoritative government source',self.discovery['truth_rule'])

if __name__=='__main__': unittest.main()
