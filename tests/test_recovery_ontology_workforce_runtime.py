import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class RecoveryOntologyWorkforceRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.recovery=json.loads((ROOT/'config/legacy-bot-recovery-program.json').read_text())
        cls.ontology=json.loads((ROOT/'config/dreamco-operational-ontology.json').read_text())
        cls.work=json.loads((ROOT/'config/universal-work-ai-bot-factory.json').read_text())
        cls.runtime=json.loads((ROOT/'config/buddy-runtime-supervisor.json').read_text())
        cls.runall=json.loads((ROOT/'config/run-everything-now.json').read_text())
        cls.manufacturing=json.loads((ROOT/'config/universal-business-manufacturing-productivity-program.json').read_text())
        cls.live=json.loads((ROOT/'config/live-user-testing-readiness.json').read_text())
        cls.sandbox_evidence=json.loads((ROOT/'config/sandbox-runtime-evidence.json').read_text())
        cls.work_platforms=json.loads((ROOT/'config/work-platform-benchmark-registry.json').read_text())

    def test_legacy_sources_merge_through_one_governed_pipeline(self):
        self.assertEqual(set(self.recovery['source_roots']),{'App_bots','original-bots','bots','attached_assets'})
        self.assertEqual(self.recovery['canonical_root'],'App_bots')
        text=' '.join(self.recovery['recovery_pipeline']).lower()
        for phrase in ['enumerate every file','dedup','unique bot candidates','universal sandbox','runtime route']:
            self.assertIn(phrase,text)
        gate=' '.join(self.recovery['promotion_gate']).lower()
        for phrase in ['unique identity','runtime implementation','sandbox curriculum','fleet e2e','code trust']:
            self.assertIn(phrase,gate)

    def test_ontology_models_objects_links_actions_functions_and_evidence(self):
        self.assertGreaterEqual(len(self.ontology['object_types']),50)
        self.assertGreaterEqual(len(self.ontology['link_types']),40)
        self.assertGreaterEqual(len(self.ontology['action_types']),20)
        self.assertGreaterEqual(len(self.ontology['functions']),15)
        for item in {'Bot','HumanTask','Occupation','SandboxTest','Evidence','Gap','Business','Deployment','Connection','Payment','Manufacturer'}:
            self.assertIn(item,self.ontology['object_types'])
        self.assertTrue(self.ontology['self_modeling']['enabled'])
        self.assertTrue(self.ontology['governance']['lineage_required'])
        self.assertTrue(self.ontology['governance']['generated_objects_not_runtime_verified_by_default'])

    def test_work_factory_covers_jobs_tasks_platforms_money_and_guardrails(self):
        self.assertGreaterEqual(len(self.work['task_dimensions']),20)
        self.assertGreaterEqual(len(self.work['opportunity_platform_classes']),10)
        self.assertGreaterEqual(len(self.work['benchmark_dimensions']),10)
        self.assertTrue(self.work['money_experiment']['required'])
        self.assertTrue(self.work['money_experiment']['never_guarantee_income'])
        self.assertIn('O*NET occupation/task datasets',self.work['authoritative_job_sources'])
        self.assertGreaterEqual(len(self.work_platforms['platforms']),10)
        self.assertIn('must not invent prices',self.work_platforms['truth_rule'].lower())

    def test_runtime_is_durable_synchronized_and_fail_safe(self):
        c=self.runtime['coordination']
        for key in ['heartbeat_seconds','lease_seconds','checkpoint_after_step','idempotency_key_required','dead_letter_queue','crash_restart','exponential_backoff','circuit_breaker_for_external_dependencies']:
            self.assertIn(key,c)
        self.assertTrue(c['ontology_is_shared_state_model'])
        self.assertGreaterEqual(c['maximum_parallel_lanes'],20)
        self.assertIn('live money movement',self.runtime['approval_gated'])
        self.assertIn('infinite compute',self.runtime['truth_rule'].lower())

    def test_run_everything_is_maximum_and_truthful(self):
        self.assertGreaterEqual(len(self.runall['maximum_steps']),15)
        self.assertTrue(self.runall['error_policy']['continue_after_independent_failure'])
        self.assertTrue(self.runall['error_policy']['never_hide_failure'])
        self.assertTrue(self.runall['always_on_model']['restart_after_crash'])
        self.assertTrue(self.runall['always_on_model']['checkpoint_resume'])
        self.assertIn('does not make failing or untested systems pass',self.runall['truth_rule'])

    def test_sandbox_planning_is_never_runtime_proof(self):
        self.assertEqual(self.sandbox_evidence['evidence'],[])
        self.assertIn('planned sandbox case is not a passed case',self.sandbox_evidence['truth_rule'].lower())
        self.assertIn('never hand-edit',self.sandbox_evidence['truth_rule'].lower())

    def test_live_user_testing_stays_controlled_and_reversible(self):
        gates=' '.join(self.live['required_gates']).lower()
        for phrase in ['core operational certification','zero release blockers','sandbox runtime evidence','rollback','privacy','approval gated','pilot scope']:
            self.assertIn(phrase,gates)
        self.assertEqual(self.live['rollout_stages'][0]['id'],'internal_only')
        self.assertEqual(self.live['rollout_stages'][1]['id'],'owner_pilot')
        self.assertIn('critical security/privacy finding',self.live['automatic_pause_conditions'])

    def test_manufacturing_productivity_is_measured_not_claimed(self):
        self.assertGreaterEqual(len(self.manufacturing['manufacturing_domains']),30)
        self.assertGreaterEqual(len(self.manufacturing['productivity_metrics']),20)
        self.assertGreaterEqual(len(self.manufacturing['factory_worker_types']),12)
        self.assertIn('before/after evidence',self.manufacturing['truth_rule'])
        self.assertIn('lockout/tagout',self.manufacturing['safety_rule'])

if __name__=='__main__': unittest.main()
