import copy
import json
from pathlib import Path
import tempfile
import unittest
import zipfile
from tools import fleet_daily_factory as factory

class FactoryTests(unittest.TestCase):
    def setUp(self):
        self.request=json.loads((factory.ROOT/'config/bots/daily-build-request.json').read_text())
    def test_bounded_complete_plan(self):
        plan=factory.plan(self.request)
        self.assertEqual(plan['selected_count'],1232)
        self.assertEqual(len(plan['batches']),13)
        self.assertTrue(all(len(b['bot_ids'])<=100 for b in plan['batches']))
    def test_invalid_requests_fail_closed(self):
        for change in [{'max_items':1},{'max_items':5001},{'max_parallel':9},{'batch_size':True},{'request_id':'../../bad'},{'selection':'explicit','bot_ids':['unknown']},{'selection':'explicit','bot_ids':['x','x']}]:
            with self.subTest(change=change), self.assertRaises(ValueError):factory.plan({**self.request,**change})
    def test_disabled_is_empty(self):
        self.assertEqual(factory.plan({**self.request,'enabled':False})['batches'],[])
    def test_evidence_requires_every_shard(self):
        self.assertFalse(factory.reduce_results(factory.plan(self.request),[])['ok'])
    def test_real_bundle_and_tamper_checks(self):
        plan=factory.plan({**self.request,'batch_size':1})
        with tempfile.TemporaryDirectory() as tmp:
            report=factory.build_batch(plan,0,tmp)
            row=report['results'][0]
            with zipfile.ZipFile(Path(tmp)/(row['bot']+'.zip')) as z:
                self.assertEqual('run.py' in z.namelist(),row['status']=='shared_engine_bundle_tested')
                if 'run.py' in z.namelist():compile(z.read('run.py'),'run.py','exec')
            bad=copy.deepcopy(plan);bad['batches'][0]['bot_ids']=['bad']
            with self.assertRaises(ValueError):factory.build_batch(bad,0,tmp)
            with self.assertRaises(ValueError):factory.reduce_results(plan,[report,report])
            report['results'][0]['production_ready']=True
            with self.assertRaises(ValueError):factory.reduce_results(plan,[report])

if __name__=='__main__':unittest.main()
