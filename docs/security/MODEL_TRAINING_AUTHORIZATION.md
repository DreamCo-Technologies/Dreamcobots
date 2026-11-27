# Model training authorization and execution boundary

Model architecture files are specifications, not permission to update weights. Every training run requires all of the following:

1. A versioned architecture profile with `training_policy.enabled=true` and `weight_updates_authorized=true`.
2. The profile must require a rights-cleared local dataset and keep external data and paid compute disabled.
3. The profile must record `approved_by`, an `authorization_reference`, and an `approved_at` timestamp.
4. The operator must pass `--authorize-weight-updates`, `--approved-by`, and the matching `--authorization-reference` at execution time.
5. The dataset must be in the owner-controlled private data root and pass the manifest's owner, license, permission, path, scope and SHA-256 checks.
6. Checkpoints and resume files must also stay inside the private data root.

The command requires an explicit architecture profile. The small CPU profile and 25M profile both ship disabled. The 25M profile is not enabled by course completion or by merging this code.

## Example after separate approval

Only after the dataset and profile have been reviewed and the profile's disabled policy has been deliberately updated with the approved owner, reference and timestamp:

```bash
python tools/train_buddy_division_model.py \
  --division-id 1 \
  --dataset-id approved-dataset-id \
  --dataset-path "$HOME/DreamCo-private-data/approved-dataset.txt" \
  --strategy domain_adaptive_pretraining \
  --seed 20261125 \
  --architecture-profile config/buddy-25m-cpu-architecture-profile.json \
  --authorize-weight-updates \
  --approved-by "Approved owner" \
  --authorization-reference "approved-change-reference" \
  --output "$HOME/DreamCo-private-data/checkpoints/buddy-division-01.pt"
```

The example is documentation only; this PR does not run it. The current authorized dataset manifest is empty, so no dataset is currently eligible. A profile, queue entry, or successful test is not a trained model or a mastery/certification result.
