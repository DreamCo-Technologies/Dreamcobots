import unittest

from scripts.dreamco_pr_and_issue_auditor import audit


class AuditorTests(unittest.TestCase):
    def test_added_secret_blocks(self):
        credential = "ghp_" + "abcdefghijklmnopqrstuvwxyz1234567890"
        patch = (
            "diff --git a/app.py b/app.py\n"
            "new file mode 100644\n"
            "--- /dev/null\n"
            "+++ b/app.py\n"
            "@@ -0,0 +1 @@\n"
            f"+token = '{credential}'\n"
        )
        self.assertEqual(audit(patch)["review_status"], "CHANGES_REQUESTED")

    def test_added_source_line_starting_with_plus_plus_is_scanned(self):
        credential = "ghp_" + "abcdefghijklmnopqrstuvwxyz1234567890"
        patch = (
            "diff --git a/app.py b/app.py\n"
            "new file mode 100644\n"
            "--- /dev/null\n"
            "+++ b/app.py\n"
            "@@ -0,0 +1 @@\n"
            f"+++ token = '{credential}'\n"
        )
        self.assertTrue(any(x["code"] == "GITHUB_TOKEN" for x in audit(patch)["gate_findings"]))

    def test_quarantine_and_conflict_are_reported(self):
        patch = (
            "diff --git a/resource_staging/a.jsonl b/resource_staging/a.jsonl\n"
            "new file mode 100644\n"
            "--- /dev/null\n"
            "+++ b/resource_staging/a.jsonl\n"
            "@@ -0,0 +1 @@\n"
            "+<<<<<<< HEAD\n"
        )
        report = audit(patch)
        self.assertTrue(any(x["code"] == "QUARANTINE_COMMIT" for x in report["gate_findings"]))
        self.assertEqual(report["mr_issues_queue"][0]["issue_type"], "MERGE_CONFLICT_MARKER")

    def test_empty_or_binary_quarantine_addition_blocks(self):
        patch = (
            "diff --git a/resource_staging/empty.jsonl b/resource_staging/empty.jsonl\n"
            "new file mode 100644\n"
            "--- /dev/null\n"
            "+++ b/resource_staging/empty.jsonl\n"
        )
        self.assertTrue(any(x["code"] == "QUARANTINE_COMMIT" for x in audit(patch)["gate_findings"]))

    def test_deleted_quarantine_file_is_not_reported_as_a_commit(self):
        patch = (
            "diff --git a/resource_staging/old.jsonl b/resource_staging/old.jsonl\n"
            "deleted file mode 100644\n"
            "--- a/resource_staging/old.jsonl\n"
            "+++ /dev/null\n"
        )
        self.assertFalse(any(x["code"] == "QUARANTINE_COMMIT" for x in audit(patch)["gate_findings"]))

    def test_checkpoint_requires_evidence(self):
        patch = (
            "diff --git a/checkpoints/buddy-sec/model.safetensors b/checkpoints/buddy-sec/model.safetensors\n"
            "new file mode 100644\n"
            "--- /dev/null\n"
            "+++ b/checkpoints/buddy-sec/model.safetensors\n"
        )
        self.assertTrue(any(x["code"] == "CHECKPOINT_WITHOUT_EVIDENCE" for x in audit(patch)["gate_findings"]))

    def test_deleted_evidence_does_not_satisfy_checkpoint_gate(self):
        patch = (
            "diff --git a/checkpoints/buddy-sec/model.safetensors b/checkpoints/buddy-sec/model.safetensors\n"
            "new file mode 100644\n"
            "--- /dev/null\n"
            "+++ b/checkpoints/buddy-sec/model.safetensors\n"
            "diff --git a/checkpoints/buddy-sec/evidence_stamp.json b/checkpoints/buddy-sec/evidence_stamp.json\n"
            "deleted file mode 100644\n"
            "--- a/checkpoints/buddy-sec/evidence_stamp.json\n"
            "+++ /dev/null\n"
        )
        self.assertTrue(any(x["code"] == "CHECKPOINT_WITHOUT_EVIDENCE" for x in audit(patch)["gate_findings"]))

    def test_unrelated_evidence_does_not_satisfy_checkpoint_gate(self):
        patch = (
            "diff --git a/checkpoints/buddy-sec/model.safetensors b/checkpoints/buddy-sec/model.safetensors\n"
            "new file mode 100644\n"
            "--- /dev/null\n"
            "+++ b/checkpoints/buddy-sec/model.safetensors\n"
            "diff --git a/docs/evidence_stamp.json b/docs/evidence_stamp.json\n"
            "new file mode 100644\n"
            "--- /dev/null\n"
            "+++ b/docs/evidence_stamp.json\n"
            "@@ -0,0 +1 @@\n"
            '+{"checkpoint_path":"checkpoints/buddy-sec/model.safetensors","sha256":"' + "a" * 64 + '"}\n'
        )
        self.assertTrue(any(x["code"] == "CHECKPOINT_WITHOUT_EVIDENCE" for x in audit(patch)["gate_findings"]))

    def test_checkpoint_evidence_must_bind_exact_path_and_sha256(self):
        patch = (
            "diff --git a/checkpoints/buddy-sec/model.safetensors b/checkpoints/buddy-sec/model.safetensors\n"
            "new file mode 100644\n"
            "--- /dev/null\n"
            "+++ b/checkpoints/buddy-sec/model.safetensors\n"
            "diff --git a/checkpoints/buddy-sec/evidence_stamp.json b/checkpoints/buddy-sec/evidence_stamp.json\n"
            "new file mode 100644\n"
            "--- /dev/null\n"
            "+++ b/checkpoints/buddy-sec/evidence_stamp.json\n"
            "@@ -0,0 +1 @@\n"
            '+{"checkpoint_path":"checkpoints/buddy-sec/model.safetensors","sha256":"' + "a" * 64 + '"}\n'
        )
        self.assertFalse(any(
            x["code"] in {"CHECKPOINT_WITHOUT_EVIDENCE", "CHECKPOINT_EVIDENCE_NOT_BOUND"}
            for x in audit(patch)["gate_findings"]
        ))

    def test_moving_revision_blocks(self):
        patch = (
            'diff --git a/config/competitor_registry.json b/config/competitor_registry.json\n'
            '+++ b/config/competitor_registry.json\n'
            '@@ -1 +1 @@\n'
            '+{"pinned_revision":"main"}\n'
        )
        self.assertTrue(any(x["code"] == "UNPINNED_COMPETITOR_REVISION" for x in audit(patch)["gate_findings"]))

    def test_absolute_superiority_claim_is_flagged(self):
        claim = "un" + "beatable"
        patch = (
            "diff --git a/docs/claim.md b/docs/claim.md\n"
            "@@ -0,0 +1 @@\n"
            f"+This result is {claim}.\n"
        )
        self.assertTrue(any(
            item["code"] == "ABSOLUTE_SUPERIORITY"
            for item in audit(patch)["gate_findings"]
        ))

    def test_clean_patch_is_not_auto_approved(self):
        self.assertEqual(audit("diff --git a/README.md b/README.md\n")["review_status"], "REVIEW_REQUIRED")


if __name__ == "__main__":
    unittest.main()
