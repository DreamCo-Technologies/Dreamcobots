# Model Foundry: configurable 25M architecture integration

The Model Foundry can now accept an explicit decoder architecture profile instead of silently using only the small default baseline.

The profile controls vocabulary size, context length, hidden width, layer count, attention heads, feed-forward width, tied embeddings and bias behavior. Before model construction, the trainer computes an expected parameter count. After construction, it counts the instantiated parameters and stops if the two values differ.

For a target-bearing profile, the trainer also checks the configured parameter target and tolerance. Checkpoint resume requires the same architecture profile as the original run.

## Authorization gate

A supplied architecture profile must contain a `training_policy` with both `enabled: true` and `weight_updates_authorized: true`. The 25M profile is intentionally disabled by default. A user must separately authorize actual weight updates and use a rights-cleared local dataset before changing that policy.

This integration does not start training, approve paid compute, download external material, or convert the 25M course target into a claim that a trained model exists.
