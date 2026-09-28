"""Acceptance tests for config/universal-business-manufacturing-productivity-program.json.

Plan: plan-business-productivity-programs (top-3 program #1).
Everything here is sandbox acceptance evidence, not production evidence:
the benchmark builder is executed inside a temporary directory copy of the
repo layout so the real config/generated/ tree is never written.
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG_REL = Path("config") / "universal-business-manufacturing-productivity-program.json"
CONFIG = ROOT / CONFIG_REL
TOOL_REL = Path("tools") / "build_manufacturing_productivity_benchmarks.py"
TOOL = ROOT / TOOL_REL
OUTPUT_REL = Path("config") / "generated" / "manufacturing-productivity-benchmarks.json"

EXPECTED_SCHEMA = "dreamco.universal_business_manufacturing_productivity.v1"
LIST_FIELDS = (
    "business_types",
    "manufacturing_domains",
    "productivity_metrics",
    "task_model",
    "improvement_methods",
    "factory_worker_types",
    "integration_targets",
)
REQUIRED_TASK_MODEL_FIELDS = (
    "trigger", "inputs", "worker_role", "tools", "steps", "decision_points",
    "outputs", "handoffs", "quality_checks", "safety_constraints",
    "time_baseline", "cost_baseline", "error_baseline", "automation_fit",
    "assist_fit", "benchmark", "evidence",
)
BASELINE_FIELDS = ("time_baseline", "cost_baseline", "error_baseline")
CLAIM_WORDS = re.compile(r"\b(sav(?:e|es|ed|ing|ings)|roi|uptime gain|quality gain)\b", re.IGNORECASE)
SANDBOX_LABEL = "sandbox_simulated_not_production_evidence"


def validate_task(task, cfg):
    """Validate a task expressed in the config's task_model shape.

    Returns a list of human-readable errors (empty list == valid).
    """
    errors = []
    missing = [f for f in cfg["task_model"] if f not in task]
    if missing:
        errors.append(f"missing task_model fields: {missing}")
    if task.get("worker_role") not in cfg["factory_worker_types"]:
        errors.append(f"unknown worker_role: {task.get('worker_role')!r}")
    bench = task.get("benchmark", {})
    for metric in bench.get("metrics", []):
        if metric not in cfg["productivity_metrics"]:
            errors.append(f"unknown productivity metric: {metric!r}")
    for target in task.get("tools", []):
        if target not in cfg["integration_targets"]:
            errors.append(f"unknown integration target: {target!r}")
    for field in BASELINE_FIELDS:
        baseline = task.get(field)
        if not isinstance(baseline, dict) or "measured" not in baseline:
            errors.append(f"{field} must be a dict with a 'measured' flag")
    evidence = task.get("evidence", {})
    if evidence.get("label") != SANDBOX_LABEL and evidence.get("production_evidence") is not False:
        errors.append("evidence must be labelled sandbox/simulated or be real production evidence")
    # Truth rule: an improvement claim needs measured before AND after.
    claim = evidence.get("improvement_claim")
    if claim:
        before = evidence.get("before_measurement") or {}
        after = evidence.get("after_measurement") or {}
        if not (before.get("measured") and after.get("measured")):
            errors.append("improvement claim without measured before/after evidence (truth_rule)")
    # Safety rule: no step may bypass safety systems / LOTO / regulated signoff.
    forbidden = ("bypass", "override interlock", "skip lockout", "skip loto", "skip signoff", "disable guard")
    for step in task.get("steps", []):
        if any(word in step.lower() for word in forbidden):
            errors.append(f"step violates safety_rule: {step!r}")
    if "lockout/tagout" not in " ".join(task.get("safety_constraints", [])).lower():
        errors.append("safety_constraints must reference lockout/tagout")
    return errors


def sample_downtime_rca_task():
    """One sample task (downtime root-cause analysis) in task_model shape. Simulated data only."""
    return {
        "trigger": "unplanned stop on line 3 longer than 15 minutes (simulated event)",
        "inputs": ["CMMS work orders (synthetic)", "MES downtime log (synthetic)", "operator shift notes (synthetic)"],
        "worker_role": "downtime root-cause analyst",
        "tools": ["CMMS", "MES", "spreadsheets"],
        "steps": [
            "collect downtime events for the sample period",
            "pareto the stop reasons",
            "run 5-whys on the top stop reason",
            "draft corrective-action recommendation for human review",
        ],
        "decision_points": ["is the top reason mechanical, material, or process?", "does the fix touch a guarded machine (escalate to human)?"],
        "outputs": ["pareto chart", "root-cause hypothesis", "corrective-action draft"],
        "handoffs": ["maintenance analyst", "human maintenance supervisor for signoff"],
        "quality_checks": ["events reconcile with MES totals", "hypothesis cites source events"],
        "safety_constraints": [
            "analysis only; never bypass machine safety systems",
            "any physical work follows lockout/tagout and is performed by qualified humans",
            "regulated signoff stays with humans",
        ],
        "time_baseline": {"measured": False, "value": None, "unit": "minutes_per_analysis", "note": "no real measurement taken"},
        "cost_baseline": {"measured": False, "value": None, "unit": "usd_per_analysis", "note": "no real measurement taken"},
        "error_baseline": {"measured": False, "value": None, "unit": "misattributed_root_causes_pct", "note": "no real measurement taken"},
        "automation_fit": "medium: event aggregation and pareto are automatable",
        "assist_fit": "high: hypothesis drafting assists the human analyst",
        "benchmark": {"scenario": "root_cause_analysis", "metrics": ["downtime", "scrap_rate", "rework_rate", "first_pass_yield"]},
        "evidence": {
            "label": SANDBOX_LABEL,
            "production_evidence": False,
            "data_source": "synthetic fixture inside test",
            "improvement_claim": None,
            "before_measurement": None,
            "after_measurement": None,
        },
    }


class BusinessManufacturingProductivityProgramTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cfg = json.loads(CONFIG.read_text(encoding="utf-8"))

    # --- schema / structure -------------------------------------------------
    def test_schema_and_version_present(self):
        self.assertEqual(self.cfg["schema"], EXPECTED_SCHEMA)
        self.assertRegex(self.cfg["version"], r"^\d+\.\d+\.\d+$")

    def test_list_fields_non_empty_and_unique(self):
        for field in LIST_FIELDS:
            with self.subTest(field=field):
                values = self.cfg[field]
                self.assertIsInstance(values, list)
                self.assertTrue(values, f"{field} is empty")
                self.assertTrue(all(isinstance(v, str) and v.strip() for v in values), f"{field} has blank/non-string entries")
                dupes = sorted({v for v in values if values.count(v) > 1})
                self.assertEqual(dupes, [], f"{field} has duplicates")

    def test_task_model_has_required_fields(self):
        missing = [f for f in REQUIRED_TASK_MODEL_FIELDS if f not in self.cfg["task_model"]]
        self.assertEqual(missing, [])

    # --- rules ----------------------------------------------------------------
    def test_safety_rule_forbids_bypassing_safety_loto_and_signoff(self):
        rule = self.cfg["safety_rule"].lower()
        self.assertIn("must not", rule)
        for phrase in ("bypass", "machine safety systems", "lockout/tagout", "regulated signoff", "human-required safety decisions"):
            self.assertIn(phrase, rule)

    def test_truth_rule_requires_measured_before_after_evidence(self):
        rule = self.cfg["truth_rule"].lower()
        self.assertIn("measured before/after evidence", rule)
        self.assertIn("must not claim", rule)
        for claim in ("savings", "roi"):
            self.assertIn(claim, rule)

    # --- benchmark builder, run in a sandbox ------------------------------
    @unittest.skipUnless(TOOL.exists(), "benchmark builder tool not present")
    def test_benchmark_builder_runs_in_sandbox_and_does_not_claim_savings(self):
        with tempfile.TemporaryDirectory(prefix="mfg-bench-sandbox-") as tmp:
            sandbox = Path(tmp)
            (sandbox / TOOL_REL).parent.mkdir(parents=True)
            (sandbox / CONFIG_REL).parent.mkdir(parents=True)
            shutil.copy2(TOOL, sandbox / TOOL_REL)
            shutil.copy2(CONFIG, sandbox / CONFIG_REL)
            real_output = ROOT / OUTPUT_REL
            real_mtime = real_output.stat().st_mtime_ns if real_output.exists() else None

            proc = subprocess.run([sys.executable, str(sandbox / TOOL_REL)], cwd=sandbox, capture_output=True, text=True, timeout=60)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            summary = json.loads(proc.stdout)
            self.assertTrue(summary["ok"])

            out = json.loads((sandbox / OUTPUT_REL).read_text(encoding="utf-8"))
            # Sandbox isolation: the real repo output was not created or touched.
            self.assertEqual(real_output.stat().st_mtime_ns if real_output.exists() else None, real_mtime)

        self.assertEqual(out["schema"], "dreamco.manufacturing_productivity_benchmarks.v1")
        self.assertEqual(out["benchmark_case_count"], len(out["cases"]))
        self.assertGreater(len(out["cases"]), 0)
        self.assertEqual(out["truth_boundary"], self.cfg["truth_rule"])
        metrics = set(self.cfg["productivity_metrics"])
        for case in out["cases"]:
            with self.subTest(scenario=case["scenario"], metric=case["metric"]):
                self.assertIn(case["metric"], metrics)
                self.assertTrue(case["baseline_required"])
                self.assertTrue(case["post_change_measurement_required"])
                for item in ("baseline sample", "post-change sample", "sample period", "data source"):
                    self.assertIn(item, case["minimum_evidence"])
                self.assertEqual(case["claim_status"], "no_improvement_claim_until_measured")
                self.assertIn("safety boundary", case["sandbox_tests"])
                # No record may carry a savings/ROI value or claim.
                for key, value in case.items():
                    self.assertIsNone(CLAIM_WORDS.search(key), f"claim-like key {key!r}")
                    if isinstance(value, str) and key != "claim_status":
                        self.assertIsNone(CLAIM_WORDS.search(value), f"claim-like value in {key}: {value!r}")

    # --- sandbox workflow check ----------------------------------------------
    def test_sample_downtime_rca_task_validates_and_is_labelled_sandbox(self):
        task = sample_downtime_rca_task()
        self.assertEqual(validate_task(task, self.cfg), [])
        self.assertEqual(task["evidence"]["label"], SANDBOX_LABEL)
        self.assertFalse(task["evidence"]["production_evidence"])
        for field in BASELINE_FIELDS:
            self.assertFalse(task[field]["measured"], "sample baselines are simulated, not measured")
        self.assertIn("downtime root-cause analyst", self.cfg["factory_worker_types"])
        self.assertIn("root cause analysis", self.cfg["manufacturing_domains"])

    def test_validator_rejects_unmeasured_savings_claim(self):
        task = sample_downtime_rca_task()
        task["evidence"]["improvement_claim"] = "30% downtime reduction, $50k savings"
        errors = validate_task(task, self.cfg)
        self.assertTrue(any("truth_rule" in e for e in errors), errors)

    def test_validator_rejects_safety_bypass_step(self):
        task = sample_downtime_rca_task()
        task["steps"].append("bypass the light curtain to restart faster")
        errors = validate_task(task, self.cfg)
        self.assertTrue(any("safety_rule" in e for e in errors), errors)

    def test_validator_rejects_missing_task_model_field(self):
        task = sample_downtime_rca_task()
        del task["handoffs"]
        errors = validate_task(task, self.cfg)
        self.assertTrue(any("handoffs" in e for e in errors), errors)


if __name__ == "__main__":
    unittest.main()
