"""
Behavioral Settings module for the Discount Dominator (settings 581–600).

Provides the :class:`BehavioralSettings` facade used by all bots to drive
customer-centric, data-driven behavioural automation.
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .settings import (
    DISCOUNT_DOMINATOR_SETTINGS,
    GROUP_BEHAVIORAL,
    get_setting,
    get_group_settings,
    as_dict,
)


class BehavioralSettings:
    """Facade for the Behavioral Settings group (581–600).

    Parameters
    ----------
    overrides:
        Optional ``{setting_id: value}`` mapping to override defaults.
    """

    def __init__(self, overrides: Optional[Dict[int, Any]] = None) -> None:
        if overrides:
            for sid, val in overrides.items():
                if sid in DISCOUNT_DOMINATOR_SETTINGS:
                    DISCOUNT_DOMINATOR_SETTINGS[sid].value = val

    # ------------------------------------------------------------------
    # Property helpers
    # ------------------------------------------------------------------

    @property
    def segmentation_model(self) -> str:
        return str(get_setting(581).value)

    @property
    def purchase_tracking(self) -> bool:
        return bool(get_setting(582).value)

    @property
    def recommendation_engine(self) -> bool:
        return bool(get_setting(583).value)

    @property
    def abandoned_cart_recovery(self) -> bool:
        return bool(get_setting(584).value)

    @property
    def loyalty_programme(self) -> bool:
        return bool(get_setting(585).value)

    @property
    def churn_prediction(self) -> bool:
        return bool(get_setting(587).value)

    @property
    def next_best_action(self) -> bool:
        return bool(get_setting(588).value)

    @property
    def real_estate_buyer_scoring(self) -> bool:
        return bool(get_setting(592).value)

    @property
    def car_buyer_intent_model(self) -> bool:
        return bool(get_setting(593).value)

    @property
    def retail_persona_modelling(self) -> bool:
        return bool(get_setting(594).value)

    @property
    def social_proof_injection(self) -> bool:
        return bool(get_setting(597).value)

    @property
    def urgency_scarcity_engine(self) -> bool:
        return bool(get_setting(598).value)

    @property
    def opt_out_management(self) -> bool:
        return bool(get_setting(599).value)

    # ------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------

    def get_all_settings(self) -> Dict[int, Any]:
        """Return all behavioral settings as ``{id: value}``."""
        return as_dict(GROUP_BEHAVIORAL)

    def get_enabled_features(self) -> List[str]:
        """Return names of behavioral settings that are currently ``True``."""
        return [
            s.name
            for s in get_group_settings(GROUP_BEHAVIORAL)
            if s.value is True
        ]

    def configure_for_real_estate(self) -> None:
        """Apply behavioral presets for the real estate optimisation system."""
        DISCOUNT_DOMINATOR_SETTINGS[581].value = "rfm"    # segmentation_model
        DISCOUNT_DOMINATOR_SETTINGS[592].value = True     # real_estate_buyer_scoring
        DISCOUNT_DOMINATOR_SETTINGS[588].value = True     # next_best_action
        DISCOUNT_DOMINATOR_SETTINGS[595].value = True     # dynamic_content_personalisation

    def configure_for_car_flipping(self) -> None:
        """Apply behavioral presets for the car-flipping bot."""
        DISCOUNT_DOMINATOR_SETTINGS[593].value = True     # car_buyer_intent_model
        DISCOUNT_DOMINATOR_SETTINGS[582].value = True     # purchase_tracking
        DISCOUNT_DOMINATOR_SETTINGS[586].value = True     # win_back_campaign
        DISCOUNT_DOMINATOR_SETTINGS[597].value = True     # social_proof_injection

    def configure_for_retail_intelligence(self) -> None:
        """Apply behavioral presets for the retail intelligence network."""
        DISCOUNT_DOMINATOR_SETTINGS[581].value = "kmeans" # segmentation_model
        DISCOUNT_DOMINATOR_SETTINGS[594].value = True     # retail_persona_modelling
        DISCOUNT_DOMINATOR_SETTINGS[598].value = True     # urgency_scarcity_engine
        DISCOUNT_DOMINATOR_SETTINGS[584].value = True     # abandoned_cart_recovery
        DISCOUNT_DOMINATOR_SETTINGS[587].value = True     # churn_prediction

    def score_customer(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Return a simple intent score for a customer based on behavioural data.

        Parameters
        ----------
        customer_data:
            Dict with keys such as ``recency_days``, ``frequency``,
            ``monetary_value``.

        Returns
        -------
        dict
            ``{"segment": str, "churn_risk": float, "intent_score": float}``
        """
        recency = customer_data.get("recency_days", 30)
        frequency = customer_data.get("frequency", 1)
        monetary = customer_data.get("monetary_value", 0.0)

        intent_score = min(1.0, (frequency * monetary) / max(recency, 1) / 100)
        churn_risk = min(1.0, recency / 365.0)

        if intent_score > 0.7:
            segment = "high_value"
        elif intent_score > 0.3:
            segment = "mid_value"
        else:
            segment = "low_value"

        return {
            "segment": segment,
            "churn_risk": round(churn_risk, 4),
            "intent_score": round(intent_score, 4),
            "model": self.segmentation_model,
        }

    def summary(self) -> Dict[str, Any]:
        """Return a human-readable summary dict of key behavioral settings."""
        return {
            "segmentation_model": self.segmentation_model,
            "recommendation_engine": self.recommendation_engine,
            "abandoned_cart_recovery": self.abandoned_cart_recovery,
            "churn_prediction": self.churn_prediction,
            "next_best_action": self.next_best_action,
            "social_proof_injection": self.social_proof_injection,
            "urgency_scarcity_engine": self.urgency_scarcity_engine,
            "enabled_feature_count": len(self.get_enabled_features()),
        }
