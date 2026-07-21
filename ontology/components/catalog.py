"""Catalog of ontology component bots for adapter-first rollout."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence, Tuple


@dataclass(frozen=True)
class OntologyComponentBotSpec:
    name: str
    domain: str
    purpose: str
    phase: str = "Phase A"


_DOMAIN_COMPONENTS: Sequence[Tuple[str, Sequence[Tuple[str, str]]]] = (
    (
        "object",
        (
            ("ObjectSchemaBot", "Defines canonical object schemas."),
            ("ObjectVersioningBot", "Manages schema version upgrades."),
            ("ObjectValidationBot", "Validates objects against contracts."),
            ("ObjectIdentityBot", "Generates canonical ontology IDs."),
            ("ObjectDedupBot", "Merges duplicate objects."),
            ("ObjectEnrichmentBot", "Fills missing object metadata."),
            ("ObjectAliasBot", "Tracks alternate names and IDs."),
            ("ObjectLifecycleBot", "Manages object state transitions."),
            ("ObjectDeprecationBot", "Handles retired object types."),
            ("ObjectTemplateBot", "Scaffolds new ontology objects."),
        ),
    ),
    (
        "relationship",
        (
            ("RelationshipSchemaBot", "Defines relationship type contracts."),
            ("RelationshipValidationBot", "Validates edge correctness."),
            ("RelationshipInferenceBot", "Infers implicit relationships."),
            ("RelationshipCardinalityBot", "Enforces cardinality rules."),
            ("RelationshipConflictBot", "Resolves contradictory edges."),
            ("RelationshipPropagationBot", "Propagates inherited links."),
            ("RelationshipWeightingBot", "Scores relationship strength."),
            ("RelationshipTemporalBot", "Tracks time-bounded edges."),
            ("RelationshipLineageBot", "Records edge creation history."),
            ("RelationshipCleanupBot", "Removes stale and broken relationships."),
        ),
    ),
    (
        "workflow",
        (
            ("WorkflowProjectionBot", "Projects legacy workflows to ontology."),
            ("WorkflowStateSyncBot", "Syncs workflow state to objects."),
            ("WorkflowStepMapperBot", "Maps steps to ontology actions."),
            ("WorkflowDependencyBot", "Models inter-workflow dependencies."),
            ("WorkflowRetryPolicyBot", "Standardizes retry semantics."),
            ("WorkflowCompensationBot", "Models rollback and compensation links."),
            ("WorkflowHealthBot", "Detects stuck and failed workflows."),
            ("WorkflowSLAWatcherBot", "Monitors workflow SLA breaches."),
            ("WorkflowReplayBot", "Replays historical workflow events."),
            ("WorkflowMigrationBot", "Migrates old workflow formats."),
        ),
    ),
    (
        "event",
        (
            ("EventEnvelopeBot", "Enforces canonical event envelopes."),
            ("EventNormalizationBot", "Standardizes fragmented event payloads."),
            ("EventRoutingBot", "Routes events by ontology context."),
            ("EventOrderingBot", "Preserves causal order constraints."),
            ("EventCorrelationBot", "Links related events into chains."),
            ("EventIdempotencyBot", "Deduplicates repeated event emissions."),
            ("EventAnomalyBot", "Flags unusual event patterns."),
            ("EventReplayGuardBot", "Protects safe event replay."),
            ("EventRetentionBot", "Applies event retention policies."),
            ("EventAuditBot", "Signs and verifies audit events."),
        ),
    ),
    (
        "role",
        (
            ("RoleContractBot", "Defines planner/coordinator/executor contracts."),
            ("RolePermissionBot", "Maps roles to allowed actions."),
            ("RoleCapabilityBot", "Maps roles to capabilities and tools."),
            ("RoleAssignmentBot", "Assigns agents to runtime roles."),
            ("RoleEscalationBot", "Handles escalation path logic."),
            ("RoleHandoffBot", "Manages inter-role handoffs."),
            ("RolePerformanceBot", "Tracks role-level KPIs."),
            ("RoleDriftBot", "Detects deviation from role contracts."),
            ("MultiAgentSyncBot", "Coordinates shared runtime context."),
            ("AgentSessionLineageBot", "Tracks agent session lineage."),
        ),
    ),
    (
        "policy",
        (
            ("PolicyAuthoringBot", "Creates reusable policy definitions."),
            ("PolicyEvaluationBot", "Executes policy.can checks."),
            ("PolicySimulationBot", "Dry-runs policy impacts."),
            ("PolicyConflictBot", "Detects conflicting policy rules."),
            ("PolicyExplainabilityBot", "Explains allow and deny decisions."),
            ("PolicyCoverageBot", "Finds unprotected actions and objects."),
            ("PolicyVersionBot", "Versions policy changes safely."),
            ("PolicyRollbackBot", "Restores prior policy states."),
            ("PolicyExceptionBot", "Manages temporary policy waivers."),
            ("PolicyEvidenceBot", "Stores policy decision evidence."),
        ),
    ),
    (
        "memory",
        (
            ("MemoryObjectBindingBot", "Binds memory entries to object IDs."),
            ("MemoryEmbeddingBot", "Manages embedding generation pipeline."),
            ("MemoryRetrievalBot", "Performs ontology-aware semantic retrieval."),
            ("MemoryTTLBot", "Expires stale memory nodes."),
            ("MemoryConsistencyBot", "Reconciles conflicting memories."),
            ("MemoryPrivacyBot", "Enforces memory data privacy classes."),
            ("MemoryPartitionBot", "Partitions memory by division and tenant."),
            ("MemorySummarizationBot", "Compacts long memory trails."),
            ("MemoryProvenanceBot", "Tracks memory source and provenance."),
            ("MemoryReplayBot", "Reconstructs context from memory history."),
        ),
    ),
    (
        "integration",
        (
            ("IntegrationCatalogBot", "Registers integrations as ontology objects."),
            ("IntegrationCapabilityBot", "Maps integration capabilities and scopes."),
            ("IntegrationCredentialPolicyBot", "Applies credential access policies."),
            ("IntegrationHealthBot", "Monitors integration availability and errors."),
            ("IntegrationRateLimitBot", "Tracks and enforces API rate limits."),
            ("IntegrationContractTestBot", "Validates connector contracts."),
            ("IntegrationWebhookBot", "Standardizes webhook event mapping."),
            ("IntegrationFallbackBot", "Handles connector failover logic."),
            ("IntegrationUsageAuditBot", "Audits integration usage lineage."),
            ("IntegrationLifecycleBot", "Deprecates and replaces integrations safely."),
        ),
    ),
    (
        "graph",
        (
            ("GraphProjectionBot", "Builds in-memory ontology graph views."),
            ("GraphSerializerBot", "Serializes graph for persistence and exchange."),
            ("GraphQueryBot", "Serves ontology graph queries."),
            ("GraphDiffBot", "Computes graph changes between snapshots."),
            ("GraphIntegrityBot", "Validates graph constraints globally."),
            ("GraphBackfillBot", "Backfills graph from legacy systems."),
            ("GraphIndexBot", "Maintains graph indexes for lookup."),
            ("GraphExplainBot", "Explains graph path reasoning."),
            ("GraphSyncBot", "Syncs transactional DB and graph store."),
            ("GraphExportBot", "Exports ontology graphs to external tools."),
        ),
    ),
    (
        "governance",
        (
            ("GovernanceLineageBot", "Provides end-to-end lineage tracking."),
            ("GovernanceTraceBot", "Builds workflow and action traceability reports."),
            ("GovernanceCausalChainBot", "Builds causal chain explanations."),
            ("GovernanceReplayBot", "Generates replayable execution timelines."),
            ("GovernanceRiskBot", "Scores governance and compliance risk."),
            ("GovernanceControlBot", "Checks required controls per action."),
            ("GovernanceDriftBot", "Detects governance drift over time."),
            ("GovernanceReportingBot", "Generates audit-ready governance reports."),
            ("OntologyAdoptionBot", "Tracks ontology migration progress by domain."),
            ("OntologyStewardBot", "Coordinates ontology change governance."),
        ),
    ),
)


def _build_specs() -> List[OntologyComponentBotSpec]:
    specs: List[OntologyComponentBotSpec] = []
    for domain, components in _DOMAIN_COMPONENTS:
        for name, purpose in components:
            specs.append(OntologyComponentBotSpec(name=name, domain=domain, purpose=purpose))
    return specs


ONTOLOGY_COMPONENT_BOTS = _build_specs()


def get_component_bot(name: str) -> OntologyComponentBotSpec | None:
    return next((spec for spec in ONTOLOGY_COMPONENT_BOTS if spec.name == name), None)


def list_component_bots(domain: str | None = None) -> List[OntologyComponentBotSpec]:
    if domain is None:
        return list(ONTOLOGY_COMPONENT_BOTS)
    return [spec for spec in ONTOLOGY_COMPONENT_BOTS if spec.domain == domain]


if len(ONTOLOGY_COMPONENT_BOTS) != 100:
    raise ValueError("Ontology component catalog must contain exactly 100 components.")
