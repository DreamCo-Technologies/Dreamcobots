"""Tier definitions for the Quantum AI Bot."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers, TIER_CATALOGUE  # noqa: F401

BOT_FEATURES = {
    Tier.FREE.value: [
        "max 4 qubits",
        "100 shots per simulation",
        "basic gate set (hadamard, pauli_x, pauli_z)",
        "single circuit simulation",
        "quantum state measurement",
    ],
    Tier.PRO.value: [
        "max 16 qubits",
        "1000 shots per simulation",
        "full gate set (8 gate types)",
        "hybrid quantum-AI model training",
        "quantum optimization (TSP, portfolio)",
        "physics simulations",
        "Quantum cloud & IonQ backend access",
        "quantum advantage evaluation",
    ],
    Tier.ENTERPRISE.value: [
        "max 50 qubits",
        "unlimited shots",
        "full gate set + custom gates",
        "advanced hybrid model training",
        "all optimization problem types",
        "global simulations (climate, protein folding)",
        "all quantum provider backends",
        "resource estimation",
        "priority quantum queue",
        "dedicated quantum support",
    ],
}

# Quantum tier pricing — premium over base tiers
QUANTUM_PRICES = {
    Tier.FREE.value: 0.0,
    Tier.PRO.value: 99.0,
    Tier.ENTERPRISE.value: 499.0,
}


def get_bot_tier_info(tier: Tier) -> dict:
    """Return quantum-specific tier information."""
    cfg = get_tier_config(tier)
    return {
        "tier": tier.value,
        "name": cfg.name,
        "price_usd_monthly": QUANTUM_PRICES[tier.value],
        "requests_per_month": cfg.requests_per_month,
        "features": BOT_FEATURES[tier.value],
        "support_level": cfg.support_level,
    }
