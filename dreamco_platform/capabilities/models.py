"""
DreamCo Platform — Capability Composition Models
=================================================

``CapabilityNode`` is the operating-system abstraction layer for DreamCo.
Every autonomous behaviour in the platform is expressed as a capability node,
then composed into ``WorkflowGraph`` instances that are:

* **orchestratable** — nodes execute in topological order
* **replayable** — full execution lineage is preserved
* **auditable** — every edge transition is a recorded event
* **monetizable** — each node has a ``cost_profile``
* **observable** — ``observability_hooks`` attach telemetry at any node
* **composable** — graphs can include sub-graphs as capability nodes

Key types
---------
CapabilityNode   — an atomic executable unit with full metadata
ExecutionEdge    — a directed connection between two nodes (with optional condition)
GovernancePolicy — a policy rule attached to a workflow graph
WorkflowGraph    — a DAG of capability nodes with edges and policies
ExecutionResult  — the outcome of executing a single CapabilityNode
EdgeCondition    — the strategy for deciding whether an edge is traversed
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


# ---------------------------------------------------------------------------
# Edge condition
# ---------------------------------------------------------------------------

class EdgeCondition(str, Enum):
    ALWAYS = "always"       # Always traverse this edge
    ON_SUCCESS = "on_success"  # Only traverse if upstream node succeeded
    ON_FAILURE = "on_failure"  # Only traverse if upstream node failed
    CONDITIONAL = "conditional"  # Evaluate a custom predicate


# ---------------------------------------------------------------------------
# CapabilityNode
# ---------------------------------------------------------------------------

@dataclass
class CapabilityNode:
    """
    An atomic capability unit within a DreamCo workflow.

    Attributes
    ----------
    capability_id : str
        Unique identifier for this capability (e.g. ``"lead.enrich"``).
    version : str
        Semantic version of the capability contract.
    inputs : dict
        JSON-Schema-style description of expected input parameters.
    outputs : dict
        JSON-Schema-style description of produced output parameters.
    permissions : list[str]
        Required permission tokens to invoke this capability.
    cost_profile : dict
        Monetisation cost descriptors, e.g.
        ``{"per_call_usd": 0.01, "monthly_cap_usd": 50.0}``.
    event_contracts : list[str]
        Event types emitted by this capability during execution.
    retry_policy : dict
        Retry configuration, e.g.
        ``{"max_attempts": 3, "backoff_seconds": 2, "strategy": "exponential"}``.
    observability_hooks : dict
        Telemetry configuration, e.g.
        ``{"trace": True, "metrics": ["latency_ms", "cost_usd"]}``.
    description : str
        Human-readable description.
    tags : list[str]
        Searchable labels.
    executor : Callable | None
        Optional in-process executor.  When provided, ``WorkflowGraph``
        will call ``executor(inputs) → dict`` to produce a result.
        If ``None`` the node is treated as declarative (for static analysis).
    metadata : dict
        Arbitrary extra metadata.
    """

    capability_id: str
    version: str = "1.0.0"
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    permissions: List[str] = field(default_factory=list)
    cost_profile: Dict[str, Any] = field(default_factory=dict)
    event_contracts: List[str] = field(default_factory=list)
    retry_policy: Dict[str, Any] = field(default_factory=lambda: {
        "max_attempts": 1,
        "backoff_seconds": 0,
        "strategy": "none",
    })
    observability_hooks: Dict[str, Any] = field(default_factory=lambda: {
        "trace": True,
        "metrics": ["latency_ms"],
    })
    description: str = ""
    tags: List[str] = field(default_factory=list)
    executor: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = field(
        default=None, compare=False, repr=False
    )
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialise to a plain dict (executor is excluded)."""
        return {
            "capability_id": self.capability_id,
            "version": self.version,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "permissions": list(self.permissions),
            "cost_profile": dict(self.cost_profile),
            "event_contracts": list(self.event_contracts),
            "retry_policy": dict(self.retry_policy),
            "observability_hooks": dict(self.observability_hooks),
            "description": self.description,
            "tags": list(self.tags),
            "metadata": dict(self.metadata),
        }

    def __repr__(self) -> str:
        return f"CapabilityNode(id={self.capability_id!r}, v={self.version!r})"


# ---------------------------------------------------------------------------
# ExecutionEdge
# ---------------------------------------------------------------------------

@dataclass
class ExecutionEdge:
    """
    A directed edge between two ``CapabilityNode`` instances.

    Attributes
    ----------
    from_id : str
        ``capability_id`` of the source node.
    to_id : str
        ``capability_id`` of the target node.
    condition : EdgeCondition
        When to traverse this edge. Default: ``ALWAYS``.
    predicate : Callable | None
        Optional Python callable used when ``condition == CONDITIONAL``.
        Signature: ``predicate(result: ExecutionResult) -> bool``.
    label : str
        Human-readable label for this edge.
    metadata : dict
        Arbitrary extra metadata.
    """

    from_id: str
    to_id: str
    condition: EdgeCondition = EdgeCondition.ALWAYS
    predicate: Optional[Callable[["ExecutionResult"], bool]] = field(
        default=None, compare=False, repr=False
    )
    label: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def should_traverse(self, result: "ExecutionResult") -> bool:
        """Return ``True`` if this edge should be followed given *result*."""
        if self.condition == EdgeCondition.ALWAYS:
            return True
        if self.condition == EdgeCondition.ON_SUCCESS:
            return result.success
        if self.condition == EdgeCondition.ON_FAILURE:
            return not result.success
        if self.condition == EdgeCondition.CONDITIONAL:
            if self.predicate is None:
                return True
            return self.predicate(result)
        return True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "from_id": self.from_id,
            "to_id": self.to_id,
            "condition": self.condition.value,
            "label": self.label,
            "metadata": dict(self.metadata),
        }


# ---------------------------------------------------------------------------
# GovernancePolicy
# ---------------------------------------------------------------------------

@dataclass
class GovernancePolicy:
    """
    A declarative governance policy attached to a workflow graph.

    Attributes
    ----------
    policy_id : str
        Unique identifier.
    description : str
        Human-readable policy description.
    condition : str
        Natural-language or expression description of the trigger condition
        (e.g. ``"action_cost > 1000"``).
    action : str
        The enforcement action (e.g. ``"require_human_approval"``).
    enabled : bool
        Whether the policy is currently active. Defaults to ``True``.
    metadata : dict
        Arbitrary extra metadata.
    """

    policy_id: str
    description: str = ""
    condition: str = ""
    action: str = ""
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "policy_id": self.policy_id,
            "description": self.description,
            "condition": self.condition,
            "action": self.action,
            "enabled": self.enabled,
            "metadata": dict(self.metadata),
        }


# ---------------------------------------------------------------------------
# ExecutionResult
# ---------------------------------------------------------------------------

@dataclass
class ExecutionResult:
    """
    The outcome of executing a single ``CapabilityNode``.

    Attributes
    ----------
    capability_id : str
        Which capability produced this result.
    success : bool
        Whether the execution succeeded.
    output : dict
        The produced output data.
    error : str | None
        Error message if the execution failed.
    latency_ms : float
        Wall-clock execution time in milliseconds.
    cost_usd : float
        Monetary cost incurred by this execution.
    timestamp : float
        Unix timestamp of completion.
    attempts : int
        Number of attempts made (including retries).
    metadata : dict
        Arbitrary extra metadata.
    """

    capability_id: str
    success: bool = True
    output: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    latency_ms: float = 0.0
    cost_usd: float = 0.0
    timestamp: float = field(default_factory=time.time)
    attempts: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "capability_id": self.capability_id,
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "latency_ms": self.latency_ms,
            "cost_usd": self.cost_usd,
            "timestamp": self.timestamp,
            "attempts": self.attempts,
            "metadata": dict(self.metadata),
        }


# ---------------------------------------------------------------------------
# WorkflowGraph
# ---------------------------------------------------------------------------

class WorkflowGraph:
    """
    A directed acyclic graph of ``CapabilityNode`` instances connected by
    ``ExecutionEdge`` instances, optionally governed by ``GovernancePolicy``
    instances.

    The graph can be validated, serialised, and executed in topological order.

    Parameters
    ----------
    graph_id : str
        Unique workflow identifier.
    description : str
        Human-readable description.
    """

    def __init__(
        self,
        graph_id: str = "",
        description: str = "",
    ) -> None:
        self.graph_id: str = graph_id or str(uuid.uuid4())
        self.description: str = description
        self.nodes: Dict[str, CapabilityNode] = {}
        self.edges: List[ExecutionEdge] = []
        self.policies: List[GovernancePolicy] = []
        self.created_at: float = time.time()

    # ------------------------------------------------------------------
    # Mutation helpers
    # ------------------------------------------------------------------

    def add_node(self, node: CapabilityNode) -> "WorkflowGraph":
        """Add *node* to the graph. Returns ``self`` for chaining."""
        self.nodes[node.capability_id] = node
        return self

    def add_edge(self, edge: ExecutionEdge) -> "WorkflowGraph":
        """
        Add *edge* to the graph.

        Raises
        ------
        ValueError
            If ``from_id`` or ``to_id`` references a non-existent node.
        """
        if edge.from_id not in self.nodes:
            raise ValueError(
                f"Edge source {edge.from_id!r} is not a registered node."
            )
        if edge.to_id not in self.nodes:
            raise ValueError(
                f"Edge target {edge.to_id!r} is not a registered node."
            )
        self.edges.append(edge)
        return self

    def add_policy(self, policy: GovernancePolicy) -> "WorkflowGraph":
        """Attach *policy* to the graph. Returns ``self`` for chaining."""
        self.policies.append(policy)
        return self

    # ------------------------------------------------------------------
    # Traversal
    # ------------------------------------------------------------------

    def topological_sort(self) -> List[str]:
        """
        Return capability IDs in topological execution order (Kahn's algorithm).

        Raises
        ------
        ValueError
            If the graph contains a cycle.
        """
        in_degree: Dict[str, int] = {nid: 0 for nid in self.nodes}
        adjacency: Dict[str, List[str]] = {nid: [] for nid in self.nodes}

        for edge in self.edges:
            adjacency[edge.from_id].append(edge.to_id)
            in_degree[edge.to_id] += 1

        queue = [nid for nid, deg in in_degree.items() if deg == 0]
        order: List[str] = []

        while queue:
            nid = queue.pop(0)
            order.append(nid)
            for neighbour in adjacency[nid]:
                in_degree[neighbour] -= 1
                if in_degree[neighbour] == 0:
                    queue.append(neighbour)

        if len(order) != len(self.nodes):
            raise ValueError(
                "WorkflowGraph contains a cycle — topological sort impossible."
            )
        return order

    def get_outgoing_edges(self, capability_id: str) -> List[ExecutionEdge]:
        """Return all edges originating from *capability_id*."""
        return [e for e in self.edges if e.from_id == capability_id]

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def execute(
        self,
        inputs: Dict[str, Any] | None = None,
    ) -> Dict[str, ExecutionResult]:
        """
        Execute all nodes in topological order, passing results between nodes.

        Only nodes whose inbound edges permit traversal (based on upstream
        results) are executed.  Nodes with no executor are skipped
        (declarative mode).

        Parameters
        ----------
        inputs : dict | None
            Initial inputs fed to the first node(s) in the graph.

        Returns
        -------
        dict[str, ExecutionResult]
            Mapping of ``capability_id → ExecutionResult`` for every node
            that was executed.
        """
        inputs = inputs or {}
        order = self.topological_sort()
        results: Dict[str, ExecutionResult] = {}
        current_data: Dict[str, Any] = dict(inputs)

        for nid in order:
            node = self.nodes[nid]

            # Determine if this node should be executed based on inbound edges
            inbound = [e for e in self.edges if e.to_id == nid]
            if inbound:
                should_run = any(
                    e.should_traverse(results[e.from_id])
                    for e in inbound
                    if e.from_id in results
                )
                if not should_run:
                    continue

            if node.executor is None:
                # Declarative node — record a skipped result
                results[nid] = ExecutionResult(
                    capability_id=nid,
                    success=True,
                    output={"skipped": True, "reason": "no_executor"},
                )
                continue

            start = time.time()
            attempts = 0
            max_attempts = node.retry_policy.get("max_attempts", 1)
            backoff = node.retry_policy.get("backoff_seconds", 0)
            last_error: Optional[str] = None
            result_output: Dict[str, Any] = {}
            success = False

            while attempts < max_attempts:
                attempts += 1
                try:
                    result_output = node.executor(current_data)
                    success = True
                    break
                except Exception as exc:  # noqa: BLE001
                    last_error = str(exc)
                    if attempts < max_attempts and backoff > 0:
                        import time as _time
                        _time.sleep(backoff)

            latency_ms = (time.time() - start) * 1000.0
            cost_usd = float(node.cost_profile.get("per_call_usd", 0.0))

            result = ExecutionResult(
                capability_id=nid,
                success=success,
                output=result_output,
                error=None if success else last_error,
                latency_ms=latency_ms,
                cost_usd=cost_usd,
                attempts=attempts,
            )
            results[nid] = result
            if success:
                current_data.update(result_output)

        return results

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate(self) -> bool:
        """
        Validate graph structure.

        Checks
        ------
        - At least one node exists.
        - All edge endpoints reference existing nodes.
        - Graph is acyclic (topological sort succeeds).

        Returns
        -------
        bool
            ``True`` on success.

        Raises
        ------
        ValueError
            With a descriptive message on the first violation.
        """
        if not self.nodes:
            raise ValueError("WorkflowGraph must contain at least one node.")
        for edge in self.edges:
            if edge.from_id not in self.nodes:
                raise ValueError(f"Edge from unknown node {edge.from_id!r}.")
            if edge.to_id not in self.nodes:
                raise ValueError(f"Edge to unknown node {edge.to_id!r}.")
        self.topological_sort()  # raises on cycle
        return True

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """Serialise to a plain dict."""
        return {
            "graph_id": self.graph_id,
            "description": self.description,
            "created_at": self.created_at,
            "nodes": [n.to_dict() for n in self.nodes.values()],
            "edges": [e.to_dict() for e in self.edges],
            "policies": [p.to_dict() for p in self.policies],
        }

    def __repr__(self) -> str:
        return (
            f"WorkflowGraph(id={self.graph_id!r}, "
            f"nodes={len(self.nodes)}, edges={len(self.edges)})"
        )
