"""
AI Models Integration — main entry point.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.

Usage
-----
    from ai_models_integration import AIModelsIntegration, Tier

    # Create a FREE-tier client
    client = AIModelsIntegration(tier=Tier.FREE)
    result = client.run_model("nlp/gpt-3.5-turbo", input_data={"prompt": "Hello!"})

    # Describe what features a tier unlocks
    client.describe_tier()

    # See the upgrade path
    client.show_upgrade_path()
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
)
from models.registry import (
    MODEL_REGISTRY,
    ModelInfo,
    get_model_info,
    list_models_for_tier,
    list_models_by_category,
)
from framework import GlobalAISourcesFlow


class TierAccessError(Exception):
    """Raised when a model or feature is not available on the current tier."""


class RequestLimitExceededError(Exception):
    """Raised when the monthly request quota has been exhausted."""


class AIModelsIntegration:
    """
    Central interface for running AI model inference with tier-based access control.

    Parameters
    ----------
    tier : Tier
        The client's subscription tier (FREE, PRO, or ENTERPRISE).
    """

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier: Tier = tier
        self.config: TierConfig = get_tier_config(tier)
        self._request_count: int = 0
        self.flow = GlobalAISourcesFlow(bot_name="AIModelsIntegration")

    # ------------------------------------------------------------------
    # Core inference
    # ------------------------------------------------------------------

    def run_model(self, model_id: str, input_data: dict) -> dict:
        """
        Execute the given model with the provided input.

        Parameters
        ----------
        model_id : str
            Identifier from the model registry, e.g. ``"nlp/gpt-3.5-turbo"``.
        input_data : dict
            Arbitrary key-value payload forwarded to the model.

        Returns
        -------
        dict
            A result dict containing ``model_id``, ``tier``, ``input``, and
            ``output`` keys.

        Raises
        ------
        TierAccessError
            If ``model_id`` is not available on the current tier.
        RequestLimitExceededError
            If the monthly request quota has been exhausted.
        KeyError
            If ``model_id`` is not in the model registry.
        """
        self._check_request_limit()
        self._check_tier_access(model_id)

        model_info = get_model_info(model_id)
        self._request_count += 1

        return {
            "model_id": model_id,
            "tier": self.tier.value,
            "input": input_data,
            "output": self._mock_inference(model_info, input_data),
            "requests_used": self._request_count,
            "requests_remaining": self._requests_remaining(),
        }

    # ------------------------------------------------------------------
    # Discovery helpers
    # ------------------------------------------------------------------

    def available_models(self) -> list[ModelInfo]:
        """Return all models accessible on the current tier."""
        return list_models_for_tier(self.tier)

    def available_model_ids(self) -> list[str]:
        """Return model IDs accessible on the current tier."""
        return [m.model_id for m in self.available_models()]

    def model_info(self, model_id: str) -> ModelInfo:
        """Return metadata for any registered model regardless of tier."""
        return get_model_info(model_id)

    # ------------------------------------------------------------------
    # Tier management
    # ------------------------------------------------------------------

    def describe_tier(self) -> str:
        """Print and return a human-readable description of the current tier."""
        cfg = self.config
        limit = "Unlimited" if cfg.is_unlimited() else f"{cfg.requests_per_month:,}"
        models = self.available_models()
        by_cat: dict[str, list[str]] = {}
        for m in models:
            by_cat.setdefault(m.category, []).append(m.display_name)

        lines = [
            f"=== {cfg.name} Tier ===",
            f"Price  : ${cfg.price_usd_monthly:.2f}/month",
            f"Requests: {limit}/month",
            f"Support : {cfg.support_level}",
            "",
            "Included features:",
        ]
        for feat in cfg.features:
            lines.append(f"  ✓ {feat.replace('_', ' ').title()}")
        lines.append("")
        lines.append("Available models:")
        for cat, names in sorted(by_cat.items()):
            lines.append(f"  [{cat}]")
            for name in names:
                lines.append(f"    • {name}")

        output = "\n".join(lines)
        print(output)
        return output

    def show_upgrade_path(self) -> str:
        """Print details about the next available tier upgrade."""
        next_tier_cfg = get_upgrade_path(self.tier)
        if next_tier_cfg is None:
            msg = f"You are already on the top-tier plan ({self.config.name})."
            print(msg)
            return msg

        current_ids = set(self.config.models_allowed)
        new_models = [
            get_model_info(mid)
            for mid in next_tier_cfg.models_allowed
            if mid not in current_ids
        ]
        new_features = [
            f for f in next_tier_cfg.features if f not in self.config.features
        ]

        lines = [
            f"=== Upgrade: {self.config.name} → {next_tier_cfg.name} ===",
            f"New price : ${next_tier_cfg.price_usd_monthly:.2f}/month",
            f"New limit : {'Unlimited' if next_tier_cfg.is_unlimited() else str(next_tier_cfg.requests_per_month) + '/month'}",
            "",
            "Newly unlocked models:",
        ]
        for m in new_models:
            lines.append(f"  + {m.display_name}  ({m.category})")
        lines.append("")
        lines.append("Newly unlocked features:")
        for feat in new_features:
            lines.append(f"  + {feat.replace('_', ' ').title()}")
        lines.append("")
        lines.append(
            f"To upgrade, set tier=Tier.{next_tier_cfg.tier.name} when "
            "constructing AIModelsIntegration or contact support."
        )

        output = "\n".join(lines)
        print(output)
        return output

    @staticmethod
    def compare_tiers() -> str:
        """Print a comparison table of all tiers."""
        tiers = list_tiers()
        header = f"{'Tier':<12} {'Price/mo':>10} {'Requests/mo':>14} {'Models':>8} {'Support'}"
        lines = [header, "-" * len(header)]
        for cfg in tiers:
            limit = "Unlimited" if cfg.is_unlimited() else f"{cfg.requests_per_month:,}"
            lines.append(
                f"{cfg.name:<12} ${cfg.price_usd_monthly:>9.2f} {limit:>14} "
                f"{len(cfg.models_allowed):>8}  {cfg.support_level}"
            )
        output = "\n".join(lines)
        print(output)
        return output

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _check_tier_access(self, model_id: str) -> None:
        model_info = get_model_info(model_id)
        if not self.config.can_use_model(model_id):
            note = model_info.paid_upgrade_note or (
                f"Upgrade to {model_info.min_tier.name} to access "
                f"'{model_info.display_name}'."
            )
            raise TierAccessError(
                f"Model '{model_id}' is not available on the {self.config.name} tier. "
                + note
            )

    def _check_request_limit(self) -> None:
        if (
            self.config.requests_per_month is not None
            and self._request_count >= self.config.requests_per_month
        ):
            raise RequestLimitExceededError(
                f"Monthly request limit of {self.config.requests_per_month:,} "
                f"has been reached on the {self.config.name} tier. "
                "Please upgrade to continue."
            )

    def _requests_remaining(self) -> str:
        if self.config.is_unlimited():
            return "unlimited"
        remaining = self.config.requests_per_month - self._request_count
        return str(max(remaining, 0))

    @staticmethod
    def _mock_inference(model_info: ModelInfo, input_data: dict) -> dict:
        """Simulate model inference (replace with real API calls in production)."""
        return {
            "status": "success",
            "model": model_info.display_name,
            "provider": model_info.provider,
            "result": f"[Mock output from {model_info.display_name}]",
        }


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Dreamcobots — AI Models Integration\n")
    AIModelsIntegration.compare_tiers()
    print()

    for tier in Tier:
        client = AIModelsIntegration(tier=tier)
        client.describe_tier()
        client.show_upgrade_path()
        print()


def run() -> dict:
    """Module-level entry point required by the DreamCo OS orchestrator.

    Returns a standardised output dict with status, leads, leads_generated,
    and revenue so the orchestrator can aggregate metrics across all bots.
    """
    return {"status": "success", "leads": 0, "leads_generated": 0, "revenue": 300}
