import json
import unittest
from pathlib import Path
from tools.normalize_legacy_portfolios import build_legacy_portfolios
ROOT=Path(__file__).resolve().parents[1]
class LegacyPortfolioTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.registry=json.loads((ROOT/'config/master_bot_registry.json').read_text());cls.data=build_legacy_portfolios(ROOT,cls.registry)
 def test_every_historical_record_is_counted_without_inflating_canonical_runtime_count(self):
  self.assertEqual(self.data['summary']['historical_source_records'],262)
  self.assertEqual(self.data['summary']['canonical_profiles'],1051)
  self.assertEqual(self.data['summary']['markdown_files_linked_to_canonical'],1051)
  ids=[x['id'] for x in self.data['items']];self.assertEqual(len(ids),len(set(ids)))
  self.assertEqual(len(self.data['bots']),len(ids))
 def test_every_legacy_record_has_the_shared_portfolio_contract_and_valid_division(self):
  divisions={d['name'] for d in self.registry['divisions']}
  for bot in self.data['bots']:
   self.assertIn(bot['identity']['division'],divisions)
   self.assertTrue(set(self.registry['bots'][0]).issubset(bot))
   self.assertTrue(bot['prospectus']['mission'])
   self.assertTrue(bot['capabilities'])
   self.assertFalse(bot['readiness']['production_verified'])
   self.assertTrue((ROOT/bot['evidence']['historical_source']).is_file())
 def test_all_markdown_profiles_are_either_canonical_linked_or_historical(self):
  covered={x['path'] for x in self.data['canonical_markdown_links']}
  covered|={x['source_refs'][0] for x in self.data['items'] if x['category']=='historical_markdown_profile'}
  self.assertEqual(covered,{p.relative_to(ROOT).as_posix() for p in (ROOT/'bots').rglob('*.md')})
 def test_old_specifications_and_source_categories_survive_normalization(self):
  row=next(x for x in self.data['items'] if x['source_refs']==['bots/saas-builder.md'])
  self.assertEqual(row['source_division'],'DreamSaaS');self.assertEqual(row['division_id'],'dreamautomation')
  bot=next(x for x in self.data['bots'] if x['identity']['slug']==row['id'])
  self.assertEqual(bot['historical_specification'],(ROOT/'bots/saas-builder.md').read_text())
if __name__=='__main__':unittest.main()
