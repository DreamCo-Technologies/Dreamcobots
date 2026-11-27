import unittest
from scripts.dreamco_pr_and_issue_auditor import audit

class AuditorTests(unittest.TestCase):
 def test_added_secret_blocks(self):
  # Assemble the fake credential at runtime so the repository-wide secret scan
  # does not mistake this intentional negative-test fixture for a real secret.
  credential = "ghp_" + "abcdefghijklmnopqrstuvwxyz1234567890"
  p=(
   "diff --git a/app.py b/app.py\n+++ b/app.py\n@@ -0,0 +1 @@\n"
   f"+token = '{credential}'\n"
  )
  self.assertEqual(audit(p)["review_status"],"CHANGES_REQUESTED")
 def test_quarantine_and_conflict_are_reported(self):
  p="diff --git a/resource_staging/a.jsonl b/resource_staging/a.jsonl\n+++ b/resource_staging/a.jsonl\n@@ -0,0 +1 @@\n+<<<<<<< HEAD\n"
  r=audit(p)
  self.assertTrue(any(x["code"]=="QUARANTINE_COMMIT" for x in r["gate_findings"]))
  self.assertEqual(r["mr_issues_queue"][0]["issue_type"],"MERGE_CONFLICT_MARKER")
 def test_checkpoint_requires_evidence(self):
  r=audit("diff --git a/checkpoints/buddy-sec/model.safetensors b/checkpoints/buddy-sec/model.safetensors\n")
  self.assertTrue(any(x["code"]=="CHECKPOINT_WITHOUT_EVIDENCE" for x in r["gate_findings"]))
 def test_moving_revision_blocks(self):
  p='diff --git a/config/competitor_registry.json b/config/competitor_registry.json\n+++ b/config/competitor_registry.json\n@@ -1 +1 @@\n+{"pinned_revision":"main"}\n'
  self.assertTrue(any(x["code"]=="UNPINNED_COMPETITOR_REVISION" for x in audit(p)["gate_findings"]))
 def test_clean_patch_is_not_auto_approved(self):
  self.assertEqual(audit("diff --git a/README.md b/README.md\n")["review_status"],"REVIEW_REQUIRED")
