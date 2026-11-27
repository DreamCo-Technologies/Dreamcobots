# Verified 45M checkpoint and competitor evidence contract

Every canonical MasterBot division uses `checkpoints/buddy-<div_key>-45m/` and must provide three non-empty artifacts:

- `model.safetensors`: parseable safetensors with complete, non-overlapping tensor byte ranges and exactly 45,038,208 parameters.
- `tokenizer.json`: parseable tokenizer object with a populated model vocabulary.
- `evidence_stamp.json`: at least 100 completed steps, a run ID, dataset-manifest and training-config hashes, exact checkpoint/tokenizer hashes, and finite loss observations whose final value is below the initial value.

Run `python tools/verify_45m_checkpoints.py`. Missing, malformed, mismatched, non-convergent, or incomplete artifacts are BLOCKED. The audit does not create checkpoints, train weights, download competitors, or certify production readiness. A self-authored evidence stamp is structural evidence only and still requires independent audit of the run record and provenance.

External competitor candidates belong in `baselines/competitor_registry.json`. The registry starts empty intentionally. Admission requires an immutable 40-character revision, local checkpoint and tokenizer artifacts with SHA-256 hashes, license-review evidence, and explicit benchmark-permission evidence. Public availability alone is not permission. No baseline is silently substituted.
