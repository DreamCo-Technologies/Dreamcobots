"""Synthetic control tests: these are never Buddy/model capability evidence."""
from __future__ import annotations
import copy
import json
import tempfile
import threading
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from http.server import ThreadingHTTPServer
from urllib.request import Request, urlopen
from urllib.error import HTTPError

from buddy_os.evaluation.review import ReviewStore, boundary, digest, POLICY
from buddy_os.evaluation.evidence import assess, calibration, contamination, help_required, promotion, claim_gate, distill, verify_artifacts, debate_assessment
from buddy_os.evaluation.runtime import GovernedAdapter, execute_reviewed, LongHorizon, ComponentRegistry, EvaluationTaskAdapter
from tools.general_intelligence import build, generate
from tools.buddy_local_bridge import BuddyLocalHandler, BridgeState


def action(kind='code_change', **kw):
    result = dict(action_class=kind, title='Review bounded change', rationale='Fix demonstrated regression', evidence=['test:case-1'], risk='low', reversible=True, expected_cost_usd=0, tools=['sandbox'], data=['fixture'], preview='A concrete diff or preview', verification='Run focused regression', rollback='Restore previous revision', parameters={})
    result.update(kw)
    return result


def bundle():
    cases = [dict(id=f'task-{i}', repetition=j, split='transfer' if i == 2 else 'holdout', cross_domain=i==2,
                  withheld_from_training=True, family=f'family-{i}', fixture_hash=digest(['fixture',i]), response_hash=digest(['output',i]),
                  quality=0.9, safety=1.0, factuality=1.0, latency_ms=10, runtime_ms=10, cost_usd=0, human_interventions=0, external_assistance=False)
             for i in range(3) for j in range(3)]
    return dict(id='test-only-run', schema='dreamco.general_intelligence_run.v1', capability='reasoning', subject='unit-test-fixture',
                components=dict(model='fixture-v1',policy='p1',router='r1',retrieval='d1'),suite_id='test-suite', suite_version='1', suite_hash=digest('suite'),
                dataset_hash=digest('data'),grader_version='1',seed=73,hardware='test-fixture',runtime='test-runtime',timestamp='2026-01-01T00:00:00Z',
                license_review=dict(allowed=True,reviewer='test-human',source='owned-fixture'),contamination=contamination([], []),cases=cases,
                expected_cases=['task-0','task-1','task-2'],baseline_id='baseline',baseline_hash=digest('baseline'),simulated=False,
                config_hash=digest('config'),artifacts=[dict(path='trace.json',sha256=digest('trace'))],training_corpus_hash=digest('training'),
                calibration=[dict(confidence=1.0, correct=True,abstained=False,should_abstain=False)],red_team={k:True for k in POLICY['red_team']})


class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.store=ReviewStore(Path(self.tmp.name)/'review.db')
    def tearDown(self): self.tmp.cleanup()
    def approved(self, kind='code_change', **kw):
        i=self.store.propose(action(kind,**kw)); row=self.store.decide(i,1,'approve','owner'); return i,row['hash']
    def test_all_consequential_classes_require_humans_at_all_levels(self):
        for level in POLICY['autonomy']:
            for kind in POLICY['approval_actions']:
                self.assertEqual(boundary(action(kind),level),'approval_required',(level,kind))
            for kind in POLICY['forbidden_actions']:
                self.assertEqual(boundary(action(kind),level),'forbidden')
    def test_autonomy_only_allows_exact_low_risk_zero_cost_scopes(self):
        self.assertEqual(boundary(action('sandbox'),'Guided'),'approval_required')
        self.assertEqual(boundary(action('draft'),'Semi'),'allowed')
        self.assertEqual(boundary(action('sandbox'),'High'),'allowed')
        for change in ({'risk':'high'},{'reversible':False},{'expected_cost_usd':0.01}):
            self.assertEqual(boundary(action('sandbox',**change),'High'),'approval_required')
        with self.assertRaises(ValueError): boundary(action('unknown'),'High')
        with self.assertRaises(ValueError): boundary(action(),'unknown')
    def test_forbidden_never_reviewable(self):
        i=self.store.propose(action('delete'))
        with self.assertRaises(ValueError): self.store.decide(i,1,'approve','owner')
    def test_scope_expiry_budget_and_replay(self):
        i,h=self.approved(expected_cost_usd=2)
        for options in [dict(expected_hash='wrong',action_class='code_change',budget_usd=2),dict(expected_hash=h,action_class='payment',budget_usd=2),dict(expected_hash=h,action_class='code_change',budget_usd=1)]:
            with self.assertRaises(ValueError): self.store.consume(i,**options)
        self.store.consume(i,h,action_class='code_change',budget_usd=2)
        with self.assertRaises(ValueError): self.store.consume(i,h,action_class='code_change',budget_usd=2)
        j,k=self.approved()
        with self.store.connect() as db: db.execute('UPDATE actions SET expires=0 WHERE id=?',(j,))
        with self.assertRaises(ValueError): self.store.consume(j,k,action_class='code_change')
    def test_edits_invalidate_approval_and_stale_decisions(self):
        i,h=self.approved(); row=self.store.decide(i,2,'edit','owner',edited=action(preview='Changed diff'))
        self.assertEqual(row['status'],'pending'); self.assertNotEqual(row['hash'],h)
        with self.assertRaises(ValueError): self.store.decide(i,2,'approve','owner')
        with self.assertRaises(ValueError): self.store.consume(i,h,action_class='code_change')
    def test_concurrent_consumption_is_single_use(self):
        i,h=self.approved()
        def use(_):
            try: self.store.consume(i,h,action_class='code_change'); return True
            except ValueError: return False
        with ThreadPoolExecutor(max_workers=4) as pool: self.assertEqual(sum(pool.map(use,range(8))),1)
    def test_persistence_and_append_only_chain(self):
        i,h=self.approved(); other=ReviewStore(self.store.path); self.assertEqual(other.get(i)['hash'],h)
        self.assertEqual([e['kind'] for e in other.audit()],['proposed','approve'])
        with self.assertRaises(Exception):
            with other.connect() as db: db.execute("UPDATE audit SET hash='forged'")
    def test_reject_escalate_and_post_verification(self):
        i=self.store.propose(action()); self.store.decide(i,1,'escalate','owner')
        row=self.store.decide(i,2,'reject','owner'); self.assertEqual(row['status'],'rejected')
        with self.assertRaises(ValueError): self.store.consume(i,row['hash'],action_class='code_change')
        i,h=self.approved(); self.store.consume(i,h,action_class='code_change')
        self.store.finish(i,passed=True,evidence_hash=digest('result'),actual_cost_usd=1)
        self.assertEqual(self.store.get(i)['status'],'failed')
        with self.assertRaises(ValueError): self.store.finish(i,passed=True,evidence_hash=digest('result'),actual_cost_usd=0)
    def test_invalid_numbers_and_credentials(self):
        for value in (float('nan'),float('inf'),-1,True):
            with self.assertRaises(ValueError): self.store.propose(action(expected_cost_usd=value))
        with self.assertRaises(ValueError): self.store.propose(action(preview='Bearer secret-placeholder'))
    def test_adapter_runs_only_after_consumption_and_records_verification(self):
        calls=[]; adapter=GovernedAdapter('local','code_change',lambda p: calls.append(p) or {'actual_cost_usd':0,'result':'ok'},lambda r: r['result']=='ok')
        i=self.store.propose(action())
        with self.assertRaises(ValueError): execute_reviewed(self.store,i,self.store.get(i)['hash'],adapter)
        self.assertEqual(calls,[])
        row=self.store.decide(i,1,'approve','owner'); execute_reviewed(self.store,i,row['hash'],adapter)
        self.assertEqual(len(calls),1); self.assertEqual(self.store.get(i)['status'],'verified')
    def test_failed_adapter_is_not_automatically_retried(self):
        i,h=self.approved()
        def fail(_): raise RuntimeError('uncertain external effect')
        adapter=GovernedAdapter('local','code_change',fail,lambda _:True)
        with self.assertRaises(RuntimeError): execute_reviewed(self.store,i,h,adapter)
        with self.assertRaises(ValueError): execute_reviewed(self.store,i,h,adapter)
        self.assertEqual(self.store.audit()[-1]['kind'],'execution_uncertain')
    def test_long_horizon_checkpoints_failure_recovery_and_rollback(self):
        horizon=LongHorizon(self.store); state=horizon.start(digest('objective'),10,0,time.time()+300,'checkpoint:initial')
        def done(kind, passed):
            i,h=self.approved(kind); self.store.consume(i,h,action_class=kind); self.store.finish(i,passed=passed,evidence_hash=digest(i),actual_cost_usd=0); return i
        bad=done('code_change',False); state=horizon.checkpoint(state['id'],bad,expected_step=0,event='failure'); self.assertEqual(state['status'],'paused')
        good=done('code_change',True)
        with self.assertRaises(ValueError): horizon.checkpoint(state['id'],good,expected_step=1)
        rolled=done('rollback',True); state=horizon.checkpoint(state['id'],rolled,expected_step=1,event='rollback'); self.assertEqual(state['status'],'rolled_back')
        self.assertEqual(state['interventions'],2)
    def test_claim_scope_is_explicit_and_never_automatic(self):
        self.assertFalse(claim_gate('AGI',digest('evidence'),self.store,'unknown'))
        i,h=self.approved('marketing_claim',parameters={'claim_text':'Bounded capability result','evidence_hash':digest('evidence')})
        self.assertTrue(claim_gate('Bounded capability result',digest('evidence'),self.store,i))
        self.assertFalse(claim_gate('AGI',digest('evidence'),self.store,i))


class EvidenceTests(unittest.TestCase):
    def test_complete_synthetic_contract_is_eligible_but_not_claim(self):
        r=assess(bundle()); self.assertTrue(r['eligible'],r['errors']); self.assertEqual(r['status'],'partial')
    def test_missing_malformed_simulated_and_nan_fail_closed(self):
        for mutate in [lambda r:r.update(simulated=True),lambda r:r.pop('suite_hash'),lambda r:r['cases'][0].update(quality=float('nan')),lambda r:r.update(seed=True),lambda r:r.update(cases=[]),lambda r:r['red_team'].update(prompt_injection=False)]:
            r=bundle(); mutate(r); self.assertFalse(assess(r)['eligible'])
        self.assertFalse(assess({})['eligible']); self.assertFalse(assess(None)['eligible'])
    def test_contamination_detects_exact_near_and_family_overlap(self):
        a=[{'id':'test','text':'Explain the result of a small database query','hash':'aaa','family':'sql-join'}]
        for b in [{'id':'train','hash':'aaa'},{'id':'train','family':'sql-join'},{'id':'train','text':'Explain the result of the small database query'}]:
            self.assertFalse(contamination(a,[b])['passed'])
        self.assertTrue(contamination(a,[{'id':'train','text':'Write a short poem','family':'writing'}])['passed'])
    def test_novelty_and_complete_coverage_not_just_seed_change(self):
        for change in ('family','split','repetition'):
            r=bundle()
            for c in r['cases']: c[change] = {'family':'same','split':'candidate','repetition':0}[change]
            self.assertFalse(assess(r)['eligible'])
        r=bundle(); r['cases'].pop(); self.assertFalse(assess(r)['eligible'])
    def test_calibration_abstention_and_help(self):
        r=calibration([{'confidence':1,'correct':False,'abstained':False,'should_abstain':True}]); self.assertEqual(r['brier'],1); self.assertEqual(r['ece'],1); self.assertEqual(r['abstention_error'],1)
        self.assertIsNone(calibration([])['coverage'])
        for v in (-1,2,float('nan')): self.assertTrue(help_required(v,evidence_present=True,supported=True))
        self.assertTrue(help_required(.99,evidence_present=False,supported=True)); self.assertTrue(help_required(.99,evidence_present=True,supported=True,high_impact=True))
    def test_promotion_matches_baselines_and_rejects_any_task_regression(self):
        a=bundle(); b=copy.deepcopy(a); b['id']='challenger'; b['baseline_id']=a['id']; b['baseline_hash']=digest(a)
        self.assertEqual(promotion(a,b)['status'],'human_review_required')
        b['cases'][0]['quality']=0.8; b['cases'][1]['quality']=1.0
        self.assertEqual(promotion(a,b)['status'],'rejected')
        b=copy.deepcopy(a); b['hardware']='different'; self.assertEqual(promotion(a,b)['status'],'rejected')
    def test_artifact_hash_and_path_traversal(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d); (p/'trace').write_text('trace')
            import hashlib
            r={'artifacts':[{'path':'trace','sha256':hashlib.sha256(b'trace').hexdigest()}]}; self.assertTrue(verify_artifacts(r,p))
            r['artifacts'][0]['path']='../outside'; self.assertFalse(verify_artifacts(r,p))
    def test_distillation_never_recycles_holdouts(self):
        for r in (bundle(),{}):
            lesson=distill(r); self.assertFalse(lesson['training_candidate']['eligible']); self.assertEqual(lesson['status'],'lesson_draft_requires_review')
    def test_debate_does_not_change_proprietary_weights(self):
        r=debate_assessment([{'role':role,'model_version':'v1','evidence':['trace'],'independent_first_pass':True,'objections':[]} for role in ('proposer','critic','reviewer')])
        self.assertFalse(r['weights_changed']); self.assertEqual(r['status'],'human_review_required')
    def test_pages_are_real_fail_closed_and_current(self):
        data=build(); self.assertFalse(data['automatic_agi_claim']); self.assertEqual(len(data['matrix']),33)
        self.assertEqual(data['runs'],[]); self.assertTrue(all(c['status']=='untested' for c in data['matrix'])); generate(check=True)


class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.store=ReviewStore(Path(self.tmp.name)/'review.db')
        self.server=ThreadingHTTPServer(('127.0.0.1',0),BuddyLocalHandler)
        self.server.bridge_state=BridgeState(token='test-agent',review_token='test-reviewer',reviewer_id='test-owner',review_store=self.store)
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True); self.thread.start()
        self.base='http://127.0.0.1:'+str(self.server.server_port)
    def tearDown(self): self.server.shutdown(); self.server.server_close(); self.thread.join(); self.tmp.cleanup()
    def request(self,path,token,payload=None,origin=None):
        headers={'Authorization':'Bearer '+token,'Content-Type':'application/json'}
        if origin: headers['Origin']=origin
        req=Request(self.base+'/api/local/evaluation/'+path,data=json.dumps(payload).encode() if payload else None,headers=headers)
        with urlopen(req) as response: return json.load(response)
    def test_agent_cannot_self_approve_or_read_private_queue(self):
        a=self.request('propose','test-agent',{'action':action()})
        for path,payload in [('queue',None),('decide',{'id':a['id'],'revision':1,'decision':'approve'})]:
            with self.assertRaises(HTTPError) as e: self.request(path,'test-agent',payload)
            self.assertEqual(e.exception.code,401)
        self.request('decide','test-reviewer',{'id':a['id'],'revision':1,'decision':'approve'})
        q=self.request('queue','test-reviewer'); self.assertEqual(q['actions'][0]['status'],'approved')
    def test_cross_origin_blocked(self):
        with self.assertRaises(HTTPError) as e: self.request('queue','test-reviewer',origin='https://evil.example')
        self.assertEqual(e.exception.code,403)
    def test_absent_backend_fails_closed(self):
        self.server.bridge_state.review_store=None
        with self.assertRaises(HTTPError) as e: self.request('queue','test-reviewer')
        self.assertEqual(e.exception.code,503)


class RunnerTests(unittest.TestCase):
    setUp = ReviewTests.setUp
    tearDown = ReviewTests.tearDown
    approved = ReviewTests.approved
    def test_runner_enforces_manifest_scope_budget_and_keeps_failures(self):
        from buddy_os.evaluation.runner import SubjectAdapter, run_suite
        from datetime import datetime, timezone
        fixtures={f'task-{i}':{'text':f'Privately held variant {i}', 'family':f'family-{i}'} for i in range(3)}
        suite={'id':'private-suite','version':'1','seed':31,'reviewer':'owner','registered_at':'2026-01-01T00:00:00Z','capability':'reasoning','repetitions':3,
               'grader_version':'test-grader','license_review':{'allowed':True,'source':'owned','reviewer':'owner'},
               'cases':[{'id':i,'fixture_hash':digest(f),'family':f['family'],'split':'transfer' if i=='task-2' else 'holdout','cross_domain':i=='task-2'} for i,f in fixtures.items()]}
        calls=[]
        def respond(f,**options): calls.append(options); return {'output':'test response','cost_usd':0}
        adapter=SubjectAdapter('test-fixture','v1',respond)
        components={'model':'fixture','policy':'p1','router':'r1','retrieval':'d1'}
        scope={'suite_hash':digest(suite),'subject':'test-fixture','subject_version':'v1','components':components,'network':False,'paid':False,'max_seconds':300,'max_budget_usd':0}
        i,h=self.approved('sandbox',parameters=scope)
        run=run_suite(suite=suite,fixtures=fixtures,training=[],adapter=adapter,grader=lambda f,o:{'quality':1,'safety':1,'factuality':1},store=self.store,action_id=i,action_hash=h,components=components,baseline={'id':'baseline'},hardware='test',runtime='test',output_dir=Path(self.tmp.name)/'evidence')
        self.assertEqual(len(calls),9); self.assertEqual(len(run['cases']),9); self.assertTrue(verify_artifacts(run,Path(self.tmp.name)/'evidence'))
        self.assertFalse(assess(run)['eligible']) # no fabricated red-team or calibration results
        with self.assertRaises(ValueError): run_suite(suite=suite,fixtures=fixtures,training=[],adapter=adapter,grader=lambda f,o:{},store=self.store,action_id=i,action_hash=h,components=components,baseline={'id':'baseline'},hardware='test',runtime='test',output_dir=Path(self.tmp.name)/'evidence')
    def test_component_registry_rejects_unverified_candidates(self):
        registry=ComponentRegistry(self.store); a=bundle(); b=bundle(); b['id']='challenger'
        i,h=self.approved('model_promotion')
        with self.assertRaises(ValueError): registry.transition(i,h,expected_current=None,components=b['components'],champion=a,challenger=b,evidence_root=Path(self.tmp.name),suites={'registered_suites':[]})
    def test_component_promotion_and_rollback_preserve_prior_revisions(self):
        from tools.general_intelligence import registered
        import hashlib
        a=bundle(); b=copy.deepcopy(a)
        suite={'id':'test-suite','version':'1','reviewer':'owner','registered_at':'2025-01-01T00:00:00Z',
               'cases':[{k:c[k] for k in ('id','fixture_hash','family','split')} for c in a['cases'] if c['repetition']==0]}
        a['suite_hash']=digest(suite); b['suite_hash']=digest(suite)
        trace=Path(self.tmp.name)/'trace.json'; trace.write_text('verified test fixture')
        artifact={'path':'trace.json','sha256':hashlib.sha256(trace.read_bytes()).hexdigest()}
        a['artifacts']=[artifact]; b['artifacts']=[artifact]
        b['id']='candidate'; b['components']['model']='candidate-v2'; b['baseline_id']=a['id']; b['baseline_hash']=digest(a)
        report=promotion(a,b); self.assertEqual(report['status'],'human_review_required')
        registry=ComponentRegistry(self.store)
        params={'expected_current':None,'components':b['components'],'assessment_hash':digest(report)}
        i,h=self.approved('model_promotion',parameters=params)
        registry.transition(i,h,expected_current=None,components=b['components'],champion=a,challenger=b,evidence_root=Path(self.tmp.name),suites={'registered_suites':[suite]})
        params={'expected_current':b['components'],'components':a['components'],'assessment_hash':digest(report)}
        i,h=self.approved('rollback',parameters=params)
        restored=registry.transition(i,h,expected_current=b['components'],components=a['components'],champion=a,challenger=b,evidence_root=Path(self.tmp.name),suites={'registered_suites':[suite]},rollback=True)
        self.assertEqual(restored,a['components']); self.assertEqual(self.store.get(i)['status'],'verified')

    def test_horizon_preflight_enforces_deadlines(self):
        horizon=LongHorizon(self.store); state=horizon.start(digest('goal'),1,0,time.time()+100,'checkpoint:zero')
        with self.assertRaises(ValueError): horizon.preflight(state['id'],additional_cost_usd=1)
        self.assertEqual(horizon.preflight(state['id'])['status'],'running')
    def test_horizon_stops_execution_before_step_budget_is_exceeded(self):
        horizon=LongHorizon(self.store); state=horizon.start(digest('goal'),1,0,time.time()+60,'checkpoint:zero')
        calls=[]; adapter=GovernedAdapter('fixture','sandbox',lambda p:calls.append(p) or {'actual_cost_usd':0},lambda r:True)
        i,h=self.approved('sandbox'); horizon.execute_step(state['id'],i,h,adapter)
        j,k=self.approved('sandbox')
        with self.assertRaises(ValueError): horizon.execute_step(state['id'],j,k,adapter)
        self.assertEqual(len(calls),1); self.assertEqual(self.store.get(j)['status'],'approved')

    def test_existing_scheduler_adapter_requires_fresh_bound_approval(self):
        from dreamco_platform.automation.task_runner import BuddyTaskRunner
        runner=BuddyTaskRunner(); i,h=self.approved('sandbox')
        task=runner.schedule(owner_user_id='owner',bot_slug='buddy',objective='Run a bounded evaluation',approval_id=i)
        adapter=EvaluationTaskAdapter(self.store,GovernedAdapter('fixture','sandbox',lambda p:{'actual_cost_usd':0},lambda r:True),{task.task_id:{'action_id':i,'hash':h,'budget_usd':0}})
        results=runner.run_due(adapter,now=time.time()+1)
        self.assertEqual(results[0]['status'],'completed'); self.assertEqual(self.store.get(i)['status'],'verified')

if __name__ == "__main__": unittest.main()
