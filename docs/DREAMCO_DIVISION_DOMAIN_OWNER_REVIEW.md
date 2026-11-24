# DreamCo division domain and shared-platform owner review

The repository distinguishes **45 original core domain divisions**, **10 promoted supplemental domain profiles**, and **20 shared-platform MasterBots**. The 65-entry MasterBot registry is not a claim that all 65 MasterBots are primary owners of domain divisions.

## Source-backed ownership model

- The first 45 canonical MasterBots correspond to the original 45 core domain divisions. Exact-name crosswalk rows remain proposals and do not constitute owner approval.
- MasterBots 46–65 are explicitly classified by `config/division-reconciliation-policy.json` and `config/generated/division-reconciliation.json` as `shared_platform_service` roles available to all domain divisions. Their primary domain owner is intentionally null; they must not be assigned to a domain merely to fill a crosswalk.
- The 10 promoted supplemental domain profiles remain first-class domains. Their proposed collaborator MasterBot IDs come from the reconciliation policy, but each link remains pending owner approval.
- Resource bundles, dataset lanes, capability packs, or workflow success do not prove that a service is connected, trained, benchmarked, mastered, or production-ready.

## Queue behavior

- Read both the generated resource readiness map and the generated division reconciliation.
- Separate unresolved primary-domain decisions from shared-platform role confirmations.
- Preserve each shared-platform MasterBot's purpose, ownership status, availability scope, resource bundle, dataset lane, capability packs, and evidence references.
- Keep `primary_domain_owner=null` for shared-platform services until an owner decision explicitly changes the architecture.
- Surface the 10 supplemental-domain collaborator IDs as proposals with their related core domain and source portfolio; do not turn a candidate into an approved assignment.
- Preserve every pending item with `no_mapping_inferred=true` and a SHA-256 of both source artifacts.

## Current source snapshot

The current reconciliation policy identifies 20 shared-platform MasterBots (IDs 46–65). The raw 55-domain crosswalk therefore leaves those 20 without a primary domain; the review queue classifies them as shared-platform roles rather than treating them as missing domain owners. Owner confirmation of the shared-platform role and its operational owner is still required.

The 10 promoted supplemental domains have policy-proposed collaborator links. Those links remain pending owner approval. The 45 original core domain exact-name matches also remain proposed until owner approval. These counts describe registry structure, not runtime execution or mastery.

## Approval requirements

A separate signed owner decision must identify the proposed role or MasterBot/domain relationship, approver, approval ID, timestamp, and supporting evidence. Name similarity or capability overlap is not approval. Training, privileged routing, and model promotion remain blocked where required ownership, dataset rights, model licensing, compute approval, or independent evaluation evidence is missing.
