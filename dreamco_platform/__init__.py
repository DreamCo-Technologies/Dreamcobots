"""
DreamCo Platform — Phase 2 Architecture Convergence Layer.

This package provides the canonical infrastructure primitives that unify
all DreamCo bots, orchestrators, and workflows under a single coherent
abstraction: Autonomous Capability Orchestration.

Sub-packages
------------
events        — Canonical event schema (10 standardised families)
registry      — Unified bot/capability metadata registry
capabilities  — CapabilityNode + WorkflowGraph composition models
orchestration — BaseOrchestrator interface for all orchestrators
memory        — Dream Memory Layer (operational graph data store)
observability — Structured telemetry for every capability execution
governance    — Policy-as-Code engine and RBAC / workspace isolation
swarm         — Governed stigmergy primitives for autonomous coordination
"""

PLATFORM_VERSION: str = "2.0.0"
