"""Tests for bots/quantum_ai_bot/ — quantum circuit simulator, optimizer, and main bot."""
import sys, os

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, os.path.join(AI_MODELS_DIR, 'models'))
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.quantum_ai_bot.quantum_simulator import (
    QuantumCircuitSimulator,
    QuantumCircuitSimulatorError,
    HybridQuantumAIModel,
    HybridQuantumAIModelError,
    GATE_TYPES,
)
from bots.quantum_ai_bot.optimization_engine import (
    QuantumOptimizer,
    QuantumOptimizerError,
    QuantumPartnershipManager,
    QuantumPartnershipManagerError,
    PROBLEM_TYPES,
    PROVIDERS,
)
from bots.quantum_ai_bot.quantum_ai_bot import QuantumAIBot, QuantumAIBotError
from bots.quantum_ai_bot.tiers import BOT_FEATURES, get_bot_tier_info


# ===========================================================================
# QuantumCircuitSimulator
# ===========================================================================

class TestQuantumCircuitSimulatorInit:
    def test_default_tier_is_free(self):
        sim = QuantumCircuitSimulator()
        assert sim.tier == Tier.FREE

    def test_pro_tier(self):
        sim = QuantumCircuitSimulator(tier=Tier.PRO)
        assert sim.tier == Tier.PRO

    def test_enterprise_tier(self):
        sim = QuantumCircuitSimulator(tier=Tier.ENTERPRISE)
        assert sim.tier == Tier.ENTERPRISE

    def test_config_loaded(self):
        sim = QuantumCircuitSimulator()
        assert sim.config is not None


class TestSimulateCircuit:
    def test_returns_dict(self):
        sim = QuantumCircuitSimulator(tier=Tier.FREE)
        result = sim.simulate_circuit(2, [{"type": "hadamard"}], 50)
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        sim = QuantumCircuitSimulator(tier=Tier.FREE)
        result = sim.simulate_circuit(2, [{"type": "hadamard"}], 50)
        for key in ("circuit_id", "qubits", "shots", "state_probabilities", "measurement_counts"):
            assert key in result

    def test_free_tier_4_qubit_limit(self):
        sim = QuantumCircuitSimulator(tier=Tier.FREE)
        result = sim.simulate_circuit(4, [], 10)
        assert result["qubits"] == 4

    def test_free_tier_exceeds_qubit_limit(self):
        sim = QuantumCircuitSimulator(tier=Tier.FREE)
        with pytest.raises(QuantumCircuitSimulatorError):
            sim.simulate_circuit(5, [], 10)

    def test_pro_tier_16_qubit_limit(self):
        sim = QuantumCircuitSimulator(tier=Tier.PRO)
        result = sim.simulate_circuit(16, [], 100)
        assert result["qubits"] == 16

    def test_pro_tier_exceeds_qubit_limit(self):
        sim = QuantumCircuitSimulator(tier=Tier.PRO)
        with pytest.raises(QuantumCircuitSimulatorError):
            sim.simulate_circuit(17, [], 100)

    def test_enterprise_tier_50_qubit_limit(self):
        sim = QuantumCircuitSimulator(tier=Tier.ENTERPRISE)
        result = sim.simulate_circuit(50, [], 100)
        assert result["qubits"] == 50

    def test_free_shot_limit_capped(self):
        sim = QuantumCircuitSimulator(tier=Tier.FREE)
        result = sim.simulate_circuit(2, [], 500)
        assert result["shots"] <= 100

    def test_pro_shot_limit_capped(self):
        sim = QuantumCircuitSimulator(tier=Tier.PRO)
        result = sim.simulate_circuit(2, [], 5000)
        assert result["shots"] <= 1000

    def test_enterprise_shots_not_capped(self):
        sim = QuantumCircuitSimulator(tier=Tier.ENTERPRISE)
        result = sim.simulate_circuit(2, [], 9999)
        assert result["shots"] == 9999

    def test_state_probabilities_sum_to_one(self):
        sim = QuantumCircuitSimulator(tier=Tier.FREE)
        result = sim.simulate_circuit(2, [{"type": "hadamard"}], 100)
        total = sum(result["state_probabilities"].values())
        assert abs(total - 1.0) < 1e-3

    def test_circuit_id_stored(self):
        sim = QuantumCircuitSimulator(tier=Tier.FREE)
        result = sim.simulate_circuit(2, [], 10)
        assert result["circuit_id"] in sim._circuits

    def test_free_gate_type_violation(self):
        sim = QuantumCircuitSimulator(tier=Tier.FREE)
        with pytest.raises(QuantumCircuitSimulatorError):
            sim.simulate_circuit(2, [{"type": "cnot"}], 10)

    def test_invalid_qubits_raises(self):
        sim = QuantumCircuitSimulator(tier=Tier.FREE)
        with pytest.raises(QuantumCircuitSimulatorError):
            sim.simulate_circuit(0, [], 10)


class TestCreateQuantumGate:
    def test_returns_dict(self):
        sim = QuantumCircuitSimulator(tier=Tier.FREE)
        gate = sim.create_quantum_gate("hadamard", [0])
        assert isinstance(gate, dict)

    def test_gate_has_required_keys(self):
        sim = QuantumCircuitSimulator(tier=Tier.FREE)
        gate = sim.create_quantum_gate("pauli_x", [0])
        assert "gate_type" in gate
        assert "target_qubits" in gate

    def test_free_allowed_gates(self):
        sim = QuantumCircuitSimulator(tier=Tier.FREE)
        for g in ("hadamard", "pauli_x", "pauli_z"):
            gate = sim.create_quantum_gate(g, [0])
            assert gate["gate_type"] == g

    def test_free_blocked_gate(self):
        sim = QuantumCircuitSimulator(tier=Tier.FREE)
        with pytest.raises(QuantumCircuitSimulatorError):
            sim.create_quantum_gate("cnot", [0, 1])

    def test_pro_allows_all_gate_types(self):
        sim = QuantumCircuitSimulator(tier=Tier.PRO)
        for g in GATE_TYPES:
            gate = sim.create_quantum_gate(g, [0])
            assert gate["gate_type"] == g

    def test_invalid_gate_type_raises(self):
        sim = QuantumCircuitSimulator(tier=Tier.FREE)
        with pytest.raises(QuantumCircuitSimulatorError):
            sim.create_quantum_gate("invalid_gate", [0])


class TestMeasureQuantumState:
    def test_returns_dict(self):
        sim = QuantumCircuitSimulator(tier=Tier.FREE)
        r = sim.simulate_circuit(2, [], 10)
        m = sim.measure_quantum_state(r["circuit_id"])
        assert isinstance(m, dict)

    def test_has_required_keys(self):
        sim = QuantumCircuitSimulator(tier=Tier.FREE)
        r = sim.simulate_circuit(2, [], 10)
        m = sim.measure_quantum_state(r["circuit_id"])
        for key in ("circuit_id", "dominant_state", "dominant_probability", "collapsed_state"):
            assert key in m

    def test_invalid_circuit_id_raises(self):
        sim = QuantumCircuitSimulator(tier=Tier.FREE)
        with pytest.raises(QuantumCircuitSimulatorError):
            sim.measure_quantum_state("nonexistent-id")

    def test_dominant_state_in_probabilities(self):
        sim = QuantumCircuitSimulator(tier=Tier.FREE)
        r = sim.simulate_circuit(2, [], 10)
        m = sim.measure_quantum_state(r["circuit_id"])
        assert m["dominant_state"] in r["state_probabilities"]


# ===========================================================================
# HybridQuantumAIModel
# ===========================================================================

class TestHybridQuantumAIModel:
    def test_default_tier(self):
        model = HybridQuantumAIModel()
        assert model.tier == Tier.FREE

    def test_free_tier_train_raises(self):
        model = HybridQuantumAIModel(tier=Tier.FREE)
        with pytest.raises(HybridQuantumAIModelError):
            model.train_hybrid_model({"samples": 100}, ["q1", "q2"])

    def test_pro_train_returns_dict(self):
        model = HybridQuantumAIModel(tier=Tier.PRO)
        result = model.train_hybrid_model({"samples": 200}, ["q1", "q2", "q3"])
        assert isinstance(result, dict)

    def test_train_has_required_keys(self):
        model = HybridQuantumAIModel(tier=Tier.PRO)
        result = model.train_hybrid_model({"samples": 100}, ["q1"])
        for key in ("model_id", "training_accuracy", "quantum_advantage_factor"):
            assert key in result

    def test_enterprise_train_has_noise_mitigation(self):
        model = HybridQuantumAIModel(tier=Tier.ENTERPRISE)
        result = model.train_hybrid_model({"samples": 500}, ["q1", "q2"])
        assert result.get("noise_mitigation") is True

    def test_free_predict_raises(self):
        model = HybridQuantumAIModel(tier=Tier.FREE)
        with pytest.raises(HybridQuantumAIModelError):
            model.predict({"features": [0.5]}, "fake-id")

    def test_pro_predict_returns_dict(self):
        model = HybridQuantumAIModel(tier=Tier.PRO)
        train = model.train_hybrid_model({"samples": 100}, ["q1"])
        result = model.predict({"features": [0.5, 0.3]}, train["model_id"])
        assert isinstance(result, dict)
        assert "prediction" in result

    def test_predict_unknown_model_raises(self):
        model = HybridQuantumAIModel(tier=Tier.PRO)
        with pytest.raises(HybridQuantumAIModelError):
            model.predict({"features": [0.5]}, "unknown-id")

    def test_evaluate_quantum_advantage_returns_dict(self):
        model = HybridQuantumAIModel(tier=Tier.FREE)
        result = model.evaluate_quantum_advantage("optimization")
        assert isinstance(result, dict)
        assert "quantum_speedup" in result

    def test_evaluate_quantum_advantage_all_problem_types(self):
        model = HybridQuantumAIModel(tier=Tier.PRO)
        for pt in ("optimization", "machine_learning", "cryptography", "simulation", "search"):
            result = model.evaluate_quantum_advantage(pt)
            assert result["problem_type"] == pt

    def test_enterprise_evaluate_has_benchmark(self):
        model = HybridQuantumAIModel(tier=Tier.ENTERPRISE)
        result = model.evaluate_quantum_advantage("simulation")
        assert "benchmark_score" in result


# ===========================================================================
# QuantumOptimizer
# ===========================================================================

class TestQuantumOptimizer:
    def test_default_tier(self):
        opt = QuantumOptimizer()
        assert opt.tier == Tier.FREE

    def test_free_allowed_problem(self):
        opt = QuantumOptimizer(tier=Tier.FREE)
        result = opt.solve_optimization("traveling_salesman", {}, ["a", "b", "c"])
        assert isinstance(result, dict)

    def test_free_blocked_problem(self):
        opt = QuantumOptimizer(tier=Tier.FREE)
        with pytest.raises(QuantumOptimizerError):
            opt.solve_optimization("protein_folding", {}, [])

    def test_pro_allowed_problem(self):
        opt = QuantumOptimizer(tier=Tier.PRO)
        result = opt.solve_optimization("logistics_routing", {}, ["r1", "r2"])
        assert isinstance(result, dict)

    def test_pro_blocked_problem(self):
        opt = QuantumOptimizer(tier=Tier.PRO)
        with pytest.raises(QuantumOptimizerError):
            opt.solve_optimization("protein_folding", {}, [])

    def test_enterprise_all_problem_types(self):
        opt = QuantumOptimizer(tier=Tier.ENTERPRISE)
        for pt in PROBLEM_TYPES:
            result = opt.solve_optimization(pt, {}, ["x"])
            assert result["problem_type"] == pt

    def test_solve_optimization_has_required_keys(self):
        opt = QuantumOptimizer(tier=Tier.FREE)
        result = opt.solve_optimization("traveling_salesman", {"max_dist": 100}, ["a", "b"])
        for key in ("solution_id", "objective_value", "optimal_solution", "convergence"):
            assert key in result

    def test_unknown_problem_raises(self):
        opt = QuantumOptimizer(tier=Tier.ENTERPRISE)
        with pytest.raises(QuantumOptimizerError):
            opt.solve_optimization("unknown_problem", {}, [])

    def test_free_physics_simulation_raises(self):
        opt = QuantumOptimizer(tier=Tier.FREE)
        with pytest.raises(QuantumOptimizerError):
            opt.simulate_physics("harmonic_oscillator", {})

    def test_pro_physics_simulation_returns_dict(self):
        opt = QuantumOptimizer(tier=Tier.PRO)
        result = opt.simulate_physics("harmonic_oscillator", {"energy_levels": 5})
        assert isinstance(result, dict)
        assert "energy_spectrum" in result

    def test_enterprise_physics_has_noise_model(self):
        opt = QuantumOptimizer(tier=Tier.ENTERPRISE)
        result = opt.simulate_physics("ising_model", {})
        assert result.get("noise_model_applied") is True

    def test_global_simulation_free_raises(self):
        opt = QuantumOptimizer(tier=Tier.FREE)
        with pytest.raises(QuantumOptimizerError):
            opt.solve_global_simulation("climate", {})

    def test_global_simulation_pro_raises(self):
        opt = QuantumOptimizer(tier=Tier.PRO)
        with pytest.raises(QuantumOptimizerError):
            opt.solve_global_simulation("climate", {})

    def test_global_simulation_enterprise_returns_dict(self):
        opt = QuantumOptimizer(tier=Tier.ENTERPRISE)
        result = opt.solve_global_simulation("climate", {"resolution_km": 10})
        assert isinstance(result, dict)
        assert result["domain"] == "climate"

    def test_global_simulation_has_required_keys(self):
        opt = QuantumOptimizer(tier=Tier.ENTERPRISE)
        result = opt.solve_global_simulation("ocean_circulation", {})
        for key in ("simulation_id", "grid_points", "quantum_advantage_speedup"):
            assert key in result


# ===========================================================================
# QuantumPartnershipManager
# ===========================================================================

class TestQuantumPartnershipManager:
    def test_default_tier(self):
        pm = QuantumPartnershipManager()
        assert pm.tier == Tier.FREE

    def test_free_connect_enterprise_ai_quantum(self):
        pm = QuantumPartnershipManager(tier=Tier.FREE)
        result = pm.connect_quantum_provider("Enterprise AI_Quantum")
        assert result["status"] == "connected"
        assert result["provider"] == "Enterprise AI_Quantum"

    def test_free_connect_google_raises(self):
        pm = QuantumPartnershipManager(tier=Tier.FREE)
        with pytest.raises(QuantumPartnershipManagerError):
            pm.connect_quantum_provider("Google_Quantum_AI")

    def test_pro_connect_ionq(self):
        pm = QuantumPartnershipManager(tier=Tier.PRO)
        result = pm.connect_quantum_provider("IonQ")
        assert result["status"] == "connected"

    def test_pro_connect_dwave_raises(self):
        pm = QuantumPartnershipManager(tier=Tier.PRO)
        with pytest.raises(QuantumPartnershipManagerError):
            pm.connect_quantum_provider("D-Wave")

    def test_enterprise_connect_all_providers(self):
        pm = QuantumPartnershipManager(tier=Tier.ENTERPRISE)
        for provider in PROVIDERS:
            result = pm.connect_quantum_provider(provider)
            assert result["status"] == "connected"

    def test_unknown_provider_raises(self):
        pm = QuantumPartnershipManager(tier=Tier.FREE)
        with pytest.raises(QuantumPartnershipManagerError):
            pm.connect_quantum_provider("Unknown_Quantum_Co")

    def test_list_available_backends_returns_dict(self):
        pm = QuantumPartnershipManager(tier=Tier.FREE)
        result = pm.list_available_backends()
        assert isinstance(result, dict)
        assert "backends" in result

    def test_list_backends_accessible_count_free(self):
        pm = QuantumPartnershipManager(tier=Tier.FREE)
        result = pm.list_available_backends()
        assert result["accessible_provider_count"] == 1

    def test_list_backends_accessible_count_enterprise(self):
        pm = QuantumPartnershipManager(tier=Tier.ENTERPRISE)
        result = pm.list_available_backends()
        assert result["accessible_provider_count"] == len(PROVIDERS)

    def test_free_resource_estimate_raises(self):
        pm = QuantumPartnershipManager(tier=Tier.FREE)
        with pytest.raises(QuantumPartnershipManagerError):
            pm.get_quantum_resource_estimate({"qubits": 4, "gates": 10, "shots": 100}, "enterprise_aiq_manila")

    def test_pro_resource_estimate_returns_dict(self):
        pm = QuantumPartnershipManager(tier=Tier.PRO)
        result = pm.get_quantum_resource_estimate({"qubits": 8, "gates": 20, "shots": 500}, "enterprise_aiq_manila")
        assert isinstance(result, dict)
        for key in ("estimated_cost_usd", "qubit_fidelity", "recommended_shots"):
            assert key in result

    def test_connection_stored(self):
        pm = QuantumPartnershipManager(tier=Tier.FREE)
        pm.connect_quantum_provider("Enterprise AI_Quantum")
        assert "Enterprise AI_Quantum" in pm._connected_providers


# ===========================================================================
# QuantumAIBot (main bot)
# ===========================================================================

class TestQuantumAIBotInit:
    def test_default_tier_is_free(self):
        bot = QuantumAIBot()
        assert bot.tier == Tier.FREE

    def test_pro_tier(self):
        bot = QuantumAIBot(tier=Tier.PRO)
        assert bot.tier == Tier.PRO

    def test_enterprise_tier(self):
        bot = QuantumAIBot(tier=Tier.ENTERPRISE)
        assert bot.tier == Tier.ENTERPRISE

    def test_config_loaded(self):
        bot = QuantumAIBot()
        assert bot.config is not None

    def test_sub_components_initialized(self):
        bot = QuantumAIBot(tier=Tier.PRO)
        assert bot.simulator is not None
        assert bot.optimizer is not None
        assert bot.partnership_manager is not None


class TestQuantumAIBotSimulate:
    def test_simulate_circuit_returns_dict(self):
        bot = QuantumAIBot(tier=Tier.FREE)
        result = bot.simulate_quantum_circuit(2, [{"type": "hadamard"}], 50)
        assert isinstance(result, dict)

    def test_simulate_circuit_qubit_violation_raises(self):
        bot = QuantumAIBot(tier=Tier.FREE)
        with pytest.raises(QuantumAIBotError):
            bot.simulate_quantum_circuit(10, [], 10)

    def test_activity_logged_after_simulate(self):
        bot = QuantumAIBot(tier=Tier.FREE)
        bot.simulate_quantum_circuit(2, [], 10)
        assert any(a["action"] == "simulate_circuit" for a in bot._activity_log)


class TestQuantumAIBotOptimization:
    def test_solve_optimization_free_tier(self):
        bot = QuantumAIBot(tier=Tier.FREE)
        result = bot.solve_optimization_problem("traveling_salesman", {}, ["a", "b"])
        assert isinstance(result, dict)

    def test_solve_optimization_tier_violation(self):
        bot = QuantumAIBot(tier=Tier.FREE)
        with pytest.raises(QuantumAIBotError):
            bot.solve_optimization_problem("protein_folding", {}, [])

    def test_run_physics_simulation_pro(self):
        bot = QuantumAIBot(tier=Tier.PRO)
        result = bot.run_physics_simulation("harmonic_oscillator", {})
        assert isinstance(result, dict)

    def test_run_physics_simulation_free_raises(self):
        bot = QuantumAIBot(tier=Tier.FREE)
        with pytest.raises(QuantumAIBotError):
            bot.run_physics_simulation("harmonic_oscillator", {})


class TestQuantumAIBotPartnership:
    def test_connect_quantum_partner_free(self):
        bot = QuantumAIBot(tier=Tier.FREE)
        result = bot.connect_quantum_partner("Enterprise AI_Quantum")
        assert result["status"] == "connected"

    def test_connect_quantum_partner_tier_violation(self):
        bot = QuantumAIBot(tier=Tier.FREE)
        with pytest.raises(QuantumAIBotError):
            bot.connect_quantum_partner("Google_Quantum_AI")


class TestQuantumAIBotDashboard:
    def test_get_quantum_dashboard_returns_dict(self):
        bot = QuantumAIBot(tier=Tier.FREE)
        dash = bot.get_quantum_dashboard()
        assert isinstance(dash, dict)

    def test_dashboard_has_required_keys(self):
        bot = QuantumAIBot(tier=Tier.PRO)
        dash = bot.get_quantum_dashboard()
        for key in ("bot", "tier", "features", "supported_problem_types", "supported_providers"):
            assert key in dash

    def test_dashboard_tier_matches(self):
        bot = QuantumAIBot(tier=Tier.ENTERPRISE)
        dash = bot.get_quantum_dashboard()
        assert dash["tier"] == "enterprise"

    def test_dashboard_upgrade_available_for_free(self):
        bot = QuantumAIBot(tier=Tier.FREE)
        dash = bot.get_quantum_dashboard()
        assert dash["upgrade_available"] is True

    def test_dashboard_no_upgrade_for_enterprise(self):
        bot = QuantumAIBot(tier=Tier.ENTERPRISE)
        dash = bot.get_quantum_dashboard()
        assert dash["upgrade_available"] is False


# ===========================================================================
# Tiers module
# ===========================================================================

class TestQuantumAIBotTiers:
    def test_bot_features_has_all_tiers(self):
        for tier in Tier:
            assert tier.value in BOT_FEATURES

    def test_get_bot_tier_info_returns_dict(self):
        for tier in Tier:
            info = get_bot_tier_info(tier)
            assert isinstance(info, dict)
            assert "features" in info
            assert "price_usd_monthly" in info

    def test_quantum_prices_higher_than_base(self):
        info_pro = get_bot_tier_info(Tier.PRO)
        info_enterprise = get_bot_tier_info(Tier.ENTERPRISE)
        assert info_pro["price_usd_monthly"] >= 99.0
        assert info_enterprise["price_usd_monthly"] >= 499.0

    def test_free_tier_price_is_zero(self):
        info = get_bot_tier_info(Tier.FREE)
        assert info["price_usd_monthly"] == 0.0
