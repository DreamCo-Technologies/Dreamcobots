"""
Dreamcobots Health & Wellness Bot — tier-aware health tracking and wellness management.

Usage
-----
    from health_wellness_bot import HealthWellnessBot
    from tiers import Tier

    bot = HealthWellnessBot(tier=Tier.FREE)
    result = bot.calculate_bmi(70.0, 1.75)
    print(result)
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))

from tiers import Tier, get_tier_config, get_upgrade_path

import importlib.util as _ilu
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_spec = _ilu.spec_from_file_location("_health_tiers", os.path.join(_THIS_DIR, "tiers.py"))
_health_tiers = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_health_tiers)
HEALTH_FEATURES = _health_tiers.HEALTH_FEATURES
get_health_tier_info = _health_tiers.get_health_tier_info


class HealthWellnessBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


class HealthWellnessBotRequestLimitError(Exception):
    """Raised when the monthly request quota has been exhausted."""


class HealthWellnessBot:
    """
    Tier-aware health and wellness tracking bot.

    Parameters
    ----------
    tier : Tier
        Subscription tier controlling feature availability and request limits.
    """

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)
        self._request_count: int = 0
        self._workouts: list[dict] = []
        self._nutrition_log: list[dict] = []

    # ------------------------------------------------------------------
    # Core API
    # ------------------------------------------------------------------

    def calculate_bmi(self, weight_kg: float, height_m: float) -> dict:
        """
        Calculate BMI and return category.

        Parameters
        ----------
        weight_kg : float
            Weight in kilograms.
        height_m : float
            Height in meters.

        Returns
        -------
        dict
        """
        self._check_request_limit()
        self._request_count += 1
        bmi = round(weight_kg / (height_m ** 2), 2)
        if bmi < 18.5:
            category = "Underweight"
        elif bmi < 25.0:
            category = "Normal weight"
        elif bmi < 30.0:
            category = "Overweight"
        else:
            category = "Obese"
        return {
            "weight_kg": weight_kg,
            "height_m": height_m,
            "bmi": bmi,
            "category": category,
            "tier": self.tier.value,
            "requests_used": self._request_count,
            "requests_remaining": self._requests_remaining(),
        }

    def log_workout(self, workout_type: str, duration_minutes: int,
                    calories_burned: int | None = None) -> dict:
        """
        Log a workout session.

        Parameters
        ----------
        workout_type : str
            Type of workout (e.g., "running", "strength").
        duration_minutes : int
            Duration in minutes.
        calories_burned : int | None
            Estimated calories burned.

        Returns
        -------
        dict
        """
        self._check_request_limit()
        self._request_count += 1
        entry = {
            "workout_id": f"WO-{len(self._workouts) + 1:04d}",
            "workout_type": workout_type,
            "duration_minutes": duration_minutes,
            "calories_burned": calories_burned or duration_minutes * 7,
        }
        self._workouts.append(entry)
        return {
            "workout": entry,
            "total_workouts": len(self._workouts),
            "tier": self.tier.value,
            "requests_used": self._request_count,
            "requests_remaining": self._requests_remaining(),
        }

    def log_nutrition(self, meal: str, calories: int, macros: dict | None = None) -> dict:
        """
        Log a meal and nutrition data.

        Parameters
        ----------
        meal : str
            Meal description.
        calories : int
            Total calories.
        macros : dict | None
            Macro breakdown (protein, carbs, fat). Requires PRO or ENTERPRISE.

        Returns
        -------
        dict
        """
        self._check_request_limit()
        if macros and self.tier == Tier.FREE:
            raise HealthWellnessBotTierError(
                "Macro nutrient tracking requires PRO or ENTERPRISE tier."
            )
        self._request_count += 1
        entry = {
            "meal_id": f"MEAL-{len(self._nutrition_log) + 1:04d}",
            "meal": meal,
            "calories": calories,
            "macros": macros,
        }
        self._nutrition_log.append(entry)
        return {
            "nutrition_entry": entry,
            "total_calories_today": sum(e["calories"] for e in self._nutrition_log),
            "tier": self.tier.value,
            "requests_used": self._request_count,
            "requests_remaining": self._requests_remaining(),
        }

    def get_health_summary(self) -> dict:
        """
        Return an overall health metrics summary.

        Returns
        -------
        dict
        """
        self._check_request_limit()
        self._request_count += 1
        total_workouts = len(self._workouts)
        total_calories_burned = sum(w.get("calories_burned", 0) for w in self._workouts)
        total_calories_consumed = sum(e["calories"] for e in self._nutrition_log)
        return {
            "total_workouts": total_workouts,
            "total_calories_burned": total_calories_burned,
            "total_calories_consumed": total_calories_consumed,
            "calorie_balance": total_calories_burned - total_calories_consumed,
            "tier": self.tier.value,
            "requests_used": self._request_count,
            "requests_remaining": self._requests_remaining(),
        }

    # ------------------------------------------------------------------
    # Tier information
    # ------------------------------------------------------------------

    def describe_tier(self) -> str:
        """Print and return a description of the current tier."""
        info = get_health_tier_info(self.tier)
        limit = (
            "Unlimited"
            if info["requests_per_month"] is None
            else f"{info['requests_per_month']:,}"
        )
        lines = [
            f"=== {info['name']} Health & Wellness Bot Tier ===",
            f"Price   : ${info['price_usd_monthly']:.2f}/month",
            f"Requests: {limit}/month",
            f"Support : {info['support_level']}",
            "",
            "Features:",
        ]
        for feat in info["health_features"]:
            lines.append(f"  ✓ {feat}")
        output = "\n".join(lines)
        print(output)
        return output

    def show_upgrade_path(self) -> str:
        """Print details about the next available tier upgrade."""
        next_cfg = get_upgrade_path(self.tier)
        if next_cfg is None:
            msg = f"You are already on the top-tier plan ({self.config.name})."
            print(msg)
            return msg
        current_feats = set(HEALTH_FEATURES[self.tier.value])
        new_feats = [f for f in HEALTH_FEATURES[next_cfg.tier.value] if f not in current_feats]
        lines = [
            f"=== Upgrade: {self.config.name} → {next_cfg.name} ===",
            f"New price: ${next_cfg.price_usd_monthly:.2f}/month",
            "",
            "New features:",
        ]
        for feat in new_feats:
            lines.append(f"  + {feat}")
        lines.append(
            f"\nTo upgrade, set tier=Tier.{next_cfg.tier.name} when "
            "constructing HealthWellnessBot or contact support."
        )
        output = "\n".join(lines)
        print(output)
        return output

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _check_request_limit(self) -> None:
        limit = self.config.requests_per_month
        if limit is not None and self._request_count >= limit:
            raise HealthWellnessBotRequestLimitError(
                f"Monthly request limit of {limit:,} reached on the "
                f"{self.config.name} tier. Please upgrade to continue."
            )

    def _requests_remaining(self) -> str:
        limit = self.config.requests_per_month
        if limit is None:
            return "unlimited"
        return str(max(limit - self._request_count, 0))


if __name__ == "__main__":
    bot = HealthWellnessBot(tier=Tier.FREE)
    bot.describe_tier()
    result = bot.calculate_bmi(70.0, 1.75)
    print(result)
