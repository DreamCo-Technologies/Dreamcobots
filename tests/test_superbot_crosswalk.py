import json
import unittest
from pathlib import Path
from tools.build_superbot_crosswalk import build, ROOT, OUTPUT, PUBLIC


class SuperbotCrosswalkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = build()

    def test_generated_views_are_current(self):
        self.assertEqual(self.data, json.loads(OUTPUT.read_text()))
        self.assertEqual(self.data, json.loads(PUBLIC.read_text()))

    def test_all_namespaces_have_stable_unique_ids_and_one_existing_owner(self):
        owners = {d['name'] for d in json.loads((ROOT/'config/masterbot-65-registry.json').read_text())['divisions']}
        for namespace in ('proposals', 'bots', 'legacy'):
            rows = self.data[namespace]
            self.assertEqual(len(rows),len({r['id'] for r in rows}))
            for row in rows:
                self.assertIn(row['primary_owner'], owners)
                self.assertTrue(set(row['collaborators']) <= owners)
                self.assertFalse(row['capability_verified'])

    def test_all_original_records_preserved_and_historical_counts_not_added_to_fleet(self):
        summary = self.data['summary']
        self.assertEqual(212,summary['original_bot_records'])
        self.assertEqual(281,summary['historical_records'])
        self.assertEqual(1101,summary['shared_planner_profiles'])
        self.assertEqual(1232,summary['manifest_bots'])

    def test_every_candidate_is_an_existing_shared_planner(self):
        slugs = {r['id'] for r in self.data['bots'] if r['state']=='shared_planner_available'}
        for namespace in ('proposals','bots','legacy'):
            for row in self.data[namespace]:
                self.assertLessEqual(len(row['candidate_bots']),3)
                self.assertTrue({c['slug'] for c in row['candidate_bots']} <= slugs)

    def test_original_system_domain_is_not_changed_by_incidental_feature_words(self):
        row = next(r for r in self.data['legacy'] if r['source_refs']==['original-bots/systems/master-bot-system.md'])
        self.assertEqual('CommandCore',row['primary_owner'])
        row = next(r for r in self.data['legacy'] if r['source_refs']==['original-bots/systems/youtube-streaming-bot.md'])
        self.assertEqual('DreamContent',row['primary_owner'])


if __name__=='__main__':
    unittest.main()
