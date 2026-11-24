# DreamCo division domain mapping owner review

The resource readiness map currently carries unresolved MasterBot-to-domain decisions and unassigned domain profiles. This queue makes those items reviewable without guessing.

## Queue behavior

- Read the generated resource readiness map's `owner_review` section.
- Preserve each pending MasterBot ID, candidate domain IDs, resource bundle and evidence references.
- Preserve each unassigned domain and candidate MasterBot list.
- Explicitly label every pending item `no_mapping_inferred=true`.
- Emit a source-map SHA-256 so reviewers can tell which readiness map snapshot produced the queue.
- Generate a review artifact PR when the source map changes; no automatic assignment or resource provisioning occurs.

## Current source snapshot

The current source map lists 20 MasterBot domain decisions awaiting owner review and 10 unassigned domain profiles. This is a source-derived count, not a fixed system limit. The workflow recalculates the counts from the current source on every run.

## Approval requirements

A separate signed owner decision must identify the MasterBot/domain pair, approver, approval ID, timestamp and supporting evidence. Name similarity, capability overlap, or an empty candidate list is not approval. Training and model promotion remain blocked where the division's domain assignment or required data rights are unresolved.
