import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class UniversalCapabilityBenchmarkPolicyTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.u=json.loads((ROOT/'config/universal-human-computer-ai-benchmark.json').read_text()); cls.g=json.loads((ROOT/'config/government-nonprofit-contract-readiness.json').read_text()); cls.c=json.loads((ROOT/'config/creative-studio-mastery-benchmarks.json').read_text()); cls.d=json.loads((ROOT/'config/continuous-human-value-discovery.json').read_text())
 def test_broad_computer_ai_and_business_coverage(self):
  for key in ['communication','knowledge','office_productivity','software_and_data','creative_media','commerce_and_money','business_lifecycle','industry_operations','government_and_civic','nonprofit','personal_life']: self.assertIn(key,self.u['domains'])
  self.assertGreaterEqual(len(self.u['benchmark_dimensions']),20); self.assertGreaterEqual(len(self.u['gap_parallel_workers']),6); self.assertIn('every failed or missing benchmark',self.u['gap_rule'].lower())
 def test_business_lifecycle_is_end_to_end(self):
  text=' '.join(self.u['domains']['business_lifecycle']).lower()
  for phrase in ['idea discovery','entity formation','finance','product development','hiring','sales','marketing','expansion','shutdown']: self.assertIn(phrase,text)
 def test_government_assistance_preserves_human_authority(self):
  self.assertGreaterEqual(len(self.g['government_job_families']),20); self.assertGreaterEqual(len(self.g['contracting_lifecycle']),20); self.assertGreaterEqual(len(self.g['nonprofit_lifecycle']),15)
  self.assertIn('contract award decision',self.g['high_risk_human_authority']); self.assertIn('must not invent',self.g['truth_rule'].lower())
 def test_creative_studio_has_full_pipelines(self):
  self.assertGreaterEqual(len(self.c['film']),20); self.assertGreaterEqual(len(self.c['books']),15); self.assertGreaterEqual(len(self.c['music']),20); self.assertIn('provenance',self.c['rights_rule'].lower())
 def test_continuous_discovery_is_evidence_based(self):
  ids={x['id'] for x in self.d['loops']}
  for x in ['productivity','intelligence','software_products','business_owner','autonomous_revenue','government','contracts','nonprofit']: self.assertIn(x,ids)
  self.assertIn('hypotheses',self.d['promotion_rule'].lower())
if __name__=='__main__': unittest.main()
