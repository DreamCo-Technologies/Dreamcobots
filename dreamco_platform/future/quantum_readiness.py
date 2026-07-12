"""Quantum computing readiness assessment layer."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List


@dataclass
class QuantumVulnerability:
    algorithm: str
    qubit_threat_threshold: int
    migration_path: str


@dataclass
class ReadinessReport:
    vulnerabilities: List[QuantumVulnerability]
    readiness_score: float
    migration_timeline: Dict[str, str]
    hybrid_algorithms: List[str]


class QuantumReadiness:
    def __init__(self, root: str | Path = ".") -> None:
        self.root = Path(root)
        self.known_vulnerabilities = [
            QuantumVulnerability("RSA-2048", 4096, "Migrate to CRYSTALS-Kyber for key exchange."),
            QuantumVulnerability("ECDSA", 2500, "Adopt Dilithium or Falcon signatures."),
            QuantumVulnerability("SHA-1", 1, "Replace with SHA-256 or SHA-3."),
        ]

    def hybrid_search_stub(self, classical_score: float, quantum_hint: float) -> float:
        return round(0.7 * classical_score + 0.3 * quantum_hint, 4)

    def hybrid_optimizer_stub(self, workload_size: int, annealing_factor: float) -> float:
        return round(workload_size / max(1.0, annealing_factor + 1.0), 3)

    def assess_codebase(self) -> ReadinessReport:
        text = "\n".join(
            path.read_text(encoding="utf-8", errors="ignore")
            for path in self.root.rglob("*.py")
            if ".git" not in path.parts
        )
        matched = [
            vulnerability
            for vulnerability in self.known_vulnerabilities
            if vulnerability.algorithm.split("-")[0] in text or vulnerability.algorithm in text
        ]
        score = max(0.0, 1.0 - 0.2 * len(matched))
        timeline = {
            "2025": "Inventory cryptographic dependencies and vendor attestations.",
            "2026": "Pilot hybrid TLS and post-quantum signing for internal services.",
            "2027": "Dual-stack certificate and key exchange rollout.",
            "2028": "Migrate customer-facing control planes to PQ-safe defaults.",
            "2029": "Retire legacy RSA/ECC dependencies where feasible.",
            "2030": "Complete cryptographic transition and third-party certification refresh.",
        }
        hybrid = [
            f"search-score:{self.hybrid_search_stub(0.8, 0.6)}",
            f"optimizer-load:{self.hybrid_optimizer_stub(100, 4.0)}",
        ]
        return ReadinessReport(matched, round(score, 3), timeline, hybrid)
