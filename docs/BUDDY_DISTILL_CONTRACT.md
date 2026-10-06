# Buddy distill evidence contract (draft)

Status: `contract_draft_no_runs`. No distill runs, no trained weights, no allowlisted adapters exist yet.

| File | Purpose | Rule |
|---|---|---|
| `config/buddy-distill-contract.json` | Teacher (Grok, xAI API) and student (LoRA/QLoRA on a pinned base) spec, thresholds copied from `buddy-open-model-coding-lab.json`, CI policy, truth block | all three |
| `schemas/buddy-distill-evidence.schema.json` | Shape of one evidence packet in `evidence/distill/` | evidence before allowlist |
| `tools/check_buddy_distill_gate.py` | Stdlib gate. Fails if a run trained before its baseline, a weight file is in the tree, or any adapter claims the allowlist without a passing packet | all three |
| `tests/test_check_buddy_distill_gate.py` | 10 unit tests, synthetic fixtures only | all three |
| `.github/workflows/buddy-distill-gate.yml` | Read-only CI job, no installs, downloads, secrets, or training | no weights in default CI |

Open item before any real run: record a `teacher_terms_check` confirming the xAI terms permit training a student on the teacher's outputs for this use. The gate refuses allowlisting until that is `permitted: true`.
