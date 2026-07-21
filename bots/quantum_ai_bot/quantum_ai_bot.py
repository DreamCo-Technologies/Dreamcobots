"""Quantum AI Bot — main entry point for quantum computing simulation and optimization."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, get_tier_config, get_upgrade_path
from bots.quantum_ai_bot.tiers import BOT_FEATURES, get_bot_tier_info
from framework import GlobalAISourcesFlow  # noqa: F401

from bots.quantum_ai_bot.quantum_simulator import (
    QuantumCircuitSimulator,
    QuantumCircuitSimulatorError,
    HybridQuantumAIModel,
    HybridQuantumAIModelError,
)
from bots.quantum_ai_bot.optimization_engine import (
    QuantumOptimizer,
    QuantumOptimizerError,
    QuantumPartnershipManager,
    QuantumPartnershipManagerError,
    PROBLEM_TYPES,
    PROVIDERS,
)

_flow = GlobalAISourcesFlow(bot_name="QuantumAIBot")


class QuantumAIBotError(Exception):
    """Raised when a Quantum AI Bot feature is unavailable on the current tier."""


class QuantumAIBot:
    """Tier-aware Quantum AI Bot for circuit simulation, optimization, and quantum partnerships."""

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)
        self.simulator = QuantumCircuitSimulator(tier=tier)
        self.hybrid_model = HybridQuantumAIModel(tier=tier)
        self.optimizer = QuantumOptimizer(tier=tier)
        self.partnership_manager = QuantumPartnershipManager(tier=tier)
        self._activity_log: list = []

    # ------------------------------------------------------------------
    # Quantum circuit simulation
    # ------------------------------------------------------------------

    def simulate_quantum_circuit(self, qubits: int, gates: list, shots: int) -> dict:
        """Simulate a quantum circuit.

        Parameters
        ----------
        qubits:
            Number of qubits.
        gates:
            List of gate configuration dicts.
        shots:
            Number of measurement shots.

        Raises
        ------
        QuantumAIBotError
            If qubit/shot/gate limits are exceeded for the current tier.
        """
        try:
            result = self.simulator.simulate_circuit(qubits, gates, shots)
            self._activity_log.append({"action": "simulate_circuit", "qubits": qubits})
            return result
        except QuantumCircuitSimulatorError as exc:
            raise QuantumAIBotError(str(exc)) from exc

    # ------------------------------------------------------------------
    # Optimization
    # ------------------------------------------------------------------

    def solve_optimization_problem(
        self, problem_type: str, constraints: dict, variables: list
    ) -> dict:
        """Solve a quantum optimization problem.

        Parameters
        ----------
        problem_type:
            One of :data:`PROBLEM_TYPES`.
        constraints:
            Problem constraints.
        variables:
            Decision variable names.

        Raises
        ------
        QuantumAIBotError
            If the problem type is not available on the current tier.
        """
        try:
            result = self.optimizer.solve_optimization(problem_type, constraints, variables)
            self._activity_log.append({"action": "solve_optimization", "problem_type": problem_type})
            return result
        except QuantumOptimizerError as exc:
            raise QuantumAIBotError(str(exc)) from exc

    # ------------------------------------------------------------------
    # Physics simulation
    # ------------------------------------------------------------------

    def run_physics_simulation(self, system_type: str, parameters: dict) -> dict:
        """Run a quantum physics simulation (PRO/ENTERPRISE only).

        Parameters
        ----------
        system_type:
            Physical system to simulate.
        parameters:
            System parameters.

        Raises
        ------
        QuantumAIBotError
            If physics simulations are not available on the current tier.
        """
        try:
            result = self.optimizer.simulate_physics(system_type, parameters)
            self._activity_log.append({"action": "physics_simulation", "system_type": system_type})
            return result
        except QuantumOptimizerError as exc:
            raise QuantumAIBotError(str(exc)) from exc

    # ------------------------------------------------------------------
    # Quantum partnerships
    # ------------------------------------------------------------------

    def connect_quantum_partner(self, provider: str) -> dict:
        """Connect to a quantum hardware provider.

        Parameters
        ----------
        provider:
            One of :data:`PROVIDERS`.

        Raises
        ------
        QuantumAIBotError
            If the provider is not accessible on the current tier.
        """
        try:
            result = self.partnership_manager.connect_quantum_provider(provider)
            self._activity_log.append({"action": "connect_provider", "provider": provider})
            return result
        except QuantumPartnershipManagerError as exc:
            raise QuantumAIBotError(str(exc)) from exc

    # ------------------------------------------------------------------
    # Dashboard
    # ------------------------------------------------------------------

    def get_quantum_dashboard(self) -> dict:
        """Return a comprehensive summary of bot capabilities and activity."""
        tier_info = get_bot_tier_info(self.tier)
        upgrade = get_upgrade_path(self.tier)
        return {
            "bot": "QuantumAIBot",
            "tier": self.tier.value,
            "tier_name": self.config.name,
            "price_usd_monthly": tier_info["price_usd_monthly"],
            "features": BOT_FEATURES[self.tier.value],
            "supported_problem_types": PROBLEM_TYPES,
            "supported_providers": PROVIDERS,
            "activity_count": len(self._activity_log),
            "recent_activity": self._activity_log[-5:],
            "upgrade_available": upgrade is not None,
            "upgrade_tier": upgrade.name if upgrade else None,
        }
