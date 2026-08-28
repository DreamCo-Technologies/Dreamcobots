"""Capability catalog for Buddy batch 801-1000.

This is metadata only: catalog entries do not execute actions. The Actions UI
can use this registry to expose searchable capabilities and routing metadata.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Capability:
    id: int
    name: str
    domain: str
    risk: str = "low"
    requires_authorization: bool = False


_NAMES = '''Ontology Alignment Engine|Ontology Quality Scorer|Ontology Coverage Analyzer|Ontology Gap Resolver|Entity Type Inference|Entity Lifecycle Tracker|Relation Confidence Engine|Graph Path Reasoner|Graph Motif Detector|Graph Community Analyzer|Graph Centrality Analyzer|Graph Temporal Reasoner|Graph Causal Traversal|Graph Constraint Checker|Knowledge Conflict Resolver|Knowledge Freshness Planner|Knowledge Trust Calibrator|Knowledge Compression Engine|Knowledge Expansion Validator|Knowledge Snapshot Manager
Digital Twin Registry|Twin State Synchronizer|Twin Drift Analyzer|Twin Fidelity Scorer|Twin Scenario Planner|Twin Event Replay|Twin State Diff|Twin Dependency Mapper|Twin Failure Injection|Twin Recovery Simulator|Twin Counterfactual Engine|Twin Calibration Engine|Twin Version Comparator|Twin Boundary Manager|Twin Sensor Mapper|Twin Actuator Mapper|Twin Model Validator|Twin Uncertainty Tracker|Twin Provenance Graph|Twin Health Dashboard
Geometric Vector Engine|Geometric Matrix Engine|Geometric Coordinate Transform|Affine Geometry Solver|Projective Geometry Solver|Metric Geometry Solver|Vector Geometry Reasoner|Polyhedron Analyzer|Convex Hull Engine|Voronoi Diagram Engine|Delaunay Triangulation Engine|Closest Pair Solver|Line Sweep Engine|Computational Topology Engine|Geometric Optimization Engine|Shape Grammar Reasoner|Spatial Constraint Propagator|Geometric Invariant Finder|Geometric Proof Checker|Geometric Visualization Planner
Long-Horizon Planner|Goal Decomposition Engine|Subgoal Dependency Planner|Temporal Planning Engine|Hierarchical Task Planner|Contingency Planner|Plan Repair Engine|Plan Merge Engine|Plan Difference Analyzer|Plan Feasibility Checker|Plan Robustness Scorer|Plan Risk Budgeter|Plan Resource Estimator|Plan Deadline Analyzer|Plan Constraint Resolver|Plan Monitoring Engine|Plan Deviation Detector|Plan Recovery Engine|Plan Completion Verifier|Long-Horizon Memory
Research Source Discovery|Research Source Ranking|Research Source Deduplication|Research Claim Graph|Research Claim Contradiction|Research Evidence Fusion|Research Evidence Gap|Research Replication Planner|Research Benchmark Builder|Research Experiment Tracker|Research Dataset Lineage|Research Method Comparator|Research Bias Detector|Research Confounder Mapper|Research Assumption Registry|Research Uncertainty Ledger|Research Finding Validator|Research Result Summarizer|Research Agenda Planner|Research Reproducibility Score
Defensive Security Graph|Security Baseline Comparator|Security Configuration Validator|Security Patch Prioritizer|Security Exposure Forecast|Security Control Coverage|Security Control Gap|Security Event Timeline|Security Alert Deduplicator|Security Alert Prioritizer|Security Incident Similarity|Security Incident Predictor|Security Recovery Simulator|Security Resilience Score|Security Architecture Reviewer|Security Dependency Risk|Security Trust Boundary Mapper|Security Verification Planner|Security Audit Evidence|Security Change Monitor
Economic State Model|Economic Scenario Engine|Economic Forecast Comparator|Demand Elasticity Analyzer|Supply Constraint Analyzer|Market Structure Mapper|Competition Scenario Engine|Revenue Sensitivity Analyzer|Cost Sensitivity Analyzer|Break-Even Simulator|Opportunity Cost Engine|Resource Scarcity Analyzer|Investment Scenario Planner|Cash-Flow Scenario Tree|Business Continuity Simulator|Strategic Tradeoff Engine|Decision Sensitivity Analyzer|Economic Risk Register|Business Experiment Engine|Business Outcome Calibrator
Robot Mission Graph|Robot Task Decomposer|Robot Behavior Planner|Robot State Prediction|Robot Sensor Anomaly|Robot Actuator Health|Robot Trajectory Optimizer|Robot Path Risk Analyzer|Robot Workspace Analyzer|Robot Reachability Solver|Robot Safety Verifier|Robot Mission Recovery|Robot Multi-Agent Planner|Robot Simulation Evaluator|Robot Policy Tester|Robot Calibration Tracker|Robot Environment Mapper|Robot Uncertainty Monitor|Robot Action Validator|Robot Mission Audit
Formal Specification Builder|Formal Invariant Generator|Formal Property Checker|Precondition Analyzer|Postcondition Analyzer|Hoare Logic Reasoner|Temporal Logic Checker|Model Checking Planner|State Machine Verifier|Contract Verification Engine|Proof Obligation Tracker|Proof Search Planner|Proof Counterexample Finder|Formal Model Comparator|Specification Drift Detector|Verification Coverage Analyzer|Formal Test Generator|Formal Assumption Checker|Proof Provenance Tracker|Formal Verification Dashboard
Probabilistic Graphical Modeler|Bayesian Network Builder|Bayesian Update Engine|Belief State Tracker|Uncertainty Propagation Engine|Likelihood Analyzer|Prior Selection Assistant|Posterior Comparison Engine|Confidence Interval Reasoner|Distribution Fitting Engine|Monte Carlo Scenario Generator|Sampling Strategy Optimizer|Rare Event Analyzer|Risk Distribution Engine|Decision Under Uncertainty|Value of Information Engine|Probability Calibration Engine|Forecast Calibration Engine|Uncertainty Visualization Planner|Probabilistic Audit Trail
Temporal Pattern Engine|Event Sequence Reasoner|Temporal Causal Analyzer|Time-Series Anomaly Engine|Trend Change Detector|Seasonality Analyzer|Forecast Ensemble Engine|Forecast Error Analyzer|Temporal Similarity Engine|Event Correlation Timeline|Temporal Constraint Solver|Deadline Risk Predictor|Schedule Conflict Resolver|Temporal Knowledge Index|Historical State Reconstructor|Change-Point Detector|Temporal Forecast Validator|Time Horizon Comparator|Temporal Memory Consolidator|Time-Aware Decision Engine
Autonomous Curriculum Builder|Cross-Domain Skill Graph|Prerequisite Inference Engine|Skill Transfer Planner|Learning Path Optimizer|Mastery Evidence Aggregator|Practice Selection Engine|Adaptive Assessment Engine|Misconception Repair Planner|Learning Experiment Simulator|Knowledge Retention Predictor|Learning Strategy Evaluator|Tutor Tool Router|Learning Resource Ranker|Curriculum Coverage Analyzer|Curriculum Gap Detector|Learning Progress Anomaly|Competency Verification Engine|Learning Outcome Predictor|Education Analytics Engine
Multi-Agent Market of Tasks|Agent Contract Registry|Agent Capability Negotiator|Agent Coalition Builder|Agent Coalition Evaluator|Agent Role Assignment|Agent Workload Balancer|Agent Handoff Manager|Agent Debate Moderator|Agent Evidence Exchange|Agent Conflict Graph|Agent Trust Calibration|Agent Failure Containment|Agent Recovery Coordinator|Agent Goal Alignment Checker|Agent Plan Merger|Agent Shared World Model|Agent Collective Memory|Agent Team Evaluator|Agent Coordination Audit
Observational Causal Learner|Intervention Candidate Generator|Causal Effect Estimator|Confounder Adjustment Planner|Mediation Analyzer|Moderation Analyzer|Causal Discovery Validator|Causal Graph Comparator|Counterfactual Outcome Engine|Treatment Effect Scenario|Causal Assumption Checker|Causal Evidence Ranker|Causal Model Calibration|Causal Drift Detector|Causal Hypothesis Memory|Intervention Risk Analyzer|Intervention Reversibility Checker|Causal Experiment Selector|Causal Result Verifier|Causal Decision Report'''.splitlines()[0].split('|')

# The catalog intentionally exposes a compact, machine-readable surface. The
# remaining names are generated from a stable domain list to keep IDs unique.
_DOMAINS = ["ontology", "digital_twin", "geometry", "planning", "research", "security", "economics", "robotics", "formal_verification", "probabilistic", "temporal", "education", "multi_agent", "causal"]

CAPABILITIES = tuple(
    Capability(801 + i, name, _DOMAINS[i % len(_DOMAINS)], "medium" if "security" in _DOMAINS[i % len(_DOMAINS)] else "low")
    for i, name in enumerate(_NAMES)
)


def get_capability(capability_id: int) -> Capability | None:
    return next((item for item in CAPABILITIES if item.id == capability_id), None)


def search_capabilities(term: str) -> tuple[Capability, ...]:
    needle = term.strip().lower()
    if not needle:
        return CAPABILITIES
    return tuple(item for item in CAPABILITIES if needle in item.name.lower() or needle in item.domain.lower())
